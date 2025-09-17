from importlib import resources
from typing import TYPE_CHECKING

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog, QDialogButtonBox, QLineEdit

from arho_feature_template.core.settings_manager import SettingsManager

if TYPE_CHECKING:
    from qgis.gui import QgsSpinBox

ui_path = resources.files(__package__) / "plugin_settings.ui"
FormClass, _ = uic.loadUiType(ui_path)


class PluginSettings(QDialog, FormClass):  # type: ignore
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        # TYPES
        self.host: QLineEdit
        self.port: QgsSpinBox
        self.lambda_address: QLineEdit
        self.button_box: QDialogButtonBox

        # INIT
        self.load_settings()

        self.button_box.button(QDialogButtonBox.Ok)
        self.button_box.accepted.connect(self.save_settings)
        self.button_box.rejected.connect(self.reject)

    def load_settings(self):
        self.host.setText(SettingsManager.get_proxy_host())
        self.port.setValue(SettingsManager.get_proxy_port())
        self.lambda_address.setText(SettingsManager.get_lambda_url())

    def save_settings(self):
        SettingsManager.set_proxy_host(self.host.text())
        SettingsManager.set_proxy_port(self.port.value())
        SettingsManager.set_lambda_url(self.lambda_address.text())

        self.accept()
