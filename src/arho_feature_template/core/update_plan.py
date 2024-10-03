from dataclasses import dataclass

from typing import List

from qgis.core import QgsProject, QgsVectorLayer, QgsMapLayer


@dataclass
class LandUsePlan:
    id: str
    name: str


LAYER_PLAN_ID_MAP = {
    "Kaava": "id",
    "Aluevaraus": "plan_id",
    "Osa-alue": "plan_id",
}


def update_selected_plan(new_plan: LandUsePlan):
    id = new_plan.id
    for layer_name, field_name in LAYER_PLAN_ID_MAP.items():
        set_filter_for_layer(layer_name, field_name, id)


def set_filter_for_layer(layer_name: str, field_name: str, field_value: str):
    # Get layer and perform checks
    layers = QgsProject.instance().mapLayersByName(layer_name)
    if not _check_layer_count(layers):
        return
    layer = layers[0]
    if not _check_vector_layer(layer):
        return

    # Perform the filtering
    query = f"{field_name} = {field_value}"
    if not layer.setSubsetString(query):
        # TODO: Convert to log msg?
        print(f"ERROR: Failed to filter layer {layer_name} with query {query}")


def _check_layer_count(layers: List[QgsMapLayer]) -> bool:
    if len(layers) > 1:
        # TODO: Convert to log msg?
        print(f"ERROR: Found multiple layers ({len(layers)}) with same name ({layers[0].name()}).")
        return False
    return True


def _check_vector_layer(layer: QgsMapLayer) -> bool:
    if not isinstance(layer, QgsVectorLayer):
        # TODO: Convert to log msg?
        print(f"ERROR: Layer {layer.name()} is not a vector layer: f{type(layer)}")
        return False
    return True
