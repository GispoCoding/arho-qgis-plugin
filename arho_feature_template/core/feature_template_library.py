from __future__ import annotations

from typing import TYPE_CHECKING, Sequence

from qgis.core import QgsMapLayer, QgsProject, QgsVectorLayer
from qgis.utils import iface

from arho_feature_template.core.feature_template import FeatureTemplate
from arho_feature_template.core.json_config import JsonKeys
from arho_feature_template.core.utils import read_json

if TYPE_CHECKING:
    from os import PathLike


class FeatureTemplateLibrary:
    """Class for storing FeatureTemplates and loading them from a JSON (or other conf. file)."""

    def __init__(self, json_path: str | PathLike):
        self.templates = []
        library_dict = read_json(json_path)
        self.name = library_dict.get(JsonKeys.NAME)
        self.version = library_dict.get(JsonKeys.VERSION)
        self.build_templates(library_dict)

    def build_templates(self, library_dict: dict):
        """Build feature templates from input `library_dict` and update `templates` attribute."""
        all_templates_count = 0
        invalid_templates_count = 0
        templates = []

        templates_raw = library_dict.get(JsonKeys.TEMPLATES)
        if not templates_raw:
            iface.messageBar().pushWarning(
                "Error: ", f"Could not find any templates in the template library JSON with key {JsonKeys.TEMPLATES}."
            )
            return

        # Go through each template data in the dictionary, save info about invalid templates?
        for template_raw in templates_raw:
            template = self.build_feature_template(template_raw)
            if not template:
                invalid_templates_count += 1
            else:
                templates.append(template)
            all_templates_count += 1

        self.templates = templates

        if invalid_templates_count > 0:
            iface.messageBar().pushWarning(
                "Warning: ",
                f"Failed to create {invalid_templates_count} out of {all_templates_count} \
                feature templates from the template library JSON."
            )

    def build_feature_template(self, template_dict: dict) -> FeatureTemplate | None:
        """
        Attempt to build a `FeatureTemplate` from given `template_dict`.

        Args:
            template_dict: Information about a feature template as a dictionary.

        Returns:
            `FeatureTemplate` if building was successful, otherwise None.
        """
        name: str = template_dict.get(JsonKeys.NAME)
        description: str = template_dict.get(JsonKeys.DESCRIPTION, "No description")
        feature: dict = template_dict.get(JsonKeys.FEATURE, {})
        feature_layer_name: str = feature.get(JsonKeys.LAYER, "")
        layers = QgsProject.instance().mapLayersByName(feature_layer_name)
        if not layers:
            feature_layer = None
        else:
            feature_layer: QgsMapLayer = layers[0]
            # Is this needed?
            if len(layers) > 1:
                iface.messageBar().pushWarning(
                    "Warning: ",
                    f"Multiple layers with the specified feature layer name {feature_layer_name} found \
                    for feature template {name}, using the first match."
                )

            if not isinstance(feature_layer, QgsVectorLayer):
                iface.messageBar().pushWarning(
                    "Error: ",
                    f"Feature layer found but has invalid type {type(feature_layer)} for feature template {name}."
                )
                feature_layer = None

        # All information is needed for FeatureTemplate except for description?
        if not name or not feature or not feature_layer_name or not feature_layer:
            return None

        # TODO: fields of feature layer
        # feature_fields = feature.get(JsonKeys.FIELDS, [])

        feature_template = FeatureTemplate(
            name=name,
            description=description,
            feature_layer=feature_layer,
        )
        feature_attribute_groups = feature.get(JsonKeys.CHILDREN, [])
        feature_template.add_feature_attributes(feature_attribute_groups)

        return feature_template

    def get_templates(self) -> Sequence[FeatureTemplate]:
        return self.templates
