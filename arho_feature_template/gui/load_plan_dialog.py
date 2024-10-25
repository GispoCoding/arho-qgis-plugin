from importlib import resources

import psycopg2
from qgis.PyQt import uic
from qgis.PyQt.QtCore import QRegularExpression, QSortFilterProxyModel, Qt
from qgis.PyQt.QtGui import QStandardItem, QStandardItemModel
from qgis.PyQt.QtWidgets import QComboBox, QDialog, QLineEdit, QMessageBox, QPushButton, QTableView

from arho_feature_template.gui.ask_credentials import DbAskCredentialsDialog
from arho_feature_template.utils.db_utils import get_db_connection_params

ui_path = resources.files(__package__) / "load_plan_dialog.ui"

LoadPlanDialogBase, _ = uic.loadUiType(ui_path)


class PlanFilterProxyModel(QSortFilterProxyModel):
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


class LoadPlanDialog(QDialog, LoadPlanDialogBase):  # type: ignore
    def __init__(self, parent, connections):
        super().__init__(parent)

        uic.loadUi(ui_path, self)

        self.connectionComboBox: QComboBox = self.findChild(QComboBox, "connectionComboBox")
        self.planTableView: QTableView = self.findChild(QTableView, "planTableView")
        self.okButton: QPushButton = self.findChild(QPushButton, "okButton")

        self.searchLineEdit: QLineEdit = self.findChild(QLineEdit, "searchLineEdit")
        self.searchLineEdit.setPlaceholderText("Etsi kaavoja...")

        self.connectionComboBox.addItems(connections)

        self.connectionComboBox.currentIndexChanged.connect(self.load_plans)
        self.okButton.clicked.connect(self.accept)

        self.okButton.setEnabled(False)

        self.filterProxyModel = PlanFilterProxyModel(self)
        self.filterProxyModel.setFilterCaseSensitivity(Qt.CaseInsensitive)

        self.planTableView.setModel(self.filterProxyModel)
        self.searchLineEdit.textChanged.connect(self.filter_plans)

        self.selected_plan_id = None

    def load_plans(self):
        selected_connection = self.connectionComboBox.currentText()
        if not selected_connection:
            self.planTableView.setModel(QStandardItemModel())
            return

        cursor = None
        conn = None

        try:
            conn_params = get_db_connection_params(selected_connection)

            if not conn_params.get("user") or not conn_params.get("password"):
                # Trigger dialog to ask for missing credentials
                dialog = DbAskCredentialsDialog(self)
                dialog.rejected.connect(self.reject)
                if dialog.exec() == QDialog.Accepted:
                    user, password = dialog.get_credentials()
                    conn_params["user"] = user
                    conn_params["password"] = password

            conn = psycopg2.connect(
                host=conn_params["host"],
                port=conn_params["port"],
                dbname=conn_params["dbname"],
                user=conn_params["user"],
                password=conn_params["password"],
                sslmode=conn_params["sslmode"],
            )

            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    p.id,
                    p.producers_plan_identifier,
                    p.name ->> 'fin' AS name_fin,
                    l.name ->> 'fin' AS lifecycle_status_fin,
                    pt.name ->> 'fin' AS plan_type_fin
                FROM
                    hame.plan p
                LEFT JOIN
                    codes.lifecycle_status l
                ON
                    p.lifecycle_status_id = l.id
                LEFT JOIN
                    codes.plan_type pt
                ON
                    p.plan_type_id = pt.id;
            """)
            plans = cursor.fetchall()

            model = QStandardItemModel(len(plans), 5)
            model.setHorizontalHeaderLabels(
                [
                    "ID",
                    "Tuottajan kaavatunnus",
                    "Nimi",
                    "Kaavan elinkaaren tila",
                    "Kaavalaji",
                ]
            )

            for row_idx, plan in enumerate(plans):
                model.setItem(row_idx, 0, QStandardItem(str(plan[0])))  # id
                model.setItem(row_idx, 1, QStandardItem(str(plan[1])))  # producer_plan_identifier
                model.setItem(row_idx, 2, QStandardItem(str(plan[2])))  # name_fin
                model.setItem(row_idx, 3, QStandardItem(str(plan[3])))  # lifecycle_status_fin
                model.setItem(row_idx, 4, QStandardItem(str(plan[4])))  # plan_type_fin

            self.filterProxyModel.setSourceModel(model)

            self.planTableView.setSelectionMode(QTableView.SingleSelection)
            self.planTableView.setSelectionBehavior(QTableView.SelectRows)

            self.planTableView.selectionModel().selectionChanged.connect(self.on_selection_changed)

        except ValueError as ve:
            QMessageBox.critical(self, "Connection Error", str(ve))
            self.planTableView.setModel(QStandardItemModel())

        except Exception as e:  # noqa: BLE001
            QMessageBox.critical(self, "Error", f"Failed to load plans: {e}")
            self.planTableView.setModel(QStandardItemModel())

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def filter_plans(self):
        search_text = self.searchLineEdit.text()
        if search_text:
            search_regex = QRegularExpression(search_text)
            self.filterProxyModel.setFilterRegularExpression(search_regex)
        else:
            self.filterProxyModel.setFilterRegularExpression("")

    def on_selection_changed(self):
        # Enable the OK button only if a row is selected
        selection = self.planTableView.selectionModel().selectedRows()
        if selection:
            selected_row = selection[0].row()
            self.selected_plan_id = self.planTableView.model().index(selected_row, 0).data()
            self.okButton.setEnabled(True)
        else:
            self.selected_plan_id = None
            self.okButton.setEnabled(False)

    def get_selected_connection(self):
        return self.connectionComboBox.currentText()

    def get_selected_plan_id(self):
        return self.selected_plan_id
