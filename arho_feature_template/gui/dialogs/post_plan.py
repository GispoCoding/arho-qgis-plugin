from __future__ import annotations

from importlib import resources

from qgis.core import Qgis
from qgis.PyQt import uic
from qgis.PyQt.QtCore import QTimer
from qgis.PyQt.QtWidgets import QDialog, QMessageBox, QProgressBar, QVBoxLayout

from arho_feature_template.core.lambda_service import LambdaService
from arho_feature_template.gui.docks.validation_tree_view import ValidationTreeView
from arho_feature_template.utils.misc_utils import get_active_plan_id, iface

# Load the UI file
ui_path = resources.files(__package__) / "post_plan.ui"
FormClass, _ = uic.loadUiType(ui_path)


class PostPlan(QDialog, FormClass):  # type: ignore
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setupUi(self)

        self.validation_result_tree_view = ValidationTreeView(self)
        self.mainLayout: QVBoxLayout = self.findChild(QVBoxLayout, "mainLayout")
        self.mainLayout.insertWidget(0, self.validation_result_tree_view)

        self.validation_result_tree_view.hide()
        self.progress_bar: QProgressBar = self.progressBar
        self.progress_bar.setRange(0, 0)
        self.progress_bar.hide()

        self.dialogButtonBox.rejected.connect(self.reject)

        self.lambda_service = LambdaService()
        self.lambda_service.plan_matter_received.connect(self.update_message_list)

        # Start the posting process after dialog is fully opened.
        QTimer.singleShot(0, self.start_post_plan)

    def start_post_plan(self):
        """Posts the plan matter after dialog has been opened."""
        self.progress_bar.show()

        plan_id = get_active_plan_id()
        if not plan_id:
            QMessageBox.critical(self, "Virhe", "Ei aktiivista kaavaa.")
            self.reject()
            return

        self.lambda_service.post_plan_matter(plan_id)

    def update_message_list(self, post_json):
        self.progress_bar.hide()
        self.validation_result_tree_view.clear_errors()
        self.validation_result_tree_view.hide()

        if not post_json:
            QMessageBox.critical(self, "Virhe", "Lambda palautti tyhjän vastauksen.")
            self.reject()
            return

        success_found = False
        errors_found = False
        warnings_found = False

        response = next(iter(post_json.values()), {})
        status = response.get("status")
        if status in [200, 201]:
            success_found = True

        for error in response.get("errors") or []:
            self.validation_result_tree_view.add_error(
                error.get("ruleId", ""), error.get("instance", ""), error.get("message", "")
            )
            errors_found = True

        for warning in response.get("warnings") or []:
            self.validation_result_tree_view.add_warning(
                warning.get("ruleId", ""), warning.get("instance", ""), warning.get("message", "")
            )
            warnings_found = True

        # If the response includes errors or warnings, show validation_result_tree_view.
        if errors_found or warnings_found:
            self.validation_result_tree_view.show()
            self.validation_result_tree_view.expandAll()
            self.validation_result_tree_view.resizeColumnToContents(0)
            self.resize(self.width(), 300)
        else:
            self.accept()

        # Notify user weather the post was successful or not.
        if success_found:
            iface.messageBar().pushMessage("Kaava-asia viety Ryhtiin onnistuneesti", level=Qgis.Success)
        else:
            iface.messageBar().pushMessage("Virhe, kaava-asiaa ei toimitettu Ryhtiin.", level=Qgis.Critical)
