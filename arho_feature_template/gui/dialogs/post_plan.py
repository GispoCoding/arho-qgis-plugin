from __future__ import annotations

from importlib import resources
from typing import TYPE_CHECKING

from qgis.core import Qgis
from qgis.PyQt import uic
from qgis.PyQt.QtCore import QTimer
from qgis.PyQt.QtWidgets import QDialog, QDialogButtonBox, QFrame, QLabel, QMessageBox, QProgressBar

from arho_feature_template.core.lambda_service import LambdaService
from arho_feature_template.utils.misc_utils import get_active_plan_id, iface

if TYPE_CHECKING:
    from arho_feature_template.gui.components.validation_tree_view import ValidationTreeView

# Load the UI file
ui_path = resources.files(__package__) / "post_plan.ui"
FormClass, _ = uic.loadUiType(ui_path)


class PostPlanDialog(QDialog, FormClass):  # type: ignore
    validation_error_frame: QFrame
    validation_label: QLabel
    validation_result_tree_view: ValidationTreeView
    progress_bar: QProgressBar
    dialogButtonBox: QDialogButtonBox  # noqa: N815

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setupUi(self)

        self.validation_error_frame.hide()
        self.progress_bar.hide()
        self.adjustSize()

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
            QMessageBox.critical(self, "Virhe", "Ei aktiivista kaavasuunnitelmaa.")
            self.reject()
            return

        self.lambda_service.post_plan_matter(plan_id)

    def update_message_list(self, post_json):
        self.progress_bar.hide()
        self.validation_result_tree_view.clear_errors()

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
            if success_found and warnings_found and not errors_found:
                self.validation_label.setText("Kaava-asia vietiin Ryhtiin, mutta se sisälsi varoituksia:")
            self.validation_error_frame.show()
            self.validation_result_tree_view.expandAll()
            self.validation_result_tree_view.resizeColumnToContents(0)
        else:
            self.accept()

        # Notify user weather the post was successful or not.
        if success_found:
            iface.messageBar().pushMessage("Kaava-asia viety Ryhtiin onnistuneesti", level=Qgis.Success)
        else:
            iface.messageBar().pushMessage("Virhe, kaava-asiaa ei toimitettu Ryhtiin.", level=Qgis.Critical)
