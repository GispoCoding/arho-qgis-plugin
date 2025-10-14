from __future__ import annotations

import logging
from abc import abstractmethod
from collections import defaultdict
from string import Template
from textwrap import dedent
from typing import Any, ClassVar, Generator, cast

from qgis.core import QgsFeature, QgsVectorLayerUtils

from arho_feature_template.core.models import (
    AdditionalInformation,
    AttributeValue,
    Document,
    LifeCycle,
    Plan,
    PlanObject,
    PlanMatter,
    Proposition,
    Regulation,
    RegulationGroup,
)
from arho_feature_template.exceptions import FeatureNotFoundError, LayerEditableError, LayerNotFoundError
from arho_feature_template.project.layers import AbstractLayer
from arho_feature_template.project.layers.code_layers import PlanTypeLayer
from arho_feature_template.utils.misc_utils import (
    deserialize_localized_text,
    get_active_plan_id,
    iface,
    serialize_localized_text,
)

logger = logging.getLogger(__name__)


class AbstractPlanLayer(AbstractLayer):
    filter_template: ClassVar[Template | None]

    @classmethod
    def filter_layer_by_plan_id(cls, plan_id: str | None) -> None:
        """Apply filter to the layer by plan id."""
        if cls.filter_template is None:
            return

        filter_expression = cls.filter_template.substitute(plan_id=plan_id)

        cls.apply_filter(filter_expression)

    @classmethod
    def hide_all_features(cls) -> None:
        cls.apply_filter("false")

    @classmethod
    def show_all_features(cls) -> None:
        cls.apply_filter("")

    @classmethod
    def apply_filter(cls, filter_expression) -> None:
        """Apply filter expression"""
        layer = cls.get_from_project()
        if layer.isEditable():
            raise LayerEditableError(cls.name)
        if not layer:
            logger.warning("Layer %s not found", cls.name)
            return None
        result = layer.setSubsetString(filter_expression)
        if result is False:
            iface.messageBar().pushMessage(
                "Error",
                f"Failed to filter layer {cls.name} with query {filter_expression}",
                level=3,
            )

    @classmethod
    @abstractmethod
    def feature_from_model(cls, model: Any) -> QgsFeature:
        raise NotImplementedError

    @classmethod
    def initialize_feature_from_model(cls, model: Any) -> QgsFeature:
        if model.id_ is not None:  # Expects all plan layer models to have 'id_' attribute
            feature = cls.get_feature_by_id(model.id_, no_geometries=False)
            if not feature:
                raise FeatureNotFoundError(model.id_, cls.name)
        else:
            feature = QgsVectorLayerUtils.createFeature(cls.get_from_project())
        return feature


# Uusi
class PlanMatterLayer(AbstractPlanLayer):
    name = "Kaava-asia"
    filter_template = Template("id = '$plan_matter_id'")

    @classmethod
    def feature_from_model(cls, model: PlanMatter) -> QgsFeature:
        feature = cls.initialize_feature_from_model(model)
        feature["name"] = serialize_localized_text(model.name)
        feature["description"] = serialize_localized_text(model.description)
        feature["permanent_plan_identifier"] = model.permanent_plan_identifier
        feature["record_number"] = model.record_number
        feature["producers_plan_identifier"] = model.producers_plan_identifier
        feature["case_identifier"] = model.case_identifier
        feature["plan_type_id"] = model.plan_type_id
        feature["organisation_id"] = model.organisation_id

        return feature

    @classmethod
    def model_from_feature(cls, feature: QgsFeature) -> PlanMatter:
        return PlanMatter(
            name=deserialize_localized_text(feature["name"]),
            description=deserialize_localized_text(feature["description"]),
            permanent_plan_identifier=feature["permanent_plan_identifier"],
            record_number=feature["record_number"],
            producers_plan_identifier=feature["producers_plan_identifier"],
            case_identifier=feature["case_identifier"],
            plan_type_id=feature["plan_type_id"],
            organisation_id=feature["organisation_id"],
            id_=feature["id"],
            modified=False,
        )

    @classmethod
    def filter_layer_by_plan_id(cls, plan_id: str | None) -> None:
        """Filter PlanMatterLayer by the plan's related plan_matter_id."""
        if cls.filter_template is None or plan_id is None:
            return

        try:
            plan_matter_id = PlanLayer.get_attribute_value_by_another_attribute_value(
                "plan_matter_id",
                "id",
                plan_id
            )

            if not plan_matter_id:
                cls.hide_all_features()
                return

            filter_expression = cls.filter_template.substitute(plan_matter_id=plan_matter_id)
            cls.apply_filter(filter_expression)

        except Exception as e:
            iface.messageBar().pushMessage(
                "Virhe",
                f"Kaava-asian suodatus epäonnistui: {e}",
                level=3,
            )
            cls.hide_all_features()

    @classmethod
    def get_plan_matter_name(cls, plan_matter_id: str) -> str:
        attribute_value = cls.get_attribute_value_by_another_attribute_value("name", "id", plan_matter_id)
        name = deserialize_localized_text(attribute_value)

        return name or "Nimetön"

    @classmethod
    def get_plan_matter_type_name(cls, plan_matter_id: str) -> str | None:
        type_id = cls.get_attribute_value_by_another_attribute_value("plan_type_id", "id", plan_matter_id)
        if type_id is None:
            return None
        attribute_value = PlanTypeLayer.get_attribute_value_by_another_attribute_value("name", "id", cast(str, type_id))
        return deserialize_localized_text(attribute_value)

    @classmethod
    def get_plan_matter_producers_plan_identifier(cls, plan_matter_id: str) -> str | None:
        producers_id = cls.get_attribute_value_by_another_attribute_value(
            "producers_plan_identifier", "id", plan_matter_id
        )
        if producers_id is None:
            return None
        return cast(str, producers_id)


