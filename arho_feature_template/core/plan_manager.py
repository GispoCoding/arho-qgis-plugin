from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING

from qgis.core import (
    QgsExpressionContextUtils,
    QgsProject,
    QgsVectorLayer,
)
from qgis.gui import QgsMapToolDigitizeFeature
from qgis.PyQt.QtWidgets import QDialog, QMessageBox
from qgis.utils import iface

from arho_feature_template.core.lambda_service import LambdaService
from arho_feature_template.exceptions import UnsavedChangesError
from arho_feature_template.gui.load_plan_dialog import LoadPlanDialog
from arho_feature_template.gui.plan_attribure_form import PlanAttributeForm
from arho_feature_template.gui.serialize_plan import SerializePlan
from arho_feature_template.project.layers.plan_layers import PlanLayer, RegulationGroupLayer, plan_layers
from arho_feature_template.utils.db_utils import get_existing_database_connection_names
from arho_feature_template.utils.misc_utils import (
    check_layer_changes,
    get_active_plan_id,
    handle_unsaved_changes,
)

if TYPE_CHECKING:
    from qgis.core import QgsFeature

    from arho_feature_template.core.models import Plan, RegulationGroup
logger = logging.getLogger(__name__)


class PlanDigitizeMapTool(QgsMapToolDigitizeFeature): ...


class PlanManager:
    def __init__(self):
        self.json_plan_path = None
        self.json_plan_outline_path = None

        self.digitize_map_tool = PlanDigitizeMapTool(iface.mapCanvas(), iface.cadDockWidget())
        self.digitize_map_tool.digitizingCompleted.connect(self._plan_geom_digitized)

    def add_new_plan(self):
        """Initiate the process to add a new plan to the Kaava layer."""

        self.previous_map_tool = iface.mapCanvas().mapTool()
        self.previous_active_plan_id = get_active_plan_id()

        if not handle_unsaved_changes():
            return

        plan_layer = PlanLayer.get_from_project()
        if not plan_layer:
            return
        self.previously_editable = plan_layer.isEditable()

        self.set_active_plan(None)

        plan_layer.startEditing()
        self.digitize_map_tool.setLayer(plan_layer)
        iface.mapCanvas().setMapTool(self.digitize_map_tool)

    def _plan_geom_digitized(self, feature: QgsFeature):
        """Callback for when a new feature is added to the Kaava layer."""
        plan_layer = PlanLayer.get_from_project()
        if not plan_layer:
            return

        attribute_form = PlanAttributeForm()
        if attribute_form.exec_():
            plan_attributes = attribute_form.get_plan_attributes()
            plan_attributes.geom = feature.geometry()
            feature = save_plan(plan_attributes)
            plan_to_be_activated = feature["id"]
        else:
            plan_to_be_activated = self.previous_active_plan_id

        self.set_active_plan(plan_to_be_activated)

        if self.previously_editable:
            plan_layer.startEditing()

        iface.mapCanvas().setMapTool(self.previous_map_tool)

    def set_active_plan(self, plan_id: str | None):
        """Update the project layers based on the selected land use plan.

        Layers to be filtered cannot be in edit mode.
        This method disables edit mode temporarily if needed.
        Therefore if there are unsaved changes, this method will raise an exception.
        """

        if check_layer_changes():
            raise UnsavedChangesError

        plan_layer = PlanLayer.get_from_project()
        previously_in_edit_mode = plan_layer.isEditable()
        if previously_in_edit_mode:
            plan_layer.rollBack()

        QgsExpressionContextUtils.setProjectVariable(QgsProject.instance(), "active_plan_id", plan_id)
        for layer in plan_layers:
            layer.apply_filter(plan_id)

        if previously_in_edit_mode:
            plan_layer.startEditing()

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

            self.set_active_plan(selected_plan_id)

    def commit_all_editable_layers(self):
        """Commit all changes in any editable layers."""
        for layer in QgsProject.instance().mapLayers().values():
            if isinstance(layer, QgsVectorLayer) and layer.isEditable():
                layer.commitChanges()

    def get_plan_json(self):
        """Serializes plan and plan outline to JSON"""
        dialog = SerializePlan()
        if dialog.exec_() == QDialog.Accepted:
            self.json_plan_path = dialog.plan_path_edit.text()
            self.json_plan_outline_path = dialog.plan_outline_path_edit.text()

            plan_id = get_active_plan_id()
            if not plan_id:
                QMessageBox.critical(None, "Virhe", "Ei aktiivista kaavaa.")
                return

            self.lambda_service = LambdaService()
            self.lambda_service.jsons_received.connect(self.save_plan_jsons)
            self.lambda_service.serialize_plan(plan_id)

    def save_plan_jsons(self, plan_json, outline_json):
        """This slot saves the plan and outline JSONs to files."""
        if plan_json is None or outline_json is None:
            QMessageBox.critical(None, "Virhe", "Kaava tai sen ulkoraja ei löytynyt.")
            return

        # Retrieve paths
        if self.json_plan_path is None or self.json_plan_outline_path is None:
            QMessageBox.critical(None, "Virhe", "Tiedostopolut eivät ole saatavilla.")
            return

        # Save the JSONs
        with open(self.json_plan_path, "w", encoding="utf-8") as full_file:
            json.dump(plan_json, full_file, ensure_ascii=False, indent=2)

        with open(self.json_plan_outline_path, "w", encoding="utf-8") as outline_file:
            json.dump(outline_json, outline_file, ensure_ascii=False, indent=2)

        QMessageBox.information(
            None,
            "Tallennus onnistui",
            "Kaava ja sen ulkoraja tallennettu onnistuneesti.",
        )


def save_plan(plan_data: Plan) -> QgsFeature:
    plan_layer = PlanLayer.get_from_project()
    in_edit_mode = plan_layer.isEditable()
    if not in_edit_mode:
        plan_layer.startEditing()

    edit_message = "Kaavan lisäys" if plan_data.id_ is None else "Kaavan muokkaus"
    plan_layer.beginEditCommand(edit_message)

    plan_data.organisation_id = "99e20d66-9730-4110-815f-5947d3f8abd3"
    plan_feature = PlanLayer.feature_from_model(plan_data)

    if plan_data.id_ is None:
        plan_layer.addFeature(plan_feature)
    else:
        plan_layer.updateFeature(plan_feature)

    plan_layer.endEditCommand()
    plan_layer.commitChanges(stopEditing=False)

    if plan_data.general_regulations:
        for regulation_group in plan_data.general_regulations:
            plan_id = plan_feature["id"]
            regulation_group_feature = save_regulation_group(regulation_group, plan_id)
            save_regulation_grop_assosiation(plan_id, regulation_group_feature["id"])

    return plan_feature


def save_regulation_group(regulation_group: RegulationGroup, plan_id: str) -> QgsFeature:
    feature = RegulationGroupLayer.feature_from_model(regulation_group)
    feature["plan_id"] = plan_id
    return feature


def save_regulation_grop_assosiation(plan_id: str, regulation_group_id: str):
    pass
