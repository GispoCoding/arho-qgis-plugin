import os

from qgis.core import QgsProject, QgsVectorLayer
from qgis.PyQt.QtWidgets import QMessageBox

PLUGIN_PATH = os.path.dirname(os.path.dirname(__file__))


def check_layer_changes() -> bool:
    """Check if there are unsaved changes in any QGIS layers."""
    project = QgsProject.instance()
    layers = project.mapLayers().values()

    return any(isinstance(layer, QgsVectorLayer) and layer.isModified() for layer in layers)


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
