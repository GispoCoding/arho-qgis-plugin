from __future__ import annotations

from importlib import resources
from typing import TYPE_CHECKING

from qgis.core import QgsApplication
from qgis.PyQt import uic
from qgis.PyQt.QtCore import pyqtSignal
from qgis.PyQt.QtWidgets import QMenu, QWidget

if TYPE_CHECKING:
    from qgis.PyQt.QtWidgets import QComboBox, QPushButton

ui_path = resources.files(__package__) / "new_plan_regulation_widget.ui"
FormClass, _ = uic.loadUiType(ui_path)


class NewPlanRegulationWidget(QWidget, FormClass):  # type: ignore
    """A widget representation of a plan regulation."""

    delete_signal = pyqtSignal(QWidget)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        # TYPES
        self.plan_regulation_type: QComboBox

        self.add_input_btn: QPushButton
        self.add_additional_information_btn: QPushButton
        self.add_regulation_number_btn: QPushButton
        self.add_file_btn: QPushButton
        self.del_btn: QPushButton

        # INIT
        self.init_plan_regulation_types()
        self.init_buttons()

    def request_delete(self):
        self.delete_signal.emit(self)

    def init_buttons(self):
        self.del_btn.setIcon(QgsApplication.getThemeIcon("mActionDeleteSelected.svg"))
        self.del_btn.clicked.connect(self.request_delete)

        input_menu = QMenu()
        input_menu.addAction("Teksti")
        input_menu.addAction("Numeerinen")
        input_menu.addAction("Koodi")
        self.add_input_btn.setMenu(input_menu)

        add_additional_information_menu = QMenu()
        add_additional_information_menu.addAction("Teksti")
        add_additional_information_menu.addAction("Numeerinen")
        add_additional_information_menu.addAction("Koodi")
        self.add_additional_information_btn.setMenu(add_additional_information_menu)

    def init_plan_regulation_types(self):
        # Get plan regulation type codes from DB
        pass
