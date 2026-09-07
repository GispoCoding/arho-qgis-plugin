from __future__ import annotations

import enum
from importlib import resources
from string import Template
from typing import TYPE_CHECKING

from qgis.PyQt import uic
from qgis.PyQt.QtCore import QDate, QDateTime, Qt, pyqtSignal
from qgis.PyQt.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QLineEdit,
    QWidget,
)

from arho_feature_template.core.lambda_service import LambdaService
from arho_feature_template.core.lifecycles import LifeCycleStatusValue, get_allowed_plan_lifecycle_transitions
from arho_feature_template.core.models import Plan
from arho_feature_template.gui.components.code_combobox import ValueDataRole
from arho_feature_template.project.layers.code_layers import (
    LifeCycleStatusLayer,
)
from arho_feature_template.project.layers.plan_layers import PlanLayer, PlanMatterLayer
from arho_feature_template.utils.localization_utils import get_localized_text
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

DATA_ROLE = Qt.ItemDataRole.UserRole
LIFECYCLE_STATUS_DATA_ROLE = Qt.ItemDataRole.UserRole + 1


class UnderAppealScopeOption(enum.Enum):
    SUBSET_OF_PLAN = "subset_of_plan"
    WHOLE_PLAN = "whole_plan"
    PARTIALLY_VALID = "partially_valid"


UNDER_APPEAL_SCOPE_LABELS = {
    UnderAppealScopeOption.SUBSET_OF_PLAN: "Koskee vain osaa kaavasta",
    UnderAppealScopeOption.WHOLE_PLAN: "Koskee koko kaavaa",
    UnderAppealScopeOption.PARTIALLY_VALID: "Aseta kaava osittain voimaan",
}
UNDER_APPEAL_SCOPE_DESCRIPTIONS = {
    UnderAppealScopeOption.SUBSET_OF_PLAN: Template(
        "Kaavasuunnitelman kaavakohteet, -määräykset ja suositukset jätetään \n"
        "elinkaaren tilaan $lifecycle.\n"
        "Avaa kaavasuunnitelma ja päivitä tarvittavien kohteiden elinkaaren tila."
    ),
    UnderAppealScopeOption.WHOLE_PLAN: Template(
        "Kaavasuunnitelman kaavakohteet, -määräykset ja suositukset asetetaan \n" "elinkaaren tilaan $lifecycle."
    ),
    UnderAppealScopeOption.PARTIALLY_VALID: Template(
        "Kaavasuunnitelman kaavakohteet, -määräykset ja suositukset asetetaan \n"
        "elinkaaren tilaan $lifecycle.\n"
        "Avaa kaavasuunnitelma ja päivitä tarvittavien kohteiden elinkaaren tila."
    ),
}