class PlanLayer(AbstractPlanLayer):
    name = "Kaava"
    filter_template = Template("id = '$plan_id'")

    @classmethod
    def feature_from_model(cls, model: Plan) -> QgsFeature:
        if not model.geom:
            message = "Plan must have a geometry to be added to the layer"
            raise ValueError(message)

        feature = cls.initialize_feature_from_model(model)
        feature.setGeometry(model.geom)
        feature["name"] = serialize_localized_text(model.name)
        feature["description"] = serialize_localized_text(model.description)
        feature["scale"] = model.scale
        # feature["permanent_plan_identifier"] = model.permanent_plan_identifier
        # feature["record_number"] = model.record_number
        # feature["producers_plan_identifier"] = model.producers_plan_identifier
        # feature["matter_management_identifier"] = model.matter_management_identifier
        # feature["plan_type_id"] = model.plan_type_id
        feature["lifecycle_status_id"] = model.lifecycle_status_id
        # feature["organisation_id"] = model.organisation_id

        return feature

    @classmethod
    def model_from_feature(cls, feature: QgsFeature) -> Plan:
        group_ids = list(RegulationGroupAssociationLayer.get_group_ids_for_feature(feature["id"], cls.name))
        general_regulation_features = list(RegulationGroupLayer.get_features_by_attribute_value("id", group_ids))

        return Plan(
            geom=feature.geometry(),
            name=deserialize_localized_text(feature["name"]),
            description=deserialize_localized_text(feature["description"]),
            scale=feature["scale"],
            # permanent_plan_identifier=feature["permanent_plan_identifier"],
            # record_number=feature["record_number"],
            # producers_plan_identifier=feature["producers_plan_identifier"],
            # matter_management_identifier=feature["matter_management_identifier"],
            # plan_type_id=feature["plan_type_id"],
            lifecycle_status_id=feature["lifecycle_status_id"],
            # organisation_id=feature["organisation_id"],
            general_regulations=RegulationGroupLayer.models_from_features(general_regulation_features),
            legal_effect_ids=list(LegalEffectAssociationLayer.get_legal_effect_ids_for_plan(feature["id"])),
            documents=[
                DocumentLayer.model_from_feature(feat)
                for feat in DocumentLayer.get_features_by_attribute_value("plan_id", feature["id"])
            ],
            id_=feature["id"],
            lifecycles=[
                LifeCycleLayer.model_from_feature(feat)
                for feat in LifeCycleLayer.get_features_by_plan_id(feature["id"])
                if feat is not None
            ],
            modified=False,
        )

    @classmethod
    def get_plan_name(cls, plan_id: str) -> str:
        attribute_value = cls.get_attribute_value_by_another_attribute_value("name", "id", plan_id)
        name = deserialize_localized_text(attribute_value)

        return name or "Nimetön"

    @classmethod
    def get_plan_type_name(cls, plan_id: str) -> str | None:
        type_id = cls.get_attribute_value_by_another_attribute_value("plan_type_id", "id", plan_id)
        if type_id is None:
            return None
        attribute_value = PlanTypeLayer.get_attribute_value_by_another_attribute_value("name", "id", cast(str, type_id))
        return deserialize_localized_text(attribute_value)

    @classmethod
    def get_plan_producers_plan_identifier(cls, plan_id: str) -> str | None:
        producers_id = cls.get_attribute_value_by_another_attribute_value("producers_plan_identifier", "id", plan_id)
        if producers_id is None:
            return None
        return cast(str, producers_id)

