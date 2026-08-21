"""Serialize ARHO ORM models into Ryhti API plan payloads.

Counterpart of deserializer.py, which reads Ryhti JSON into ORM models.
"""

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, Any, ClassVar, Protocol, cast
from uuid import uuid4
from zoneinfo import ZoneInfo

import simplejson as json
from geoalchemy2.shape import to_shape
from shapely import to_geojson
from shapely.geometry.base import BaseMultipartGeometry
from sqlalchemy import and_, select, text
from sqlalchemy.exc import MultipleResultsFound

from database import base, models
from database.enums import AttributeValueDataType
from ryhti_client.ryhti_schema import (
    Period,
    RyhtiAdditionalInformation,
    RyhtiAttributeValue,
    RyhtiPlan,
)

if TYPE_CHECKING:
    from collections.abc import Mapping

    from geoalchemy2 import WKBElement
    from sqlalchemy import Table
    from sqlalchemy.orm import Session, sessionmaker
    from sqlalchemy.sql import FromClause

    from database.base import DbId

LOCAL_TZ = ZoneInfo("Europe/Helsinki")


class Geometrical(Protocol):
    geom: WKBElement
    __table__: ClassVar[FromClause]


class PlanSerializer:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self.Session = session_factory
        self._table_srids: dict[tuple[str, str], int] = {}

    def _get_srid_of_table(self, table: Table) -> int:
        table_schema = table.schema
        table_name = table.name
        if not table_schema:
            raise ValueError(f"Table {table_name} does not have a schema defined.")

        srid = self._table_srids.get((table_schema, table_name))
        if srid is not None:
            return srid

        with self.Session() as session:
            srid = session.execute(
                text(
                    "SELECT srid FROM public.geometry_columns "
                    "WHERE f_table_schema = :schema AND f_table_name = :table"
                ),
                {"schema": table_schema, "table": table_name},
            ).scalar_one()
            self._table_srids[(table_schema, table_name)] = srid
        return srid

    def get_geometry_as_json(self, obj: Geometrical) -> dict[str, Any]:
        """Returns Ryhti formatted geom dict with the correct SRID and
        geometry as geojson
        """
        # We cannot use postgis geojson functions here, because the data has already
        # been fetched from the database. So let's create geojson the python way, it's
        # probably faster than doing extra database queries for the conversion.
        # However, it seems that to_shape forgets to add the SRID information from the
        # EWKB (https://github.com/geoalchemy/geoalchemy2/issues/235), so we have to
        # paste the SRID back manually :/

        shape = to_shape(obj.geom)
        if not isinstance(shape, BaseMultipartGeometry):
            raise TypeError(f"Geometry is not multigeometry: {shape.geom_type}")
        srid = self._get_srid_of_table(cast("Table", obj.__table__))
        if len(shape.geoms) == 1:
            # Ryhti API may not allow single geometries in multigeometries in all cases.
            # Let's make them into single geometries instead:
            shape = shape.geoms[0]
        # Also, we don't want to serialize the geojson quite yet. Looks like the only
        # way to do get python dict to actually convert the json back to dict until we
        # are ready to reserialize it :/
        return {"srid": str(srid), "geometry": json.loads(to_geojson(shape))}

    def get_date(self, datetime_value: datetime.datetime) -> str:
        """Returns isoformatted date for the given datetime in local timezone."""
        return datetime_value.astimezone(LOCAL_TZ).date().isoformat()

    def serialize_date_period(
        self, date_start: datetime.date, date_end: datetime.date | None
    ) -> Period:
        return {
            "begin": date_start.isoformat(),
            "end": date_end.isoformat() if date_end else None,
        }

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

        if plan_recommendation.period_of_validity_start:
            recommendation_dict["periodOfValidity"] = self.serialize_date_period(
                plan_recommendation.period_of_validity_start,
                plan_recommendation.period_of_validity_end,
            )
        recommendation_dict["value"] = self.format_language_string_value(
            plan_recommendation.text_value
        )
        return recommendation_dict

    def get_attribute_value(
        self, attribute_value: base.AttributeValueMixin
    ) -> RyhtiAttributeValue | None:
        if attribute_value.value_data_type is None:
            return None

        value: RyhtiAttributeValue = {"dataType": attribute_value.value_data_type.value}

        def cast_numeric(number: float) -> int | float:
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

        elif attribute_value.value_data_type == AttributeValueDataType.LOCALIZED_TEXT:
            if attribute_value.text_value is not None:
                value["text"] = self.format_language_string_value(
                    attribute_value.text_value
                )
            if attribute_value.text_syntax is not None:
                value["syntax"] = attribute_value.text_syntax

        elif attribute_value.value_data_type == AttributeValueDataType.TEXT:
            if isinstance(
                attribute_value.text_value, str
            ):  # take advantage that jsonb can contain either a "dict" or "string".
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
    ) -> RyhtiAdditionalInformation:
        additional_information_dict: RyhtiAdditionalInformation = {
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

        if plan_regulation.period_of_validity_start:
            regulation_dict["periodOfValidity"] = self.serialize_date_period(
                plan_regulation.period_of_validity_start,
                plan_regulation.period_of_validity_end,
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
        group_dict["titleOfPlanRegulation"] = self.format_language_string_value(
            group.name
        )
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

    def get_plan_object(
        self,
        plan_object: models.PlanObjectBase,
        containing_land_use_area_ids: Mapping[DbId, DbId],
    ) -> dict:
        """Construct a dict of Ryhti compatible plan object."""
        plan_object_dict: dict[str, Any] = {}
        plan_object_dict["planObjectKey"] = plan_object.id
        plan_object_dict["lifeCycleStatus"] = plan_object.lifecycle_status.uri
        plan_object_dict["undergroundStatus"] = plan_object.type_of_underground.uri
        plan_object_dict["geometry"] = self.get_geometry_as_json(plan_object)
        plan_object_dict["name"] = self.format_language_string_value(plan_object.name)
        plan_object_dict["description"] = self.format_language_string_value(
            plan_object.description
        )
        plan_object_dict["objectNumber"] = plan_object.ordering

        if plan_object.period_of_validity_start:
            plan_object_dict["periodOfValidity"] = self.serialize_date_period(
                plan_object.period_of_validity_start, plan_object.period_of_validity_end
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
        related_plan_object_keys = self._get_related_plan_object_keys(
            plan_object, containing_land_use_area_ids
        )
        if related_plan_object_keys:
            plan_object_dict["relatedPlanObjectKeys"] = related_plan_object_keys

        return plan_object_dict

    def format_language_string_value(
        self, field_value: dict[str, str] | None
    ) -> dict[str, str] | None:
        """Formats language string and returns None if empty."""
        if not field_value or not isinstance(field_value, dict):
            return None

        languages = {"fin", "swe", "smn", "sms", "sme", "eng"}
        serialized_str = {
            language: name
            for (language, name) in field_value.items()
            if language in languages and isinstance(name, str) and name
        }

        return serialized_str or None

    def _needs_containing_land_use_area(
        self, plan_object: models.PlanObjectBase
    ) -> bool:
        """Returns True if the plan object needs a containing land use area as related plan
        object based on the validation rule
        58 quality/req-spatialplanregulationtype-reference-spatialplanobject.
        """
        return isinstance(plan_object, (models.OtherArea, models.Point)) and any(
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

    def _get_containing_land_use_area_ids(
        self, plan_objects: list[models.PlanObjectBase]
    ) -> dict[DbId, DbId]:
        """Returns {plan object id: id of the land use area that contains it} for
        plan objects that need a containing land use area.

        Plan objects with no containing land use area are absent from the mapping.

        Raises MultipleResultsFound if several land use areas contain the same
        plan object.
        """
        ids_by_model: dict[type[models.PlanObjectBase], list[DbId]] = {}
        for plan_object in plan_objects:
            if self._needs_containing_land_use_area(plan_object):
                ids_by_model.setdefault(type(plan_object), []).append(plan_object.id)

        if not ids_by_model:
            return {}

        containing_area_ids: dict[DbId, DbId] = {}
        with self.Session(expire_on_commit=False) as session:
            # Plan objects live in separate tables, so one query per table.
            for model, object_ids in ids_by_model.items():
                stmt = (
                    select(
                        model.id.label("plan_object_id"),
                        models.LandUseArea.id.label("land_use_area_id"),
                    )
                    .join(
                        models.LandUseArea,
                        and_(
                            models.LandUseArea.plan_id == model.plan_id,
                            models.LandUseArea.geom.ST_Contains(model.geom),
                        ),
                    )
                    .where(model.id.in_(object_ids))
                )
                for plan_object_id, land_use_area_id in session.execute(stmt):
                    if plan_object_id in containing_area_ids:
                        msg = (
                            "Multiple land use areas contain plan object "
                            f"{plan_object_id}"
                        )
                        raise MultipleResultsFound(msg)
                    containing_area_ids[plan_object_id] = land_use_area_id
        return containing_area_ids

    def _get_related_plan_object_keys(
        self,
        plan_object: models.PlanObjectBase,
        containing_land_use_area_ids: Mapping[DbId, DbId],
    ) -> list[DbId]:
        # TODO: there might be other use cases for related plan objects
        related_plan_object_keys = []

        # Address the validation rule
        # 58: quality/req-spatialplanregulationtype-reference-spatialplanobject
        containing_land_use_area_id = containing_land_use_area_ids.get(plan_object.id)
        if containing_land_use_area_id:
            related_plan_object_keys.append(containing_land_use_area_id)

        return related_plan_object_keys

    def get_plan_object_dicts(self, plan_objects: list[models.PlanObjectBase]) -> list:
        """Construct a list of Ryhti compatible plan object dicts from plan objects
        in the local database.
        """
        containing_land_use_area_ids = self._get_containing_land_use_area_ids(
            plan_objects
        )
        return [
            self.get_plan_object(plan_object, containing_land_use_area_ids)
            for plan_object in plan_objects
        ]

    def get_plan_regulation_groups(
        self, plan_objects: list[models.PlanObjectBase]
    ) -> list[dict]:
        """Construct a list of Ryhti compatible plan regulation groups from plan objects
        in the local database.
        """
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
            group_dicts = [
                self.get_plan_regulation_group(group)
                for group in plan_regulation_groups
            ]

        return group_dicts

    def get_plan_regulation_group_relations(
        self, plan_objects: list[models.PlanObjectBase]
    ) -> list[dict[str, DbId]]:
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
        plan_dictionary["geographicalArea"] = self.get_geometry_as_json(plan)
        # For reasons unknown, Ryhti does not allow multilanguage description.
        plan_description = (
            plan.description.get("fin") if isinstance(plan.description, dict) else None
        )
        if plan_description:
            plan_dictionary["planDescription"] = plan_description
        if plan.official_use_only:
            plan_dictionary["officialUseOnly"] = plan.official_use_only

        # Here come the dependent objects. They are related to the plan directly or
        # via the plan objects, so we better fetch the objects first and then move on.
        plan_objects: list[models.PlanObjectBase] = []
        with self.Session(expire_on_commit=False) as session:
            session.add(plan)
            plan_objects += plan.land_use_areas
            plan_objects += plan.other_areas
            plan_objects += plan.lines
            plan_objects += plan.points

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

        if plan.approval_date:
            plan_dictionary["approvalDate"] = plan.approval_date.isoformat()

        if plan.period_of_validity_start:
            plan_dictionary["periodOfValidity"] = self.serialize_date_period(
                plan.period_of_validity_start, plan.period_of_validity_end
            )

        # Documents are divided into different categories. They may only be added
        # to plan *after* they have been uploaded.
        plan_dictionary["planMaps"] = []
        plan_dictionary["planAnnexes"] = []
        plan_dictionary["otherPlanMaterials"] = []
        plan_dictionary["planReport"] = None

        return plan_dictionary

    def get_plan_map(self, document: models.Document) -> dict:
        """Construct a dict of single Ryhti compatible plan map."""
        plan_map: dict[str, Any] = {}
        plan_map["planMapKey"] = document.id
        plan_map["name"] = self.format_language_string_value(document.name)
        plan_map["fileKey"] = (
            str(document.exported_file_key) if document.exported_file_key else None
        )
        # TODO: Take the coordinate system from the actual file?
        plan_map["coordinateSystem"] = (
            f"http://uri.suomi.fi/codelist/rakrek/ETRS89/code/EPSG{base.PROJECT_SRID!s}"
        )
        return plan_map

    def get_plan_attachment_document(self, document: models.Document) -> dict:
        """Construct a dict of single Ryhti compatible plan attachment document."""
        attachment_document: dict[str, Any] = {}
        attachment_document["attachmentDocumentKey"] = document.id
        attachment_document["documentIdentifier"] = (
            document.permanent_document_identifier
        )
        attachment_document["name"] = self.format_language_string_value(document.name)
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
        other_plan_material["name"] = self.format_language_string_value(document.name)
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
