from __future__ import annotations

from importlib import resources
from typing import TYPE_CHECKING, cast

from qgis.PyQt import uic
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QDialog, QDialogButtonBox, QMessageBox, QTreeWidgetItem

from arho_feature_template.core.models import (
    Library,
    PlanFeatureLibrary,
    PlanObject,
    RegulationGroup,
    RegulationGroupLibrary,
)
from arho_feature_template.gui.components.tree_with_search_widget import TreeWithSearchWidget
from arho_feature_template.project.layers.code_layers import (
    PlanRegulationGroupTypeLayer,
    PlanType,
    PlanTypeLayer,
)
from arho_feature_template.project.layers.plan_layers import PlanMatterLayer
from arho_feature_template.utils.localization_utils import get_localized_text
from arho_feature_template.utils.misc_utils import get_active_plan_matter_id

if TYPE_CHECKING:
    from qgis.PyQt.QtWidgets import QComboBox, QWidget

ui_path = resources.files(__package__) / "template_selection_form.ui"
FormClass, _ = uic.loadUiType(ui_path)


DATA_COLUMN = 0
DATA_ROLE = Qt.UserRole


class TemplateSelectionForm(QDialog, FormClass):  # type: ignore
    def __init__(self, libraries: list[Library]):
        super().__init__()
        self.setupUi(self)

        # TYPES
        self.libraries_widget: QWidget
        self.libraries_combobox: QComboBox
        self.button_box: QDialogButtonBox

        # INIT
        self.template_categories: dict[str, QTreeWidgetItem] = {}

        self.selected_item: QTreeWidgetItem | None = None
        self.selected_template: RegulationGroup | PlanObject | None = None

        self.button_box.button(QDialogButtonBox.Ok).setEnabled(False)

        self.libraries = [*(library for library in libraries if library.status)]

        self.libraries_combobox.addItems(library.name for library in self.libraries)
        self.libraries_combobox.currentIndexChanged.connect(self.show_library)

        self.template_selection_widget = TreeWithSearchWidget()
        self.libraries_widget.layout().insertWidget(2, self.template_selection_widget)
        self.select_library_by_active_plan_type()

        self.show_library(self.libraries_combobox.currentIndex())

        self.button_box.accepted.connect(self._on_accept)
        self.template_selection_widget.tree.itemDoubleClicked.connect(lambda _: self._on_accept())
        self.template_selection_widget.tree.itemSelectionChanged.connect(self._on_selection_changed)

    def _on_selection_changed(self):
        self.selected_item = self.template_selection_widget.get_selected_item()
        self.button_box.button(QDialogButtonBox.Ok).setEnabled(self.selected_item is not None)

    def select_library_by_active_plan_type(self):
        feature = PlanMatterLayer.get_feature_by_id(get_active_plan_matter_id(), no_geometries=False)
        if feature is not None:
            model = PlanMatterLayer.model_from_feature(feature)
            plan_type = PlanTypeLayer.get_plan_type(model.plan_type_id)

            library_name = ""
            if plan_type == PlanType.REGIONAL:
                library_name = "Maakuntakaavan kaavamääräysryhmät (Katja)"
            elif plan_type == PlanType.GENERAL:
                library_name = "Yleiskaavan kaavamääräysryhmät (Katja)"
            elif plan_type == PlanType.TOWN:
                library_name = "Asemakaavan kaavamääräysryhmät (Katja)"
            else:
                return

            for i, library in enumerate(self.libraries):
                if library.name == library_name:
                    self.libraries_combobox.setCurrentIndex(i)
                    return

        self.libraries_combobox.setCurrentIndex(0)

    def show_library(self, i: int):
        self.template_selection_widget.tree.clear()
        self.template_categories.clear()

        library = self.libraries[i]
        if type(library) is RegulationGroupLibrary:
            self._populate_regulation_group_library(library)
        elif type(library) is PlanFeatureLibrary:
            self._populate_plan_object_library(library)

    def _populate_regulation_group_library(self, library: RegulationGroupLibrary):
        # COPIED FROM regulation_groups_view.py
        for group in library.regulation_groups:
            category = group.category

            # Fallback strategies when category not saved in model
            if category is None:
                if group.type_code_id is not None:
                    group_type = PlanRegulationGroupTypeLayer.get_attribute_by_id("name", group.type_code_id)
                    category = cast(str, get_localized_text(group_type)) if group_type else "Muut"
                else:
                    category = "Muut"

            if category not in self.template_categories:
                # Create category item
                category_item = self.template_selection_widget.add_item_to_tree(category)
                self.template_categories[category] = category_item

            # Add group item to tree
            _ = self.template_selection_widget.add_item_to_tree(str(group), group, self.template_categories[category])

    def _populate_plan_object_library(self, _library: PlanFeatureLibrary):
        # TODO: Implement when needed
        pass

    def _on_accept(self):
        model = self.template_selection_widget.get_item_data(self.template_selection_widget.get_selected_item())
        if model:
            self.selected_template = model
            self.accept()
        else:
            QMessageBox.critical(None, "Virhe", "Valittu rivi on kategoria eikä sisällä pohjaa.")