class PlanObjectLayer(AbstractPlanLayer):
    @classmethod
    def feature_from_model(cls, model: PlanObject, plan_id: str | None = None) -> QgsFeature:
        if not model.geom:
            message = "Plan feature must have a geometry to be added to the layer"
            raise ValueError(message)

        feature = cls.initialize_feature_from_model(model)
        feature.setGeometry(model.geom)
        feature["name"] = serialize_localized_text(model.name)
        feature["type_of_underground_id"] = model.type_of_underground_id
        feature["description"] = serialize_localized_text(model.description)
        feature["plan_id"] = plan_id if plan_id else get_active_plan_id()

        return feature

    @classmethod
    def models_from_features(cls, features: list[QgsFeature]) -> list[PlanObject]:
        plan_object_ids = {feat["id"] for feat in features}
        plan_object_field_name = RegulationGroupAssociationLayer.layer_name_to_attribute_map.get(cls.name)
        if not plan_object_field_name:
            return []

        association_features = RegulationGroupAssociationLayer.get_features_by_attribute_value(
            plan_object_field_name, plan_object_ids
        )

        plan_object_ids_by_group_id: dict[str, list[str]] = defaultdict(list)
        for association in association_features:
            plan_object_ids_by_group_id[association["plan_regulation_group_id"]].append(
                association[plan_object_field_name]
            )

        regulation_group_ids = set(plan_object_ids_by_group_id)
        regulation_group_features = list(
            RegulationGroupLayer.get_features_by_attribute_value("id", regulation_group_ids)
        )
        regulation_group_models = RegulationGroupLayer.models_from_features(regulation_group_features)

        groups_by_plan_object_id: dict[str, list[RegulationGroup]] = defaultdict(list)
        for group in regulation_group_models:
            group_id = group.id_
            if group_id:
                for plan_object_id in plan_object_ids_by_group_id.get(group_id, []):
                    groups_by_plan_object_id[plan_object_id].append(group)

        return [
            PlanObject(
                geom=feature.geometry(),
                type_of_underground_id=feature["type_of_underground_id"],
                layer_name=cls.get_from_project().name(),
                name=deserialize_localized_text(feature["name"]),
                description=deserialize_localized_text(feature["description"]),
                regulation_groups=groups_by_plan_object_id[feature["id"]],
                plan_id=feature["plan_id"],
                modified=False,
                id_=feature["id"],
            )
            for feature in features
        ]

    @classmethod
    def model_from_feature(cls, feature: QgsFeature) -> PlanObject:
        return cls.models_from_features([feature])[0]


class PointLayer(PlanObjectLayer):
    name = "Pisteet"
    filter_template = Template("plan_id = '$plan_id'")


class LineLayer(PlanObjectLayer):
    name = "Viivat"
    filter_template = Template("plan_id = '$plan_id'")


class LandUseAreaLayer(PlanObjectLayer):
    name = "Aluevaraus"
    filter_template = Template("plan_id = '$plan_id'")


class OtherAreaLayer(PlanObjectLayer):
    name = "Osa-alue"
    filter_template = Template("plan_id = '$plan_id'")


class RegulationGroupLayer(AbstractPlanLayer):
    name = "Kaavamääräysryhmät"
    filter_template = Template("plan_id = '$plan_id'")

    @classmethod
    def feature_from_model(cls, model: RegulationGroup, plan_id: str | None = None) -> QgsFeature:
        feature = cls.initialize_feature_from_model(model)

        # TODO: Change `short_name` into `letter_code` in DB
        # TODO: Change `name` into `heading` or `regulation_heading` in DB
        feature["short_name"] = model.letter_code if model.letter_code else None
        feature["name"] = serialize_localized_text(model.heading)
        feature["type_of_plan_regulation_group_id"] = model.type_code_id
        feature["plan_id"] = plan_id if plan_id else get_active_plan_id()
        feature["id"] = model.id_ if model.id_ else feature["id"]
        feature["ordering"] = model.group_number if model.group_number else None
        return feature

    @classmethod
    def models_from_features(cls, features: list[QgsFeature]) -> list[RegulationGroup]:
        group_ids = {feature["id"] for feature in features}

        regulation_features = list(
            PlanRegulationLayer.get_features_by_attribute_value("plan_regulation_group_id", group_ids)
        )
        regulation_models = PlanRegulationLayer.models_from_features(regulation_features)
        regulations_by_group_id: dict[str, list[Regulation]] = defaultdict(list)
        for regulation in regulation_models:
            if regulation.regulation_group_id:
                regulations_by_group_id[regulation.regulation_group_id].append(regulation)

        proposition_features = list(
            PlanPropositionLayer.get_features_by_attribute_value("plan_regulation_group_id", group_ids)
        )
        proposition_models = PlanPropositionLayer.models_from_features(proposition_features)
        propositions_by_group_id: dict[str, list[Proposition]] = defaultdict(list)
        for proposition in proposition_models:
            if proposition.regulation_group_id:
                propositions_by_group_id[proposition.regulation_group_id].append(proposition)

        return [
            RegulationGroup(
                type_code_id=feature["type_of_plan_regulation_group_id"],
                heading=deserialize_localized_text(feature["name"]),
                letter_code=feature["short_name"],
                color_code=None,
                group_number=feature["ordering"],
                regulations=regulations_by_group_id[feature["id"]],
                propositions=propositions_by_group_id[feature["id"]],
                modified=False,
                id_=feature["id"],
            )
            for feature in features
        ]

    @classmethod
    def model_from_feature(cls, feature: QgsFeature) -> RegulationGroup:
        return cls.models_from_features([feature])[0]


