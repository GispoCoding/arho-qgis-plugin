from __future__ import annotations

import os
from importlib import resources
from pathlib import Path
from typing import TYPE_CHECKING, NamedTuple

from qgis.core import QgsApplication
from qgis.gui import QgsFileWidget, QgsOptionsPageWidget, QgsOptionsWidgetFactory
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QComboBox, QHBoxLayout, QPushButton

from arho_feature_template.core.plan_manager import (
    GENERAL_PLAN_PATH,
    LAYER_NAME_TRANSLATION_MAP,
    REGIONAL_PLAN_PATH,
    TOWN_PLAN_PATH,
)
from arho_feature_template.core.settings_manager import SettingsManager
from arho_feature_template.gui.components.code_combobox import CodeComboBox
from arho_feature_template.project.layers.code_layers import PlanType
from arho_feature_template.project.layers.plan_layers import (
    LandUseAreaLayer,
    LineLayer,
    OtherAreaLayer,
    PlanObjectLayer,
    PointLayer,
)
from arho_feature_template.qgis_plugin_tools.tools.custom_logging import LogTarget
from arho_feature_template.utils.localization_utils import LANGUAGES
from arho_feature_template.utils.misc_utils import iface

if TYPE_CHECKING:
    from qgis.gui import QgsSpinBox
    from qgis.PyQt.QtWidgets import QCheckBox, QGroupBox, QLineEdit, QWidget

ui_path = resources.files(__package__) / "plugin_settings.ui"
FormClass, _ = uic.loadUiType(ui_path)


class FileWidgetConfig(NamedTuple):
    plan_type: PlanType
    layer_type: type[PlanObjectLayer]
    file_widget: QgsFileWidget


LOG_LEVELS = [
    "DEBUG",
    "INFO",
    "WARNING",
    "ERROR",
    "CRITICAL",
]


