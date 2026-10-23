from __future__ import annotations

import os
from importlib import resources
from typing import TYPE_CHECKING

from qgis.PyQt import uic
from qgis.PyQt.QtCore import QLocale, QSignalBlocker
from qgis.PyQt.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QLabel,
    QMessageBox,
    QSpinBox,
    QWidget,
)

from arho_feature_template.core.plan_scale import (
    PIXEL_SIZES,
    default_pixel_size,
    dpi_for,
    image_size,
    nearest_allowed_pixel_size,
    pixel_size_for,
    plan_map_extent,
    scale_for,
)

if TYPE_CHECKING:
    from qgis.core import QgsRectangle
    from qgis.gui import QgsFileWidget

ui_path = resources.files(__package__) / "geotiff_dialog.ui"
FormClass, _ = uic.loadUiType(ui_path)

# The map is rendered into one image in memory, 4 bytes per pixel
MAX_IMAGE_BYTES = 2 * 1024**3
# Ryhti accepts plan maps up to 1 GB
MAX_FILE_BYTES = 1_000_000_000
# Pixel size when the scale is not known
FALLBACK_PIXEL_SIZE = 0.5


class GeoTiffDialog(QDialog, FormClass):  # type: ignore
    """Asks the output file, scale, pixel size and dpi of the plan map GeoTIFF.

    The three values are tied by pixel size = scale * 0.0254 / dpi. A typed scale or dpi
    stays: the other of the two picks the nearest allowed pixel size and is then fitted to
    it. A new pixel size keeps the scale and changes the dpi.
    """

    file_widget: QgsFileWidget
    scale_spin_box: QSpinBox
    pixel_size_combo_box: QComboBox
    dpi_spin_box: QDoubleSpinBox
    image_size_label: QLabel
    warning_label: QLabel
    button_box: QDialogButtonBox

    def __init__(
        self, plan_extent: QgsRectangle, scale: int | None, file_path: str = "", parent: QWidget | None = None
    ):
        super().__init__(parent)
        self.setupUi(self)

        self.plan_extent = plan_extent
        self.image_too_large = False
        self.file_widget.setFilePath(file_path)

        for pixel_size in PIXEL_SIZES:
            self.pixel_size_combo_box.addItem(QLocale().toString(pixel_size, "g", 10), pixel_size)

        self.scale_spin_box.setValue(scale or 0)
        self.pixel_size_combo_box.setCurrentIndex(
            PIXEL_SIZES.index(default_pixel_size(scale) if scale else FALLBACK_PIXEL_SIZE)
        )
        self._update_dpi()
        self._update_image_size()

        self.file_widget.fileChanged.connect(self._check_inputs)
        self.scale_spin_box.valueChanged.connect(self._on_scale_changed)
        self.pixel_size_combo_box.currentIndexChanged.connect(self._on_pixel_size_changed)
        self.dpi_spin_box.valueChanged.connect(self._on_dpi_changed)
        self.button_box.accepted.connect(self._on_ok_clicked)

    def file_path(self) -> str:
        file_path = self.file_widget.filePath()
        if file_path and not file_path.lower().endswith((".tif", ".tiff")):
            file_path += ".tif"
        return file_path

    def scale(self) -> int:
        return self.scale_spin_box.value()

    def pixel_size(self) -> float:
        return PIXEL_SIZES[self.pixel_size_combo_box.currentIndex()]

    def dpi(self) -> float:
        return self.dpi_spin_box.value()

    def _on_scale_changed(self):
        # Without a scale before, the dpi is 0 and the pixel size stays
        if self.scale() and self.dpi() > 0:
            self._set_pixel_size(nearest_allowed_pixel_size(pixel_size_for(self.scale(), self.dpi())))
        self._update_dpi()
        self._update_image_size()

    def _on_pixel_size_changed(self):
        self._update_dpi()
        self._update_image_size()

    def _on_dpi_changed(self):
        dpi = self.dpi()
        if not self.scale() or dpi <= 0:
            self._update_dpi()
            return
        pixel_size = nearest_allowed_pixel_size(pixel_size_for(self.scale(), dpi))
        scale = min(max(round(scale_for(pixel_size, dpi)), 1), self.scale_spin_box.maximum())
        self._set_pixel_size(pixel_size)
        with QSignalBlocker(self.scale_spin_box):
            self.scale_spin_box.setValue(scale)
        self._update_image_size()

    def _set_pixel_size(self, pixel_size: float):
        with QSignalBlocker(self.pixel_size_combo_box):
            self.pixel_size_combo_box.setCurrentIndex(PIXEL_SIZES.index(pixel_size))

    def _update_dpi(self):
        self.dpi_spin_box.setEnabled(bool(self.scale()))
        with QSignalBlocker(self.dpi_spin_box):
            self.dpi_spin_box.setValue(dpi_for(self.scale(), self.pixel_size()) if self.scale() else 0)

    def _update_image_size(self):
        pixel_size = self.pixel_size()
        width, height = image_size(plan_map_extent(self.plan_extent, pixel_size), pixel_size)
        file_bytes = width * height * 3
        self.image_too_large = width * height * 4 > MAX_IMAGE_BYTES

        locale = QLocale()
        self.image_size_label.setText(
            f"{locale.toString(width)} × {locale.toString(height)} px, "  # noqa: RUF001
            f"pakkaamattomana noin {locale.toString(file_bytes / 1e6, 'f', 0)} Mt"
        )
        if self.image_too_large:
            warning = "Kuva on liian suuri piirrettäväksi. Valitse suurempi pikselin koko."
        elif file_bytes > MAX_FILE_BYTES:
            warning = (
                "Pakkaamaton kuva on yli 1 Gt, joka on Ryhdin yläraja. Pakattu tiedosto on yleensä paljon pienempi."
            )
        else:
            warning = ""
        self.warning_label.setText(warning)
        self.warning_label.setVisible(bool(warning))
        self._check_inputs()

    def _on_ok_clicked(self):
        if (
            os.path.exists(self.file_path())
            and QMessageBox.question(
                self,
                "Tiedosto on jo olemassa",
                f"Tiedosto {self.file_path()} on jo olemassa. Korvataanko?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            != QMessageBox.StandardButton.Yes
        ):
            return
        self.accept()

    def _check_inputs(self):
        self.button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(
            bool(self.file_path()) and bool(self.scale()) and not self.image_too_large
        )
