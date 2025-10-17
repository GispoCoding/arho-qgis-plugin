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
from arho_feature_template.project.layers.plan_layers import PlanLayer
from arho_feature_template.qgis_plugin_tools.tools.resources import resources_path
from arho_feature_template.utils.misc_utils import (
    check_layer_changes,
    deserialize_localized_text,
    get_active_plan_id,
    get_active_plan_matter_id,
    iface,
)

if TYPE_CHECKING:
    from qgis.gui import QgsFilterLineEdit

    from arho_feature_template.core.models import Plan

ui_path = resources.files(__package__) / "manage_plans.ui"
FormClass, _ = uic.loadUiType(ui_path)

DATA_ROLE = Qt.UserRole


class ManagePlans(QDialog, FormClass):  # type: ignore
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

    def show_plans_in_table(self):
        self.plans_table.setRowCount(0)
        for plan in self._get_plans():
            self._add_plan_row(plan)
        self.plans_table.resizeColumnsToContents()

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

    def _add_plan_row(self, plan: Plan):
        row = self.plans_table.rowCount()
        self.plans_table.insertRow(row)

        plan_name_item = QTableWidgetItem(plan.name or "")
        plan_name_item.setData(DATA_ROLE, plan)
        self.plans_table.setItem(row, 0, plan_name_item)

        lifecycle_text = (
            deserialize_localized_text(LifeCycleStatusLayer.get_attribute_by_id("name", plan.lifecycle_status_id))
            if plan.lifecycle_status_id
            else ""
        )
        plan_lifecycle_item = QTableWidgetItem(lifecycle_text or "")
        self.plans_table.setItem(row, 1, plan_lifecycle_item)

        description_item = QTableWidgetItem(plan.description or "")
        self.plans_table.setItem(row, 2, description_item)

        # If plan is currently active one
        if plan.id_ == get_active_plan_id():
            # Select row
            self.plans_table.selectRow(row)
            # Set icon
            plan_name_item.setIcon(QIcon(resources_path("icons", "green_dot.png")))

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
        plan = self.plans_table.item(row, 0).data(DATA_ROLE)
        form = PlanAttributeForm(plan, self.regulation_group_libraries)
        if form.exec():
            save_plan(form.model)

    def _on_new_plan_button_clicked(self):
        form = NewPlanDialog()
        if form.exec():
            new_plan: Plan = form.plan
            plan_id = save_plan(new_plan)
            if plan_id:
                new_plan.id_ = plan_id
                self._add_plan_row(new_plan)

    def _restore_plan_layer_edit_state(self):
        is_now_in_edit_mode = self.plan_layer.isEditable()
        if self.previously_in_edit_mode and not is_now_in_edit_mode:
            self.plan_layer.startEditing()
        elif not self.previously_in_edit_mode and is_now_in_edit_mode:
            self.plan_layer.rollBack()

    def _on_ok_clicked(self):
        self._restore_plan_layer_edit_state()
        row = self.plans_table.currentRow()
        self.selected_plan = self.plans_table.item(row, 0).data(DATA_ROLE)
        self.accept()

    def _on_cancel_clicked(self):
        self._restore_plan_layer_edit_state()
        self.reject()
