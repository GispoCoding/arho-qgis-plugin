from __future__ import annotations

from importlib import resources
from typing import TYPE_CHECKING

from qgis.PyQt import uic
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QLineEdit,
    QSizePolicy,
    QSpacerItem,
    QTextEdit,
    QTreeWidgetItem,
)

from arho_feature_template.core.models import Plan, RegulationGroup, RegulationGroupLibrary
from arho_feature_template.gui.components.plan_regulation_group_widget import RegulationGroupWidget
from arho_feature_template.gui.components.tree_with_search_widget import TreeWithSearchWidget
from arho_feature_template.project.layers.code_layers import (
    LifeCycleStatusLayer,
    OrganisationLayer,
    PlanTypeLayer,
)

if TYPE_CHECKING:
    from qgis.PyQt.QtWidgets import QComboBox, QLineEdit, QTextEdit, QVBoxLayout, QWidget

    from arho_feature_template.gui.components.code_combobox import CodeComboBox, HierarchicalCodeComboBox

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

    plan_regulation_group_scrollarea_contents: QWidget
    plan_regulation_group_libraries_combobox: QComboBox
    regulation_groups_tree_layout: QVBoxLayout

    button_box: QDialogButtonBox

    def __init__(self, regulation_group_libraries: list[RegulationGroupLibrary], parent=None):
        super().__init__(parent)

        self.setupUi(self)

        self.plan_type_combo_box.populate_from_code_layer(PlanTypeLayer)
        self.lifecycle_status_combo_box.populate_from_code_layer(LifeCycleStatusLayer)
        self.organisation_combo_box.populate_from_code_layer(OrganisationLayer)

        self.name_line_edit.textChanged.connect(self._check_required_fields)
        self.organisation_combo_box.currentIndexChanged.connect(self._check_required_fields)
        self.plan_type_combo_box.currentIndexChanged.connect(self._check_required_fields)
        self.lifecycle_status_combo_box.currentIndexChanged.connect(self._check_required_fields)

        self.scroll_area_spacer = None
        self.regulation_groups_selection_widget = TreeWithSearchWidget()
        self.regulation_groups_tree_layout.insertWidget(2, self.regulation_groups_selection_widget)
        self.regulation_group_widgets: list[RegulationGroupWidget] = []
        for library in regulation_group_libraries:
            self.init_plan_regulation_group_library(library)

        self.regulation_groups_selection_widget.tree.itemDoubleClicked.connect(self.add_selected_plan_regulation_group)

        self.button_box.button(QDialogButtonBox.Ok).setEnabled(False)

    def _check_required_fields(self) -> None:
        ok_button = self.button_box.button(QDialogButtonBox.Ok)
        if (
            self.name_line_edit.text() != ""
            and self.plan_type_combo_box.value() is not None
            and self.organisation_combo_box.value() is not None
            and self.lifecycle_status_combo_box.value() is not None
        ):
            ok_button.setEnabled(True)
        else:
            ok_button.setEnabled(False)

    # --- COPIED FROM PLAN FEATURE FORM ---

    def _add_spacer(self):
        self.scroll_area_spacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.plan_regulation_group_scrollarea_contents.layout().addItem(self.scroll_area_spacer)

    def _remove_spacer(self):
        if self.scroll_area_spacer is not None:
            self.plan_regulation_group_scrollarea_contents.layout().removeItem(self.scroll_area_spacer)
            self.scroll_area_spacer = None

    def add_selected_plan_regulation_group(self, item: QTreeWidgetItem, column: int):
        if not item.parent():
            return
        regulation_group: RegulationGroup = item.data(column, Qt.UserRole)
        self.add_plan_regulation_group(regulation_group)

    def add_plan_regulation_group(self, regulation_group: RegulationGroup):
        regulation_group_widget = RegulationGroupWidget(regulation_group, general_regulation=True)
        regulation_group_widget.delete_signal.connect(self.remove_plan_regulation_group)
        self._remove_spacer()
        self.plan_regulation_group_scrollarea_contents.layout().addWidget(regulation_group_widget)
        self.regulation_group_widgets.append(regulation_group_widget)
        self._add_spacer()

    def remove_plan_regulation_group(self, regulation_group_widget: RegulationGroupWidget):
        self.plan_regulation_group_scrollarea_contents.layout().removeWidget(regulation_group_widget)
        self.regulation_group_widgets.remove(regulation_group_widget)
        regulation_group_widget.deleteLater()

    def init_plan_regulation_group_library(self, library: RegulationGroupLibrary):
        self.plan_regulation_group_libraries_combobox.addItem(library.name)
        for category in library.regulation_group_categories:
            category_item = self.regulation_groups_selection_widget.add_item_to_tree(category.name)
            for group_definition in category.regulation_groups:
                self.regulation_groups_selection_widget.add_item_to_tree(
                    group_definition.name, group_definition, category_item
                )

    # ---

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
            general_regulations=[reg_group_widget.into_model() for reg_group_widget in self.regulation_group_widgets],
        )
