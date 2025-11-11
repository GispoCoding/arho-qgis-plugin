from __future__ import annotations

from importlib import resources
from typing import TYPE_CHECKING, Generator

from qgis.core import QgsApplication
from qgis.gui import QgsDockWidget
from qgis.PyQt import uic
from qgis.PyQt.QtCore import QModelIndex, QRegularExpression, QSortFilterProxyModel, Qt, pyqtSignal
from qgis.PyQt.QtGui import QStandardItem, QStandardItemModel
from qgis.PyQt.QtWidgets import QHeaderView, QMenu, QMessageBox, QPushButton, QTableView

from arho_feature_template.core.models import RegulationGroup, RegulationGroupLibrary
from arho_feature_template.project.layers.plan_layers import plan_feature_layers
from arho_feature_template.utils.misc_utils import disconnect_signal, iface

if TYPE_CHECKING:
    from qgis.gui import QgsFilterLineEdit
    from qgis.PyQt.QtWidgets import QWidget


ui_path = resources.files(__package__) / "regulation_groups_dock.ui"
DockClass, _ = uic.loadUiType(ui_path)


# COLUMNS
DATA_COLUMN = 0
DATA_ROLE = Qt.UserRole


class RegulationGroupsDockFilterProxyModel(QSortFilterProxyModel):
    def __init__(self, model: QStandardItemModel):
        super().__init__()
        self.setSourceModel(model)
        self.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.allowed_types: set[str] = set()

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:  # noqa: N802
        model: QStandardItemModel = self.sourceModel()
        if not model:
            return False

        # Filter by text
        text_match = False
        filter_text = self.filterRegularExpression().pattern()
        if not filter_text:
            text_match = True
        else:
            for column in range(model.columnCount()):
                index = model.index(source_row, column, source_parent)
                data = model.data(index)
                if data and filter_text.lower() in data.lower():
                    text_match = True
                    break

        return text_match


