from __future__ import annotations

from typing import TYPE_CHECKING, Sequence

from qgis.core import QgsFeature, QgsVectorLayer
from qgis.gui import QgsMapCanvas, QgsMapMouseEvent, QgsMapToolIdentify
from qgis.PyQt.QtCore import Qt, pyqtSignal

from arho_feature_template.exceptions import LayerNotFoundError

if TYPE_CHECKING:
    from arho_feature_template.project.layers import AbstractLayer

LayerPairs = list[tuple[type["AbstractLayer"], QgsVectorLayer]]


class InspectPlanFeatures(QgsMapToolIdentify):
    """Identifies a plan object on the given layers and reports it with its layer class.

    Layer names repeat across the layer tree groups, so the layer class, not the name, says
    which kind of layer the feature came from.
    """

    # (feature, layer class). The class travels as `object`.
    feature_identified = pyqtSignal(QgsFeature, object)

    def __init__(
        self,
        canvas: QgsMapCanvas,
        layer_classes: Sequence[type[AbstractLayer]],
        visible_only: bool = True,  # noqa: FBT001, FBT002
    ):
        super().__init__(canvas)
        self.canvas = canvas

        self.layer_classes = list(layer_classes)
        # Only identify on layers shown in the canvas, like the identify tool of QGIS.
        self.visible_only = visible_only
        self.layers: list[QgsVectorLayer] = []

        # Set to QgsMapTool cursor
        self.setCursor(Qt.CursorShape.CrossCursor)

        # Disable "Identify all action"
        self.identifyMenu().setAllowMultipleReturn(False)

    def activate(self):
        super().activate()

    def resolve_layers(self) -> LayerPairs:
        """Project layers of the configured classes, in configuration order.

        Missing layers are skipped. Hidden layers are skipped when `visible_only` is set.
        """
        visible_ids = None
        if self.visible_only:
            # Expand group layers, so that their child layers count as visible
            visible_ids = {layer.id() for layer in self.canvas.layers(True)}

        pairs: LayerPairs = []
        for layer_class in self.layer_classes:
            try:
                layer = layer_class.get_from_project()
            except LayerNotFoundError:
                continue
            if visible_ids is None or layer.id() in visible_ids:
                pairs.append((layer_class, layer))
        return pairs

    @staticmethod
    def layer_class_for(layer: QgsVectorLayer, pairs: LayerPairs) -> type[AbstractLayer] | None:
        return next((layer_class for layer_class, candidate in pairs if candidate.id() == layer.id()), None)

    def canvasReleaseEvent(self, event: QgsMapMouseEvent):  # noqa: N802
        pairs = self.resolve_layers()
        self.layers = [layer for _, layer in pairs]
        identify_results = self.identify(
            x=event.x(), y=event.y(), layerList=self.layers, mode=QgsMapToolIdentify.IdentifyMode.LayerSelection
        )
        if identify_results:
            self.emit_result(identify_results[0], pairs)

    def emit_result(self, result: QgsMapToolIdentify.IdentifyResult, pairs: LayerPairs) -> None:
        layer_class = self.layer_class_for(result.mLayer, pairs)
        if layer_class is not None:
            self.feature_identified.emit(result.mFeature, layer_class)
