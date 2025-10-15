from __future__ import annotations

from importlib import resources
from typing import Sequence

from qgis.core import QgsProviderRegistry
from qgis.PyQt import uic
from qgis.PyQt.QtCore import QRegularExpression, QSortFilterProxyModel, Qt
from qgis.PyQt.QtGui import QStandardItem, QStandardItemModel
from qgis.PyQt.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QHeaderView,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableView,
)

from arho_feature_template.exceptions import UnexpectedNoneError
from arho_feature_template.utils.misc_utils import get_active_plan_matter_id

ui_path = resources.files(__package__) / "load_plan_matter_dialog.ui"

LoadPlanMatterDialogBase, _ = uic.loadUiType(ui_path)


class PlanMatterFilterProxyModel(QSortFilterProxyModel):
    def __init__(self, model: QStandardItemModel):
        super().__init__()
        self.setSourceModel(model)
        self.setFilterCaseSensitivity(Qt.CaseInsensitive)

    def filterAcceptsRow(self, source_row, source_parent):  # noqa: N802
        model = self.sourceModel()
        if not model:
            return False

        filter_text = self.filterRegularExpression().pattern()
        if not filter_text:
            return True

        for column in range(5):
            index = model.index(source_row, column, source_parent)
            data = model.data(index)
            if data and filter_text.lower() in data.lower():
                return True

        return False


class LoadPlanMatterDialog(QDialog, LoadPlanMatterDialogBase):  # type: ignore
    connections_selection: QComboBox
    load_btn: QPushButton
    plan_matter_table_view: QTableView
    search_line_edit: QLineEdit
    button_box: QDialogButtonBox

    # ID_COLUMN = 4

    def __init__(self, parent, connection_names: list[str]):
        super().__init__(parent)
        self.setupUi(self)

        self._selected_plan_matter_id = None

        self.button_box.rejected.connect(self.reject)
        self.button_box.accepted.connect(self.accept)
        self.button_box.button(QDialogButtonBox.Ok).setEnabled(False)

        self.load_btn.clicked.connect(self.load_plan_matters)
        self.search_line_edit.textChanged.connect(self.filter_plan_matters)

        self.connections_selection.addItems(connection_names)

        self.plan_matter_table_view: QTableView
        self.plan_matter_table_view.setSelectionMode(QTableView.SingleSelection)
        self.plan_matter_table_view.setSelectionBehavior(QTableView.SelectRows)
        self.plan_matter_table_view.setSortingEnabled(True)

        self.model = QStandardItemModel()
        self.model.setColumnCount(4)
        self.model.setHorizontalHeaderLabels(["Nimi", "Kaava tyyppi", "Tuottajan kaavatunnus", "Pysyvä kaavatunnus"])

        self.filterProxyModel = PlanMatterFilterProxyModel(self.model)

        self.plan_matter_table_view.setModel(self.filterProxyModel)
        self.plan_matter_table_view.selectionModel().selectionChanged.connect(self.on_selection_changed)

        header = self.plan_matter_table_view.horizontalHeader()
        for i in range(3):
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # stretch name column

        # Show plans for the first connections by default
        # NOTE: Could be changed to the previously used connection if/when plugin can remember it
        if len(connection_names) > 0:
            self.load_plan_matters()

    def clear_table(self):
        self.model.removeRows(0, self.model.rowCount())

    def load_plan_matters(self):
        self.clear_table()

        selected_connection = self.connections_selection.currentText()
        if not selected_connection:
            return

        active_plan_matter_id = get_active_plan_matter_id()
        row_to_select = None
        plan_matters = self.get_plan_matters_from_db(selected_connection)
        for i, plan in enumerate(plan_matters):
            id_, name, plan_type, producers_plan_identifier, permanent_plan_identifier = plan
            self.model.appendRow(
                [
                    QStandardItem(name or ""),
                    QStandardItem(plan_type or ""),
                    QStandardItem(producers_plan_identifier or ""),
                    QStandardItem(permanent_plan_identifier or ""),
                ]
            )
            self.model.item(i, 0).setData(id_, Qt.UserRole)
            if active_plan_matter_id == id_:
                row_to_select = i

        if row_to_select is not None:
            self.plan_matter_table_view.selectRow(row_to_select)

    def get_plan_matters_from_db(self, selected_connection: str) -> Sequence[str]:
        """
        Loads plan matters from the selected DB connection.

        Returns plan information in the format [ID, name, plan_type, producers_plan_identifier, permanent_plan_identifier].
        """
        provider_registry = QgsProviderRegistry.instance()
        if provider_registry is None:
            raise UnexpectedNoneError
        postgres_provider_metadata = provider_registry.providerMetadata("postgres")
        if postgres_provider_metadata is None:
            raise UnexpectedNoneError

        try:
            connection = postgres_provider_metadata.createConnection(selected_connection)
            plan_matters = connection.executeSql("""
                SELECT
                    pm.id,
                    pm.name ->> 'fin',
                    pt.name ->> 'fin',
                    pm.producers_plan_identifier,
                    pm.permanent_plan_identifier
                FROM
                    hame.plan_matter pm
                    JOIN codes.plan_type pt
                        ON pm.plan_type_id = pt.id;
            """)
        except Exception as e:  # noqa: BLE001
            QMessageBox.critical(self, "Virhe", f"Kaava-asioiden lataus epäonnistui: {e}")
            self.clear_table()

        return plan_matters

    def filter_plan_matters(self):
        search_text = self.search_line_edit.text()
        if search_text:
            search_regex = QRegularExpression(search_text)
            self.filterProxyModel.setFilterRegularExpression(search_regex)
        else:
            self.filterProxyModel.setFilterRegularExpression("")

    def on_selection_changed(self):
        """
        Check active selection in `plan_matter_table_view`.

        Enable the OK button only if a row is selected.
        """
        selection = self.plan_matter_table_view.selectionModel().selectedRows()
        if selection:
            selected_row = selection[0].row()
            self._selected_plan_matter_id = self.plan_matter_table_view.model().index(selected_row, 0).data(Qt.UserRole)
            self.button_box.button(QDialogButtonBox.Ok).setEnabled(True)
        else:
            self._selected_plan_matter_id = None
            self.button_box.button(QDialogButtonBox.Ok).setEnabled(False)

    def get_selected_connection(self):
        return self.connections_selection.currentText()

    def get_selected_plan_matter_id(self):
        return self._selected_plan_matter_id
