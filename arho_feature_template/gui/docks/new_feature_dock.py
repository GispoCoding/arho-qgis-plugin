from __future__ import annotations

from importlib import resources
from typing import TYPE_CHECKING

from qgis.gui import QgsDockWidget
from qgis.PyQt import uic
from qgis.PyQt.QtCore import Qt, pyqtSignal
from qgis.PyQt.QtWidgets import QListWidget, QListWidgetItem

from arho_feature_template.core.template_manager import TemplateManager
from arho_feature_template.gui.components.new_feature_grid_widget import NewFeatureGridWidget
from arho_feature_template.utils.localization_utils import deserialize_localized_text

if TYPE_CHECKING:
    from qgis.gui import QgsFilterLineEdit
    from qgis.PyQt.QtWidgets import QComboBox, QWidget

    from arho_feature_template.core.models import PlanFeatureLibrary, PlanObject

ui_path = resources.files(__package__) / "new_feature_dock.ui"
DockClass, _ = uic.loadUiType(ui_path)


class NewFeatureDock(QgsDockWidget, DockClass):  # type: ignore
    library_selection: QComboBox
    search_box: QgsFilterLineEdit
    template_list: QListWidget
    dockWidgetContents: QWidget  # noqa: N815

    tool_activated = pyqtSignal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setupUi(self)

        # INIT
        # 1. New feature grid
        self.new_feature_grid = NewFeatureGridWidget()
        self.dockWidgetContents.layout().insertWidget(1, self.new_feature_grid)

        # 2. Feature templates
        self.active_feature_type: str | None = None
        self.active_feature_layer: str | None = None
        self.active_template: PlanObject | None = None
        self.plan_feature_libraries: list[PlanFeatureLibrary] | None = None
        self.library_selection.currentIndexChanged.connect(self.set_active_plan_feature_library)

        self.template_list.setSelectionMode(self.template_list.SingleSelection)
        self.search_box.valueChanged.connect(self.filter_plan_feature_templates)

        # NOTE: If user moves selection with arrow keys, this is not registered currently
        self.template_list.clicked.connect(self.on_template_item_clicked)
        self.new_feature_grid.active_feature_type_changed.connect(self.on_active_feature_type_changed)

        TemplateManager.signal_manager.feature_object_added_to_library.connect(self.update_template_list)

    def initialize_plan_feature_libraries(self, plan_feature_libraries: list[PlanFeatureLibrary]):
        self.plan_feature_libraries = plan_feature_libraries
        self.library_selection.clear()
        self.library_selection.addItems([library.name for library in self.plan_feature_libraries])
        self.set_active_plan_feature_library(0)

    def on_active_feature_type_changed(self, feature_name: str, layer_name: str):
        self.active_feature_type = feature_name if feature_name else None
        self.active_feature_layer = layer_name if layer_name else None
        self.clear_template_selection()
        self.filter_plan_feature_templates()
        if self.active_feature_type:
            self.tool_activated.emit()

    def filter_plan_feature_templates(self) -> None:
        # Consider both search text and active plan feature type
        search_text = self.search_box.value().lower()

        for index in range(self.template_list.count()):
            item = self.template_list.item(index)
            item_text = item.text().lower()
            plan_feature: PlanObject = item.data(Qt.UserRole)
            text_matches = search_text in item_text
            feature_type_matches = (
                plan_feature.layer_name == self.active_feature_layer if self.active_feature_layer else True
            )
            item.setHidden(not (text_matches and feature_type_matches))

            # Clear selection if the selected template was filtered
            if self.active_template and self.active_template is plan_feature and item.isHidden():
                self.template_list.clearSelection()

    def on_template_item_clicked(self, index: int):
        item = self.template_list.itemFromIndex(index)
        template: PlanObject = item.data(Qt.UserRole)
        # Clicked new list item => activate new template
        if template != self.active_template:
            self.active_template = template
            # NOTE: Workaround to fix make sure clicked item is selected. At least after a selected item has been
            # filtered out, clicking on a new template will select, immediately deselect (but keep focus)
            self.template_list.setCurrentItem(item)
        else:
            # Clicked selected list item => clear selection
            self.active_template = None
            self.template_list.clearSelection()

    def deactivate_and_clear_selections(self):
        self.on_active_feature_type_changed("", "")
        self.new_feature_grid.clear_selections()
        self.clear_template_selection()

    def clear_template_selection(self):
        self.active_template = None
        self.template_list.clearSelection()

    def set_active_plan_feature_library(self, index: int) -> None:
        self.update_template_list(index)

    def update_template_list(self, index: int | None = None) -> None:
        if self.plan_feature_libraries and len(self.plan_feature_libraries) > 0:
            self.template_list.clear()
            library = (
                self.plan_feature_libraries[index]
                if index
                else self.plan_feature_libraries[self.library_selection.currentIndex()]
            )

            for feature_template in library.plan_features:
                item = QListWidgetItem(
                    feature_template.name
                    if isinstance(feature_template.name, str)
                    else deserialize_localized_text(feature_template.name)
                )
                item.setData(Qt.UserRole, feature_template)
                self.template_list.addItem(item)
