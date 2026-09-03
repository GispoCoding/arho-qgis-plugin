"""Serialize ARHO ORM models into Ryhti API plan models.

Counterpart of deserializer.py, which reads Ryhti models into ORM models. The Ryhti
models come from the generated ryhti_api_client package, so the serializer builds the
same objects the deserializer reads. The models are pydantic models, so a value the
Ryhti schema does not allow raises a ValidationError already here.

The models are built with the camelCase alias names of the Ryhti JSON, because the
type checkers only know the aliases as constructor arguments. The attributes are read
with their snake_case names.
"""

from __future__ import annotations

import datetime
import json
import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, ClassVar, Protocol, cast
from uuid import UUID, uuid4
from zoneinfo import ZoneInfo

from geoalchemy2.shape import to_shape
from ryhti_api_client import (
    AdditionalInformation as RyhtiAdditionalInformation,
    CodeValue as RyhtiCodeValue,
    DecimalRange as RyhtiDecimalRange,
    DecimalValue as RyhtiDecimalValue,
    GeneralRegulationGroup as RyhtiGeneralRegulationGroup,
    LanguageString as RyhtiLanguageString,
    LocalizedTextValue as RyhtiLocalizedTextValue,
    NumericRange as RyhtiNumericRange,
    NumericValue as RyhtiNumericValue,
    OtherPlanMaterial as RyhtiOtherPlanMaterial,
    Plan as RyhtiPlan,
    PlanAttachmentDocument as RyhtiPlanAttachmentDocument,
    PlanMap as RyhtiPlanMap,
    PlanObject as RyhtiPlanObject,
    PlanRecommendation as RyhtiPlanRecommendation,
    PlanRegulation as RyhtiPlanRegulation,
    PlanRegulationGroup as RyhtiPlanRegulationGroup,
    PlanRegulationGroupRelations as RyhtiPlanRegulationGroupRelations,
    PlanReport as RyhtiPlanReport,
    PositiveDecimalRange as RyhtiPositiveDecimalRange,
    PositiveDecimalValue as RyhtiPositiveDecimalValue,
    PositiveNumericRange as RyhtiPositiveNumericRange,
    PositiveNumericValue as RyhtiPositiveNumericValue,
    RyhtiGeometry,
    SpotElevation as RyhtiSpotElevation,
    TextValue as RyhtiTextValue,
    TimePeriodDateOnly as RyhtiTimePeriodDateOnly,
)
from shapely import to_geojson
from sqlalchemy import and_, func, select, text
from sqlalchemy.exc import MultipleResultsFound
from sqlalchemy.orm import defer, raiseload

from database import base, models
from database.enums import AttributeValueDataType
from ryhti_client.profiling import log_duration

if TYPE_CHECKING:
    from collections.abc import Mapping

    from geoalchemy2 import WKBElement
    from pydantic import BaseModel
    from ryhti_api_client import AttributeValue as RyhtiAttributeValue
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

LANGUAGES = ("fin", "swe", "smn", "sms", "sme", "eng")


