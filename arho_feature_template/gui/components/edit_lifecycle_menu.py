from __future__ import annotations

from qgis.PyQt.QtCore import QDate, pyqtSignal
from qgis.PyQt.QtGui import QAction, QIcon
from qgis.PyQt.QtWidgets import QDateEdit, QDialog, QDialogButtonBox, QLabel, QMenu, QVBoxLayout, QWidget

from arho_feature_template.project.layers.code_layers import (
    LIFECYCLE_PIXMAPS,
    LifeCycleStatusLayer,
    LifeCycleStatusValue,
)
from arho_feature_template.project.layers.plan_layers import PlanMatterLayer
from arho_feature_template.qgis_plugin_tools.tools.resources import resources_path
from arho_feature_template.utils.localization_utils import get_localized_text
from arho_feature_template.utils.misc_utils import get_active_plan_matter_id

lifecycle_status_icons = {
    LifeCycleStatusValue.REPEALED: QIcon(resources_path("icons", "repealed_mark.svg")),
    LifeCycleStatusValue.VALID: QIcon(resources_path("icons", "valid_mark.svg")),
    LifeCycleStatusValue.UNDER_APPEAL: QIcon(resources_path("icons", "under_appeal.svg")),
    LifeCycleStatusValue.UNDER_RECTIFICATION_REMINDER: QIcon(resources_path("icons", "under_appeal.svg")),
    LifeCycleStatusValue.UNDER_RECTIFICATION_REMINDER_AND_UNDER_APPEAL: QIcon(
        resources_path("icons", "under_appeal.svg")
    ),
}


class EditLifecycleMenu(QMenu):
    lifecycle_change_requested = pyqtSignal(LifeCycleStatusValue, object)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        lifecycle_values = [
            LifeCycleStatusValue.VALID,
            LifeCycleStatusValue.UNDER_APPEAL,
            LifeCycleStatusValue.UNDER_RECTIFICATION_REMINDER,
            LifeCycleStatusValue.UNDER_RECTIFICATION_REMINDER_AND_UNDER_APPEAL,
            LifeCycleStatusValue.REPEALED,
        ]
        if PlanMatterLayer.is_regional_plan(get_active_plan_matter_id()):
            lifecycle_values.insert(1, LifeCycleStatusValue.VALID_BEFORE_LEGAL_VALIDITY)

        for lifecycle_value in lifecycle_values:
            lifecycle_name = get_localized_text(
                LifeCycleStatusLayer.get_attribute_value_by_another_attribute_value(
                    "name", "value", lifecycle_value.value
                )
            )
            if not lifecycle_name:
                continue
            action = self.addAction(lifecycle_name)
            action.setData(lifecycle_value)
            action.setIcon(QIcon(LIFECYCLE_PIXMAPS[lifecycle_value]))

        self.triggered.connect(self._on_triggered)

    def _on_triggered(self, action: QAction):
        lifecycle_value = action.data()
        date = None
        if lifecycle_value == LifeCycleStatusValue.VALID:
            date = ask_date(self.parentWidget())
            if date is None:
                return
        if lifecycle_value:
            self.lifecycle_change_requested.emit(lifecycle_value, date)


def ask_date(parent: QWidget | None = None, initial: QDate | None = None) -> QDate | None:
    dialog = QDialog(parent)
    dialog.setWindowTitle("Voimaantulopäivä")

    date_edit = QDateEdit()
    date_edit.setCalendarPopup(True)
    date_edit.setDate(initial or QDate.currentDate())

    buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
    buttons.accepted.connect(dialog.accept)
    buttons.rejected.connect(dialog.reject)

    layout = QVBoxLayout(dialog)
    layout.addWidget(QLabel("Valitse kohteiden voimaantulopäivä:"))
    layout.addWidget(date_edit)
    layout.addWidget(buttons)

    if dialog.exec_() == QDialog.Accepted:
        return date_edit.date()

    return None