class RegulationGroupAssociationLayer(AbstractPlanLayer):
    name = "Kaavamääräysryhmien assosiaatiot"
    filter_template = Template(
        dedent(
            """\
            EXISTS (
                SELECT 1
                FROM hame.plan_regulation_group prg
                WHERE
                    hame.regulation_group_association.plan_regulation_group_id = prg.id
                    AND prg.plan_id = '$plan_id'
            )"""
        )
    )

    layer_name_to_attribute_map: ClassVar[dict[str, str]] = {
        OtherAreaLayer.name: "other_area_id",
        PointLayer.name: "point_id",
        LandUseAreaLayer.name: "land_use_area_id",
        LineLayer.name: "line_id",
        PlanLayer.name: "plan_id",
    }

    @classmethod
    def feature_from(cls, regulation_group_id: str, layer_name: str, feature_id: str) -> QgsFeature | None:
        layer = cls.get_from_project()
        attribute = cls.layer_name_to_attribute_map.get(layer_name)

        feature = QgsVectorLayerUtils.createFeature(layer)
        feature["plan_regulation_group_id"] = regulation_group_id

        if not attribute:
            msg = f"Unrecognized layer name given for saving regulation group association: {layer_name}"
            raise ValueError(msg)
        feature[attribute] = feature_id

        return feature

    @classmethod
    def association_exists(cls, regulation_group_id: str, layer_name: str, feature_id: str):
        attribute = cls.layer_name_to_attribute_map.get(layer_name)
        for feature in cls.get_features_by_attribute_value("plan_regulation_group_id", regulation_group_id):
            if feature[attribute] == feature_id:
                return True
        return False

    @classmethod
    def get_associations_for_feature(cls, feature_id: str, layer_name: str) -> Generator[QgsFeature]:
        attribute = cls.layer_name_to_attribute_map.get(layer_name)
        if not attribute:
            raise LayerNotFoundError(layer_name)
        return cls.get_features_by_attribute_value(attribute, feature_id)

    @classmethod
    def get_associations_for_regulation_group(cls, group_id: str) -> Generator[QgsFeature]:
        return cls.get_features_by_attribute_value("plan_regulation_group_id", group_id)

    @classmethod
    def get_associations_for_regulation_group_exclude_feature(
        cls, group_id: str, excluded_feature_id: str, excluded_feature_layer_name: str
    ) -> list[QgsFeature]:
        attribute = RegulationGroupAssociationLayer.layer_name_to_attribute_map.get(excluded_feature_layer_name)
        return [
            association
            for association in cls.get_associations_for_regulation_group(group_id)
            if association[attribute] != excluded_feature_id
        ]

    @classmethod
    def get_group_ids_for_feature(cls, feature_id: str, layer_name: str) -> Generator[str]:
        attribute = cls.layer_name_to_attribute_map.get(layer_name)
        if not attribute:
            raise LayerNotFoundError(layer_name)
        return cls.get_attribute_values_by_another_attribute_value("plan_regulation_group_id", attribute, feature_id)

    @classmethod
    def get_dangling_associations(  # by_feature
        cls, groups: list[RegulationGroup], feature_id: str, layer_name: str
    ) -> list[QgsFeature]:
        associations = RegulationGroupAssociationLayer.get_associations_for_feature(feature_id, layer_name)
        updated_group_ids = [group.id_ for group in groups]
        return [assoc for assoc in associations if assoc["plan_regulation_group_id"] not in updated_group_ids]


def attribute_value_model_from_feature(feature: QgsFeature) -> AttributeValue:
    return AttributeValue(
        value_data_type=feature["value_data_type"],
        numeric_value=feature["numeric_value"],
        numeric_range_min=feature["numeric_range_min"],
        numeric_range_max=feature["numeric_range_max"],
        unit=feature["unit"],
        text_value=deserialize_localized_text(feature["text_value"]),
        text_syntax=feature["text_syntax"],
        code_list=feature["code_list"],
        code_value=feature["code_value"],
        code_title=deserialize_localized_text(feature["code_title"]),
        height_reference_point=feature["height_reference_point"],
    )


def update_feature_from_attribute_value_model(value: AttributeValue | None, feature: QgsFeature):
    if value is None:
        return
    feature["value_data_type"] = value.value_data_type.value if value.value_data_type is not None else None
    feature["numeric_value"] = value.numeric_value
    feature["numeric_range_min"] = value.numeric_range_min
    feature["numeric_range_max"] = value.numeric_range_max
    feature["unit"] = value.unit
    feature["text_value"] = serialize_localized_text(value.text_value)
    feature["text_syntax"] = value.text_syntax
    feature["code_list"] = value.code_list
    feature["code_value"] = value.code_value
    feature["code_title"] = serialize_localized_text(value.code_title)
    feature["height_reference_point"] = value.height_reference_point