def to_json_dict(model: BaseModel) -> dict[str, Any]:
    """Returns a JSON compatible dict with the camelCase names Ryhti expects.

    Fields that are None are left out, so the result is the same as the JSON the
    model prints.
    """
    return model.model_dump(mode="json", by_alias=True, exclude_none=True)


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

    def serialize_geometry(self, geojson: str, table: Table) -> RyhtiGeometry:
        """Returns Ryhti geometry with the correct SRID from geojson of the table.

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
        # The geometry type picks the geojson model class.
        return RyhtiGeometry.model_validate(
            {"srid": str(self._get_srid_of_table(table)), "geometry": geometry}
        )

    def serialize_geometry_of(self, obj: Geometrical) -> RyhtiGeometry:
        """Returns Ryhti geometry of a single object.

        Plan objects get their geojson from PostGIS instead, see _load_plan_objects.
        Converting one geometry in python is cheaper than an extra database query.
        """
        return self.serialize_geometry(
            to_geojson(to_shape(obj.geom)), cast("Table", obj.__table__)
        )

    def get_local_date(self, datetime_value: datetime.datetime) -> datetime.date:
        """Returns the date of the given datetime in local timezone."""
        return datetime_value.astimezone(LOCAL_TZ).date()

    def serialize_date_period(
        self, date_start: datetime.date, date_end: datetime.date | None
    ) -> RyhtiTimePeriodDateOnly:
        return RyhtiTimePeriodDateOnly(begin=date_start, end=date_end)

    def serialize_language_string(
        self, field_value: dict[str, str] | None
    ) -> RyhtiLanguageString | None:
        """Serializes a language string dict, returns None if empty."""
        if not field_value or not isinstance(field_value, dict):
            return None

        texts = {
            language: name
            for (language, name) in field_value.items()
            if language in LANGUAGES and isinstance(name, str) and name
        }
        return RyhtiLanguageString(**texts) if texts else None

    def serialize_required_language_string(
        self, field_value: dict[str, str] | None
    ) -> RyhtiLanguageString:
        """Serializes a language string dict for a field Ryhti requires.

        An empty language string is sent when there is no text, so Ryhti reports the
        missing text instead of the serializer failing.
        """
        return self.serialize_language_string(field_value) or RyhtiLanguageString()

    def serialize_recommendation(
        self, plan_recommendation: models.PlanProposition
    ) -> RyhtiPlanRecommendation:
        period_of_validity = None
        if plan_recommendation.period_of_validity_start:
            period_of_validity = self.serialize_date_period(
                plan_recommendation.period_of_validity_start,
                plan_recommendation.period_of_validity_end,
            )
        return RyhtiPlanRecommendation(
            planRecommendationKey=UUID(plan_recommendation.id),
            lifeCycleStatus=plan_recommendation.lifecycle_status.uri,
            planThemes=(
                [plan_theme.uri for plan_theme in plan_recommendation.plan_themes]
                if plan_recommendation.plan_themes
                else None
            ),
            recommendationNumber=plan_recommendation.ordering,
            periodOfValidity=period_of_validity,
            value=self.serialize_required_language_string(
                plan_recommendation.text_value
            ),
        )

    def serialize_attribute_value(
        self, attribute_value: base.AttributeValueMixin
    ) -> RyhtiAttributeValue | None:
        """Serializes the value of a regulation or an additional information.

        Every Ryhti data type has a model class of its own. Numeric types hold whole
        numbers, decimal types hold floats.
        """
        data_type = attribute_value.value_data_type
        if data_type is None:
            return None

        number = attribute_value.numeric_value
        range_min = attribute_value.numeric_range_min
        range_max = attribute_value.numeric_range_max
        unit = attribute_value.unit or None
        text_value = attribute_value.text_value
        syntax = attribute_value.text_syntax

        value: RyhtiAttributeValue | None
        match data_type:
            case AttributeValueDataType.CODE:
                value = RyhtiCodeValue(
                    dataType="Code",
                    code=attribute_value.code_value,
                    codeList=attribute_value.code_list,
                    title=self.serialize_language_string(attribute_value.code_title),
                )
            case AttributeValueDataType.NUMERIC:
                value = RyhtiNumericValue(
                    dataType="Numeric",
                    number=int(number) if number is not None else None,
                    unitOfMeasure=unit,
                )
            case AttributeValueDataType.POSITIVE_NUMERIC:
                value = RyhtiPositiveNumericValue(
                    dataType="PositiveNumeric",
                    number=int(number) if number is not None else None,
                    unitOfMeasure=unit,
                )
            case AttributeValueDataType.SPOT_ELEVATION:
                value = RyhtiSpotElevation(
                    dataType="SpotElevation",
                    number=int(number) if number is not None else None,
                    unitOfMeasure=unit,
                )
            case AttributeValueDataType.DECIMAL:
                value = RyhtiDecimalValue(
                    dataType="Decimal", number=number, unitOfMeasure=unit
                )
            case AttributeValueDataType.POSITIVE_DECIMAL:
                value = RyhtiPositiveDecimalValue(
                    dataType="PositiveDecimal", number=number, unitOfMeasure=unit
                )
            case AttributeValueDataType.NUMERIC_RANGE:
                value = RyhtiNumericRange(
                    dataType="NumericRange",
                    minimumValue=int(range_min) if range_min is not None else None,
                    maximumValue=int(range_max) if range_max is not None else None,
                    unitOfMeasure=unit,
                )
            case AttributeValueDataType.POSITIVE_NUMERIC_RANGE:
                value = RyhtiPositiveNumericRange(
                    dataType="PositiveNumericRange",
                    minimumValue=int(range_min) if range_min is not None else None,
                    maximumValue=int(range_max) if range_max is not None else None,
                    unitOfMeasure=unit,
                )
            case AttributeValueDataType.DECIMAL_RANGE:
                value = RyhtiDecimalRange(
                    dataType="DecimalRange",
                    minimumValue=range_min,
                    maximumValue=range_max,
                    unitOfMeasure=unit,
                )
            case AttributeValueDataType.POSITIVE_DECIMAL_RANGE:
                value = RyhtiPositiveDecimalRange(
                    dataType="PositiveDecimalRange",
                    minimumValue=range_min,
                    maximumValue=range_max,
                    unitOfMeasure=unit,
                )
            case AttributeValueDataType.LOCALIZED_TEXT:
                value = RyhtiLocalizedTextValue(
                    dataType="LocalizedText",
                    text=(
                        self.serialize_language_string(text_value)
                        if isinstance(text_value, dict)
                        else None
                    ),
                    syntax=syntax,
                )
            case AttributeValueDataType.TEXT:
                # jsonb can contain either a "dict" or a "string".
                value = RyhtiTextValue(
                    dataType="Text",
                    text=text_value if isinstance(text_value, str) else None,
                    syntax=syntax,
                )
            case (
                AttributeValueDataType.IDENTIFIER
                | AttributeValueDataType.TIME_PERIOD
                | AttributeValueDataType.TIME_PERIOD_DATE_ONLY
            ):
                # TODO: implement identifier and time period values
                value = None
        return value

    def serialize_additional_information(
        self, additional_information: models.AdditionalInformation
    ) -> RyhtiAdditionalInformation:
        return RyhtiAdditionalInformation(
            type=additional_information.type_of_additional_information.uri,
            value=self.serialize_attribute_value(additional_information),
        )

    def serialize_regulation(
        self, plan_regulation: models.PlanRegulation
    ) -> RyhtiPlanRegulation:
        period_of_validity = None
        if plan_regulation.period_of_validity_start:
            period_of_validity = self.serialize_date_period(
                plan_regulation.period_of_validity_start,
                plan_regulation.period_of_validity_end,
            )
        return RyhtiPlanRegulation(
            planRegulationKey=UUID(plan_regulation.id),
            lifeCycleStatus=plan_regulation.lifecycle_status.uri,
            type=plan_regulation.type_of_plan_regulation.uri,
            planThemes=(
                [plan_theme.uri for plan_theme in plan_regulation.plan_themes]
                if plan_regulation.plan_themes
                else None
            ),
            subjectIdentifiers=plan_regulation.subject_identifiers,
            # Ryhti wants the regulation number as a string.
            regulationNumber=(
                str(plan_regulation.ordering)
                if plan_regulation.ordering is not None
                else None
            ),
            periodOfValidity=period_of_validity,
            verbalRegulations=(
                [
                    type_code.uri
                    for type_code in plan_regulation.types_of_verbal_plan_regulations
                ]
                if plan_regulation.types_of_verbal_plan_regulations
                else None
            ),
            additionalInformations=[
                self.serialize_additional_information(ai)
                for ai in plan_regulation.additional_information
            ],
            value=self.serialize_attribute_value(plan_regulation),
        )

    def serialize_plan_regulation_group(
        self, group: models.PlanRegulationGroup
    ) -> RyhtiPlanRegulationGroup:
        return RyhtiPlanRegulationGroup(
            planRegulationGroupKey=UUID(group.id),
            titleOfPlanRegulation=self.serialize_required_language_string(group.name),
            groupNumber=group.ordering,
            letterIdentifier=group.short_name,
            colorNumber="#FFFFFF",
            planRecommendations=[
                self.serialize_recommendation(recommendation)
                for recommendation in group.plan_propositions
            ],
            planRegulations=[
                self.serialize_regulation(regulation)
                for regulation in group.plan_regulations
            ],
        )

    def serialize_general_regulation_group(
        self, group: models.PlanRegulationGroup
    ) -> RyhtiGeneralRegulationGroup:
        """General regulation groups have no letter identifier or color."""
        return RyhtiGeneralRegulationGroup(
            generalRegulationGroupKey=UUID(group.id),
            titleOfPlanRegulation=self.serialize_required_language_string(group.name),
            groupNumber=group.ordering,
            planRecommendations=[
                self.serialize_recommendation(recommendation)
                for recommendation in group.plan_propositions
            ],
            planRegulations=[
                self.serialize_regulation(regulation)
                for regulation in group.plan_regulations
            ],
        )

    def serialize_plan_object(
        self,
        plan_object: models.PlanObjectBase,
        geojson: str,
        containing_land_use_area_ids: Mapping[DbId, DbId],
    ) -> RyhtiPlanObject:
        period_of_validity = None
        if plan_object.period_of_validity_start:
            period_of_validity = self.serialize_date_period(
                plan_object.period_of_validity_start, plan_object.period_of_validity_end
            )
        vertical_limit = None
        if plan_object.height_min or plan_object.height_max:
            vertical_limit = RyhtiDecimalRange(
                dataType="DecimalRange",
                minimumValue=plan_object.height_min,
                maximumValue=plan_object.height_max,
                unitOfMeasure=plan_object.height_unit,
            )
        related_plan_object_keys = self._get_related_plan_object_keys(
            plan_object, containing_land_use_area_ids
        )
        return RyhtiPlanObject(
            planObjectKey=UUID(plan_object.id),
            lifeCycleStatus=plan_object.lifecycle_status.uri,
            undergroundStatus=plan_object.type_of_underground.uri,
            geometry=self.serialize_geometry(
                geojson, cast("Table", plan_object.__table__)
            ),
            name=self.serialize_language_string(plan_object.name),
            description=self.serialize_language_string(plan_object.description),
            objectNumber=plan_object.ordering,
            periodOfValidity=period_of_validity,
            verticalLimit=vertical_limit,
            relatedPlanObjectKeys=(
                [UUID(key) for key in related_plan_object_keys]
                if related_plan_object_keys
                else None
            ),
        )

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

    def serialize_plan_objects(
        self, loaded: LoadedPlanObjects
    ) -> list[RyhtiPlanObject]:
        """Serializes the plan objects of a plan in the local database."""
        containing_land_use_area_ids = self._get_containing_land_use_area_ids(
            loaded.plan_objects, loaded.groups_by_object
        )
        return [
            self.serialize_plan_object(
                plan_object,
                loaded.geojson_by_id[plan_object.id],
                containing_land_use_area_ids,
            )
            for plan_object in loaded.plan_objects
        ]

    def serialize_plan_regulation_groups(
        self, loaded: LoadedPlanObjects
    ) -> list[RyhtiPlanRegulationGroup]:
        """Serializes the regulation groups of the plan objects of a plan in the local
        database.
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
        return [self.serialize_plan_regulation_group(group) for group in ordered_groups]

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

    def serialize_plan_regulation_group_relations(
        self, loaded: LoadedPlanObjects
    ) -> list[RyhtiPlanRegulationGroupRelations]:
        """Serializes the relations between plan objects and their regulation groups."""
        return [
            RyhtiPlanRegulationGroupRelations(
                planObjectKey=UUID(plan_object.id),
                planRegulationGroupKey=UUID(regulation_group.id),
            )
            for plan_object in loaded.plan_objects
            for regulation_group in loaded.groups_by_object.get(plan_object.id, [])
        ]

    def serialize_plan(self, plan: models.Plan) -> RyhtiPlan:
        """Serializes a plan in the local database into a Ryhti plan.

        The plan may be a detached instance; it is attached to a new session while
        the plan objects are loaded.
        """
        # Here come the dependent objects. They are related to the plan directly or
        # via the plan objects, so we better fetch the objects first and then move on.
        with (
            log_duration("load_plan_objects"),
            self.Session(expire_on_commit=False) as session,
        ):
            session.add(plan)
            loaded = self._load_plan_objects(session, plan)

        # Our plans have lots of different plan objects, each of which has one plan
        # regulation group.
        with log_duration("plan_objects"):
            plan_objects = self.serialize_plan_objects(loaded)

        # For reasons unknown, Ryhti does not allow multilanguage description.
        plan_description = (
            plan.description.get("fin") if isinstance(plan.description, dict) else None
        )
        period_of_validity = None
        if plan.period_of_validity_start:
            period_of_validity = self.serialize_date_period(
                plan.period_of_validity_start, plan.period_of_validity_end
            )

        return RyhtiPlan(
            # planKey should always be the local uuid, not the permanent plan matter id.
            planKey=UUID(plan.id),
            # Let's have all the code values preloaded joined from db.
            # It makes this super easy:
            lifeCycleStatus=plan.lifecycle_status.uri,
            legalEffectOfLocalMasterPlans=(
                [effect.uri for effect in plan.legal_effects_of_master_plan]
                if plan.legal_effects_of_master_plan
                else None
            ),
            scale=plan.scale,
            geographicalArea=self.serialize_geometry_of(plan),
            planDescription=plan_description or None,
            officialUseOnly=plan.official_use_only or None,
            generalRegulationGroups=[
                self.serialize_general_regulation_group(regulation_group)
                for regulation_group in plan.general_plan_regulation_groups
            ],
            planObjects=plan_objects,
            planRegulationGroups=self.serialize_plan_regulation_groups(loaded),
            planRegulationGroupRelations=(
                self.serialize_plan_regulation_group_relations(loaded)
            ),
            approvalDate=plan.approval_date,
            periodOfValidity=period_of_validity,
            # Documents are divided into different categories. They may only be added
            # to plan *after* they have been uploaded, see add_document_to_plan.
            planMaps=[],
            planAnnexes=[],
            otherPlanMaterials=[],
        )

    def get_exported_file_key(self, document: models.Document) -> UUID:
        """Returns the Ryhti file key of an uploaded document.

        Raises ValueError if the document has not been uploaded.
        """
        if document.exported_file_key is None:
            raise ValueError(f"Document {document.id} has not been uploaded to Ryhti.")
        return document.exported_file_key

    def serialize_plan_map(self, document: models.Document) -> RyhtiPlanMap:
        return RyhtiPlanMap(
            planMapKey=UUID(document.id),
            name=self.serialize_required_language_string(document.name),
            fileKey=self.get_exported_file_key(document),
            # TODO: Take the coordinate system from the actual file?
            coordinateSystem=(
                f"http://uri.suomi.fi/codelist/rakrek/ETRS89/code/EPSG{base.PROJECT_SRID!s}"
            ),
        )

    def serialize_plan_annex(
        self, document: models.Document
    ) -> RyhtiPlanAttachmentDocument:
        if not document.permanent_document_identifier:
            raise ValueError(
                f"Document {document.id} has no permanent document identifier."
            )
        return RyhtiPlanAttachmentDocument(
            attachmentDocumentKey=UUID(document.id),
            documentIdentifier=document.permanent_document_identifier,
            name=self.serialize_required_language_string(document.name),
            personalDataContent=document.personal_data_content.uri,
            categoryOfPublicity=document.category_of_publicity.uri,
            accessibility=document.accessibility,
            retentionTime=document.retention_time.uri,
            languages=[document.language.uri],
            fileKey=self.get_exported_file_key(document),
            documentDate=self.get_local_date(document.document_date),
            arrivedDate=(
                self.get_local_date(document.arrival_date)
                if document.arrival_date
                else None
            ),
            typeOfAttachment=document.type_of_document.uri,
        )

    def serialize_other_plan_material(
        self, document: models.Document
    ) -> RyhtiOtherPlanMaterial:
        return RyhtiOtherPlanMaterial(
            otherPlanMaterialKey=UUID(document.id),
            name=self.serialize_required_language_string(document.name),
            fileKey=document.exported_file_key,
            personalDataContent=document.personal_data_content.uri,
            categoryOfPublicity=document.category_of_publicity.uri,
        )

    def add_plan_report_to_plan(
        self, document: models.Document, ryhti_plan: RyhtiPlan
    ) -> None:
        """Adds a plan report document to the Ryhti plan.

        The plan has a single plan report that holds all the report documents.
        """
        if ryhti_plan.plan_report is None:
            ryhti_plan.plan_report = RyhtiPlanReport(
                planReportKey=uuid4(),
                attachmentDocuments=[self.serialize_plan_annex(document)],
            )
        else:
            ryhti_plan.plan_report.attachment_documents.append(
                self.serialize_plan_annex(document)
            )

    def add_document_to_plan(
        self, document: models.Document, ryhti_plan: RyhtiPlan
    ) -> None:
        """Adds a document to the Ryhti plan. The document type picks the category.

        The document must be uploaded first. Raises ValueError if the document has no
        file key.
        """
        if document.type_of_document.value == "03":
            # Kaavakartta
            if ryhti_plan.plan_maps is None:
                ryhti_plan.plan_maps = []
            ryhti_plan.plan_maps.append(self.serialize_plan_map(document))
        elif document.type_of_document.value == "06":
            # Kaavaselostus
            self.add_plan_report_to_plan(document, ryhti_plan)
        elif document.type_of_document.value == "99":
            # Muu asiakirja
            if ryhti_plan.other_plan_materials is None:
                ryhti_plan.other_plan_materials = []
            ryhti_plan.other_plan_materials.append(
                self.serialize_other_plan_material(document)
            )
        else:
            # Kaavan liite
            if ryhti_plan.plan_annexes is None:
                ryhti_plan.plan_annexes = []
            ryhti_plan.plan_annexes.append(self.serialize_plan_annex(document))
