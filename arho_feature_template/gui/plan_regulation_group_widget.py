from __future__ import annotations

from importlib import resources
from typing import TYPE_CHECKING

from qgis.core import QgsApplication
from qgis.PyQt import uic
from qgis.PyQt.QtCore import pyqtSignal
from qgis.PyQt.QtWidgets import QWidget

from arho_feature_template.gui.plan_regulation_widget import PlanRegulationWidget

if TYPE_CHECKING:
    from qgis.PyQt.QtWidgets import QFrame, QLineEdit, QPushButton

    from arho_feature_template.core.template_library_config import Feature

ui_path = resources.files(__package__) / "plan_regulation_group_widget.ui"
FormClass, _ = uic.loadUiType(ui_path)


class PlanRegulationGroupWidget(QWidget, FormClass):  # type: ignore
    """A widget representation of a plan regulation group."""

    delete_signal = pyqtSignal(QWidget)

    def __init__(self, feature: Feature):
        super().__init__()
        self.setupUi(self)

        # TYPES
        self.frame: QFrame
        self.heading: QLineEdit
        self.del_btn: QPushButton

        # INIT
        self.feature = feature
        self.layer = self.feature.layer  # Should be plan_regulation_group layer

        self.init_buttons()
        self.set_group_heading()
        self.add_plan_regulation_widgets()

    def request_delete(self):
        self.delete_signal.emit(self)

    def init_buttons(self):
        self.del_btn.setIcon(QgsApplication.getThemeIcon("mActionDeleteSelected.svg"))
        self.del_btn.clicked.connect(self.request_delete)

    def set_group_heading(self):
        for attribute_config in self.feature.attributes:
            if attribute_config.attribute == "name":
                self.heading.setText(attribute_config.display())

    def add_plan_regulation_widgets(self):
        if self.feature.child_features is not None:
            for child in self.feature.child_features:
                if child.layer == "plan_requlation":
                    self.add_plan_regulation_widget(child)

    def add_plan_regulation_widget(self, plan_regulation_feature: Feature):
        plan_regulation_widget = PlanRegulationWidget(plan_regulation_feature)
        self.frame.layout().addWidget(plan_regulation_widget)
