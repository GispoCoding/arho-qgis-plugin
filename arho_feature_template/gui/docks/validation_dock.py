from __future__ import annotations

import logging
import re
from importlib import resources
from typing import TYPE_CHECKING

from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsExpressionContextUtils,
    QgsGeometry,
    QgsProject,
)
from qgis.gui import QgsDockWidget
from qgis.PyQt import uic

from arho_feature_template.core.lambda_service import LambdaService
from arho_feature_template.core.settings_manager import SettingsManager
from arho_feature_template.project.layers.plan_layers import (
    AdditionalInformationLayer,
    PlanLayer,
    PlanPropositionLayer,
    PlanRegulationLayer,
    RegulationGroupLayer,
    plan_feature_layers,
)
from arho_feature_template.utils.misc_utils import disconnect_signal, get_active_plan_id, iface

if TYPE_CHECKING:
    from qgis.PyQt.QtWidgets import QLabel, QProgressBar, QPushButton

    from arho_feature_template.core.plan_manager import PlanManager
    from arho_feature_template.gui.components.validation_tree_view import ValidationTreeView

logger = logging.getLogger(__name__)

ui_path = resources.files(__package__) / "validation_dock.ui"
DockClass, _ = uic.loadUiType(ui_path)


class ValidationDock(QgsDockWidget, DockClass):  # type: ignore
    progress_bar: QProgressBar
    validation_result_tree_view: ValidationTreeView
    validate_button: QPushButton
    validate_plan_matter_button: QPushButton
    validation_label: QLabel

    def __init__(self, plan_manager: PlanManager, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.plan_manager = plan_manager
        self.lambda_service = LambdaService()
        self.lambda_service.validation_received.connect(self.list_validation_errors)
        self.lambda_service.validation_failed.connect(self.handle_validation_call_errors)
        self.validate_button.clicked.connect(self.validate_plan)
        self.validate_plan_matter_button.clicked.connect(self.validate_plan_matter)

        self.validation_result_tree_view.clicked.connect(self.on_item_clicked)
        self.validation_result_tree_view.doubleClicked.connect(self.on_item_double_clicked)

        if not SettingsManager.get_data_exchange_layer_enabled():
            self.validate_plan_matter_button.hide()

    def handle_validation_call_errors(self, error: str):
        self.validation_label.setText("Validoinnissa tapahtui virhe.")
        self.validation_label.setStyleSheet("QLabel {color: red}")

        logger.warning("Validoinnissa tapahtui virhe: %s", error)

        self.enable_validation()

    def on_permanent_identifier_set(self, identifier: str | None):
        """Enable the validate plan matter button when a valid permanent identifier is received."""
        if identifier:
            self.validate_plan_matter_button.setEnabled(True)
            self.validate_plan_matter_button.setToolTip("Lähetä liitteet Ryhtiin ja validoi kaava-asia")
        else:
            self.validate_plan_matter_button.setEnabled(False)
            self.validate_plan_matter_button.setToolTip("Hae ensin pysyvä kaavatunnus")

    def validate_plan(self):
        """Handles the button press to trigger the validation process."""
        # Get IDs from all layers
        # self.layer_features = self.get_all_features()

        self.validation_label.setText("Kaavasuunnitelman validointivirheet:")
        self.validation_label.setStyleSheet("")

        # Clear the existing errors from the list view
        self.validation_result_tree_view.clear_errors()

        active_plan_id = get_active_plan_id()
        if not active_plan_id:
            iface.messageBar().pushMessage("Virhe", "Ei aktiivista kaavasuunnitelmaa.", level=3)
            return

        # Disable buttons and show progress bar
        self.validate_button.setEnabled(False)
        self.validate_plan_matter_button.setEnabled(False)
        self.progress_bar.setVisible(True)

        self.lambda_service.validate_plan(active_plan_id)

    def validate_plan_matter(self):
        """Handles the button press to trigger the plan matter validation process."""

        self.validation_label.setText("Kaava-asian validointivirheet:")
        self.validation_label.setStyleSheet("")

        # Clear the existing errors from the list view
        self.validation_result_tree_view.clear_errors()

        active_plan_id = get_active_plan_id()
        if not active_plan_id:
            iface.messageBar().pushMessage("Virhe", "Ei aktiivista kaavasuunnitelmaa.", level=3)
            return

        # Disable buttons and show progress bar
        self.validate_plan_matter_button.setEnabled(False)
        self.validate_button.setEnabled(False)
        self.progress_bar.setVisible(True)

        self.lambda_service.validate_plan_matter(active_plan_id)

    def enable_validation(self):
        """Hide progress bar and re-enable the button"""
        self.progress_bar.setVisible(False)
        self.validate_button.setEnabled(True)

        # Retrieve the permanent_identifier from project variables
        permanent_identifier = QgsExpressionContextUtils.projectScope(QgsProject.instance()).variable(
            "permanent_identifier"
        )

        # Check if validate_plan_matter_button should be enabled
        if permanent_identifier:
            self.validate_plan_matter_button.setEnabled(True)
        else:
            self.validate_plan_matter_button.setEnabled(False)

        # Ensure the validation results are visible and properly resized
        self.validation_result_tree_view.expandAll()
        self.validation_result_tree_view.resizeColumnToContents(0)

    def list_validation_errors(self, validation_json):
        """Slot for listing validation errors and warnings."""

        if not validation_json:
            iface.messageBar().pushMessage("Virhe", "Validaatio json puuttuu.", level=1)
            self.enable_validation()
            return

        # If no errors or warnings, display a message and exit
        if not any(validation_json.values()):
            iface.messageBar().pushMessage("Virhe", "Ei virheitä havaittu.", level=1)
            self.enable_validation()
            return
        self.layer_features = {}

        for error_data in validation_json.values():
            if not isinstance(error_data, dict):
                continue

            errors = error_data.get("errors") or []
            # Sort so that errors with classKey are first
            errors = sorted(errors, key=lambda x: "classKey" not in x)
            for error in errors:
                self.get_feature_from_validation_error(error)
                self.validation_result_tree_view.add_error(
                    error.get("ruleId", ""),
                    error.get("instance", ""),
                    error.get("message", ""),
                    error.get("classKey", ""),
                    self.layer_features,
                )

            warnings = error_data.get("warnings") or []
            # Sort so that warnings with classKey are first
            warnings = sorted(warnings, key=lambda x: "classKey" not in x)
            for warning in warnings:
                self.get_feature_from_validation_error(warning)
                self.validation_result_tree_view.add_warning(
                    warning.get("ruleId", ""),
                    warning.get("instance", ""),
                    warning.get("message", ""),
                    warning.get("classKey", ""),
                    self.layer_features,
                )

        # Always enable validation at the end
        self.enable_validation()

    def on_item_clicked(self, index):
        model = self.validation_result_tree_view.model
        clicked_item = model.itemFromIndex(index)
        feature_id = clicked_item.feature_id

        if not feature_id:
            return

        feature_found, _ = self.layer_features.get(feature_id, (None, None))
        if feature_found and feature_found.geometry():
            self._zoom_to_feature(feature_found.geometry())

    def on_item_double_clicked(self, index):
        model = self.validation_result_tree_view.model
        clicked_item = model.itemFromIndex(index)
        feature_id = clicked_item.feature_id

        if not feature_id:
            iface.messageBar().pushWarning(
                "Lomakkeen avaaminen epäonnistui", "Kohteen ID puuttuu validointivirheen JSON:sta"
            )
            return

        feature_found, layer = self.layer_features.get(feature_id, (None, None))

        if feature_found:
            if feature_found.geometry():
                if "plan_type_id" in feature_found.fields().names():
                    self.plan_manager.edit_plan()
                else:
                    self.plan_manager.edit_plan_feature(feature=feature_found, layer_name=layer.name)
            else:
                if layer.name in ("Kaavamääräys", "Kaavasuositus"):
                    regulation_group_id = feature_found["plan_regulation_group_id"]
                elif layer.name == "Kaavamääräysryhmät":
                    regulation_group_id = feature_found["id"]

                regulation_group_feature, _ = self.layer_features[regulation_group_id]
                if regulation_group_feature:
                    regulation_group = RegulationGroupLayer.model_from_feature(regulation_group_feature)
                    self.plan_manager.edit_regulation_group(regulation_group)
        else:
            iface.messageBar().pushWarning("", "Ei avattavaa lomaketta.")

    def get_feature_from_validation_error(self, validation_json: dict):
        key = validation_json.get("classKey", "")
        object_path = validation_json.get("instance", "")
        if not key or not object_path:
            return

        object_path = object_path.lower()
        parts = object_path.split(".")
        match = [item for item in parts if re.search(r"\[\d+\]$", item)]
        # classKey is for the last object with square brackets, i.e. planRegulations[1] in plan.planRegulationGroups[0].planRegulations[1]
        object_with_id = match[-1] if match else None
        if object_with_id:
            # Remove square brackets and the number within
            object_with_id = re.sub(r"\[(\d+)\]", "", object_with_id)

        # If "plan" is in object path parts while there is no object with square brackets, it is likely we need plan feature for signal connections.
        if not object_with_id and "plan" in parts:
            feature = PlanLayer.get_feature_by_id(id_=key, no_geometries=False)
            self.layer_features[key] = (feature, PlanLayer)

        regulation_group_id = None

        if object_with_id == "planobjects":
            for feature_layer in plan_feature_layers:
                feature = feature_layer.get_feature_by_id(id_=key, no_geometries=False)
                if feature:
                    break
            self.layer_features[key] = (feature, feature_layer)

        elif object_with_id == "additionalinformations":
            feature = AdditionalInformationLayer.get_feature_by_id(key)
            if feature:
                self.layer_features[key] = (feature, AdditionalInformationLayer)
                plan_regulation_id = AdditionalInformationLayer.get_attribute_by_id(
                    target_attribute="plan_regulation_id", id_=key
                )
                if plan_regulation_id:
                    regulation_group_id = PlanRegulationLayer.get_attribute_by_id(
                        "plan_regulation_group_id", id_=plan_regulation_id
                    )
                    if regulation_group_id:
                        feature = RegulationGroupLayer.get_feature_by_id(regulation_group_id)
                        if feature and regulation_group_id not in self.layer_features:
                            self.layer_features[regulation_group_id] = (feature, RegulationGroupLayer)

        elif object_with_id == "planregulations":
            feature = PlanRegulationLayer.get_feature_by_id(key)
            if feature:
                self.layer_features[key] = (feature, PlanRegulationLayer)
                plan_regulation_id = key
                if plan_regulation_id:
                    regulation_group_id = PlanRegulationLayer.get_attribute_by_id(
                        "plan_regulation_group_id", id_=plan_regulation_id
                    )
                    if regulation_group_id:
                        feature = RegulationGroupLayer.get_feature_by_id(regulation_group_id)
                        if feature and regulation_group_id not in self.layer_features:
                            self.layer_features[regulation_group_id] = (feature, RegulationGroupLayer)

        elif object_with_id == "planrecommendations":
            feature = PlanPropositionLayer.get_feature_by_id(key)
            if feature:
                self.layer_features[key] = (feature, PlanPropositionLayer)
                regulation_group_id = PlanPropositionLayer.get_attribute_by_id(
                    target_attribute="plan_regulation_group_id", id_=key
                )
                if regulation_group_id:
                    feature = RegulationGroupLayer.get_feature_by_id(regulation_group_id)
                    if feature and regulation_group_id not in self.layer_features:
                        self.layer_features[regulation_group_id] = (feature, RegulationGroupLayer)

        elif object_with_id == "planregulationgroups":
            feature = RegulationGroupLayer.get_feature_by_id(key)
            self.layer_features[key] = (feature, RegulationGroupLayer)

    def _zoom_to_feature(self, geom: QgsGeometry):
        bounding_box = geom.boundingBox()
        canvas = iface.mapCanvas()
        canvas.zoomToFeatureExtent(bounding_box.buffered(1000))
        canvas.flashGeometries(geometries=[geom], crs=QgsCoordinateReferenceSystem("EPSG:3067"))
        canvas.redrawAllLayers()

    def unload(self):
        disconnect_signal(self.validation_result_tree_view.clicked)
        disconnect_signal(self.validation_result_tree_view.doubleClicked)
