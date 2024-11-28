from __future__ import annotations

from importlib import resources
from typing import TYPE_CHECKING, cast

from qgis.core import QgsApplication
from qgis.gui import QgsDoubleSpinBox, QgsFileWidget, QgsSpinBox
from qgis.PyQt import uic
from qgis.PyQt.QtCore import Qt, pyqtSignal
from qgis.PyQt.QtWidgets import (
    QFormLayout,
    QLabel,
    QLineEdit,
    QMenu,
    QSizePolicy,
    QTextEdit,
    QToolButton,
    QWidget,
)

from arho_feature_template.core.plan_regulation_config import PlanRegulationConfig, Unit, ValueType
from arho_feature_template.utils.misc_utils import get_additional_information_name, get_layer_by_name

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

    language = "fin"

    delete_signal = pyqtSignal(QWidget)

    def __init__(self, config: PlanRegulationConfig, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        # TYPES
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
        self.widgets: list[tuple[QLabel, QWidget]] = []
        self.plan_regulation_name.setText(config.name)
        self.plan_regulation_name.setReadOnly(True)
        self.init_value_fields()
        self.init_additional_information_btn()
        self.init_other_information_btn()
        self.del_btn.setIcon(QgsApplication.getThemeIcon("mActionDeleteSelected.svg"))
        self.del_btn.clicked.connect(lambda: self.delete_signal.emit(self))
        self.expand_hide_btn.clicked.connect(self._on_expand_hide_btn_clicked)

    def populate_from_definition(self, definition: PlanRegulationDefinition):
        # Additional information
        for info in definition.additional_information:
            info_type: str = cast("str", info["type"])
            self.add_additional_info(info_type)
            if info_type == "kayttotarkoituskohdistus":
                info_value_widget = QLineEdit()
                label = QLabel(get_additional_information_name(info_type))
                value = info.get("value")
                if value:
                    info_value_widget.setText(value)
                self.form_layout.addRow(label, info_value_widget)

        # TODO: Other saved information from PlanRegulationDefinition

    def init_value_fields(self):
        value_type = self.config.value_type
        if value_type:
            self._add_value_input(value_type, self.config.unit)

    def _add_value_input(self, value_type: ValueType, unit: Unit | None):
        if value_type in [ValueType.DECIMAL, ValueType.POSITIVE_DECIMAL]:
            self.add_decimal_input(value_type, unit)
        elif value_type == ValueType.POSITIVE_INTEGER:
            self.add_positive_integer_input(unit)
        elif value_type == ValueType.POSITIVE_INTEGER_RANGE:
            self.add_positive_integer_range_input(unit)
        elif value_type == ValueType.VERSIONED_TEXT:
            self.add_versioned_text_input()
        else:
            msg = f"Invalid input value type for plan regulation: {value_type}"
            raise ValueError(msg)

    def init_additional_information_btn(self):
        informations_dict: dict[str, QMenu] = {}
        add_later: dict[str, list[str]] = {}

        def _add_action(informations_dict: dict[str, QMenu], parent_id: str, info_type: str):
            action = informations_dict[parent_id].addAction(info_type)
            action.triggered.connect(lambda _: self.add_additional_info(info_type))

        # Iterate code layer and build menus
        for feature in get_layer_by_name("Lisätiedonlaji").getFeatures():
            if feature["level"] == 1:
                menu = QMenu(feature["name"][self.language], self)
                informations_dict[feature["id"]] = menu
            else:
                parent_id = feature["parent_id"]
                info_type = feature["name"][self.language]
                if parent_id in informations_dict:
                    _add_action(informations_dict, parent_id, info_type)
                else:
                    if parent_id not in add_later:
                        add_later[parent_id] = []
                    add_later[parent_id].append(info_type)
        for parent_id, additional_information_types in add_later.items():
            for info_type in additional_information_types:
                _add_action(informations_dict, parent_id, info_type)

        # Create main menu for btn and add submenus
        additional_information_type_menu = QMenu(self)
        for menu in informations_dict.values():
            additional_information_type_menu.addMenu(menu)
        self.add_additional_information_btn.setMenu(additional_information_type_menu)
        self.add_additional_information_btn.setIcon(QgsApplication.getThemeIcon("mActionPropertiesWidget.svg"))

    def init_other_information_btn(self):
        add_field_menu = QMenu(self)
        add_field_menu.addAction("Määräysnumero").triggered.connect(self.add_regulation_number)
        add_field_menu.addAction("Liiteasiakirja").triggered.connect(self.add_file)
        add_field_menu.addAction("Aihetunniste").triggered.connect(self.add_topic_tag)

        theme_menu = QMenu("Kaavoitusteema", self)
        for feature in get_layer_by_name("Kaavoitusteemat").getFeatures():
            name = feature["name"][self.language]
            action = theme_menu.addAction(name)
            action.triggered.connect(lambda _, name=name: self.add_theme(name))
        add_field_menu.addMenu(theme_menu)

        self.add_field_btn.setMenu(add_field_menu)
        self.add_field_btn.setIcon(QgsApplication.getThemeIcon("mActionAdd.svg"))

    def _on_expand_hide_btn_clicked(self):
        if self.expanded:
            for label, value_widget in self.widgets:
                self.form_layout.removeWidget(label)
                label.hide()
                self.form_layout.removeWidget(value_widget)
                value_widget.hide()
            self.expand_hide_btn.setArrowType(Qt.ArrowType.DownArrow)
            self.expanded = False
        else:
            for label, value_widget in self.widgets:
                self.form_layout.addRow(label, value_widget)
                label.show()
                value_widget.show()
            self.expand_hide_btn.setArrowType(Qt.ArrowType.UpArrow)
            self.expanded = True

    def _add_widgets_to_form(self, label: QLabel, widget: QWidget):
        self.form_layout.addRow(label, widget)
        self.widgets.append((label, widget))
        if not self.expanded:
            self._on_expand_hide_btn_clicked()

    def add_decimal_input(self, value_type: ValueType, unit: Unit | None):
        value_widget = QgsDoubleSpinBox()
        label = QLabel("Arvo")
        if value_type == ValueType.POSITIVE_DECIMAL:
            value_widget.setMinimum(0.0)
            label.setToolTip("Tyyppi: desimaali (positiivinen)")
        else:
            value_widget.setMinimum(-9999.9)
            label.setToolTip("Tyyppi: desimaali")
        value_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        if unit:
            value_widget.setSuffix(f" {unit.value}")
        self._add_widgets_to_form(label, value_widget)

    def add_positive_integer_input(self, unit: Unit | None):
        value_widget = QgsSpinBox()
        value_widget.setMinimum(0)
        value_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        if unit:
            value_widget.setSuffix(f" {unit.value}")
        label = QLabel("Arvo")
        label.setToolTip("Tyyppi: kokonaisluku (positiivinen)")
        self._add_widgets_to_form(label, value_widget)

    def add_positive_integer_range_input(self, unit: Unit | None):
        min_widget = QgsSpinBox()
        min_widget.setMinimum(0)
        min_label = QLabel("Arvo minimi")
        min_label.setToolTip("Tyyppi: kokonaisluku arvoväli (positiivinen)")

        max_widget = QgsSpinBox()
        max_widget.setMinimum(0)
        max_label = QLabel("Arvo maksimi")
        max_label.setToolTip("Tyyppi: kokonaisluku arvoväli (positiivinen)")
        if unit:
            min_widget.setSuffix(f" {unit.value}")
            max_widget.setSuffix(f" {unit.value}")
        self._add_widgets_to_form(min_label, min_widget)
        self._add_widgets_to_form(max_label, max_widget)

    def add_versioned_text_input(self):
        text_widget = QTextEdit()
        label = QLabel("Arvo")
        label.setToolTip("Tyyppi: kieliversioitu teksti")
        self._add_widgets_to_form(label, text_widget)

    def add_additional_info(self, info_type: str):
        info_type_line = QLineEdit(get_additional_information_name(info_type))
        info_type_line.setReadOnly(True)
        label = QLabel("Lisätiedonlaji")
        self._add_widgets_to_form(label, info_type_line)

    def add_regulation_number(self):
        if not self.regulation_number_added:
            number_widget = QgsSpinBox()
            label = QLabel("Määräysnumero")
            self._add_widgets_to_form(label, number_widget)
            self.regulation_number_added = True

    def add_file(self):
        file_input = QgsFileWidget()
        label = QLabel("Liiteasiakirja")
        self._add_widgets_to_form(label, file_input)

    def add_topic_tag(self):
        text_input = QLineEdit()
        label = QLabel("Aihetunniste")
        self._add_widgets_to_form(label, text_input)

    def add_theme(self, theme_name: str):
        theme_type_line = QLineEdit(theme_name)
        theme_type_line.setReadOnly(True)
        label = QLabel("Kaavoitusteema")
        self._add_widgets_to_form(label, theme_type_line)
