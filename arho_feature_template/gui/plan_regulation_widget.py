from __future__ import annotations

from importlib import resources
from typing import TYPE_CHECKING, cast

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
    QToolButton,
    QWidget,
)

from arho_feature_template.core.plan_regulation_config import PlanRegulationConfig, Unit, ValueType
from arho_feature_template.utils.misc_utils import get_additional_information_name

if TYPE_CHECKING:
    from qgis.PyQt.QtWidgets import QPushButton

    from arho_feature_template.core.plan_regulation_group_config import PlanRegulationDefinition

ui_path = resources.files(__package__) / "plan_regulation_widget.ui"
FormClass, _ = uic.loadUiType(ui_path)


# Related layer and field names to save information later on
LAYER_NAME = "Kaavamääräys"
TYPE_OF_PLAN_REGULATION_KIND_FIELD = "type_of_plan_regulation_kind"
NUMERIC_VALUE_FIELD = "numeric_value"
TYPE_OF_VERBAL_PLAN_REGULATION_FIELD = "type_of_verbal_plan_regulation"
UNIT_FIELD = "unit"
TEXT_VALUE_FIELD = "text_value"
REGULATION_TYPE_ADDITIONAL_INFORMATION_ID = "regulation_type_additional_information_id"

# TO BE REPLACED
ADDITIONAL_INFORMATION_TYPES_WITH_INPUT = ["kayttotarkoituskohdistus"]


class PlanRegulationWidget(QWidget, FormClass):  # type: ignore
    """A widget representation of a plan regulation."""

    delete_signal = pyqtSignal(QWidget)

    def __init__(self, config: PlanRegulationConfig, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        # TYPES
        # self.spacer_layout: QBoxLayout
        self.plan_regulation_name: QLineEdit
        self.form_layout: QFormLayout

        self.add_additional_information_btn: QPushButton
        self.add_field_btn: QPushButton
        self.del_btn: QPushButton
        self.expand_hide_btn: QToolButton

        self.code_label: QLabel
        self.code: QLineEdit

        # INIT
        self.config = config
        self.regulation_number_added = False
        self.expanded = True
        self.widgets: list[tuple] = []
        self.plan_regulation_name.setText(config.name)
        self.plan_regulation_name.setReadOnly(True)
        self.init_value_fields()
        self.init_buttons()

    def populate_from_definition(self, definition: PlanRegulationDefinition):
        # Additional information
        for info in definition.additional_information:
            info_type: str = cast("str", info["type"])
            layout = self.add_additional_info(info_type)
            if info_type in ADDITIONAL_INFORMATION_TYPES_WITH_INPUT:
                info_value_widget = QLineEdit()
                layout.addWidget(info_value_widget)
                value = info.get("value")
                if value:
                    info_value_widget.setText(value)

        # TODO: Other saved information from PlanRegulationDefinition

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
        self.add_additional_information_btn.setIcon(QgsApplication.getThemeIcon("mActionPropertiesWidget.svg"))

        # OTHER INFO / ADD FIELD
        add_field_menu = QMenu(self)
        add_field_menu.addAction("Määräysnumero").triggered.connect(self.add_regulation_number)
        add_field_menu.addAction("Liiteasiakirja").triggered.connect(self.add_file)
        self.add_field_btn.setMenu(add_field_menu)
        self.add_field_btn.setIcon(QgsApplication.getThemeIcon("mActionAdd.svg"))

        # EXPAND BTN
        self.expand_hide_btn.clicked.connect(self._on_expand_hide_btn_clicked)

    def _on_expand_hide_btn_clicked(self):
        if self.expanded:
            for label, widget in self.widgets:
                self.form_layout.removeWidget(label)
                label.hide()
                self.form_layout.removeWidget(widget)
                widget.hide()
            self.expand_hide_btn.setArrowType(Qt.ArrowType.DownArrow)
            self.expanded = False
        else:
            for label, widget in self.widgets:
                label.show()
                widget.show()
                self.form_layout.addRow(label, widget)
            self.expand_hide_btn.setArrowType(Qt.ArrowType.UpArrow)
            self.expanded = True

    def add_decimal_input(self, layout: QHBoxLayout, value_type: ValueType):
        value_widget = QgsDoubleSpinBox()
        label = QLabel("Arvo")
        if value_type == ValueType.POSITIVE_DECIMAL:
            value_widget.setMinimum(0.0)
            label.setToolTip("Tyyppi: desimaali (positiivinen)")
        else:
            value_widget.setMinimum(-9999.9)
            label.setToolTip("Tyyppi: desimaali")
        value_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(value_widget)
        self.form_layout.addRow(label, layout)
        self.widgets.append((label, value_widget))

    def add_positive_integer_input(self, layout: QHBoxLayout):
        value_widget = QgsSpinBox()
        value_widget.setMinimum(0)
        value_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(value_widget)
        label = QLabel("Arvo")
        label.setToolTip("Tyyppi: kokonaisluku (positiivinen)")
        self.form_layout.addRow(label, layout)
        self.widgets.append((label, value_widget))

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
        label = QLabel("Arvo")
        label.setToolTip("Tyyppi: kokonaisluku arvoväli (positiivinen)")
        self.form_layout.addRow(label, layout)
        self.widgets.append((label, layout))

    def add_versioned_text_input(self, layout: QHBoxLayout):
        text_widget = QTextEdit()
        layout.addWidget(text_widget)
        label = QLabel("Arvo")
        label.setToolTip("Tyyppi: kieliversioitu teksti")
        self.form_layout.addRow(label, layout)
        self.widgets.append((label, text_widget))

    def add_additional_info(self, info_type: str) -> QHBoxLayout:
        layout = QHBoxLayout()
        info_name = get_additional_information_name(info_type)
        info_type_label = QLineEdit(info_name)
        info_type_label.setReadOnly(True)
        layout.addWidget(info_type_label)
        label = QLabel("Lisätiedonlaji")
        self.form_layout.addRow(label, layout)
        self.widgets.append((label, info_type_label))
        return layout

    def add_regulation_number(self):
        if not self.regulation_number_added:
            number_widget = QgsSpinBox()
            label = QLabel("Määräysnumero")
            self.form_layout.addRow(label, number_widget)
            self.widgets.append((label, number_widget))
            self.regulation_number_added = True

    def add_file(self):
        file_input = QgsFileWidget()
        label = QLabel("Liiteasiakirja")
        self.form_layout.addRow(label, file_input)
        self.widgets.append((label, file_input))
