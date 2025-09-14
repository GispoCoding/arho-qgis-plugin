"""Module for deserializing Ryhti API plan data into SQLAlchemy models."""

from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING, Any, cast
from uuid import UUID

from geoalchemy2.shape import from_shape
from pydantic import BaseModel, ValidationError
from ryhti_api_client import (
    AdditionalInformation as RyhtiAdditionalInformation,
    AttributeValue as RyhtiAttributeValue,
    GeneralRegulationGroup as RyhtiGeneralRegulationGroup,
    LanguageString as RyhtiLanguageString,
    Plan as RyhtiPlan,
    PlanAttachmentDocument as RyhtiPlanAttachmentDocument,
    PlanMap as RyhtiPlanMap,
    PlanObject as RyhtiPlanObject,
    PlanRecommendation as RyhtiPlanRecommendation,
    PlanRegulation as RyhtiPlanRegulation,
    PlanRegulationGroup as RyhtiPlanRegulationGroup,
    RyhtiGeometry,
)
from shapely import (
    LineString,
    MultiLineString,
    MultiPoint,
    MultiPolygon,
    Point,
    Polygon,
    from_geojson,
)
from sqlalchemy import select

from database.base import PROJECT_SRID
from database.codes import CodeBase, PlanType, TypeOfDocument, TypeOfPlanRegulationGroup
from database.enums import AttributeValueDataType
from database.models import (
    AdditionalInformation,
    Document,
    LandUseArea,
    LandUsePoint,
    Line,
    OtherArea,
    OtherPoint,
    Plan,
    PlanProposition,
    PlanRegulation,
    PlanRegulationGroup,
)

if TYPE_CHECKING:
    from geoalchemy2.elements import WKBElement
    from ryhti_api_client import (
        CodeValue,
        DecimalRange,
        DecimalValue,
        LocalizedTextValue,
        NumericRange,
        NumericValue,
        PositiveDecimalRange,
        PositiveDecimalValue,
        PositiveNumericRange,
        PositiveNumericValue,
        TextValue,
    )
    from shapely.geometry.base import BaseGeometry
    from sqlalchemy.orm import Session

    type RangeType = (
        DecimalRange | NumericRange | PositiveDecimalRange | PositiveNumericRange
    )
    type NumberValue = (
        DecimalValue | NumericValue | PositiveDecimalValue | PositiveNumericValue
    )


class PlanMatterData(BaseModel):
    name: str
    plan_type_id: UUID
    organization_id: UUID
    permanent_plan_identifier: str | None = None
    producers_plan_identifier: str | None = None


def ryhti_plan_from_json(json_data: str) -> RyhtiPlan:
    try:
        ryhti_plan = RyhtiPlan.model_validate_json(json_data)
    except ValidationError as e:
        raise ValueError(f"Invalid plan data: \n{e}") from e
    return ryhti_plan


def plan_matter_data_from_extra_data_dict(extra_data: dict) -> PlanMatterData:
    try:
        plan_matter_data = PlanMatterData.model_validate(extra_data)
    except ValidationError as e:
        raise ValueError(f"Invalid extra data: \n{e}") from e
    return plan_matter_data


