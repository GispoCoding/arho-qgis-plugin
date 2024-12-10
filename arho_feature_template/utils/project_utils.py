import logging

from qgis.core import QgsProject, QgsVectorLayer

from arho_feature_template.exceptions import LayerNotFoundError

logger = logging.getLogger(__name__)


def get_vector_layer_from_project(layer_name: str) -> QgsVectorLayer:
    project = QgsProject.instance()
    if not project:
        raise LayerNotFoundError(layer_name)

    layers = project.mapLayersByName(layer_name)
    if not layers:
        raise LayerNotFoundError(layer_name)

    vector_layers = [layer for layer in layers if isinstance(layer, QgsVectorLayer)]
    if not vector_layers:
        raise LayerNotFoundError(layer_name)

    if len(vector_layers) > 1:
        logger.warning("Multiple layers with the same name found. Using the first one.")
    return vector_layers[0]
