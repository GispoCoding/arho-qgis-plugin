from __future__ import annotations

import logging
import os
from abc import abstractmethod
from string import Template
from textwrap import dedent
from typing import Any, ClassVar, Generator, cast

from PyQt5.QtCore import QMetaType
from qgis.core import QgsFeature, QgsField, QgsVectorLayer, QgsVectorLayerUtils

from arho_feature_template.core.models import (
    AdditionalInformation,
    AttributeValue,
    Document,
    LifeCycle,
    Plan,
    PlanFeature,
    Proposition,
    Regulation,
    RegulationGroup,
)
from arho_feature_template.exceptions import FeatureNotFoundError, LayerEditableError, LayerNotFoundError
from arho_feature_template.project.layers import AbstractLayer
from arho_feature_template.project.layers.code_layers import PlanTypeLayer
from arho_feature_template.qgis_plugin_tools.tools.resources import resources_path
from arho_feature_template.utils.misc_utils import (
    deserialize_localized_text,
    get_active_plan_id,
    iface,
    serialize_localized_text,
)

logger = logging.getLogger(__name__)

QLR_PATH = resources_path("configs", "layer_configs")


class AbstractPlanLayer(AbstractLayer):
    filter_template: ClassVar[Template | None]

    @classmethod
    def apply_filter(cls, plan_id: str | None) -> None:
        """Apply a filter to the layer based on the plan_id."""
        if cls.filter_template is None:
            return
        filter_expression = cls.filter_template.substitute(plan_id=plan_id) if plan_id else ""
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


