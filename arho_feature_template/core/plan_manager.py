from qgis.core import QgsExpressionContextUtils, QgsProject, QgsVectorLayer
from qgis.PyQt.QtWidgets import QDialog, QMessageBox
from qgis.utils import iface

from arho_feature_template.core.update_plan import LandUsePlan, update_selected_plan
from arho_feature_template.gui.load_plan_dialog import LoadPlanDialog
from arho_feature_template.utils.db_utils import get_existing_database_connection_names
from arho_feature_template.utils.misc_utils import handle_unsaved_changes


class PlanManager:
    def __init__(self):
        self.kaava_layer = self.get_layer_by_name("Kaava")

    def get_layer_by_name(self, layer_name):
        """Retrieve a layer by name from the project."""
        layers = QgsProject.instance().mapLayersByName(layer_name)
        if layers:
            return layers[0]
        iface.messageBar().pushMessage("Error", f"Layer '{layer_name}' not found", level=3)
        return None

    def add_new_plan(self):
        """Initiate the process to add a new plan to the Kaava layer."""
        if not handle_unsaved_changes():
            return

        self.clear_all_filters()

        if not self.kaava_layer:
            return

        if not self.kaava_layer.isEditable():
            self.kaava_layer.startEditing()

        iface.setActiveLayer(self.kaava_layer)
        iface.actionAddFeature().trigger()

        # Connect the featureAdded signal to a callback method
        self.kaava_layer.featureAdded.connect(self.feature_added)

    def feature_added(self):
        """Callback for when a new feature is added to the Kaava layer."""
        if not self.kaava_layer:
            return

        # Disconnect the signal to avoid repeated triggers
        self.kaava_layer.featureAdded.disconnect()

        feature_ids_before_commit = self.kaava_layer.allFeatureIds()

        if self.kaava_layer.isEditable():
            if not self.kaava_layer.commitChanges():
                iface.messageBar().pushMessage("Error", "Failed to commit changes to the layer.", level=3)
                return
        else:
            iface.messageBar().pushMessage("Error", "Layer is not editable.", level=3)
            return

        feature_ids_after_commit = self.kaava_layer.allFeatureIds()
        new_feature_id = next((fid for fid in feature_ids_after_commit if fid not in feature_ids_before_commit), None)

        if new_feature_id is not None:
            new_feature = self.kaava_layer.getFeature(new_feature_id)
            if new_feature.isValid():
                feature_id_value = new_feature["id"]
                update_selected_plan(LandUsePlan(feature_id_value))
            else:
                iface.messageBar().pushMessage("Error", "Invalid feature retrieved.", level=3)
        else:
            iface.messageBar().pushMessage("Error", "No new feature was added.", level=3)

    def load_land_use_plan(self):
        """Load an existing land use plan using a dialog selection."""
        connections = get_existing_database_connection_names()

        if not connections:
            QMessageBox.critical(None, "Error", "No database connections found.")
            return

        if not handle_unsaved_changes():
            return

        dialog = LoadPlanDialog(None, connections)

        if dialog.exec_() == QDialog.Accepted:
            selected_plan_id = dialog.get_selected_plan_id()
            self.commit_all_editable_layers()

            if not selected_plan_id:
                QMessageBox.critical(None, "Error", "No plan was selected.")
                return

            plan = LandUsePlan(selected_plan_id)
            update_selected_plan(plan)

    def clear_all_filters(self):
        """Clear active_plan_id and filters for all vector layers in the project."""
        QgsExpressionContextUtils.setProjectVariable(QgsProject.instance(), "active_plan_id", None)
        for layer in QgsProject.instance().mapLayers().values():
            if isinstance(layer, QgsVectorLayer):
                layer.setSubsetString("")

    def commit_all_editable_layers(self):
        """Commit all changes in any editable layers."""
        for layer in QgsProject.instance().mapLayers().values():
            if isinstance(layer, QgsVectorLayer) and layer.isEditable():
                layer.commitChanges()
