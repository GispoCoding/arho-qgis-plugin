from __future__ import annotations

from typing import TYPE_CHECKING

from qgis.core import QgsFeature, QgsVectorLayer
from qgis.gui import QgsMapCanvas, QgsMapMouseEvent, QgsMapToolIdentify
from qgis.PyQt.QtCore import Qt, pyqtSignal

from arho_feature_template.utils.misc_utils import disconnect_signal

if TYPE_CHECKING:
    from arho_feature_template.project.layers.plan_layers import PlanObjectLayer


class InspectPlanFeatures(QgsMapToolIdentify):
    edit_feature_requested = pyqtSignal(QgsFeature, str)

    def __init__(self, canvas: QgsMapCanvas, layer_classes: list[PlanObjectLayer]):
        super().__init__(canvas)
        self.canvas = canvas

        self.layer_classes = layer_classes
        self.layers: list[QgsVectorLayer] | None = None

        # Set to QgsMapTool cursor
        self.setCursor(Qt.CrossCursor)

        # Disable "Identify all action"
        self.identifyMenu().setAllowMultipleReturn(False)

    def activate(self):
        super().activate()

    def canvasReleaseEvent(self, event: QgsMapMouseEvent):  # noqa: N802
        self.layers = [cls.get_from_project() for cls in self.layer_classes]
        identify_results = self.identify(
            x=event.x(), y=event.y(), layerList=self.layers, mode=QgsMapToolIdentify.IdentifyMode.LayerSelection
        )
        if identify_results:
            result = identify_results[0]
            self.edit_feature_requested.emit(result.mFeature, result.mLayer.name())

    def unload(self):
        disconnect_signal(self.edit_feature_requested)
