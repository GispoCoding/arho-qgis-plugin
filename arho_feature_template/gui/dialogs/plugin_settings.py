from importlib import resources

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog

from arho_feature_template.core.settings_manager import SettingsManager

ui_path = resources.files(__package__) / "plugin_settings.ui"
FormClass, _ = uic.loadUiType(ui_path)


class PluginSettings(QDialog, FormClass):  # type: ignore
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.saveButton.clicked.connect(self.save_settings)
        self.load_settings()

    def load_settings(self):
        self.hostInput.setText(SettingsManager.get_proxy_host())
        self.portInput.setText(str(SettingsManager.get_proxy_port()))
        self.lambdaInput.setText(SettingsManager.get_lambda_url())

    def save_settings(self):
        SettingsManager.set_proxy_host(self.hostInput.text())
        SettingsManager.set_proxy_port(int(self.portInput.text()))
        SettingsManager.set_lambda_url(self.lambdaInput.text())

        self.accept()