class PlanRegulationLayer(AbstractPlanLayer):
    name = "Kaavamääräys"
    filter_template = Template(
        dedent(
            """\
            EXISTS (
                SELECT 1
                FROM hame.plan_regulation_group prg
                WHERE
                    hame.plan_regulation.plan_regulation_group_id = prg.id
                    AND prg.plan_id = '$plan_id'
            )"""
        )
    )

    @classmethod
    def feature_from_model(cls, model: Regulation) -> QgsFeature:
        feature = cls.initialize_feature_from_model(model)

        feature["plan_regulation_group_id"] = model.regulation_group_id
        feature["type_of_plan_regulation_id"] = model.regulation_type_id
        feature["subject_identifiers"] = model.subject_identifiers

        update_feature_from_attribute_value_model(model.value, feature)

        return feature

    @classmethod
    def models_from_features(cls, features: list[QgsFeature]) -> list[Regulation]:
        regulation_ids = [feature["id"] for feature in features]

        info_features = list(
            AdditionalInformationLayer.get_features_by_attribute_value("plan_regulation_id", regulation_ids)
        )
        info_models = AdditionalInformationLayer.models_from_features(info_features)
        infos_by_regulation_id: dict[str, list[AdditionalInformation]] = defaultdict(list)
        for info in info_models:
            if info.plan_regulation_id:
                infos_by_regulation_id[info.plan_regulation_id].append(info)

        plan_theme_associations = list(
            PlanThemeAssociationLayer.get_features_by_attribute_value("plan_regulation_id", regulation_ids)
        )

        plan_theme_ids_by_regulation_id: dict[str, list[str]] = defaultdict(list)
        for association in plan_theme_associations:
            plan_theme_ids_by_regulation_id[association["plan_regulation_id"]].append(association["plan_theme_id"])

        verbal_regulation_type_associations = list(
            TypeOfVerbalRegulationAssociationLayer.get_features_by_attribute_value("plan_regulation_id", regulation_ids)
        )

        verbal_regulation_types_by_regulation_id: dict[str, list[str]] = defaultdict(list)
        for association in verbal_regulation_type_associations:
            verbal_regulation_types_by_regulation_id[association["plan_regulation_id"]].append(
                association["type_of_verbal_plan_regulation_id"]
            )

        return [
            Regulation(
                regulation_type_id=feature["type_of_plan_regulation_id"],
                value=attribute_value_model_from_feature(feature),
                additional_information=infos_by_regulation_id[feature["id"]],
                regulation_number=None,
                files=[],
                theme_ids=plan_theme_ids_by_regulation_id[feature["id"]],
                subject_identifiers=feature["subject_identifiers"],
                regulation_group_id=feature["plan_regulation_group_id"],
                verbal_regulation_type_ids=verbal_regulation_types_by_regulation_id[feature["id"]],
                modified=False,
                id_=feature["id"],
            )
            for feature in features
        ]

    @classmethod
    def model_from_feature(cls, feature: QgsFeature) -> Regulation:
        return cls.models_from_features([feature])[0]

    @classmethod
    def regulations_with_group_id(cls, group_id: str) -> Generator[QgsFeature]:
        return cls.get_features_by_attribute_value("plan_regulation_group_id", group_id)

    @classmethod
    def get_regulations_to_delete(cls, regulations: list[Regulation], group_id: str) -> list[QgsFeature]:
        updated_regulation_ids = [regulation.id_ for regulation in regulations]
        return [
            reg
            for reg in cls.get_features_by_attribute_value("plan_regulation_group_id", group_id)
            if reg["id"] not in updated_regulation_ids
        ]


class TypeOfVerbalRegulationAssociationLayer(AbstractPlanLayer):
    name = "Sanallisten kaavamääräyksien lajien assosiaatiot"
    filter_template = Template(
        dedent(
            """\
            EXISTS (
                SELECT 1
                FROM
                    hame.plan_regulation_group prg
                    JOIN hame.plan_regulation pr
                        ON (prg.id = pr.plan_regulation_group_id)
                WHERE
                    hame.type_of_verbal_regulation_association.plan_regulation_id = pr.id
                    AND prg.plan_id = '$plan_id'
            )"""
        )
    )

    @classmethod
    def feature_from(cls, regulation_id: str, type_of_verbal_regulation_id: str) -> QgsFeature | None:
        layer = cls.get_from_project()

        feature = QgsVectorLayerUtils.createFeature(layer)
        feature["plan_regulation_id"] = regulation_id
        feature["type_of_verbal_plan_regulation_id"] = type_of_verbal_regulation_id
        return feature

    @classmethod
    def association_exists(cls, regulation_id: str, type_of_verbal_regulation_id: str) -> bool:
        for feature in cls.get_features_by_attribute_value("plan_regulation_id", regulation_id):
            if feature["type_of_verbal_plan_regulation_id"] == type_of_verbal_regulation_id:
                return True
        return False

    @classmethod
    def get_associations_for_regulation(cls, regulation_id: str) -> Generator[QgsFeature]:
        return cls.get_features_by_attribute_value("plan_regulation_id", regulation_id)

    @classmethod
    def get_dangling_associations(cls, regulation_id: str, updated_type_ids: list[str]) -> list[QgsFeature]:
        associations = cls.get_associations_for_regulation(regulation_id)
        return [assoc for assoc in associations if assoc["type_of_verbal_plan_regulation_id"] not in updated_type_ids]