class NewPlanDialog(QDialog, FormClass):  # type: ignore
    widget_input: QWidget
    plan_name: QLineEdit
    source_plan: QComboBox
    label_source_plan: QLabel
    check_box_deep_copy: QCheckBox
    plan_target_lifecycle: CodeComboBox
    label_plan_target_lifecycle: QLabel
    check_box_show_allowed_transitions_only: QCheckBox
    label_under_appeal_scope: QLabel
    combo_box_under_appeal_scope: QComboBox
    label_under_appeal_scope_description: QLabel
    check_box_keep_under_appeal_lifecycle: QCheckBox
    label_validity_start_date: QLabel
    validity_start_date: QgsDateTimeEdit
    label_approval_date: QLabel
    approval_date: QgsDateTimeEdit
    check_box_lock: QCheckBox
    button_box: QDialogButtonBox
    widget_progress: QWidget

    widget_under_appeal_scope: QWidget
    widget_target_lifecycle: QWidget

    plan_copied = pyqtSignal(str)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setupUi(self)
        self.setModal(True)
        # self.setFixedWidth(550)
        self.widget_progress.hide()
        self.adjustSize()

        # INIT
        self.plan = None
        self.plan_layer = PlanLayer.get_from_project()
        self.previously_in_edit_mode = self.plan_layer.isEditable()

        self._populate_plan_combobox()
        self.plan_target_lifecycle.populate_from_code_layer(LifeCycleStatusLayer)
        self._update_allowed_plan_lifecycles()
        self._add_lifecycle_status_data_to_target_lifecycle_combobox()
        self._populate_combo_box_under_appeal_scope()
        self.plan_name.textChanged.connect(self._check_required_fields)
        self.plan_target_lifecycle.currentIndexChanged.connect(self._check_required_fields)
        self.check_box_deep_copy.stateChanged.connect(self._check_required_fields)
        self.approval_date.valueChanged.connect(self._check_required_fields)
        self.validity_start_date.valueChanged.connect(self._check_required_fields)
        self.button_box.accepted.connect(self._on_ok_clicked)

        self.source_plan.currentIndexChanged.connect(self._on_source_plan_changed)
        self.check_box_show_allowed_transitions_only.stateChanged.connect(self._on_show_allowed_transitions_changed)

        self.lambda_service = LambdaService()
        self.lambda_service.plan_copied.connect(self._plan_copied)
        self.lambda_service.plan_copy_failed.connect(self._handle_copy_failed)

        # Start date widget initially invisible
        self.label_validity_start_date.setVisible(False)
        self.validity_start_date.setVisible(False)
        self.label_approval_date.setVisible(False)
        self.approval_date.setVisible(False)

        # Set dates as today initially
        self.validity_start_date.setDateTime(QDateTime(QDate.currentDate()))
        self.approval_date.setDateTime(QDateTime(QDate.currentDate()))

        # Show/hide start date based on lifecycle stage
        self._on_plan_lifecycle_changed(self.plan_target_lifecycle.currentIndex())
        self.plan_target_lifecycle.currentIndexChanged.connect(self._on_plan_lifecycle_changed)

        self.combo_box_under_appeal_scope.currentIndexChanged.connect(self._on_combo_box_under_appeal_scope_changed)

        self.check_box_deep_copy.stateChanged.connect(self._on_check_box_deep_copy_changed)

        self._check_required_fields()

    def _on_check_box_deep_copy_changed(self, state: int):  # noqa: ARG002
        self._set_validity_date_visibility()
        self._set_approval_date_visibility()
        self._set_under_appeal_scope_visibility()
        self._set_keep_under_appeal_lifecycle_visibility()
        self._set_target_lifecycle_visibility()

    def _update_under_appeal_scope_description(self, scope: UnderAppealScopeOption) -> None:
        description_template = UNDER_APPEAL_SCOPE_DESCRIPTIONS.get(scope)
        if description_template:
            if scope == UnderAppealScopeOption.PARTIALLY_VALID:
                if PlanMatterLayer.is_regional_plan(get_active_plan_matter_id()):
                    lifecycle_value = LifeCycleStatusValue.VALID_BEFORE_LEGAL_VALIDITY
                else:
                    lifecycle_value = LifeCycleStatusValue.VALID
            elif scope == UnderAppealScopeOption.WHOLE_PLAN:
                lifecycle_value = self.plan_target_lifecycle.currentData(ValueDataRole)
            elif scope == UnderAppealScopeOption.SUBSET_OF_PLAN:
                lifecycle_value = LifeCycleStatusValue.APPORVED
            else:
                self.label_under_appeal_scope_description.setText("")
                return

            lifecycle_name = get_localized_text(
                LifeCycleStatusLayer.get_name_from_lifecycle_status_value(lifecycle_value)
            )
            self.label_under_appeal_scope_description.setText(description_template.substitute(lifecycle=lifecycle_name))

    def _set_keep_under_appeal_lifecycle_visibility(self):
        visible = (
            LifeCycleStatusLayer.is_under_appeal(self._get_source_plan_lifecycle())
            and self.plan_target_lifecycle.currentData(ValueDataRole)
            in {
                LifeCycleStatusValue.LEGALLY_VALID,
                LifeCycleStatusValue.VALID,
            }
            and not self.check_box_deep_copy.isChecked()
        )
        self.check_box_keep_under_appeal_lifecycle.setVisible(visible)

    def _on_combo_box_under_appeal_scope_changed(self, index: int):
        self._set_validity_date_visibility()
        scope = self.combo_box_under_appeal_scope.itemData(index)
        self._update_under_appeal_scope_description(scope)

    def _populate_combo_box_under_appeal_scope(self):
        for under_appeal_scope_option in UnderAppealScopeOption:
            self.combo_box_under_appeal_scope.addItem(
                UNDER_APPEAL_SCOPE_LABELS[under_appeal_scope_option], under_appeal_scope_option
            )

    def _add_lifecycle_status_data_to_target_lifecycle_combobox(self):
        for i in range(self.plan_target_lifecycle.model().rowCount()):
            lifecycle_value = self.plan_target_lifecycle.itemData(i, ValueDataRole)
            if lifecycle_value is not None:
                lifecycle_status = LifeCycleStatusValue(lifecycle_value)
                self.plan_target_lifecycle.setItemData(i, lifecycle_status, LIFECYCLE_STATUS_DATA_ROLE)

    def _populate_plan_combobox(self):
        active_plan_id = get_active_plan_id()
        selected_index = None
        self.source_plan.addItem("NULL", None)
        for index, plan in enumerate(PlanLayer.get_plans_for_active_plan_matter(), start=1):
            lifecycle_status = LifeCycleStatusLayer.get_lifecycle_status_by_id(plan.lifecycle_status_id)
            lifecycle_name = get_localized_text(LifeCycleStatusLayer.get_name_by_id(plan.lifecycle_status_id))
            self.source_plan.addItem(f"{plan.name} - {lifecycle_name}", plan.id_)
            self.source_plan.setItemData(index, lifecycle_status, LIFECYCLE_STATUS_DATA_ROLE)
            if plan.id_ == active_plan_id:
                selected_index = index

        if selected_index is not None:
            self.source_plan.setCurrentIndex(selected_index)

    def _check_required_fields(self) -> None:
        ok_button = self.button_box.button(QDialogButtonBox.StandardButton.Ok)

        # Required: plan name + lifecycle
        required_fields_filled = self.plan_name.text() != "" and (
            self.check_box_deep_copy.isChecked()
            or (
                self.plan_target_lifecycle.value() is not None
                and ((not self.validity_start_date.isVisible()) or self.validity_start_date.date().isValid())
                and ((not self.approval_date.isVisible()) or self.approval_date.date().isValid())
            )
        )

        ok_button.setEnabled(required_fields_filled)

    def _set_deep_copy_visibility(self):
        visible = self.source_plan.currentData(DATA_ROLE) is not None
        self.check_box_deep_copy.setVisible(visible)

    def _set_target_lifecycle_visibility(self):
        visible = not self.check_box_deep_copy.isChecked()
        self.label_plan_target_lifecycle.setVisible(visible)
        self.widget_target_lifecycle.setVisible(visible)

        self.check_box_show_allowed_transitions_only.setVisible(self.source_plan.currentData(DATA_ROLE) is not None)

    def _set_under_appeal_scope_visibility(self):
        visible = (
            LifeCycleStatusLayer.is_under_appeal(self.plan_target_lifecycle.currentData(ValueDataRole))
            and not self.check_box_deep_copy.isChecked()
        )

        self.label_under_appeal_scope.setVisible(visible)
        self.widget_under_appeal_scope.setVisible(visible)

    def _set_validity_date_visibility(self):
        visible = not self.check_box_deep_copy.isChecked() and (
            self.plan_target_lifecycle.currentData(ValueDataRole) == LifeCycleStatusValue.VALID
            or (
                LifeCycleStatusLayer.is_under_appeal(self.plan_target_lifecycle.currentData(ValueDataRole))
                and self.combo_box_under_appeal_scope.currentData() == UnderAppealScopeOption.PARTIALLY_VALID
            )
        )
        self.label_validity_start_date.setVisible(visible)
        self.validity_start_date.setVisible(visible)

    def _set_approval_date_visibility(self):
        visible = (
            self.plan_target_lifecycle.currentData(ValueDataRole) == LifeCycleStatusValue.APPORVED
            and not self.check_box_deep_copy.isChecked()
        )
        self.label_approval_date.setVisible(visible)
        self.approval_date.setVisible(visible)

    def _on_plan_lifecycle_changed(self, index: int):  # noqa: ARG002
        self._set_validity_date_visibility()
        self._set_approval_date_visibility()
        self._set_under_appeal_scope_visibility()
        self._set_keep_under_appeal_lifecycle_visibility()

        self._on_combo_box_under_appeal_scope_changed(self.combo_box_under_appeal_scope.currentIndex())

    def _on_show_allowed_transitions_changed(self, state: int):  # noqa: ARG002
        self._update_allowed_plan_lifecycles()

    def _get_source_plan_lifecycle(self) -> LifeCycleStatusValue | None:
        source_lifecycle: LifeCycleStatusValue | None = self.source_plan.currentData(LIFECYCLE_STATUS_DATA_ROLE)
        return source_lifecycle

    def _update_allowed_plan_lifecycles(self) -> None:
        source_lifecycle = self._get_source_plan_lifecycle()
        if source_lifecycle is None:
            allowed_lifecycle_values = set(LifeCycleStatusValue)
        else:
            allowed_lifecycle_values = set(get_allowed_plan_lifecycle_transitions(source_lifecycle))
        view = self.plan_target_lifecycle.view()
        model = self.plan_target_lifecycle.model()

        for row_num in range(model.rowCount()):
            item_lifecycle = self.plan_target_lifecycle.itemData(row_num, ValueDataRole)
            if item_lifecycle is None:
                continue
            item = model.item(row_num)
            lifecycle_is_allowed = item_lifecycle in allowed_lifecycle_values
            if (
                self.check_box_show_allowed_transitions_only.checkState() == Qt.CheckState.Checked
                and not lifecycle_is_allowed
            ):
                view.setRowHidden(row_num, True)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEnabled)
            else:
                view.setRowHidden(row_num, False)
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEnabled)

    def _on_source_plan_changed(self, index: int):  # noqa: ARG002
        self._update_allowed_plan_lifecycles()
        self._set_keep_under_appeal_lifecycle_visibility()
        self._set_deep_copy_visibility()
        self._set_target_lifecycle_visibility()

    def _get_keep_under_appeal_lifecycle(self) -> bool | None:
        return (
            self.check_box_keep_under_appeal_lifecycle.isChecked()
            if self.check_box_keep_under_appeal_lifecycle.isVisible()
            else None
        )

    def _on_ok_clicked(self):
        plan_id = self.source_plan.currentData(DATA_ROLE)

        period_of_validity_start = self.validity_start_date.date() if self.validity_start_date.isVisible() else None
        approval_date = self.approval_date.date() if self.approval_date.isVisible() else None
        keep_under_appeal_lifecycle = self._get_keep_under_appeal_lifecycle()
        if plan_id is not None:
            self.widget_input.hide()
            self.widget_progress.show()
            self.adjustSize()

            self.lambda_service.copy_plan(
                plan_id,
                self.plan_target_lifecycle.value(),
                self.plan_name.text(),
                under_appeal_scope=self.combo_box_under_appeal_scope.currentData(),
                keep_under_appeal_lifecycle=keep_under_appeal_lifecycle,
                deep_copy=self.check_box_deep_copy.isChecked(),
                period_of_validity_start=period_of_validity_start,
                approval_date=approval_date,
                lock=self.check_box_lock.isChecked(),
            )
        else:
            self.plan = Plan(
                name=self.plan_name.text(),
                lifecycle_status_id=self.plan_target_lifecycle.value(),
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
