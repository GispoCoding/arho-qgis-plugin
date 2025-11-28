from __future__ import annotations

import os
from importlib import resources
from pathlib import Path
from typing import TYPE_CHECKING, NamedTuple

from qgis.gui import QgsFileWidget, QgsOptionsPageWidget, QgsOptionsWidgetFactory
from qgis.PyQt import uic

from arho_feature_template.core.plan_manager import (
    GENERAL_PLAN_PATH,
    LAYER_NAME_TRANSLATION_MAP,
    REGIONAL_PLAN_PATH,
    TOWN_PLAN_PATH,
)
from arho_feature_template.core.settings_manager import SettingsManager
from arho_feature_template.project.layers.code_layers import PlanType
from arho_feature_template.project.layers.plan_layers import (
    LandUseAreaLayer,
    LineLayer,
    OtherAreaLayer,
    PlanObjectLayer,
    PointLayer,
)
from arho_feature_template.utils.misc_utils import iface

if TYPE_CHECKING:
    from qgis.gui import QgsSpinBox
    from qgis.PyQt.QtWidgets import QCheckBox, QGroupBox, QLineEdit

ui_path = resources.files(__package__) / "plugin_settings.ui"
FormClass, _ = uic.loadUiType(ui_path)


class FileWidgetConfig(NamedTuple):
    plan_type: PlanType
    layer_type: type[PlanObjectLayer]
    file_widget: QgsFileWidget


class ArhoOptionsPage(QgsOptionsPageWidget, FormClass):  # type: ignore
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        # TYPES
        self.host: QLineEdit
        self.port: QgsSpinBox
        self.lambda_address: QLineEdit
        self.data_exchange_layer_enabled: QCheckBox

        self.visualisations_group_box: QGroupBox

        self.region_land_use_area: QgsFileWidget
        self.region_other_area: QgsFileWidget
        self.region_line: QgsFileWidget
        self.region_point: QgsFileWidget

        self.general_land_use_area: QgsFileWidget
        self.general_other_area: QgsFileWidget
        self.general_line: QgsFileWidget
        self.general_point: QgsFileWidget

        self.town_land_use_area: QgsFileWidget
        self.town_other_area: QgsFileWidget
        self.town_line: QgsFileWidget
        self.town_point: QgsFileWidget

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
        self.load_settings()

    def _set_file_filter(self):
        for config in self.file_widget_configs:
            widget: QgsFileWidget = config.file_widget
            widget.setFilter("*.qml")

    def apply(self):
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

        SettingsManager.finish()

    def load_settings(self):
        self.host.setText(SettingsManager.get_proxy_host())
        self.port.setValue(SettingsManager.get_proxy_port() or 0)
        self.lambda_address.setText(SettingsManager.get_lambda_url())
        self.data_exchange_layer_enabled.setChecked(SettingsManager.get_data_exchange_layer_enabled())

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


class ArhoOptionsPageFactory(QgsOptionsWidgetFactory):
    def __init__(self):
        super().__init__()
        self.setTitle("ARHO")
        self.setKey("ARHO")

    def createWidget(self, parent):  # noqa: N802
        return ArhoOptionsPage(parent)
