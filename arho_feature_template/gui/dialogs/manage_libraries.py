from __future__ import annotations

from importlib import resources

from qgis.PyQt import uic
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QDialog, QDialogButtonBox, QMessageBox, QTabWidget

from arho_feature_template.core.models import PlanFeatureLibrary, RegulationGroupLibrary
from arho_feature_template.gui.components.library_display_widget import LibaryDisplayWidget

ui_path = resources.files(__package__) / "manage_libraries.ui"
FormClass, _ = uic.loadUiType(ui_path)

DATA_ROLE = Qt.UserRole


class ManageLibrariesForm(QDialog, FormClass):  # type: ignore
    def __init__(
        self,
        tr,
        regulation_group_libraries: list[RegulationGroupLibrary],
        custom_plan_feature_libraries: list[PlanFeatureLibrary],
    ):
        super().__init__()
        self.tr = tr
        self.setupUi(self)

        # TYPES
        self.library_tabs: QTabWidget
        self.button_box: QDialogButtonBox

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

        # Create tabs for regulation group libraries and plan feature libraries
        self.regulation_group_library_widget = LibaryDisplayWidget(self.tr,
            list(custom_regulation_group_libraries), RegulationGroupLibrary, list(regulation_group_libraries)
        )
        self.plan_feature_library_widget = LibaryDisplayWidget(self.tr,
            list(custom_plan_feature_libraries), PlanFeatureLibrary, list(regulation_group_libraries)
        )
        self.library_tabs.addTab(self.regulation_group_library_widget, "Kaavamääräysryhmäpohjat")
        self.library_tabs.addTab(self.plan_feature_library_widget, "Kaavakohdepohjat")

        self.updated_regulation_group_libraries: list[RegulationGroupLibrary] = []
        self.updated_plan_feature_libraries: list[PlanFeatureLibrary] = []

        self.regulation_group_library_widget.library_elements_updated.connect(self._on_regulation_groups_updated)
        self.button_box.accepted.connect(self._on_ok_clicked)

    def _check_form(self) -> bool:
        file_paths = set()
        names = set()
        for tab in [self.regulation_group_library_widget, self.plan_feature_library_widget]:
            for library in tab.get_current_libraries():
                # Check for duplicate filepaths
                if library.file_path in file_paths:
                    QMessageBox.critical(
                        self,
                        "Virhe",
                        f"Useammalle kirjastolle on määritelty sama tallennuspolku ({library.file_path}).",
                    )
                    return False
                # Check for duplicate names
                if library.name in names:
                    QMessageBox.critical(
                        self,
                        "Virhe",
                        f"Useammalle kirjastolle on määritelty sama nimi ({library.name}).",
                    )
                    return False
                file_paths.add(library.file_path)
                names.add(library.name)

        return True

    def _on_regulation_groups_updated(self, new_custom_regulation_groups: list):
        # Update plan feature library widgets regulation group libraries when custom regulation group libraries
        # are modified
        self.plan_feature_library_widget.regulation_group_libraries = (
            self.default_regulation_group_libraries + new_custom_regulation_groups
        )

    def _on_ok_clicked(self):
        if self._check_form():
            self.accept()
