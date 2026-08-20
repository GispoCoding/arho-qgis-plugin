from __future__ import annotations

from typing import TYPE_CHECKING

from qgis.PyQt.QtCore import QSize, Qt, pyqtSignal
from qgis.PyQt.QtGui import QIcon, QMouseEvent, QStandardItem
from qgis.PyQt.QtWidgets import QLabel, QSizePolicy, QWidget

from arho_feature_template.core.lifecycles import LIFECYCLE_PIXMAPS, LifeCycleStatusValue
from arho_feature_template.project.layers.code_layers import (
    LifeCycleStatusLayer,
)
from arho_feature_template.utils.localization_utils import get_localized_text
from arho_feature_template.utils.misc_utils import date_as_str

if TYPE_CHECKING:
    from arho_feature_template.core.models import LifecycleBase

VALIDITY_SORT_ROLE = Qt.ItemDataRole.UserRole


class ValidityLabel(QLabel):
    clicked = pyqtSignal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setMaximumSize(23, 23)
        self.setScaledContents(True)

    def mousePressEvent(self, ev: QMouseEvent):  # noqa: N802
        self.clicked.emit()
        super().mousePressEvent(ev)

    def set_from_model(self, model: LifecycleBase) -> None:
        if not hasattr(model, "lifecycle_status_id") or model.lifecycle_status_id is None:
            self.hide_widget()
            return

        lifecycle_status = LifeCycleStatusLayer.get_lifecycle_status_by_id(model.lifecycle_status_id)
        if lifecycle_status is None:
            self.hide_widget()
            return
        lifecycle_name = LifeCycleStatusLayer.get_name_by_id(model.lifecycle_status_id)
        if LifeCycleStatusLayer.is_repealed_status(model.lifecycle_status_id):
            self.setPixmap(LIFECYCLE_PIXMAPS[LifeCycleStatusValue.REPEALED])

            if model.period_of_validity_start is not None and model.period_of_validity_end is not None:  # type: ignore
                self.setToolTip(
                    "KUMOTTU\n"  # noqa: ISC003
                    + f"Voimassa {date_as_str(model.period_of_validity_start)} - "  # type: ignore
                    + date_as_str(model.period_of_validity_end)  # type: ignore
                )
            elif model.period_of_validity_end is not None:  # type: ignore
                self.setToolTip(f"KUMOTTU\nKumottu alkaen: {date_as_str(model.period_of_validity_end)}")  # type: ignore
            else:
                self.setToolTip("KUMOTTU")

        elif LifeCycleStatusLayer.is_valid_status(model.lifecycle_status_id):
            self.setPixmap(LIFECYCLE_PIXMAPS[LifeCycleStatusValue.VALID])
            self.setToolTip(f"VOIMASSA\nVoimassa alkaen: {date_as_str(model.period_of_validity_start)}")  # type: ignore

        else:
            pixmap = LIFECYCLE_PIXMAPS.get(lifecycle_status)
            if pixmap is None:
                self.hide_widget()
                return
            self.setPixmap(pixmap)
            lifecycle_name_translated = get_localized_text(lifecycle_name)
            if lifecycle_name_translated:
                self.setToolTip(lifecycle_name_translated)

    def hide_widget(self):
        self.setToolTip("")
        self.hide()


def validity_item_from_model(model: LifecycleBase) -> QStandardItem:
    """
    Create a QStandardItem with valid icon, repealed icon or no icon depending on model status.

    Items are meant to be used in PlanObjectDock table.

    Each item has a validity number for sorting stored in `VALIDITY_SORT_ROLE`.
    0 = valid, 1 = repealed, 0 = undefined.
    """
    item = QStandardItem("")
    item.setEditable(False)

    item.setData(QSize(23, 23), Qt.ItemDataRole.SizeHintRole)

    if not hasattr(model, "lifecycle_status_id") or model.lifecycle_status_id is None:
        item.setData(2, VALIDITY_SORT_ROLE)
        return item

    lifecycle_status = LifeCycleStatusLayer.get_lifecycle_status_by_id(model.lifecycle_status_id)
    if lifecycle_status is None:
        item.setData(2, VALIDITY_SORT_ROLE)
        return item
    lifecycle_name = LifeCycleStatusLayer.get_name_by_id(model.lifecycle_status_id)
    if LifeCycleStatusLayer.is_repealed_status(model.lifecycle_status_id):
        item.setData(QIcon(LIFECYCLE_PIXMAPS[LifeCycleStatusValue.REPEALED]), Qt.ItemDataRole.DecorationRole)

        if model.period_of_validity_start and model.period_of_validity_end:  # type: ignore
            tooltip = (
                "KUMOTTU\n"
                f"Voimassa {date_as_str(model.period_of_validity_start)} - "  # type: ignore
                f"{date_as_str(model.period_of_validity_end)}"  # type: ignore
            )
        elif model.period_of_validity_end:  # type: ignore
            tooltip = f"KUMOTTU\nKumottu alkaen: {date_as_str(model.period_of_validity_end)}"  # type: ignore
        else:
            tooltip = "KUMOTTU"

        item.setData(1, VALIDITY_SORT_ROLE)
        item.setData(tooltip, Qt.ItemDataRole.ToolTipRole)

    elif LifeCycleStatusLayer.is_valid_status(model.lifecycle_status_id):
        item.setData(QIcon(LIFECYCLE_PIXMAPS[LifeCycleStatusValue.VALID]), Qt.ItemDataRole.DecorationRole)
        item.setData(
            f"VOIMASSA\nVoimassa alkaen: {date_as_str(model.period_of_validity_start)}", Qt.ItemDataRole.ToolTipRole
        )  # type: ignore
        item.setData(0, VALIDITY_SORT_ROLE)

    elif LifeCycleStatusLayer.is_under_appeal(lifecycle_status):
        icon = LIFECYCLE_PIXMAPS[lifecycle_status]
        item.setData(QIcon(icon), Qt.ItemDataRole.DecorationRole)
        item.setData(get_localized_text(lifecycle_name), Qt.ItemDataRole.ToolTipRole)
        item.setData(3, VALIDITY_SORT_ROLE)

    return item
