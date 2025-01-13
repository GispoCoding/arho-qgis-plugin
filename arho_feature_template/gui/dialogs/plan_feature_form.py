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
    QScrollArea,
    QSizePolicy,
    QSpacerItem,
    QTextEdit,
    QTreeWidget,
    QTreeWidgetItem,
)

from arho_feature_template.core.models import PlanFeature, RegulationGroup
from arho_feature_template.gui.components.plan_regulation_group_widget import RegulationGroupWidget
from arho_feature_template.gui.components.tree_with_search_widget import TreeWithSearchWidget
from arho_feature_template.project.layers.code_layers import UndergroundTypeLayer

if TYPE_CHECKING:
    from qgis.PyQt.QtWidgets import QVBoxLayout, QWidget

    from arho_feature_template.core.models import RegulationGroupLibrary
    from arho_feature_template.gui.components.code_combobox import CodeComboBox

ui_path = resources.files(__package__) / "plan_feature_form.ui"
FormClass, _ = uic.loadUiType(ui_path)


class PlanFeatureForm(QDialog, FormClass):  # type: ignore
    """Parent class for feature forms for adding and modifying feature attribute data."""

    def __init__(
        self, plan_feature: PlanFeature, form_title: str, regulation_group_libraries: list[RegulationGroupLibrary]
    ):
        super().__init__()
        self.setupUi(self)

        # TYPES
        self.feature_name: QLineEdit
        self.feature_description: QTextEdit
        self.feature_type_of_underground: CodeComboBox
        self.plan_regulation_group_scrollarea: QScrollArea
        self.plan_regulation_group_scrollarea_contents: QWidget
        self.plan_regulation_group_libraries_combobox: QComboBox
        self.plan_regulation_groups_tree: QTreeWidget
        self.button_box: QDialogButtonBox

        self.regulation_groups_tree_layout: QVBoxLayout

        # INIT
        self.regulation_group_libraries = regulation_group_libraries
        self.plan_regulation_group_libraries_combobox.addItems(
            library.name for library in self.regulation_group_libraries
        )
        self.plan_regulation_group_libraries_combobox.currentIndexChanged.connect(self.show_regulation_group_library)

        self.regulation_group_widgets: list[RegulationGroupWidget] = []
        self.scroll_area_spacer = None
        self.setWindowTitle(form_title)

        self.regulation_groups_selection_widget = TreeWithSearchWidget()
        self.regulation_groups_tree_layout.insertWidget(2, self.regulation_groups_selection_widget)
        self.regulation_groups_selection_widget.tree.itemDoubleClicked.connect(self.add_selected_plan_regulation_group)
        self.show_regulation_group_library(0)

        self.feature_type_of_underground.populate_from_code_layer(UndergroundTypeLayer)
        self.feature_type_of_underground.removeItem(0)  # Remove NULL from combobox as underground data is required
        self.feature_type_of_underground.setCurrentIndex(1)  # Set default to Maanpäällinen (index 1)

        # Initialize attributes from template
        self.plan_feature = plan_feature
        self.layer_name = plan_feature.layer_name  # Should have a layer name
        if plan_feature.name:
            self.feature_name.setText(plan_feature.name)
        if plan_feature.description:
            self.feature_description.setText(plan_feature.description)
        for regulation_group in plan_feature.regulation_groups:
            self.add_plan_regulation_group(regulation_group)

        self.button_box.accepted.connect(self._on_ok_clicked)

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

    def add_plan_regulation_group(self, definition: RegulationGroup):
        regulation_group_widget = RegulationGroupWidget(definition)
        regulation_group_widget.delete_signal.connect(self.remove_plan_regulation_group)
        self._remove_spacer()
        self.plan_regulation_group_scrollarea_contents.layout().addWidget(regulation_group_widget)
        self.regulation_group_widgets.append(regulation_group_widget)
        self._add_spacer()

    def remove_plan_regulation_group(self, regulation_group_widget: RegulationGroupWidget):
        self.plan_regulation_group_scrollarea_contents.layout().removeWidget(regulation_group_widget)
        self.regulation_group_widgets.remove(regulation_group_widget)
        regulation_group_widget.deleteLater()

    def show_regulation_group_library(self, i: int):
        self.regulation_groups_selection_widget.tree.clear()
        library = self.regulation_group_libraries[i]
        for category in library.regulation_group_categories:
            category_item = self.regulation_groups_selection_widget.add_item_to_tree(category.name)
            for group_definition in category.regulation_groups:
                _ = self.regulation_groups_selection_widget.add_item_to_tree(
                    group_definition.name, group_definition, category_item
                )

    def into_model(self) -> PlanFeature:
        return PlanFeature(
            name=self.feature_name.text(),
            type_of_underground_id=self.feature_type_of_underground.value(),
            description=self.feature_description.toPlainText(),
            geom=self.plan_feature.geom,
            layer_name=self.layer_name,
            regulation_groups=[reg_group_widget.into_model() for reg_group_widget in self.regulation_group_widgets],
            id_=self.plan_feature.id_,
        )

    def _on_ok_clicked(self):
        self.model = self.into_model()
        self.accept()
