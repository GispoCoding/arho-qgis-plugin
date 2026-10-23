"""The GeoTIFF export draws the visible layers in the order of the layer tree, on the pixel grid."""

from __future__ import annotations

from osgeo import gdal
from qgis.core import QgsFeature, QgsGeometry, QgsGroupLayer, QgsProject, QgsRectangle, QgsVectorLayer

from arho_feature_template.core.geotiff_creator import GeoTiffCreator, visible_layers_in_render_order
from arho_feature_template.core.plan_scale import dpi_for


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


def test_geotiff_has_the_pixel_size_and_covers_the_plan(new_project, tmp_path, qtbot):
    plan_feature = QgsFeature()
    plan_feature.setGeometry(QgsGeometry.fromRect(QgsRectangle(385000, 6672000, 385100, 6672050)))
    creator = GeoTiffCreator.__new__(GeoTiffCreator)
    creator.plan_layer = _add_layer(new_project, "plan")
    creator.feature = plan_feature
    geotiff_path = tmp_path / "plan.tif"

    creator.create_geotiff(str(geotiff_path), 0.25, dpi_for(1000, 0.25))
    qtbot.waitUntil(geotiff_path.exists, timeout=10000)

    dataset = gdal.Open(str(geotiff_path))
    x_min, pixel_width, _, y_max, _, pixel_height = dataset.GetGeoTransform()
    assert (pixel_width, pixel_height) == (0.25, -0.25)
    assert dataset.RasterCount == 3
    assert x_min <= 385000 - 10
    assert y_max >= 6672050 + 10
    assert x_min + dataset.RasterXSize * pixel_width >= 385100 + 10