class LegalEffectAssociationLayer(AbstractPlanLayer):
    name = "Yleiskaavan oikeusvaikutusten assosiaatiot"
    filter_template = Template("plan_id = '$plan_id'")

    @classmethod
    def feature_from(cls, plan_id: str, legal_effect_id: str) -> QgsFeature | None:
        layer = cls.get_from_project()

        feature = QgsVectorLayerUtils.createFeature(layer)
        feature["plan_id"] = plan_id
        feature["legal_effects_of_master_plan_id"] = legal_effect_id
        return feature

    @classmethod
    def association_exists(cls, plan_id: str, legal_effect_id: str) -> bool:
        for feature in cls.get_features_by_attribute_value("plan_id", plan_id):
            if feature["legal_effects_of_master_plan_id"] == legal_effect_id:
                return True
        return False

    @classmethod
    def get_associations_for_plan(cls, plan_id: str) -> Generator[QgsFeature]:
        return cls.get_features_by_attribute_value("plan_id", plan_id)

    @classmethod
    def get_legal_effect_ids_for_plan(cls, plan_id: str) -> Generator[QgsFeature]:
        return cls.get_attribute_values_by_another_attribute_value(
            "legal_effects_of_master_plan_id", "plan_id", plan_id
        )

    @classmethod
    def get_dangling_associations(cls, plan_id: str, updated_legal_effect_ids: list[str]) -> list[QgsFeature]:
        associations = cls.get_associations_for_plan(plan_id)
        return [
            assoc for assoc in associations if assoc["legal_effects_of_master_plan_id"] not in updated_legal_effect_ids
        ]


class PlanPropositionLayer(AbstractPlanLayer):
    name = "Kaavasuositus"
    filter_template = Template(
        dedent(
            """\
            EXISTS (
                SELECT 1
                FROM hame.plan_regulation_group rg
                WHERE
                    hame.plan_proposition.plan_regulation_group_id = rg.id
                    AND rg.plan_id = '$plan_id'
            )"""
        )
    )

    @classmethod
    def feature_from_model(cls, model: Proposition) -> QgsFeature:
        feature = cls.initialize_feature_from_model(model)

        feature["text_value"] = serialize_localized_text(model.value)
        feature["plan_regulation_group_id"] = model.regulation_group_id
        feature["ordering"] = model.proposition_number
        feature["id"] = model.id_ if model.id_ else feature["id"]

        return feature

    @classmethod
    def models_from_features(cls, features: list[QgsFeature]) -> list[Proposition]:
        proposition_ids = {feature["id"] for feature in features}
        plan_theme_associations = list(
            PlanThemeAssociationLayer.get_features_by_attribute_value("plan_proposition_id", proposition_ids)
        )

        plan_theme_ids_by_proposition_id: dict[str, list[str]] = defaultdict(list)
        for association in plan_theme_associations:
            plan_theme_ids_by_proposition_id[association["plan_proposition_id"]].append(association["plan_theme_id"])

        return [
            Proposition(
                value=deserialize_localized_text(feature["text_value"]),
                regulation_group_id=feature["plan_regulation_group_id"],
                proposition_number=feature["ordering"],
                theme_ids=plan_theme_ids_by_proposition_id[feature["id"]],
                modified=False,
                id_=feature["id"],
            )
            for feature in features
        ]

    @classmethod
    def model_from_feature(cls, feature: QgsFeature) -> Proposition:
        return cls.models_from_features([feature])[0]

    @classmethod
    def propositions_with_group_id(cls, group_id: str) -> Generator[QgsFeature]:
        return cls.get_features_by_attribute_value("plan_regulation_group_id", group_id)

    @classmethod
    def get_propositions_to_delete(cls, propositions: list[Proposition], group_id: str) -> list[QgsFeature]:
        updated_proposition_ids = [proposition.id_ for proposition in propositions]
        return [
            prop
            for prop in cls.get_features_by_attribute_value("plan_regulation_group_id", group_id)
            if prop["id"] not in updated_proposition_ids
        ]


