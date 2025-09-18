from __future__ import annotations

import logging
from importlib import resources
from typing import TYPE_CHECKING

from qgis.core import QgsExpressionContextUtils, QgsProject
from qgis.gui import QgsDockWidget
from qgis.PyQt import uic

from arho_feature_template.core.lambda_service import LambdaService
from arho_feature_template.core.settings_manager import SettingsManager
from arho_feature_template.utils.misc_utils import get_active_plan_id, iface

if TYPE_CHECKING:
    from qgis.PyQt.QtWidgets import QLabel, QProgressBar, QPushButton

    from arho_feature_template.gui.components.validation_tree_view import ValidationTreeView

logger = logging.getLogger(__name__)

ui_path = resources.files(__package__) / "validation_dock.ui"
DockClass, _ = uic.loadUiType(ui_path)


class ValidationDock(QgsDockWidget, DockClass):  # type: ignore
    progress_bar: QProgressBar
    validation_result_tree_view: ValidationTreeView
    validate_button: QPushButton
    validate_plan_matter_button: QPushButton
    validation_label: QLabel

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.lambda_service = LambdaService()
        self.lambda_service.validation_received.connect(self.list_validation_errors)
        self.lambda_service.validation_failed.connect(self.handle_validation_call_errors)
        self.validate_button.clicked.connect(self.validate_plan)
        self.validate_plan_matter_button.clicked.connect(self.validate_plan_matter)

        self.enable_validation()

        if not SettingsManager.get_service_bus_enabled():
            self.validate_plan_matter_button.hide()

    def handle_validation_call_errors(self, error: str):
        self.validation_label.setText("Kaavan validoinnissa tapahtui virhe.")
        self.validation_label.setStyleSheet("QLabel {color: red}")

        logger.warning("Kaavan validoinnissa tapahtui virhe: %s", error)

        self.enable_validation()

    def on_permanent_identifier_set(self, identifier: str | None):
        """Enable the validate plan matter button when a valid permanent identifier is received."""
        if identifier:
            self.validate_plan_matter_button.setEnabled(True)
            self.validate_plan_matter_button.setToolTip("Lähetä liitteet Ryhtiin ja validoi kaava-asia")
        else:
            self.validate_plan_matter_button.setEnabled(False)
            self.validate_plan_matter_button.setToolTip("Hae ensin pysyvä kaavatunnus")

    def validate_plan(self):
        """Handles the button press to trigger the validation process."""

        self.validation_label.setText("Kaavan validointivirheet:")
        self.validation_label.setStyleSheet("")

        # Clear the existing errors from the list view
        self.validation_result_tree_view.clear_errors()

        active_plan_id = get_active_plan_id()
        if not active_plan_id:
            iface.messageBar().pushMessage("Virhe", "Ei aktiivista kaavaa.", level=3)
            return

        # Disable buttons and show progress bar
        self.validate_button.setEnabled(False)
        self.validate_plan_matter_button.setEnabled(False)
        self.progress_bar.setVisible(True)

        self.lambda_service.validate_plan(active_plan_id)

    def validate_plan_matter(self):
        """Handles the button press to trigger the plan matter validation process."""

        self.validation_label.setText("Kaava-asian validointivirheet:")
        self.validation_label.setStyleSheet("")

        # Clear the existing errors from the list view
        self.validation_result_tree_view.clear_errors()

        active_plan_id = get_active_plan_id()
        if not active_plan_id:
            iface.messageBar().pushMessage("Virhe", "Ei aktiivista kaavaa-asiaa.", level=3)
            return

        # Disable buttons and show progress bar
        self.validate_plan_matter_button.setEnabled(False)
        self.validate_button.setEnabled(False)
        self.progress_bar.setVisible(True)

        self.lambda_service.validate_plan_matter(active_plan_id)

    def enable_validation(self):
        """Hide progress bar and re-enable the button"""
        self.progress_bar.setVisible(False)
        self.validate_button.setEnabled(True)

        # Retrieve the permanent_identifier from project variables
        permanent_identifier = QgsExpressionContextUtils.projectScope(QgsProject.instance()).variable(
            "permanent_identifier"
        )

        # Check if validate_plan_matter_button should be enabled
        if permanent_identifier:
            self.validate_plan_matter_button.setEnabled(True)
        else:
            self.validate_plan_matter_button.setEnabled(False)

        # Ensure the validation results are visible and properly resized
        self.validation_result_tree_view.expandAll()
        self.validation_result_tree_view.resizeColumnToContents(0)

    def list_validation_errors(self, validation_json):
        """Slot for listing validation errors and warnings."""

        if not validation_json:
            iface.messageBar().pushMessage("Virhe", "Validaatio json puuttuu.", level=1)
            self.enable_validation()
            return

        # If no errors or warnings, display a message and exit
        if not any(validation_json.values()):
            iface.messageBar().pushMessage("Virhe", "Ei virheitä havaittu.", level=1)
            self.enable_validation()
            return

        for error_data in validation_json.values():
            if not isinstance(error_data, dict):
                continue

            errors = error_data.get("errors") or []
            for error in errors:
                self.validation_result_tree_view.add_error(
                    error.get("ruleId", ""),
                    error.get("instance", ""),
                    error.get("message", ""),
                )

            warnings = error_data.get("warnings") or []
            for warning in warnings:
                self.validation_result_tree_view.add_warning(
                    warning.get("ruleId", ""),
                    warning.get("instance", ""),
                    warning.get("message", ""),
                )

        # Always enable validation at the end
        self.enable_validation()
