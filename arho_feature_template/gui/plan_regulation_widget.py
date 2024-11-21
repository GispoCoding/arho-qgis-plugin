from __future__ import annotations

from collections import defaultdict
from importlib import resources
from typing import TYPE_CHECKING

from qgis.core import QgsApplication
from qgis.gui import QgsDoubleSpinBox, QgsFileWidget, QgsSpinBox
from qgis.PyQt import uic
from qgis.PyQt.QtCore import Qt, pyqtSignal
from qgis.PyQt.QtWidgets import (
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMenu,
    QSizePolicy,
    QTextEdit,
    QWidget,
)

from arho_feature_template.core.plan_regulation_config import PlanRegulationConfig, Unit, ValueType

if TYPE_CHECKING:
    from numbers import Number

    from qgis.PyQt.QtWidgets import QPushButton

    from arho_feature_template.core.plan_regulation_group_config import PlanRegulationDefinition

ui_path = resources.files(__package__) / "new_plan_regulation_widget.ui"
FormClass, _ = uic.loadUiType(ui_path)


# Related layer and field names to save information later on
LAYER_NAME = "Kaavamääräys"
TYPE_OF_PLAN_REGULATION_KIND_FIELD = "type_of_plan_regulation_kind"
NUMERIC_VALUE_FIELD = "numeric_value"
TYPE_OF_VERBAL_PLAN_REGULATION_FIELD = "type_of_verbal_plan_regulation"
UNIT_FIELD = "unit"
TEXT_VALUE_FIELD = "text_value"
REGULATION_TYPE_ADDITIONAL_INFORMATION_ID = "regulation_type_additional_information_id"


class PlanRegulationWidget(QWidget, FormClass):  # type: ignore
    """A widget representation of a plan regulation."""

    delete_signal = pyqtSignal(QWidget)

    def __init__(self, config: PlanRegulationConfig, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        # TYPES
        self.plan_regulation_name: QLineEdit
        self.form_layout: QFormLayout

        self.add_additional_information_btn: QPushButton
        self.add_regulation_number_btn: QPushButton
        self.add_file_btn: QPushButton
        self.del_btn: QPushButton

        # INIT
        self.config = config
        self.regulation_number_added = False
        # Key is related field name, value is 1) widget, 2) tuple of widget and default value
        # NOTE: Maybe this is not something needed? Instead, when user clicks Ok, write into a YAML
        # in a separate script?
        self.attribute_widgets: dict[str, QWidget | tuple[QWidget, str | Number]] = defaultdict(dict)
        self.plan_regulation_name.setText(config.name)
        self.plan_regulation_name.setReadOnly(True)
        self.init_value_fields()
        self.init_buttons()

    def populate_from_definition(self, definition: PlanRegulationDefinition):
        pass

    def init_value_fields(self):
        layout = QHBoxLayout()
        value_type = self.config.value_type
        if value_type:
            self._add_value_input(value_type, layout)

        unit = self.config.unit
        if unit:
            self._add_value_unit(unit, layout)

    def _add_value_input(self, value_type: ValueType, layout: QHBoxLayout):
        if value_type in [ValueType.DECIMAL, ValueType.POSITIVE_DECIMAL]:
            self.add_decimal_input(layout, value_type)
        elif value_type == ValueType.POSITIVE_INTEGER:
            self.add_positive_integer_input(layout)
        elif value_type == ValueType.POSITIVE_INTEGER_RANGE:
            self.add_positive_integer_range_input(layout)
        elif value_type == ValueType.VERSIONED_TEXT:
            self.add_versioned_text_input(layout)
        else:
            msg = f"Invalid input value type for plan regulation: {value_type}"
            raise ValueError(msg)

    def _add_value_unit(self, unit: Unit, layout: QHBoxLayout):
        # NOTE: Unit could also be suffix in the QgsSpinBox, could be clearer?
        unit_label = QLabel(unit.value)
        layout.addWidget(unit_label)

    def init_buttons(self):
        # DEL
        self.del_btn.setIcon(QgsApplication.getThemeIcon("mActionDeleteSelected.svg"))
        self.del_btn.clicked.connect(lambda: self.delete_signal.emit(self))

        # ADDITIONAL INFORMATION
        type_menu = QMenu("Tyyppi", self)
        type_menu_items = [
            "Pääkäyttötarkoitus",
            "Osa-alue",
            "Poisluettava käyttötarkoitus",
            "Väliaikainen määräys",
            "Vaihtoehtoinen",
            "Ohjeellinen sijainti",
            "Yhteystarve",
        ]

        for item in type_menu_items:
            action = type_menu.addAction(item)
            action.triggered.connect(lambda _, item=item: self.add_additional_info(item))

        signifigance_menu = QMenu("Merkittävyys", self)
        signifigance_menu_items = [
            "Kansainvälinen",
            "Valtakunnallinen",
            "Maakunnallinen",
            "Seudullinen",
            "Alueellinen",
            "Paikallinen",
        ]

        for item in signifigance_menu_items:
            action = signifigance_menu.addAction(item)
            action.triggered.connect(lambda _, item=item: self.add_additional_info(item))

        type_main_menu = QMenu(self)
        type_main_menu.addMenu(type_menu)
        type_main_menu.addMenu(signifigance_menu)
        self.add_additional_information_btn.setMenu(type_main_menu)

        # REGULATION NUMBER
        self.add_regulation_number_btn.clicked.connect(self.add_regulation_number)

        # ADD FILE
        self.add_file_btn.clicked.connect(self.add_file)

    def add_decimal_input(self, layout: QHBoxLayout, value_type: ValueType):
        value_widget = QgsDoubleSpinBox()
        label_text = "Desimaali"
        if value_type == ValueType.POSITIVE_DECIMAL:
            value_widget.setMinimum(0.0)
            label_text += " (positiivinen)"
        else:
            value_widget.setMinimum(-9999.9)
        value_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(value_widget)
        self.form_layout.addRow(label_text, layout)

    def add_positive_integer_input(self, layout: QHBoxLayout):
        value_widget = QgsSpinBox()
        value_widget.setMinimum(0)
        value_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(value_widget)
        self.form_layout.addRow("Kokonaisluku (positiivinen)", layout)

    def add_positive_integer_range_input(self, layout: QHBoxLayout):
        min_widget = QgsSpinBox()
        min_widget.setMinimum(0)
        max_widget = QgsSpinBox()
        max_widget.setMinimum(0)
        layout.addWidget(min_widget)
        dash_label = QLabel(" — ")
        dash_label.setAlignment(Qt.AlignCenter)
        dash_label.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        layout.addWidget(dash_label)
        layout.addWidget(max_widget)
        self.form_layout.addRow("Kokonaisluku arvoväli (positiivinen)", layout)

    def add_versioned_text_input(self, layout: QHBoxLayout):
        text_widget = QTextEdit()
        layout.addWidget(text_widget)
        self.form_layout.addRow("Kieliversioitu teksti", layout)

    def add_additional_info(self, info_type):
        info_type_label = QLineEdit(info_type)
        info_type_label.setReadOnly(True)
        self.form_layout.addRow("Lisätiedonlaji", info_type_label)

    def add_regulation_number(self):
        if not self.regulation_number_added:
            number_widget = QgsSpinBox()
            self.form_layout.addRow("Määräysnumero", number_widget)
            self.regulation_number_added = True

    def add_file(self):
        file_input = QgsFileWidget()
        self.form_layout.addRow("Liiteasiakirja", file_input)
