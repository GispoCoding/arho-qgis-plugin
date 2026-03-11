from __future__ import annotations

import logging
from importlib import resources
from pathlib import Path

from qgis.PyQt import uic
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QDialog, QDialogButtonBox, QMessageBox, QTabWidget

from arho_feature_template.core.models import PlanFeatureLibrary, RegulationGroupLibrary
from arho_feature_template.gui.components.library_display_widget import LibaryDisplayWidget
from arho_feature_template.resources.libraries.feature_templates import set_user_plan_feature_library_config_files
from arho_feature_template.resources.libraries.regulation_groups import set_user_regulation_group_library_config_files

ui_path = resources.files(__package__) / "manage_libraries.ui"
FormClass, _ = uic.loadUiType(ui_path)

DATA_ROLE = Qt.UserRole

logger = logging.getLogger(__name__)


class ManageLibrariesForm(QDialog, FormClass):  # type: ignore
    def __init__(
        self,
        regulation_group_libraries: list[RegulationGroupLibrary],
        custom_plan_feature_libraries: list[PlanFeatureLibrary],
    ):
        super().__init__()
        self.setupUi(self)
        logger.debug("Initializing ManageLibrariesForm")

        # TYPES
        self.library_tabs: QTabWidget
        self.button_box: QDialogButtonBox
        self.close_button = self.button_box.button(QDialogButtonBox.StandardButton.Close)
        if self.close_button:
            self.close_button.setText("Sulje")

        self.default_regulation_group_libraries: list[RegulationGroupLibrary] = [
            library
            for library in regulation_group_libraries
            if library.library_type == RegulationGroupLibrary.LibraryType.DEFAULT
        ]
        custom_regulation_group_libraries: list[RegulationGroupLibrary] = [
            library
            for library in regulation_group_libraries
            if library.library_type == RegulationGroupLibrary.LibraryType.CUSTOM
        ]
        logger.debug(
            "Library dialog received regulation_group_libraries=%s custom_plan_feature_libraries=%s",
            len(regulation_group_libraries),
            len(custom_plan_feature_libraries),
        )

        # Create tabs for regulation group libraries and plan feature libraries
        self.regulation_group_library_widget = LibaryDisplayWidget(
            list(custom_regulation_group_libraries), RegulationGroupLibrary, list(regulation_group_libraries)
        )
        self.plan_feature_library_widget = LibaryDisplayWidget(
            list(custom_plan_feature_libraries), PlanFeatureLibrary, list(regulation_group_libraries)
        )
        self.library_tabs.addTab(self.regulation_group_library_widget, "Kaavamääräysryhmäpohjat")
        self.library_tabs.addTab(self.plan_feature_library_widget, "Kaavakohdepohjat")

        self.updated_regulation_group_libraries: list[RegulationGroupLibrary] = []
        self.updated_plan_feature_libraries: list[PlanFeatureLibrary] = []

        self.regulation_group_library_widget.library_elements_updated.connect(self._on_regulation_groups_updated)
        self.button_box.clicked.connect(self.reject)

    def _on_regulation_groups_updated(self, new_custom_regulation_groups: list):
        logger.debug("Regulation group libraries updated new_custom_count=%s", len(new_custom_regulation_groups))
        # Update plan feature library widgets regulation group libraries when custom regulation group libraries
        # are modified
        self.plan_feature_library_widget.regulation_group_libraries = (
            self.default_regulation_group_libraries + new_custom_regulation_groups
        )

    def _delete_all_invalid_libraries(self):
        logger.debug("Deleting invalid libraries from both library widgets")
        self._delete_invalid_libraries(self.regulation_group_library_widget)
        self._delete_invalid_libraries(self.plan_feature_library_widget)

    def _delete_invalid_libraries(self, library_widget: LibaryDisplayWidget):
        logger.debug("Checking widget libraries for invalid entries")
        for library in library_widget.get_current_libraries():
            # Check for library missing file path or name, or if library is not saved into file
            if not library.file_path or not library.name or not Path(library.file_path).exists():
                logger.debug("Deleting invalid library name=%s file_path=%s", library.name, library.file_path)
                library_widget.delete_library(library)

    def _handle_unsaved_libraries(self) -> bool:
        unsaved_regulation_group_libraries = self.regulation_group_library_widget.unsaved_libraries
        unsaved_plan_object_libraries = self.plan_feature_library_widget.unsaved_libraries
        logger.debug(
            "Handling unsaved libraries unsaved_regulation_groups=%s unsaved_plan_features=%s",
            len(unsaved_regulation_group_libraries),
            len(unsaved_plan_object_libraries),
        )
        if (
            unsaved_regulation_group_libraries
            and QMessageBox.question(
                None,
                "Varoitus",
                f"Tallentamattomia kaavamääräysryhmäkirjastoja: {unsaved_regulation_group_libraries}. Jos valitset Kyllä, muutokset menetetään.",
                QMessageBox.Yes | QMessageBox.No,
            )
            == QMessageBox.No
        ):
            logger.debug("User cancelled closing due to unsaved regulation group libraries")
            return False

        if unsaved_plan_object_libraries and (
            QMessageBox.question(
                None,
                "Varoitus",
                f"Tallentamattomia kaavakohdepohjakirjastoja: {unsaved_plan_object_libraries}. Jos valitset Kyllä, muutokset menetetään.",
                QMessageBox.Yes | QMessageBox.No,
            )
            == QMessageBox.No
        ):
            logger.debug("User cancelled closing due to unsaved plan feature libraries")
            return False

        self._delete_all_invalid_libraries()
        logger.debug("Unsaved library checks completed successfully")
        return True

    def reject(self):
        logger.debug("Closing ManageLibrariesForm requested")
        if self._handle_unsaved_libraries():
            updated_regulation_group_libraries = self.regulation_group_library_widget.get_current_libraries()
            updated_plan_feature_libraries = self.plan_feature_library_widget.get_current_libraries()
            logger.debug(
                "Persisting library paths regulation_group_count=%s plan_feature_count=%s",
                len(updated_regulation_group_libraries),
                len(updated_plan_feature_libraries),
            )

            set_user_regulation_group_library_config_files(
                library.file_path for library in updated_regulation_group_libraries
            )
            set_user_plan_feature_library_config_files(library.file_path for library in updated_plan_feature_libraries)

            super().reject()
            logger.debug("ManageLibrariesForm closed")
