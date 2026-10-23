"""The GeoTIFF dialog keeps scale, pixel size and dpi tied: pixel size = scale * 0.0254 / dpi."""

from __future__ import annotations

import pytest
from qgis.core import QgsRectangle
from qgis.PyQt.QtWidgets import QDialogButtonBox

from arho_feature_template.core.plan_scale import PIXEL_SIZES
from arho_feature_template.gui.dialogs.geotiff_dialog import GeoTiffDialog
from arho_feature_template.utils.widget_utils import deleted_after_use

pytestmark = pytest.mark.fake_iface

# A 1 km x 1 km asemakaava
PLAN_EXTENT = QgsRectangle(0, 0, 1000, 1000)


@pytest.fixture
def dialog(iface):
    with deleted_after_use(GeoTiffDialog(PLAN_EXTENT, 1000, iface.mainWindow())) as dialog:
        yield dialog


def _ok_enabled(dialog: GeoTiffDialog) -> bool:
    return dialog.button_box.button(QDialogButtonBox.StandardButton.Ok).isEnabled()


def test_defaults_follow_the_plan_scale(dialog):
    assert dialog.scale() == 1000
    assert dialog.pixel_size() == 0.125
    assert dialog.dpi() == pytest.approx(203.2)
    assert dialog.dpi_spin_box.value() == pytest.approx(203.2)


def test_new_pixel_size_changes_the_dpi(dialog):
    dialog.pixel_size_combo_box.setCurrentIndex(PIXEL_SIZES.index(0.5))

    assert dialog.scale() == 1000
    assert dialog.dpi_spin_box.value() == pytest.approx(50.8)


def test_new_dpi_picks_the_nearest_pixel_size(dialog):
    dialog.dpi_spin_box.setValue(300)
    dialog.dpi_spin_box.editingFinished.emit()

    assert dialog.pixel_size() == 0.0625
    assert dialog.dpi_spin_box.value() == pytest.approx(406.4)


def test_new_scale_keeps_the_pixel_size(dialog):
    dialog.scale_spin_box.setValue(2000)

    assert dialog.pixel_size() == 0.125
    assert dialog.dpi_spin_box.value() == pytest.approx(406.4)


def test_ok_needs_a_file_and_a_scale(dialog):
    assert not _ok_enabled(dialog)

    dialog.file_widget.setFilePath("plan.tif")
    assert _ok_enabled(dialog)

    dialog.scale_spin_box.setValue(0)
    assert not _ok_enabled(dialog)


def test_unknown_scale_starts_from_half_a_metre(iface):
    with deleted_after_use(GeoTiffDialog(PLAN_EXTENT, None, iface.mainWindow())) as dialog:
        assert dialog.pixel_size() == 0.5
        assert not dialog.dpi_spin_box.isEnabled()


def test_too_large_image_blocks_ok(dialog):
    dialog.file_widget.setFilePath("plan.tif")

    # 1200 m / 0.015625 m = 76800 px per side, about 23.6 GB in memory
    dialog.pixel_size_combo_box.setCurrentIndex(PIXEL_SIZES.index(0.015625))

    assert dialog.warning_label.text()
    assert not _ok_enabled(dialog)
