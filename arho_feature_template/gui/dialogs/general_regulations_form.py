from __future__ import annotations

import dataclasses
from importlib import resources
from typing import TYPE_CHECKING

from qgis.core import (
    QgsApplication,
)
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog

from arho_feature_template.core.models import Plan, RegulationGroup
from arho_feature_template.gui.components.general_regulation_group_widget import GeneralRegulationGroupWidget
from arho_feature_template.project.layers.plan_layers import PlanLayer
from arho_feature_template.utils.misc_utils import disconnect_signal, iface

if TYPE_CHECKING:
    from qgis.PyQt.QtWidgets import QDialogButtonBox, QPushButton, QVBoxLayout


ui_path = resources.files(__package__) / "general_regulations_form.ui"
FormClass, _ = uic.loadUiType(ui_path)


class GeneralRegulationsForm(QDialog, FormClass):  # type: ignore
    add_general_regulation_group_btn: QPushButton
    regulations_layout: QVBoxLayout
    button_box: QDialogButtonBox

    def __init__(self, plan: Plan):
        super().__init__(parent=iface.mainWindow())
        self.setupUi(self)

        self.plan = plan

        self.regulation_group_widgets: list[GeneralRegulationGroupWidget] = []
        for regulation_group in plan.general_regulations:
            self.add_plan_regulation_group(regulation_group)

        self.add_general_regulation_group_btn.clicked.connect(self.add_new_regulation_group)
        self.add_general_regulation_group_btn.setIcon(QgsApplication.getThemeIcon("mActionAdd.svg"))

        self.button_box.accepted.connect(self._on_ok_clicked)

    def add_new_regulation_group(self):
        self.add_plan_regulation_group(RegulationGroup())

    def add_plan_regulation_group(self, regulation_group: RegulationGroup):
        regulation_group_widget = GeneralRegulationGroupWidget(regulation_group, layer_name=PlanLayer.name)
        regulation_group_widget.delete_signal.connect(self.remove_plan_regulation_group)
        self.regulations_layout.insertWidget(1, regulation_group_widget)
        self.regulation_group_widgets.append(regulation_group_widget)

    def remove_plan_regulation_group(self, regulation_group_widget: GeneralRegulationGroupWidget):
        disconnect_signal(regulation_group_widget.delete_signal)
        self.regulations_layout.removeWidget(regulation_group_widget)
        self.regulation_group_widgets.remove(regulation_group_widget)
        regulation_group_widget.deleteLater()

    def into_model(self) -> Plan:
        model = dataclasses.replace(self.plan)
        model.general_regulations = [
            reg_group_widget.into_model() for reg_group_widget in self.regulation_group_widgets
        ]

        if not model.modified and model != self.plan:
            model.modified = True

        return model

    def _on_ok_clicked(self):
        self.model = self.into_model()
        self.accept()
