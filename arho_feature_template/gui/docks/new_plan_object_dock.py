from __future__ import annotations

import logging
from importlib import resources
from typing import TYPE_CHECKING

from qgis.gui import QgsDockWidget
from qgis.PyQt import uic
from qgis.PyQt.QtCore import Qt, pyqtSignal
from qgis.PyQt.QtWidgets import QListWidget, QListWidgetItem

from arho_feature_template.core.template_manager import TemplateManager
from arho_feature_template.gui.components.new_plan_object_grid_widget import NewPlanObjectGridWidget
from arho_feature_template.utils.localization_utils import get_localized_text

if TYPE_CHECKING:
    from qgis.gui import QgsFilterLineEdit
    from qgis.PyQt.QtWidgets import QComboBox, QWidget

    from arho_feature_template.core.models import PlanObject, PlanObjectLibrary

ui_path = resources.files(__package__) / "new_plan_object_dock.ui"
DockClass, _ = uic.loadUiType(ui_path)

logger = logging.getLogger(__name__)


class NewPlanObjectDock(QgsDockWidget, DockClass):  # type: ignore
    library_selection: QComboBox
    search_box: QgsFilterLineEdit
    template_list: QListWidget
    dockWidgetContents: QWidget  # noqa: N815

    tool_activated = pyqtSignal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setupUi(self)
        logger.debug("Initializing NewPlanObjectDock")

        # INIT
        # 1. New plan object grid
        self.new_plan_object_grid = NewPlanObjectGridWidget()
        self.dockWidgetContents.layout().insertWidget(1, self.new_plan_object_grid)

        # 2. Plan object templates
        self.active_plan_object_type: str | None = None
        self.active_plan_object_layer: str | None = None
        self.active_template: PlanObject | None = None
        self.plan_object_libraries: list[PlanObjectLibrary] | None = None
        self.library_selection.currentIndexChanged.connect(self.set_active_plan_object_library)

        self.template_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.search_box.valueChanged.connect(self.filter_plan_object_templates)

        # NOTE: If user moves selection with arrow keys, this is not registered currently
        self.template_list.clicked.connect(self.on_template_item_clicked)
        self.new_plan_object_grid.active_plan_object_type_changed.connect(self.on_active_plan_object_type_changed)

        TemplateManager.signal_manager.plan_object_added_to_library.connect(self.update_template_list)

    def unload(self):
        logger.debug("Unloading NewPlanObjectDock")
        # `signal_manager` is a module level singleton that outlives the dock, so Qt cannot
        # drop this connection for us
        TemplateManager.signal_manager.plan_object_added_to_library.disconnect(self.update_template_list)

    def update_lock_status(self, locked: bool):  # noqa: FBT001
        logger.debug("Updating new plan object dock lock status locked=%s", locked)
        self.new_plan_object_grid.setEnabled(not locked)
        if locked:
            self.new_plan_object_grid.setToolTip("Kaavasuunnitelma on lukittu, kaavakohteita ei voi lisätä.")
        else:
            self.new_plan_object_grid.setToolTip("")

    def initialize_plan_object_libraries(self, plan_object_libraries: list[PlanObjectLibrary]):
        logger.debug("Initializing plan object libraries in new plan object dock count=%s", len(plan_object_libraries))
        self.plan_object_libraries = plan_object_libraries
        self.library_selection.clear()
        self.library_selection.addItems([library.name for library in self.plan_object_libraries])
        self.set_active_plan_object_library(0)

    def on_active_plan_object_type_changed(self, plan_object_type: str, layer_name: str):
        logger.debug("Active plan object type changed type=%s layer=%s", plan_object_type, layer_name)
        self.active_plan_object_type = plan_object_type if plan_object_type else None
        self.active_plan_object_layer = layer_name if layer_name else None
        self.clear_template_selection()
        self.filter_plan_object_templates()
        if self.active_plan_object_type:
            logger.debug("Emitting tool_activated for plan_object_type=%s", self.active_plan_object_type)
            self.tool_activated.emit()

    def filter_plan_object_templates(self) -> None:
        # Consider both search text and active plan object type
        search_text = self.search_box.value().lower()
        logger.debug(
            "Filtering plan object templates search_text=%s active_layer=%s",
            search_text,
            self.active_plan_object_layer,
        )

        for index in range(self.template_list.count()):
            item = self.template_list.item(index)
            item_text = item.text().lower()
            plan_object: PlanObject = item.data(Qt.ItemDataRole.UserRole)
            text_matches = search_text in item_text
            plan_object_type_matches = (
                plan_object.layer_name == self.active_plan_object_layer if self.active_plan_object_layer else True
            )
            item.setHidden(not (text_matches and plan_object_type_matches))

            # Clear selection if the selected template was filtered
            if self.active_template and self.active_template is plan_object and item.isHidden():
                logger.debug("Active template filtered out, clearing selection")
                self.template_list.clearSelection()

    def on_template_item_clicked(self, index: int):
        item = self.template_list.itemFromIndex(index)
        template: PlanObject = item.data(Qt.ItemDataRole.UserRole)
        logger.debug("Template list item clicked template_name=%s", item.text())
        # Clicked new list item => activate new template
        if template != self.active_template:
            self.active_template = template
            logger.debug("Activated template from list")
            # NOTE: Workaround to fix make sure clicked item is selected. At least after a selected item has been
            # filtered out, clicking on a new template will select, immediately deselect (but keep focus)
            self.template_list.setCurrentItem(item)
        else:
            # Clicked selected list item => clear selection
            self.active_template = None
            logger.debug("Clicked active template again, clearing active template")
            self.template_list.clearSelection()

    def deactivate_and_clear_selections(self):
        logger.debug("Deactivating new plan object dock and clearing selections")
        self.on_active_plan_object_type_changed("", "")
        self.new_plan_object_grid.clear_selections()
        self.clear_template_selection()

    def clear_template_selection(self):
        logger.debug("Clearing template selection")
        self.active_template = None
        self.template_list.clearSelection()

    def set_active_plan_object_library(self, index: int) -> None:
        logger.debug("Setting active plan object library index=%s", index)
        self.update_template_list(index)

    def update_template_list(self, index: int | None = None) -> None:
        logger.debug("Updating template list requested_index=%s", index)
        if self.plan_object_libraries and len(self.plan_object_libraries) > 0:
            self.template_list.clear()
            library = (
                self.plan_object_libraries[index]
                if index
                else self.plan_object_libraries[self.library_selection.currentIndex()]
            )
            logger.debug("Using template library name=%s template_count=%s", library.name, len(library.plan_objects))

            for plan_object_template in library.plan_objects:
                item = QListWidgetItem(
                    plan_object_template.name
                    if isinstance(plan_object_template.name, str)
                    else get_localized_text(plan_object_template.name)
                )
                item.setData(Qt.ItemDataRole.UserRole, plan_object_template)
                self.template_list.addItem(item)
            logger.debug("Template list updated count=%s", self.template_list.count())
