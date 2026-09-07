from __future__ import annotations

import logging

from qgis.core import QgsLayerTreeGroup, QgsProject, QgsVectorLayer

from arho_feature_template.exceptions import LayerGroupNotFoundError, LayerNotFoundError

logger = logging.getLogger(__name__)

# Layer names are not unique in the project: the "Ajantasakaava" group holds read-only
# views that repeat the names used by the editable plan layers. Every lookup therefore
# has to say which layer tree group the layer is expected to be in.
PLAN_LAYER_GROUP_NAME = "Kaavasuunnitelma"
VALID_LAYER_GROUP_NAME = "Ajantasakaava"
CODE_LAYER_GROUP_NAME = "Koodit"


def get_layer_group(group_name: str) -> QgsLayerTreeGroup:
    project = QgsProject.instance()
    if not project:
        raise LayerGroupNotFoundError(group_name)

    group = project.layerTreeRoot().findGroup(group_name)
    if group is None:
        raise LayerGroupNotFoundError(group_name)

    return group


def find_vector_layers(layer_name: str, group_name: str) -> list[QgsVectorLayer]:
    """Vector layers named `layer_name` within `group_name`, sub-groups included."""
    vector_layers = []
    for node in get_layer_group(group_name).findLayers():
        layer = node.layer()  # None if the layer has not been resolved (yet)
        if isinstance(layer, QgsVectorLayer) and layer.name() == layer_name:
            vector_layers.append(layer)
    return vector_layers


def get_vector_layer_from_project(layer_name: str, group_name: str) -> QgsVectorLayer:
    vector_layers = find_vector_layers(layer_name, group_name)
    if not vector_layers:
        raise LayerNotFoundError(layer_name, group_name)

    if len(vector_layers) > 1:
        logger.warning("Multiple layers named %s found in group %s. Using the first one.", layer_name, group_name)
    return vector_layers[0]
