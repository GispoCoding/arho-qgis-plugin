import datetime
import logging
from typing import TYPE_CHECKING, Any, Optional, cast
from uuid import UUID, uuid4
from zoneinfo import ZoneInfo

import simplejson as json  # type: ignore
from geoalchemy2 import WKBElement
from geoalchemy2.shape import to_shape
from shapely import to_geojson
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from database import base, codes, models
from database.codes import (
    NameOfPlanCaseDecision,
    TypeOfDecisionMaker,
    TypeOfInteractionEvent,
    TypeOfProcessingEvent,
    decisionmaker_by_status,
    decisions_by_status,
    get_code_uri,
    interaction_events_by_status,
    processing_events_by_status,
)
from database.enums import AttributeValueDataType
from ryhti_client.deserializer import (
    Deserializer,
    plan_matter_data_from_extra_data_dict,
    ryhti_plan_from_json,
)
from ryhti_client.ryhti_schema import (
    AttributeValue,
    Period,
    RyhtiHandlingEvent,
    RyhtiInteractionEvent,
    RyhtiPlan,
    RyhtiPlanDecision,
    RyhtiPlanMatter,
    RyhtiPlanMatterPhase,
)

if TYPE_CHECKING:
    import uuid

    from ryhti_client.ryhti_client import RyhtiResponse

LOGGER = logging.getLogger(__name__)

LOCAL_TZ = ZoneInfo("Europe/Helsinki")


class PlanAlreadyExistsError(Exception):
    def __init__(self, plan_id: str) -> None:
        self.plan_id = plan_id
        super().__init__(f"Plan '{plan_id}' already exists in the database.")


