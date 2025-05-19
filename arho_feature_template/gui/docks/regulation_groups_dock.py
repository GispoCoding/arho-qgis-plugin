from __future__ import annotations

from importlib import resources
from typing import TYPE_CHECKING, Generator

from qgis.core import QgsApplication
from qgis.gui import QgsDockWidget
from qgis.PyQt import uic
from qgis.PyQt.QtCore import Qt, pyqtSignal
from qgis.PyQt.QtWidgets import QListWidget, QListWidgetItem, QMessageBox, QPushButton

from arho_feature_template.core.models import RegulationGroup, RegulationGroupLibrary
from arho_feature_template.project.layers.plan_layers import plan_feature_layers
from arho_feature_template.utils.misc_utils import disconnect_signal, iface

if TYPE_CHECKING:
    from qgis.gui import QgsFilterLineEdit
    from qgis.PyQt.QtWidgets import QWidget


ui_path = resources.files(__package__) / "regulation_groups_dock.ui"
DockClass, _ = uic.loadUiType(ui_path)


class RegulationGroupsDock(QgsDockWidget, DockClass):  # type: ignore
    request_new_regulation_group = pyqtSignal()
    request_edit_regulation_group = pyqtSignal(RegulationGroup)
    request_delete_regulation_groups = pyqtSignal(object)  # Type: list[RegulationGroup]
    request_delete_all_regulation_groups = pyqtSignal(object)  # Type: list[tuple[str, Generator[str]]]
    request_add_groups_to_feats = pyqtSignal(
        object, object
    )  # Types: list[RegulationGroup],  list[tuple[str, Generator[str]]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        # TYPES
        self.search_box: QgsFilterLineEdit
        self.dockWidgetContents: QWidget
        self.regulation_group_list: QListWidget

        self.new_btn: QPushButton
        self.delete_btn: QPushButton
        self.edit_btn: QPushButton
        self.remove_all_btn: QPushButton
        self.add_all_btn: QPushButton

        # INIT
        self.new_btn.setIcon(QgsApplication.getThemeIcon("mActionAdd.svg"))
        self.delete_btn.setIcon(QgsApplication.getThemeIcon("mActionDeleteSelected.svg"))
        self.edit_btn.setIcon(QgsApplication.getThemeIcon("mActionEditTable.svg"))

        self.regulation_group_list.setSelectionMode(self.regulation_group_list.ExtendedSelection)
        self.search_box.valueChanged.connect(self.filter_regulation_groups)

        self.connect_buttons()

    def _disconnect_buttons(self):
        disconnect_signal(self.new_btn.clicked)
        disconnect_signal(self.edit_btn.clicked)
        disconnect_signal(self.delete_btn.clicked)
        disconnect_signal(self.remove_all_btn.clicked)
        disconnect_signal(self.add_all_btn.clicked)

    def connect_buttons(self):
        self._disconnect_buttons()

        self.new_btn.clicked.connect(self.request_new_regulation_group.emit)
        self.edit_btn.clicked.connect(self.on_edit_btn_clicked)
        self.delete_btn.clicked.connect(self.on_delete_btn_clicked)
        self.remove_all_btn.clicked.connect(self.on_remove_all_btn_clicked)
        self.add_all_btn.clicked.connect(self.on_add_all_btn_clicked)

    def update_regulation_groups(self, regulation_group_library: RegulationGroupLibrary):
        self.regulation_group_list.clear()

        for category in regulation_group_library.regulation_group_categories:
            for group in category.regulation_groups:
                self.add_regulation_group_to_list(group)

    def add_regulation_group_to_list(self, group: RegulationGroup):
        text = str(group)
        item = QListWidgetItem(text)
        item.setToolTip(text)
        item.setData(Qt.UserRole, group)
        self.regulation_group_list.addItem(item)

    def get_selected_regulation_groups(self) -> list[RegulationGroup]:
        return [item.data(Qt.UserRole) for item in self.regulation_group_list.selectedItems()]

    def on_edit_btn_clicked(self):
        selected = self.get_selected_regulation_groups()
        if len(selected) == 1:
            self.request_edit_regulation_group.emit(selected[0])
        else:
            iface.messageBar().pushWarning("", "Valitse vain yksi kaavamääräysryhmä kerrallaan muokkaamista varten.")

    def on_delete_btn_clicked(self):
        selected_groups = self.get_selected_regulation_groups()
        if len(selected_groups) > 0:
            response = QMessageBox.question(
                None,
                "Kaavamääräysryhmän poisto",
                "Haluatko varmasti poistaa kaavamääräysryhmän?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if response == QMessageBox.Yes:
                self.request_delete_regulation_groups.emit(selected_groups)

    def on_remove_all_btn_clicked(self):
        feats: list[tuple[str, Generator[str]]] = [
            (layer_class.name, layer_class.get_selected_feature_ids()) for layer_class in plan_feature_layers
        ]
        self.request_delete_all_regulation_groups.emit(feats)

    def on_add_all_btn_clicked(self):
        selected_groups = self.get_selected_regulation_groups()
        if len(selected_groups) > 0:
            feats: list[tuple[str, Generator[str]]] = [
                (layer_class.name, layer_class.get_selected_feature_ids()) for layer_class in plan_feature_layers
            ]
            self.request_add_groups_to_feats.emit(selected_groups, feats)

    def filter_regulation_groups(self) -> None:
        search_text = self.search_box.value().lower()
        for index in range(self.regulation_group_list.count()):
            item = self.regulation_group_list.item(index)
            item.setHidden(search_text not in item.text().lower())

    def unload(self):
        self._disconnect_buttons()

        disconnect_signal(self.request_new_regulation_group)
        disconnect_signal(self.request_edit_regulation_group)
        disconnect_signal(self.request_delete_regulation_groups)
        disconnect_signal(self.request_delete_all_regulation_groups)
        disconnect_signal(self.request_add_groups_to_feats)
