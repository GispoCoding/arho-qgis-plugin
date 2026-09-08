"""The plan matter layer maps the repealing flag between the feature and the model."""

from __future__ import annotations

import pytest
from qgis.core import QgsFeature, QgsProject, QgsVectorLayer

from arho_feature_template.core.models import PlanMatter
from arho_feature_template.project.layers.plan_layers import PlanMatterLayer
from arho_feature_template.utils.project_utils import PLAN_LAYER_GROUP_NAME

PLAN_MATTER_URI = (
    "None?field=id:string&field=name:map&field=description:map&field=permanent_plan_identifier:string"
    "&field=record_number:string&field=producers_plan_identifier:string&field=case_identifier:string"
    "&field=plan_type_id:string&field=digital_origin_id:string&field=organisation_id:string"
    "&field=repealing:boolean"
)


@pytest.fixture
def plan_matter_layer(new_project: QgsProject) -> QgsVectorLayer:
    root = new_project.layerTreeRoot()
    group = root.addGroup(PLAN_LAYER_GROUP_NAME)
    layer = QgsVectorLayer(PLAN_MATTER_URI, PlanMatterLayer.name, "memory")
    assert layer.isValid()
    new_project.addMapLayer(layer, addToLegend=False)
    group.addLayer(layer)
    return layer


def test_a_repealing_plan_matter_is_read_as_repealing(plan_matter_layer: QgsVectorLayer):
    feature = QgsFeature(plan_matter_layer.fields())
    feature.setAttribute("id", "matter-1")
    feature.setAttribute("name", {"fin": "Kumoava"})
    feature.setAttribute("repealing", True)

    model = PlanMatterLayer.model_from_feature(feature)

    assert model.repealing is True


def test_a_repealing_plan_matter_is_written_with_the_flag_set(plan_matter_layer: QgsVectorLayer):  # noqa: ARG001
    model = PlanMatter(name={"fin": "Kumoava"}, repealing=True)

    feature = PlanMatterLayer.feature_from_model(model)

    assert feature["repealing"] is True


def test_a_new_plan_matter_is_not_repealing_by_default(plan_matter_layer: QgsVectorLayer):  # noqa: ARG001
    feature = PlanMatterLayer.feature_from_model(PlanMatter(name={"fin": "Tavallinen"}))

    assert feature["repealing"] is False
