"""Read-only "Ajantasakaava" views that hold the currently valid plan data.

The layers repeat the names of the editable plan layers, so they are resolved from
their own layer tree group. They are filtered by the plan type (kaavalaji) of the
active plan matter, so that only plans of the same kind as the edited one are shown.

Only `hame.plan_matter_valid` has a `plan_type` column, and it holds the level 1
kaavalaji code value. The other views are reached from it through their foreign keys.

The views expose the same columns as the editable layers, so the plan objects of the
valid views are read into the same models with the shared readers of `model_readers`.
"""

from __future__ import annotations

from string import Template
from typing import ClassVar

from arho_feature_template.project.layers.model_readers import (
    AdditionalInformationReader,
    FamilyLayer,
    LayerFamily,
    PlanObjectReader,
    PropositionReader,
    RegulationGroupReader,
    RegulationReader,
)
from arho_feature_template.project.layers.plan_layers import (
    LandUseAreaLayer,
    LineLayer,
    OtherAreaLayer,
    PlanObjectLayer,
    PointLayer,
)
from arho_feature_template.utils.project_utils import VALID_LAYER_GROUP_NAME

# Sub selects that name the rows of one level 1 plan type, each built on the previous one.
# The only value ever substituted into them is a code value read from the code table, so
# the S608 warnings about a query built from strings do not apply here.
MATTER_IDS = "SELECT id FROM hame.plan_matter_valid WHERE plan_type = '$plan_type'"
PLAN_IDS = f"SELECT id FROM hame.plan_valid WHERE plan_matter_id IN ({MATTER_IDS})"  # noqa: S608
GROUP_IDS = f"SELECT id FROM hame.plan_regulation_group_valid WHERE plan_id IN ({PLAN_IDS})"  # noqa: S608
REGULATION_IDS = f"SELECT id FROM hame.plan_regulation_valid WHERE plan_regulation_group_id IN ({GROUP_IDS})"  # noqa: S608
PROPOSITION_IDS = f"SELECT id FROM hame.plan_proposition_valid WHERE plan_regulation_group_id IN ({GROUP_IDS})"  # noqa: S608


class AbstractValidLayer(FamilyLayer):
    group = VALID_LAYER_GROUP_NAME
    filter_template: ClassVar[Template]

    @classmethod
    def filter_layer_by_plan_type(cls, plan_type: str | None) -> None:
        """Show only the valid plan data of the given level 1 kaavalaji code value.

        Hides all features when the plan type is not known.
        """
        if plan_type is None:
            cls.hide_all_features()
            return

        cls.apply_filter(cls.filter_template.substitute(plan_type=plan_type))


class ValidPlanMatterLayer(AbstractValidLayer):
    name = "Kaava-asiat"
    filter_template = Template("plan_type = '$plan_type'")


class ValidPlanLayer(AbstractValidLayer):
    name = "Kaavat"
    filter_template = Template(f"plan_matter_id IN ({MATTER_IDS})")


class ValidPlanObjectLayer(PlanObjectReader, AbstractValidLayer):
    """A valid plan object view.

    Its models carry the layer name of the editable counterpart, so the plan object form
    and the regulation group type lookup work with them as with any plan object.
    """

    plan_layer: ClassVar[type[PlanObjectLayer]]

    @classmethod
    def plan_object_layer_name(cls) -> str:
        return cls.plan_layer.name


class ValidPointLayer(ValidPlanObjectLayer):
    name = "Pisteet"
    plan_layer = PointLayer
    association_attribute = PointLayer.association_attribute
    filter_template = Template(f"plan_id IN ({PLAN_IDS})")


class ValidLineLayer(ValidPlanObjectLayer):
    name = "Viivat"
    plan_layer = LineLayer
    association_attribute = LineLayer.association_attribute
    filter_template = Template(f"plan_id IN ({PLAN_IDS})")


class ValidLandUseAreaLayer(ValidPlanObjectLayer):
    name = "Aluevaraukset"
    plan_layer = LandUseAreaLayer
    association_attribute = LandUseAreaLayer.association_attribute
    filter_template = Template(f"plan_id IN ({PLAN_IDS})")


class ValidOtherAreaLayer(ValidPlanObjectLayer):
    name = "Osa-alueet"
    plan_layer = OtherAreaLayer
    association_attribute = OtherAreaLayer.association_attribute
    filter_template = Template(f"plan_id IN ({PLAN_IDS})")


class ValidRegulationGroupLayer(RegulationGroupReader, AbstractValidLayer):
    name = "Kaavamääräysryhmät"
    filter_template = Template(f"plan_id IN ({PLAN_IDS})")


class ValidPlanRegulationLayer(RegulationReader, AbstractValidLayer):
    name = "Kaavamääräys"
    filter_template = Template(f"plan_regulation_group_id IN ({GROUP_IDS})")


class ValidPlanPropositionLayer(PropositionReader, AbstractValidLayer):
    name = "Kaavasuositus"
    filter_template = Template(f"plan_regulation_group_id IN ({GROUP_IDS})")


class ValidAdditionalInformationLayer(AdditionalInformationReader, AbstractValidLayer):
    name = "Kaavamääräyksen lisätiedot"
    filter_template = Template(f"plan_regulation_id IN ({REGULATION_IDS})")


class ValidDocumentLayer(AbstractValidLayer):
    name = "Asiakirjat"
    filter_template = Template(f"plan_id IN ({PLAN_IDS})")


class ValidRegulationGroupAssociationLayer(AbstractValidLayer):
    name = "Kaavamääräysryhmien assosiaatiot"
    filter_template = Template(f"plan_regulation_group_id IN ({GROUP_IDS})")


class ValidTypeOfVerbalRegulationAssociationLayer(AbstractValidLayer):
    name = "Sanallisten kaavamääräyksien lajien assosiaatiot"
    filter_template = Template(f"plan_regulation_id IN ({REGULATION_IDS})")


class ValidPlanThemeAssociationLayer(AbstractValidLayer):
    name = "Kaavoitusteemojen assosiaatiot"
    # A theme association points either to a regulation or to a proposition.
    filter_template = Template(
        f"plan_regulation_id IN ({REGULATION_IDS}) OR plan_proposition_id IN ({PROPOSITION_IDS})"
    )


class ValidLegalEffectAssociationLayer(AbstractValidLayer):
    name = "Yleiskaavan oikeusvaikutusten assosiaatiot"
    filter_template = Template(f"plan_id IN ({PLAN_IDS})")


AbstractValidLayer.family = LayerFamily(
    regulation_group_association=ValidRegulationGroupAssociationLayer,
    regulation_group=ValidRegulationGroupLayer,
    plan_regulation=ValidPlanRegulationLayer,
    plan_proposition=ValidPlanPropositionLayer,
    additional_information=ValidAdditionalInformationLayer,
    plan_theme_association=ValidPlanThemeAssociationLayer,
    type_of_verbal_regulation_association=ValidTypeOfVerbalRegulationAssociationLayer,
)

# `__subclasses__()` lists direct subclasses only, and the object layers sit one level deeper.
valid_plan_object_layers = ValidPlanObjectLayer.__subclasses__()
valid_layers = [cls for cls in AbstractValidLayer.__subclasses__() if cls is not ValidPlanObjectLayer]
valid_layers.extend(valid_plan_object_layers)
