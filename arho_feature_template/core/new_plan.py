from qgis.core import Qgis, QgsProject, QgsVectorLayer

from arho_feature_template.core.update_plan import LandUsePlan, update_selected_plan
from arho_feature_template.utils.qgis_utils import iface, show_message_bar


class NewPlan:
    def add_new_plan(self):
        # Filtered layers are not editable, so clear filters first.
        self.clear_all_filters()

        layers = QgsProject.instance().mapLayersByName("Kaava")
        if not layers:
            show_message_bar("Error", "Layer 'Kaava' not found", level=Qgis.MessageLevel.Warning)
            return

        kaava_layer = layers[0]

        if not kaava_layer.isEditable():
            kaava_layer.startEditing()

        iface.setActiveLayer(kaava_layer)

        iface.actionAddFeature().trigger()

        # Connect the featureAdded signal
        kaava_layer.featureAdded.connect(self.feature_added)

    def feature_added(self):
        kaava_layer = iface.activeLayer()
        kaava_layer.featureAdded.disconnect()
        feature_ids_before_commit = kaava_layer.allFeatureIds()
        if kaava_layer.isEditable():
            if not kaava_layer.commitChanges():
                show_message_bar("Error", "Failed to commit changes to the layer.", level=Qgis.MessageLevel.Warning)
                return
        else:
            show_message_bar("Error", "Layer is not editable.", level=Qgis.MessageLevel.Warning)
            return

        feature_ids_after_commit = kaava_layer.allFeatureIds()

        # Find the new plan.id by comparing fids before and after commit.
        new_feature_id = next((fid for fid in feature_ids_after_commit if fid not in feature_ids_before_commit), None)

        if new_feature_id is not None:
            new_feature = kaava_layer.getFeature(new_feature_id)

            if new_feature.isValid():
                feature_id_value = new_feature["id"]
                update_selected_plan(LandUsePlan(feature_id_value))
            else:
                show_message_bar("Error", "Invalid feature retrieved.", level=Qgis.MessageLevel.Warning)
        else:
            show_message_bar("Error", "No new feature was added.", level=Qgis.MessageLevel.Warning)

    def clear_all_filters(self):
        """Clear filters for all vector layers in the project."""
        layers = QgsProject.instance().mapLayers().values()

        for layer in layers:
            if isinstance(layer, QgsVectorLayer):
                layer.setSubsetString("")
