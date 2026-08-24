"""Serialize ARHO ORM models into Ryhti API plan payloads.

Counterpart of deserializer.py, which reads Ryhti JSON into ORM models.
"""

from __future__ import annotations

import datetime
import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, ClassVar, Protocol, cast
from uuid import uuid4
from zoneinfo import ZoneInfo

import simplejson as json
from geoalchemy2.shape import to_shape
from shapely import to_geojson
from sqlalchemy import and_, func, select, text
from sqlalchemy.exc import MultipleResultsFound
from sqlalchemy.orm import defer, raiseload

from database import base, models
from database.enums import AttributeValueDataType
from ryhti_client.profiling import log_duration
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

LOGGER = logging.getLogger(__name__)

LOCAL_TZ = ZoneInfo("Europe/Helsinki")

# Plan objects live in four tables. They are serialized in this order.
PLAN_OBJECT_MODELS: tuple[type[models.PlanObjectBase], ...] = (
    models.LandUseArea,
    models.OtherArea,
    models.Line,
    models.Point,
)
# ST_AsGeoJSON prints coordinates with this many decimals. 15 gives the same digits
# as shapely to_geojson, so the exported geometry does not change.
GEOJSON_MAX_DECIMALS = 15
# ST_AsGeoJSON option 0 leaves out the crs member, just like shapely does.
GEOJSON_WITHOUT_CRS = 0


class Geometrical(Protocol):
    geom: WKBElement
    __table__: ClassVar[FromClause]


@dataclass(frozen=True)
class LoadedPlanObjects:
    """Everything the serializer needs about the plan objects of one plan.

    The geometries and the regulation groups are fetched for the whole plan at once,
    because a plan may have tens of thousands of objects but only a handful of groups.
    """

    plan_objects: list[models.PlanObjectBase]
    # Geojson rendered by PostGIS, by plan object id.
    geojson_by_id: dict[DbId, str]
    # Regulation groups of each plan object, ordered, by plan object id. Plan objects
    # with no regulation group are absent.
    groups_by_object: dict[DbId, list[models.PlanRegulationGroup]]


