import logging

from qgis.core import QgsProject, QgsVectorLayer

from arho_feature_template.exceptions import LayerNotFoundError, LayerNotVectorTypeError

logger = logging.getLogger(__name__)


def get_layer_from_project(layer_name: str) -> QgsVectorLayer:
    project = QgsProject.instance()
    if not project:
        raise LayerNotFoundError(layer_name)

    layers = project.mapLayersByName(layer_name)
    if not layers:
        raise LayerNotFoundError(layer_name)

    if len(layers) > 1:
        logger.warning("Multiple layers with the same name found. Using the first one.")

    layer = layers[0]
    if not isinstance(layer, QgsVectorLayer):
        raise LayerNotVectorTypeError(layer_name)

    return layer
