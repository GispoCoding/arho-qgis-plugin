"""Saving a plan matter while a locked plan is open.

A read-only layer stops every layer of its transaction group from entering edit mode, also the
plan matter layer. So the plan layers must be writable while the plan matter is saved, and
locked again afterwards, because the plan stays open.
"""

from __future__ import annotations

import pytest
from qgis.core import QgsVectorLayer

import arho_feature_template.core.plan_manager as plan_manager_module
import arho_feature_template.utils.layer_utils as layer_utils_module
from arho_feature_template.core.plan_manager import PlanManager
from arho_feature_template.project.layers.plan_layers import PlanLayer, PlanMatterLayer

pytestmark = pytest.mark.fake_iface


class FakeForm:
    model = object()

    def __init__(self, *_args, **_kwargs):
        pass

    def exec(self) -> bool:
        return True

    def deleteLater(self) -> None:
        pass


@pytest.fixture
def plan_layer() -> QgsVectorLayer:
    layer = QgsVectorLayer("None?field=id:string", PlanLayer.name, "memory")
    layer.setReadOnly(True)
    return layer


@pytest.fixture
def read_only_during_save(plugin, plan_layer: QgsVectorLayer, monkeypatch: pytest.MonkeyPatch) -> list[bool]:
    manager = plugin.plan_manager
    manager.plan_locked = True
    matter_layer = QgsVectorLayer("None?field=id:string", PlanMatterLayer.name, "memory")
    monkeypatch.setattr(PlanMatterLayer, "get_from_project", lambda: matter_layer)
    monkeypatch.setattr(PlanLayer, "get_from_project", lambda: plan_layer)
    monkeypatch.setattr(layer_utils_module, "plan_layers", [PlanLayer])
    monkeypatch.setattr(plan_manager_module, "handle_unsaved_changes", lambda: True)
    monkeypatch.setattr(plan_manager_module, "PlanMatterAttributeForm", FakeForm)
    monkeypatch.setattr(PlanMatterLayer, "get_feature_by_id", lambda *_args, **_kwargs: object())
    monkeypatch.setattr(PlanMatterLayer, "model_from_feature", lambda _feature: object())
    monkeypatch.setattr(plan_manager_module, "get_active_plan_matter_id", lambda: "matter-1")
    monkeypatch.setattr(PlanManager, "set_active_plan_matter", lambda *_args, **_kwargs: None)

    states: list[bool] = []

    def save(_model) -> str:
        states.append(plan_layer.readOnly())
        return "matter-1"

    monkeypatch.setattr(plan_manager_module, "save_plan_matter", save)
    return states


@pytest.mark.parametrize("flow", ["new_plan_matter", "edit_plan_matter"])
def test_the_plan_layers_are_writable_while_the_plan_matter_is_saved(
    plugin, plan_layer: QgsVectorLayer, read_only_during_save: list[bool], flow: str
):
    getattr(plugin.plan_manager, flow)()

    assert read_only_during_save == [False]
    assert plan_layer.readOnly()
    assert plugin.plan_manager.plan_locked
