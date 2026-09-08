"""Feature-to-model readers shared by the editable plan layers and the valid plan views.

Both layer tree groups hold the same kinds of layers with the same columns. A reader builds
the models of one layer and reaches its sibling layers (regulation groups, regulations, ...)
through `FamilyLayer.family`, which each group binds once at the bottom of its own module,
after every member class exists.

This module must not import `plan_layers`, `valid_layers` or `code_layers`.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar

from arho_feature_template.core.models import (
    AdditionalInformation,
    AttributeValue,
    AttributeValueDataType,
    PlanObject,
    Proposition,
    Regulation,
    RegulationGroup,
)
from arho_feature_template.project.layers import AbstractLayer
from arho_feature_template.utils.localization_utils import get_localized_text

if TYPE_CHECKING:
    from qgis.core import QgsFeature


@dataclass(frozen=True)
class LayerFamily:
    """The sibling layer classes of one layer tree group."""

    regulation_group_association: type[AbstractLayer]
    regulation_group: type[RegulationGroupReader]
    plan_regulation: type[RegulationReader]
    plan_proposition: type[PropositionReader]
    additional_information: type[AdditionalInformationReader]
    plan_theme_association: type[AbstractLayer]
    type_of_verbal_regulation_association: type[AbstractLayer]


class FamilyLayer(AbstractLayer):
    """A layer whose readers find their sibling layers through `family`."""

    family: ClassVar[LayerFamily]


def attribute_value_model_from_feature(feature: QgsFeature) -> AttributeValue:
    return AttributeValue(
        value_data_type=AttributeValueDataType(feature["value_data_type"]) if feature["value_data_type"] else None,
        numeric_value=feature["numeric_value"],
        numeric_range_min=feature["numeric_range_min"],
        numeric_range_max=feature["numeric_range_max"],
        unit=feature["unit"],
        text_value=feature["text_value"],
        text_syntax=feature["text_syntax"],
        code_list=feature["code_list"],
        code_value=feature["code_value"],
        code_title=get_localized_text(feature["code_title"]),
        height_reference_point=feature["height_reference_point"],
    )


class PlanObjectReader(FamilyLayer):
    """Reads plan objects (points, lines, land use areas, other areas) with their regulation groups."""

    # Column of the regulation group association layer that points at this object layer.
    association_attribute: ClassVar[str]

    @classmethod
    def plan_object_layer_name(cls) -> str:
        """Value of `PlanObject.layer_name`: the editable plan object layer of this kind of object."""
        return cls.name

    @classmethod
    def models_from_features(
        cls, features: list[QgsFeature], regulation_groups: list[RegulationGroup] | None = None
    ) -> list[PlanObject]:
        plan_object_ids = {feat["id"] for feat in features}

        association_features = cls.family.regulation_group_association.get_features_by_attribute_value(
            cls.association_attribute, plan_object_ids
        )

        plan_object_ids_by_group_id: dict[str, list[str]] = defaultdict(list)
        for association in association_features:
            plan_object_ids_by_group_id[association["plan_regulation_group_id"]].append(
                association[cls.association_attribute]
            )

        # Read the regulation group models only if they are not given as a parameter
        if not regulation_groups:
            regulation_group_features = list(
                cls.family.regulation_group.get_features_by_attribute_value("id", set(plan_object_ids_by_group_id))
            )
            regulation_groups = cls.family.regulation_group.models_from_features(regulation_group_features)

        groups_by_plan_object_id: dict[str, list[RegulationGroup]] = defaultdict(list)
        for group in regulation_groups:
            group_id = group.id_
            if group_id:
                for plan_object_id in plan_object_ids_by_group_id.get(group_id, []):
                    groups_by_plan_object_id[plan_object_id].append(group)

        return [
            PlanObject(
                geom=feature.geometry(),
                type_of_underground_id=feature["type_of_underground_id"],
                layer_name=cls.plan_object_layer_name(),
                name=feature["name"],
                description=feature["description"],
                regulation_groups=groups_by_plan_object_id[feature["id"]],
                plan_id=feature["plan_id"],
                lifecycle_status_id=feature["lifecycle_status_id"],
                period_of_validity_start=feature["period_of_validity_start"] or None,
                period_of_validity_end=feature["period_of_validity_end"] or None,
                modified=False,
                id_=feature["id"],
            )
            for feature in features
        ]

    @classmethod
    def model_from_feature(cls, feature: QgsFeature) -> PlanObject:
        return cls.models_from_features([feature])[0]


class RegulationGroupReader(FamilyLayer):
    """Reads regulation groups with their regulations and propositions."""

    @classmethod
    def models_from_features(cls, features: list[QgsFeature]) -> list[RegulationGroup]:
        group_ids = {feature["id"] for feature in features}

        regulation_layer = cls.family.plan_regulation
        regulation_features = list(
            regulation_layer.get_features_by_attribute_value("plan_regulation_group_id", group_ids)
        )
        regulation_models = regulation_layer.models_from_features(regulation_features)
        regulations_by_group_id: dict[str, list[Regulation]] = defaultdict(list)
        for regulation in regulation_models:
            if regulation.regulation_group_id:
                regulations_by_group_id[regulation.regulation_group_id].append(regulation)

        proposition_layer = cls.family.plan_proposition
        proposition_features = list(
            proposition_layer.get_features_by_attribute_value("plan_regulation_group_id", group_ids)
        )
        proposition_models = proposition_layer.models_from_features(proposition_features)
        propositions_by_group_id: dict[str, list[Proposition]] = defaultdict(list)
        for proposition in proposition_models:
            if proposition.regulation_group_id:
                propositions_by_group_id[proposition.regulation_group_id].append(proposition)

        return [
            RegulationGroup(
                type_code_id=feature["type_of_plan_regulation_group_id"],
                heading=feature["name"],
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


class RegulationReader(FamilyLayer):
    """Reads regulations with their additional information, themes and verbal regulation types."""

    @classmethod
    def models_from_features(cls, features: list[QgsFeature]) -> list[Regulation]:
        regulation_ids = [feature["id"] for feature in features]

        info_layer = cls.family.additional_information
        info_features = list(info_layer.get_features_by_attribute_value("plan_regulation_id", regulation_ids))
        info_models = info_layer.models_from_features(info_features)
        infos_by_regulation_id: dict[str, list[AdditionalInformation]] = defaultdict(list)
        for info in info_models:
            if info.plan_regulation_id:
                infos_by_regulation_id[info.plan_regulation_id].append(info)

        plan_theme_associations = list(
            cls.family.plan_theme_association.get_features_by_attribute_value("plan_regulation_id", regulation_ids)
        )
        plan_theme_ids_by_regulation_id: dict[str, list[str]] = defaultdict(list)
        for association in plan_theme_associations:
            plan_theme_ids_by_regulation_id[association["plan_regulation_id"]].append(association["plan_theme_id"])

        verbal_regulation_type_associations = list(
            cls.family.type_of_verbal_regulation_association.get_features_by_attribute_value(
                "plan_regulation_id", regulation_ids
            )
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
                lifecycle_status_id=feature["lifecycle_status_id"],
                period_of_validity_start=feature["period_of_validity_start"] or None,
                period_of_validity_end=feature["period_of_validity_end"] or None,
                modified=False,
                id_=feature["id"],
            )
            for feature in features
        ]

    @classmethod
    def model_from_feature(cls, feature: QgsFeature) -> Regulation:
        return cls.models_from_features([feature])[0]


class PropositionReader(FamilyLayer):
    """Reads propositions with their themes."""

    @classmethod
    def models_from_features(cls, features: list[QgsFeature]) -> list[Proposition]:
        proposition_ids = {feature["id"] for feature in features}
        plan_theme_associations = list(
            cls.family.plan_theme_association.get_features_by_attribute_value("plan_proposition_id", proposition_ids)
        )

        plan_theme_ids_by_proposition_id: dict[str, list[str]] = defaultdict(list)
        for association in plan_theme_associations:
            plan_theme_ids_by_proposition_id[association["plan_proposition_id"]].append(association["plan_theme_id"])

        return [
            Proposition(
                value=feature["text_value"],
                regulation_group_id=feature["plan_regulation_group_id"],
                proposition_number=feature["ordering"],
                theme_ids=plan_theme_ids_by_proposition_id[feature["id"]],
                lifecycle_status_id=feature["lifecycle_status_id"],
                period_of_validity_start=feature["period_of_validity_start"] or None,
                period_of_validity_end=feature["period_of_validity_end"] or None,
                modified=False,
                id_=feature["id"],
            )
            for feature in features
        ]

    @classmethod
    def model_from_feature(cls, feature: QgsFeature) -> Proposition:
        return cls.models_from_features([feature])[0]


class AdditionalInformationReader(FamilyLayer):
    """Reads the additional information of regulations."""

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
