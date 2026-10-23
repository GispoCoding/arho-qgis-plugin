from __future__ import annotations

import logging
import re
import uuid
from collections import defaultdict
from importlib import resources
from typing import TYPE_CHECKING

from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsExpressionContextUtils,
    QgsGeometry,
    QgsProject,
    QgsVariantUtils,
)
from qgis.gui import QgsDockWidget
from qgis.PyQt import uic

from arho_feature_template.core.lambda_service import LambdaService
from arho_feature_template.core.settings_manager import SettingsManager
from arho_feature_template.gui.components.lambda_job_status import job_status_text
from arho_feature_template.gui.components.validation_tree_view import ValidationFeatures
from arho_feature_template.project.layers.plan_layers import (
    AdditionalInformationLayer,
    PlanLayer,
    PlanPropositionLayer,
    PlanRegulationLayer,
    RegulationGroupLayer,
    plan_object_layers,
)
from arho_feature_template.utils.misc_utils import get_active_plan_id, iface
from arho_feature_template.utils.timing import timed

if TYPE_CHECKING:
    from qgis.core import QgsFeature
    from qgis.PyQt.QtWidgets import QLabel, QProgressBar, QPushButton

    from arho_feature_template.core.plan_manager import PlanManager
    from arho_feature_template.gui.components.validation_tree_view import ValidationTreeView
    from arho_feature_template.project.layers import AbstractLayer

logger = logging.getLogger(__name__)


