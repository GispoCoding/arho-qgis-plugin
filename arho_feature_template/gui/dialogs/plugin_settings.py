from importlib import resources
from typing import TYPE_CHECKING

from qgis.gui import QgsOptionsPageWidget, QgsOptionsWidgetFactory
from qgis.PyQt import uic

from arho_feature_template.core.settings_manager import SettingsManager

if TYPE_CHECKING:
    from qgis.gui import QgsSpinBox
    from qgis.PyQt.QtWidgets import QCheckBox, QLineEdit

ui_path = resources.files(__package__) / "plugin_settings.ui"
FormClass, _ = uic.loadUiType(ui_path)


class ArhoOptionsPage(QgsOptionsPageWidget, FormClass):  # type: ignore
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        # TYPES
        self.host: QLineEdit
        self.port: QgsSpinBox
        self.lambda_address: QLineEdit
        self.data_exchange_layer_enabled: QCheckBox

        # INIT
        self.load_settings()

    def apply(self):
        SettingsManager.set_proxy_host(self.host.text())
        SettingsManager.set_proxy_port(self.port.value())
        SettingsManager.set_lambda_url(self.lambda_address.text())
        SettingsManager.set_data_exchange_layer_enabled(self.data_exchange_layer_enabled.isChecked())

        SettingsManager.finish()

    def load_settings(self):
        self.host.setText(SettingsManager.get_proxy_host())
        self.port.setValue(SettingsManager.get_proxy_port() or 0)
        self.lambda_address.setText(SettingsManager.get_lambda_url())
        self.data_exchange_layer_enabled.setChecked(SettingsManager.get_data_exchange_layer_enabled())


class ArhoOptionsPageFactory(QgsOptionsWidgetFactory):
    def __init__(self):
        super().__init__()
        self.setTitle("ARHO")
        self.setKey("ARHO")

    def createWidget(self, parent):  # noqa: N802
        return ArhoOptionsPage(parent)
