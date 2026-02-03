from contextlib import contextmanager

from qgis.core import QgsVectorLayer

from arho_feature_template.core.models import Plan
from arho_feature_template.project.layers.plan_layers import PlanLayer, plan_layers
from arho_feature_template.utils.misc_utils import get_active_plan_id


def lock_plan_layers():
    for layer in plan_layers:
        vlayer = layer.get_from_project()
        if vlayer is None:
            continue

        if vlayer.isEditable():
            vlayer.rollBack()

        vlayer.setReadOnly(True)


def unlock_plan_layers(start_editing_plan_layer: bool = True):  # noqa: FBT001, FBT002
    for layer in plan_layers:
        vlayer = layer.get_from_project()
        if vlayer is None:
            continue

        vlayer.setReadOnly(False)

    if start_editing_plan_layer:
        PlanLayer.get_from_project().startEditing()


def update_lock_status_if_needed(edited_plan_model: Plan):
    """If edited plan is the active plan, applies locked/unlocked state from the given model."""
    if edited_plan_model.id_ == get_active_plan_id():
        if edited_plan_model.locked:
            lock_plan_layers()
        else:
            unlock_plan_layers()


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
