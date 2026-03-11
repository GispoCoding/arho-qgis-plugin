import logging
from contextlib import contextmanager

from qgis.core import QgsVectorLayer

from arho_feature_template.project.layers.plan_layers import PlanLayer, plan_layers

logger = logging.getLogger(__name__)


def lock_plan_layers():
    """NOTE: Should be used from PlanManager if not temporary, otherwise PlanManager.plan_locked gets out of sync."""
    logger.debug("Locking plan layers")
    for layer in plan_layers:
        vlayer = layer.get_from_project()
        if vlayer is None:
            logger.debug("Skipping lock for missing layer=%s", layer.name)
            continue

        if vlayer.isEditable():
            logger.debug("Rolling back editable layer before locking layer=%s", vlayer.name())
            vlayer.rollBack()

        vlayer.setReadOnly(True)
        logger.debug("Layer locked layer=%s", vlayer.name())


def unlock_plan_layers(start_editing_plan_layer: bool = True):  # noqa: FBT001, FBT002
    """NOTE: Should be used from PlanManager if not temporary, otherwise PlanManager.plan_locked gets out of sync."""
    logger.debug("Unlocking plan layers start_editing_plan_layer=%s", start_editing_plan_layer)
    for layer in plan_layers:
        vlayer = layer.get_from_project()
        if vlayer is None:
            logger.debug("Skipping unlock for missing layer=%s", layer.name)
            continue

        vlayer.setReadOnly(False)
        logger.debug("Layer unlocked layer=%s", vlayer.name())

    if start_editing_plan_layer:
        plan_layer = PlanLayer.get_from_project()
        plan_layer.startEditing()
        logger.debug("Started editing main plan layer layer=%s", plan_layer.name())


@contextmanager
def plan_layers_temporarily_unlocked():
    """Ensures layers are editable and returns to locked afterwards if they were locked before."""
    plan_layer = PlanLayer.get_from_project()
    was_locked = plan_layer.readOnly()
    logger.debug("Temporarily unlocking plan layers was_locked=%s", was_locked)

    unlock_plan_layers()
    try:
        yield
    finally:
        if was_locked:
            logger.debug("Restoring locked state for plan layers")
            lock_plan_layers()
        else:
            logger.debug("Leaving plan layers unlocked after temporary context")


@contextmanager
def temporary_subset(layer: QgsVectorLayer, subset: str):
    """Sets a temporary subset string for given layer and stops edit mode if needed."""
    # NOTE: Do we want to snapshot the edit state before the subset and restore it afterwards?
    # was_in_edit_state_before = layer.isEditable()
    original = layer.subsetString()
    logger.debug("Applying temporary subset layer=%s subset=%s", layer.name(), subset)
    try:
        if layer.isEditable():
            logger.debug("Rolling back layer before applying subset layer=%s", layer.name())
            layer.rollBack()
        layer.setSubsetString(subset)
        yield
    finally:
        if layer.isEditable():
            logger.debug("Rolling back layer before restoring subset layer=%s", layer.name())
            layer.rollBack()
        layer.setSubsetString(original)
        logger.debug("Restored original subset layer=%s", layer.name())
        # if was_in_edit_state_before: layer.startEditing()
