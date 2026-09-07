from __future__ import annotations

import gzip
import json
import logging
from http import HTTPStatus
from typing import TYPE_CHECKING, Any, Callable

from qgis.PyQt.QtCore import QDate, QObject, pyqtSignal
from qgis.PyQt.QtWidgets import QMessageBox
from qgis.utils import iface

from arho_feature_template.core.lambda_client import LambdaClient
from arho_feature_template.core.plan_importer import PlanImporter
from arho_feature_template.utils.misc_utils import get_active_plan_id
from arho_feature_template.utils.network_utils import prepare_presigned_request, presigned_reply_error

if TYPE_CHECKING:
    from qgis.PyQt.QtNetwork import QNetworkReply

    from arho_feature_template.gui.dialogs.new_plan_dialog import UnderAppealScopeOption


logger = logging.getLogger(__name__)


class LambdaService(QObject):
    plan_matter_data_received = pyqtSignal(dict)
    plan_data_received = pyqtSignal(dict, dict)
    validation_received = pyqtSignal(dict)
    validation_failed = pyqtSignal(str)
    plan_matter_received = pyqtSignal(dict)
    plan_identifier_received = pyqtSignal(dict)
    plan_imported = pyqtSignal(str)
    plan_import_failed = pyqtSignal(str)
    plan_copied = pyqtSignal(str)
    plan_copy_failed = pyqtSignal(str)

    # Aliases so existing callers and tests keep working against the facade
    ActionAttribute = LambdaClient.ActionAttribute
    ACTION_VALIDATE_PLAN = LambdaClient.ACTION_VALIDATE_PLAN
    ACTION_VALIDATE_PLAN_MATTERS = LambdaClient.ACTION_VALIDATE_PLAN_MATTERS
    ACTION_GET_PLAN = LambdaClient.ACTION_GET_PLAN
    ACTION_GET_PLAN_MATTERS = LambdaClient.ACTION_GET_PLAN_MATTERS
    ACTION_POST_PLAN_MATTERS = LambdaClient.ACTION_POST_PLAN_MATTERS
    ACTION_GET_PERMANENT_IDENTIFIER = LambdaClient.ACTION_GET_PERMANENT_IDENTIFIER
    ACTION_IMPORT_PLAN = LambdaClient.ACTION_IMPORT_PLAN
    ACTION_COPY_PLAN = LambdaClient.ACTION_COPY_PLAN
    ACTION_GET_UPLOAD_URL = LambdaClient.ACTION_GET_UPLOAD_URL
    S3_DOWNLOAD_PLAN = LambdaClient.S3_DOWNLOAD_PLAN
    S3_UPLOAD_PLAN = LambdaClient.S3_UPLOAD_PLAN

    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)
        self._client = LambdaClient(self)
        self._importer = PlanImporter(self._client, self)
        self._client.response_received.connect(self._on_response)
        self._client.request_failed.connect(self._on_request_failed)
        self._client.parse_failed.connect(self._on_parse_failed)
        self._client.s3_reply_received.connect(self._on_s3_reply)
        self._importer.plan_imported.connect(self.plan_imported)
        self._importer.plan_import_failed.connect(self.plan_import_failed)
        logger.debug("LambdaService initialized")

    def abort_pending(self) -> int:
        """Cancels every request still in flight. See `LambdaClient.abort_pending`."""
        return self._client.abort_pending()

    def export_plan(self, plan_id: str):
        logger.debug("Requesting plan export plan_id=%s", plan_id)
        self._client.post_action(action=self.ACTION_GET_PLAN, plan_id=plan_id)

    def export_plan_matter(self, plan_id: str):
        logger.debug("Requesting plan matter export plan_id=%s", plan_id)
        self._client.post_action(action=self.ACTION_GET_PLAN_MATTERS, plan_id=plan_id)

    def validate_plan(self, plan_id: str):
        logger.debug("Requesting plan validation plan_id=%s", plan_id)
        self._client.post_action(action=self.ACTION_VALIDATE_PLAN, plan_id=plan_id)

    def validate_plan_matter(self, plan_id: str):
        logger.debug("Requesting plan matter validation plan_id=%s", plan_id)
        self._client.post_action(action=self.ACTION_VALIDATE_PLAN_MATTERS, plan_id=plan_id)

    def post_plan_matter(self, plan_id: str):
        logger.debug("Posting plan matter plan_id=%s", plan_id)
        self._client.post_action(action=self.ACTION_POST_PLAN_MATTERS, plan_id=plan_id)

    def get_permanent_identifier(self, plan_id: str):
        logger.debug("Requesting permanent identifier plan_id=%s", plan_id)
        self._client.post_action(action=self.ACTION_GET_PERMANENT_IDENTIFIER, plan_id=plan_id)

    def import_plan(self, plan_json: str, extra_data: dict, force: bool = False):  # noqa: FBT001, FBT002
        """Imports a plan by uploading it to S3 with a presigned URL and then calling the import action.

        The chain is: get_upload_url -> HTTP PUT to the presigned URL -> import_plan with the S3 key.
        """
        self._importer.import_plan(plan_json, extra_data, force)

    def copy_plan(
        self,
        plan_id: str,
        lifecycle_status_id: str | None,
        plan_name: str,
        under_appeal_scope: UnderAppealScopeOption | None,
        keep_under_appeal_lifecycle: bool | None,
        deep_copy: bool,  # noqa: FBT001
        period_of_validity_start: QDate | None,
        approval_date: QDate | None,
        lock: bool,  # noqa: FBT001
    ):
        payload: dict[str, Any] = {
            "plan_uuid": plan_id,
            "data": {
                "plan_name": {"fin": plan_name},
            },
        }
        if lifecycle_status_id:
            payload["data"]["lifecycle_status_id"] = lifecycle_status_id
        if under_appeal_scope:
            payload["data"]["under_appeal_scope"] = under_appeal_scope.value
        if keep_under_appeal_lifecycle:
            payload["data"]["keep_under_appeal_lifecycle"] = keep_under_appeal_lifecycle
        if period_of_validity_start:  # pyright: ignore[reportGeneralTypeIssues]
            payload["data"]["period_of_validity_start"] = period_of_validity_start.toPyDate().isoformat()
        if approval_date:  # pyright: ignore[reportGeneralTypeIssues]
            payload["data"]["approval_date"] = approval_date.toPyDate().isoformat()
        if deep_copy:
            payload["data"]["deep_copy"] = deep_copy
        payload["data"]["lock"] = lock

        logger.debug(
            "Copying plan source_plan_id=%s lifecycle_status_id=%s under_appeal_scope=%s has_period_start=%s has_approval_date=%s",
            plan_id,
            lifecycle_status_id,
            under_appeal_scope,
            bool(period_of_validity_start),
            bool(approval_date),
        )

        self._client.post_action(action=self.ACTION_COPY_PLAN, payload=payload)

    def _get_response_handler(self, action: str) -> Callable[[dict], None]:
        handlers = {
            self.ACTION_GET_PLAN: self._process_export_plan_response,
            self.ACTION_GET_UPLOAD_URL: self._importer.handle_upload_url_response,
            self.ACTION_GET_PLAN_MATTERS: self._process_export_plan_matter_response,
            self.ACTION_IMPORT_PLAN: self._importer.handle_import_response,
            self.ACTION_VALIDATE_PLAN: self._process_validation_response,
            self.ACTION_VALIDATE_PLAN_MATTERS: self._process_validation_response,
            self.ACTION_POST_PLAN_MATTERS: self._process_plan_matter_response,
            self.ACTION_GET_PERMANENT_IDENTIFIER: self._process_identifier_response,
            self.ACTION_COPY_PLAN: self._process_copy_plan_response,
        }
        return handlers[action]

    def _get_error_handler(self, action: str) -> Callable[[str], None]:
        handlers = {
            self.ACTION_GET_PLAN: lambda x: None,  # noqa: ARG005
            self.ACTION_GET_UPLOAD_URL: self._importer.handle_upload_url_error,
            self.ACTION_GET_PLAN_MATTERS: lambda x: None,  # noqa: ARG005
            self.ACTION_IMPORT_PLAN: self._importer.handle_import_error,
            self.ACTION_VALIDATE_PLAN: self._handle_validation_error,
            self.ACTION_VALIDATE_PLAN_MATTERS: self._handle_validation_error,
            self.ACTION_POST_PLAN_MATTERS: lambda x: None,  # noqa: ARG005
            self.ACTION_GET_PERMANENT_IDENTIFIER: lambda x: None,  # noqa: ARG005
            self.ACTION_COPY_PLAN: self._handle_copy_error,
        }
        return handlers[action]

    def _on_response(self, action: str, response_body: dict):
        logger.debug("Dispatching response handler for action=%s", action)
        self._get_response_handler(action)(response_body)

    def _on_request_failed(self, action: str, error: str):
        QMessageBox.critical(None, "API Virhe", f"Lambda kutsu epäonnistui: {error}")
        self._get_error_handler(action)(error)

    def _on_parse_failed(self, action: str, error: str):
        QMessageBox.critical(None, "JSON Virhe", f"Vastauksen JSON-tiedoston jäsennys epäonnistui: {error}")
        self._get_error_handler(action)(error)

    def _on_s3_reply(self, tag: str, response: QNetworkReply):
        if tag == self.S3_DOWNLOAD_PLAN:
            self._handle_s3_download_response(response)
        elif tag == self.S3_UPLOAD_PLAN:
            self._importer.handle_s3_upload_reply(response)

    def _handle_validation_error(self, error: str):
        logger.debug("Validation request failed error=%s", error)
        self.validation_failed.emit(error)

    def _process_plan_matter_response(self, response_body: dict):
        """Processes the post plan matter reply from the lambda and emits a signal."""
        ryhti_responses = response_body.get("ryhti_responses")
        logger.debug("Processed plan matter post response keys=%s", list(response_body.keys()))

        self.plan_matter_received.emit(ryhti_responses)

    def _process_identifier_response(self, response_body: dict):
        """Process the identifier reply and update project variable for the active plan.

        `details` holds the identifier string on success, or a Finnish error message when
        the Ryhti API refused. `ryhti_response` is null when the plan matter already had
        a permanent identifier.
        """
        plan_id = get_active_plan_id()
        ryhti_response = response_body.get("ryhti_response")
        details = response_body.get("details")
        status = ryhti_response.get("status") if isinstance(ryhti_response, dict) else None

        if (ryhti_response is None or status == HTTPStatus.OK) and isinstance(details, str) and details:
            logger.debug("Permanent identifier fetch succeeded plan_id=%s", plan_id)
            iface.messageBar().pushSuccess(
                "Success", f"Pysyvän kaavatunnuksen haku onnistui kaavasuunnitelman {plan_id} kaava-asialle."
            )
            self.plan_identifier_received.emit({"plan_id": plan_id, "status": "success", "identifier": details})
        else:
            logger.debug("Permanent identifier fetch failed plan_id=%s status=%s", plan_id, status)
            message = (
                details
                if isinstance(details, str) and details
                else (
                    f"Pysyvän kaavatunnuksen haku epäonnistui kaavasuunnitelmalla {plan_id} kaava-asialle "
                    f"statuksella {status if status is not None else 'N/A'}."
                )
            )
            iface.messageBar().pushWarning("Virhe", message)

    def _process_validation_response(self, response_body: dict):
        """Processes the validation reply from the lambda and emits a signal."""
        ryhti_response = response_body.get("ryhti_response")
        if not isinstance(ryhti_response, dict):
            logger.debug("Validation response missing ryhti_response object")
            self.validation_failed.emit(f"Arhovirhe - Lambdavastaus ei odotetun muotoinen: {response_body}")
            return

        SERVER_ERROR_MIN_STATUS = 500  # noqa: N806
        SERVER_ERROR_MAX_STATUS = 599  # noqa: N806
        status = ryhti_response.get("status")
        if status is not None and SERVER_ERROR_MIN_STATUS <= status <= SERVER_ERROR_MAX_STATUS:
            logger.debug("Validation response indicates server error status=%s", status)
            self.validation_failed.emit(f"Ryhtivirhe: {ryhti_response}")
            return

        logger.debug("Validation response accepted status=%s", status)
        self.validation_received.emit(ryhti_response)

    def _process_export_plan_response(self, response_body: dict):
        """Processes the reply from the lambda and starts the download of the exported plans."""
        details = response_body.get("details", {})
        download_url = details.get("download_url") if isinstance(details, dict) else None
        if not download_url:
            # An old backend returns the plans inline keyed by plan id -> version mismatch
            logger.debug(
                "Plan export response has no download_url, details_keys=%s",
                list(details.keys()) if isinstance(details, dict) else type(details),
            )
            QMessageBox.critical(
                None,
                "API Virhe",
                "Taustapalvelun vastaus oli odottamattomassa muodossa. Taustapalvelua ei ehkä ole vielä "
                "päivitetty tukemaan tätä lisäosan versiota, tai lisäosa pitää päivittää.",
            )
            return

        logger.debug("Plan export response received, downloading exported plans")
        request = prepare_presigned_request(download_url)
        request.setAttribute(LambdaService.ActionAttribute, self.S3_DOWNLOAD_PLAN)
        self._client.get(request)

    def _handle_s3_download_response(self, response: QNetworkReply):
        """Processes the downloaded plan file from S3 and emits signal."""
        try:
            error = presigned_reply_error(response)
            if error is not None:
                logger.debug("Exported plan download failed error=%s", error)
                QMessageBox.critical(None, "API Virhe", f"Kaavan lataus epäonnistui: {error}")
                return
            response_bytes = response.readAll().data()
            # Qt decompresses the gzipped object transparently; decompress manually just in case it did not
            if response_bytes[:2] == b"\x1f\x8b":
                response_bytes = gzip.decompress(response_bytes)
            try:
                plan_data = json.loads(response_bytes.decode("utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                logger.debug("Failed to parse downloaded plan file error=%s", e)
                QMessageBox.critical(None, "JSON Virhe", f"Vastauksen JSON-tiedoston jäsennys epäonnistui: {e}")
                return
        finally:
            response.deleteLater()

        # The downloaded file is a single bare plan JSON
        if not isinstance(plan_data, dict):
            plan_data = {}
        logger.debug("Processing downloaded plan export data")

        outline_data = {}
        if plan_data:
            geographical_area = plan_data.get("geographicalArea")
            if geographical_area:
                outline_data = {
                    "srid": geographical_area.get("srid"),
                    "geometry": geographical_area.get("geometry"),
                }

        self.plan_data_received.emit(plan_data, outline_data)
        logger.debug(
            "Emitted plan export data plan_data_keys=%s outline_keys=%s",
            list(plan_data.keys()),
            list(outline_data.keys()),
        )

    def _process_export_plan_matter_response(self, response_body: dict):
        """Processes the reply from the lambda and emits signal."""
        plan_id = get_active_plan_id()
        logger.debug("Processing plan matter export response for plan_id=%s", plan_id)

        details = response_body.get("details", {})

        # Extract the plan matter data for the given plan_id
        plan_matter = details.get(plan_id, {})
        if not isinstance(plan_matter, dict):
            plan_matter = {}

        # Emit the signal with the JSON
        self.plan_matter_data_received.emit(plan_matter)
        logger.debug("Emitted plan matter export data keys=%s", list(plan_matter.keys()))

    def _process_copy_plan_response(self, response_body: dict):
        title = response_body.get("title")
        logger.debug("Processing copy plan response title=%s", title)
        if title == "Plan copied.":
            details = response_body.get("details") or {}
            plan_id = details.get("copied_plan_id")
            logger.debug("Plan copy succeeded copied_plan_id=%s", plan_id)
            self.plan_copied.emit(plan_id)
        else:
            self._handle_copy_error(str(response_body))

    def _handle_copy_error(self, error: str):
        logger.debug("Plan copy failed error=%s", error)
        self.plan_copy_failed.emit(f"error: {error}")
