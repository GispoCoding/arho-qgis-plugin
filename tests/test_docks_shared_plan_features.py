"""Both docks list the plan features; a caller that has read them once can hand them to each dock.

Uses the fake interface. The layer classes are stand-ins that fail on any read, so a dock
that got the features must not touch the layers.
"""

from __future__ import annotations

import pytest
from qgis.core import QgsFeature, QgsField, QgsFields, QgsGeometry, QgsPointXY
from qgis.PyQt.QtCore import QMetaType

import arho_feature_template.gui.docks.plan_features_dock as plan_features_dock_module
import arho_feature_template.gui.docks.regulation_groups_dock as regulation_groups_dock_module
from arho_feature_template.core.models import PlanObject, RegulationGroup, RegulationGroupLibrary
from arho_feature_template.gui.docks.plan_features_dock import DATA_COLUMN as FEATURE_DATA_COLUMN
from arho_feature_template.gui.docks.plan_features_dock import DATA_ROLE as FEATURE_DATA_ROLE
from arho_feature_template.gui.docks.regulation_groups_dock import DATA_COLUMN as GROUP_DATA_COLUMN
from arho_feature_template.gui.docks.regulation_groups_dock import DATA_ROLE as GROUP_DATA_ROLE
from arho_feature_template.gui.docks.regulation_groups_dock import RegulationGroupsDock
from arho_feature_template.project.layers.plan_layers import RegulationGroupAssociationLayer

pytestmark = pytest.mark.fake_iface

LAYER_NAME = "Aluevaraus"


class NoReadLayerClass:
    """Stands in for a `plan_feature_layers` entry that must not be read."""

    name = LAYER_NAME

    def __init__(self):
        self.reader_calls: list[tuple[list[QgsFeature], list[RegulationGroup] | None]] = []

    def get_from_project(self):
        pytest.fail("layer read")

    def get_features(self):
        pytest.fail("layer read")

    def models_from_features(self, features, regulation_groups=None):
        self.reader_calls.append((features, regulation_groups))
        return [
            PlanObject(layer_name=LAYER_NAME, name={"fin": feature["id"]}, id_=feature["id"]) for feature in features
        ]


def _plan_feature(fid: int, id_: str) -> QgsFeature:
    fields = QgsFields()
    fields.append(QgsField("id", QMetaType.Type.QString))
    feature = QgsFeature(fields, fid)
    feature.setAttribute("id", id_)
    feature.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(fid, fid)))
    return feature


def test_regulation_groups_dock_uses_the_given_plan_features(monkeypatch):
    dock = RegulationGroupsDock()
    monkeypatch.setattr(regulation_groups_dock_module, "plan_feature_layers", [NoReadLayerClass()])
    monkeypatch.setattr(RegulationGroupAssociationLayer, "get_features", list)
    monkeypatch.setattr(
        RegulationGroupAssociationLayer,
        "get_plan_object_ids_by_regulation_group",
        lambda associations: {"group-1": {LAYER_NAME: ["area-1"]}},  # noqa: ARG005
    )
    library = RegulationGroupLibrary(regulation_groups=[RegulationGroup(id_="group-1", heading={"fin": "Ryhmä"})])
    linked, other = _plan_feature(1, "area-1"), _plan_feature(2, "area-2")

    dock.update_regulation_groups(library, {LAYER_NAME: [linked, other]})

    assert dock.model.rowCount() == 1
    group, fids_and_geoms = dock.model.item(0, GROUP_DATA_COLUMN).data(GROUP_DATA_ROLE)
    assert group.id_ == "group-1"
    assert list(fids_and_geoms[LAYER_NAME]) == [1]
    assert fids_and_geoms[LAYER_NAME][1].asPoint() == QgsPointXY(1, 1)


def test_plan_features_dock_uses_the_given_plan_features_and_groups(plugin, monkeypatch):
    dock = plugin.plan_manager.features_dock
    layer_class = NoReadLayerClass()
    monkeypatch.setattr(plan_features_dock_module, "plan_feature_layers", [layer_class])
    groups = [RegulationGroup(id_="group-1")]
    features = [_plan_feature(1, "area-1"), _plan_feature(2, "area-2")]

    dock.create_plan_feature_view(groups, {LAYER_NAME: features})

    assert layer_class.reader_calls == [(features, groups)]
    assert dock.model.rowCount() == 2
    model, fid = dock.model.item(1, FEATURE_DATA_COLUMN).data(FEATURE_DATA_ROLE)
    assert (model.id_, fid) == ("area-2", 2)


def test_plan_features_dock_reads_a_layer_missing_from_the_given_features(plugin, monkeypatch):
    dock = plugin.plan_manager.features_dock
    layer_class = NoReadLayerClass()
    layer_class.get_features = lambda: [_plan_feature(3, "area-3")]  # type: ignore[method-assign]
    monkeypatch.setattr(plan_features_dock_module, "plan_feature_layers", [layer_class])

    dock.create_plan_feature_view(None, {"Piste": []})

    assert dock.model.rowCount() == 1
