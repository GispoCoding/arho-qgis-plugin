"""Activating a plan reads its row once: model, name, lifecycle status and extent come from it.

Uses the fake interface. The plan layer is an in-memory layer in the plan layer group; the
other plan layers, the regulation group library and the features dock are stood in for.
"""

from __future__ import annotations

import logging

import pytest
from qgis.core import QgsFeature, QgsGeometry, QgsProject, QgsVectorLayer

import arho_feature_template.core.plan_manager as plan_manager_module
from arho_feature_template.core.lifecycles import LifeCycleStatusValue
from arho_feature_template.core.plan_manager import PlanManager
from arho_feature_template.project.layers import plan_layers as plan_layers_module
from arho_feature_template.project.layers.code_layers import LifeCycleStatusLayer
from arho_feature_template.project.layers.plan_layers import PlanLayer
from arho_feature_template.utils.misc_utils import get_active_plan_id, get_active_plan_name, set_active_plan_id
from arho_feature_template.utils.project_utils import PLAN_LAYER_GROUP_NAME

pytestmark = pytest.mark.fake_iface

PLAN_URI = (
    "MultiPolygon?crs=EPSG:3067&field=id:string&field=name:map&field=description:map&field=scale:integer"
    "&field=lifecycle_status_id:string&field=plan_matter_id:string&field=approval_date:date"
    "&field=period_of_validity_start:date&field=period_of_validity_end:date&field=locked:boolean"
    "&field=final:boolean"
)
OUTLINE = QgsGeometry.fromWkt("MULTIPOLYGON (((100 100, 200 100, 200 200, 100 200, 100 100)))")


@pytest.fixture
def plan_layer(new_project: QgsProject) -> QgsVectorLayer:
    group = new_project.layerTreeRoot().addGroup(PLAN_LAYER_GROUP_NAME)
    layer = QgsVectorLayer(PLAN_URI, PlanLayer.name, "memory")
    assert layer.isValid()
    feature = QgsFeature(layer.fields())
    feature.setGeometry(OUTLINE)
    feature.setAttribute("id", "plan-1")
    feature.setAttribute("name", {"fin": "Kaava"})
    feature.setAttribute("lifecycle_status_id", "status-1")
    feature.setAttribute("locked", False)
    feature.setAttribute("final", False)
    assert layer.dataProvider().addFeature(feature)
    new_project.addMapLayer(layer, addToLegend=False)
    group.addLayer(layer)
    return layer


@pytest.fixture
def manager(plugin, plan_layer: QgsVectorLayer, monkeypatch: pytest.MonkeyPatch) -> PlanManager:  # noqa: ARG001
    """The plugin's manager with only the plan layer in the project."""
    monkeypatch.setattr(plan_manager_module, "plan_layers", [PlanLayer])
    monkeypatch.setattr(plan_manager_module, "plan_feature_layers", [])
    for layer_class in (
        plan_layers_module.RegulationGroupAssociationLayer,
        plan_layers_module.LegalEffectAssociationLayer,
        plan_layers_module.DocumentLayer,
    ):
        monkeypatch.setattr(layer_class, "get_features_by_attribute_value", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(LifeCycleStatusLayer, "get_lifecycle_status_by_id", lambda _id: None)
    monkeypatch.setattr(PlanManager, "update_active_plan_regulation_group_library", lambda _self, *_args: None)
    # Walks every plan layer through `layer_utils`; not part of this seam
    monkeypatch.setattr(PlanManager, "update_plan_status", lambda _self, _model: None)
    return plugin.plan_manager


@pytest.fixture
def view_calls(manager: PlanManager, monkeypatch: pytest.MonkeyPatch) -> list[tuple]:
    calls: list[tuple] = []
    monkeypatch.setattr(manager.features_dock, "create_plan_feature_view", lambda *args: calls.append(args))
    return calls


@pytest.fixture
def _no_other_plan_reads(monkeypatch: pytest.MonkeyPatch) -> None:
    """Only `get_feature_by_id` may touch the plan layer."""
    for name in ("get_features", "get_attribute_value_by_another_attribute_value"):
        monkeypatch.setattr(PlanLayer, name, lambda *_args, **_kwargs: pytest.fail("plan layer read"))


@pytest.mark.usefixtures("_no_other_plan_reads")
def test_the_plan_values_come_from_the_one_read(manager: PlanManager, view_calls, iface):
    manager.set_active_plan("plan-1")

    assert get_active_plan_id() == "plan-1"
    assert get_active_plan_name() == "Kaava"
    (call,) = view_calls
    assert call[2] == "status-1"
    assert iface.mapCanvas().extent().contains(OUTLINE.boundingBox())


def test_a_missing_plan_unsets_the_plan(manager: PlanManager, view_calls, caplog):
    unset: list[bool] = []
    manager.plan_unset.connect(lambda: unset.append(True))

    with caplog.at_level(logging.WARNING, logger=plan_manager_module.logger.name):
        manager.set_active_plan("plan-gone")

    assert "plan-gone" in caplog.text
    assert get_active_plan_id() == ""
    assert get_active_plan_name() == ""
    assert unset == [True]
    (call,) = view_calls
    assert call[2] is None


def test_the_lifecycle_button_uses_the_given_status(plugin, monkeypatch):
    dock = plugin.plan_manager.features_dock
    set_active_plan_id("plan-1")
    monkeypatch.setattr(PlanLayer, "get_attribute_by_id", lambda *_args: pytest.fail("PlanLayer read"))
    monkeypatch.setattr(LifeCycleStatusLayer, "get_lifecycle_status_by_id", lambda _id: LifeCycleStatusValue(_id))

    dock._update_edit_lifecycle_visibility(LifeCycleStatusValue.VALID)
    assert not dock.push_button_edit_lifecycle.isHidden()

    dock._update_edit_lifecycle_visibility(LifeCycleStatusValue.PREPARATION)
    assert dock.push_button_edit_lifecycle.isHidden()
