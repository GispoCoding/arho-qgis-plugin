from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Sequence

if TYPE_CHECKING:
    from qgis.core import QgsVectorLayer
    from qgis.gui import QgsDoubleSpinBox, QgsSpinBox
    from qgis.PyQt.QtGui import QIcon
    from qgis.PyQt.QtWidgets import QLineEdit


@dataclass
class FeatureAttribute:
    name: str
    display_name: str
    feature_attribte_group: str
    # attribute_layer: QgsMapLayer  # Is this correct type?
    additional_information: str
    input_field_type: QLineEdit | QgsSpinBox | QgsDoubleSpinBox | None
    modifiable: bool = False
    hidden: bool = False


@dataclass
class FeatureTemplate:
    name: str
    description: str
    feature_layer: QgsVectorLayer
    feature_attributes: Sequence[FeatureAttribute] | None = None
    display_icon: QIcon | None = None

    def add_feature_attributes(self, feature_attribute_groups: Sequence[dict]):
        for _group in feature_attribute_groups:
            # Should we add FeatureAttributeGroup as a class? Or can group name be
            # only one class attribute of FeatureAttribute?
            # TODO
            pass
