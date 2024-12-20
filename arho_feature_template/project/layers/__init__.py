from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, ClassVar

from qgis.core import QgsFeatureRequest

from arho_feature_template.utils.project_utils import get_vector_layer_from_project

if TYPE_CHECKING:
    from qgis.core import QgsFeature, QgsFeatureIterator, QgsVectorLayer


class AbstractLayer(ABC):
    name: ClassVar[str]

    @classmethod
    def get_from_project(cls) -> QgsVectorLayer:
        return get_vector_layer_from_project(cls.name)

    @classmethod
    def get_features(cls) -> QgsFeatureIterator:
        return cls.get_from_project().getFeatures()

    @classmethod
    def get_feature_by_id(cls, _id: str) -> QgsFeature | None:
        request = QgsFeatureRequest().setFilterExpression(f"\"id\"='{_id}'")
        return next(cls.get_from_project().getFeatures(request), None)
