"""`AbstractLayer.create_feature` fills defaults like `QgsVectorLayerUtils.createFeature` but never
queries the database: no layer clone, no unique-value scan."""

from __future__ import annotations

import uuid

import pytest
from qgis.core import QgsDefaultValue, QgsProject, QgsVariantUtils, QgsVectorLayer

from arho_feature_template.core.models import PlanMatter
from arho_feature_template.project.layers.plan_layers import PlanMatterLayer
from arho_feature_template.utils.project_utils import PLAN_LAYER_GROUP_NAME
from tests.test_plan_matter_layer import PLAN_MATTER_URI


@pytest.fixture
def layer(new_project: QgsProject) -> QgsVectorLayer:
    group = new_project.layerTreeRoot().addGroup(PLAN_LAYER_GROUP_NAME)
    layer = QgsVectorLayer(PLAN_MATTER_URI, PlanMatterLayer.name, "memory")
    assert layer.isValid()
    new_project.addMapLayer(layer, addToLegend=False)
    group.addLayer(layer)
    return layer


def test_id_is_a_uuid_when_the_layer_has_no_default(layer: QgsVectorLayer):  # noqa: ARG001
    feature = PlanMatterLayer.create_feature()

    assert uuid.UUID(feature["id"]).version == 4
    assert QgsVariantUtils.isNull(feature["name"])
    assert QgsVariantUtils.isNull(feature["record_number"])


def test_layer_default_expressions_are_applied(layer: QgsVectorLayer):
    layer.setDefaultValueDefinition(0, QgsDefaultValue("uuid('WithoutBraces')"))
    layer.setDefaultValueDefinition(layer.fields().indexOf("record_number"), QgsDefaultValue("'x'"))

    feature = PlanMatterLayer.create_feature()

    assert uuid.UUID(feature["id"]).version == 4
    assert feature["record_number"] == "x"
    assert QgsVariantUtils.isNull(feature["name"])


def test_feature_from_model_uses_the_helper(layer: QgsVectorLayer, monkeypatch: pytest.MonkeyPatch):  # noqa: ARG001
    calls: list[str] = []
    original = PlanMatterLayer.create_feature

    def spy():
        calls.append(PlanMatterLayer.name)
        return original()

    monkeypatch.setattr(PlanMatterLayer, "create_feature", spy)

    feature = PlanMatterLayer.feature_from_model(PlanMatter(name={"fin": "Asia"}))

    assert calls == [PlanMatterLayer.name]
    assert uuid.UUID(feature["id"]).version == 4
