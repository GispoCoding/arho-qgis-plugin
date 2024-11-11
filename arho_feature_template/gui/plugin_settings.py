from importlib import resources

from qgis.PyQt import uic
from qgis.PyQt.QtCore import QSettings
from qgis.PyQt.QtWidgets import QDialog

ui_path = resources.files(__package__) / "plugin_settings.ui"
FormClass, _ = uic.loadUiType(ui_path)


class PluginSettings(QDialog, FormClass):  # type: ignore
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setupUi(self)

        self.saveButton.clicked.connect(self.save_settings)

        self.load_settings()

    def load_settings(self):
        """Load settings from QSettings with default values."""
        settings = QSettings("ArhoFeatureTemplate")

        lambda_host = settings.value("lambda_host", "localhost")
        lambda_port = settings.value("lambda_port", "5435")

        self.hostInput.setText(lambda_host)
        self.portInput.setText(lambda_port)

    def save_settings(self):
        """Save settings to QSettings."""
        settings = QSettings("ArhoFeatureTemplate")
        settings.setValue("lambda_host", self.hostInput.text())
        settings.setValue("lambda_port", self.portInput.text())

        self.accept()
