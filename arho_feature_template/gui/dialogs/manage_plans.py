from __future__ import annotations

from importlib import resources
from typing import TYPE_CHECKING

from qgis.core import QgsApplication
from qgis.PyQt import uic
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QDialog, QDialogButtonBox, QPushButton, QTableWidget, QTableWidgetItem

from arho_feature_template.core.feature_editing import save_plan
from arho_feature_template.exceptions import UnsavedChangesError
from arho_feature_template.gui.dialogs.new_plan_dialog import NewPlanDialog
from arho_feature_template.gui.dialogs.plan_attribute_form import PlanAttributeForm
from arho_feature_template.project.layers.code_layers import LifeCycleStatusLayer
from arho_feature_template.project.layers.plan_layers import PlanLayer, plan_layers
from arho_feature_template.qgis_plugin_tools.tools.resources import resources_path
from arho_feature_template.utils.localization_utils import deserialize_localized_text
from arho_feature_template.utils.misc_utils import (
    check_layer_changes,
    get_active_plan_id,
    get_active_plan_matter_id,
    iface,
    use_wait_cursor,
)

if TYPE_CHECKING:
    from qgis.gui import QgsFilterLineEdit

    from arho_feature_template.core.models import Plan

ui_path = resources.files(__package__) / "manage_plans.ui"
FormClass, _ = uic.loadUiType(ui_path)

DATA_ROLE = Qt.UserRole


