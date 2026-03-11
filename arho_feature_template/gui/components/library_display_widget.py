from __future__ import annotations

import copy
import logging
from importlib import resources
from pathlib import Path
from typing import TYPE_CHECKING

from qgis.core import QgsApplication
from qgis.PyQt import uic
from qgis.PyQt.QtCore import Qt, pyqtSignal
from qgis.PyQt.QtWidgets import (
    QComboBox,
    QFileDialog,
    QGroupBox,
    QLabel,
    QLineEdit,
    QListWidgetItem,
    QMenu,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QWidget,
)

from arho_feature_template.core.models import (
    Library,
    PlanFeatureLibrary,
    PlanObject,
    RegulationGroup,
    RegulationGroupLibrary,
)
from arho_feature_template.core.template_manager import TemplateManager
from arho_feature_template.gui.dialogs.plan_feature_form import PlanObjectForm
from arho_feature_template.gui.dialogs.plan_regulation_group_form import PlanRegulationGroupForm
from arho_feature_template.project.layers.plan_layers import LandUseAreaLayer, LineLayer, OtherAreaLayer, PointLayer
from arho_feature_template.utils.misc_utils import iface

if TYPE_CHECKING:
    from qgis.gui import QgsCollapsibleGroupBox, QgsFileWidget, QgsFilterLineEdit
    from qgis.PyQt.QtWidgets import QListWidget, QPushButton


ui_path = resources.files(__package__) / "library_display_widget.ui"
FormClass, _ = uic.loadUiType(ui_path)

# TODO: Now almost duplicate version exists in NewFeatureGridWidget, both should be moved to a generic place
FEATURE_TYPE_TO_LAYER_NAME = {
    "Viiva": LineLayer.name,
    "Osa-alue": OtherAreaLayer.name,
    "Aluevaraus": LandUseAreaLayer.name,
    "Piste": PointLayer.name,
}

DATA_ROLE = Qt.UserRole

logger = logging.getLogger(__name__)


