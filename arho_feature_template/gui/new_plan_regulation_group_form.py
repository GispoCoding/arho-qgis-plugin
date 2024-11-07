from __future__ import annotations

from importlib import resources
from typing import TYPE_CHECKING

from qgis.core import QgsApplication
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog

from arho_feature_template.gui.new_plan_regulation_widget import NewPlanRegulationWidget

if TYPE_CHECKING:
    from qgis.PyQt.QtWidgets import QBoxLayout, QPushButton, QWidget

ui_path = resources.files(__package__) / "new_plan_regulation_group_form.ui"
FormClass, _ = uic.loadUiType(ui_path)


class NewPlanRegulationGroupForm(QDialog, FormClass):  # type: ignore
    """Form to create a new plan regulation group."""

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # TYPES
        self.add_plan_regulation_btn: QPushButton
        self.plan_regulations_scroll_area_contents: QWidget
        self.plan_regulations_layout: QBoxLayout

        # INIT
        self.add_plan_regulation_btn.clicked.connect(self.add_plan_regulation)
        self.add_plan_regulation_btn.setIcon(QgsApplication.getThemeIcon("mActionAdd.svg"))
        self.add_plan_regulation()

    def add_plan_regulation(self):
        index = self.plan_regulations_layout.count() - 2
        new_plan_regulation_widget = NewPlanRegulationWidget(self.plan_regulations_scroll_area_contents)
        new_plan_regulation_widget.delete_signal.connect(self.remove_plan_regulation_group)
        self.plan_regulations_layout.insertWidget(index, new_plan_regulation_widget)

    def remove_plan_regulation_group(self, plan_regulation_widget: NewPlanRegulationWidget):
        self.plan_regulations_layout.removeWidget(plan_regulation_widget)
        plan_regulation_widget.deleteLater()