class PlanThemeAssociationLayer(AbstractPlanLayer):
    name = "Kaavoitusteemojen assosiaatiot"
    filter_template = Template(
        dedent(
            """\
            EXISTS (
                SELECT 1
                FROM
                    hame.plan_regulation_group prg
                    LEFT JOIN hame.plan_regulation pr
                        ON prg.id = pr.plan_regulation_group_id
                    LEFT JOIN hame.plan_proposition pp
                        ON prg.id = pp.plan_regulation_group_id
                WHERE
                    prg.plan_id = '$plan_id'
                    AND (
                    hame.plan_theme_association.plan_regulation_id = pr.id
                        OR hame.plan_theme_association.plan_proposition_id = pp.id
                )
            )"""
        )
    )

    @classmethod
    def feature_from(
        cls, plan_theme_id: str, plan_regulation_id: str | None = None, plan_proposition_id: str | None = None
    ) -> QgsFeature | None:
        layer = cls.get_from_project()

        feature = QgsVectorLayerUtils.createFeature(layer)
        feature["plan_regulation_id"] = plan_regulation_id
        feature["plan_proposition_id"] = plan_proposition_id
        feature["plan_theme_id"] = plan_theme_id
        return feature

    @classmethod
    def regulation_association_exists(cls, plan_theme_id: str, plan_regulation_id: str | None = None) -> bool:
        if plan_regulation_id:
            for feature in cls.get_features_by_attribute_value("plan_regulation_id", plan_regulation_id):
                if feature["plan_theme_id"] == plan_theme_id:
                    return True
        return False

    @classmethod
    def proposition_association_exists(cls, plan_theme_id: str, plan_proposition_id: str | None = None) -> bool:
        if plan_proposition_id:
            for feature in cls.get_features_by_attribute_value("plan_proposition_id", plan_proposition_id):
                if feature["plan_theme_id"] == plan_theme_id:
                    return True
        return False

    @classmethod
    def get_associations_for_plan_regulation(cls, plan_regulation_id: str) -> Generator[QgsFeature]:
        return cls.get_features_by_attribute_value("plan_regulation_id", plan_regulation_id)

    @classmethod
    def get_associations_for_plan_proposition(cls, plan_proposition_id: str) -> Generator[QgsFeature]:
        return cls.get_features_by_attribute_value("plan_proposition_id", plan_proposition_id)

    @classmethod
    def get_dangling_regulation_associations(
        cls, plan_regulation_id: str, updated_plan_theme_ids: list[str]
    ) -> list[QgsFeature]:
        associations = cls.get_associations_for_plan_regulation(plan_regulation_id)
        return [assoc for assoc in associations if assoc["plan_theme_id"] not in updated_plan_theme_ids]

    @classmethod
    def get_dangling_proposition_associations(
        cls, plan_proposition_id: str, updated_plan_theme_ids: list[str]
    ) -> list[QgsFeature]:
        associations = cls.get_associations_for_plan_proposition(plan_proposition_id)
        return [assoc for assoc in associations if assoc["plan_theme_id"] not in updated_plan_theme_ids]


class DocumentLayer(AbstractPlanLayer):
    name = "Asiakirjat"
    filter_template = Template("plan_id = '$plan_id'")

    @classmethod
    def feature_from_model(cls, model: Document) -> QgsFeature:
        feature = cls.initialize_feature_from_model(model)

        feature["name"] = serialize_localized_text(model.name)
        feature["url"] = model.url
        feature["permanent_document_identifier"] = model.identifier
        feature["type_of_document_id"] = model.type_of_document_id
        feature["accessibility"] = model.accessibility
        feature["category_of_publicity_id"] = model.category_of_publicity_id
        feature["personal_data_content_id"] = model.personal_data_content_id
        feature["retention_time_id"] = model.retention_time_id
        feature["language_id"] = model.language_id
        feature["document_date"] = model.document_date
        feature["arrival_date"] = model.arrival_date
        feature["confirmation_date"] = model.confirmation_date
        feature["plan_id"] = model.plan_id
        feature["id"] = model.id_ if model.id_ else feature["id"]

        return feature

    @classmethod
    def model_from_feature(cls, feature: QgsFeature) -> Document:
        return Document(
            name=deserialize_localized_text(feature["name"]),
            url=feature["url"],
            identifier=feature["permanent_document_identifier"],
            type_of_document_id=feature["type_of_document_id"],
            accessibility=feature["accessibility"],
            category_of_publicity_id=feature["category_of_publicity_id"],
            personal_data_content_id=feature["personal_data_content_id"],
            retention_time_id=feature["retention_time_id"],
            language_id=feature["language_id"],
            document_date=feature["document_date"].date() if feature["document_date"] else None,
            arrival_date=feature["arrival_date"].date() if feature["confirmation_date"] else None,
            confirmation_date=feature["confirmation_date"].date() if feature["confirmation_date"] else None,
            plan_id=feature["plan_id"],
            modified=False,
            id_=feature["id"],
        )

    @classmethod
    def get_documents_to_delete(cls, documents: list[Document], plan_id: str) -> list[QgsFeature]:
        updated_document_ids = [doc.id_ for doc in documents]
        return [
            doc
            for doc in cls.get_features_by_attribute_value("plan_id", plan_id)
            if doc["id"] not in updated_document_ids
        ]


# class SourceDataLayer(AbstractPlanLayer):
    # name = "Lähtötietoaineistot"
    # filter_template = Template("plan_id = '$plan_id'")


class SourceDataLayer(AbstractPlanLayer):
    name = "Lähtötietoaineistot"
    filter_template = Template("plan_matter_id = '$plan_matter_id'")

    @classmethod
    def filter_layer_by_plan_id(cls, plan_id: str | None) -> None:
        if not plan_id or cls.filter_template is None:
            return cls.hide_all_features()

        try:
            plan_matter_id = PlanLayer.get_attribute_value_by_another_attribute_value("plan_matter_id", "id", plan_id)
            if not plan_matter_id:
                return cls.hide_all_features()

            cls.apply_filter(cls.filter_template.substitute(plan_matter_id=plan_matter_id))
        except Exception as e:
            iface.messageBar().pushMessage("Virhe", f"Lähtötietoaineiston suodatus epäonnistui: {e}", level=3)
            cls.hide_all_features()


