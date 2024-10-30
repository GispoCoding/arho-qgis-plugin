from __future__ import annotations

from importlib import resources
from typing import TYPE_CHECKING

from qgis.PyQt import uic
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QSizePolicy,
    QToolButton,
    QWidget,
)

from arho_feature_template.qgis_plugin_tools.tools.resources import plugin_path

if TYPE_CHECKING:
    from qgis.PyQt.QtWidgets import QFormLayout

    from arho_feature_template.core.template_library_config import Feature

ui_path = resources.files(__package__) / "plan_regulation_widget.ui"
FormClass, _ = uic.loadUiType(ui_path)


class PlanRegulationWidget(QWidget, FormClass):  # type: ignore
    """A widget representation of a plan regulation group."""

    def __init__(self, feature: Feature):
        super().__init__()
        self.setupUi(self)

        # TYPES
        self.regulation_kind: QLineEdit
        self.form_layout: QFormLayout = self.layout()

        # INITI
        self.feature = feature
        self.initialize_fields()

    def initialize_fields(self):
        for plan_regulation_config in self.feature.attributes:
            # Set regulation type / kind
            if plan_regulation_config.attribute == "type_of_plan_regulation_id":
                self.regulation_kind.setText(plan_regulation_config.display())

            elif plan_regulation_config.attribute == "numeric_default":
                self.add_quantity_input()

            # elif plan_regulation_config.attribute == "text???":
            #     self.add_text_input()

        if self.feature.child_features is None:
            return

        for child in self.feature.child_features:
            # Additional information here, what else?
            # Assume attribute is "additional_information_of_plan_regulation"
            # NOTE: Could additional information be attribute of plan regulation instead of child feature?

            # TBD: Multiple additional feature per plan regulation
            for attribute in child.attributes:
                # Assume "type_of_additional_information_id"
                self.add_additional_information_field(attribute.display())

    def add_additional_information_field(self, default_value: str | None = None):
        label = QLabel("Lisätieto", self)
        horizontal_layout = QHBoxLayout(self)
        line_edit = QLineEdit(self)
        if default_value:
            line_edit.setText(default_value)
        conf_btn = QPushButton(self)
        conf_btn.setIcon(QIcon(plugin_path("resources", "icons", "settings.svg")))
        horizontal_layout.addWidget(line_edit)
        horizontal_layout.addWidget(conf_btn)
        self.form_layout.addRow(label, horizontal_layout)

    def add_quantity_input(self, quantity_types: list[str] | None = None):
        label = QLabel("Arvo", self)
        line_edit = QLineEdit(self)
        if quantity_types:
            quantity_types_selection = QComboBox(self)
            quantity_types_selection.addItems(quantity_types)
            horizontal_layout = QHBoxLayout(self)
            horizontal_layout.addItem(line_edit)
            horizontal_layout.addItem(quantity_types_selection)
            self.form_layout.addRow(label, horizontal_layout)
        else:
            self.form_layout.addRow(label, line_edit)
        # TODO: Input validation

    def add_text_input(self):
        label = QLabel("Arvo", self)
        horizontal_layout = QHBoxLayout(self)
        text_edit = QPlainTextEdit(self)
        text_edit.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Preferred)
        open_btn = QToolButton(self)
        horizontal_layout.addWidget(text_edit)
        horizontal_layout.addWidget(open_btn)
        self.form_layout.addRow(label, horizontal_layout)
