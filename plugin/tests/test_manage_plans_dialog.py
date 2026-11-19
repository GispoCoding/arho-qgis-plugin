"""The Kaavasuunnitelmat dialog marks a final plan in the column that shows the lock.

Final wins over locked in the column; the tooltip still names both states.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from qgis.core import QgsProject, QgsVectorLayer

import arho_feature_template.gui.dialogs.manage_plans as manage_plans_module
from arho_feature_template.core.models import Plan
from arho_feature_template.gui.dialogs.manage_plans import ManagePlans
from arho_feature_template.project.layers.plan_layers import PlanLayer
from arho_feature_template.utils.project_utils import PLAN_LAYER_GROUP_NAME
from arho_feature_template.utils.widget_utils import deleted_after_use

if TYPE_CHECKING:
    from contextlib import AbstractContextManager

    from qgis.gui import QgisInterface

pytestmark = pytest.mark.fake_iface

PLAN_URI = "MultiPolygon?crs=EPSG:3067&field=id:string&field=name:map&field=plan_matter_id:string"


@pytest.fixture
def plan_layer(new_project: QgsProject) -> QgsVectorLayer:
    group = new_project.layerTreeRoot().addGroup(PLAN_LAYER_GROUP_NAME)
    layer = QgsVectorLayer(PLAN_URI, PlanLayer.name, "memory")
    assert layer.isValid()
    new_project.addMapLayer(layer, addToLegend=False)
    group.addLayer(layer)
    return layer


@pytest.fixture
def open_dialog(iface: QgisInterface, plan_layer: QgsVectorLayer, monkeypatch: pytest.MonkeyPatch):  # noqa: ARG001
    """Opens the dialog for the given plans of the active plan matter, and deletes it after use."""
    monkeypatch.setattr(manage_plans_module, "get_active_plan_id", lambda: None)
    monkeypatch.setattr(manage_plans_module.LifeCycleStatusLayer, "get_attribute_by_id", lambda *_args: None)

    def _open(plans: list[Plan]) -> AbstractContextManager[ManagePlans]:
        monkeypatch.setattr(manage_plans_module.PlanLayer, "get_plans_for_active_plan_matter", lambda: plans)
        return deleted_after_use(ManagePlans([], plan_manager_ref=object(), parent=iface.mainWindow()))  # type: ignore[arg-type]

    return _open


def test_a_final_plan_shows_the_final_mark(open_dialog):
    with open_dialog([Plan(id_="plan-1", name="Kaava", final=True)]) as dialog:
        item = dialog.plans_table.item(0, 0)

        assert item.text() == "Lopullinen"
        assert not item.icon().isNull()
        assert item.toolTip() == "Lopullinen"


def test_a_final_and_locked_plan_names_both_states_in_the_tooltip(open_dialog):
    with open_dialog([Plan(id_="plan-1", name="Kaava", final=True, locked=True)]) as dialog:
        item = dialog.plans_table.item(0, 0)

        assert item.text() == "Lopullinen"
        assert item.toolTip() == "Lopullinen, lukittu"


def test_a_locked_plan_that_is_not_final_still_shows_the_lock(open_dialog):
    with open_dialog([Plan(id_="plan-1", name="Kaava", locked=True)]) as dialog:
        item = dialog.plans_table.item(0, 0)

        assert item.text() == "Lukittu"
        assert item.toolTip() == "Lukittu"


def test_a_plain_plan_shows_no_mark(open_dialog):
    with open_dialog([Plan(id_="plan-1", name="Kaava")]) as dialog:
        item = dialog.plans_table.item(0, 0)

        assert item.text() == ""
        assert item.toolTip() == ""
