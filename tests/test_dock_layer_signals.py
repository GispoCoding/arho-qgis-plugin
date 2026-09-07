"""Docks connect to project layers, which outlive the plugin.

Those connections have to be undone in ``unload``, or the layer keeps calling into a
deleted dock. Qt cannot do it for us while the dock is only scheduled for deletion.
"""

from __future__ import annotations

import pytest
from qgis.core import QgsVectorLayer

from arho_feature_template.gui.docks.regulation_groups_dock import RegulationGroupsDock

pytestmark = pytest.mark.fake_iface


class FakeLayerClass:
    """Stands in for a `plan_feature_layers` entry."""

    def __init__(self, layer: QgsVectorLayer):
        self.name = layer.name()
        self._layer = layer

    def get_from_project(self) -> QgsVectorLayer:
        return self._layer


@pytest.fixture
def plan_object_layer() -> QgsVectorLayer:
    return QgsVectorLayer("Point?crs=EPSG:3067&field=id:integer", "Aluevaraus", "memory")


def test_regulation_groups_dock_disconnects_layers_on_unload(monkeypatch, plan_object_layer):
    dock = RegulationGroupsDock()
    monkeypatch.setattr(
        "arho_feature_template.gui.docks.regulation_groups_dock.plan_feature_layers",
        [FakeLayerClass(plan_object_layer)],
    )

    dock.initialize()
    assert dock._connected_layers == [plan_object_layer]

    dock.unload()

    assert dock._connected_layers == []
    with pytest.raises(TypeError):
        plan_object_layer.committedFeaturesRemoved.disconnect(dock._on_feats_removed)


def test_regulation_groups_dock_does_not_stack_layer_connections(monkeypatch, plan_object_layer):
    """`initialize` runs on every project read."""
    dock = RegulationGroupsDock()
    monkeypatch.setattr(
        "arho_feature_template.gui.docks.regulation_groups_dock.plan_feature_layers",
        [FakeLayerClass(plan_object_layer)],
    )

    dock.initialize()
    dock.initialize()

    assert dock._connected_layers == [plan_object_layer]
    # A single connection: disconnecting once must leave none behind
    plan_object_layer.committedFeaturesRemoved.disconnect(dock._on_feats_removed)
    with pytest.raises(TypeError):
        plan_object_layer.committedFeaturesRemoved.disconnect(dock._on_feats_removed)
