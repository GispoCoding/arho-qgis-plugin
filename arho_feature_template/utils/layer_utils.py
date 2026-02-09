from contextlib import contextmanager

from qgis.core import QgsVectorLayer

from arho_feature_template.project.layers.plan_layers import PlanLayer, plan_layers


def lock_plan_layers():
    """NOTE: Should be used from PlanManager if not temporary, otherwise PlanManager.plan_locked gets out of sync."""
    for layer in plan_layers:
        vlayer = layer.get_from_project()
        if vlayer is None:
            continue

        if vlayer.isEditable():
            vlayer.rollBack()

        vlayer.setReadOnly(True)


def unlock_plan_layers(start_editing_plan_layer: bool = True):  # noqa: FBT001, FBT002
    """NOTE: Should be used from PlanManager if not temporary, otherwise PlanManager.plan_locked gets out of sync."""
    for layer in plan_layers:
        vlayer = layer.get_from_project()
        if vlayer is None:
            continue

        vlayer.setReadOnly(False)

    if start_editing_plan_layer:
        PlanLayer.get_from_project().startEditing()


@contextmanager
def plan_layers_temporarily_unlocked():
    """Ensures layers are editable and returns to locked afterwards if they were locked before."""
    was_locked = PlanLayer.get_from_project().readOnly()

    unlock_plan_layers()
    try:
        yield
    finally:
        if was_locked:
            lock_plan_layers()


@contextmanager
def temporary_subset(layer: QgsVectorLayer, subset: str):
    """Sets a temporary subset string for given layer and stops edit mode if needed."""
    # NOTE: Do we want to snapshot the edit state before the subset and restore it afterwards?
    # was_in_edit_state_before = layer.isEditable()
    original = layer.subsetString()
    try:
        if layer.isEditable():
            layer.rollBack()
        layer.setSubsetString(subset)
        yield
    finally:
        if layer.isEditable():
            layer.rollBack()
        layer.setSubsetString(original)
        # if was_in_edit_state_before: layer.startEditing()