class LibaryDisplayWidget(QWidget, FormClass):  # type: ignore
    library_elements_updated = pyqtSignal(list)

    def __init__(
        self,
        libraries: list[PlanFeatureLibrary | RegulationGroupLibrary],
        library_type_class: type[PlanFeatureLibrary | RegulationGroupLibrary],
        # regulation_group_libraries is needed to open PlanFeatureForm
        # would be a lot easier and cleaner if this could be accessed globally
        regulation_group_libraries: list[RegulationGroupLibrary],
    ):
        super().__init__()
        self.setupUi(self)
        logger.debug("Initializing LibaryDisplayWidget")

        # TYPES
        self.new_library_btn: QPushButton
        self.import_library_btn: QPushButton
        self.delete_library_btn: QPushButton
        self.library_selection: QComboBox

        self.library_file_path: QgsFileWidget
        self.reload_library_btn: QPushButton
        self.broken_path_warning_label: QLabel

        self.library_details_groupbox: QgsCollapsibleGroupBox
        self.library_name: QLineEdit
        self.library_description: QTextEdit

        self.library_elements_box: QGroupBox
        self.new_library_element_btn: QPushButton
        self.edit_library_element_btn: QPushButton
        self.delete_library_element_btn: QPushButton
        self.save_library_btn: QPushButton

        self.library_element_filter: QgsFilterLineEdit
        self.library_element_list: QListWidget

        # VARS
        self.initialize_by_library_type(library_type_class)
        logger.debug("Library display widget initialized for type=%s", self.library_type)
        self.active_library: Library | None = None
        self.new_libraries: list[Library] = []

        # Needed if library display widget is for plan features
        self.regulation_group_libraries = regulation_group_libraries

        # Reference to the original library list
        self.libraries = libraries

        # Make a deep copy of the given library list so that modifications will only be saved when user
        # succesfully clicks Ok
        self.updated_libraries = copy.deepcopy(libraries)
        # Initialize set for storing references to unsaved libraries
        self.unsaved_libraries: set[str] = set()

        # SIGNALS
        self.library_selection.currentIndexChanged.connect(self._on_library_selection_changed)
        self.reload_library_btn.clicked.connect(self._on_reload_library_file_clicked)
        self.library_name.textChanged.connect(self._on_library_name_changed)
        self.library_file_path.fileChanged.connect(self._on_library_file_path_changed)
        self.library_description.textChanged.connect(self._on_library_description_changed)

        self.new_library_btn.clicked.connect(self._on_new_library_clicked)
        self.import_library_btn.clicked.connect(self._on_import_library_clicked)
        self.delete_library_btn.clicked.connect(self._on_delete_library_clicked)

        self.library_element_list.itemDoubleClicked.connect(lambda _: self._on_edit_element_clicked())
        self.edit_library_element_btn.clicked.connect(self._on_edit_element_clicked)
        self.delete_library_element_btn.clicked.connect(self._on_delete_element_clicked)
        self.save_library_btn.clicked.connect(self._on_save_library_clicked)

        self.library_element_filter.valueChanged.connect(self._on_filter_elements)

        # ICONS
        self.reload_library_btn.setIcon(QgsApplication.getThemeIcon("mActionRefresh.svg"))

        self.new_library_btn.setIcon(QgsApplication.getThemeIcon("mActionAdd.svg"))
        self.import_library_btn.setIcon(QgsApplication.getThemeIcon("mActionFileOpen.svg"))
        self.delete_library_btn.setIcon(QgsApplication.getThemeIcon("mActionDeleteSelected.svg"))
        self.save_library_btn.setIcon(QgsApplication.getThemeIcon("mActionFileSave.svg"))

        self.new_library_element_btn.setIcon(QgsApplication.getThemeIcon("mActionAdd.svg"))
        self.edit_library_element_btn.setIcon(QgsApplication.getThemeIcon("mActionEditTable.svg"))
        self.delete_library_element_btn.setIcon(QgsApplication.getThemeIcon("mActionDeleteSelected.svg"))

        # Initialize existing libraries, selection and widgets
        for library in self.libraries:
            self._add_library(library)

        if self.library_selection.count() != 0:
            self.library_selection.setCurrentIndex(0)
        self._check_required_fields()

        # Call to handle the case where no libraries are present
        self._on_library_selection_changed(None)

    def initialize_by_library_type(self, library_type_class: type[PlanFeatureLibrary | RegulationGroupLibrary]):
        self.library_type_class = library_type_class

        if self.library_type_class is PlanFeatureLibrary:
            self.library_type = "plan_feature"
            self.library_element_property = "plan_features"
            select_plan_feature_type_menu = QMenu()
            for feature_name, layer_name in FEATURE_TYPE_TO_LAYER_NAME.items():
                select_plan_feature_type_menu.addAction(feature_name).triggered.connect(
                    lambda _, fn=feature_name, ln=layer_name: self._on_new_plan_feature_clicked(fn, ln)
                )
            self.new_library_element_btn.setMenu(select_plan_feature_type_menu)
        elif self.library_type_class is RegulationGroupLibrary:
            self.library_type = "regulation_group"
            self.library_element_property = "regulation_groups"
            self.new_library_element_btn.clicked.connect(self._on_new_regulation_group_clicked)
        else:
            pass
        logger.debug("Configured library widget library_type=%s", getattr(self, "library_type", None))

    # LIBRARIES
    def _check_required_fields(self) -> bool:
        valid = all(
            library.name != "" and library.file_path not in ["", None] for library in self.get_current_libraries()
        )
        logger.debug("Required field check valid=%s", valid)
        return valid

    def _on_library_selection_changed(self, _):
        logger.debug("Library selection changed count=%s", self.library_selection.count())
        if self.library_selection.count() == 0:
            self._handle_no_libraries_present()
        else:
            current_library = self.library_selection.currentData(DATA_ROLE)
            current_library_name = self.library_selection.currentText()
            logger.debug("Active library changed name=%s", current_library_name)
            self._change_active_library(current_library)
            if current_library_name in self.unsaved_libraries:
                self.save_library_btn.setEnabled(True)
            else:
                self.save_library_btn.setEnabled(False)

    def _on_library_name_changed(self, new_name: str):
        if self.active_library is None:
            return

        logger.debug("Library name changed new_name=%s", new_name)
        self.active_library.name = new_name
        self.save_library_btn.setEnabled(True)
        self._check_required_fields()

    def _on_reload_library_file_clicked(self):
        file_path = self.library_file_path.filePath()
        logger.debug("Reloading library from file path=%s", file_path)
        loaded_library = self.library_type_class.from_template_dict(
            data=TemplateManager.read_library_config_file(file_path, self.library_type),
            library_type=Library.LibraryType.CUSTOM,
            file_path=str(file_path),
        )
        self.library_selection.setItemData(self.library_selection.currentIndex(), loaded_library, DATA_ROLE)
        self._change_active_library(loaded_library)
        self.save_library_btn.setEnabled(False)
        logger.debug("Library reloaded from file path=%s status=%s", file_path, loaded_library.status)

    def _on_library_file_path_changed(self, new_path: str):
        if self.active_library is None:
            return

        logger.debug("Library file path changed new_path=%s", new_path)
        self.active_library.file_path = new_path
        self.save_library_btn.setEnabled(True)
        self._check_required_fields()

    def _on_library_description_changed(self):
        if self.active_library is None:
            return

        logger.debug("Library description changed for active library=%s", self.active_library.name)
        self.active_library.description = self.library_description.toPlainText()
        self.save_library_btn.setEnabled(True)

    def _handle_no_libraries_present(self):
        logger.debug("No libraries present, clearing and disabling library widgets")
        self.library_name.clear()
        self.library_file_path.setFilePath("")
        self.library_description.clear()
        self.library_element_list.clear()

        self.library_details_groupbox.setEnabled(False)
        self.library_elements_box.setEnabled(False)
        self.broken_path_warning_label.hide()

    def _change_active_library(self, library: RegulationGroupLibrary):
        logger.debug("Changing active library to name=%s status=%s", library.name, library.status)
        self.active_library = library

        self.library_file_path.setFilePath(library.file_path)
        if library.status is True:
            # Enable widgets and show contents
            self.library_name.setEnabled(True)
            self.library_name.setText(library.name)
            self.library_description.setEnabled(True)
            self.library_description.setText(library.description)
            self.library_details_groupbox.setEnabled(True)
            self.library_elements_box.setEnabled(True)

            self.broken_path_warning_label.hide()
        else:
            # Disable and clear widgets
            self.library_name.setEnabled(False)
            self.library_name.clear()
            self.library_description.setEnabled(False)
            self.library_description.clear()
            self.library_details_groupbox.setEnabled(True)
            self.library_elements_box.setEnabled(False)

            self.broken_path_warning_label.show()

        # Cannot reload a new library from file (this would be importing)
        if self._is_new_library(library):
            self.reload_library_btn.setEnabled(False)
        else:
            self.reload_library_btn.setEnabled(True)

        self._update_template_view()

    def _add_library(self, library: Library):
        logger.debug("Adding library to selection name=%s file_path=%s", library.name, library.file_path)
        self.library_selection.addItem(library.name, library)
        self.library_selection.setCurrentIndex(self.library_selection.count() - 1)

    def _on_new_library_clicked(self):
        logger.debug("Creating new library entry")
        library = self.library_type_class(f"Uusi kirjasto {len(self.new_libraries) + 1}")
        self.new_libraries.append(library)
        self._add_library(library)
        self.library_name.clear()  # Keep the name field empty to make sure user types something themselves

    def _on_import_library_clicked(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Tuo kirjasto", "", "YAML files (*.yaml)")
        if file_path:
            logger.debug("Import library requested path=%s", file_path)
            # Ask user for confirmation if about to import a library with an existing/duplicate filepath
            if file_path in [library.file_path for library in self.get_current_libraries()]:
                response = QMessageBox.question(
                    None,
                    "Kirjaston tuominen",
                    "Valitulle tiedostopolulle on jo määritetty kirjasto. Haluatko silti tuoda kirjaston?",
                    QMessageBox.Yes | QMessageBox.No,
                )
                if response == QMessageBox.No:
                    logger.debug("Import library cancelled due to duplicate path confirmation")
                    return

            # Attempt import
            library = self.library_type_class.from_template_dict(
                data=TemplateManager.read_library_config_file(file_path, self.library_type),
                library_type=Library.LibraryType.CUSTOM,
                file_path=str(file_path),
            )
            if library.status:
                self._add_library(library)
                logger.debug("Library imported successfully path=%s", file_path)
            else:
                logger.warning("Library import failed path=%s", file_path)
                QMessageBox.critical(
                    self,
                    "Virhe",
                    "Valitun tiedoston lukeminen kirjastoksi epäonnistui.",
                )

    def _on_delete_library_clicked(self):
        if not self.active_library:
            return

        logger.debug("Delete library requested name=%s", self.active_library.name)

        # If we are deleting a new and empty library, skip asking for confirmation to delete
        if self._is_new_library(self.active_library) and self.library_element_list.count() == 0:
            self.delete_library(self.active_library)
            return

        response = QMessageBox.question(
            None,
            "Kirjaston poisto",
            "Haluatko varmasti poistaa kirjaston?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if response == QMessageBox.Yes:
            self.delete_library(self.active_library)

    def delete_library(self, library: Library):
        logger.debug("Deleting library name=%s file_path=%s", library.name, library.file_path)
        # Find the correct library from the list of updated libraries
        # We have to find the correct library like this because the library instances are
        # different in the original list and the copied list
        for lib in self.updated_libraries:
            if lib.file_path == library.file_path:
                self.updated_libraries.remove(lib)

        self.library_selection.removeItem(self.library_selection.currentIndex())

    def _is_new_library(self, library: Library) -> bool:
        return id(library) in [id(_library) for _library in self.new_libraries]

    # TEMPLATES
    def get_current_libraries(self) -> list[Library]:
        return [self.library_selection.itemData(i, DATA_ROLE) for i in range(self.library_selection.count())]

    def _add_library_element_to_list(self, element: RegulationGroup | PlanObject):
        logger.debug("Adding library element to list element=%s", str(element))
        item = QListWidgetItem(str(element))
        item.setToolTip(element.as_tooltip())
        item.setData(DATA_ROLE, element)
        self.library_element_list.addItem(item)

    def _on_filter_elements(self) -> None:
        search_text = self.library_element_filter.value().lower()
        logger.debug("Filtering library elements search_text=%s", search_text)
        for index in range(self.library_element_list.count()):
            item = self.library_element_list.item(index)
            item.setHidden(search_text not in item.text().lower())

    def _update_active_library_templates_from_view(self):
        """Reconstruct active library's elements from all remaining list items."""
        if not self.active_library:
            return

        new_elements = [
            self.library_element_list.item(i).data(DATA_ROLE) for i in range(self.library_element_list.count())
        ]
        setattr(self.active_library, self.library_element_property, new_elements)
        self.library_elements_updated.emit(new_elements)
        logger.debug(
            "Updated active library templates from view library=%s count=%s",
            self.active_library.name,
            len(new_elements),
        )

    def _update_template_view(self):
        logger.debug("Updating template view")
        self.library_element_list.clear()
        if not self.active_library:
            return

        for element in getattr(self.active_library, self.library_element_property, []):
            self._add_library_element_to_list(element)

        self._on_filter_elements()
        logger.debug("Template view updated item_count=%s", self.library_element_list.count())

    def _on_new_regulation_group_clicked(self):
        if not self.active_library:
            return

        logger.debug("Creating new regulation group template")

        form = PlanRegulationGroupForm(RegulationGroup(), None)
        form.setWindowTitle("Luo kaavamääräysryhmäpohja")

        # TODO: Let user select a category for their regulation group template?
        if form.exec_():
            self._add_library_element_to_list(form.model)
            self._update_active_library_templates_from_view()
            self.unsaved_libraries.add(self.active_library.name)
            self.save_library_btn.setEnabled(True)
            logger.debug("New regulation group template added library=%s", self.active_library.name)

    def _on_new_plan_feature_clicked(self, plan_feature_type: str, plan_feature_layer: str):
        if not self.active_library:
            return

        logger.debug(
            "Creating new plan feature template feature_type=%s layer=%s",
            plan_feature_type,
            plan_feature_layer,
        )

        form = PlanObjectForm(
            plan_feature=PlanObject(layer_name=plan_feature_layer),
            form_title=f"Luo kaavakohdepohja ({plan_feature_type})",
            regulation_group_libraries=self.regulation_group_libraries,
            template_form=True,
        )

        if form.exec_():
            self._add_library_element_to_list(form.model)
            self._update_active_library_templates_from_view()
            self.unsaved_libraries.add(self.active_library.name)
            self.save_library_btn.setEnabled(True)
            logger.debug("New plan feature template added library=%s", self.active_library.name)

    def _on_edit_element_clicked(self):
        selected_items = self.library_element_list.selectedItems()
        logger.debug("Edit library element requested selected_count=%s", len(selected_items))
        if len(selected_items) == 0:
            return
        if len(selected_items) > 1:
            iface.messageBar().pushWarning("", "Valitse vain yksi pohja kerrallaan muokkaamista varten.")
            return

        selected_item = selected_items[0]
        element = selected_item.data(DATA_ROLE)

        if self.library_type_class is PlanFeatureLibrary:
            title = "Muokkaa kaavakohdepohjaa"
            # Find correct plan feature type for the plan feature template to be edited
            for plan_feature_type, plan_feature_layer in FEATURE_TYPE_TO_LAYER_NAME.items():
                if plan_feature_layer == element.layer_name:
                    title = f"Muokkaa kaavakohdepohjaa ({plan_feature_type})"
                    break
            form = PlanObjectForm(element, title, self.regulation_group_libraries)
        elif self.library_type_class is RegulationGroupLibrary:
            form = PlanRegulationGroupForm(element, None)
            form.setWindowTitle("Muokkaa kaavamääräysryhmäpohjaa")
        else:
            return

        if form.exec_() and element.data_hash() != form.model.data_hash():
            selected_item.setData(DATA_ROLE, form.model)

            self._update_active_library_templates_from_view()
            self._update_template_view()
            self.unsaved_libraries.add(self.active_library.name)
            self.save_library_btn.setEnabled(True)
            logger.debug("Library element edited library=%s", self.active_library.name)

    def _on_delete_element_clicked(self):
        selected_items = self.library_element_list.selectedItems()
        logger.debug("Delete library elements requested selected_count=%s", len(selected_items))
        if len(selected_items) == 0:
            return

        if self.library_type_class is PlanFeatureLibrary:
            if len(selected_items) == 1:
                title = "Kaavakohdepohjan poisto"
                text = "Haluatko varmasti poistaa kaavakohdepohjan?"
            else:
                title = "Kaavakohdepohjien poisto"
                text = "Haluatko varmasti poistaa kaavakohdepohjat?"
        elif self.library_type_class is RegulationGroupLibrary:
            if len(selected_items) == 1:
                title = "Kaavamääräysryhmäpohjan poisto"
                text = "Haluatko varmasti poistaa kaavamääräysryhmäpohjan?"
            else:
                title = "Kaavamääräysryhmäpohjien poisto"
                text = "Haluatko varmasti poistaa kaavamääräysryhmäpohjat?"
        else:
            return

        if QMessageBox.question(None, title, text, QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            # Remove selected items from list view
            for item in selected_items:
                self.library_element_list.takeItem(self.library_element_list.row(item))

            self._update_active_library_templates_from_view()
            self.save_library_btn.setEnabled(True)
            self.unsaved_libraries.add(self.active_library.name)
            logger.debug("Deleted library elements and marked library unsaved name=%s", self.active_library.name)

    def _check_form(self) -> bool | None:
        file_path = self.library_file_path.filePath()
        library_name = self.library_name.text()
        current_library: Library = self.library_selection.currentData(DATA_ROLE)
        current_libraries = self.get_current_libraries()
        other_library_names = {library.name for library in current_libraries if library is not current_library}
        other_library_file_paths = {
            library.file_path for library in current_libraries if library is not current_library
        }

        # Check for missing filepath
        if not file_path:
            logger.warning("Library save validation failed: missing file path")
            QMessageBox.critical(self, "Virhe", "Kirjastolle ei ole asetettu tiedostopolkua.")
            return False
        # Check for duplicate filepaths
        if file_path in other_library_file_paths:
            logger.warning("Library save validation failed: duplicate file path path=%s", file_path)
            QMessageBox.critical(
                self,
                "Virhe",
                f"Useammalle kirjastolle on määritelty sama tallennuspolku ({file_path}).",
            )
            return False
        # Check for missing name
        if not library_name:
            logger.warning("Library save validation failed: missing name")
            QMessageBox.critical(self, "Virhe", "Kirjastolle ei ole asetettu nimeä.")
            return False
        # Check for duplicate names
        if library_name in other_library_names:
            logger.warning("Library save validation failed: duplicate name=%s", library_name)
            QMessageBox.critical(
                self,
                "Virhe",
                f"Useammalle kirjastolle on määritelty sama nimi ({library_name}).",
            )
            return False

        return True

    def _on_save_library_clicked(self):
        logger.debug("Save library requested")
        if self._check_form():
            current_library: PlanFeatureLibrary | RegulationGroupLibrary = self.library_selection.currentData(DATA_ROLE)
            current_library_old_name = current_library.name
            current_library.name = self.library_name.text()
            current_library.file_path = self.library_file_path.filePath()
            current_library.description = self.library_description.toPlainText()

            if isinstance(current_library, RegulationGroupLibrary):
                TemplateManager.write_regulation_group_template_file(
                    current_library.into_template_dict(), Path(current_library.file_path)
                )
            elif isinstance(current_library, PlanFeatureLibrary):
                TemplateManager.write_plan_feature_template_file(
                    current_library.into_template_dict(), Path(current_library.file_path)
                )
            logger.debug("Library saved name=%s file_path=%s", current_library.name, current_library.file_path)
            iface.messageBar().pushSuccess("", f"Kirjasto {self.library_name.text()} tallennettu.")

            if current_library_old_name in self.unsaved_libraries:
                self.unsaved_libraries.remove(current_library_old_name)
            self.save_library_btn.setEnabled(False)
            logger.debug("Library marked as saved name=%s", current_library.name)
