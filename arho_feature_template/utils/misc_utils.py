from __future__ import annotations

import json
import os
from contextlib import suppress
from functools import wraps
from typing import TYPE_CHECKING, Any, cast

from qgis.core import QgsExpressionContextUtils, QgsProject, QgsSymbol, QgsVectorLayer
from qgis.PyQt.QtCore import NULL, Qt, pyqtBoundSignal
from qgis.PyQt.QtWidgets import QMessageBox
from qgis.utils import OverrideCursor, iface

if TYPE_CHECKING:
    from qgis.core import QgsMapLayer
    from qgis.gui import QgisInterface

    iface: QgisInterface = cast("QgisInterface", iface)  # type: ignore[no-redef]

PLUGIN_PATH = os.path.dirname(os.path.dirname(__file__))

LANGUAGE = "fin"


# NOTE: Consider creating "layer_utils.py" or similar for layer related utils in the future
def get_layer_by_name(layer_name: str) -> QgsMapLayer | None:
    """
    Retrieve a layer by name from the project.

    If multiple layers with the same name exist, returns the first one. Returns None
    if layer with a matching name is not found.
    """
    layers = QgsProject.instance().mapLayersByName(layer_name)
    if layers:
        return layers[0]
    iface.messageBar().pushWarning("Error", f"Layer '{layer_name}' not found")
    return None


def check_layer_changes() -> bool:
    """Check if there are unsaved changes in any QGIS layers."""
    project = QgsProject.instance()
    layers = project.mapLayers().values()

    return any(layer.isModified() for layer in layers if isinstance(layer, QgsVectorLayer))


def prompt_commit_changes() -> bool:
    """Ask user if changes should be committed."""
    response = QMessageBox.question(
        None,
        "Tallentamattomat muutokset",
        "Tasoilla on tallentamattomia muutoksia. Tallenetaanko muutokset?",
        QMessageBox.Yes | QMessageBox.No,
    )
    return response == QMessageBox.Yes


def commit_all_layer_changes() -> bool:
    """
    Commit changes to all modified layers in the QGIS project.
    Returns True if all changes were successfully committed, False if any failed.
    """
    project = QgsProject.instance()
    layers = project.mapLayers().values()
    all_committed = True

    for layer in layers:
        if isinstance(layer, QgsVectorLayer) and layer.isModified() and not layer.commitChanges():
            QMessageBox.critical(None, "Virhe", f"Tason {layer.name()} muutosten tallentaminen epäonnistui.")
            all_committed = False

    return all_committed


def handle_unsaved_changes() -> bool:
    """
    Wrapper function to check for unsaved changes, prompt user to commit, and commit changes if chosen.
    Returns:
        bool: True if changes are committed or no changes were found;
            False if user does not want to commit or if commit fails.
    """
    if check_layer_changes():
        if not prompt_commit_changes():
            return False
        if not commit_all_layer_changes():
            return False
    return True


def set_active_plan_id(plan_id: str | None):
    """Store the given plan ID as project variables."""
    QgsExpressionContextUtils.setProjectVariable(
        QgsProject.instance(), "active_plan_id", plan_id if plan_id is not None else ""
    )


def set_active_plan_name(plan_name: str | None):
    """Store the given plan name as project variables."""
    QgsExpressionContextUtils.setProjectVariable(
        QgsProject.instance(), "active_plan_name", plan_name if plan_name is not None else ""
    )


def get_active_plan_id():
    """Retrieve the active plan ID stored as a project variable."""
    return QgsExpressionContextUtils.projectScope(QgsProject.instance()).variable("active_plan_id")


def get_active_plan_name():
    """Retrieve the active plan name stored as a project variable."""
    return QgsExpressionContextUtils.projectScope(QgsProject.instance()).variable("active_plan_name")


def set_active_plan_matter_id(plan_matter_id: str | None):
    """Store the given plan matter ID as project variables."""
    QgsExpressionContextUtils.setProjectVariable(
        QgsProject.instance(), "active_plan_matter_id", plan_matter_id if plan_matter_id is not None else ""
    )


def set_active_plan_matter_name(plan_matter_name: str | None):
    """Store the given plan matter name as project variables."""
    QgsExpressionContextUtils.setProjectVariable(
        QgsProject.instance(), "active_plan_matter_name", plan_matter_name if plan_matter_name is not None else ""
    )


def get_active_plan_matter_id():
    """Retrieve the active plan matter ID stored as a project variable."""
    return QgsExpressionContextUtils.projectScope(QgsProject.instance()).variable("active_plan_matter_id")


def get_active_plan_matter_name():
    """Retrieve the active plan matter name stored as a project variable."""
    return QgsExpressionContextUtils.projectScope(QgsProject.instance()).variable("active_plan_matter_name")


def disconnect_signal(signal: pyqtBoundSignal) -> None:
    """
    Disconnects all existing connections of a given signal.

    If no connections are defined for the signal, ignores the raised error silently.
    """
    with suppress(TypeError):
        signal.disconnect()


def serialize_localized_text(text: str | None) -> dict[str, str] | None:
    if isinstance(text, str):
        text = text.strip()
    if text:
        return {LANGUAGE: text}
    return None


def deserialize_localized_text(text_value: dict[str, str] | None | Any) -> str | None:
    text = None
    if isinstance(text_value, dict):
        text = text_value.get(LANGUAGE)
    return text


def use_wait_cursor(func):
    """Decorator for showing wait cursor during function execution."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        with OverrideCursor(Qt.WaitCursor):
            return func(*args, **kwargs)

    return wrapper


def status_message(message: str, timeout: int = 0):
    """Decorator for displaying a message in the QGIS status bar during function execution."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            iface.statusBarIface().showMessage(message, timeout)
            try:
                return func(*args, **kwargs)
            finally:
                iface.statusBarIface().clearMessage()

        return wrapper

    return decorator


def null_to_none(value) -> Any:
    if value == NULL or value is None:
        return None
    return value


def set_imported_layer_invisible(layer: QgsVectorLayer) -> None:
    root = QgsProject.instance().layerTreeRoot()
    layer_node = root.findLayer(layer.id())
    layer_node.setItemVisibilityChecked(False)


def symbol_fingerprint(symbol: QgsSymbol) -> str:
    data = {
        "type": symbol.type(),
        "layers": [
            {
                "layer": layer.layerType(),
                "props": layer.properties(),
            }
            for layer in symbol.symbolLayers()
        ],
    }
    return json.dumps(data, sort_keys=True)