class PlanLayer(AbstractPlanLayer):
    name = "Kaava"
    filter_template = Template("id = '$plan_id'")
    qlr_path = os.path.join(QLR_PATH, "plan.qlr")

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
        feature["permanent_plan_identifier"] = model.permanent_plan_identifier
        feature["record_number"] = model.record_number
        feature["producers_plan_identifier"] = model.producers_plan_identifier
        feature["matter_management_identifier"] = model.matter_management_identifier
        feature["plan_type_id"] = model.plan_type_id
        feature["lifecycle_status_id"] = model.lifecycle_status_id
        feature["organisation_id"] = model.organisation_id

        return feature

    @classmethod
    def model_from_feature(cls, feature: QgsFeature) -> Plan:
        general_regulation_features = [
            RegulationGroupLayer.get_feature_by_id(group_id)
            for group_id in RegulationGroupAssociationLayer.get_group_ids_for_feature(feature["id"], cls.name)
        ]
        return Plan(
            geom=feature.geometry(),
            name=deserialize_localized_text(feature["name"]),
            description=deserialize_localized_text(feature["description"]),
            scale=feature["scale"],
            permanent_plan_identifier=feature["permanent_plan_identifier"],
            record_number=feature["record_number"],
            producers_plan_identifier=feature["producers_plan_identifier"],
            matter_management_identifier=feature["matter_management_identifier"],
            plan_type_id=feature["plan_type_id"],
            lifecycle_status_id=feature["lifecycle_status_id"],
            organisation_id=feature["organisation_id"],
            general_regulations=[
                RegulationGroupLayer.model_from_feature(feat)
                for feat in general_regulation_features
                if feat is not None
            ],
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

    @classmethod
    def create_qgis_layer(cls) -> QgsVectorLayer:
        layer = QgsVectorLayer("MultiPolygon?crs=epsg:3067", "Kaava", "memory")
        provider = layer.dataProvider()
        layer.startEditing()
        provider.addAttributes(
            [
                QgsField("name", QMetaType.QString),
                QgsField("id", QMetaType.QString),
                QgsField("created_at", QMetaType.QDate),
                QgsField("modified_at", QMetaType.QDate),
                QgsField("exported_at", QMetaType.QDate),
                QgsField("lifecycle_status_id", QMetaType.QString),
                QgsField("organisation_id", QMetaType.QString),
                QgsField("plan_type_id", QMetaType.QString),
                QgsField("permanent_plan_identifier", QMetaType.QString),
                QgsField("producers_plan_identifier", QMetaType.QString),
                QgsField("description", QMetaType.QString),
                QgsField("scale", QMetaType.Int),
                QgsField("matter_management_identifier", QMetaType.QString),
                QgsField("record_number", QMetaType.QString),
                QgsField("validated_at", QMetaType.QDate),
                QgsField("validation_errors", QMetaType.QString),
            ]
        )
        layer.commitChanges()

        return layer


class PlanFeatureLayer(AbstractPlanLayer):
    @classmethod
    def feature_from_model(cls, model: PlanFeature, plan_id: str | None = None) -> QgsFeature:
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
    def model_from_feature(cls, feature: QgsFeature) -> PlanFeature:
        regulation_group_features = [
            RegulationGroupLayer.get_feature_by_id(group_id)
            for group_id in RegulationGroupAssociationLayer.get_group_ids_for_feature(feature["id"], cls.name)
        ]

        return PlanFeature(
            geom=feature.geometry(),
            type_of_underground_id=feature["type_of_underground_id"],
            layer_name=cls.get_from_project().name(),
            name=deserialize_localized_text(feature["name"]),
            description=deserialize_localized_text(feature["description"]),
            regulation_groups=[
                RegulationGroupLayer.model_from_feature(feat) for feat in regulation_group_features if feat is not None
            ],
            plan_id=feature["plan_id"],
            modified=False,
            id_=feature["id"],
        )

    # @classmethod
    # def create_qgis_layer(cls) -> QgsVectorLayer:
    #     layer = QgsVectorLayer(f"{cls.geom}?crs=epsg:3067", cls.name, "memory")  # ignore
    #     provider = layer.dataProvider()
    #     layer.startEditing()
    #     provider.addAttributes(
    #         [
    #             QgsField("name", QMetaType.QString),
    #             QgsField("id", QMetaType.QString),
    #             QgsField("created_at", QMetaType.QDate),
    #             QgsField("modified_at", QMetaType.QDate),
    #             QgsField("exported_at", QMetaType.QDate),
    #             QgsField("description", QMetaType.QString),
    #             QgsField("source_data_object", QMetaType.QString),
    #             QgsField("height_unit", QMetaType.QString),
    #             QgsField("ordering", QMetaType.Int),
    #             QgsField("type_of_underground", QMetaType.QString),
    #             QgsField("plan_id", QMetaType.QString),
    #             QgsField("lifecycle_status_id", QMetaType.QString),
    #             QgsField("height_min", QMetaType.Double),
    #             QgsField("height_max", QMetaType.Double),
    #             QgsField("height_reference_point", QMetaType.QString),
    #             QgsField("short_names", QMetaType.QStringList),
    #             QgsField("type_regulations", QMetaType.QString),
    #             QgsField("regulation_values", QMetaType.QString),
    #         ]
    #     )
    #     layer.commitChanges()

    #     return layer


class LandUsePointLayer(PlanFeatureLayer):
    name = "Maankäytön kohteet"
    geom = "MultiPoint"
    filter_template = Template("plan_id = '$plan_id'")
    qlr_path = os.path.join(QLR_PATH, "land_use_point.qlr")


class OtherPointLayer(PlanFeatureLayer):
    name = "Muut pisteet"
    geom = "MultiPoint"
    filter_template = Template("plan_id = '$plan_id'")
    qlr_path = os.path.join(QLR_PATH, "other_point.qlr")


class LineLayer(PlanFeatureLayer):
    name = "Viivat"
    geom = "MultiLineString"
    filter_template = Template("plan_id = '$plan_id'")
    qlr_path = os.path.join(QLR_PATH, "line.qlr")


class LandUseAreaLayer(PlanFeatureLayer):
    name = "Aluevaraus"
    geom = "MultiPolygon"
    filter_template = Template("plan_id = '$plan_id'")
    qlr_path = os.path.join(QLR_PATH, "land_use_area.qlr")


class OtherAreaLayer(PlanFeatureLayer):
    name = "Osa-alue"
    geom = "MultiPolygon"
    filter_template = Template("plan_id = '$plan_id'")
    qlr_path = os.path.join(QLR_PATH, "other_area.qlr")


class RegulationGroupLayer(AbstractPlanLayer):
    name = "Kaavamääräysryhmät"
    filter_template = Template("plan_id = '$plan_id'")
    qlr_path = os.path.join(QLR_PATH, "plan_regulation_group.qlr")

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
    def model_from_feature(cls, feature: QgsFeature) -> RegulationGroup:
        return RegulationGroup(
            type_code_id=feature["type_of_plan_regulation_group_id"],
            heading=deserialize_localized_text(feature["name"]),
            letter_code=feature["short_name"],
            color_code=None,
            group_number=feature["ordering"],
            regulations=[
                PlanRegulationLayer.model_from_feature(feat)
                for feat in PlanRegulationLayer.regulations_with_group_id(feature["id"])
            ],
            propositions=[
                PlanPropositionLayer.model_from_feature(feat)
                for feat in PlanPropositionLayer.propositions_with_group_id(feature["id"])
            ],
            modified=False,
            id_=feature["id"],
        )

    @classmethod
    def create_qgis_layer(cls) -> QgsVectorLayer:
        layer = QgsVectorLayer("none", cls.name, "memory")
        provider = layer.dataProvider()
        layer.startEditing()
        provider.addAttributes(
            [
                QgsField("short_name", QMetaType.QString),
                QgsField("name", QMetaType.QString),
                QgsField("id", QMetaType.QString),
                QgsField("created_at", QMetaType.QDate),
                QgsField("modified_at", QMetaType.QDate),
                QgsField("ordering", QMetaType.Int),
                QgsField("plan_id", QMetaType.QString),
                QgsField("type_of_plan_regulation_group_id", QMetaType.QString),
            ]
        )
        layer.commitChanges()

        return layer


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
    qlr_path = os.path.join(QLR_PATH, "plan_regulation_group_associations.qlr")

    layer_name_to_attribute_map: ClassVar[dict[str, str]] = {
        LandUsePointLayer.name: "land_use_point_id",
        OtherAreaLayer.name: "other_area_id",
        OtherPointLayer.name: "other_point_id",
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

    @classmethod
    def create_qgis_layer(cls) -> QgsVectorLayer:
        layer = QgsVectorLayer("none", cls.name, "memory")
        provider = layer.dataProvider()
        layer.startEditing()
        provider.addAttributes(
            [
                QgsField("id", QMetaType.QString),
                QgsField("plan_regulation_group_id", QMetaType.QString),
                QgsField("plan_id", QMetaType.QString),
                QgsField("land_use_area_id", QMetaType.QString),
                QgsField("other_area_id", QMetaType.QString),
                QgsField("land_use_point_id", QMetaType.QString),
                QgsField("other_point_id", QMetaType.QString),
                QgsField("line_id", QMetaType.QString),
            ]
        )
        layer.commitChanges()

        return layer


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
    qlr_path = os.path.join(QLR_PATH, "plan_regulation.qlr")

    @classmethod
    def feature_from_model(cls, model: Regulation) -> QgsFeature:
        feature = cls.initialize_feature_from_model(model)

        feature["plan_regulation_group_id"] = model.regulation_group_id
        feature["type_of_plan_regulation_id"] = model.regulation_type_id
        feature["subject_identifiers"] = model.subject_identifiers

        update_feature_from_attribute_value_model(model.value, feature)

        return feature

    @classmethod
    def model_from_feature(cls, feature: QgsFeature) -> Regulation:
        return Regulation(
            regulation_type_id=feature["type_of_plan_regulation_id"],
            value=attribute_value_model_from_feature(feature),
            additional_information=[
                AdditionalInformationLayer.model_from_feature(ai_feat)
                for ai_feat in AdditionalInformationLayer.get_features_by_attribute_value(
                    "plan_regulation_id", feature["id"]
                )
            ],
            regulation_number=None,
            files=[],
            theme_ids=(list(PlanThemeAssociationLayer.get_plan_theme_id_for_plan_regulation(feature["id"]))),
            subject_identifiers=feature["subject_identifiers"],
            regulation_group_id=feature["plan_regulation_group_id"],
            verbal_regulation_type_ids=(
                list(TypeOfVerbalRegulationAssociationLayer.get_verbal_type_ids_for_regulation(feature["id"]))
            ),
            modified=False,
            id_=feature["id"],
        )

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

    @classmethod
    def create_qgis_layer(cls) -> QgsVectorLayer:
        layer = QgsVectorLayer("none", cls.name, "memory")
        provider = layer.dataProvider()
        layer.startEditing()
        provider.addAttributes(
            [
                QgsField("plan_regulation_group_id", QMetaType.QString),
                QgsField("type_of_plan_regulation_id", QMetaType.QString),
                QgsField("unit", QMetaType.QString),
                QgsField("text_value", QMetaType.QString),
                QgsField("numeric_value", QMetaType.Double),
                QgsField("exported_at", QMetaType.QDate),
                QgsField("lifecycle_status_id", QMetaType.QString),
                QgsField("id", QMetaType.QString),
                QgsField("created_at", QMetaType.QDate),
                QgsField("modified_at", QMetaType.QDate),
                QgsField("ordering", QMetaType.Int),
                QgsField("subject_identifiers", QMetaType.QStringList),
                QgsField("numeric_range_min", QMetaType.Double),
                QgsField("numeric_range_max", QMetaType.Double),
                QgsField("value_data_type", QMetaType.QString),
                QgsField("text_syntax", QMetaType.QString),
                QgsField("code_list", QMetaType.QString),
                QgsField("code_value", QMetaType.QString),
                QgsField("code_title", QMetaType.QString),
                QgsField("height_reference_point", QMetaType.QString),
            ]
        )
        layer.commitChanges()

        return layer


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
    qlr_path = os.path.join(QLR_PATH, "verbal_regulation_type_associations.qlr")

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
    def get_verbal_type_ids_for_regulation(cls, regulation_id: str) -> Generator[QgsFeature]:
        return cls.get_attribute_values_by_another_attribute_value(
            "type_of_verbal_plan_regulation_id", "plan_regulation_id", regulation_id
        )

    @classmethod
    def get_dangling_associations(cls, regulation_id: str, updated_type_ids: list[str]) -> list[QgsFeature]:
        associations = cls.get_associations_for_regulation(regulation_id)
        return [assoc for assoc in associations if assoc["type_of_verbal_plan_regulation_id"] not in updated_type_ids]

    @classmethod
    def create_qgis_layer(cls) -> QgsVectorLayer:
        layer = QgsVectorLayer("none", cls.name, "memory")
        provider = layer.dataProvider()
        layer.startEditing()
        provider.addAttributes(
            [
                QgsField("plan_regulation_id", QMetaType.QString),
                QgsField("type_of_verbal_plan_regulation_id", QMetaType.QString),
            ]
        )
        layer.commitChanges()

        return layer


class LegalEffectAssociationLayer(AbstractPlanLayer):
    name = "Yleiskaavan oikeusvaikutusten assosiaatiot"
    filter_template = None
    qlr_path = os.path.join(QLR_PATH, "legal_effect_associations.qlr")

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

    @classmethod
    def create_qgis_layer(cls) -> QgsVectorLayer:
        layer = QgsVectorLayer("none", cls.name, "memory")
        provider = layer.dataProvider()
        layer.startEditing()
        provider.addAttributes(
            [
                QgsField("plan_id", QMetaType.QString),
                QgsField("legal_effects_of_master_plan_id", QMetaType.QString),
            ]
        )
        layer.commitChanges()

        return layer


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
    qlr_path = os.path.join(QLR_PATH, "plan_proposition.qlr")

    @classmethod
    def feature_from_model(cls, model: Proposition) -> QgsFeature:
        feature = cls.initialize_feature_from_model(model)

        feature["text_value"] = serialize_localized_text(model.value)
        feature["plan_regulation_group_id"] = model.regulation_group_id
        feature["ordering"] = model.proposition_number
        feature["id"] = model.id_ if model.id_ else feature["id"]

        return feature

    @classmethod
    def model_from_feature(cls, feature: QgsFeature) -> Proposition:
        proposition_value = deserialize_localized_text(feature["text_value"])
        return Proposition(
            value=proposition_value,
            regulation_group_id=feature["plan_regulation_group_id"],
            proposition_number=feature["ordering"],
            theme_ids=(list(PlanThemeAssociationLayer.get_plan_theme_id_for_plan_proposition(feature["id"]))),
            modified=False,
            id_=feature["id"],
        )

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

    @classmethod
    def create_qgis_layer(cls) -> QgsVectorLayer:
        layer = QgsVectorLayer("none", cls.name, "memory")
        provider = layer.dataProvider()
        layer.startEditing()
        provider.addAttributes(
            [
                QgsField("plan_regulation_group_id", QMetaType.QString),
                QgsField("text_value", QMetaType.QString),
                QgsField("exported_at", QMetaType.QDate),
                QgsField("lifecycle_status_id", QMetaType.QString),
                QgsField("id", QMetaType.QString),
                QgsField("created_at", QMetaType.QDate),
                QgsField("modified_at", QMetaType.QDate),
                QgsField("ordering", QMetaType.Int),
            ]
        )
        layer.commitChanges()

        return layer


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
    qlr_path = os.path.join(QLR_PATH, "plan_theme_associations.qlr")

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
    def get_plan_theme_id_for_plan_regulation(cls, plan_regulation_id: str) -> Generator[QgsFeature]:
        return cls.get_attribute_values_by_another_attribute_value(
            "plan_theme_id", "plan_regulation_id", plan_regulation_id
        )

    @classmethod
    def get_plan_theme_id_for_plan_proposition(cls, plan_proposition_id: str) -> Generator[QgsFeature]:
        return cls.get_attribute_values_by_another_attribute_value(
            "plan_theme_id", "plan_proposition_id", plan_proposition_id
        )

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

    @classmethod
    def create_qgis_layer(cls) -> QgsVectorLayer:
        layer = QgsVectorLayer("none", cls.name, "memory")
        provider = layer.dataProvider()
        layer.startEditing()
        provider.addAttributes(
            [
                QgsField("id", QMetaType.QString),
                QgsField("plan_regulation_id", QMetaType.QString),
                QgsField("plan_proposition_id", QMetaType.QString),
                QgsField("plan_theme_id", QMetaType.QString),
            ]
        )
        layer.commitChanges()

        return layer


class DocumentLayer(AbstractPlanLayer):
    name = "Asiakirjat"
    filter_template = Template("plan_id = '$plan_id'")
    qlr_path = os.path.join(QLR_PATH, "documents.qlr")

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

    @classmethod
    def create_qgis_layer(cls) -> QgsVectorLayer:
        layer = QgsVectorLayer("none", cls.name, "memory")
        provider = layer.dataProvider()
        layer.startEditing()
        provider.addAttributes(
            [
                QgsField("type_of_document_id", QMetaType.QString),
                QgsField("decision_date", QMetaType.QDate),
                QgsField("id", QMetaType.QString),
                QgsField("created_at", QMetaType.QDate),
                QgsField("modified_at", QMetaType.QDate),
                QgsField("plan_id", QMetaType.QString),
                QgsField("permanent_document_identifier", QMetaType.QString),
                QgsField("category_of_publicity_id", QMetaType.QString),
                QgsField("url", QMetaType.QString),
                QgsField("personal_data_content_id", QMetaType.QString),
                QgsField("retention_time_id", QMetaType.QString),
                QgsField("language_id", QMetaType.QString),
                QgsField("exported_at", QMetaType.QDate),
                QgsField("exported_file_key", QMetaType.QString),
                QgsField("arrival_date", QMetaType.QDate),
                QgsField("confirmation_date", QMetaType.QDate),
                QgsField("document_date", QMetaType.QDate),
                QgsField("name", QMetaType.QString),
                QgsField("accessibility", QMetaType.Bool),
                QgsField("exported_file_etag", QMetaType.QString),
            ]
        )
        layer.commitChanges()

        return layer


class SourceDataLayer(AbstractPlanLayer):
    name = "Lähtötietoaineistot"
    filter_template = Template("plan_id = '$plan_id'")
    qlr_path = os.path.join(QLR_PATH, "source_data.qlr")

    @classmethod
    def create_qgis_layer(cls) -> QgsVectorLayer:
        layer = QgsVectorLayer("none", cls.name, "memory")
        provider = layer.dataProvider()
        layer.startEditing()
        provider.addAttributes(
            [
                QgsField("type_of_source_data_id", QMetaType.QString),
                QgsField("name", QMetaType.QString),
                QgsField("additional_information_uri", QMetaType.QString),
                QgsField("id", QMetaType.QString),
                QgsField("created_at", QMetaType.QDate),
                QgsField("modified_at", QMetaType.QDate),
                QgsField("detachment_date", QMetaType.QDate),
                QgsField("plan_id", QMetaType.QString),
            ]
        )
        layer.commitChanges()

        return layer


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
    qlr_path = os.path.join(QLR_PATH, "additional_information.qlr")

    @classmethod
    def feature_from_model(cls, model: AdditionalInformation) -> QgsFeature:
        feature = cls.initialize_feature_from_model(model)

        feature["plan_regulation_id"] = model.plan_regulation_id
        feature["type_additional_information_id"] = model.additional_information_type_id

        update_feature_from_attribute_value_model(model.value, feature)

        return feature

    @classmethod
    def model_from_feature(cls, feature: QgsFeature) -> AdditionalInformation:
        return AdditionalInformation(
            additional_information_type_id=feature["type_additional_information_id"],
            id_=feature["id"],
            plan_regulation_id=feature["plan_regulation_id"],
            value=attribute_value_model_from_feature(feature),
            modified=False,
        )

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

    @classmethod
    def create_qgis_layer(cls) -> QgsVectorLayer:
        layer = QgsVectorLayer("none", cls.name, "memory")
        provider = layer.dataProvider()
        layer.startEditing()
        provider.addAttributes(
            [
                QgsField("plan_regulation_id", QMetaType.QString),
                QgsField("type_additional_information_id", QMetaType.QString),
                QgsField("id", QMetaType.QString),
                QgsField("created_at", QMetaType.QDate),
                QgsField("modified_at", QMetaType.QDate),
                QgsField("value_data_type", QMetaType.QString),
                QgsField("numeric_value", QMetaType.Double),
                QgsField("numeric_range_min", QMetaType.Double),
                QgsField("numeric_range_max", QMetaType.Double),
                QgsField("unit", QMetaType.QString),
                QgsField("text_value", QMetaType.QString),
                QgsField("text_syntax", QMetaType.QString),
                QgsField("code_list", QMetaType.QString),
                QgsField("code_value", QMetaType.QString),
                QgsField("code_title", QMetaType.QString),
                QgsField("height_reference_point", QMetaType.QString),
            ]
        )
        layer.commitChanges()

        return layer


class LifeCycleLayer(AbstractPlanLayer):
    name = "Elinkaaren päiväykset"
    filter_template = None
    qlr_path = os.path.join(QLR_PATH, "lifecycle.qlr")

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
        feature["land_use_point_id"] = model.land_use_point_id
        feature["other_point_id"] = model.other_point_id
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
            land_use_point_id=feature["land_use_point_id"],
            other_point_id=feature["other_point_id"],
            plan_regulation_id=feature["plan_regulation_id"],
            plan_proposition_id=feature["plan_proposition_id"],
            modified=False,
        )

    @classmethod
    def get_features_by_plan_id(cls, plan_id: str) -> list[QgsFeature]:
        return list(cls.get_features_by_attribute_value("plan_id", plan_id))

    @classmethod
    def create_qgis_layer(cls) -> QgsVectorLayer:
        layer = QgsVectorLayer("none", cls.name, "memory")
        provider = layer.dataProvider()
        layer.startEditing()
        provider.addAttributes(
            [
                QgsField("lifecycle_status_id", QMetaType.QString),
                QgsField("plan_id", QMetaType.QString),
                QgsField("plan_regulation_id", QMetaType.QString),
                QgsField("plan_proposition_id", QMetaType.QString),
                QgsField("starting_at", QMetaType.QDate),
                QgsField("ending_at", QMetaType.QDate),
                QgsField("id", QMetaType.QString),
                QgsField("created_at", QMetaType.QDate),
                QgsField("modified_at", QMetaType.QDate),
                QgsField("land_use_area_id", QMetaType.QString),
                QgsField("other_area_id", QMetaType.QString),
                QgsField("line_id", QMetaType.QString),
                QgsField("land_use_point_id", QMetaType.QString),
                QgsField("other_point_id", QMetaType.QString),
            ]
        )
        layer.commitChanges()

        return layer


FEATURE_LAYER_NAME_TO_CLASS_MAP: dict[str, type[PlanFeatureLayer]] = {
    LandUsePointLayer.name: LandUsePointLayer,
    OtherPointLayer.name: OtherPointLayer,
    LineLayer.name: LineLayer,
    OtherAreaLayer.name: OtherAreaLayer,
    LandUseAreaLayer.name: LandUseAreaLayer,
}

plan_layers = AbstractPlanLayer.__subclasses__()
plan_layers.remove(PlanFeatureLayer)

plan_feature_layers = PlanFeatureLayer.__subclasses__()
plan_layers.extend(plan_feature_layers)