class ManagePlans(QDialog, FormClass):  # type: ignore
    LOCK_ICON: QIcon = QgsApplication.getThemeIcon("locked.svg")
    UNLOCKED_ICON: QIcon = QgsApplication.getThemeIcon("unlocked.svg")

    @use_wait_cursor
    def __init__(self, regulation_group_libraries):
        super().__init__()
        self.setupUi(self)

        # TYPES
        self.new_plan_button: QPushButton
        self.filter_line: QgsFilterLineEdit
        self.plans_table: QTableWidget

        self.button_box: QDialogButtonBox

        # INIT
        self.regulation_group_libraries = regulation_group_libraries
        self.selected_plan = None
        self.plan_layer = PlanLayer.get_from_project()
        self.previously_in_edit_mode = self.plan_layer.isEditable()
        self.show_plans_in_table()
        self.plans_table.setFocus()

        self.plans_table.setColumnWidth(0, 25)

        # If no plans exist in the plan matter yet, disable new plan button and tell user
        # to make the first plan by drawing the geometry from the toolbar
        if self.plans_table.rowCount() == 0:
            self.new_plan_button.setEnabled(False)
            self.new_plan_button.setToolTip("Luo ensimmäinen kaavasuunnitelma piirtämällä tai tuomalla ulkoraja.")
            iface.messageBar().pushWarning(
                "",
                "Kaava-asialle ei ole luotu vielä yhtään kaavasuunnitelmaa. Luo ensimmäinen kaavasuunnitelma "
                " piirtämällä tai tuomalla ulkoraja.",
            )

        self.filter_line.valueChanged.connect(self._filter_plans)
        self.plans_table.itemDoubleClicked.connect(self._on_row_double_clicked)
        self.new_plan_button.clicked.connect(self._on_new_plan_button_clicked)
        self.button_box.accepted.connect(self._on_ok_clicked)
        self.button_box.rejected.connect(self._on_cancel_clicked)

        self.new_plan_button.setIcon(QgsApplication.getThemeIcon("mActionAdd.svg"))

    def show_plans_in_table(self, resize: bool = True):  # noqa: FBT001, FBT002
        self.plans_table.setRowCount(0)
        for plan in self._get_plans():
            self._add_plan_row(plan)
        if resize:
            self.plans_table.resizeColumnsToContents()

    def _get_plan_data(self, row: int) -> Plan:
        return self.plans_table.item(row, 1).data(DATA_ROLE)

    def _get_plans(self) -> list[Plan]:
        if check_layer_changes():
            raise UnsavedChangesError

        active_plan_matter_id = get_active_plan_matter_id()
        layer = PlanLayer.get_from_project()
        original_filter = layer.subsetString()
        plans = []
        try:
            # Make sure plan layer is not in edit state to set new filter
            if self.previously_in_edit_mode:
                self.plan_layer.rollBack()
            layer.setSubsetString(f"\"plan_matter_id\"='{active_plan_matter_id}'")  # set temporary filter
            plans = PlanLayer.models_from_features(list(PlanLayer.get_features()))
        finally:
            layer.setSubsetString(original_filter)  # restore filter
        return plans

    def _add_plan_row(self, plan: Plan, select: bool = False):  # noqa: FBT001, FBT002
        row = self.plans_table.rowCount()
        self.plans_table.insertRow(row)

        plan_name_item = self._set_row_attributes(row, plan)

        active_plan_id = get_active_plan_id()
        if plan.id_ == active_plan_id:
            plan_name_item.setIcon(QIcon(resources_path("icons", "green_dot.png")))
        if select or plan.id_ == active_plan_id:
            self.plans_table.selectRow(row)
        self.plans_table.setFocus()

    def _update_plan_row(self, row: int, plan: Plan):
        self._set_row_attributes(row, plan)

    def _set_row_attributes(self, row: int, plan: Plan) -> QTableWidgetItem:
        if plan.locked:
            plan_locked_item = QTableWidgetItem(self.LOCK_ICON, "Lukittu")
        else:
            plan_locked_item = QTableWidgetItem(self.UNLOCKED_ICON, "")
        self.plans_table.setItem(row, 0, plan_locked_item)

        plan_name_item = QTableWidgetItem(plan.name or "")
        plan_name_item.setData(DATA_ROLE, plan)
        self.plans_table.setItem(row, 1, plan_name_item)

        lifecycle_text = (
            deserialize_localized_text(LifeCycleStatusLayer.get_attribute_by_id("name", plan.lifecycle_status_id))
            if plan.lifecycle_status_id
            else ""
        )
        plan_lifecycle_item = QTableWidgetItem(lifecycle_text or "")
        self.plans_table.setItem(row, 2, plan_lifecycle_item)

        description_item = QTableWidgetItem(plan.description or "")
        self.plans_table.setItem(row, 3, description_item)

        return plan_name_item

    def _filter_plans(self) -> None:
        text = self.filter_line.text().lower().strip()
        for row in range(self.plans_table.rowCount()):
            match = False
            for col in range(self.plans_table.columnCount()):
                item = self.plans_table.item(row, col)
                if item and text in item.text().lower():
                    match = True
                    break
            self.plans_table.setRowHidden(row, not match)

    def _on_row_double_clicked(self, item: QTableWidgetItem):
        row = item.row()
        plan = self._get_plan_data(row)
        form = PlanAttributeForm(plan, self.regulation_group_libraries)

        active_plan_matter_id = get_active_plan_matter_id()
        original_filter = self.plan_layer.subsetString()
        if form.exec():
            try:
                edited_plan = form.model
                self.plan_layer.setSubsetString(f"\"plan_matter_id\"='{active_plan_matter_id}'")  # Set temporary filter

                # Unlock to allow edits
                self.unlock_plan_layers()

                save_plan(edited_plan)

                # If we edited the active plan, update lock status
                if edited_plan.id_ == get_active_plan_id():
                    if edited_plan.locked:
                        self.lock_plan_layers()
                    else:
                        self.unlock_plan_layers()
            finally:
                # Make sure plan layer is not in edit state to set new filter
                if self.plan_layer.isEditable():
                    self.plan_layer.rollBack()
                self.plan_layer.setSubsetString(original_filter)  # restore filter
                self._update_plan_row(row, edited_plan)

    def _on_new_plan_button_clicked(self):
        form = NewPlanDialog()
        form.plan_copied.connect(self._handle_plan_copied)
        if form.exec() and form.plan:
            new_plan: Plan = form.plan
            plan_id = save_plan(new_plan)
            if plan_id:
                new_plan.id_ = plan_id
                self._add_plan_row(new_plan, select=True)

    def _handle_plan_copied(self, copied_plan_id: str):
        if copied_plan_id:
            self.show_plans_in_table(resize=False)

            for row in range(self.plans_table.rowCount()):
                plan = self._get_plan_data(row)
                if plan.id_ == copied_plan_id:
                    self.plans_table.selectRow(row)
                    break
            self.plans_table.setFocus()

    def _restore_plan_layer_edit_state(self):
        is_now_in_edit_mode = self.plan_layer.isEditable()
        if self.previously_in_edit_mode and not is_now_in_edit_mode:
            self.plan_layer.startEditing()
        elif not self.previously_in_edit_mode and is_now_in_edit_mode:
            self.plan_layer.rollBack()

    def _on_ok_clicked(self):
        self._restore_plan_layer_edit_state()
        row = self.plans_table.currentRow()
        self.selected_plan = self._get_plan_data(row)
        self.accept()

    def _on_cancel_clicked(self):
        self._restore_plan_layer_edit_state()
        self.reject()

    # DUPLICATED FROM PLAN MANAGER
    def lock_plan_layers(self):
        for layer in plan_layers:
            vlayer = layer.get_from_project()
            vlayer.rollBack()
            vlayer.setReadOnly(True)

    def unlock_plan_layers(self):
        for layer in plan_layers:
            layer.get_from_project().setReadOnly(False)

        PlanLayer.get_from_project().startEditing()
