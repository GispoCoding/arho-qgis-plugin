from __future__ import annotations

from importlib import resources
from typing import TYPE_CHECKING

from qgis.PyQt import uic
from qgis.PyQt.QtCore import Qt, pyqtSignal
from qgis.PyQt.QtWidgets import QComboBox, QDialog, QDialogButtonBox, QLineEdit, QWidget

from arho_feature_template.core.lambda_service import LambdaService
from arho_feature_template.core.models import Plan
from arho_feature_template.exceptions import UnsavedChangesError
from arho_feature_template.project.layers.code_layers import LifeCycleStatusLayer
from arho_feature_template.project.layers.plan_layers import PlanLayer
from arho_feature_template.qgis_plugin_tools.tools.i18n import tr
from arho_feature_template.utils.misc_utils import (
    check_layer_changes,
    get_active_plan_id,
    get_active_plan_matter_id,
    iface,
)

if TYPE_CHECKING:
    from arho_feature_template.gui.components.code_combobox import CodeComboBox

ui_path = resources.files(__package__) / "new_plan_dialog.ui"
FormClass, _ = uic.loadUiType(ui_path)

DATA_ROLE = Qt.UserRole


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

        self._check_required_fields()

    def populate_plan_combobox(self):
        active_plan_id = get_active_plan_id()
        selected_index = None
        self.source_plan.addItem("NULL")
        for index, plan in enumerate(self._get_plans(), start=1):
            self.source_plan.addItem(plan.name, plan.id_)
            if plan.id_ == active_plan_id:
                selected_index = index

        if selected_index is not None:
            self.source_plan.setCurrentIndex(selected_index)

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

    def _check_required_fields(self) -> None:
        ok_button = self.button_box.button(QDialogButtonBox.Ok)
        if self.plan_name.text() != "" and self.plan_lifecycle.value() is not None:
            ok_button.setEnabled(True)
        else:
            ok_button.setEnabled(False)

    def _on_ok_clicked(self):
        plan_id = self.source_plan.currentData(DATA_ROLE)
        if plan_id is not None:
            self.widget_input.hide()
            self.widget_progress.show()
            self.adjustSize()

            self.lambda_service.copy_plan(plan_id, self.plan_lifecycle.value(), self.plan_name.text())
        else:
            self.plan = Plan(
                name=self.plan_name.text(),
                lifecycle_status_id=self.plan_lifecycle.value(),
                plan_matter_id=get_active_plan_matter_id(),
            )
            self.plan.geom = PlanLayer.get_active_plan().geom  # Always copy geometry from active plan for now
            # TODO: Copy details and child ojbect details from selected version

            self.accept()

    def _plan_copied(self, copied_plan_id: str):
        if copied_plan_id:
            self.plan_copied.emit(copied_plan_id)
        self.accept()

    def _handle_copy_failed(self, error_message: str):
        iface.messageBar().pushCritical("", tr("Kaavasuunnitelman kopiointi epäonnistui:") + f" {error_message}")
