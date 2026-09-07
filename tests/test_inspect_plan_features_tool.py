"""The inspect tool reports the clicked feature with its layer class, not its layer name."""

from __future__ import annotations

from typing import TYPE_CHECKING, Iterator

import pytest
from qgis.core import QgsFeature, QgsProject, QgsVectorLayer
from qgis.gui import QgsMapToolIdentify

from arho_feature_template.gui.tools.inspect_plan_features_tool import InspectPlanFeatures
from arho_feature_template.project.layers.plan_layers import PointLayer
from arho_feature_template.project.layers.valid_layers import ValidLineLayer, ValidPointLayer
from arho_feature_template.utils.project_utils import PLAN_LAYER_GROUP_NAME, VALID_LAYER_GROUP_NAME

if TYPE_CHECKING:
    from qgis.gui import QgsMapCanvas


def _add_point_layer(project: QgsProject, group_name: str, layer_name: str) -> QgsVectorLayer:
    root = project.layerTreeRoot()
    group = root.findGroup(group_name) or root.addGroup(group_name)
    layer = QgsVectorLayer("Point?crs=EPSG:3067&field=id:string", layer_name, "memory")
    assert layer.isValid()
    project.addMapLayer(layer, addToLegend=False)
    group.addLayer(layer)
    return layer


@pytest.fixture
def point_layers(new_project: QgsProject) -> tuple[QgsVectorLayer, QgsVectorLayer]:
    """Same-named point layers in the plan group and in the valid group."""
    plan_points = _add_point_layer(new_project, PLAN_LAYER_GROUP_NAME, PointLayer.name)
    valid_points = _add_point_layer(new_project, VALID_LAYER_GROUP_NAME, ValidPointLayer.name)
    return plan_points, valid_points


@pytest.fixture
def make_tool(canvas: QgsMapCanvas) -> Iterator:
    tools: list[InspectPlanFeatures] = []

    def make(layer_classes, visible_only: bool) -> InspectPlanFeatures:
        tool = InspectPlanFeatures(canvas, layer_classes, visible_only=visible_only)
        tools.append(tool)
        return tool

    yield make
    for tool in tools:
        tool.deleteLater()


def test_layers_are_resolved_by_group_in_the_given_order(point_layers, make_tool):
    plan_points, valid_points = point_layers
    tool = make_tool([ValidPointLayer, PointLayer], visible_only=False)

    pairs = tool.resolve_layers()

    assert [(layer_class, layer.id()) for layer_class, layer in pairs] == [
        (ValidPointLayer, valid_points.id()),
        (PointLayer, plan_points.id()),
    ]


def test_a_missing_layer_is_skipped(point_layers, make_tool):
    plan_points, _ = point_layers
    tool = make_tool([PointLayer, ValidLineLayer], visible_only=False)

    pairs = tool.resolve_layers()

    assert [(layer_class, layer.id()) for layer_class, layer in pairs] == [(PointLayer, plan_points.id())]


def test_the_identified_feature_is_reported_with_its_layer_class(point_layers, make_tool):
    _, valid_points = point_layers
    tool = make_tool([PointLayer, ValidPointLayer], visible_only=False)
    received: list[tuple[QgsFeature, type]] = []
    tool.feature_identified.connect(lambda feature, layer_class: received.append((feature, layer_class)))
    feature = QgsFeature(valid_points.fields())
    feature.setAttribute("id", "point-1")

    tool.emit_result(QgsMapToolIdentify.IdentifyResult(valid_points, feature, {}), tool.resolve_layers())

    assert len(received) == 1
    reported_feature, reported_class = received[0]
    assert reported_class is ValidPointLayer
    assert reported_feature["id"] == "point-1"


def test_a_feature_of_an_unknown_layer_is_not_reported(new_project: QgsProject, point_layers, make_tool):
    _, valid_points = point_layers
    other = QgsVectorLayer("Point?crs=EPSG:3067&field=id:string", "Muu", "memory")
    new_project.addMapLayer(other, addToLegend=False)
    tool = make_tool([PointLayer, ValidPointLayer], visible_only=False)
    received = []
    tool.feature_identified.connect(lambda _feature, layer_class: received.append(layer_class))

    tool.emit_result(QgsMapToolIdentify.IdentifyResult(other, QgsFeature(), {}), tool.resolve_layers())

    assert received == []
    assert valid_points.id() != other.id()


def test_only_layers_shown_in_the_canvas_are_identified(canvas: QgsMapCanvas, point_layers, make_tool):
    plan_points, valid_points = point_layers
    canvas.setLayers([valid_points])
    tool = make_tool([PointLayer, ValidPointLayer], visible_only=True)

    pairs = tool.resolve_layers()

    assert [layer_class for layer_class, _ in pairs] == [ValidPointLayer]
    assert pairs[0][1].id() == valid_points.id() != plan_points.id()