class DatabaseClient:
    def __init__(self, connection_string: str, plan_uuid: str | None = None) -> None:
        engine = create_engine(connection_string)
        self.Session = sessionmaker(bind=engine)
        # Cache plans fetched from database
        self.plans: dict[UUID, models.Plan] = {}
        # Cache plan dictionaries
        self.plan_dictionaries: dict[UUID, RyhtiPlan] = {}

        # We only ever need code uri values, not codes themselves, so let's not bother
        # fetching codes from the database at all. URI is known from class and value.
        # TODO: check that valid status is "13" and approval status is "06" when
        # the lifecycle status code list transitions from DRAFT to VALID.
        #
        # It is exceedingly weird that this, the most important of all codes, is
        # *not* a descriptive string, but a random number that may change, while all
        # the other code lists have descriptive strings that will *not* change.
        self.pending_status_value = "02"
        self.approved_status_value = "06"
        self.valid_status_value = "13"

        # Do some prefetching before starting the run.
        #
        # Do *not* expire on commit, because we want to cache the old data in plan
        # objects throughout the session. If we want up-to date plan data, we will
        # know to explicitly refresh the object from a new session.
        #
        # Otherwise, we may access old plan data without having to create a session
        # and query.
        with self.Session(expire_on_commit=False) as session:
            LOGGER.info("Caching requested plans from database...")
            # Only process specified plans
            stmt = select(models.Plan)
            if plan_uuid:
                LOGGER.info(f"Only fetching plan {plan_uuid}")
                stmt = stmt.where(models.Plan.id == plan_uuid)

            self.plans = {plan.id: plan for plan in session.scalars(stmt).unique()}
        if not self.plans:
            LOGGER.info("No plans found in database.")
        else:
            # Serialize plans in database. All actions require serialized plans.
            # However, plan matters are not always required, they are not serialized
            # by default.
            LOGGER.info("Formatting plan data...")
            self.plan_dictionaries = self.get_plan_dictionaries()
            LOGGER.info("Client initialized with plans to process:")
            LOGGER.info(self.plans)

    def get_geojson(self, geometry: WKBElement) -> dict:
        """Returns geojson format dict with the correct SRID set."""
        # We cannot use postgis geojson functions here, because the data has already
        # been fetched from the database. So let's create geojson the python way, it's
        # probably faster than doing extra database queries for the conversion.
        # However, it seems that to_shape forgets to add the SRID information from the
        # EWKB (https://github.com/geoalchemy/geoalchemy2/issues/235), so we have to
        # paste the SRID back manually :/
        shape = to_shape(geometry)
        if len(shape.geoms) == 1:
            # Ryhti API may not allow single geometries in multigeometries in all cases.
            # Let's make them into single geometries instead:
            shape = shape.geoms[0]
        # Also, we don't want to serialize the geojson quite yet. Looks like the only
        # way to do get python dict to actually convert the json back to dict until we
        # are ready to reserialize it :/
        return {
            "srid": str(base.PROJECT_SRID),
            "geometry": json.loads(to_geojson(shape)),
        }

    def get_isoformat_value_with_z(self, datetime_value: datetime.datetime) -> str:
        """Returns isoformatted datetime in UTC with Z instead of +00:00."""
        return datetime_value.isoformat().replace("+00:00", "Z")

    def get_date(self, datetime_value: datetime.datetime) -> str:
        """Returns isoformatted date for the given datetime in local timezone."""
        return datetime_value.astimezone(LOCAL_TZ).date().isoformat()

    def get_periods(
        self,
        dates_objects: list[models.LifeCycleDate] | list[models.EventDate],
        datetimes: bool = True,
    ) -> list[Period]:
        """Returns the time periods of given date objects. Optionally, only dates instead
        of datetimes may be returned.
        """
        return [
            {
                "begin": (
                    self.get_isoformat_value_with_z(dates_object.starting_at)
                    if datetimes
                    else self.get_date(dates_object.starting_at)
                ),
                "end": (
                    (
                        self.get_isoformat_value_with_z(dates_object.ending_at)
                        if datetimes
                        else self.get_date(dates_object.ending_at)
                    )
                    if dates_object.ending_at
                    else None
                ),
            }
            for dates_object in dates_objects
        ]

    def get_lifecycle_dates_for_status(
        self, plan_base: models.PlanBase, status_value: str
    ) -> list[models.LifeCycleDate]:
        """Returns the plan lifecycle date objects for the desired status."""
        return [
            lifecycle_date
            for lifecycle_date in plan_base.lifecycle_dates
            if lifecycle_date.lifecycle_status.value == status_value
        ]

    def get_lifecycle_periods(
        self, plan_base: models.PlanBase, status_value: str, datetimes: bool = True
    ) -> list[Period]:
        """Returns the start and end datetimes of lifecycle status for object. Optionally,
        only dates instead of datetimes may be returned.

        Note that for some lifecycle statuses, we may return multiple periods.
        """
        lifecycle_dates = self.get_lifecycle_dates_for_status(plan_base, status_value)
        return self.get_periods(lifecycle_dates, datetimes)

    def get_event_periods(
        self,
        lifecycle_date: models.LifeCycleDate,
        event_class: type[codes.CodeBase],
        event_value: str,
        datetimes: bool = True,
    ) -> list[Period]:
        """Returns the start and end datetimes of events with desired class and value
        linked to a lifecycle date object. Optionally, only dates instead of datetimes
        may be returned.

        Note that if the event occurs multiple times, we may return multiple periods.
        """

        def class_and_value_match(event_date: models.EventDate) -> bool:
            return bool(
                (
                    event_class is NameOfPlanCaseDecision
                    and event_date.decision
                    and event_date.decision.value == event_value
                )
                or (
                    event_class is TypeOfProcessingEvent
                    and event_date.processing_event
                    and event_date.processing_event.value == event_value
                )
                or (
                    event_class is TypeOfInteractionEvent
                    and event_date.interaction_event
                    and event_date.interaction_event.value == event_value
                )
            )

        event_dates = [
            date for date in lifecycle_date.event_dates if class_and_value_match(date)
        ]
        return self.get_periods(event_dates, datetimes)

    def get_last_period(self, periods: list[Period]) -> Period | None:
        """Returns the last period in the list, or None if the list is empty."""
        return periods[-1] if periods else None

    def get_plan_recommendation(
        self, plan_recommendation: models.PlanProposition
    ) -> dict:
        """Construct a dict of Ryhti compatible plan recommendation."""
        recommendation_dict: dict[str, Any] = {}
        recommendation_dict["planRecommendationKey"] = plan_recommendation.id
        recommendation_dict["lifeCycleStatus"] = (
            plan_recommendation.lifecycle_status.uri
        )
        if plan_recommendation.plan_themes:
            recommendation_dict["planThemes"] = [
                plan_theme.uri for plan_theme in plan_recommendation.plan_themes
            ]
        recommendation_dict["recommendationNumber"] = plan_recommendation.ordering
        # we should only have one valid period. If there are several, pick last
        recommendation_dict["periodOfValidity"] = self.get_last_period(
            self.get_lifecycle_periods(
                plan_recommendation, self.valid_status_value, datetimes=False
            )
        )
        recommendation_dict["value"] = plan_recommendation.text_value
        return recommendation_dict

    def get_attribute_value(
        self, attribute_value: base.AttributeValueMixin
    ) -> AttributeValue | None:
        if attribute_value.value_data_type is None:
            return None

        value: AttributeValue = {"dataType": attribute_value.value_data_type.value}

        def cast_numeric(number: float):
            if attribute_value.value_data_type in (
                AttributeValueDataType.NUMERIC,
                AttributeValueDataType.POSITIVE_NUMERIC,
                AttributeValueDataType.NUMERIC_RANGE,
                AttributeValueDataType.POSITIVE_NUMERIC_RANGE,
                AttributeValueDataType.SPOT_ELEVATION,
            ):
                return int(number)
            return number

        if attribute_value.value_data_type is AttributeValueDataType.CODE:
            if attribute_value.code_value is not None:
                value["code"] = attribute_value.code_value
            if attribute_value.code_list is not None:
                value["codeList"] = attribute_value.code_list
            if attribute_value.code_title is not None:
                value["title"] = attribute_value.code_title
        elif attribute_value.value_data_type in (
            AttributeValueDataType.NUMERIC,
            AttributeValueDataType.POSITIVE_NUMERIC,
            AttributeValueDataType.DECIMAL,
            AttributeValueDataType.POSITIVE_DECIMAL,
            AttributeValueDataType.SPOT_ELEVATION,
        ):
            if attribute_value.numeric_value is not None:
                value["number"] = cast_numeric(attribute_value.numeric_value)
            if attribute_value.unit:
                value["unitOfMeasure"] = attribute_value.unit
        elif attribute_value.value_data_type in (
            AttributeValueDataType.NUMERIC_RANGE,
            AttributeValueDataType.POSITIVE_NUMERIC_RANGE,
            AttributeValueDataType.DECIMAL_RANGE,
            AttributeValueDataType.POSITIVE_DECIMAL_RANGE,
        ):
            if attribute_value.numeric_range_min is not None:
                value["minimumValue"] = cast_numeric(attribute_value.numeric_range_min)
            if attribute_value.numeric_range_max is not None:
                value["maximumValue"] = cast_numeric(attribute_value.numeric_range_max)
            if attribute_value.unit is not None:
                value["unitOfMeasure"] = attribute_value.unit

        elif attribute_value.value_data_type is AttributeValueDataType.IDENTIFIER:
            pass  # TODO: implement identifier values
        elif attribute_value.value_data_type in (
            AttributeValueDataType.LOCALIZED_TEXT,
            AttributeValueDataType.TEXT,
        ):
            if attribute_value.text_value is not None:
                value["text"] = attribute_value.text_value
            if attribute_value.text_syntax is not None:
                value["syntax"] = attribute_value.text_syntax
        elif attribute_value.value_data_type in (
            AttributeValueDataType.TIME_PERIOD,
            AttributeValueDataType.TIME_PERIOD_DATE_ONLY,
        ):
            pass  # TODO: implement time period and time period date only values

        return value

    def get_additional_information(
        self, additional_information: models.AdditionalInformation
    ) -> dict:
        additional_information_dict = {
            "type": additional_information.type_of_additional_information.uri
        }

        if value := self.get_attribute_value(additional_information):
            additional_information_dict["value"] = value

        return additional_information_dict

    def get_plan_regulation(self, plan_regulation: models.PlanRegulation) -> dict:
        """Construct a dict of Ryhti compatible plan regulation."""
        regulation_dict: dict[str, Any] = {}
        regulation_dict["planRegulationKey"] = plan_regulation.id
        regulation_dict["lifeCycleStatus"] = plan_regulation.lifecycle_status.uri
        regulation_dict["type"] = plan_regulation.type_of_plan_regulation.uri
        if plan_regulation.plan_themes:
            regulation_dict["planThemes"] = [
                plan_theme.uri for plan_theme in plan_regulation.plan_themes
            ]
        regulation_dict["subjectIdentifiers"] = plan_regulation.subject_identifiers
        regulation_dict["regulationNumber"] = str(plan_regulation.ordering)
        # we should only have one valid period. If there are several, pick last
        regulation_dict["periodOfValidity"] = self.get_last_period(
            self.get_lifecycle_periods(
                plan_regulation, self.valid_status_value, datetimes=False
            )
        )

        if plan_regulation.types_of_verbal_plan_regulations:
            regulation_dict["verbalRegulations"] = [
                type_code.uri
                for type_code in plan_regulation.types_of_verbal_plan_regulations
            ]

        # Additional informations may contain multiple additional info
        # code values.
        regulation_dict["additionalInformations"] = [
            self.get_additional_information(ai)
            for ai in plan_regulation.additional_information
        ]

        if value := self.get_attribute_value(plan_regulation):
            regulation_dict["value"] = value

        return regulation_dict

    def get_plan_regulation_group(
        self, group: models.PlanRegulationGroup, general: bool = False
    ) -> dict:
        """Construct a dict of Ryhti compatible plan regulation group.

        Plan regulation groups and general regulation groups have some minor
        differences, so you can specify if you want to create a general
        regulation group.
        """
        group_dict: dict[str, Any] = {}
        if general:
            group_dict["generalRegulationGroupKey"] = group.id
        else:
            group_dict["planRegulationGroupKey"] = group.id
        group_dict["titleOfPlanRegulation"] = group.name
        if group.ordering is not None:
            group_dict["groupNumber"] = group.ordering
        if not general:
            group_dict["letterIdentifier"] = group.short_name
            group_dict["colorNumber"] = "#FFFFFF"
        group_dict["planRecommendations"] = []
        for recommendation in group.plan_propositions:
            group_dict["planRecommendations"].append(
                self.get_plan_recommendation(recommendation)
            )
        group_dict["planRegulations"] = []
        for regulation in group.plan_regulations:
            group_dict["planRegulations"].append(self.get_plan_regulation(regulation))
        return group_dict

    def get_plan_object(self, plan_object: models.PlanObjectBase) -> dict:
        """Construct a dict of Ryhti compatible plan object."""
        plan_object_dict: dict[str, Any] = {}
        plan_object_dict["planObjectKey"] = plan_object.id
        plan_object_dict["lifeCycleStatus"] = plan_object.lifecycle_status.uri
        plan_object_dict["undergroundStatus"] = plan_object.type_of_underground.uri
        plan_object_dict["geometry"] = self.get_geojson(plan_object.geom)
        plan_object_dict["name"] = plan_object.name
        plan_object_dict["description"] = plan_object.description
        plan_object_dict["objectNumber"] = plan_object.ordering
        # we should only have one valid period. If there are several, pick last
        plan_object_dict["periodOfValidity"] = self.get_last_period(
            self.get_lifecycle_periods(
                plan_object, self.valid_status_value, datetimes=False
            )
        )
        if plan_object.height_min or plan_object.height_max:
            plan_object_dict["verticalLimit"] = {
                "dataType": "DecimalRange",
                # we have to use simplejson because numbers are Decimal
                "minimumValue": plan_object.height_min,
                "maximumValue": plan_object.height_max,
                "unitOfMeasure": plan_object.height_unit,
            }

        # RelatedPlanObjectKeys
        related_plan_object_keys = self._get_related_plan_object_keys(plan_object)
        if related_plan_object_keys:
            plan_object_dict["relatedPlanObjectKeys"] = related_plan_object_keys

        return plan_object_dict

    def _needs_containing_land_use_area(
        self, plan_object: models.PlanObjectBase
    ) -> bool:
        """Returns True if the plan object needs a containing land use area as related plan
        object based on the validation rule
        58 quality/req-spatialplanregulationtype-reference-spatialplanobject.
        """
        return isinstance(plan_object, models.OtherArea) and any(
            regulation.type_of_plan_regulation.value
            in {
                "sitovanTonttijaonMukainenTontti",
                "ohjeellinenrakennusPaikka",
                "rakennusala",
                "rakennuspaikka",
                "rakennusalaJolleSaaSijoittaaTalousrakennuksen",
                "rakennusalaJolleSaaSijoittaaSaunan",
                "korttelialueTaiKorttelialueenOsa",
            }
            for group in plan_object.plan_regulation_groups
            for regulation in cast("models.PlanRegulationGroup", group).plan_regulations
        )

    def _get_containing_land_use_area(
        self, plan_object: models.PlanObjectBase
    ) -> Optional["uuid.UUID"]:
        """Returns a land use area id that contains this plan_object.
        If not found, returns None.
        """
        with self.Session(expire_on_commit=False) as session:
            stmt = select(models.LandUseArea.id).where(
                models.LandUseArea.plan_id == plan_object.plan_id,
                models.LandUseArea.geom.ST_Contains(plan_object.geom),
            )
            return session.scalars(stmt).one_or_none()

    def _get_related_plan_object_keys(
        self, plan_object: models.PlanObjectBase
    ) -> list["uuid.UUID"]:
        # TODO: there might be other use cases for related plan objects
        related_plan_object_keys = []

        # Address the validation rule
        # 58: quality/req-spatialplanregulationtype-reference-spatialplanobject
        if self._needs_containing_land_use_area(plan_object):
            containing_land_use_area_id = self._get_containing_land_use_area(
                plan_object
            )
            if containing_land_use_area_id:
                related_plan_object_keys.append(containing_land_use_area_id)

        return related_plan_object_keys

    def get_plan_object_dicts(self, plan_objects: list[models.PlanObjectBase]) -> list:
        """Construct a list of Ryhti compatible plan object dicts from plan objects
        in the local database.
        """
        plan_object_dicts = []
        for plan_object in plan_objects:
            plan_object_dicts.append(self.get_plan_object(plan_object))
        return plan_object_dicts

    def get_plan_regulation_groups(
        self, plan_objects: list[models.PlanObjectBase]
    ) -> list:
        """Construct a list of Ryhti compatible plan regulation groups from plan objects
        in the local database.
        """
        group_dicts = []
        group_ids = {
            regulation_group.id
            for plan_object in plan_objects
            for regulation_group in plan_object.plan_regulation_groups
        }
        # Let's fetch all the plan regulation groups for all the objects with a single
        # query. Hoping lazy loading does its trick with all the plan regulations.
        with self.Session(expire_on_commit=False) as session:
            plan_regulation_groups = (
                session.query(models.PlanRegulationGroup)
                .filter(models.PlanRegulationGroup.id.in_(group_ids))
                .order_by(models.PlanRegulationGroup.ordering)
                .all()
            )
            for group in plan_regulation_groups:
                group_dicts.append(self.get_plan_regulation_group(group))
        return group_dicts

    def get_plan_regulation_group_relations(
        self, plan_objects: list[models.PlanObjectBase]
    ) -> list[dict[str, "uuid.UUID"]]:
        """Construct a list of Ryhti compatible plan regulation group relations from plan
        objects in the local database.
        """
        return [
            {
                "planObjectKey": plan_object.id,
                "planRegulationGroupKey": regulation_group.id,
            }
            for plan_object in plan_objects
            for regulation_group in plan_object.plan_regulation_groups
        ]

    def get_plan_dictionary(self, plan: models.Plan) -> RyhtiPlan:
        """Construct a dict of single Ryhti compatible plan from plan in the
        local database.
        """
        plan_dictionary = RyhtiPlan()

        # planKey should always be the local uuid, not the permanent plan matter id.
        plan_dictionary["planKey"] = str(plan.id)
        # Let's have all the code values preloaded joined from db.
        # It makes this super easy:
        plan_dictionary["lifeCycleStatus"] = plan.lifecycle_status.uri
        plan_dictionary["legalEffectOfLocalMasterPlans"] = (
            [effect.uri for effect in plan.legal_effects_of_master_plan]
            if plan.legal_effects_of_master_plan
            else None
        )
        plan_dictionary["scale"] = plan.scale
        plan_dictionary["geographicalArea"] = self.get_geojson(plan.geom)
        # For reasons unknown, Ryhti does not allow multilanguage description.
        plan_description = (
            plan.description.get("fin") if isinstance(plan.description, dict) else None
        )
        plan_dictionary["planDescription"] = plan_description

        # Here come the dependent objects. They are related to the plan directly or
        # via the plan objects, so we better fetch the objects first and then move on.
        plan_objects: list[models.PlanObjectBase] = []
        with self.Session(expire_on_commit=False) as session:
            session.add(plan)
            plan_objects += plan.land_use_areas
            plan_objects += plan.other_areas
            plan_objects += plan.lines
            plan_objects += plan.land_use_points
            plan_objects += plan.other_points

        plan_dictionary["generalRegulationGroups"] = [
            self.get_plan_regulation_group(regulation_group, general=True)
            for regulation_group in plan.general_plan_regulation_groups
        ]

        # Our plans have lots of different plan objects, each of which has one plan
        # regulation group.
        plan_dictionary["planObjects"] = self.get_plan_object_dicts(plan_objects)
        plan_dictionary["planRegulationGroups"] = self.get_plan_regulation_groups(
            plan_objects
        )
        plan_dictionary["planRegulationGroupRelations"] = (
            self.get_plan_regulation_group_relations(plan_objects)
        )

        # we should only have one valid period. If there are several, pick last
        plan_dictionary["periodOfValidity"] = self.get_last_period(
            self.get_lifecycle_periods(plan, self.valid_status_value, datetimes=False)
        )
        # we should only have one approved period. If there are several, pick last
        period_of_approval = self.get_last_period(
            self.get_lifecycle_periods(
                plan, self.approved_status_value, datetimes=False
            )
        )
        plan_dictionary["approvalDate"] = (
            period_of_approval["begin"] if period_of_approval else None
        )

        # Documents are divided into different categories. They may only be added
        # to plan *after* they have been uploaded.
        plan_dictionary["planMaps"] = []
        plan_dictionary["planAnnexes"] = []
        plan_dictionary["otherPlanMaterials"] = []
        plan_dictionary["planReport"] = None

        return plan_dictionary

    def get_plan_dictionaries(self) -> dict[UUID, RyhtiPlan]:
        """Construct a dict of valid Ryhti compatible plan dictionaries from plans in the
        local database.
        """
        plan_dictionaries = {}
        for plan_id, plan in self.plans.items():
            plan_dictionaries[plan_id] = self.get_plan_dictionary(plan)
        return plan_dictionaries

    def get_plan_map(self, document: models.Document) -> dict:
        """Construct a dict of single Ryhti compatible plan map."""
        plan_map: dict[str, Any] = {}
        plan_map["planMapKey"] = document.id
        plan_map["name"] = document.name
        plan_map["fileKey"] = (
            str(document.exported_file_key) if document.exported_file_key else None
        )
        # TODO: Take the coordinate system from the actual file?
        plan_map["coordinateSystem"] = (
            f"http://uri.suomi.fi/codelist/rakrek/ETRS89/code/EPSG{str(base.PROJECT_SRID)}"  # noqa
        )
        return plan_map

    def get_plan_attachment_document(self, document: models.Document) -> dict:
        """Construct a dict of single Ryhti compatible plan attachment document."""
        attachment_document: dict[str, Any] = {}
        attachment_document["attachmentDocumentKey"] = document.id
        attachment_document["documentIdentifier"] = (
            document.permanent_document_identifier
        )
        attachment_document["name"] = document.name
        attachment_document["personalDataContent"] = document.personal_data_content.uri
        attachment_document["categoryOfPublicity"] = document.category_of_publicity.uri
        attachment_document["accessibility"] = document.accessibility
        attachment_document["retentionTime"] = document.retention_time.uri
        attachment_document["languages"] = [document.language.uri]
        attachment_document["fileKey"] = (
            str(document.exported_file_key) if document.exported_file_key else None
        )
        attachment_document["documentDate"] = self.get_date(document.document_date)
        if document.arrival_date:
            attachment_document["arrivedDate"] = self.get_date(document.arrival_date)
        attachment_document["typeOfAttachment"] = document.type_of_document.uri
        return attachment_document

    def get_other_plan_material(self, document: models.Document) -> dict:
        """Construct a dict of single Ryhti compatible other plan material item."""
        other_plan_material: dict[str, Any] = {}
        other_plan_material["otherPlanMaterialKey"] = document.id
        other_plan_material["name"] = document.name
        other_plan_material["fileKey"] = (
            str(document.exported_file_key) if document.exported_file_key else None
        )
        other_plan_material["personalDataContent"] = document.personal_data_content.uri
        other_plan_material["categoryOfPublicity"] = document.category_of_publicity.uri
        return other_plan_material

    def add_plan_report_to_plan_dict(
        self, document: models.Document, plan_dictionary: RyhtiPlan
    ) -> RyhtiPlan:
        """Construct a dict of single Ryhti compatible plan report and add it to the
        provided plan dict. The plan dict may already have existing plan reports.
        """
        if not plan_dictionary["planReport"]:
            plan_dictionary["planReport"] = {
                "planReportKey": str(uuid4()),
                "attachmentDocuments": [self.get_plan_attachment_document(document)],
            }
        else:
            plan_dictionary["planReport"]["attachmentDocuments"].append(
                self.get_plan_attachment_document(document)
            )
        return plan_dictionary

    def add_document_to_plan_dict(
        self, document: models.Document, plan_dictionary: RyhtiPlan
    ) -> RyhtiPlan:
        """Construct a dict of single Ryhti compatible plan document and add it to the
        provided plan dict.

        The exact type of the dictionary to be added depends on the document type.
        """
        if document.type_of_document.value == "03":
            # Kaavakartta
            plan_dictionary["planMaps"].append(self.get_plan_map(document))
        elif document.type_of_document.value == "06":
            # Kaavaselostus
            # For some reason, if there are multiple plan reports, they will have to be
            # added inside a single plan report instead of a list of plan reports.
            plan_dictionary = self.add_plan_report_to_plan_dict(
                document, plan_dictionary
            )
        elif document.type_of_document.value == "99":
            # Muu asiakirja
            plan_dictionary["otherPlanMaterials"].append(
                self.get_other_plan_material(document)
            )
        else:
            # Kaavan liite
            plan_dictionary["planAnnexes"].append(
                self.get_plan_attachment_document(document)
            )
        return plan_dictionary

    def get_plan_decisions(self, plan: models.Plan) -> list[RyhtiPlanDecision]:
        """Construct a list of Ryhti compatible plan decisions from plan in the local
        database.
        """
        decisions: list[RyhtiPlanDecision] = []
        # Decision name must correspond to the phase the plan is in. This requires
        # mapping from lifecycle statuses to decision names.
        print(decisions_by_status.get(plan.lifecycle_status.value, []))
        for decision_value in decisions_by_status.get(plan.lifecycle_status.value, []):
            entry = RyhtiPlanDecision()
            # TODO: Let's just have random uuid for now, on the assumption that each
            # phase is only POSTed to ryhti once. If planners need to post and repost
            # the same phase, script needs logic to check if the phase exists in Ryhti
            # already before reposting.
            entry["planDecisionKey"] = str(uuid4())
            entry["name"] = get_code_uri(NameOfPlanCaseDecision, decision_value)
            entry["typeOfDecisionMaker"] = get_code_uri(
                TypeOfDecisionMaker,
                decisionmaker_by_status[plan.lifecycle_status.value],
            )
            # Plan must be embedded in decision when POSTing!
            entry["plans"] = [self.plan_dictionaries[plan.id]]

            try:
                lifecycle_date = self.get_lifecycle_dates_for_status(
                    plan, plan.lifecycle_status.value
                )[-1]
            except IndexError:
                # If we have an old plan with no phase data, we cannot add decisions.
                LOGGER.warning(
                    "Error in plan! Current lifecycle status is missing start date."
                )
                continue
            # Decision date will be
            # 1) decision date if found in database or, if not found,
            # 2) start of the current status period is used as backup.
            # TODO: Remove 2) once QGIS makes sure all necessary dates are filled in
            # manually (or automatically).
            period_of_decision = self.get_last_period(
                self.get_event_periods(
                    lifecycle_date,
                    NameOfPlanCaseDecision,
                    decision_value,
                    datetimes=False,
                )
            )
            period_of_current_status = self.get_periods(
                [lifecycle_date], datetimes=False
            )[-1]
            # Decision has no duration:
            entry["decisionDate"] = (
                period_of_decision["begin"]
                if period_of_decision
                else period_of_current_status["begin"]
            )
            entry["dateOfDecision"] = entry["decisionDate"]

            decisions.append(entry)
        return decisions

    def get_plan_handling_events(self, plan: models.Plan) -> list[RyhtiHandlingEvent]:
        """Construct a list of Ryhti compatible plan handling events from plan in the local
        database.
        """
        events: list[RyhtiHandlingEvent] = []
        # Decision name must correspond to the phase the plan is in. This requires
        # mapping from lifecycle statuses to decision names.
        for event_value in processing_events_by_status.get(
            plan.lifecycle_status.value, []
        ):
            entry = RyhtiHandlingEvent()
            # TODO: Let's just have random uuid for now, on the assumption that each
            # phase is only POSTed to ryhti once. If planners need to post and repost
            # the same phase, script needs logic to check if the phase exists in Ryhti
            # already before reposting.
            entry["handlingEventKey"] = str(uuid4())
            entry["handlingEventType"] = get_code_uri(
                TypeOfProcessingEvent, event_value
            )

            try:
                lifecycle_date = self.get_lifecycle_dates_for_status(
                    plan, plan.lifecycle_status.value
                )[-1]
            except IndexError:
                # If we have an old plan with no phase data, we cannot add any events.
                LOGGER.warning(
                    "Error in plan! Current lifecycle status is missing start date."
                )
                continue
            # Handling event date will be
            # 1) handling event date if found in database or, if not found,
            # 2) start of the current status period is used as backup.
            # TODO: Remove 2) once QGIS makes sure all necessary dates are filled in
            # manually (or automatically).
            period_of_handling_event = self.get_last_period(
                self.get_event_periods(
                    lifecycle_date, TypeOfProcessingEvent, event_value, datetimes=False
                )
            )
            period_of_current_status = self.get_periods(
                [lifecycle_date], datetimes=False
            )[-1]
            # Handling event has no duration:
            entry["eventTime"] = (
                period_of_handling_event["begin"]
                if period_of_handling_event
                else period_of_current_status["begin"]
            )
            entry["cancelled"] = False

            events.append(entry)
        return events

    def get_interaction_events(self, plan: models.Plan) -> list[RyhtiInteractionEvent]:
        """Construct a list of Ryhti compatible interaction events from plan in the local
        database.
        """
        events: list[RyhtiInteractionEvent] = []
        # Decision name must correspond to the phase the plan is in. This requires
        # mapping from lifecycle statuses to decision names.
        for event_value in interaction_events_by_status.get(
            plan.lifecycle_status.value, []
        ):
            entry = RyhtiInteractionEvent()
            # TODO: Let's just have random uuid for now, on the assumption that each
            # phase is only POSTed to ryhti once. If planners need to post and repost
            # the same phase, script needs logic to check if the phase exists in Ryhti
            # already before reposting.
            entry["interactionEventKey"] = str(uuid4())
            entry["interactionEventType"] = get_code_uri(
                TypeOfInteractionEvent, event_value
            )

            try:
                lifecycle_date = self.get_lifecycle_dates_for_status(
                    plan, plan.lifecycle_status.value
                )[-1]
            except IndexError:
                # If we have an old plan with no phase data, we cannot add any events.
                LOGGER.warning(
                    "Error in plan! Current lifecycle status is missing start date."
                )
                continue
            # Interaction event period will be
            # 1) interaction event period if found in database or, if not found,
            # 2) 30 days at start of the current status period (nähtävilläoloaika) are
            # used as backup.
            # TODO: Remove 2) once QGIS makes sure all necessary dates are filled in
            # manually (or automatically).
            period_of_interaction_event = self.get_last_period(
                self.get_event_periods(
                    lifecycle_date, TypeOfInteractionEvent, event_value
                )
            )
            period_of_current_status = self.get_periods([lifecycle_date])[-1]
            entry["eventTime"] = (
                period_of_interaction_event
                if period_of_interaction_event
                else {
                    "begin": (period_of_current_status["begin"]),
                    "end": (
                        datetime.datetime.fromisoformat(
                            period_of_current_status["begin"]
                        )
                        + datetime.timedelta(days=30)
                    )
                    .isoformat()
                    .replace("+00:00", "Z"),
                }
            )

            events.append(entry)
        return events

    def get_plan_matter_phases(self, plan: models.Plan) -> list[RyhtiPlanMatterPhase]:
        """Construct a list of Ryhti compatible plan matter phases from plan in the local
        database.

        Currently, we only return the *current* phase, because our database does *not*
        save plan history between phases. However, we could return multiple phases or
        multiple decisions in the future, if there is a need to POST all the dates
        saved in the lifecycle_dates table.

        TODO: perhaps we will have to return multiple phases, if there may be multiple
        decision or multiple processing events in this phase. However, if we are only
        returning one phase per phase, then let's just return one phase. Simple, isn't
        it?
        """
        phase = RyhtiPlanMatterPhase()
        # TODO: Let's just have random uuid for now, on the assumption that each phase
        # is only POSTed to ryhti once. If planners need to post and repost the same
        # phase, script needs logic to check if the phase exists in Ryhti already before
        # reposting.
        #
        # However, such logic may not be forthcoming, if multiple phases with
        # the same lifecycle status are allowed??
        phase["planMatterPhaseKey"] = str(uuid4())
        # Always post phase and plan with the same status.
        phase["lifeCycleStatus"] = self.plan_dictionaries[plan.id]["lifeCycleStatus"]
        phase["geographicalArea"] = self.plan_dictionaries[plan.id]["geographicalArea"]

        # TODO: currently, the API spec only allows for one plan decision per phase,
        # for reasons unknown. Therefore, let's pick the first possible decision in
        # each phase.
        plan_decisions = self.get_plan_decisions(plan)
        phase["planDecision"] = plan_decisions[0] if plan_decisions else None
        # TODO: currently, the API spec only allows for one plan handling event per
        # phase, for reasons unknown. Therefore, let's pick the first possible event in
        # each phase.
        handling_events = self.get_plan_handling_events(plan)
        phase["handlingEvent"] = handling_events[0] if handling_events else None
        interaction_events = self.get_interaction_events(plan)
        phase["interactionEvents"] = interaction_events if interaction_events else None

        return [phase]

    def get_source_datas(self, plan: models.Plan) -> list[dict]:
        """Construct a list of Ryhti compatible source datas from plan in the local
        database.
        """
        # TODO
        return []

    def get_plan_matter(self, plan: models.Plan) -> RyhtiPlanMatter:
        """Construct a dict of single Ryhti compatible plan matter from plan in the local
        database.
        """
        plan_matter = RyhtiPlanMatter()

        # TODO: permanentPlanIdentifier should be mandatory in this stage
        plan_matter["permanentPlanIdentifier"] = plan.permanent_plan_identifier

        # Plan type has to be proper URI (not just value) here, *unlike* when only
        # validating plan. Go figure.
        plan_matter["planType"] = plan.plan_type.uri
        # For reasons unknown, name is needed for plan matter but not for plan. Plan
        # only contains description, and only in one language.
        plan_matter["name"] = plan.name

        # we should only have one pending period. If there are several, pick last
        dates_of_initiation = self.get_last_period(
            self.get_lifecycle_periods(plan, self.pending_status_value, datetimes=False)
        )
        plan_matter["timeOfInitiation"] = (
            dates_of_initiation["begin"] if dates_of_initiation else None
        )
        # Hooray, unlike plan, the plan *matter* description allows multilanguage data!
        plan_matter["description"] = plan.description
        plan_matter["producerPlanIdentifier"] = plan.producers_plan_identifier
        plan_matter["caseIdentifiers"] = (
            [plan.matter_management_identifier]
            if plan.matter_management_identifier
            else []
        )
        plan_matter["recordNumbers"] = (
            [plan.record_number] if plan.record_number else []
        )
        # Apparently Ryhti plans may cover multiple administrative areas, so the region
        # identifier has to be embedded in a list.
        plan_matter["administrativeAreaIdentifiers"] = [
            (
                plan.organisation.municipality.value
                if plan.organisation.municipality
                else plan.organisation.administrative_region.value
            )
        ]
        # We have no need of importing the digital origin code list as long as we are
        # not digitizing old plans:
        plan_matter["digitalOrigin"] = (
            "http://uri.suomi.fi/codelist/rytj/RY_DigitaalinenAlkupera/code/01"
        )
        # TODO: kaava-asian liitteet
        # are these different from plan annexes? why? how??
        # plan_matter["matterAnnexes"] = self.get_plan_matter_annexes(plan)
        # TODO: lähdeaineistot
        # plan_matter["sourceDatas"] = self.get_source_datas(plan)
        plan_matter["planMatterPhases"] = self.get_plan_matter_phases(plan)
        return plan_matter

    def get_plan_matters(self) -> dict[UUID, RyhtiPlanMatter]:
        """Construct a dict of Ryhti compatible plan matters from plans with
        permanent identifiers in the local database. In case plan has no
        permanent identifier, it is not included in the dict.
        """
        return {plan.id: self.get_plan_matter(plan) for plan in self.plans.values()}

    def save_plan_validation_responses(
        self, responses: dict[UUID, "RyhtiResponse"]
    ) -> dict[UUID, str]:
        """Save open validation API response data to the database and return lambda
        response.

        If validation is successful, update validated_at field and validation_errors
        field

        If validation/post is unsuccessful, save the error JSON in plan
        validation_errors json field (in addition to saving it to AWS logs and
        returning them in lambda return value).

        If Ryhti request fails unexpectedly, save the returned error.
        """
        details: dict[UUID, str] = {}
        with self.Session(expire_on_commit=False) as session:
            for plan_id, response in responses.items():
                # Refetch plan from db in case it has been deleted
                plan = session.get(models.Plan, plan_id)
                if not plan:
                    # Plan has been deleted in the middle of validation. Nothing
                    # to see here, move on
                    LOGGER.info(
                        f"Plan {plan_id} no longer found in database! Moving on"
                    )
                    continue
                LOGGER.info(f"Saving response for plan {plan_id}...")
                LOGGER.info(response)
                # In case Ryhti API does not respond in the expected manner,
                # save the response for debugging.
                if "status" not in response or "errors" not in response:
                    details[plan_id] = (
                        f"RYHTI API returned unexpected response: {response}"
                    )
                    plan.validation_errors = f"RYHTI API ERROR: {response}"
                    LOGGER.info(details[plan_id])
                    LOGGER.info(f"Ryhti response: {json.dumps(response)}")
                    continue
                if response["status"] == 200:
                    details[plan_id] = f"Plan validation successful for {plan_id}!"
                    plan.validation_errors = (
                        "Kaava on validi. Kaava-asiaa ei ole vielä validoitu."
                    )
                else:
                    details[plan_id] = f"Plan validation FAILED for {plan_id}."
                    plan.validation_errors = response["errors"]

                LOGGER.info(details[plan_id])
                LOGGER.info(f"Ryhti response: {json.dumps(response)}")
                plan.validated_at = datetime.datetime.now(tz=LOCAL_TZ)
            session.commit()
        return details

    def set_plan_documents(self, responses: dict[UUID, list["RyhtiResponse"]]) -> None:
        """Save uploaded plan document keys, export times and etags to the database.
        Also, append document data to the plan dictionaries.
        """
        with self.Session(expire_on_commit=False) as session:
            for plan_id, response in responses.items():
                # Make sure that the plan in the plans dict stays up to date
                plan = self.plans[plan_id]
                session.add(plan)
                for document, document_response in zip(
                    plan.documents, response, strict=True
                ):
                    session.add(document)
                    if document_response["status"] == 201:
                        document.exported_file_key = UUID(document_response["detail"])
                        document.exported_at = datetime.datetime.now(tz=LOCAL_TZ)
                        # Save the etag of the uploaded file, piggybacked in response
                        if document_response["warnings"]:
                            document.exported_file_etag = document_response["warnings"][
                                "ETag"
                            ]
                    # We can only serialize the document after it has been uploaded
                    self.add_document_to_plan_dict(
                        document, self.plan_dictionaries[plan_id]
                    )
                session.commit()

    def set_permanent_plan_identifiers(
        self, responses: dict[UUID, "RyhtiResponse"]
    ) -> dict[UUID, str]:
        """Save permanent plan identifiers returned by RYHTI API to the database and
        return lambda response.
        """
        details: dict[UUID, str] = {}
        with self.Session(expire_on_commit=False) as session:
            for plan_id, response in responses.items():
                # Make sure that the plan dict stays up to date
                plan = self.plans[plan_id]
                session.add(plan)
                if response["status"] == 200:
                    plan.permanent_plan_identifier = response["detail"]
                    details[plan_id] = response["detail"]  # type: ignore[assignment]
                elif response["status"] == 401:
                    details[plan_id] = (
                        "Sinulla ei ole oikeuksia luoda kaavaa tälle alueelle."
                    )
                elif response["status"] == 400:
                    details[plan_id] = "Kaavalta puuttuu tuottajan kaavatunnus."
            session.commit()
        return details

    def save_plan_matter_validation_responses(
        self, responses: dict[UUID, "RyhtiResponse"]
    ) -> dict[UUID, str]:
        """Save X-Road validation API response data to the database and return lambda
        response.

        If validation is successful, update validated_at field and validation_errors
        field.

        If validation/post is unsuccessful, save the error JSON in plan
        validation_errors json field (in addition to saving it to AWS logs and
        returning them in lambda return value).

        If Ryhti request fails unexpectedly, save the returned error.
        """
        details: dict[UUID, str] = {}
        with self.Session(expire_on_commit=False) as session:
            for plan_id in self.plans:
                plan: models.Plan | None = session.get(models.Plan, plan_id)
                if not plan:
                    # Plan has been deleted in the middle of validation. Nothing
                    # to see here, move on
                    LOGGER.info(
                        f"Plan {plan_id} no longer found in database! Moving on"
                    )
                    continue
                response = responses.get(plan_id)
                if not response:
                    # Return error message if we had no plan matter
                    details[plan_id] = (
                        f"Plan {plan_id} had no permanent identifier. "
                        "Could not create plan matter!"
                    )
                    plan.validation_errors = details[plan_id]
                    LOGGER.info(details[plan_id])
                    continue
                LOGGER.info(f"Saving response for plan matter {plan_id}...")
                LOGGER.info(response)
                # In case Ryhti API does not respond in the expected manner,
                # save the response for debugging.
                if "status" not in response or "errors" not in response:
                    details[plan_id] = (
                        f"RYHTI API returned unexpected response: {response}"
                    )
                    plan.validation_errors = f"RYHTI API ERROR: {response}"
                    LOGGER.info(details[plan_id])
                    LOGGER.info(f"Ryhti response: {json.dumps(response)}")
                    continue
                if response["status"] == 200:
                    details[plan_id] = (
                        f"Plan matter validation successful for {plan_id}!"
                    )
                    plan.validation_errors = (
                        "Kaava-asia on validi ja sen voi viedä Ryhtiin."
                    )
                else:
                    details[plan_id] = f"Plan matter validation FAILED for {plan_id}."
                    plan.validation_errors = response["errors"]

                LOGGER.info(details[plan_id])
                LOGGER.info(f"Ryhti response: {json.dumps(response)}")
                plan.validated_at = datetime.datetime.now(tz=LOCAL_TZ)
            session.commit()
        return details

    def save_plan_matter_post_responses(
        self, responses: dict[UUID, "RyhtiResponse"]
    ) -> dict[UUID, str]:
        """Save X-Road API POST response data to the database and return lambda response.

        If POST is successful, update exported_at and validated_at fields.

        If POST is unsuccessful, save the error JSON in plan
        validation_errors json field (in addition to saving it to AWS logs and
        returning them in lambda return value).

        If Ryhti request fails unexpectedly, save the returned error.
        """
        details: dict[UUID, str] = {}
        with self.Session(expire_on_commit=False) as session:
            for plan_id in self.plans:
                plan: models.Plan | None = session.get(models.Plan, plan_id)
                if not plan:
                    # Plan has been deleted in the middle of POST. Nothing
                    # to see here, move on
                    LOGGER.info(
                        f"Plan {plan_id} no longer found in database! Moving on"
                    )
                    continue
                response = responses.get(plan_id)
                if not response:
                    # Return error message if we had no plan matter
                    details[plan_id] = (
                        f"Plan {plan_id} had no permanent identifier. "
                        "Could not create plan matter!"
                    )
                    LOGGER.info(details[plan_id])
                    continue
                LOGGER.info(f"Saving response for plan matter {plan_id}...")
                LOGGER.info(response)
                # In case Ryhti API does not respond in the expected manner,
                # save the response for debugging.
                if "status" not in response or "errors" not in response:
                    details[plan_id] = (
                        f"RYHTI API returned unexpected response: {response}"
                    )
                    plan.validation_errors = f"RYHTI API ERROR: {response}"
                elif response["status"] == 200:
                    details[plan_id] = (
                        f"Plan matter phase PUT successful for {plan_id}!"
                    )
                    plan.validation_errors = "Kaava-asian vaihe on päivitetty Ryhtiin."
                    plan.validated_at = datetime.datetime.now(tz=LOCAL_TZ)
                    plan.exported_at = datetime.datetime.now(tz=LOCAL_TZ)
                elif response["status"] == 201:
                    details[plan_id] = (
                        "Plan matter or plan matter phase POST successful for "
                        + str(plan_id)
                        + "."
                    )
                    plan.validation_errors = "Uusi kaava-asian vaihe on viety Ryhtiin."
                    plan.validated_at = datetime.datetime.now(tz=LOCAL_TZ)
                    plan.exported_at = datetime.datetime.now(tz=LOCAL_TZ)
                else:
                    details[plan_id] = f"Plan matter POST FAILED for {plan_id}!"
                    plan.validation_errors = response["errors"]
                    plan.validated_at = datetime.datetime.now(tz=LOCAL_TZ)

                LOGGER.info(details[plan_id])
                LOGGER.info(f"Ryhti response: {json.dumps(response)}")
            session.commit()
        return details

    def import_plan(
        self, plan_json: str, extra_data: dict, overwrite: bool = False
    ) -> UUID | None:
        ryhti_plan = ryhti_plan_from_json(plan_json)
        plan_matter_data = plan_matter_data_from_extra_data_dict(extra_data)

        with self.Session(autoflush=False, expire_on_commit=False) as session:
            existing_plan = session.get(models.Plan, ryhti_plan.plan_key)
            if existing_plan:
                if overwrite is True:
                    session.delete(existing_plan)
                    session.flush()
                else:
                    raise PlanAlreadyExistsError(ryhti_plan.plan_key)

            desesrializer = Deserializer(session)
            plan = desesrializer.deserialise_ryhti_plan(ryhti_plan, plan_matter_data)

            session.add(plan)
            session.commit()

        return plan.id
