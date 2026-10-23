"""With buffered transaction groups, no plugin path leaves the edit buffer group stuck.

In `Qgis.TransactionMode.BufferedGroups` a commit with nothing to commit marks the group as
editing even when no layer is in edit mode. `QgsProject.startEditing` then returns at once
and no layer enters edit mode again. See `docs/stuck-buffered-edit-group.md`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Iterator

import pytest
from qgis.core import Qgis, QgsFeature, QgsFeatureRequest
from qgis.PyQt.QtCore import QDate

import arho_feature_template.gui.docks.plan_objects_dock as plan_objects_dock_module
from arho_feature_template.core import feature_editing
from arho_feature_template.core.lifecycles import LifeCycleStatusValue
from arho_feature_template.project.layers.code_layers import LifeCycleStatusLayer
from arho_feature_template.project.layers.plan_layers import LandUseAreaLayer
from arho_feature_template.utils.project_utils import PLAN_LAYER_GROUP_NAME
from tests.test_model_readers import _add_layer, _build_family, _fill_family

if TYPE_CHECKING:
    from qgis.core import QgsProject, QgsVectorLayer


@pytest.fixture
def buffered_project(new_project: QgsProject) -> Iterator[QgsProject]:
    new_project.setTransactionMode(Qgis.TransactionMode.BufferedGroups)
    yield new_project
    # The edit buffer group is a singleton that `clear()` leaves in editing state
    new_project.rollBack(stopEditing=True)
    feature_editing.discard_after_commit_callbacks()


@pytest.fixture
def layer(buffered_project: QgsProject) -> QgsVectorLayer:
    return _add_layer(buffered_project, PLAN_LAYER_GROUP_NAME, "pisteet", "Point?crs=EPSG:3067&field=id:string")


def _assert_editing_can_start(project: QgsProject, layer: QgsVectorLayer) -> None:
    """The group is editing only when its layers are, and starting the edit session works."""
    assert project.editBufferGroup().isEditing() == layer.isEditable()
    assert project.startEditing(layer)
    assert layer.isEditable()


def test_a_commit_with_no_layer_in_edit_mode_does_not_start_the_group(
    buffered_project: QgsProject, layer: QgsVectorLayer
):
    applied: list[bool] = []
    feature_editing._after_commit.append(lambda: applied.append(True))

    assert feature_editing.commit_edit_buffer(stop_editing=False) is True

    assert applied == [True]
    assert feature_editing._after_commit == []
    assert not layer.isEditable()
    _assert_editing_can_start(buffered_project, layer)


def test_a_commit_in_edit_mode_writes_and_keeps_editing(buffered_project: QgsProject, layer: QgsVectorLayer):
    assert feature_editing.start_editing(layer)
    feature = QgsFeature(layer.fields())
    feature.setAttribute("id", "p-1")
    assert layer.addFeature(feature)

    assert feature_editing.commit_edit_buffer(stop_editing=False) is True

    assert [f["id"] for f in layer.dataProvider().getFeatures()] == ["p-1"]
    assert layer.isEditable()
    assert buffered_project.editBufferGroup().isEditing()


@pytest.fixture
def family(buffered_project: QgsProject) -> Iterator[dict[str, QgsVectorLayer]]:
    """Area 1 with group 1, and area 2 without groups. No layer is in edit mode."""
    layers = _build_family(buffered_project, PLAN_LAYER_GROUP_NAME, LandUseAreaLayer.name)
    _fill_family(layers)
    yield layers
    feature_editing.created_object_models.clear()


@pytest.mark.fake_iface
def test_a_lifecycle_change_with_no_layer_in_edit_mode_is_saved(
    plugin, family: dict[str, QgsVectorLayer], buffered_project: QgsProject, monkeypatch
):
    monkeypatch.setattr(plan_objects_dock_module, "plan_object_layers", [LandUseAreaLayer])
    monkeypatch.setattr(LifeCycleStatusLayer, "get_id_from_lifecycle_status_value", lambda _value: "status-8")
    objects = family["objects"]
    (area,) = objects.getFeatures("\"id\" = 'area-1'")
    objects.selectByIds([area.id()])

    plugin.plan_manager.plan_objects_dock._on_lifecycle_change_requested(
        LifeCycleStatusValue.UNDER_APPEAL, QDate(2026, 10, 1)
    )

    (saved,) = objects.dataProvider().getFeatures(QgsFeatureRequest().setFilterFid(area.id()))
    assert saved["lifecycle_status_id"] == "status-8"
    assert saved["period_of_validity_start"] == QDate(2026, 10, 1)
    _assert_editing_can_start(buffered_project, objects)
