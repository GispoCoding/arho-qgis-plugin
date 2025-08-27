from importlib import resources
from pathlib import Path

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog, QLabel

ui_path = resources.files(__package__) / "plugin_about.ui"
FormClass, _ = uic.loadUiType(ui_path)

PLUGIN_PATH = Path(__file__).resolve().parents[2]
FILE_PATH = PLUGIN_PATH / "metadata.txt"


class PluginAbout(QDialog, FormClass):  # type: ignore
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setupUi(self)

        self.plugin_version_label: QLabel
        self.katja_version_label: QLabel

        self.show_versions()

    def show_versions(self):
        if not FILE_PATH.exists():
            return

        with open(FILE_PATH) as file:
            for line in file:
                if line.strip().startswith("version="):
                    self.plugin_version_label.setText(line.strip().split("=", 1)[1])
                if line.strip().startswith("katja_version="):
                    self.katja_version_label.setText(line.strip().split("=", 1)[1])
