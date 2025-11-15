from __future__ import annotations

from importlib import resources
from typing import TYPE_CHECKING, cast

from qgis.core import QgsApplication
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog, QDialogButtonBox, QLabel, QLineEdit, QPushButton, QSpinBox, QTextEdit

from arho_feature_template.core.models import Document, Plan, RegulationGroup, RegulationGroupLibrary
from arho_feature_template.gui.components.general_regulation_group_widget import GeneralRegulationGroupWidget

# from arho_feature_template.gui.components.plan_regulation_group_widget import RegulationGroupWidget
from arho_feature_template.gui.components.plan_document_widget import DocumentWidget
from arho_feature_template.gui.components.value_input_widgets import LegalEffectWidget
from arho_feature_template.project.layers.code_layers import (
    LifeCycleStatusLayer,
    PlanTypeLayer,
)
from arho_feature_template.project.layers.plan_layers import PlanLayer, PlanMatterLayer
from arho_feature_template.utils.misc_utils import disconnect_signal, get_active_plan_matter_id

if TYPE_CHECKING:
    from qgis.PyQt.QtWidgets import QFormLayout, QLineEdit, QTextEdit, QVBoxLayout

    from arho_feature_template.gui.components.code_combobox import CodeComboBox

ui_path = resources.files(__package__) / "plan_attribute_form.ui"
FormClass, _ = uic.loadUiType(ui_path)


