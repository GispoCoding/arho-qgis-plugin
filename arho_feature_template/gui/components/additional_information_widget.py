from __future__ import annotations

from importlib import resources
from typing import TYPE_CHECKING

from qgis.core import QgsApplication
from qgis.PyQt import uic
from qgis.PyQt.QtCore import Qt, pyqtSignal
from qgis.PyQt.QtWidgets import (
    QFormLayout,
    QLabel,
    QLineEdit,
    QToolButton,
    QWidget,
)

from arho_feature_template.core.models import AdditionalInformation
from arho_feature_template.gui.components.value_input_widgets import (
    ValueWidgetManager,
)

if TYPE_CHECKING:
    from qgis.PyQt.QtWidgets import QPushButton

ui_path = resources.files(__package__) / "additional_information_widget.ui"
FormClass, _ = uic.loadUiType(ui_path)


class AdditionalInformationWidget(QWidget, FormClass):  # type: ignore
    """A widget representation of a plan regulation."""

    # TYPES
    type_of_additional_information_name: QLineEdit
    form_layout: QFormLayout
    del_btn: QPushButton
    expand_hide_btn: QToolButton

    delete_signal = pyqtSignal(QWidget)

    def __init__(self, additional_information: AdditionalInformation, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        # INIT
        self.config = additional_information.config
        self.additional_information = additional_information

        self.value_widget_manager = (
            ValueWidgetManager(
                self.additional_information.value,
                self.config.default_value,
            )
            if self.config and self.config.default_value
            else None
        )

        # List of widgets for hiding / showing
        self.widgets: list[tuple[QLabel, QWidget]] = []

        self.expanded = True

        self.type_of_additional_information_name.setText(self.config.name)
        self.type_of_additional_information_name.setReadOnly(True)
        self.del_btn.setIcon(QgsApplication.getThemeIcon("mActionDeleteSelected.svg"))
        self.del_btn.setDisabled(True)  # TODO: Implement delete
        self.del_btn.clicked.connect(lambda: self.delete_signal.emit(self))
        self.expand_hide_btn.clicked.connect(self._on_expand_hide_btn_clicked)

        if self.value_widget_manager is not None:
            widget = (
                self.value_widget_manager.value_widget
                if self.value_widget_manager.value_widget is not None
                else QLabel("Syötekenttää tälle tyypille ei ole vielä toteutettu")
            )
            self._add_widget(QLabel("Arvo"), widget)

    def _add_widget(self, label: QLabel, widget: QWidget):
        self.form_layout.addRow(label, widget)
        self.widgets.append((label, widget))
        if not self.expanded:
            self._on_expand_hide_btn_clicked()

    def _on_expand_hide_btn_clicked(self):
        if self.expanded:
            for label, value_widget in self.widgets:
                # self.form_layout.removeWidget(label)
                label.hide()
                # self.form_layout.removeWidget(value_widget)
                value_widget.hide()
            self.expand_hide_btn.setArrowType(Qt.ArrowType.DownArrow)
            self.expanded = False
        else:
            for label, value_widget in self.widgets:
                # self.form_layout.addRow(label, value_widget)
                label.show()
                value_widget.show()
            self.expand_hide_btn.setArrowType(Qt.ArrowType.UpArrow)
            self.expanded = True

    def into_model(self) -> AdditionalInformation:
        return AdditionalInformation(
            config=self.config,
            id_=self.additional_information.id_,
            plan_regulation_id=self.additional_information.plan_regulation_id,
            type_additional_information_id=self.additional_information.type_additional_information_id,
            value=self.value_widget_manager.into_model() if self.value_widget_manager else None,
        )