class ArhoOptionsPage(QgsOptionsPageWidget, FormClass):  # type: ignore
    # TYPES
    host: QLineEdit
    port: QgsSpinBox
    lambda_address: QLineEdit
    data_exchange_layer_enabled: QCheckBox

    visualisations_group_box: QGroupBox

    region_land_use_area: QgsFileWidget
    region_other_area: QgsFileWidget
    region_line: QgsFileWidget
    region_point: QgsFileWidget

    general_land_use_area: QgsFileWidget
    general_other_area: QgsFileWidget
    general_line: QgsFileWidget
    general_point: QgsFileWidget

    town_land_use_area: QgsFileWidget
    town_other_area: QgsFileWidget
    town_line: QgsFileWidget
    town_point: QgsFileWidget

    language_widgets_container: QWidget
    primary_language_combobox: CodeComboBox
    add_language_btn: QPushButton
    show_only_primary_language_checkbox: QCheckBox
    check_box_add_only_selected_languages: QCheckBox
    code_value_language_combo_box: CodeComboBox

    combo_box_log_stream: QComboBox
    combo_box_log_file: QComboBox
    combo_box_log_msgbar: QComboBox

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setupUi(self)

        tooltip_text = """
        Käyttääksesi tasoille jotain muuta kuin Arhossa tulevaa Katja-asetuksen mukaista visualisaatiota,
        vaihda tarvittavat tiedostopolut osoittamaan omiin QML-tyylitiedostoihisi.
        Uudet visualisaatiot aktivoituvat, kun avaat kaava-asian uudelleen tai vaihdat toiseen kaavasuunnitelmaan.
        """
        self.visualisations_group_box.setToolTip(tooltip_text)

        # QML FILE PATHS
        self.file_widget_configs: list[FileWidgetConfig] = [
            # REGIONAL
            FileWidgetConfig(PlanType.REGIONAL, LandUseAreaLayer, self.region_land_use_area),
            FileWidgetConfig(PlanType.REGIONAL, OtherAreaLayer, self.region_other_area),
            FileWidgetConfig(PlanType.REGIONAL, LineLayer, self.region_line),
            FileWidgetConfig(PlanType.REGIONAL, PointLayer, self.region_point),
            # GENERAL
            FileWidgetConfig(PlanType.GENERAL, LandUseAreaLayer, self.general_land_use_area),
            FileWidgetConfig(PlanType.GENERAL, OtherAreaLayer, self.general_other_area),
            FileWidgetConfig(PlanType.GENERAL, LineLayer, self.general_line),
            FileWidgetConfig(PlanType.GENERAL, PointLayer, self.general_point),
            # TOWN
            FileWidgetConfig(PlanType.TOWN, LandUseAreaLayer, self.town_land_use_area),
            FileWidgetConfig(PlanType.TOWN, OtherAreaLayer, self.town_other_area),
            FileWidgetConfig(PlanType.TOWN, LineLayer, self.town_line),
            FileWidgetConfig(PlanType.TOWN, PointLayer, self.town_point),
        ]
        self._set_file_filter()

        # INIT
        self.primary_language_combobox.populate_from_dict(LANGUAGES)
        self.primary_language_combobox.remove_item_by_text("NULL")  # Language must be defined
        self.language_widgets: list[CodeComboBox] = [self.primary_language_combobox]

        self.add_language_btn.setIcon(QgsApplication.getThemeIcon("mActionAdd.svg"))
        self.add_language_btn.clicked.connect(self._add_language_combobox)

        self.code_value_language_combo_box.populate_from_dict(LANGUAGES)
        self.code_value_language_combo_box.remove_item_by_text("NULL")  # Language must be defined

        for level_name in LOG_LEVELS:
            self.combo_box_log_stream.addItem(level_name)
            self.combo_box_log_file.addItem(level_name)
            self.combo_box_log_msgbar.addItem(level_name)

        self.load_settings()

    def _add_language_combobox(self) -> CodeComboBox:
        layout = QHBoxLayout()

        language_combobox = CodeComboBox()
        language_combobox.populate_from_dict(LANGUAGES)
        language_combobox.remove_item_by_text("NULL")  # Language must be defined
        self.language_widgets.append(language_combobox)
        layout.addWidget(language_combobox)

        del_btn = QPushButton()
        del_btn.setMaximumWidth(30)
        del_btn.setIcon(QgsApplication.getThemeIcon("mActionDeleteSelected.svg"))
        del_btn.clicked.connect(lambda _: self._delete_language_combobox(layout, language_combobox))
        layout.addWidget(del_btn)

        self.language_widgets_container.layout().insertLayout(len(self.language_widgets) - 1, layout)

        return language_combobox

    def _delete_language_combobox(self, layout: QHBoxLayout, widget_to_delete: CodeComboBox) -> None:
        self.language_widgets_container.layout().removeItem(layout)
        self.language_widgets.remove(widget_to_delete)
        while layout.count():
            child = layout.takeAt(0)
            child.widget().deleteLater()
        layout.deleteLater()

    def _set_file_filter(self):
        for config in self.file_widget_configs:
            widget: QgsFileWidget = config.file_widget
            widget.setFilter("*.qml")

    def apply(self) -> None:
        SettingsManager.set_proxy_host(self.host.text())
        SettingsManager.set_proxy_port(self.port.value())
        SettingsManager.set_lambda_url(self.lambda_address.text())
        SettingsManager.set_data_exchange_layer_enabled(self.data_exchange_layer_enabled.isChecked())

        missing_files = []
        invalid_file_types = []
        for config in self.file_widget_configs:
            widget: QgsFileWidget = config.file_widget
            file_path = widget.filePath()
            path_object = Path(file_path)
            if not path_object.is_file():
                missing_files.append(file_path)
                continue

            if path_object.suffix.lower() != ".qml":
                invalid_file_types.append(file_path)
                continue

            SettingsManager.set_layer_style_path(config.plan_type, config.layer_type, file_path)

        if missing_files:
            iface.messageBar().pushCritical("Tiedostoa ei olemassa:", ", ".join(missing_files))

        if invalid_file_types:
            iface.messageBar().pushCritical("Väärä tiedostotyyppi:", ", ".join(invalid_file_types))

        SettingsManager.set_primary_language(self.primary_language_combobox.value())
        SettingsManager.set_languages([widget.value() for widget in self.language_widgets])

        SettingsManager.set_show_only_primary_language(self.show_only_primary_language_checkbox.isChecked())
        SettingsManager.set_add_only_selected_languages(self.check_box_add_only_selected_languages.isChecked())

        SettingsManager.set_code_value_language(self.code_value_language_combo_box.value())

        SettingsManager.set_log_level(LogTarget.STREAM, self.combo_box_log_stream.currentText())
        SettingsManager.set_log_level(LogTarget.FILE, self.combo_box_log_file.currentText())
        SettingsManager.set_log_level(LogTarget.BAR, self.combo_box_log_msgbar.currentText())

        SettingsManager.finish()

    def load_settings(self) -> None:
        # Load lambda settings
        self.host.setText(SettingsManager.get_proxy_host())
        self.port.setValue(SettingsManager.get_proxy_port() or 0)
        self.lambda_address.setText(SettingsManager.get_lambda_url())
        self.data_exchange_layer_enabled.setChecked(SettingsManager.get_data_exchange_layer_enabled())

        # Load visualization file settings
        for config in self.file_widget_configs:
            widget: QgsFileWidget = config.file_widget

            if config.plan_type == PlanType.REGIONAL:
                folder = REGIONAL_PLAN_PATH
            elif config.plan_type == PlanType.GENERAL:
                folder = GENERAL_PLAN_PATH
            elif config.plan_type == PlanType.TOWN:
                folder = TOWN_PLAN_PATH

            default = os.path.join(folder, f"{LAYER_NAME_TRANSLATION_MAP[config.layer_type.name]}.qml")
            path = SettingsManager.get_layer_style_path(config.plan_type, config.layer_type, default)
            widget.setFilePath(path)

        # Load language settings
        # Keep track of added languages to avoid duplicates (should concern only primary language)
        added_languages: set[str] = set()
        primary_language = SettingsManager.get_primary_language()
        self.primary_language_combobox.set_value(primary_language)
        added_languages.add(primary_language)
        for language in SettingsManager.get_languages():
            if language in added_languages:
                continue
            self._add_language_combobox().set_value(language)
            added_languages.add(language)

        self.show_only_primary_language_checkbox.setChecked(SettingsManager.get_show_only_primary_language())
        self.check_box_add_only_selected_languages.setChecked(SettingsManager.get_add_only_selected_languages())

        self.code_value_language_combo_box.set_value(SettingsManager.get_code_value_language())

        self.combo_box_log_stream.setCurrentText(SettingsManager.get_log_level(LogTarget.STREAM))
        self.combo_box_log_file.setCurrentText(SettingsManager.get_log_level(LogTarget.FILE))
        self.combo_box_log_msgbar.setCurrentText(SettingsManager.get_log_level(LogTarget.BAR))


class ArhoOptionsPageFactory(QgsOptionsWidgetFactory):
    def __init__(self):
        super().__init__()
        self.setTitle("ARHO")
        self.setKey("ARHO")

    def createWidget(self, parent):  # noqa: N802
        return ArhoOptionsPage(parent)
