from __future__ import annotations

from importlib import resources
from typing import TYPE_CHECKING

from qgis.PyQt import uic
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QComboBox, QDialog, QDialogButtonBox, QLineEdit

from arho_feature_template.core.models import Plan
from arho_feature_template.project.layers.code_layers import LifeCycleStatusLayer

if TYPE_CHECKING:
    from arho_feature_template.gui.components.code_combobox import CodeComboBox

ui_path = resources.files(__package__) / "new_plan_dialog.ui"
FormClass, _ = uic.loadUiType(ui_path)

DATA_ROLE = Qt.UserRole


class NewPlanDialog(QDialog, FormClass):  # type: ignore
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # TYPES
        self.plan_name: QLineEdit
        self.plan_lifecycle: CodeComboBox
        self.origin_version: QComboBox

        self.button_box: QDialogButtonBox

        # INIT
        self.plan = None

        self.plan_lifecycle.populate_from_code_layer(LifeCycleStatusLayer)
        self.plan_name.textChanged.connect(self._check_required_fields)
        self.plan_lifecycle.currentIndexChanged.connect(self._check_required_fields)
        self.button_box.accepted.connect(self._on_ok_clicked)

        self._check_required_fields()

    def _check_required_fields(self) -> None:
        ok_button = self.button_box.button(QDialogButtonBox.Ok)
        if self.plan_name.text() != "" and self.plan_lifecycle.value() is not None:
            ok_button.setEnabled(True)
        else:
            ok_button.setEnabled(False)

    def _on_ok_clicked(self):
        self.plan = Plan(name=self.plan_name.text(), lifecycle_status_id=self.plan_lifecycle.value())
        # Copy from version TODO

        self.accept()
