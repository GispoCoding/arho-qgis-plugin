from importlib import resources

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog

from arho_feature_template.core.feature_template import FeatureTemplate

ui_path = resources.files(__package__) / "feature_attribute_form.ui"
FormClass, _ = uic.loadUiType(ui_path)


class FeatureAttributeForm(QDialog, FormClass):  # type: ignore
    """Parent class for feature forms for adding and modifying feature attribute data."""

    def __init__(self, feature_template: FeatureTemplate):
        super().__init__()
        self.setupUi(self)
        self.feature_template = feature_template