def _is_uuid(value: str) -> bool:
    try:
        uuid.UUID(value)
    except (TypeError, ValueError, AttributeError):
        return False
    return True


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
        logger.debug("Initializing ValidationDock")

        self.plan_manager = plan_manager
        self.lambda_service = LambdaService(self)
        self.lambda_service.validation_received.connect(self.list_validation_errors)
        self.lambda_service.validation_failed.connect(self.handle_validation_call_errors)
        self.lambda_service.job_status_changed.connect(self.on_job_status_changed)
        self.lambda_service.busy_changed.connect(self.on_busy_changed)
        self._listing_title = ""
        self.validation_features = ValidationFeatures()
        self.validate_button.clicked.connect(self.validate_plan)
        self.validate_plan_matter_button.clicked.connect(self.validate_plan_matter)

        self.validation_result_tree_view.clicked.connect(self.on_item_clicked)
        self.validation_result_tree_view.doubleClicked.connect(self.on_item_double_clicked)

        if not SettingsManager.get_data_exchange_layer_enabled():
            self.validate_plan_matter_button.hide()
            logger.debug("Data exchange layer disabled, hiding validate plan matter button")

    def unload(self):
        """Cancels a validation still in flight.

        Qt drops the connections when the dock is destroyed, but the reply would still
        reach a `LambdaService` that is being torn down with it.
        """
        logger.debug("Unloading ValidationDock")
        self.lambda_service.abort_pending()

    def handle_validation_call_errors(self, error: str):
        self.validation_label.setText("Validoinnissa tapahtui virhe.")
        self.validation_label.setStyleSheet("QLabel {color: red}")

        logger.warning("Validoinnissa tapahtui virhe: %s", error)

        self.enable_validation()

    def on_finalize_validation_failed(self, ryhti_response: dict):
        """The plan was not made final because it failed the Ryhti validation. Shows the errors."""
        logger.debug("Listing the validation errors that stopped making the plan final")
        self._start_listing("Kaavasuunnitelmaa ei asetettu lopulliseksi. Validointivirheet:")
        self.list_validation_errors(ryhti_response)
        self.setUserVisible(True)
        iface.messageBar().pushWarning(
            "", "Kaavasuunnitelmaa ei asetettu lopulliseksi, koska se ei läpäissyt Ryhti-validointia."
        )

    def on_permanent_identifier_set(self, identifier: str | None):
        """Enable the validate plan matter button when a valid permanent identifier is received."""
        logger.debug("Permanent identifier updated in validation dock is_set=%s", bool(identifier))
        if identifier:
            self.validate_plan_matter_button.setEnabled(True)
            self.validate_plan_matter_button.setToolTip("Lähetä liitteet Ryhtiin ja validoi kaava-asia")
        else:
            self.validate_plan_matter_button.setEnabled(False)
            self.validate_plan_matter_button.setToolTip("Hae ensin pysyvä kaavatunnus")

    def validate_plan(self):
        """Handles the button press to trigger the validation process."""
        logger.debug("Validate plan requested")
        # Get IDs from all layers
        # self.layer_features = self.get_all_features()

        self._start_listing("Kaavasuunnitelman validointivirheet:")

        active_plan_id = get_active_plan_id()
        if not active_plan_id:
            logger.debug("No active plan id, aborting validate_plan")
            iface.messageBar().pushMessage("Virhe", "Ei aktiivista kaavasuunnitelmaa.", level=3)
            return

        # Disable buttons and show progress bar
        self.validate_button.setEnabled(False)
        self.validate_plan_matter_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        logger.debug("Plan validation started for active_plan_id=%s", active_plan_id)

        self.lambda_service.validate_plan(active_plan_id)

    def validate_plan_matter(self):
        """Handles the button press to trigger the plan matter validation process."""
        logger.debug("Validate plan matter requested")

        self._start_listing("Kaava-asian validointivirheet:")

        active_plan_id = get_active_plan_id()
        if not active_plan_id:
            logger.debug("No active plan id, aborting validate_plan_matter")
            iface.messageBar().pushMessage("Virhe", "Ei aktiivista kaavasuunnitelmaa.", level=3)
            return

        # Disable buttons and show progress bar
        self.validate_plan_matter_button.setEnabled(False)
        self.validate_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        logger.debug("Plan matter validation started for active_plan_id=%s", active_plan_id)

        self.lambda_service.validate_plan_matter(active_plan_id)

    def on_job_status_changed(self, _action: str, status: str):
        """Shows after the title whether the validation job is queued or running."""
        self.validation_label.setText(f"{self._listing_title} {job_status_text(status)}")

    def on_busy_changed(self, _action: str, busy: bool):  # noqa: FBT001
        if not busy:
            self.validation_label.setText(self._listing_title)

    def _start_listing(self, title: str):
        """Resets the label and the tree for a new list of validation results."""
        self._listing_title = title
        self.validation_label.setText(title)
        self.validation_label.setStyleSheet("")
        self.validation_result_tree_view.clear_errors()

    def enable_validation(self):
        """Hide progress bar and re-enable the button"""
        logger.debug("Enabling validation controls")
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
        logger.debug("Validation controls updated permanent_identifier_set=%s", bool(permanent_identifier))

        # Ensure the validation results are visible and properly resized
        self.validation_result_tree_view.expandAll()
        self.validation_result_tree_view.resizeColumnToContents(0)

    def list_validation_errors(self, validation_json):
        """Slot for listing validation errors and warnings.

        Receives a single ryhti_response object: {status, detail, errors, warnings}.
        """
        logger.debug("Listing validation errors")

        if not validation_json:
            logger.debug("Validation response JSON missing")
            iface.messageBar().pushMessage("Virhe", "Validaatio json puuttuu.", level=1)
            self.enable_validation()
            return

        errors = validation_json.get("errors") or []
        warnings = validation_json.get("warnings") or []

        # If no errors or warnings, display a message and exit
        if not errors and not warnings:
            logger.debug("Validation response contains no errors or warnings")
            self.validation_label.setText("Ei validointivirheitä tai -varoituksia.")
            self.validation_label.setStyleSheet("QLabel {color: green}")
            self.enable_validation()
            return
        with timed("list_validation_errors", errors=len(errors), warnings=len(warnings)):
            self.load_features(errors + warnings)

            # Sort so that entries with classKey are first
            self.validation_result_tree_view.model.add_results(
                sorted(errors, key=lambda x: "classKey" not in x),
                sorted(warnings, key=lambda x: "classKey" not in x),
                self.validation_features,
            )

        # Always enable validation at the end
        logger.debug("Validation results populated feature_refs=%s", len(self.validation_features.by_id))
        self.enable_validation()

    def on_item_clicked(self, index):
        model = self.validation_result_tree_view.model
        clicked_item = model.itemFromIndex(index)
        feature_id = clicked_item.feature_id
        logger.debug("Validation item clicked feature_id=%s", feature_id)

        if not feature_id:
            return

        feature_found, _ = self.validation_features.get(feature_id)
        if feature_found and feature_found.geometry():
            logger.debug("Zooming to feature from validation click feature_id=%s", feature_id)
            self._zoom_to_feature(feature_found.geometry())

    def on_item_double_clicked(self, index):
        model = self.validation_result_tree_view.model
        clicked_item = model.itemFromIndex(index)
        feature_id = clicked_item.feature_id
        logger.debug("Validation item double-clicked feature_id=%s", feature_id)

        if not feature_id:
            iface.messageBar().pushWarning(
                "Lomakkeen avaaminen epäonnistui", "Kohteen ID puuttuu validointivirheen JSON:sta"
            )
            return

        feature_found, layer = self.validation_features.get(feature_id)

        if feature_found:
            if feature_found.geometry():
                if "plan_type_id" in feature_found.fields().names():
                    logger.debug("Opening plan form from validation item feature_id=%s", feature_id)
                    self.plan_manager.edit_plan()
                else:
                    logger.debug("Opening plan object form from validation item feature_id=%s", feature_id)
                    self.plan_manager.edit_plan_object(feature=feature_found, layer_name=layer.name)
            else:
                regulation_group_feature = self.validation_features.regulation_group(feature_id)
                if regulation_group_feature:
                    logger.debug(
                        "Opening regulation group form from validation item regulation_group_id=%s",
                        regulation_group_feature["id"],
                    )
                    regulation_group = RegulationGroupLayer.model_from_feature(regulation_group_feature)
                    self.plan_manager.edit_regulation_group(regulation_group)
        else:
            iface.messageBar().pushWarning("", "Ei avattavaa lomaketta.")

    def load_features(self, entries: list[dict]):
        """Fetches the features the validation entries point to, with one query per layer.

        Fills `validation_features`.
        A query per entry took minutes for a large result on a remote database.
        """
        self.validation_features = ValidationFeatures()

        ids_by_object_type: dict[str, set[str]] = defaultdict(set)
        for entry in entries:
            key = entry.get("classKey", "")
            object_type = self._object_type(entry.get("instance", ""))
            # classKey is not always a feature id, e.g. lifecycle errors give the lifecycle status code URI
            if object_type and _is_uuid(key):
                ids_by_object_type[object_type].add(key)
        logger.debug("Loading validation features ids=%s", {k: len(v) for k, v in ids_by_object_type.items()})

        self._add_features(PlanLayer, ids_by_object_type["plan"], no_geometries=False)

        missing_ids = set(ids_by_object_type["planobjects"])
        for plan_object_layer in plan_object_layers:
            missing_ids -= self._add_features(plan_object_layer, missing_ids, no_geometries=False).keys()

        propositions = self._add_features(PlanPropositionLayer, ids_by_object_type["planrecommendations"])
        additional_informations = self._add_features(
            AdditionalInformationLayer, ids_by_object_type["additionalinformations"]
        )
        # The regulations of the additional informations are needed only for their regulation group
        regulation_ids_of_informations = {
            feature["plan_regulation_id"]
            for feature in additional_informations.values()
            if not QgsVariantUtils.isNull(feature["plan_regulation_id"])
        }
        regulation_ids = ids_by_object_type["planregulations"]
        regulations = {
            feature["id"]: feature
            for feature in PlanRegulationLayer.get_features_by_attribute_value(
                "id", regulation_ids | regulation_ids_of_informations
            )
        }
        for id_, feature in regulations.items():
            if id_ in regulation_ids:
                self.validation_features.add(id_, feature, PlanRegulationLayer)
                self.validation_features.set_regulation_group_id(id_, feature["plan_regulation_group_id"])
        for id_, feature in propositions.items():
            self.validation_features.set_regulation_group_id(id_, feature["plan_regulation_group_id"])
        for id_, feature in additional_informations.items():
            regulation = regulations.get(feature["plan_regulation_id"])
            if regulation:
                self.validation_features.set_regulation_group_id(id_, regulation["plan_regulation_group_id"])

        self._add_features(
            RegulationGroupLayer,
            ids_by_object_type["planregulationgroups"] | set(self.validation_features.regulation_group_ids.values()),
        )

    @staticmethod
    def _object_type(object_path: str) -> str | None:
        """The type of the object the classKey of a validation entry belongs to.

        classKey is for the last object with square brackets, i.e. planRegulations[1] in
        plan.planRegulationGroups[0].planRegulations[1]. With no square brackets in a path
        that has "plan", the key is of the plan.
        """
        parts = object_path.lower().split(".")
        match = [item for item in parts if re.search(r"\[\d+\]$", item)]
        if match:
            # Remove square brackets and the number within
            return re.sub(r"\[(\d+)\]", "", match[-1])
        return "plan" if "plan" in parts else None

    def _add_features(
        self,
        layer: type[AbstractLayer],
        ids: set[str],
        no_geometries: bool = True,  # noqa: FBT001, FBT002
    ) -> dict[str, QgsFeature]:
        """Adds the features of the layer with the ids to `validation_features` and returns them by id."""
        features = {
            feature["id"]: feature
            for feature in layer.get_features_by_attribute_value("id", ids, no_geometries=no_geometries)
        }
        for id_, feature in features.items():
            self.validation_features.add(id_, feature, layer)
        return features

    def _zoom_to_feature(self, geom: QgsGeometry):
        logger.debug("Zooming and flashing geometry from validation result")
        bounding_box = geom.boundingBox()
        canvas = iface.mapCanvas()
        canvas.zoomToFeatureExtent(bounding_box.buffered(1000))
        canvas.flashGeometries(geometries=[geom], crs=QgsCoordinateReferenceSystem("EPSG:3067"))
        canvas.redrawAllLayers()