class AdditionalInformationLayer(AbstractPlanLayer):
    name = "Kaavamääräyksen lisätiedot"
    filter_template = Template(
        dedent(
            """\
            EXISTS (
                SELECT 1
                FROM
                    hame.plan_regulation_group prg
                    JOIN hame.plan_regulation pr
                        ON (prg.id = pr.plan_regulation_group_id)
                WHERE
                    hame.additional_information.plan_regulation_id = pr.id
                    AND prg.plan_id = '$plan_id'
            )"""
        )
    )

    @classmethod
    def feature_from_model(cls, model: AdditionalInformation) -> QgsFeature:
        feature = cls.initialize_feature_from_model(model)

        feature["plan_regulation_id"] = model.plan_regulation_id
        feature["type_additional_information_id"] = model.additional_information_type_id

        update_feature_from_attribute_value_model(model.value, feature)

        return feature

    @classmethod
    def models_from_features(cls, features: list[QgsFeature]) -> list[AdditionalInformation]:
        return [
            AdditionalInformation(
                additional_information_type_id=feature["type_additional_information_id"],
                id_=feature["id"],
                plan_regulation_id=feature["plan_regulation_id"],
                value=attribute_value_model_from_feature(feature),
                modified=False,
            )
            for feature in features
        ]

    @classmethod
    def model_from_feature(cls, feature: QgsFeature) -> AdditionalInformation:
        return cls.models_from_features([feature])[0]

    @classmethod
    def get_additional_information_to_delete(
        cls, additional_infos: list[AdditionalInformation], regulation_id: str
    ) -> list[QgsFeature]:
        updated_info_ids = [info.id_ for info in additional_infos]
        return [
            info
            for info in cls.get_features_by_attribute_value("plan_regulation_id", regulation_id)
            if info["id"] not in updated_info_ids
        ]


class LifeCycleLayer(AbstractPlanLayer):
    name = "Elinkaaren päiväykset"
    filter_template = None

    @classmethod
    def feature_from_model(cls, model: LifeCycle) -> QgsFeature:
        feature = cls.initialize_feature_from_model(model)

        feature["id"] = model.id_ if model.id_ else feature["id"]
        feature["lifecycle_status_id"] = model.status_id
        feature["starting_at"] = model.starting_at
        feature["ending_at"] = model.ending_at if model.ending_at else None
        feature["plan_id"] = model.plan_id
        feature["land_use_area_id"] = model.land_use_are_id
        feature["other_area_id"] = model.other_area_id
        feature["line_id"] = model.line_id
        feature["point_id"] = model.point_id
        feature["plan_regulation_id"] = model.plan_regulation_id
        feature["plan_proposition_id"] = model.plan_proposition_id

        return feature

    @classmethod
    def model_from_feature(cls, feature: QgsFeature) -> LifeCycle:
        return LifeCycle(
            id_=feature["id"],
            status_id=feature["lifecycle_status_id"],
            starting_at=feature["starting_at"].date() if feature["starting_at"] else None,
            ending_at=feature["ending_at"].date() if feature["ending_at"] else None,
            plan_id=feature["plan_id"],
            land_use_are_id=feature["land_use_area_id"],
            other_area_id=feature["other_area_id"],
            line_id=feature["line_id"],
            point_id=feature["point_id"],
            plan_regulation_id=feature["plan_regulation_id"],
            plan_proposition_id=feature["plan_proposition_id"],
            modified=False,
        )

    @classmethod
    def get_features_by_plan_id(cls, plan_id: str) -> list[QgsFeature]:
        return list(cls.get_features_by_attribute_value("plan_id", plan_id))


def get_plan_feature_layer_class_by_model(plan_feature: PlanObject) -> type[PlanObjectLayer]:
    layer_name = plan_feature.layer_name
    if not layer_name:
        msg = "Cannot save plan feature without a target layer"
        raise ValueError(msg)
    layer_class = FEATURE_LAYER_NAME_TO_CLASS_MAP.get(layer_name)
    if not layer_class:
        msg = f"Could not find plan feature layer class for layer name {layer_name}"
        raise ValueError(msg)

    return layer_class


def get_plan_feature_layer_class_by_layer_name(layer_name: str) -> type[PlanObjectLayer]:
    layer = FEATURE_LAYER_NAME_TO_CLASS_MAP.get(layer_name)
    if not layer:
        msg = f"Could not find plan feature layer class for layer name {layer_name}"
        raise ValueError(msg)
    return layer


FEATURE_LAYER_NAME_TO_CLASS_MAP: dict[str, type[PlanObjectLayer]] = {
    PointLayer.name: PointLayer,
    LineLayer.name: LineLayer,
    OtherAreaLayer.name: OtherAreaLayer,
    LandUseAreaLayer.name: LandUseAreaLayer,
}

plan_layers = AbstractPlanLayer.__subclasses__()
plan_layers.remove(PlanObjectLayer)

plan_feature_layers = PlanObjectLayer.__subclasses__()
plan_layers.extend(plan_feature_layers)
