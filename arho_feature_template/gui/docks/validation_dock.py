from __future__ import annotations

import logging
from importlib import resources
from typing import TYPE_CHECKING

from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsExpressionContextUtils,
    QgsFeature,
    QgsFeatureRequest,
    QgsGeometry,
    QgsMapLayer,
    QgsProject,
)
from qgis.gui import QgsDockWidget
from qgis.PyQt import uic

from arho_feature_template.core.lambda_service import LambdaService
from arho_feature_template.project.layers.plan_layers import (
    PlanPropositionLayer,
    PlanRegulationLayer,
    RegulationGroupLayer,
    plan_features_and_regulations,
    plan_layers,
)
from arho_feature_template.utils.misc_utils import get_active_plan_id, iface

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

        self.annotation_layer = None
        self._annotation_ids: dict[str, list[str]] = {}

    def handle_validation_call_errors(self, error: str):
        self.validation_label.setText("Kaavan validoinnissa tapahtui virhe.")
        self.validation_label.setStyleSheet("QLabel {color: red}")

        logger.warning("Kaavan validoinnissa tapahtui virhe: %s", error)

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
        self.layer_features = self.get_all_features()

        self.validation_label.setText("Kaavan validointivirheet:")
        self.validation_label.setStyleSheet("")

        # Clear the existing errors from the list view
        self.validation_result_tree_view.clear_errors()

        active_plan_id = get_active_plan_id()
        if not active_plan_id:
            iface.messageBar().pushMessage("Virhe", "Ei aktiivista kaavaa.", level=3)
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
            iface.messageBar().pushMessage("Virhe", "Ei aktiivista kaavaa-asiaa.", level=3)
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

        for error_data in validation_json.values():
            if not isinstance(error_data, dict):
                continue

            errors = error_data.get("errors") or []
            for error in errors:
                self.validation_result_tree_view.add_error(
                    error.get("ruleId", ""),
                    error.get("instance", ""),
                    error.get("message", ""),
                    error.get("classKey", ""),
                    self.layer_features,
                )

            warnings = error_data.get("warnings") or []
            for warning in warnings:
                self.validation_result_tree_view.add_warning(
                    warning.get("ruleId", ""),
                    warning.get("instance", ""),
                    warning.get("message", ""),
                    warning.get("classKey", ""),
                    self.layer_features,
                )
        self.validation_result_tree_view.clicked.connect(self.on_item_clicked)
        self.validation_result_tree_view.doubleClicked.connect(self.on_item_double_clicked)

        # Always enable validation at the end
        self.enable_validation()

    def get_all_features(self) -> dict:
        """Returns all IDs, names and geometries."""
        result: dict[str, list] = {}
        project = QgsProject.instance()
        for feature_layer in plan_features_and_regulations:
            layer = project.mapLayersByName(feature_layer.name)[0]
            features = layer.getFeatures()
            for feature in features:
                feature_id = feature["id"]
                name = feature["name"] if "name" in feature.fields().names() else None
                geom = feature.geometry()
                result.setdefault(layer.name(), []).append((feature_id, name, geom))
        return result

    def on_item_clicked(self, index):
        model = self.validation_result_tree_view.model
        clicked_item = model.itemFromIndex(index)
        feature_id = clicked_item.feature_id

        feature_found, _ = self._find_feature(feature_id)
        if feature_found and feature_found.geometry():
            self._zoom_to_feature(feature_found.geometry())

    def on_item_double_clicked(self, index):
        model = self.validation_result_tree_view.model
        clicked_item = model.itemFromIndex(index)
        feature_id = clicked_item.feature_id

        feature_found, layer = self._find_feature(feature_id)

        if feature_found:
            if feature_found.geometry():
                self.plan_manager.edit_plan_feature(feature=feature_found, layer_name=layer.name())
            else:
                if layer.name() == "Kaavamääräys":
                    regulation_feature = PlanRegulationLayer.get_feature_by_id(feature_found["id"])
                    regulation_group_id = regulation_feature["plan_regulation_group_id"]
                elif layer.name() == "Kaavasuositus":
                    proposition_feature = PlanPropositionLayer.get_feature_by_id(feature_found["id"])
                    regulation_group_id = proposition_feature["plan_regulation_group_id"]

                regulation_group_feature = RegulationGroupLayer.get_feature_by_id(regulation_group_id)
                if regulation_group_feature:
                    regulation_group = RegulationGroupLayer.model_from_feature(regulation_group_feature)
                    self.plan_manager.edit_regulation_group(regulation_group)
        else:
            iface.messageBar().pushWarning("", "Kohdetta ei löytynyt.")

    def _find_feature(self, feature_id: str | None) -> tuple[QgsFeature | None, QgsMapLayer | None]:
        if feature_id is None:
            return None, None

        expression = f"\"id\" = '{feature_id}'"
        request = QgsFeatureRequest().setFilterExpression(expression)

        for feature_layer in plan_layers:
            layer = QgsProject.instance().mapLayersByName(feature_layer.name)[0]
            features = layer.getFeatures(request)
            feature = next(features, None)
            if feature:
                return feature, layer

        return None, None

    def _zoom_to_feature(self, geom: QgsGeometry):
        bounding_box = geom.boundingBox()
        canvas = iface.mapCanvas()
        canvas.zoomToFeatureExtent(bounding_box.buffered(1000))
        canvas.flashGeometries(geometries=[geom], crs=QgsCoordinateReferenceSystem("EPSG:3067"))
        canvas.redrawAllLayers()
