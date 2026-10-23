from __future__ import annotations

from importlib import resources
from typing import TYPE_CHECKING

from qgis.PyQt import uic
from qgis.PyQt.QtCore import QLocale
from qgis.PyQt.QtWidgets import QComboBox, QDialog, QDialogButtonBox, QDoubleSpinBox, QLabel, QSpinBox, QWidget

from arho_feature_template.core.plan_scale import (
    PIXEL_SIZES,
    default_pixel_size,
    dpi_for,
    image_size,
    nearest_allowed_pixel_size,
    pixel_size_for,
    plan_map_extent,
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

    The three values are tied by pixel size = scale * 0.0254 / dpi. A new pixel size or a
    new scale changes the dpi. A new dpi picks the nearest allowed pixel size.
    """

    file_widget: QgsFileWidget
    scale_spin_box: QSpinBox
    pixel_size_combo_box: QComboBox
    dpi_spin_box: QDoubleSpinBox
    image_size_label: QLabel
    warning_label: QLabel
    button_box: QDialogButtonBox

    def __init__(self, plan_extent: QgsRectangle, scale: int | None, parent: QWidget | None = None):
        super().__init__(parent)
        self.setupUi(self)

        self.plan_extent = plan_extent
        self.image_too_large = False

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
        self.dpi_spin_box.editingFinished.connect(self._on_dpi_edited)

    def file_path(self) -> str:
        return self.file_widget.filePath()

    def scale(self) -> int:
        return self.scale_spin_box.value()

    def pixel_size(self) -> float:
        return PIXEL_SIZES[self.pixel_size_combo_box.currentIndex()]

    def dpi(self) -> float:
        return dpi_for(self.scale(), self.pixel_size())

    def _on_scale_changed(self):
        self._update_dpi()
        self._check_inputs()

    def _on_pixel_size_changed(self):
        self._update_dpi()
        self._update_image_size()

    def _on_dpi_edited(self):
        dpi = self.dpi_spin_box.value()
        if self.scale() and dpi > 0:
            pixel_size = nearest_allowed_pixel_size(pixel_size_for(self.scale(), dpi))
            self.pixel_size_combo_box.setCurrentIndex(PIXEL_SIZES.index(pixel_size))
        # Show the dpi of the chosen pixel size, also when the pixel size did not change
        self._update_dpi()

    def _update_dpi(self):
        self.dpi_spin_box.setEnabled(bool(self.scale()))
        self.dpi_spin_box.setValue(self.dpi() if self.scale() else 0)

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

    def _check_inputs(self):
        self.button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(
            bool(self.file_path()) and bool(self.scale()) and not self.image_too_large
        )
