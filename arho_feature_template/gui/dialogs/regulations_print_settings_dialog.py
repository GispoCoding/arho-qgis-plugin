from __future__ import annotations

from importlib import resources
from typing import TYPE_CHECKING

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QCheckBox, QDialog

from arho_feature_template.core.prints.regulation_print_settings import RegulationPrintSettings
from arho_feature_template.core.settings_manager import SettingsManager
from arho_feature_template.utils.localization_utils import LANGUAGES

if TYPE_CHECKING:
    from qgis.gui import QgsFontButton, QgsSpinBox

    from arho_feature_template.gui.components.code_combobox import CodeComboBox

ui_path = resources.files(__package__) / "regulations_print_settings_dialog.ui"
FormClass, _ = uic.loadUiType(ui_path)


class RegulationsPrintSettingsDialog(QDialog, FormClass):  # type: ignore
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # TYPES
        self.include_regulation_headings_checkbox: QCheckBox
        self.include_regulation_texts_checkbox: QCheckBox
        self.heading_font_selection: QgsFontButton
        self.text_font_selection: QgsFontButton
        self.symbol_width_spinbox: QgsSpinBox
        self.symbol_height_spinbox: QgsSpinBox

        self.language_1_selection: CodeComboBox
        self.language_2_selection: CodeComboBox

        self.x_margins_spinbox: QgsSpinBox
        self.y_margins_spinbox: QgsSpinBox

        # INIT
        self.language_1_selection.populate_from_dict(LANGUAGES)
        self.language_1_selection.remove_item_by_text("NULL")
        primary_language = SettingsManager.get_primary_language()
        self.language_1_selection.set_value(primary_language)

        self.language_2_selection.populate_from_dict(LANGUAGES)

    def get_settings(self) -> RegulationPrintSettings:
        return RegulationPrintSettings(
            self.include_regulation_headings_checkbox.isChecked(),
            self.include_regulation_texts_checkbox.isChecked(),
            self.symbol_width_spinbox.value(),
            self.symbol_height_spinbox.value(),
            self.heading_font_selection.currentFont(),
            self.text_font_selection.currentFont(),
            self.x_margins_spinbox.value(),
            self.y_margins_spinbox.value(),
            self.get_language_codes(),
        )

    def get_language_codes(self) -> list[str]:
        language_codes = [self.language_1_selection.value()]
        secondary_language_id = self.language_2_selection.value()
        if secondary_language_id:
            language_codes.append(secondary_language_id)

        return [language_code for language_code in language_codes if language_code is not None]
