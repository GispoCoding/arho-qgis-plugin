from __future__ import annotations

from importlib import resources
from typing import TYPE_CHECKING

from qgis.PyQt import uic
from qgis.PyQt.QtCore import QStringListModel
from qgis.PyQt.QtWidgets import QDialog, QListView, QMessageBox, QProgressBar

from arho_feature_template.core.lambda_service import LambdaService
from arho_feature_template.utils.misc_utils import get_active_plan_id

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

        # Prepare errors and warnings for display
        new_errors = []
        validation_errors = post_json.get("ryhti_responses", {})
        for error_data in validation_errors.values():
            if isinstance(error_data, dict):
                # Get the errors
                errors = error_data.get("errors", [])
                for error in errors:
                    rule_id = error.get("ruleId", "Tuntematon sääntö")
                    message = error.get("message", "Ei viestiä")
                    instance = error.get("instance", "Tuntematon instance")
                    error_message = f"Validointivirhe - Sääntö: {rule_id}, Viesti: {message}, Instance: {instance}"
                    new_errors.append(error_message)

                # Get warnings
                warnings = error_data.get("warnings", [])
                new_errors.extend([f"Varoitus: {warning}" for warning in warnings])

        # If no errors or warnings, display a success message
        if not new_errors:
            new_errors.append("Kaava on validi. Ei virheitä tai varoituksia havaittu.")

        # Update the list view with errors and warnings
        self.validation_list_model.setStringList(new_errors)

        # Hide progress bar and re-enable the button
        self.progress_bar.hide()
        self.export_button.setEnabled(True)
