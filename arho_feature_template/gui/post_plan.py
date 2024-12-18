from __future__ import annotations

from importlib import resources
from typing import TYPE_CHECKING

from qgis.PyQt import uic
from qgis.PyQt.QtCore import QStringListModel
from qgis.PyQt.QtWidgets import QDialog, QListView, QMessageBox, QProgressBar

from arho_feature_template.core.lambda_service import LambdaService
from arho_feature_template.utils.misc_utils import form_validation_messages, get_active_plan_id

if TYPE_CHECKING:
    from qgis.PyQt.QtWidgets import QListView

# Load the UI file
ui_path = resources.files(__package__) / "post_plan.ui"
FormClass, _ = uic.loadUiType(ui_path)


class PostPlan(QDialog, FormClass):  # type: ignore
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setupUi(self)

        # Initialize list model and assign to the list view
        self.validation_list_model: QStringListModel = QStringListModel()
        self.validation_list_view: QListView = self.validationListView
        self.validation_list_view.setModel(self.validation_list_model)

        # Initialize progress bar
        self.progress_bar: QProgressBar = self.progressBar
        self.progress_bar.setRange(0, 0)  # Set to "busy" indicator mode initially
        self.progress_bar.hide()  # Hide initially

        # Initialize buttons
        self.export_button = self.exportButton
        self.export_button.clicked.connect(self.post_plan)
        self.dialogButtonBox.rejected.connect(self.reject)

    def post_plan(self):
        """Handles the 'Vie kaava' button logic."""
        # Disable the button to prevent multiple clicks
        self.export_button.setEnabled(False)
        self.progress_bar.show()

        plan_id = get_active_plan_id()
        self.lambda_service = LambdaService()
        self.lambda_service.post_received.connect(self.do_something)
        self.lambda_service.post_plan(plan_id)

    def do_something(self, post_json):
        """Handles the Lambda response."""
        if not post_json:
            self.progress_bar.hide()
            QMessageBox.critical(self, "Virhe", "Lambda palautti tyhjän vastauksen.")
            self.export_button.setEnabled(True)
            return

        # Clear previous validation messages
        self.validation_list_model.setStringList([])

        ryhti_responses = post_json.get("ryhti_responses", {})
        validation_messages = form_validation_messages(ryhti_responses)

        # Update the list view with errors and warnings
        self.validation_list_model.setStringList(validation_messages)

        # Hide progress bar and re-enable the button
        self.progress_bar.hide()
        self.export_button.setEnabled(True)
