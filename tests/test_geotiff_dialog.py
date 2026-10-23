"""The GeoTIFF dialog keeps scale, pixel size and dpi tied: pixel size = scale * 0.0254 / dpi.

OK asks before it overwrites a file.
"""

from __future__ import annotations

import pytest
from qgis.core import QgsRectangle
from qgis.PyQt.QtWidgets import QDialog, QDialogButtonBox, QMessageBox

from arho_feature_template.core.plan_scale import PIXEL_SIZES
from arho_feature_template.gui.dialogs.geotiff_dialog import GeoTiffDialog
from arho_feature_template.utils.widget_utils import deleted_after_use

pytestmark = pytest.mark.fake_iface

# A 1 km x 1 km asemakaava
PLAN_EXTENT = QgsRectangle(0, 0, 1000, 1000)


@pytest.fixture
def dialog(iface):
    with deleted_after_use(GeoTiffDialog(PLAN_EXTENT, 1000, parent=iface.mainWindow())) as dialog:
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
    with deleted_after_use(GeoTiffDialog(PLAN_EXTENT, None, parent=iface.mainWindow())) as dialog:
        assert dialog.pixel_size() == 0.5
        assert not dialog.dpi_spin_box.isEnabled()


def test_too_large_image_blocks_ok(dialog):
    dialog.file_widget.setFilePath("plan.tif")

    # 1200 m / 0.015625 m = 76800 px per side, about 23.6 GB in memory
    dialog.pixel_size_combo_box.setCurrentIndex(PIXEL_SIZES.index(0.015625))

    assert dialog.warning_label.text()
    assert not _ok_enabled(dialog)


def test_given_path_enables_ok_at_once(iface, tmp_path):
    file_path = str(tmp_path / "Keskusta - Ehdotus.tif")
    with deleted_after_use(GeoTiffDialog(PLAN_EXTENT, 1000, file_path, iface.mainWindow())) as dialog:
        assert dialog.file_path() == file_path
        assert _ok_enabled(dialog)


def test_tif_suffix_is_added(dialog):
    dialog.file_widget.setFilePath("plan")

    assert dialog.file_path() == "plan.tif"


@pytest.mark.parametrize(
    ("answer", "result"),
    [
        (QMessageBox.StandardButton.No, QDialog.DialogCode.Rejected),
        (QMessageBox.StandardButton.Yes, QDialog.DialogCode.Accepted),
    ],
)
def test_ok_asks_before_overwriting(dialog, tmp_path, monkeypatch, answer, result):
    existing = tmp_path / "plan.tif"
    existing.write_bytes(b"")
    dialog.file_widget.setFilePath(str(existing))
    questions = []
    monkeypatch.setattr(QMessageBox, "question", lambda *args: questions.append(args) or answer)

    dialog.button_box.button(QDialogButtonBox.StandardButton.Ok).click()

    assert len(questions) == 1
    assert dialog.result() == result


def test_ok_does_not_ask_for_a_new_file(dialog, tmp_path, monkeypatch):
    dialog.file_widget.setFilePath(str(tmp_path / "plan.tif"))
    monkeypatch.setattr(QMessageBox, "question", lambda *_args: pytest.fail("asked"))

    dialog.button_box.button(QDialogButtonBox.StandardButton.Ok).click()

    assert dialog.result() == QDialog.DialogCode.Accepted