class Deserializer:
    def __init__(self, session: Session) -> None:
        self.session = session

        self.code_id_cache: dict[tuple[type[CodeBase], str], UUID | None] = {}
        self.code_instance_cache: dict[tuple[type[CodeBase], str], CodeBase | None] = {}

    def get_code_id(self, code_model: type[CodeBase], code: str) -> UUID | None:
        if (code_model, code) in self.code_id_cache:
            return self.code_id_cache[(code_model, code)]

        code_uuid = self.session.scalars(
            select(code_model.id).where(code_model.value == code)
        ).one_or_none()
        self.code_id_cache[(code_model, code)] = code_uuid

        return code_uuid

    def get_code_instance(
        self, code_model: type[CodeBase], code: str
    ) -> CodeBase | None:
        if (code_model, code) in self.code_instance_cache:
            return self.code_instance_cache[(code_model, code)]

        code_instance = self.session.scalars(
            select(code_model).where(code_model.value == code)
        ).one_or_none()
        self.code_instance_cache[(code_model, code)] = code_instance

        return code_instance

    def _get_model_and_code(self, code_uri: str) -> tuple[type[CodeBase], str]:
        CodeModel = next(  # noqa: N806
            (
                model
                for model in CodeBase.__subclasses__()
                if model.code_list_uri and code_uri.startswith(model.code_list_uri)
            ),
            None,
        )
        if CodeModel is None:
            raise ValueError(f"No matching code list found for URI: {code_uri}")

        code = (
            code_uri.removeprefix(CodeModel.code_list_uri)
            .removeprefix("/")
            .removeprefix("code/")
        )

        return (CodeModel, code)

    def get_code_id_from_uri(self, code_uri: str) -> UUID | None:
        if not code_uri:
            return None

        CodeModel, code = self._get_model_and_code(code_uri)  # noqa: N806
        return self.get_code_id(CodeModel, code)

    def get_code_instance_from_uri(self, code_uri: str) -> CodeBase | None:
        if not code_uri:
            return None

        CodeModel, code = self._get_model_and_code(code_uri)  # noqa: N806
        return self.get_code_instance(CodeModel, code)

    def deserialize_ryhti_geometry(self, geometry: RyhtiGeometry) -> WKBElement:
        if int(geometry.srid) != PROJECT_SRID:
            raise ValueError(
                f"Unsupported SRID: {geometry.srid}, expected: {PROJECT_SRID}"
            )
        print(f"{geometry=}")
        json = geometry.geometry.model_dump_json()
        print(f"{json=}")
        shape = from_geojson(json)
        print(f"{shape=}")

        multi_shape = self.convert_to_multi_geom(shape)
        return from_shape(multi_shape, srid=int(geometry.srid))

    def convert_to_multi_geom(
        self, shape: BaseGeometry
    ) -> MultiPolygon | MultiPoint | MultiLineString | BaseGeometry:
        if shape.geom_type == "Polygon":
            shape = MultiPolygon([cast("Polygon", shape)])
        elif shape.geom_type == "Point":
            shape = MultiPoint([cast("Point", shape)])
        elif shape.geom_type == "LineString":
            shape = MultiLineString([cast("LineString", shape)])

        return shape

    def deserialize_language_string(
        self, ryhti_language_string: RyhtiLanguageString | None
    ) -> dict[str, str] | None:
        if ryhti_language_string is None:
            return None
        languages = ["fin", "swe", "smn", "sms", "sme", "eng"]
        return {
            lang: text
            for lang in languages
            if (text := getattr(ryhti_language_string, lang, None))
        } or None

    def form_value_dict(self, value: RyhtiAttributeValue | None) -> dict[str, Any]:
        if value is None:
            return {}

        database_field_values: dict[str, Any]

        data_type = AttributeValueDataType(value.data_type)
        if data_type is AttributeValueDataType.CODE:
            value = cast("CodeValue", value)
            database_field_values = {
                "code_value": value.code,
                "code_list": value.code_list,
                "code_title": self.deserialize_language_string(value.title),
            }
        elif data_type in (
            AttributeValueDataType.NUMERIC,
            AttributeValueDataType.POSITIVE_NUMERIC,
            AttributeValueDataType.DECIMAL,
            AttributeValueDataType.POSITIVE_DECIMAL,
            AttributeValueDataType.SPOT_ELEVATION,
        ):
            value = cast("NumberValue", value)
            database_field_values = {
                "numeric_value": value.number,
                "unit": value.unit_of_measure,
            }
        elif data_type in (
            AttributeValueDataType.NUMERIC_RANGE,
            AttributeValueDataType.POSITIVE_NUMERIC_RANGE,
            AttributeValueDataType.DECIMAL_RANGE,
            AttributeValueDataType.POSITIVE_DECIMAL_RANGE,
        ):
            value = cast("RangeType", value)
            database_field_values = {
                "numeric_range_min": value.minimum_value,
                "numeric_range_max": value.maximum_value,
                "unit": value.unit_of_measure,
            }
        elif data_type is AttributeValueDataType.IDENTIFIER:
            pass  # TODO implement identifier values
        elif data_type == AttributeValueDataType.LOCALIZED_TEXT:
            value = cast("LocalizedTextValue", value)
            database_field_values = {
                "text_value": self.deserialize_language_string(value.text),
                "text_syntax": value.syntax,
            }
        elif data_type == AttributeValueDataType.TEXT:
            value = cast("TextValue", value)
            database_field_values = {
                "text_value": value.text,
                "text_syntax": value.syntax,
            }
        elif data_type is AttributeValueDataType.TIME_PERIOD:
            pass  # TODO: implement time period values
        elif data_type is AttributeValueDataType.TIME_PERIOD_DATE_ONLY:
            pass  # TODO: implement time period date only values
        elif data_type is AttributeValueDataType.SPOT_ELEVATION:
            pass  # TODO: implement spot elevation values
        else:
            database_field_values = {}

        database_field_values["value_data_type"] = value.data_type
        return database_field_values

    def deserialize_additional_information(
        self, additional_information: RyhtiAdditionalInformation
    ) -> AdditionalInformation:
        """Deserializes a RyhtiAdditionalInformation into an AdditionalInformation SQLAlchemy model instance."""
        value = self.form_value_dict(additional_information.value)
        return AdditionalInformation(
            type_of_additional_information=self.get_code_instance_from_uri(
                additional_information.type
            ),
            **value,
        )

    def deserialize_regulation(
        self, ryhti_regulation: RyhtiPlanRegulation
    ) -> PlanRegulation:
        """Deserializes a RyhtiPlanRegulation into a PlanRegulation SQLAlchemy model instance.

        "planRegulationKey", ✅
        "planRegulationUri",
        "value",  ✅
        "lifeCycleStatus", ✅
        "type", ✅
        "verbalRegulations", ✅
        "additionalInformations", ✅
        "relatedDocuments",
        "planThemes", ✅
        "periodOfValidity",
        "subjectIdentifiers", ✅
        "regulationNumber", ✅
        """
        value = self.form_value_dict(ryhti_regulation.value)

        try:
            regulation_number = int(
                ryhti_regulation.regulation_number  # type: ignore[arg-type]
            )
        except (ValueError, TypeError):
            regulation_number = None

        return PlanRegulation(
            id=ryhti_regulation.plan_regulation_key,
            type_of_plan_regulation=self.get_code_instance_from_uri(
                ryhti_regulation.type
            ),
            lifecycle_status_id=self.get_code_id_from_uri(
                ryhti_regulation.life_cycle_status
            ),
            additional_information=[
                self.deserialize_additional_information(a_i)
                for a_i in ryhti_regulation.additional_informations or []
            ],
            plan_themes=[
                self.get_code_instance_from_uri(theme)
                for theme in ryhti_regulation.plan_themes or []
            ],
            types_of_verbal_plan_regulations=[
                self.get_code_instance_from_uri(type_)
                for type_ in ryhti_regulation.verbal_regulations or []
            ],
            ordering=regulation_number,
            subject_identifiers=ryhti_regulation.subject_identifiers,
            **value,
        )

    def deserialize_recommendation(
        self, ryhti_plan_recommendation: RyhtiPlanRecommendation
    ) -> PlanProposition:
        """Deserializes a RyhtiPlanRecommendation into a PlanProposition SQLAlchemy model instance.

        "planRecommendationKey", ✅
        "planRecommendationUri",
        "value", ✅
        "lifeCycleStatus", ✅
        "relatedDocuments",
        "planThemes", ✅
        "periodOfValidity",
        "recommendationNumber", ✅
        """
        return PlanProposition(
            id=ryhti_plan_recommendation.plan_recommendation_key,
            lifecycle_status_id=self.get_code_id_from_uri(
                ryhti_plan_recommendation.life_cycle_status
            ),
            ordering=ryhti_plan_recommendation.recommendation_number,
            plan_themes=[
                self.get_code_instance_from_uri(theme_code)
                for theme_code in ryhti_plan_recommendation.plan_themes or []
            ],
            text_value=self.deserialize_language_string(
                ryhti_plan_recommendation.value
            ),
        )

    def deserialize_plan_regulation_group(
        self, regulation_group: RyhtiPlanRegulationGroup
    ):
        """Deserializes a RyhtiPlanRegulationGroup into a PlanRegulationGroup SQLAlchemy model instance.

        "planRegulationGroupKey", ✅
        "planRegulationGroupUri",
        "titleOfPlanRegulation", ✅
        "letterIdentifier", ✅
        "planRegulations", ✅
        "planRecommendations", ✅
        "colorNumber",
        "groupNumber", ✅
        """
        return PlanRegulationGroup(
            id=regulation_group.plan_regulation_group_key,
            name=self.deserialize_language_string(
                regulation_group.title_of_plan_regulation
            ),
            short_name=regulation_group.letter_identifier,
            ordering=regulation_group.group_number,
            plan_regulations=[
                self.deserialize_regulation(regulation)
                for regulation in regulation_group.plan_regulations
            ],
            plan_propositions=[
                self.deserialize_recommendation(recommendation)
                for recommendation in regulation_group.plan_recommendations or []
            ],
        )

    def deserialize_general_regulation_group(
        self, ryhti_general_regulation_group: RyhtiGeneralRegulationGroup
    ) -> PlanRegulationGroup:
        """Deserializes a RyhtiGeneralRegulationGroup into a PlanRegulationGroup SQLAlchemy model instance.

        "generalRegulationGroupKey", ✅
        "generalRegulationGroupUri",
        "titleOfPlanRegulation", ✅
        "planRegulations", ✅
        "planRecommendations", ✅
        "groupNumber", ✅
        """
        group_type_code_id = self.get_code_id(
            TypeOfPlanRegulationGroup, "generalRegulations"
        )
        if group_type_code_id is None:
            raise ValueError("Could not find code id for type generalRegulations")

        plan_regulations = [
            self.deserialize_regulation(regulation)
            for regulation in ryhti_general_regulation_group.plan_regulations or []
        ]
        plan_propositions = [
            self.deserialize_recommendation(recommendation)
            for recommendation in ryhti_general_regulation_group.plan_recommendations
            or []
        ]

        return PlanRegulationGroup(
            id=ryhti_general_regulation_group.general_regulation_group_key,
            name=self.deserialize_language_string(
                ryhti_general_regulation_group.title_of_plan_regulation
            ),
            ordering=ryhti_general_regulation_group.group_number,
            plan_regulations=plan_regulations,
            plan_propositions=plan_propositions,
            type_of_plan_regulation_group_id=group_type_code_id,
        )

    def _determine_area_plan_object_type(
        self, regulation_groups: list[PlanRegulationGroup]
    ) -> type[LandUseArea | OtherArea]:
        has_primary_usage_regulation = any(
            additional_info.type_of_additional_information.value == "paakayttotarkoitus"
            for group in regulation_groups
            for regulation in group.plan_regulations
            for additional_info in regulation.additional_information
        )
        if has_primary_usage_regulation:
            return LandUseArea
        return OtherArea

    def _determine_point_plan_object_type(
        self, regulation_groups: list[PlanRegulationGroup], plan_type: PlanType
    ) -> type[LandUsePoint | OtherPoint]:
        def get_root_plan_type(plan_type: PlanType) -> PlanType:
            if plan_type.parent is None:
                return plan_type
            return get_root_plan_type(plan_type.parent)

        root_plan_type = get_root_plan_type(plan_type)
        if root_plan_type.value == "3":  # Asemakaava
            return OtherPoint

        possible_land_use_regulations = {
            "ampumarataAlue",
            "asuinkerrostaloalue",
            "asuinpientaloalue",
            "asumisenAlue",
            "asuntovaunualue",
            "energiahuollonAlue",
            "erityisalue",
            "hautausmaa",
            "henkiloliikenteenTerminaalialue",
            "huoltoasemaAlue",
            "jatteenkasittelyalue",
            "kaivosalue",
            "keskustatoimintojenAlakeskus",
            "keskustatoimintojenAlue",
            "kiertotaloudenAlue",
            "kotielaintaloudenSuuryksikonAlue",
            "kylaAlue",
            "lahivirkistysalue",
            "leirintaAlue",
            "lentoliikenteenAlue",
            "liikennealue",
            "luonnonsuojelualue",
            "maaAinestenOttoalue",
            "maaJaMetsatalousAlue",
            "maaJaMetsatalousalueJollaErityisiaYmparistoarvoja",
            "maaJaMetsatalousalueJollaErityistaUlkoilunOhjaamistarvetta",
            "maaliikenteenAlue",
            "maatalousalue",
            "maisemallisestiArvokasAlue",
            "matkailupalvelujenAlue",
            "metsatalousalue",
            "moottoriurheilualue",
            "muinaismuistoAlue",
            "palstaviljelyalue",
            "palvelujenAlue",
            "pelto",
            "puolustusvoimienAlue",
            "raideliikenteenAlue",
            "rakennusperinnonSuojelemisestaAnnetunLainNojallaSuojeltuRakennus",
            "rakennussuojelualue",
            "retkeilyJaUlkoiluAlue",
            "satama-alue",
            "siirtolapuutarhaAlue",
            "suojaviheralue",
            "suojelualue",
            "taajamatoimintojenAlue",
            "tavaraliikenteenTerminaalialue",
            "teollisuusalue",
            "turvetuotantoalue",
            "tyopaikkojenAlue",
            "uimaranta",
            "urheiluJaVirkistyspalvelujenAlue",
            "vahittaiskaupanMyymalakeskittyma",
            "vahittaiskaupanSuuryksikko",
            "vapaaAjanAsumisenAlue",
            "vapaaAjanAsumisenJaMatkailunAlue",
            "varastoalue",
            "varikko",
            "venesatama",
            "venevalkama",
            "vesialue",
            "virkistysalue",
            "yhdyskuntateknisenHuollonAlue",
        }

        has_primary_usage_regulation = any(
            regulation.type_of_plan_regulation.value in possible_land_use_regulations
            for group in regulation_groups
            for regulation in group.plan_regulations
        )
        if has_primary_usage_regulation:
            return LandUsePoint
        return OtherPoint

    def deserialize_plan_object(
        self,
        ryhti_plan_object: RyhtiPlanObject,
        regulation_groups: list[PlanRegulationGroup],
        plan_type: PlanType,
    ) -> LandUseArea | OtherArea | LandUsePoint | OtherPoint | Line:
        """Deserializes a RyhtiPlanObject into a PlanObject SQLAlchemy model instance.

        "planObjectKey", ✅
        "planObjectUri",
        "lifeCycleStatus", ✅
        "undergroundStatus", ✅
        "geometry", ✅
        "name", ✅
        "description", ✅
        "verticalLimit", ✅
        "relatedPlanSourceDataKeys",
        "relatedPlanSourceDataUris",
        "periodOfValidity",
        "objectNumber", ✅
        "relatedPlanObjectKeys",
        """
        geom = ryhti_plan_object.geometry.geometry
        geojson = geom.model_dump_json()
        try:
            shape = from_geojson(geojson)
        except Exception:
            print(f"Error parsing geometry from geojson: '{geojson}'")
            raise

        shape = self.convert_to_multi_geom(shape)
        PlanObjectClass: (  # noqa: N806
            type[LandUseArea | OtherArea | LandUsePoint | OtherPoint | Line] | None
        ) = None
        if shape.geom_type == "MultiPolygon":
            PlanObjectClass = self._determine_area_plan_object_type(  # noqa: N806
                regulation_groups
            )
        elif shape.geom_type == "MultiPoint":
            PlanObjectClass = self._determine_point_plan_object_type(  # noqa: N806
                regulation_groups, plan_type
            )
        elif shape.geom_type == "MultiLineString":
            PlanObjectClass = Line  # noqa: N806

        if PlanObjectClass is None:
            raise ValueError

        plan_object = PlanObjectClass(
            id=ryhti_plan_object.plan_object_key,
            name=self.deserialize_language_string(ryhti_plan_object.name),
            description=self.deserialize_language_string(ryhti_plan_object.description),
            lifecycle_status_id=self.get_code_id_from_uri(
                ryhti_plan_object.life_cycle_status
            ),
            type_of_underground_id=self.get_code_id_from_uri(
                ryhti_plan_object.underground_status
            ),
            geom=from_shape(shape),
            ordering=ryhti_plan_object.object_number,
            height_min=(
                ryhti_plan_object.vertical_limit.minimum_value
                if ryhti_plan_object.vertical_limit
                else None
            ),
            height_max=(
                ryhti_plan_object.vertical_limit.maximum_value
                if ryhti_plan_object.vertical_limit
                else None
            ),
            height_unit=(
                ryhti_plan_object.vertical_limit.unit_of_measure
                if ryhti_plan_object.vertical_limit
                else None
            ),
            plan_regulation_groups=regulation_groups,
        )
        return plan_object

    def deserialize_plan_annex(
        self, ryhti_document: RyhtiPlanAttachmentDocument
    ) -> Document:
        """Deserializes a RyhtiPlanAttachmentDocument into a Document SQLAlchemy model instance.

        "attachmentDocumentKey", ✅
        "documentIdentifier", ✅
        "name", ✅
        "personalDataContent", ✅
        "categoryOfPublicity", ✅
        "accessibility", ✅
        "retentionTime", ✅
        "confirmationDate", ✅
        "languages", ✅
        "fileKey", ✅
        "descriptors",
        "documentDate", ✅
        "arrivedDate", ✅
        "planAttachmentDocumentUri",
        "typeOfAttachment", ✅
        "documentSpecification",
        "documentCreatorOperators",
        "relatedPlanAttachmentDocuments",
        """
        return Document(
            id=ryhti_document.attachment_document_key,
            name=self.deserialize_language_string(ryhti_document.name),
            type_of_document_id=self.get_code_id_from_uri(
                ryhti_document.type_of_attachment
            ),
            category_of_publicity_id=self.get_code_id_from_uri(
                ryhti_document.category_of_publicity
            ),
            personal_data_content_id=self.get_code_id_from_uri(
                ryhti_document.personal_data_content
            ),
            retention_time_id=self.get_code_id_from_uri(ryhti_document.retention_time),
            permanent_document_identifier=self.get_code_id_from_uri(
                ryhti_document.document_identifier
            ),
            exported_file_key=ryhti_document.file_key,
            arrival_date=ryhti_document.arrived_date,
            confirmation_date=ryhti_document.confirmation_date,
            accessibility=ryhti_document.accessibility,
            decision_date=ryhti_document.confirmation_date,
            document_date=ryhti_document.document_date,
            language_id=(
                self.get_code_id_from_uri(ryhti_document.languages[0])
                if ryhti_document.languages
                else None
            ),  # TODO: Support multiple languages
        )

    def deserialise_plan_map(self, ryhti_plan_map: RyhtiPlanMap) -> Document:
        """Deserializes a RyhtiPlanMap into a Document SQLAlchemy model instance.

        "planMapKey", ✅
        "planMapUri",
        "name", ✅
        "fileKey", ✅
        "coordinateSystem",
        """
        return Document(
            id=ryhti_plan_map.plan_map_key,
            name=self.deserialize_language_string(ryhti_plan_map.name),
            exported_file_key=ryhti_plan_map.file_key,
            type_of_document_id=self.get_code_id(TypeOfDocument, "03"),  # Kaavakartta
        )

    def deserialise_ryhti_plan(
        self, ryhti_plan: RyhtiPlan, plan_matter_data: PlanMatterData
    ) -> Plan:
        """Deserializes a RyhtiPlan into a Plan SQLAlchemy model instance.

        "planKey", ✅
        "planUri",
        "lifeCycleStatus", ✅
        "legalEffectOfLocalMasterPlans", ✅
        "scale", ✅
        "officialUseOnly",
        "planMaps", ✅
        "geographicalArea", ✅
        "planDescription", ✅
        "planAnnexes", ✅
        "otherPlanMaterials",
        "planCancellationInfos",
        "planReport", ✅ # TODO: planreportKey not saved
        "generalRegulationGroups", ✅
        "presentationAlignments",
        "periodOfValidity",
        "approvalDate",
        "planners",
        "planObjects", ✅
        "planRegulationGroups", ✅
        "planRegulationGroupRelations", ✅
        "relatedPlanObjectRegulationGroupRelations",
        "relatedRegulationGroupPlanObjectRelations",
        """
        plan_type = self.session.get(PlanType, plan_matter_data.plan_type_id)
        if not plan_type:
            raise ValueError(f"Invalid plan type id: {plan_matter_data.plan_type_id}")

        plan_regulation_groups = {
            regulation_group.id: regulation_group
            for ryhti_group in ryhti_plan.plan_regulation_groups or []
            if (regulation_group := self.deserialize_plan_regulation_group(ryhti_group))
        }

        groups_of_plan_objects: dict[str, list[PlanRegulationGroup]] = defaultdict(list)
        for regulation_group_relation in (
            ryhti_plan.plan_regulation_group_relations or []
        ):
            if (
                regulation_group_relation.plan_object_key
                and regulation_group_relation.plan_regulation_group_key
            ):
                groups_of_plan_objects[
                    regulation_group_relation.plan_object_key
                ].append(
                    plan_regulation_groups[
                        regulation_group_relation.plan_regulation_group_key
                    ]
                )

        general_regulation_groups = [
            self.deserialize_general_regulation_group(ryhti_group)
            for ryhti_group in ryhti_plan.general_regulation_groups or []
        ]

        plan_objects = {
            plan_object.id: plan_object
            for ryhti_plan_object in ryhti_plan.plan_objects or []
            if (
                plan_object := self.deserialize_plan_object(
                    ryhti_plan_object,
                    groups_of_plan_objects.get(ryhti_plan_object.plan_object_key, []),
                    plan_type,
                )
            )
        }

        documents = [
            self.deserialize_plan_annex(doc) for doc in ryhti_plan.plan_annexes or []
        ]
        plan_maps = [
            self.deserialise_plan_map(plan_map)
            for plan_map in ryhti_plan.plan_maps or []
        ]
        plan_reports = (
            [
                self.deserialize_plan_annex(report)
                for report in ryhti_plan.plan_report.attachment_documents or []
            ]
            if ryhti_plan.plan_report
            else []
        )
        documents.extend(plan_maps)
        documents.extend(plan_reports)

        ryhti_plan.other_plan_materials

        plan = Plan(
            id=UUID(ryhti_plan.plan_key),
            plan_type=plan_type,
            # organisation # not included in plan, part of plan matter
            # plan_type # not included in plan, part of plan matter
            # permanent_plan_identifier # not included in plan, part of plan matter
            # producers_plan_identifier # not included in plan, part of plan matter
            # name # not included in plan, part of plan matter
            description={"fin": ryhti_plan.plan_description},
            scale=ryhti_plan.scale,
            lifecycle_status_id=self.get_code_id_from_uri(ryhti_plan.life_cycle_status),
            geom=self.deserialize_ryhti_geometry(ryhti_plan.geographical_area),
            legal_effects_of_master_plan=[
                code
                for effect in ryhti_plan.legal_effect_of_local_master_plans or []
                if (code := self.get_code_instance_from_uri(effect)) is not None
            ],
            regulation_groups=list(plan_regulation_groups.values())
            + general_regulation_groups,
            general_plan_regulation_groups=general_regulation_groups,
            land_use_areas=[
                p_o for p_o in plan_objects.values() if isinstance(p_o, LandUseArea)
            ],
            other_areas=[
                p_o for p_o in plan_objects.values() if isinstance(p_o, OtherArea)
            ],
            land_use_points=[
                p_o for p_o in plan_objects.values() if isinstance(p_o, LandUsePoint)
            ],
            other_points=[
                p_o for p_o in plan_objects.values() if isinstance(p_o, OtherPoint)
            ],
            lines=[p_o for p_o in plan_objects.values() if isinstance(p_o, Line)],
            documents=documents,
        )

        plan.name = {"fin": plan_matter_data.name}
        plan.permanent_plan_identifier = plan_matter_data.permanent_plan_identifier
        plan.producers_plan_identifier = plan_matter_data.producers_plan_identifier
        plan.organisation_id = plan_matter_data.organization_id

        plan = self._determine_and_update_regulation_group_types(plan)

        return plan

    def _add_plan_matter_data_to_plan(
        self, plan: Plan, plan_matter_data: PlanMatterData
    ) -> Plan:
        plan_type_id = plan_matter_data.plan_type_id
        if not plan_type_id:
            raise ValueError
        plan.plan_type_id = plan_type_id
        plan.name = {"fin": plan_matter_data.name}
        plan.permanent_plan_identifier = plan_matter_data.permanent_plan_identifier
        plan.producers_plan_identifier = plan_matter_data.producers_plan_identifier
        plan.organisation_id = plan_matter_data.organization_id

        return plan

    def _determine_and_update_regulation_group_types(self, plan: Plan):
        for group in plan.regulation_groups:
            group_type = max(
                (
                    (len(group.land_use_areas), "landUseRegulations"),
                    (len(group.other_areas), "otherAreaRegulations"),
                    (len(group.lines), "lineRegulations"),
                    (len(group.land_use_points), "landUseRegulations"),
                ),
                key=lambda x: x[0],
            )[1]

            group_type_code_id = self.get_code_id(TypeOfPlanRegulationGroup, group_type)
            if group_type_code_id is None:
                raise ValueError(f"Could not find code id for type {group_type}")
            group.type_of_plan_regulation_group_id = group_type_code_id

        return plan
