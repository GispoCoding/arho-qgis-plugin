from __future__ import annotations

import os
import re

from osgeo import gdal
from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsLayerTree,
    QgsMapLayer,
    QgsMapRendererSequentialJob,
    QgsMapSettings,
    QgsMapSettingsUtils,
    QgsProject,
    QgsVariantUtils,
)
from qgis.PyQt.QtCore import QDir, QSize, Qt
from qgis.PyQt.QtGui import QColor
from qgis.PyQt.QtWidgets import QApplication

from arho_feature_template.core.plan_scale import default_scale_of_active_plan_matter, image_size, plan_map_extent
from arho_feature_template.core.settings_manager import SettingsManager
from arho_feature_template.gui.dialogs.geotiff_dialog import MAX_FILE_BYTES, GeoTiffDialog
from arho_feature_template.project.layers.plan_layers import (
    PlanLayer,
)
from arho_feature_template.utils.localization_utils import get_localized_text
from arho_feature_template.utils.misc_utils import get_active_plan_id, get_active_plan_matter_name, iface
from arho_feature_template.utils.widget_utils import deleted_after_use


def visible_layers_in_render_order(root: QgsLayerTree) -> list[QgsMapLayer]:
    """Return the visible layers of the layer tree in render order.

    A group rendered as a group layer is in the render order as its QgsGroupLayer,
    which has no layer node, so its visibility is read from the group node.
    """
    group_nodes = {group.groupLayer().id(): group for group in root.findGroups(recursive=True) if group.groupLayer()}
    layers = []
    for layer in root.layerOrder():
        node = root.findLayer(layer) or group_nodes.get(layer.id())
        if node is not None and node.isVisible():
            layers.append(layer)
    return layers


def geotiff_file_name(plan_matter_name: str, plan_name: str) -> str:
    """`<plan matter name> - <plan name>.tif`, without characters Windows does not allow in a file name."""
    stem = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", f"{plan_matter_name} - {plan_name}")
    return f"{stem.rstrip('. ')}.tif"


def default_geotiff_path(plan_matter_name: str, plan_name: str) -> str:
    """The file name in the folder of the last saved GeoTIFF, or in the home folder."""
    directory = SettingsManager.get_geotiff_directory()
    if not directory or not os.path.isdir(directory):
        directory = QDir.homePath()
    return os.path.join(directory, geotiff_file_name(plan_matter_name, plan_name))


class GeoTiffCreator:
    def __init__(self):
        """Initialize the CreateGeoTiff class and fetch the required data."""
        self.plan_layer = PlanLayer.get_from_project()

        if not self.plan_layer:
            iface.messageBar().pushWarning("", "Ei aktiivista kaavasuunnitelmaa.")
            return

        self.feature = PlanLayer.get_feature_by_id(get_active_plan_id(), no_geometries=False)

        if not self.feature:
            iface.messageBar().pushWarning("", "Ei aktiivista kaavasuunnitelmaa.")
            return

    def select_output_file(self):
        """Asks the output file, scale and resolution, then creates the GeoTIFF."""
        if not self.plan_layer or not self.feature:
            return

        scale = self.feature["scale"]
        if QgsVariantUtils.isNull(scale) or not scale:
            scale = default_scale_of_active_plan_matter()

        file_path = default_geotiff_path(
            get_active_plan_matter_name() or "Nimetön", get_localized_text(self.feature["name"]) or "Nimetön"
        )

        with deleted_after_use(
            GeoTiffDialog(self.feature.geometry().boundingBox(), scale, file_path, iface.mainWindow())
        ) as dialog:
            if not dialog.exec():
                return
            SettingsManager.set_geotiff_directory(os.path.dirname(dialog.file_path()))
            self.create_geotiff(dialog.file_path(), dialog.pixel_size(), dialog.dpi())

    def create_geotiff(self, geotiff_path: str, pixel_size: float, dpi: float):
        """Creates a GeoTIFF from the active plan layer and feature.

        The dpi makes the map render at the plan scale, so symbols and labels sized in
        millimetres look as on a printed map.
        """
        if not self.plan_layer or not self.feature:
            return

        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)

        extent = plan_map_extent(self.feature.geometry().boundingBox(), pixel_size)

        # Rendering settings
        settings = QgsMapSettings()
        layer_tree = QgsProject.instance().layerTreeRoot()

        settings.setLayers(visible_layers_in_render_order(layer_tree))
        settings.setDestinationCrs(QgsCoordinateReferenceSystem("EPSG:3067"))
        settings.setBackgroundColor(QColor(255, 255, 255))
        settings.setExtent(extent)
        settings.setOutputSize(QSize(*image_size(extent, pixel_size)))
        settings.setOutputDpi(dpi)

        render = QgsMapRendererSequentialJob(settings)

        def finished():
            try:
                img = render.renderedImage()
                if img.isNull():
                    iface.messageBar().pushCritical("", "GeoTIFF-kuvaa ei voitu piirtää. Muisti ei riittänyt.")
                    return

                # Save the image as PNG temporarily
                image_path = geotiff_path.replace(".tif", ".png")
                img.save(image_path, "PNG")

                # Generate the World File (.pgw)
                pgw_content = QgsMapSettingsUtils.worldFileContent(settings)
                pgw_path = image_path.replace(".png", ".pgw")
                with open(pgw_path, "w") as f:
                    f.write(pgw_content)

                # Convert PNG to GeoTIFF
                self._create_geotiff_from_png(image_path, geotiff_path)

                # Delete temporary PNG
                if os.path.exists(image_path):
                    os.remove(image_path)

                # Delete temporary World File (.pgw)
                if os.path.exists(pgw_path):
                    os.remove(pgw_path)
            finally:
                QApplication.restoreOverrideCursor()

        render.finished.connect(finished)
        render.start()

    def _create_geotiff_from_png(self, image_path, geotiff_path):
        """Convert the rendered PNG to GeoTIFF."""

        ds = gdal.Open(image_path)

        # Convert the PNG to GeoTIFF
        gdal.Translate(
            geotiff_path,
            ds,
            outputSRS="EPSG:3067",
            format="GTiff",
            outputType=gdal.GDT_Byte,
            bandList=[1, 2, 3],
            creationOptions={
                "COMPRESS": "LZW",
                "TILED": "YES",
                "BIGTIFF": "IF_SAFER",
            },
        )

        iface.messageBar().pushSuccess("", f"GeoTIFF tallennettu polkuun: {geotiff_path}")
        if os.path.getsize(geotiff_path) > MAX_FILE_BYTES:
            iface.messageBar().pushWarning(
                "", "GeoTIFF on yli 1 Gt, eikä Ryhti hyväksy sitä. Valitse suurempi pikselin koko."
            )
