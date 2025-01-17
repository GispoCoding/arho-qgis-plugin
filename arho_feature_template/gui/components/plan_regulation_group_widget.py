from __future__ import annotations

from importlib import resources
from typing import TYPE_CHECKING

from qgis.core import QgsApplication
from qgis.PyQt import uic
from qgis.PyQt.QtCore import pyqtSignal
from qgis.PyQt.QtWidgets import QWidget

from arho_feature_template.core.models import Proposition, Regulation, RegulationGroup
from arho_feature_template.gui.components.plan_proposition_widget import PropositionWidget
from arho_feature_template.gui.components.plan_regulation_widget import RegulationWidget
from arho_feature_template.project.layers.code_layers import PlanRegulationGroupTypeLayer

if TYPE_CHECKING:
    from qgis.PyQt.QtWidgets import QFormLayout, QFrame, QLabel, QLineEdit, QPushButton

ui_path = resources.files(__package__) / "plan_regulation_group_widget.ui"
FormClass, _ = uic.loadUiType(ui_path)


class RegulationGroupWidget(QWidget, FormClass):  # type: ignore
    """A widget representation of a plan regulation group."""

    delete_signal = pyqtSignal(QWidget)

    def __init__(self, regulation_group_data: RegulationGroup, layer_name: str):
        super().__init__()
        self.setupUi(self)

        # TYPES
        self.frame: QFrame
        self.name: QLineEdit
        self.short_name: QLineEdit
        self.short_name_label: QLabel
        self.del_btn: QPushButton
        self.regulation_group_details_layout: QFormLayout

        # INIT
        self.regulation_group_data = regulation_group_data
        self.regulation_widgets: list[RegulationWidget] = [
            self.add_regulation_widget(regulation) for regulation in self.regulation_group_data.regulations
        ]
        self.proposition_widgets: list[PropositionWidget] = [
            self.add_proposition_widget(proposition) for proposition in self.regulation_group_data.propositions
        ]

        regulation_group_data.type_code_id = PlanRegulationGroupTypeLayer.get_id_by_feature_layer_name(layer_name)
        self.name.setText(self.regulation_group_data.name if self.regulation_group_data.name else "")
        self.short_name.setText(self.regulation_group_data.short_name if self.regulation_group_data.short_name else "")
        self.del_btn.setIcon(QgsApplication.getThemeIcon("mActionDeleteSelected.svg"))
        self.del_btn.clicked.connect(lambda: self.delete_signal.emit(self))

    def add_regulation_widget(self, regulation: Regulation) -> RegulationWidget:
        widget = RegulationWidget(regulation=regulation, parent=self.frame)
        widget.delete_signal.connect(self.delete_regulation_widget)
        self.frame.layout().addWidget(widget)
        return widget

    def delete_regulation_widget(self, regulation_widget: RegulationWidget):
        self.frame.layout().removeWidget(regulation_widget)
        self.regulation_widgets.remove(regulation_widget)
        regulation_widget.deleteLater()

    def add_proposition_widget(self, proposition: Proposition) -> PropositionWidget:
        widget = PropositionWidget(proposition=proposition, parent=self.frame)
        widget.delete_signal.connect(self.delete_proposition_widget)
        self.frame.layout().addWidget(widget)
        return widget

    def delete_proposition_widget(self, proposition_widget: RegulationWidget):
        self.frame.layout().removeWidget(proposition_widget)
        self.proposition_widgets.remove(proposition_widget)
        proposition_widget.deleteLater()

    def into_model(self) -> RegulationGroup:
        return RegulationGroup(
            type_code_id=self.regulation_group_data.type_code_id,
            name=self.name.text(),
            short_name=None if not self.short_name.text() else self.short_name.text(),
            color_code=self.regulation_group_data.color_code,
            regulations=[widget.into_model() for widget in self.regulation_widgets],
            propositions=[widget.into_model() for widget in self.proposition_widgets],
            id_=self.regulation_group_data.id_,
        )
