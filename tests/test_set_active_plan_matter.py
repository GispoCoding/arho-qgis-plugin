"""Activating a plan matter reads its row once and activates the given plan in the same pass.

Uses the fake interface: the manager comes from the loaded plugin, and the plan matter layer
is an in-memory layer in the plan layer group. The plan activation itself is recorded, not run.
"""

from __future__ import annotations

import logging

import pytest
from qgis.core import QgsFeature, QgsProject, QgsVectorLayer

import arho_feature_template.core.plan_manager as plan_manager_module
from arho_feature_template.core.plan_manager import PlanManager
from arho_feature_template.project.layers.plan_layers import PlanMatterLayer
from arho_feature_template.utils.misc_utils import get_active_plan_matter_id
from arho_feature_template.utils.project_utils import PLAN_LAYER_GROUP_NAME

pytestmark = pytest.mark.fake_iface

PLAN_MATTER_URI = (
    "None?field=id:string&field=name:map&field=description:map&field=permanent_plan_identifier:string"
    "&field=record_number:string&field=producers_plan_identifier:string&field=case_identifier:string"
    "&field=plan_type_id:string&field=digital_origin_id:string&field=organisation_id:string"
    "&field=repealing:boolean"
)


@pytest.fixture
def plan_matter_layer(new_project: QgsProject) -> QgsVectorLayer:
    group = new_project.layerTreeRoot().addGroup(PLAN_LAYER_GROUP_NAME)
    layer = QgsVectorLayer(PLAN_MATTER_URI, PlanMatterLayer.name, "memory")
    assert layer.isValid()
    feature = QgsFeature(layer.fields())
    feature.setAttribute("id", "matter-1")
    feature.setAttribute("name", {"fin": "Kaava-asia"})
    assert layer.dataProvider().addFeature(feature)
    new_project.addMapLayer(layer, addToLegend=False)
    group.addLayer(layer)
    return layer


@pytest.fixture
def manager(plugin, plan_matter_layer: QgsVectorLayer, monkeypatch: pytest.MonkeyPatch) -> PlanManager:  # noqa: ARG001
    """The plugin's manager with only the plan matter layer in the project."""
    monkeypatch.setattr(plan_manager_module, "plan_matter_layers", [PlanMatterLayer])
    monkeypatch.setattr(plan_manager_module, "valid_layers", [])
    return plugin.plan_manager


@pytest.fixture
def plan_activations(monkeypatch: pytest.MonkeyPatch) -> list[str | None]:
    calls: list[str | None] = []
    monkeypatch.setattr(PlanManager, "set_active_plan", lambda _self, plan_id: calls.append(plan_id))
    return calls


def test_the_given_plan_is_activated_with_its_plan_matter(manager: PlanManager, plan_activations, monkeypatch):
    reads: list[str] = []
    original = PlanMatterLayer.get_feature_by_id

    def counting(id_, no_geometries=True):
        reads.append(id_)
        return original(id_, no_geometries)

    monkeypatch.setattr(PlanMatterLayer, "get_feature_by_id", counting)

    manager.set_active_plan_matter("matter-1", "plan-1")

    assert get_active_plan_matter_id() == "matter-1"
    assert plan_activations == ["plan-1"]
    assert reads == ["matter-1"]


def test_no_plan_is_activated_by_default(manager: PlanManager, plan_activations):
    manager.set_active_plan_matter("matter-1")

    assert get_active_plan_matter_id() == "matter-1"
    assert plan_activations == [None]


def test_a_missing_plan_matter_unsets_the_plan_matter_and_the_plan(manager: PlanManager, plan_activations, caplog):
    with caplog.at_level(logging.WARNING, logger=plan_manager_module.logger.name):
        manager.set_active_plan_matter("matter-gone", "plan-1")

    assert get_active_plan_matter_id() == ""
    assert plan_activations == [None]
    assert "matter-gone" in caplog.text


def test_unsetting_the_plan_matter_unsets_the_plan(manager: PlanManager, plan_activations):
    manager.set_active_plan_matter(None)

    assert get_active_plan_matter_id() == ""
    assert plan_activations == [None]
