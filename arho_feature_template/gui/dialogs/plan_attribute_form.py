from __future__ import annotations

from importlib import resources
from typing import TYPE_CHECKING, cast

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QTextEdit,
)

from arho_feature_template.core.models import Plan
from arho_feature_template.gui.components.value_input_widgets import LegalEffectWidget
from arho_feature_template.project.layers.code_layers import (
    LifeCycleStatusLayer,
    PlanTypeLayer,
)
from arho_feature_template.project.layers.plan_layers import PlanMatterLayer
from arho_feature_template.utils.misc_utils import date_as_str, get_active_plan_matter_id

if TYPE_CHECKING:
    from qgis.PyQt.QtWidgets import QFormLayout, QLineEdit, QTextEdit

    from arho_feature_template.gui.components.code_combobox import CodeComboBox

ui_path = resources.files(__package__) / "plan_attribute_form.ui"
FormClass, _ = uic.loadUiType(ui_path)


class PlanAttributeForm(QDialog, FormClass):  # type: ignore
    name_edit: QLineEdit
    description_text_edit: QTextEdit
    scale_spin_box: QSpinBox
    lifecycle_status_combo_box: CodeComboBox
    approved_date_label: QLabel
    approved_date: QLineEdit
    validity_start_label: QLabel
    validity_start_date: QLineEdit
    validity_end_label: QLabel
    validity_end_date: QLineEdit
    lock_checkbox: QCheckBox
    button_box: QDialogButtonBox
    general_data_layout: QFormLayout

    def __init__(self, plan: Plan, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        # INIT
        self.plan = plan
        self.is_general_plan_type = self._is_general_plan_type()

        self.lifecycle_status_combo_box.populate_from_code_layer(LifeCycleStatusLayer)
        self.lifecycle_status_combo_box.set_value(plan.lifecycle_status_id)
        self.scale_spin_box.setValue(plan.scale if plan.scale else 0)
        self.name_edit.setText(plan.name or "")
        self.description_text_edit.setText(plan.description if plan.description else "")
        self.lock_checkbox.setChecked(plan.locked)

        self.name_edit.textChanged.connect(self._check_required_fields)
        self.lifecycle_status_combo_box.currentIndexChanged.connect(self._check_required_fields)

        self.scroll_area_spacer = None
        self.legal_effect_widgets: list[tuple[QLabel, LegalEffectWidget]] = []

        # Legal effects
        for legal_effect_id in plan.legal_effect_ids:
            self.add_legal_effect_widget(legal_effect_id)
        if len(self.legal_effect_widgets) == 0:
            self.add_legal_effect_widget()

        # Approval
        if plan.approval_date:
            self.approved_date.setText(date_as_str(plan.approval_date))
        else:
            self.general_data_layout.removeRow(self.approved_date_label)

        # Validity start
        if plan.period_of_validity_start:
            self.validity_start_date.setText(date_as_str(plan.period_of_validity_start))
        else:
            self.general_data_layout.removeRow(self.validity_start_label)

        # Validity end
        if plan.period_of_validity_end:
            self.validity_end_date.setText(date_as_str(plan.period_of_validity_end))
        else:
            self.general_data_layout.removeRow(self.validity_end_label)

        self.button_box.button(QDialogButtonBox.Ok).setEnabled(False)
        self.button_box.accepted.connect(self._on_ok_clicked)

        self._check_required_fields()
        self._update_legal_effect_widgets_visibility()

    def _check_required_fields(self) -> None:
        ok_button = self.button_box.button(QDialogButtonBox.Ok)
        if self.name_edit.text() != "" and self.lifecycle_status_combo_box.value() is not None:
            ok_button.setEnabled(True)
        else:
            ok_button.setEnabled(False)

    def _is_general_plan_type(self):
        active_plan_matter_id = get_active_plan_matter_id()
        plan_type_id = PlanMatterLayer.get_attribute_value_by_another_attribute_value(
            "plan_type_id", "id", active_plan_matter_id
        )
        return PlanTypeLayer.is_general_plan_type(plan_type_id)

    def _update_legal_effect_widgets_visibility(self):
        if self.is_general_plan_type:
            self._show_legal_effect_widgets()
        else:
            self._hide_legal_effect_widgets()

    def _show_legal_effect_widgets(self):
        for label, widget in self.legal_effect_widgets:
            label.show()
            widget.show()

    def _hide_legal_effect_widgets(self):
        for label, widget in self.legal_effect_widgets:
            label.hide()
            widget.hide()

    def add_legal_effect_widget(self, legal_effect_id: str | None = None):
        """
        Adds a legal effect widget to the form.

        If no legal widgets exist yet, includes an "add" button, otherwise a
        "delete" button.
        """
        if len(self.legal_effect_widgets) == 0:
            widget = LegalEffectWidget(with_add_btn=True)
            btn = cast(QPushButton, widget.add_btn)
            btn.clicked.connect(self.add_legal_effect_widget)
        else:
            widget = LegalEffectWidget(with_del_btn=True)
            btn = cast(QPushButton, widget.del_btn)
            btn.clicked.connect(lambda: self.delete_legal_effect_widget(widget))

        if legal_effect_id:
            widget.set_value(legal_effect_id)

        label = QLabel("Oikeusvaikutus:")
        self.legal_effect_widgets.append((label, widget))
        self.general_data_layout.addRow(label, widget)

    def delete_legal_effect_widget(self, widget_to_delete: LegalEffectWidget):
        for i, (label, widget) in enumerate(self.legal_effect_widgets):
            if widget is widget_to_delete:
                self.legal_effect_widgets.pop(i)
                widget.deleteLater()
                label.deleteLater()

    def into_model(self) -> Plan:
        if self.is_general_plan_type:
            legal_effect_ids = [legal_effect_widget[1].get_value() for legal_effect_widget in self.legal_effect_widgets]
        else:
            legal_effect_ids = []

        model = Plan(
            id_=self.plan.id_,
            name=self.name_edit.text(),
            description=self.description_text_edit.toPlainText() or None,
            scale=self.scale_spin_box.value() or None,
            lifecycle_status_id=self.lifecycle_status_combo_box.value(),
            general_regulations=self.plan.general_regulations,
            legal_effect_ids=[value for value in legal_effect_ids if value is not None],
            documents=self.plan.documents,
            modified=self.plan.modified,
            plan_matter_id=self.plan.plan_matter_id,
            approval_date=self.plan.approval_date,
            period_of_validity_start=self.plan.period_of_validity_start,
            period_of_validity_end=self.plan.period_of_validity_end,
            geom=self.plan.geom,
            locked=self.lock_checkbox.isChecked(),
        )
        if not model.modified and model != self.plan:
            model.modified = True

        return model

    def _on_ok_clicked(self):
        self.model = self.into_model()
        self.accept()
