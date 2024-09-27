from __future__ import annotations

import json
from typing import TYPE_CHECKING, Sequence

if TYPE_CHECKING:
    from os import PathLike

    from arho_feature_template.core.feature_template import FeatureTemplate


class FeatureTemplateLibrary:
    """Class for storing FeatureTemplates and loading them from a JSON (or other conf. file)."""

    def __init__(self, json_path: str | PathLike):
        self.templates: list[FeatureTemplate] = []
        library_dict = self.read_json(json_path)
        self.build_templates(library_dict)

    def read_json(self, json_path: str | PathLike) -> dict:
        self.source_json = json_path
        with open(json_path) as f:
            return json.load(f)

    def build_templates(self, library_dict: dict):
        templates: list[FeatureTemplate] = []

        _templates_raw = library_dict["templates"]
        # for template_raw in templates_raw:
        ## ... build FeatureTemplate from dict here, in FeatureTemplate class or elsewhere?
        # template = FeatureTemplate()
        # templates.append(template)
        self.templates = templates

    def get_templates(self) -> Sequence[FeatureTemplate]:
        return self.templates
