from __future__ import annotations

from collections import defaultdict
from importlib import resources
from typing import TYPE_CHECKING

from qgis.core import QgsApplication
from qgis.PyQt import uic
from qgis.PyQt.QtCore import pyqtSignal
from qgis.PyQt.QtGui import QFont, QIcon
from qgis.PyQt.QtWidgets import QLabel, QLineEdit, QWidget

from arho_feature_template.qgis_plugin_tools.tools.resources import plugin_path

if TYPE_CHECKING:
    from qgis.gui import QgsCollapsibleGroupBox
    from qgis.PyQt.QtWidgets import QGridLayout, QPushButton

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
        self.heading: QLineEdit
        self.conf_btn: QPushButton
        self.del_btn: QPushButton

        self.plan_regulation_groupbox: QgsCollapsibleGroupBox
        self.plan_regulation_grid_layout: QGridLayout

        # INIT
        self.feature = feature
        self.layer = self.feature.layer  # Should be plan_regulation_group layer

        self.input_value_header = None
        self.input_value_col = None

        self.additional_information_header = None
        self.additional_information_col = None

        self.bold_font = QFont()
        self.bold_font.setBold(True)

        self.init_buttons()

        self.attribute_widgets: dict[str, dict[str, QWidget]] = defaultdict(dict)

        for attribute_config in feature.attributes:
            if attribute_config.attribute == "name":
                self.heading.setText(attribute_config.display())

        if feature.child_features is not None:
            for child in feature.child_features:
                if child.layer == "plan_requlation":
                    self.create_widgets_for_plan_regulation(child)

    def request_delete(self):
        self.delete_signal.emit(self)

    def init_buttons(self):
        self.conf_btn.setIcon(QIcon(plugin_path("resources", "icons", "settings.svg")))
        self.del_btn.setIcon(QgsApplication.getThemeIcon("mActionDeleteSelected.svg"))
        self.del_btn.clicked.connect(self.request_delete)

    def create_widgets_for_plan_regulation(self, plan_regulation_feature: Feature):
        row = self.plan_regulation_grid_layout.rowCount() + 1
        for plan_regulation_config in plan_regulation_feature.attributes:
            if plan_regulation_config.attribute == "type_of_plan_regulation_id":
                id_label = QLabel(plan_regulation_config.display())
                # print(plan_regulation_config)
                self.plan_regulation_grid_layout.addWidget(id_label, row, 0)
            elif plan_regulation_config.attribute == "numeric_default":
                if not self.input_value_header:
                    self.input_value_header = QLabel("Arvo")
                    self.input_value_header.setFont(self.bold_font)
                    self.input_value_col = self.plan_regulation_grid_layout.columnCount() + 1
                    self.plan_regulation_grid_layout.addWidget(self.input_value_header, 0, self.input_value_col)

                input_field = QLineEdit()
                self.plan_regulation_grid_layout.addWidget(input_field, row, self.input_value_col)

        if plan_regulation_feature.child_features is None:
            return
        for child in plan_regulation_feature.child_features:
            # Additional information here, what else?
            # Assume attribute is "additional_information_of_plan_regulation"
            # NOTE: Could additional information be attribute of plan regulation instead of child feature?

            # Add header if not added yet
            if not self.additional_information_header:
                self.additional_information_header = QLabel("Lisätiedot")
                self.additional_information_header.setFont(self.bold_font)
                self.additonal_information_col = self.plan_regulation_grid_layout.columnCount() + 1
                self.plan_regulation_grid_layout.addWidget(
                    self.additional_information_header, 0, self.additonal_information_col
                )

            # TBD: Multiple additional feature per plan regulation
            for attribute in child.attributes:
                # Assume "type_of_additional_information_id"
                additional_information_label = QLabel(attribute.display())
                self.plan_regulation_grid_layout.addWidget(
                    additional_information_label, row, self.additonal_information_col
                )