class PlanSerializer:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self.Session = session_factory
        # SRIDs of every geometry column, by schema and table name. Filled on demand.
        self._srids_by_schema: dict[str, dict[str, int]] = {}

    def _load_srids_of_schema(self, schema: str) -> dict[str, int]:
        """Reads the SRID of every geometry column in the schema, in one query."""
        with self.Session() as session:
            rows = session.execute(
                text(
                    "SELECT f_table_name, srid FROM public.geometry_columns "
                    "WHERE f_table_schema = :schema"
                ),
                {"schema": schema},
            )
            return {table_name: int(srid) for table_name, srid in rows}

    def _get_srid_of_table(self, table: Table) -> int:
        """Returns the SRID of the geometry column of the table.

        The SRID has to come from the database, not from the model, because a
        customer database may have been changed to another SRID after the migrations.
        The values are cached, so a plan with thousands of objects still needs only
        one query.
        """
        if not table.schema:
            raise ValueError(f"Table {table.name} does not have a schema defined.")
        if table.schema not in self._srids_by_schema:
            self._srids_by_schema[table.schema] = self._load_srids_of_schema(
                table.schema
            )
        srid = self._srids_by_schema[table.schema].get(table.name)
        if srid is None:
            raise ValueError(
                f"Table {table.schema}.{table.name} has no geometry column "
                f"in the database."
            )
        return srid

    def _format_geometry(self, geojson: str, table: Table) -> dict[str, Any]:
        """Returns Ryhti formatted geom dict with the correct SRID and the geojson
        as a dict.

        It seems that geojson carries no SRID information, so we have to paste the
        SRID back manually :/
        """
        # PostGIS prints a whole coordinate without a decimal point, shapely prints it
        # as a float. parse_int keeps every coordinate a float, whatever the source.
        geometry = json.loads(geojson, parse_int=float)
        if not geometry["type"].startswith("Multi"):
            raise TypeError(f"Geometry is not multigeometry: {geometry['type']}")
        if len(geometry["coordinates"]) == 1:
            # Ryhti API may not allow single geometries in multigeometries in all cases.
            # Let's make them into single geometries instead:
            geometry = {
                "type": geometry["type"].removeprefix("Multi"),
                "coordinates": geometry["coordinates"][0],
            }
        # We don't want to serialize the geojson quite yet, so it stays a dict until
        # we are ready to reserialize it :/
        return {"srid": str(self._get_srid_of_table(table)), "geometry": geometry}

    def get_geometry_as_json(self, obj: Geometrical) -> dict[str, Any]:
        """Returns Ryhti formatted geom dict for a single object.

        Plan objects get their geojson from PostGIS instead, see _load_plan_objects.
        Converting one geometry in python is cheaper than an extra database query.
        """
        return self._format_geometry(
            to_geojson(to_shape(obj.geom)), cast("Table", obj.__table__)
        )

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
        geojson: str,
        containing_land_use_area_ids: Mapping[DbId, DbId],
    ) -> dict:
        """Construct a dict of Ryhti compatible plan object."""
        plan_object_dict: dict[str, Any] = {}
        plan_object_dict["planObjectKey"] = plan_object.id
        plan_object_dict["lifeCycleStatus"] = plan_object.lifecycle_status.uri
        plan_object_dict["undergroundStatus"] = plan_object.type_of_underground.uri
        plan_object_dict["geometry"] = self._format_geometry(
            geojson, cast("Table", plan_object.__table__)
        )
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
        self,
        plan_object: models.PlanObjectBase,
        groups: list[models.PlanRegulationGroup],
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
            for group in groups
            for regulation in group.plan_regulations
        )

    def _get_containing_land_use_area_ids(
        self,
        plan_objects: list[models.PlanObjectBase],
        groups_by_object: Mapping[DbId, list[models.PlanRegulationGroup]],
    ) -> dict[DbId, DbId]:
        """Returns {plan object id: id of the land use area that contains it} for
        plan objects that need a containing land use area.

        Plan objects with no containing land use area are absent from the mapping.

        Raises MultipleResultsFound if several land use areas contain the same
        plan object.
        """
        ids_by_model: dict[type[models.PlanObjectBase], list[DbId]] = {}
        for plan_object in plan_objects:
            groups = groups_by_object.get(plan_object.id, [])
            if self._needs_containing_land_use_area(plan_object, groups):
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

    def get_plan_object_dicts(self, loaded: LoadedPlanObjects) -> list:
        """Construct a list of Ryhti compatible plan object dicts from plan objects
        in the local database.
        """
        containing_land_use_area_ids = self._get_containing_land_use_area_ids(
            loaded.plan_objects, loaded.groups_by_object
        )
        return [
            self.get_plan_object(
                plan_object,
                loaded.geojson_by_id[plan_object.id],
                containing_land_use_area_ids,
            )
            for plan_object in loaded.plan_objects
        ]

    def get_plan_regulation_groups(self, loaded: LoadedPlanObjects) -> list[dict]:
        """Construct a list of Ryhti compatible plan regulation groups from plan objects
        in the local database.
        """
        # The groups are already loaded for the whole plan, so there is no need to
        # query them again. List each group only once.
        groups_by_id: dict[DbId, models.PlanRegulationGroup] = {}
        for plan_object in loaded.plan_objects:
            for regulation_group in loaded.groups_by_object.get(plan_object.id, []):
                groups_by_id.setdefault(regulation_group.id, regulation_group)
        # Sort by ordering, nulls last, like ORDER BY in the database.
        ordered_groups = sorted(
            groups_by_id.values(),
            key=lambda group: (group.ordering is None, group.ordering or 0),
        )
        LOGGER.info("arho_export regulation_groups=%d", len(ordered_groups))
        return [self.get_plan_regulation_group(group) for group in ordered_groups]

    def _load_plan_objects(
        self, session: Session, plan: models.Plan
    ) -> LoadedPlanObjects:
        """Load the plan objects of a plan with everything the serializer needs.

        PostGIS renders the geometry as geojson, which is much cheaper than reading the
        WKB into shapely, and the WKB is not transferred at all. The regulation groups
        are fetched once for the whole plan, because loading them through every single
        plan object is slow for plans with tens of thousands of objects.
        """
        association = models.regulation_group_association
        plan_objects: list[models.PlanObjectBase] = []
        geojson_by_id: dict[DbId, str] = {}
        group_ids_by_object: dict[DbId, list[DbId]] = {}
        counts: dict[str, int] = {}

        for model in PLAN_OBJECT_MODELS:
            object_rows = session.execute(
                select(
                    model,
                    func.ST_AsGeoJSON(
                        model.geom, GEOJSON_MAX_DECIMALS, GEOJSON_WITHOUT_CRS
                    ),
                )
                # The geometry is only needed as geojson, and the groups are loaded
                # below. raiseload is loud if some other code still walks them.
                .options(defer(model.geom), raiseload(model.plan_regulation_groups))
                .where(model.plan_id == plan.id)
                .order_by(model.ordering)
            )
            objects_of_model: list[models.PlanObjectBase] = []
            for plan_object, geojson in object_rows:
                objects_of_model.append(plan_object)
                geojson_by_id[plan_object.id] = geojson
            plan_objects += objects_of_model
            counts[model.__tablename__] = len(objects_of_model)

            # The association table has one foreign key column per plan object table.
            plan_object_id = association.c[f"{model.__tablename__}_id"]
            group_rows = session.execute(
                select(plan_object_id, association.c.plan_regulation_group_id)
                .select_from(association)
                .join(model, model.id == plan_object_id)
                .join(
                    models.PlanRegulationGroup,
                    models.PlanRegulationGroup.id
                    == association.c.plan_regulation_group_id,
                )
                .where(model.plan_id == plan.id)
                .order_by(models.PlanRegulationGroup.ordering)
            )
            for object_id, group_id in group_rows:
                group_ids_by_object.setdefault(object_id, []).append(group_id)

        # The object counts are needed to make sense of the step durations.
        LOGGER.info(
            "arho_export plan=%s %s",
            plan.id,
            " ".join(f"{table}s={count}" for table, count in counts.items()),
        )

        group_ids = {
            group_id for ids in group_ids_by_object.values() for group_id in ids
        }
        groups_by_id = {
            group.id: group
            for group in session.scalars(
                select(models.PlanRegulationGroup).where(
                    models.PlanRegulationGroup.id.in_(group_ids)
                )
            )
        }
        return LoadedPlanObjects(
            plan_objects=plan_objects,
            geojson_by_id=geojson_by_id,
            groups_by_object={
                object_id: [groups_by_id[group_id] for group_id in ids]
                for object_id, ids in group_ids_by_object.items()
            },
        )

    def get_plan_regulation_group_relations(
        self, loaded: LoadedPlanObjects
    ) -> list[dict[str, DbId]]:
        """Construct a list of Ryhti compatible plan regulation group relations from plan
        objects in the local database.
        """
        return [
            {
                "planObjectKey": plan_object.id,
                "planRegulationGroupKey": regulation_group.id,
            }
            for plan_object in loaded.plan_objects
            for regulation_group in loaded.groups_by_object.get(plan_object.id, [])
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
        with (
            log_duration("load_plan_objects"),
            self.Session(expire_on_commit=False) as session,
        ):
            session.add(plan)
            loaded = self._load_plan_objects(session, plan)

        plan_dictionary["generalRegulationGroups"] = [
            self.get_plan_regulation_group(regulation_group, general=True)
            for regulation_group in plan.general_plan_regulation_groups
        ]

        # Our plans have lots of different plan objects, each of which has one plan
        # regulation group.
        with log_duration("plan_object_dicts"):
            plan_dictionary["planObjects"] = self.get_plan_object_dicts(loaded)
        plan_dictionary["planRegulationGroups"] = self.get_plan_regulation_groups(
            loaded
        )
        plan_dictionary["planRegulationGroupRelations"] = (
            self.get_plan_regulation_group_relations(loaded)
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
