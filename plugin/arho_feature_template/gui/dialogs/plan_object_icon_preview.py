from importlib import resources
from typing import TYPE_CHECKING

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog, QFrame, QLabel, QPushButton

from arho_feature_template.core.plan_object_icons import PlanObjectIconRenderer
from arho_feature_template.project.layers.plan_layers import (
    LandUseAreaLayer,
    LineLayer,
    OtherAreaLayer,
    PlanObjectLayer,
    PointLayer,
)

if TYPE_CHECKING:
    from qgis.gui import QgsSpinBox


ui_path = resources.files(__package__) / "plan_object_icon_preview.ui"
FormClass, _ = uic.loadUiType(ui_path)


class PlanObjectIconPreview(QDialog, FormClass):  # type: ignore
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.width_spinbox: QgsSpinBox
        self.height_spinbox: QgsSpinBox
        self.generate_btn: QPushButton

        self.land_use_frame: QFrame
        self.other_area_frame: QFrame
        self.line_frame: QFrame
        self.point_frame: QFrame

        self.layers_and_widgets: list[tuple[PlanObjectLayer, QFrame]] = [
            (LandUseAreaLayer, self.land_use_frame),
            (OtherAreaLayer, self.other_area_frame),
            (LineLayer, self.line_frame),
            (PointLayer, self.point_frame),
        ]
        self._preview_labels: list[QLabel] = []
        self.generate_btn.clicked.connect(self.generate_previews)

        self.generate_previews()

    def generate_previews(self):
        self._clear()
        for layer_class, frame in self.layers_and_widgets:
            self._generate_preview(layer_class, frame)

    def _clear(self):
        for widget in self._preview_labels:
            widget.deleteLater()
        self._preview_labels.clear()

    def _generate_preview(self, layer_class: PlanObjectLayer, frame: QFrame):
        widget_index = 2
        for icon in PlanObjectIconRenderer.render_icons_for_layer(
            layer=layer_class, symbol_width=self.width_spinbox.value(), symbol_height=self.height_spinbox.value()
        ).values():
            label = QLabel()
            label.setPixmap(icon)
            frame.layout().insertWidget(widget_index, label)
            widget_index += 1
            self._preview_labels.append(label)
