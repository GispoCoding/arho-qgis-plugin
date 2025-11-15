from __future__ import annotations

from importlib import resources
from typing import TYPE_CHECKING

from qgis.PyQt import uic
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import (
    QComboBox,
    QGroupBox,
    QLabel,
    QMessageBox,
    QScrollArea,
    QSizePolicy,
    QSpacerItem,
    QSplitter,
    QTreeWidget,
    QTreeWidgetItem,
)

from arho_feature_template.gui.components.plan_regulation_group_widget import RegulationGroupWidget
from arho_feature_template.gui.components.tree_with_search_widget import TreeWithSearchWidget
from arho_feature_template.gui.dialogs.plan_regulation_group_form import PlanRegulationGroupForm
from arho_feature_template.project.layers.code_layers import (
    AdditionalInformationTypeLayer,
    PlanRegulationGroupTypeLayer,
    PlanType,
    PlanTypeLayer,
)
from arho_feature_template.project.layers.plan_layers import PlanMatterLayer
from arho_feature_template.utils.misc_utils import LANGUAGE, disconnect_signal, get_active_plan_matter_id

if TYPE_CHECKING:
    from collections import defaultdict

    from qgis.PyQt.QtWidgets import QWidget

    from arho_feature_template.core.models import PlanObject, RegulationGroup, RegulationGroupLibrary

ui_path = resources.files(__package__) / "regulation_groups_view.ui"
FormClass, _ = uic.loadUiType(ui_path)


