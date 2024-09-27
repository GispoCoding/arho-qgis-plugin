from importlib import resources

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QWidget

from arho_feature_template.core.feature_template_library import FeatureTemplateLibrary

ui_path = resources.files(__package__) / "template_library_panel.ui"
FormClass, _ = uic.loadUiType(ui_path)


class TemplateLibraryPanel(QWidget, FormClass):  # type: ignore
    """Dock widget for selecting a feature template."""

    def __init__(self, feature_template_library: FeatureTemplateLibrary):
        super().__init__()
        self.setupUi(self)
        self.initialize_from_library(feature_template_library)

    def initialize_from_library(self, feature_template_library: FeatureTemplateLibrary):
        # Initialization logic
        self.library = feature_template_library
