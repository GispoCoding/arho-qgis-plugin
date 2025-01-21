from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING

from qgis.core import QgsFeature, QgsFeatureRequest, QgsPointXY, QgsRectangle, QgsVectorLayer
from qgis.gui import QgsMapCanvas, QgsMapMouseEvent, QgsMapTool, QgsRubberBand
from qgis.PyQt.QtCore import QPoint, Qt, QTimer, pyqtSignal
from qgis.PyQt.QtGui import QColor
from qgis.PyQt.QtWidgets import QMenu
from qgis.utils import OverrideCursor

if TYPE_CHECKING:
    from arho_feature_template.project.layers.plan_layers import PlanFeatureLayer


class InspectPlanFeatures(QgsMapTool):
    CLICK_POS_TOLERANCE = 2
    edit_feature_requested = pyqtSignal(QgsFeature, str)

    def __init__(self, canvas: QgsMapCanvas, layer_classes: list[PlanFeatureLayer]):
        super().__init__(canvas)
        self.canvas = canvas

        self.layer_classes = layer_classes
        self.layers: list[QgsVectorLayer] | None = None

        self.highlighted: tuple[QgsFeature, str] | None = None
        self.highlight_rubber_band: QgsRubberBand | None = None

    def activate(self):
        super().activate()

    def create_highlight_rubberband(self, feature: QgsFeature, layer: QgsVectorLayer):
        self.highlight_rubber_band = QgsRubberBand(self.canvas, layer.geometryType())
        self.highlight_rubber_band.setToGeometry(feature.geometry(), layer)
        self.highlight_rubber_band.setColor(QColor(255, 0, 0, 100))  # Semi-transparent red
        self.highlight_rubber_band.setWidth(2)

    def _clear_highlight(self):
        if self.highlight_rubber_band:
            self.canvas.scene().removeItem(self.highlight_rubber_band)
            self.highlight_rubber_band = None

    def check_menu_selections(self, menu: QMenu):
        # If no menu item is selected, clear highlights/rubberbands
        if menu.activeAction() is None:
            self._clear_highlight()

    def highlight_feature(self, feature: QgsFeature, layer: QgsVectorLayer):
        self._clear_highlight()
        self.create_highlight_rubberband(feature, layer)

    def canvasReleaseEvent(self, event: QgsMapMouseEvent):  # noqa: N802
        point = self.toMapCoordinates(event.pos())
        nearby_features = self.query_nearby_features(point)

        if nearby_features:
            self.create_menu(event.pos(), nearby_features)

    def query_nearby_features(self, point: QgsPointXY) -> dict[QgsVectorLayer, list[QgsFeature]]:
        """Query all feature layers for features near (within `CLICK_POS_TOLERANCE`) the clicked point."""
        results = {}
        tolerance_geom = QgsRectangle(
            point.x() - self.CLICK_POS_TOLERANCE,
            point.y() - self.CLICK_POS_TOLERANCE,
            point.x() + self.CLICK_POS_TOLERANCE,
            point.y() + self.CLICK_POS_TOLERANCE,
        )
        request = QgsFeatureRequest()
        request.setFilterRect(tolerance_geom)
        request.setFlags(QgsFeatureRequest.Flag.ExactIntersect)

        # Lazy reading of feature layers to avoid reading them too early
        if self.layers is None:
            self.layers = [cls.get_from_project() for cls in self.layer_classes]

        with OverrideCursor(Qt.WaitCursor):
            for layer in self.layers:
                features = list(layer.getFeatures(request))
                if features:
                    results[layer] = features

        return results

    def create_menu(self, click_pos: QPoint, nearby_features: dict[QgsVectorLayer, list[QgsFeature]]):
        """Create a menu with feature layer names at the click position."""
        menu = QMenu("Avaa kaavakohteen tiedot")
        for layer, features in nearby_features.items():
            for feature in features:
                menu_text = layer.name()
                # feat_name = feature["name"]["fin"]
                # if feat_name:
                #     menu_text += f" — {feat_name}"
                action = menu.addAction(menu_text)
                action.triggered.connect(partial(self.edit_feature_requested.emit, feature, layer.name()))
                action.hovered.connect(partial(self.highlight_feature, feature, layer))
        if not menu.isEmpty():
            self.show_menu(menu, click_pos)

    def show_menu(self, menu: QMenu, screen_pos: QPoint):
        self._create_timer(menu)
        menu.aboutToHide.connect(self.close_menu)
        menu.exec_(self.canvas.mapToGlobal(screen_pos))

    def close_menu(self):
        self._clear_highlight()
        self._destroy_timer()

    def _create_timer(self, menu: QMenu):
        self.check_menu_selections_timer = QTimer(self)
        self.check_menu_selections_timer.timeout.connect(lambda: self.check_menu_selections(menu))
        self.check_menu_selections_timer.start(100)  # 0.1 seconds interval

    def _destroy_timer(self):
        self.check_menu_selections_timer.timeout.disconnect()
        self.check_menu_selections_timer.deleteLater()
        self.check_menu_selections_timer = None
