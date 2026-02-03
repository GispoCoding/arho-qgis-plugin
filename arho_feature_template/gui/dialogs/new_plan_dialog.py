from __future__ import annotations

from importlib import resources
from typing import TYPE_CHECKING

from qgis.PyQt import uic
from qgis.PyQt.QtCore import QDate, QDateTime, Qt, pyqtSignal
from qgis.PyQt.QtWidgets import QComboBox, QDialog, QDialogButtonBox, QLineEdit, QWidget

from arho_feature_template.core.lambda_service import LambdaService
from arho_feature_template.core.models import Plan
from arho_feature_template.project.layers.code_layers import LifeCycleStatusLayer
from arho_feature_template.project.layers.plan_layers import PlanLayer
from arho_feature_template.utils.misc_utils import (
    get_active_plan_id,
    get_active_plan_matter_id,
    iface,
)

if TYPE_CHECKING:
    from qgis.gui import QgsDateTimeEdit
    from qgis.PyQt.QtWidgets import QLabel

    from arho_feature_template.gui.components.code_combobox import CodeComboBox

ui_path = resources.files(__package__) / "new_plan_dialog.ui"
FormClass, _ = uic.loadUiType(ui_path)

DATA_ROLE = Qt.UserRole

VALID_LIFECYCLE_TEXT = "Voimassa"
APPORVED_LIFECYCLE_TEXT = "Hyväksytty kaava"


class NewPlanDialog(QDialog, FormClass):  # type: ignore
    plan_copied = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setModal(True)
        self.setFixedWidth(550)
        self.widget_progress.hide()
        self.adjustSize()

        # TYPES
        self.plan_name: QLineEdit
        self.plan_lifecycle: CodeComboBox
        self.source_plan: QComboBox
        self.button_box: QDialogButtonBox
        self.widget_input: QWidget
        self.widget_progress: QWidget
        self.label_validity_start: QLabel
        self.validity_start_date: QgsDateTimeEdit
        self.label_approval: QLabel
        self.approval_date: QgsDateTimeEdit

        # INIT
        self.plan = None
        self.plan_layer = PlanLayer.get_from_project()
        self.previously_in_edit_mode = self.plan_layer.isEditable()

        self.populate_plan_combobox()
        self.plan_lifecycle.populate_from_code_layer(LifeCycleStatusLayer)
        self.plan_name.textChanged.connect(self._check_required_fields)
        self.plan_lifecycle.currentIndexChanged.connect(self._check_required_fields)
        self.button_box.accepted.connect(self._on_ok_clicked)

        self.lambda_service = LambdaService()
        self.lambda_service.plan_copied.connect(self._plan_copied)
        self.lambda_service.plan_copy_failed.connect(self._handle_copy_failed)

        # Start date widget initially invisible
        self.label_validity_start.setVisible(False)
        self.validity_start_date.setVisible(False)
        self.label_approval.setVisible(False)
        self.approval_date.setVisible(False)

        # Set dates as today initially
        self.validity_start_date.setDateTime(QDateTime(QDate.currentDate()))
        self.approval_date.setDateTime(QDateTime(QDate.currentDate()))

        # Show/hide start date based on lifecycle stage
        self.plan_lifecycle.currentTextChanged.connect(self._update_validity_widgets)
        self._update_validity_widgets(self.plan_lifecycle.currentText())

        self._check_required_fields()

    def populate_plan_combobox(self):
        active_plan_id = get_active_plan_id()
        selected_index = None
        self.source_plan.addItem("NULL")
        for index, plan in enumerate(PlanLayer.get_plans_for_active_plan_matter(), start=1):
            self.source_plan.addItem(plan.name, plan.id_)
            if plan.id_ == active_plan_id:
                selected_index = index

        if selected_index is not None:
            self.source_plan.setCurrentIndex(selected_index)

    def _check_required_fields(self) -> None:
        ok_button = self.button_box.button(QDialogButtonBox.Ok)

        # Required: plan name + lifecycle
        required_fields_filled = self.plan_name.text() != "" and self.plan_lifecycle.value() is not None

        # Require valid/approved date for corresponding lifecycle statuses
        if self.validity_start_date.isVisible():
            required_fields_filled = required_fields_filled and self.validity_start_date.date() is not None
        if self.approval_date.isVisible():
            required_fields_filled = required_fields_filled and self.approval_date.date() is not None

        ok_button.setEnabled(required_fields_filled)

    def _update_validity_widgets(self, text: str):
        self.label_validity_start.setVisible(text == VALID_LIFECYCLE_TEXT)
        self.validity_start_date.setVisible(text == VALID_LIFECYCLE_TEXT)

        self.label_approval.setVisible(text == APPORVED_LIFECYCLE_TEXT)
        self.approval_date.setVisible(text == APPORVED_LIFECYCLE_TEXT)

        # Re-check required fields after visibility change
        self._check_required_fields()

    def _on_ok_clicked(self):
        plan_id = self.source_plan.currentData(DATA_ROLE)

        period_of_validity_start = (
            self.validity_start_date.date().toPyDate()
            if self.plan_lifecycle.currentText() == VALID_LIFECYCLE_TEXT
            else None
        )
        approval_date = (
            self.approval_date.date().toPyDate()
            if self.plan_lifecycle.currentText() == APPORVED_LIFECYCLE_TEXT
            else None
        )

        if plan_id is not None:
            self.widget_input.hide()
            self.widget_progress.show()
            self.adjustSize()

            # Pass the start date only if applicable
            self.lambda_service.copy_plan(
                plan_id,
                self.plan_lifecycle.value(),
                self.plan_name.text(),
                period_of_validity_start=period_of_validity_start,
                approval_date=approval_date,
            )
        else:
            self.plan = Plan(
                name=self.plan_name.text(),
                lifecycle_status_id=self.plan_lifecycle.value(),
                plan_matter_id=get_active_plan_matter_id(),
                period_of_validity_start=period_of_validity_start,
                approval_date=approval_date,
            )
            self.plan.geom = PlanLayer.get_active_plan().geom

            self.accept()

    def _plan_copied(self, copied_plan_id: str):
        if copied_plan_id:
            self.plan_copied.emit(copied_plan_id)
        self.accept()

    def _handle_copy_failed(self, error_message: str):
        iface.messageBar().pushCritical("", f"Kaavasuunnitelman kopiointi epäonnistui: {error_message}")
