from __future__ import annotations

from importlib import resources
from pathlib import Path
from typing import TYPE_CHECKING

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog, QDialogButtonBox, QLineEdit, QWidget

from arho_feature_template.core.lambda_service import LambdaService
from arho_feature_template.utils.misc_utils import get_active_plan_matter_id, iface

if TYPE_CHECKING:
    from qgis.gui import QgsFileWidget


ui_path = resources.files(__package__) / "import_plan_form.ui"
FormClass, _ = uic.loadUiType(ui_path)


class ImportPlanForm(QDialog, FormClass):  # type: ignore
    file_selection: QgsFileWidget
    line_edit_name: QLineEdit
    button_box_accept: QDialogButtonBox
    button_box_overwrite: QDialogButtonBox
    widget_input: QWidget
    widget_replace: QWidget
    widget_progress: QWidget

    def __init__(self, tr, parent: QWidget | None = None):
        super().__init__(parent)
        self.tr = tr

        self.setupUi(self)
        self.setModal(True)
        self.setFixedWidth(550)

        self.widget_replace.hide()
        self.widget_progress.hide()
        self.adjustSize()

        self.button_box_accept.accepted.connect(self.import_plan)
        self.button_box_accept.rejected.connect(self.reject)
        self.button_box_overwrite.accepted.connect(lambda: self.import_plan(overwrite=True))
        self.button_box_overwrite.rejected.connect(self.reject)

        self.file_selection.fileChanged.connect(self.check_inputs)
        self.line_edit_name.textChanged.connect(self.check_inputs)

        self.button_box_accept.button(QDialogButtonBox.Ok).setEnabled(False)

        self.lambda_service = LambdaService(self.tr)
        self.lambda_service.plan_imported.connect(self.plan_imported)
        self.lambda_service.plan_import_failed.connect(self.handle_import_failed)

        self.imported_plan_id: str | None = None
        self.plan_json: str | None = None
        self.extra_data: dict | None = None

    def check_inputs(self):
        """Enables ok/save button only if both file paths are defined."""
        if self.file_selection.filePath() and self.line_edit_name.text():
            self.button_box_accept.button(QDialogButtonBox.Ok).setEnabled(True)
        else:
            self.button_box_accept.button(QDialogButtonBox.Ok).setEnabled(False)

    def import_plan(self, overwrite: bool = False) -> None:  # noqa: FBT001, FBT002
        self.widget_input.hide()
        self.widget_replace.hide()
        self.widget_progress.show()
        self.adjustSize()

        if not self.plan_json:
            json_plan_path = Path(self.file_selection.filePath())
            if not json_plan_path.exists():
                return
            self.plan_json = json_plan_path.read_text(encoding="utf-8")

        if not self.extra_data:
            self.extra_data = {"name": self.line_edit_name.text(), "plan_matter_id": get_active_plan_matter_id()}

        self.lambda_service.import_plan(self.plan_json, self.extra_data, overwrite)

        return None

    def plan_imported(self, plan_id: str):
        self.imported_plan_id = plan_id
        self.accept()

    def handle_import_failed(self, error_message: str):
        """If error message is "plan already exists", prompt user if they want to overwrite the plan."""
        if "Plan already exists." in error_message:
            self.widget_progress.hide()
            self.widget_replace.show()
            self.adjustSize()

        else:
            iface.messageBar().pushCritical("", self.tr("Kaavasuunnitelman tuonti epäonnistui:") + f" {error_message}")
            self.reject()
