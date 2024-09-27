from arho_feature_template.core.feature_template import FeatureTemplate
from arho_feature_template.core.forms.feature_attribute_form import FeatureAttributeForm


class AddFeatureForm(FeatureAttributeForm):
    """Dialog for filling and saving attribute data that opens when a new feature has been digitized."""

    def __init__(self, feature_template: FeatureTemplate):
        super().__init__(feature_template)

    def _init_feature_attributes(self):
        # for feature_attribute in self.feature_template.feature_attributes:
        # # Create the form here, add rows with labels and input fields
        pass

    def save(self):
        pass