class PlanAttributeForm(QDialog, FormClass):  # type: ignore
    name_line_edit: QLineEdit
    description_text_edit: QTextEdit
    scale_spin_box: QSpinBox
    lifecycle_status_combo_box: CodeComboBox
    regulations_layout: QVBoxLayout
    add_general_regulation_group_btn: QPushButton
    documents_layout: QVBoxLayout
    add_document_btn: QPushButton

    button_box: QDialogButtonBox

    def __init__(self, tr, plan: Plan, _regulation_group_libraries: list[RegulationGroupLibrary], parent=None):
        super().__init__(parent)
        self.tr = tr
        self.setupUi(self)

        self.is_general_plan_type = self._is_general_plan_type()

        self.general_data_layout: QFormLayout

        self.plan = plan

        self.lifecycle_status_combo_box.populate_from_code_layer(LifeCycleStatusLayer)

        self.lifecycle_status_combo_box.set_value(plan.lifecycle_status_id)
        self.scale_spin_box.setValue(plan.scale if plan.scale else 0)
        self.name_line_edit.setText(plan.name if plan.name else "")
        self.description_text_edit.setText(plan.description if plan.description else "")

        self.name_line_edit.textChanged.connect(self._check_required_fields)
        self.lifecycle_status_combo_box.currentIndexChanged.connect(self._check_required_fields)

        self.scroll_area_spacer = None
        self.regulation_group_widgets: list[GeneralRegulationGroupWidget] = []
        self.legal_effect_widgets: list[tuple[QLabel, LegalEffectWidget]] = []
        # self.regulation_groups_selection_widget = TreeWithSearchWidget()
        # self.regulation_groups_tree_layout.insertWidget(2, self.regulation_groups_selection_widget)
        # for library in regulation_group_libraries:
        #     self.init_plan_regulation_group_library(library)
        # self.regulation_groups_selection_widget.tree.itemDoubleClicked.connect(self.add_selected_plan_regulation_group)

        for regulation_group in plan.general_regulations:
            self.add_plan_regulation_group(regulation_group)

        # Documents
        self.document_widgets: list[DocumentWidget] = []
        for document in plan.documents:
            self.add_document(document)

        # Legal effects
        for legal_effect_id in plan.legal_effect_ids:
            self.add_legal_effect_widget(legal_effect_id)
        if len(self.legal_effect_widgets) == 0:
            self.add_legal_effect_widget()

        self.add_general_regulation_group_btn.clicked.connect(self.add_new_regulation_group)
        self.add_general_regulation_group_btn.setIcon(QgsApplication.getThemeIcon("mActionAdd.svg"))

        self.add_document_btn.clicked.connect(self.add_new_document)
        self.add_document_btn.setIcon(QgsApplication.getThemeIcon("mActionAdd.svg"))

        self.button_box.button(QDialogButtonBox.Ok).setEnabled(False)
        self.button_box.accepted.connect(self._on_ok_clicked)

        self._check_required_fields()
        self._update_legal_effect_widgets_visibility()

    def _check_required_fields(self) -> None:
        ok_button = self.button_box.button(QDialogButtonBox.Ok)
        if (
            self.name_line_edit.text() != ""
            and self.lifecycle_status_combo_box.value() is not None
            and all(document_widget.is_ok() for document_widget in self.document_widgets)
        ):
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

    # --- COPIED FROM PLAN FEATURE FORM ---

    # def add_selected_plan_regulation_group(self, item: QTreeWidgetItem, column: int):
    #     if not item.parent():
    #         return
    #     regulation_group: RegulationGroup = item.data(column, Qt.UserRole)
    #     self.add_plan_regulation_group(regulation_group)

    def add_new_regulation_group(self):
        self.add_plan_regulation_group(RegulationGroup())

    def add_plan_regulation_group(self, regulation_group: RegulationGroup):
        regulation_group_widget = GeneralRegulationGroupWidget(self.tr, regulation_group, layer_name=PlanLayer.name)
        regulation_group_widget.delete_signal.connect(self.remove_plan_regulation_group)
        # regulation_group_widget.open_as_form_signal.connect(self.open_plan_regulation_group_form)
        self.regulations_layout.insertWidget(1, regulation_group_widget)
        self.regulation_group_widgets.append(regulation_group_widget)

    # def open_plan_regulation_group_form(self, regulation_group_widget: GeneralRegulationGroupWidget):
    #     group_as_form = PlanRegulationGroupForm(self.tr, regulation_group_widget.into_model())
    #     if group_as_form.exec_():
    #         regulation_group_widget.from_model(group_as_form.model)

    def remove_plan_regulation_group(self, regulation_group_widget: GeneralRegulationGroupWidget):
        disconnect_signal(regulation_group_widget.delete_signal)
        # disconnect_signal(regulation_group_widget.open_as_form_signal)
        self.regulations_layout.removeWidget(regulation_group_widget)
        self.regulation_group_widgets.remove(regulation_group_widget)
        regulation_group_widget.deleteLater()

    # def init_plan_regulation_group_library(self, library: RegulationGroupLibrary):
    #     self.plan_regulation_group_libraries_combobox.addItem(library.name)
    #     for category in library.regulation_group_categories:
    #         category_item = self.regulation_groups_selection_widget.add_item_to_tree(category.name)
    #         for group_definition in category.regulation_groups:
    #             self.regulation_groups_selection_widget.add_item_to_tree(
    #                 group_definition.name, group_definition, category_item
    #             )

    def add_new_document(self):
        self.add_document(Document())
        self._check_required_fields()

    def add_document(self, document: Document):
        widget = DocumentWidget(document)
        widget.delete_signal.connect(self.delete_document)
        widget.document_edited.connect(self._check_required_fields)
        self.documents_layout.insertWidget(1, widget)
        self.document_widgets.append(widget)

    def delete_document(self, document_widget: DocumentWidget):
        document_widget.delete_signal.disconnect()
        document_widget.document_edited.disconnect()
        self.documents_layout.removeWidget(document_widget)
        self.document_widgets.remove(document_widget)
        document_widget.deleteLater()
        self._check_required_fields()

    # ---

    def into_model(self) -> Plan:
        if self.is_general_plan_type:
            legal_effect_ids = [legal_effect_widget[1].get_value() for legal_effect_widget in self.legal_effect_widgets]
        else:
            legal_effect_ids = []

        model = Plan(
            id_=self.plan.id_,
            name=self.name_line_edit.text(),
            description=self.description_text_edit.toPlainText() or None,
            scale=self.scale_spin_box.value() or None,
            lifecycle_status_id=self.lifecycle_status_combo_box.value(),
            general_regulations=[reg_group_widget.into_model() for reg_group_widget in self.regulation_group_widgets],
            legal_effect_ids=[value for value in legal_effect_ids if value is not None],
            documents=[document_widget.into_model() for document_widget in self.document_widgets],
            modified=self.plan.modified,
            plan_matter_id=self.plan.plan_matter_id,
            geom=self.plan.geom,
        )
        if not model.modified and model != self.plan:
            model.modified = True

        return model

    def _on_ok_clicked(self):
        self.model = self.into_model()
        self.accept()