class RegulationGroupsDock(QgsDockWidget, DockClass):  # type: ignore
    request_new_regulation_group_empty = pyqtSignal()
    request_new_regulation_group_template = pyqtSignal()

    request_edit_regulation_group = pyqtSignal(RegulationGroup)
    request_delete_regulation_groups = pyqtSignal(object)  # Type: list[RegulationGroup]
    request_remove_all_regulation_groups = pyqtSignal(object)  # Type: list[tuple[str, Generator[str]]]
    request_remove_selected_groups = pyqtSignal(
        object, object
    )  # Types: list[RegulationGroup],  list[tuple[str, Generator[str]]
    request_add_groups_to_features = pyqtSignal(
        object, object
    )  # Types: list[RegulationGroup],  list[tuple[str, Generator[str]]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        # TYPES
        self.filter_line: QgsFilterLineEdit
        self.dockWidgetContents: QWidget
        self.table: QTableView

        self.new_btn: QPushButton
        self.delete_btn: QPushButton
        self.edit_btn: QPushButton
        self.modify_selected_features_btn: QPushButton

        # INIT
        self.new_btn.setIcon(QgsApplication.getThemeIcon("mActionAdd.svg"))
        self.delete_btn.setIcon(QgsApplication.getThemeIcon("mActionDeleteSelected.svg"))
        self.edit_btn.setIcon(QgsApplication.getThemeIcon("mActionEditTable.svg"))

        self.regulation_group_list.setSelectionMode(self.regulation_group_list.ExtendedSelection)
        self.search_box.valueChanged.connect(self.filter_regulation_groups)

        new_regulation_group_menu = QMenu()
        self.new_group_empty_action = new_regulation_group_menu.addAction("Tyhjä")
        self.new_group_from_template_action = new_regulation_group_menu.addAction("Pohjasta")
        new_regulation_group_menu.addActions([self.new_group_empty_action, self.new_group_from_template_action])
        self.new_btn.setMenu(new_regulation_group_menu)

        plan_object_actions_menu = QMenu()
        self.add_selected_action = plan_object_actions_menu.addAction("Lisää valitut ryhmät valituille kohteille")
        self.remove_all_action = plan_object_actions_menu.addAction("Poista kaikki ryhmät valituilta kohteilta")
        self.remove_selected_action = plan_object_actions_menu.addAction("Poista valitut ryhmät valituilta kohteilta")
        self.modify_selected_features_btn.setMenu(plan_object_actions_menu)

        self._connect_signals()

        # Create the model
        self.model = QStandardItemModel()
        self.model.setColumnCount(3)
        self.model.setHorizontalHeaderLabels(
            [
                "Kirjaintunnus",
                "Otsikko",
                "Määräysten lkm.",
            ]
        )
        self.filter_proxy_model = RegulationGroupsDockFilterProxyModel(self.model)
        self.table.setModel(self.filter_proxy_model)
        self.table.resizeColumnsToContents()
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)

        self.selection_model = self.table.selectionModel()

        self.filter_line.textChanged.connect(self._filter_table)
        self.table.doubleClicked.connect(self._open_form)

    def _disconnect_signals(self):
        disconnect_signal(self.new_group_empty_action.triggered)
        disconnect_signal(self.new_group_from_template_action.triggered)
        disconnect_signal(self.edit_btn.clicked)
        disconnect_signal(self.delete_btn.clicked)
        disconnect_signal(self.remove_all_action.triggered)
        disconnect_signal(self.remove_selected_action.triggered)
        disconnect_signal(self.add_selected_action.triggered)

    def _connect_signals(self):
        self._disconnect_signals()

        self.new_group_empty_action.triggered.connect(self.request_new_regulation_group_empty.emit)
        self.new_group_from_template_action.triggered.connect(self.request_new_regulation_group_template.emit)
        self.edit_btn.clicked.connect(self.on_edit_btn_clicked)
        self.delete_btn.clicked.connect(self.on_delete_btn_clicked)
        self.remove_all_action.triggered.connect(self.on_remove_all_btn_clicked)
        self.remove_selected_action.triggered.connect(self.on_remove_selected_btn_clicked)
        self.add_selected_action.triggered.connect(self.on_add_selected_btn_clicked)

    def _filter_table(self):
        # Set text filter
        search_text = self.filter_line.text()
        regex = QRegularExpression(search_text) if search_text else QRegularExpression("")
        self.filter_proxy_model.setFilterRegularExpression(regex)
        self.filter_proxy_model.invalidateFilter()

    def update_regulation_groups(self, regulation_group_library: RegulationGroupLibrary):
        # Clear table
        self.model.setRowCount(0)

        for group in regulation_group_library.regulation_groups:
            self.model.appendRow(self._regulation_group_into_items(group))

    def _regulation_group_into_items(self, group: RegulationGroup) -> list[QStandardItem]:
        # Create items
        items = [
            QStandardItem(group.letter_code or ""),
            QStandardItem(group.heading or ""),
            QStandardItem(str(len(group.regulations))),
        ]

        # Set tooltips
        tooltip_text = group.as_tooltip(long=True)
        for item in items:
            item.setToolTip(tooltip_text)

        # Set data
        items[DATA_COLUMN].setData(group, DATA_ROLE)
        return items

    def get_selected_plan_object_ids(self) -> list[tuple[str, Generator[str]]]:
        """Returns selected plan object IDs for each plan object layer (name)."""
        return [(layer_class.name, layer_class.get_selected_feature_ids()) for layer_class in plan_feature_layers]

    def get_selected_regulation_groups(self) -> list[RegulationGroup]:
        groups: list[RegulationGroup] = []
        for proxy_index in self.selection_model.selectedRows(DATA_COLUMN):
            group = self._regulation_group_from_index(proxy_index)
            if group is not None:
                groups.append(group)
        return groups

    def on_edit_btn_clicked(self):
        selected = self.get_selected_regulation_groups()
        if len(selected) == 0:
            return
        if len(selected) == 1:
            self.request_edit_regulation_group.emit(selected[0])
        else:
            iface.messageBar().pushWarning("", "Valitse vain yksi kaavamääräysryhmä kerrallaan muokkaamista varten.")

    def _row_items_from_index(self, proxy_index: QModelIndex) -> list[QStandardItem]:
        if not proxy_index.isValid():
            return []
        model_index = self.filter_proxy_model.mapToSource(proxy_index)
        row = model_index.row()
        return [self.model.item(row, i) for i in range(self.model.columnCount())]

    def _regulation_group_from_index(self, proxy_index: QModelIndex) -> RegulationGroup | None:
        row_items = self._row_items_from_index(proxy_index)
        if len(row_items) == 0:
            return None
        return row_items[DATA_COLUMN].data(DATA_ROLE) or None

    def _open_form(self, index: QModelIndex):
        group_model = self._regulation_group_from_index(index)
        if not group_model:
            iface.messageBar().pushWarning("", "Kaavamääräysryhmää ei löytynyt.")
            return

        self.request_edit_regulation_group.emit(group_model)

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
        self.request_remove_all_regulation_groups.emit(self.get_selected_plan_object_ids())

    def on_remove_selected_btn_clicked(self):
        selected_groups = self.get_selected_regulation_groups()
        if len(selected_groups) > 0:
            self.request_remove_selected_groups.emit(selected_groups, self.get_selected_plan_object_ids())

    def on_add_selected_btn_clicked(self):
        selected_groups = self.get_selected_regulation_groups()
        if len(selected_groups) > 0:
            self.request_add_groups_to_features.emit(selected_groups, self.get_selected_plan_object_ids())

    def unload(self):
        self._disconnect_signals()

        disconnect_signal(self.request_new_regulation_group_empty)
        disconnect_signal(self.request_new_regulation_group_template)
        disconnect_signal(self.request_edit_regulation_group)
        disconnect_signal(self.request_delete_regulation_groups)
        disconnect_signal(self.request_remove_all_regulation_groups)
        disconnect_signal(self.request_remove_selected_groups)
        disconnect_signal(self.request_add_groups_to_features)
