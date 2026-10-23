"""The GeoTIFF export draws the visible layers in the order of the layer tree."""

from __future__ import annotations

from qgis.core import QgsGroupLayer, QgsProject, QgsVectorLayer

from arho_feature_template.core.geotiff_creator import visible_layers_in_render_order


def _add_layer(project: QgsProject, name: str) -> QgsVectorLayer:
    layer = QgsVectorLayer("Point?crs=EPSG:3067", name, "memory")
    assert layer.isValid()
    project.addMapLayer(layer)
    return layer


def _add_group_layer(project: QgsProject, name: str) -> QgsGroupLayer:
    """Add a group with one layer and render the group as a group layer."""
    layer = _add_layer(project, f"{name} child")
    root = project.layerTreeRoot()
    group = root.addGroup(name)
    group.addLayer(layer)
    root.removeLayer(layer)
    group_layer = group.convertToGroupLayer(QgsGroupLayer.LayerOptions(project.transformContext()))
    assert group_layer is not None
    # The caller owns the group layer. QGIS gives it to the project, as here.
    project.addMapLayer(group_layer, addToLegend=False)
    return group_layer


def test_group_layer_is_kept_and_hidden_layer_is_left_out(new_project):
    visible = _add_layer(new_project, "visible")
    hidden = _add_layer(new_project, "hidden")
    new_project.layerTreeRoot().findLayer(hidden).setItemVisibilityChecked(False)
    group_layer = _add_group_layer(new_project, "Ajantasakaava")

    layers = visible_layers_in_render_order(new_project.layerTreeRoot())

    assert visible in layers
    assert group_layer in layers
    assert hidden not in layers


def test_hidden_group_layer_is_left_out(new_project):
    group_layer = _add_group_layer(new_project, "Ajantasakaava")
    new_project.layerTreeRoot().findGroup("Ajantasakaava").setItemVisibilityChecked(False)

    assert group_layer not in visible_layers_in_render_order(new_project.layerTreeRoot())
