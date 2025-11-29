from __future__ import annotations

from importlib import resources
from pathlib import Path

import yaml
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog, QLabel

from arho_feature_template.qgis_plugin_tools.tools.i18n import tr

ui_path = resources.files(__package__) / "plugin_about.ui"
FormClass, _ = uic.loadUiType(ui_path)

PLUGIN_PATH = Path(__file__).resolve().parents[2]
FOLDER_PATH = PLUGIN_PATH / "resources" / "libraries" / "regulation_groups"


class PluginAbout(QDialog, FormClass):  # type: ignore
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.version_labels: dict[str, QLabel] = {
            tr("asemakaava"): self.katja_version_town,
            tr("yleiskaava"): self.katja_version_general,
            tr("maakuntakaava"): self.katja_version_regional,
        }

        self.show_versions()

    def _get_version_from_file(self, file_path: Path) -> str | None:
        if not file_path.is_file():
            return None

        with file_path.open("r") as f:
            data = yaml.safe_load(f)
            if "version" in data:
                return str(data["version"])
            return None

    def show_versions(self):
        if not FOLDER_PATH.exists():
            return

        for plan_type, label_widget in self.version_labels.items():
            file_path = FOLDER_PATH / f"katja_{plan_type}.yaml"
            version = self._get_version_from_file(file_path)
            label_widget.setText(version or "-")
