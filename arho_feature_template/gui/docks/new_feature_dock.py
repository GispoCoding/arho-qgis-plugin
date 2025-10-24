from __future__ import annotations

from importlib import resources
from typing import TYPE_CHECKING

from qgis.gui import QgsDockWidget
from qgis.PyQt import uic
from qgis.PyQt.QtCore import Qt, pyqtSignal
from qgis.PyQt.QtWidgets import QListWidget, QListWidgetItem, QPushButton

if TYPE_CHECKING:
    from qgis.gui import QgsFilterLineEdit
    from qgis.PyQt.QtWidgets import QComboBox, QWidget

    from arho_feature_template.core.models import PlanFeatureLibrary, PlanObject

ui_path = resources.files(__package__) / "new_feature_dock.ui"
DockClass, _ = uic.loadUiType(ui_path)

FEATURE_TYPES = ["Aluevaraus", "Osa-alue", "Viiva", "Piste"]
FEATURE_TYPE_TO_LAYER_NAME = {
    "Viiva": "Viivat",
    "Osa-alue": "Osa-alue",
    "Aluevaraus": "Aluevaraus",
    "Piste": "Pisteet",
}


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
        # 1. Plan feature types
        self.land_use_area_btn: QPushButton
        self.other_area_btn: QPushButton
        self.line_btn: QPushButton
        self.point_btn: QPushButton

        self.feature_type_buttons = [self.land_use_area_btn, self.other_area_btn, self.line_btn, self.point_btn]
        for btn in self.feature_type_buttons:
            btn.clicked.connect(lambda _, button=btn: self.handle_button_click(button))

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

    def handle_button_click(self, clicked_button: QPushButton):
        for btn in self.feature_type_buttons:
            if btn == clicked_button:
                btn.setChecked(True)
            else:
                btn.setChecked(False)
        self.update_activate_feature_type(clicked_button.text(), FEATURE_TYPE_TO_LAYER_NAME[clicked_button.text()])

    def initialize_plan_feature_libraries(self, plan_feature_libraries: list[PlanFeatureLibrary]):
        self.plan_feature_libraries = plan_feature_libraries
        self.library_selection.clear()
        self.library_selection.addItems([library.name for library in self.plan_feature_libraries])
        self.set_active_plan_feature_library(0)

    def update_activate_feature_type(self, feature_name: str, layer_name: str):
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
        self.update_activate_feature_type("", "")
        for btn in self.feature_type_buttons:
            btn.setChecked(False)
        self.clear_template_selection()

    def clear_template_selection(self):
        self.active_template = None
        self.template_list.clearSelection()

    def set_active_plan_feature_library(self, index: int) -> None:
        if self.plan_feature_libraries and len(self.plan_feature_libraries) > 0:
            self.template_list.clear()
            library = self.plan_feature_libraries[index]
            for feature_template in library.plan_features:
                item = QListWidgetItem(feature_template.name)
                item.setData(Qt.UserRole, feature_template)
                self.template_list.addItem(item)
