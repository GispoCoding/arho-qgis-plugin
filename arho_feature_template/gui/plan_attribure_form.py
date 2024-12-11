from __future__ import annotations

from importlib import resources
from typing import TYPE_CHECKING

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog

from arho_feature_template.core.models import Plan
from arho_feature_template.project.layers.code_layers import (
    LifeCycleStatusLayer,
    OrganisationLayer,
    PlanTypeLayer,
)

if TYPE_CHECKING:
    from qgis.PyQt.QtWidgets import QLineEdit, QTextEdit

    from arho_feature_template.gui.code_combobox import CodeComboBox, HierarchicalCodeComboBox

ui_path = resources.files(__package__) / "plan_attribute_form.ui"
FormClass, _ = uic.loadUiType(ui_path)


class PlanAttributeForm(QDialog, FormClass):  # type: ignore
    permanent_identifier_line_edit: QLineEdit
    name_line_edit: QLineEdit
    organisation_combo_box: CodeComboBox
    description_text_edit: QTextEdit
    plan_type_combo_box: HierarchicalCodeComboBox
    lifecycle_status_combo_box: CodeComboBox
    record_number_line_edit: QLineEdit
    producers_plan_identifier_line_edit: QLineEdit
    matter_management_identifier_line_edit: QLineEdit

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setupUi(self)

        self.plan_type_combo_box.populate_from_code_layer(PlanTypeLayer)
        self.lifecycle_status_combo_box.populate_from_code_layer(LifeCycleStatusLayer)
        self.organisation_combo_box.populate_from_code_layer(OrganisationLayer)

    def get_plan_attributes(self) -> Plan:
        return Plan(
            id_=None,
            name=self.name_line_edit.text(),
            description=self.description_text_edit.toPlainText() or None,
            plan_type_id=self.plan_type_combo_box.value(),
            organisation_id=self.organisation_combo_box.value(),
            permanent_plan_identifier=self.permanent_identifier_line_edit.text() or None,
            record_number=self.record_number_line_edit.text() or None,
            producers_plan_identifier=self.producers_plan_identifier_line_edit.text() or None,
            matter_management_identifier=self.matter_management_identifier_line_edit.text() or None,
            lifecycle_status_id=self.lifecycle_status_combo_box.value(),
            general_regulations=[],
        )
