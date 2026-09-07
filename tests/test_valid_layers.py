"""The "Ajantasakaava" layers are filtered by the plan type of the active plan matter."""

from __future__ import annotations

import pytest
from qgis.core import QgsProject, QgsVectorLayer

from arho_feature_template.project.layers.valid_layers import (
    ValidAdditionalInformationLayer,
    ValidPlanMatterLayer,
    ValidPlanThemeAssociationLayer,
    valid_layers,
)
from arho_feature_template.utils.project_utils import VALID_LAYER_GROUP_NAME


def test_every_valid_layer_is_registered_once():
    names = [layer.name for layer in valid_layers]
    assert len(names) == len(set(names))
    assert ValidPlanMatterLayer in valid_layers


def test_every_filter_template_is_substituted_fully():
    for layer in valid_layers:
        assert layer.group == VALID_LAYER_GROUP_NAME
        assert "$" not in layer.filter_template.substitute(plan_type="3")


def test_plan_matter_is_filtered_by_the_plan_type_column():
    assert ValidPlanMatterLayer.filter_template.substitute(plan_type="3") == "plan_type = '3'"


def test_a_nested_layer_reaches_the_plan_type_through_its_foreign_keys():
    assert ValidAdditionalInformationLayer.filter_template.substitute(plan_type="2") == (
        "plan_regulation_id IN ("
        "SELECT id FROM hame.plan_regulation_valid WHERE plan_regulation_group_id IN ("
        "SELECT id FROM hame.plan_regulation_group_valid WHERE plan_id IN ("
        "SELECT id FROM hame.plan_valid WHERE plan_matter_id IN ("
        "SELECT id FROM hame.plan_matter_valid WHERE plan_type = '2'"
        "))))"
    )


def test_theme_associations_cover_regulations_and_propositions():
    expression = ValidPlanThemeAssociationLayer.filter_template.substitute(plan_type="1")
    assert expression.count("hame.plan_matter_valid WHERE plan_type = '1'") == 2
    assert "hame.plan_regulation_valid" in expression
    assert "hame.plan_proposition_valid" in expression


@pytest.fixture
def plan_matter_layer(new_project: QgsProject) -> QgsVectorLayer:
    """A memory layer named like the Kaava-asiat view, inside the Ajantasakaava group."""
    layer = QgsVectorLayer("None?field=id:string&field=plan_type:string", ValidPlanMatterLayer.name, "memory")
    assert layer.isValid()
    new_project.addMapLayer(layer, addToLegend=False)
    new_project.layerTreeRoot().addGroup(VALID_LAYER_GROUP_NAME).addLayer(layer)
    return layer


def test_a_known_plan_type_filters_the_layer(plan_matter_layer: QgsVectorLayer):
    ValidPlanMatterLayer.filter_layer_by_plan_type("3")

    assert plan_matter_layer.subsetString() == "plan_type = '3'"


def test_an_unknown_plan_type_hides_all_features(plan_matter_layer: QgsVectorLayer):
    ValidPlanMatterLayer.filter_layer_by_plan_type(None)

    assert plan_matter_layer.subsetString() == "false"