class RegulationGroupsView(QGroupBox, FormClass):  # type: ignore
    def __init__(
        self,
        tr,
        regulation_group_libraries: list[RegulationGroupLibrary],
        active_plan_regulation_groups_library: RegulationGroupLibrary | None = None,
        plan_object: PlanObject | None = None,
    ):
        super().__init__()
        self.tr = tr
        self.setupUi(self)

        # TYPES
        self.libraries_widget: QWidget
        self.regulation_groups_widget: QWidget
        self.plan_regulation_group_scrollarea: QScrollArea
        self.plan_regulation_group_scrollarea_contents: QWidget
        self.plan_regulation_group_libraries_combobox: QComboBox
        self.plan_regulation_groups_tree: QTreeWidget
        self.regulation_groups_label: QLabel

        # INIT
        self.layout().removeWidget(self.libraries_widget)
        self.layout().removeWidget(self.regulation_groups_widget)
        splitter = QSplitter(self)
        splitter.addWidget(self.libraries_widget)
        splitter.addWidget(self.regulation_groups_widget)
        splitter.setSizes([300, 550])
        self.layout().addWidget(splitter)

        self.plan_object = plan_object
        self.template_categories: dict[str, QTreeWidgetItem] = {}

        self.regulation_group_libraries = [*(library for library in regulation_group_libraries if library.status)]

        self.regulation_groups_hash_map: defaultdict[int, list] | None = None
        self.active_plan_regulation_groups_library: RegulationGroupLibrary | None = None
        if active_plan_regulation_groups_library:
            self.existing_group_letter_codes = active_plan_regulation_groups_library.get_letter_codes()
            self.active_plan_regulation_groups_library = active_plan_regulation_groups_library
            self.regulation_group_libraries.append(active_plan_regulation_groups_library)
            self.regulation_groups_hash_map = self.active_plan_regulation_groups_library.into_hash_map()
        else:
            self.existing_group_letter_codes = set()

        self.plan_regulation_group_libraries_combobox.addItems(
            library.name for library in self.regulation_group_libraries
        )
        self.plan_regulation_group_libraries_combobox.currentIndexChanged.connect(self.show_regulation_group_library)

        self.regulation_group_widgets: list[RegulationGroupWidget] = []
        self.scroll_area_spacer = None

        self.regulation_groups_selection_widget = TreeWithSearchWidget()
        self.libraries_widget.layout().insertWidget(2, self.regulation_groups_selection_widget)
        self.regulation_groups_selection_widget.tree.itemDoubleClicked.connect(self.add_selected_plan_regulation_group)
        self.select_library_by_active_plan_type()

        self.show_regulation_group_library(self.plan_regulation_group_libraries_combobox.currentIndex())

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

            for i, library in enumerate(self.regulation_group_libraries):
                if library.name == library_name:
                    self.plan_regulation_group_libraries_combobox.setCurrentIndex(i)
                    return

        self.plan_regulation_group_libraries_combobox.setCurrentIndex(0)

    def _add_spacer(self):
        self.scroll_area_spacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.plan_regulation_group_scrollarea_contents.layout().addItem(self.scroll_area_spacer)

    def _remove_spacer(self):
        if self.scroll_area_spacer is not None:
            self.plan_regulation_group_scrollarea_contents.layout().removeItem(self.scroll_area_spacer)
            self.scroll_area_spacer = None

    def check_multiple_regulation_groups_with_principal_intended_use_regulations(self) -> bool:
        principal_intended_use_groups = {
            regulation_group_widget
            for regulation_group_widget in self.regulation_group_widgets
            for regulation_widget in regulation_group_widget.regulation_widgets
            for additional_information_widget in regulation_widget.additional_information_widgets
            if AdditionalInformationTypeLayer.get_type_by_id(
                additional_information_widget.additional_information.additional_information_type_id
            )
            == "paakayttotarkoitus"
        }

        if len(principal_intended_use_groups) > 1:
            msg = "Kaavakohteella voi olla vain yksi kaavamääräysryhmä, jossa pääkäyttötarkoituksia."
            QMessageBox.critical(self, "Virhe", msg)
            return False

        return True

    def add_selected_plan_regulation_group(self, item: QTreeWidgetItem, column: int):
        if not item.parent():
            return
        regulation_group: RegulationGroup = item.data(column, Qt.UserRole)
        self.add_plan_regulation_group(regulation_group)

    def add_plan_regulation_group(self, regulation_group: RegulationGroup):
        regulation_group_widget = RegulationGroupWidget(self.tr, regulation_group, self.plan_object)
        regulation_group_widget.delete_signal.connect(self.remove_plan_regulation_group)
        regulation_group_widget.open_as_form_signal.connect(self.open_plan_regulation_group_form)
        regulation_group_widget.update_matching_groups.connect(self.update_matching_groups)
        self._remove_spacer()
        self.plan_regulation_group_scrollarea_contents.layout().addWidget(regulation_group_widget)
        self.regulation_group_widgets.append(regulation_group_widget)
        self._add_spacer()

        # If active plan regulation groups library is not given, disable linking functionality in
        # plan regulation group widget. This should be the case only when the view is accessed
        # through plan feature template library manager
        if not self.active_plan_regulation_groups_library:
            regulation_group_widget.disable_linking()
        elif regulation_group.id_ is None:
            self.update_matching_groups(regulation_group_widget)

    def open_plan_regulation_group_form(self, regulation_group_widget: RegulationGroupWidget):
        group_as_form = PlanRegulationGroupForm(
            self.tr, regulation_group_widget.into_model(), self.active_plan_regulation_groups_library
        )
        if group_as_form.exec_():
            regulation_group_widget.from_model(group_as_form.model)

    def remove_plan_regulation_group(self, regulation_group_widget: RegulationGroupWidget):
        disconnect_signal(regulation_group_widget.delete_signal)
        disconnect_signal(regulation_group_widget.open_as_form_signal)
        self.plan_regulation_group_scrollarea_contents.layout().removeWidget(regulation_group_widget)
        self.regulation_group_widgets.remove(regulation_group_widget)
        regulation_group_widget.deleteLater()

    def show_regulation_group_library(self, i: int):
        self.regulation_groups_selection_widget.tree.clear()
        self.template_categories.clear()

        library = self.regulation_group_libraries[i]
        for group in library.regulation_groups:
            category = group.category

            # Fallback strategies when category not saved in model
            if category is None:
                if group.type_code_id is not None:
                    group_type = PlanRegulationGroupTypeLayer.get_attribute_by_id("name", group.type_code_id)
                    category = group_type[LANGUAGE] if group_type else "Muut"
                else:
                    category = "Muut"

            if category not in self.template_categories:
                # Create category item
                category_item = self.regulation_groups_selection_widget.add_item_to_tree(category)
                self.template_categories[category] = category_item

            # Add group item to tree
            _ = self.regulation_groups_selection_widget.add_item_to_tree(
                str(group), group, self.template_categories[category]
            )

    def update_matching_groups(self, regulation_group_widget: RegulationGroupWidget):
        matching_groups = self.find_matching_groups(regulation_group_widget.into_model())
        regulation_group_widget.setup_linking_to_matching_groups(matching_groups)

    def find_matching_groups(self, regulation_group: RegulationGroup) -> list[RegulationGroup]:
        if self.regulation_groups_hash_map:
            return self.regulation_groups_hash_map.get(regulation_group.data_hash(), [])
        return []

    def into_model(self) -> list[RegulationGroup]:
        return [reg_group_widget.into_model() for reg_group_widget in self.regulation_group_widgets]
