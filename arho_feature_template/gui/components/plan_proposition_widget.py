from __future__ import annotations

from importlib import resources
from typing import TYPE_CHECKING

from qgis.core import NULL, QgsApplication
from qgis.PyQt import uic
from qgis.PyQt.QtCore import Qt, pyqtSignal
from qgis.PyQt.QtWidgets import QFormLayout, QLabel, QMenu, QToolButton, QWidget

from arho_feature_template.core.models import Proposition
from arho_feature_template.gui.components.theme_widget import ThemeWidget
from arho_feature_template.gui.components.value_input_widgets import (
    IntegerInputWidget,
    LocalizedMultilineTextInputWidget,
)

if TYPE_CHECKING:
    from qgis.PyQt.QtWidgets import QPushButton

    from arho_feature_template.gui.components.validity_label import ValidityLabel


ui_path = resources.files(__package__) / "plan_proposition_widget.ui"
FormClass, _ = uic.loadUiType(ui_path)


class PropositionWidget(QWidget, FormClass):  # type: ignore
    """A widget representation of a plan proposition."""

    delete_signal = pyqtSignal(QWidget)
    changed = pyqtSignal()

    def __init__(self, proposition: Proposition, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        # TYPES
        self.add_field_btn: QPushButton
        self.del_btn: QPushButton
        self.form_layout: QFormLayout
        self.text_input: LocalizedMultilineTextInputWidget
        self.expand_hide_btn: QToolButton
        self.validity_label: ValidityLabel

        # INIT
        self.proposition = proposition
        self.proposition_number_widget: IntegerInputWidget | None = None

        self.theme_widgets: list[ThemeWidget] = []

        # List of widgets for hiding / showing
        self.widgets: list[tuple[QLabel, QWidget]] = []

        add_field_menu = QMenu(self)
        add_field_menu.addAction("Suositusnumero").triggered.connect(self._add_proposition_number)
        add_field_menu.addAction("Kaavoitusteema").triggered.connect(self._add_theme)
        self.add_field_btn.setMenu(add_field_menu)
        self.add_field_btn.setIcon(QgsApplication.getThemeIcon("mActionAdd.svg"))

        self.del_btn.setIcon(QgsApplication.getThemeIcon("mActionDeleteSelected.svg"))
        self.del_btn.clicked.connect(lambda: self.delete_signal.emit(self))

        self.expanded = True
        self.expand_hide_btn.clicked.connect(self._on_expand_hide_btn_clicked)

        self.text_input.set_value(self.proposition.value)
        if self.proposition.theme_ids not in [None, NULL]:
            for theme_id in self.proposition.theme_ids:
                self._add_theme(theme_id)
        if self.proposition.proposition_number:
            self._add_proposition_number(self.proposition.proposition_number)

        self.validity_label.set_from_model(self.proposition)

    def _add_widget(self, label: QLabel, widget: QWidget):
        self.form_layout.addRow(label, widget)
        self.widgets.append((label, widget))
        if not self.expanded:
            self._on_expand_hide_btn_clicked()

        widget.changed.connect(lambda: self.changed.emit())
        self.changed.emit()

    def _delete_widget(self, widget_to_delete: QWidget) -> bool:
        for label, widget in self.widgets:
            if widget == widget_to_delete:
                if isinstance(widget, ThemeWidget):
                    self.theme_widgets.remove(widget)
                self.form_layout.removeRow(widget_to_delete)
                self.widgets.remove((label, widget))
                self.changed.emit()
                return True
        return False

    def _add_proposition_number(self, default_value: int | None = None):
        if not self.proposition_number_widget:
            self.proposition_number_widget = IntegerInputWidget(default_value, None, True)
            self._add_widget(QLabel("Suositusnumero"), self.proposition_number_widget)

    def _add_theme(self, theme_name: str):
        theme_widget = ThemeWidget(theme_name)
        self.theme_widgets.append(theme_widget)
        theme_widget.delete_signal.connect(self._delete_widget)
        self._add_widget(QLabel("Kaavoitusteema:"), theme_widget)

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

    def into_model(self, force_new: bool = False) -> Proposition:  # noqa: FBT001, FBT002
        model = Proposition(
            regulation_group_id=self.proposition.regulation_group_id,
            value=self.text_input.get_value(),
            theme_ids=[
                theme_widget.get_value() for theme_widget in self.theme_widgets if theme_widget.get_value() != NULL
            ],
            proposition_number=self.proposition_number_widget.get_value() if self.proposition_number_widget else None,
            lifecycle_status_id=self.proposition.lifecycle_status_id,
            period_of_validity_start=self.proposition.period_of_validity_start,
            period_of_validity_end=self.proposition.period_of_validity_end,
            modified=self.proposition.modified,
            id_=self.proposition.id_ if not force_new else None,
        )
        if not model.modified and model != self.proposition:
            model.modified = True

        return model
