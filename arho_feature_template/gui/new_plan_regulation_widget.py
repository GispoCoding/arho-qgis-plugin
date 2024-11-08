from __future__ import annotations

from enum import Enum
from importlib import resources
from typing import TYPE_CHECKING

from qgis.core import QgsApplication
from qgis.gui import QgsDoubleSpinBox, QgsFileWidget, QgsSpinBox
from qgis.PyQt import uic
from qgis.PyQt.QtCore import pyqtSignal
from qgis.PyQt.QtWidgets import QComboBox, QFormLayout, QMenu, QTextEdit, QWidget

if TYPE_CHECKING:
    from qgis.PyQt.QtWidgets import QLineEdit, QPushButton

ui_path = resources.files(__package__) / "new_plan_regulation_widget.ui"
FormClass, _ = uic.loadUiType(ui_path)


class InputTypes(Enum):
    TEXT_VALUE = 1
    NUMERIC_VALUE = 2
    CODE_VALUE = 3

    TEXT_INFO = 4
    NUMERIC_INFO = 5
    CODE_INFO = 6

    REGULATION_NUMBER = 7
    RELATED_FILE = 8


class NewPlanRegulationWidget(QWidget, FormClass):  # type: ignore
    """A widget representation of a plan regulation."""

    delete_signal = pyqtSignal(QWidget)

    def __init__(self, regulation_type: str, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        # TYPES
        self.plan_regulation_type: QLineEdit
        self.form_layout: QFormLayout

        self.add_input_btn: QPushButton
        self.add_additional_information_btn: QPushButton
        self.add_regulation_number_btn: QPushButton
        self.add_file_btn: QPushButton
        self.del_btn: QPushButton

        # INIT
        self.widgets: dict[InputTypes, list[QWidget]] = {}
        self.plan_regulation_type.setText(regulation_type)
        self.init_buttons()

    def request_delete(self):
        self.delete_signal.emit(self)

    def init_buttons(self):
        self.del_btn.setIcon(QgsApplication.getThemeIcon("mActionDeleteSelected.svg"))
        self.del_btn.clicked.connect(self.request_delete)

        input_menu = QMenu()
        input_menu.addAction("Teksti").triggered.connect(lambda: self.add_input_field(InputTypes.TEXT_VALUE))
        input_menu.addAction("Numeerinen").triggered.connect(lambda: self.add_input_field(InputTypes.NUMERIC_VALUE))
        input_menu.addAction("Koodi").triggered.connect(lambda: self.add_input_field(InputTypes.CODE_VALUE))
        self.add_input_btn.setMenu(input_menu)

        additional_info_menu = QMenu()
        additional_info_menu.addAction("Teksti").triggered.connect(lambda: self.add_input_field(InputTypes.TEXT_INFO))
        additional_info_menu.addAction("Numeerinen").triggered.connect(
            lambda: self.add_input_field(InputTypes.NUMERIC_INFO)
        )
        additional_info_menu.addAction("Koodi").triggered.connect(lambda: self.add_input_field(InputTypes.CODE_INFO))
        self.add_additional_information_btn.setMenu(additional_info_menu)

        self.add_regulation_number_btn.clicked.connect(lambda: self.add_input_field(InputTypes.REGULATION_NUMBER))
        self.add_file_btn.clicked.connect(lambda: self.add_input_field(InputTypes.RELATED_FILE))

    def add_input_field(self, input_field_type: InputTypes):
        if input_field_type == InputTypes.TEXT_VALUE:
            widget = QTextEdit()
            self.form_layout.addRow("Tekstiarvo", widget)
        elif input_field_type == InputTypes.NUMERIC_VALUE:
            widget = QgsDoubleSpinBox()  # Or QgsSpinBox?
            self.form_layout.addRow("Numeerinen arvo", widget)
        elif input_field_type == InputTypes.CODE_VALUE:
            widget = QComboBox()
            # TODO: widget.addItems()
            self.form_layout.addRow("Koodiarvo", widget)

        elif input_field_type == InputTypes.TEXT_INFO:
            widget = QTextEdit()
            self.form_layout.addRow("Lisätieto", widget)
        elif input_field_type == InputTypes.NUMERIC_INFO:
            widget = QgsDoubleSpinBox()
            self.form_layout.addRow("Lisätieto", widget)
        elif input_field_type == InputTypes.CODE_INFO:
            widget = QComboBox()
            # TODO: widget.addItems()
            self.form_layout.addRow("Lisätieto", widget)

        elif input_field_type == InputTypes.REGULATION_NUMBER:
            widget = QgsSpinBox()
            self.form_layout.addRow("Määräysnumero", widget)
        elif input_field_type == InputTypes.RELATED_FILE:
            widget = QgsFileWidget()
            self.form_layout.addRow("Liiteasiakirja", widget)

        if self.widgets.get(input_field_type) is None:
            self.widgets[input_field_type] = [widget]
        else:
            self.widgets[input_field_type].append(widget)
