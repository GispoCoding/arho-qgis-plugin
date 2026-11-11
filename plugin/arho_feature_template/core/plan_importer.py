from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from qgis.PyQt.QtCore import QByteArray, QObject, pyqtSignal
from qgis.PyQt.QtWidgets import QMessageBox

from arho_feature_template.core.lambda_client import LambdaClient
from arho_feature_template.utils.network_utils import prepare_presigned_request, presigned_reply_error

if TYPE_CHECKING:
    from qgis.PyQt.QtNetwork import QNetworkReply

logger = logging.getLogger(__name__)


class PlanImporter(QObject):
    """State machine for the plan import chain.

    The chain is: get_upload_url -> HTTP PUT to the presigned URL -> import_plan with the S3 key.
    """

    plan_imported = pyqtSignal(str)
    plan_import_failed = pyqtSignal(str)

    def __init__(self, client: LambdaClient, parent: QObject | None = None):
        super().__init__(parent)
        self._client = client
        # Context of the in-flight import chain; None when no import is running
        self._pending_import: dict[str, Any] | None = None
        # (plan_json, s3_key) of the last upload, so a force-retry can reuse the key without re-uploading
        self._cached_upload: tuple[str, str] | None = None

    def import_plan(self, plan_json: str, extra_data: dict, force: bool = False):  # noqa: FBT001, FBT002
        """Imports a plan by uploading it to S3 with a presigned URL and then calling the import action."""
        logger.debug("Importing plan force=%s extra_data_keys=%s", force, list(extra_data.keys()))
        self._pending_import = {"plan_json": plan_json, "extra_data": extra_data, "force": force}

        if self._cached_upload and self._cached_upload[0] == plan_json:
            # The same plan file was already uploaded (e.g. force-retry after "Plan already exists.");
            # the backend does not delete the file on import, so the key can be reused
            logger.debug("Reusing already uploaded plan file s3_key=%s", self._cached_upload[1])
            self._send_import_plan_request(self._cached_upload[1])
            return

        self._cached_upload = None
        self._client.post_action(action=LambdaClient.ACTION_GET_UPLOAD_URL)

    def handle_upload_url_response(self, response_body: dict):
        """Processes the presigned upload URL reply and uploads the plan file to S3."""
        if self._pending_import is None:
            logger.debug("Received upload URL but no import is pending, ignoring")
            return
        details = response_body.get("details") or {}
        upload_url = details.get("upload_url")
        s3_key = details.get("key")
        if not upload_url or not s3_key:
            logger.debug("Upload URL response missing url or key, details_keys=%s", list(details.keys()))
            self._pending_import = None
            self.plan_import_failed.emit(
                "error: Taustapalvelu ei palauttanut latausosoitetta. "
                "Taustapalvelua ei ehkä ole vielä päivitetty tukemaan tätä lisäosan versiota."
            )
            return

        logger.debug("Uploading plan file to S3 s3_key=%s", s3_key)
        self._pending_import["s3_key"] = s3_key
        request = prepare_presigned_request(upload_url)
        request.setAttribute(LambdaClient.ActionAttribute, LambdaClient.S3_UPLOAD_PLAN)
        body = QByteArray(self._pending_import["plan_json"].encode("utf-8"))
        self._client.put(request, body)

    def handle_upload_url_error(self, error: str):
        logger.debug("Getting upload URL failed error=%s", error)
        self._pending_import = None
        self.plan_import_failed.emit(
            f"error: {error} (Taustapalvelua ei ehkä ole vielä päivitetty tukemaan tätä lisäosan versiota.)"
        )

    def handle_s3_upload_reply(self, response: QNetworkReply):
        """Processes the S3 upload reply and sends the actual import request."""
        try:
            if self._pending_import is None:
                logger.debug("Plan file uploaded but no import is pending, ignoring")
                return
            error = presigned_reply_error(response)
            if error is not None:
                logger.debug("Plan file upload failed error=%s", error)
                self._cached_upload = None
                QMessageBox.critical(None, "API Virhe", f"Kaavatiedoston siirto epäonnistui: {error}")
                self.handle_import_error(error)
                return
        finally:
            response.deleteLater()

        s3_key = self._pending_import["s3_key"]
        logger.debug("Plan file uploaded s3_key=%s", s3_key)
        self._cached_upload = (self._pending_import["plan_json"], s3_key)
        self._send_import_plan_request(s3_key)

    def handle_import_response(self, response_body: dict):
        title = response_body.get("title")
        logger.debug("Processing import plan response title=%s", title)
        if title == "Plan imported.":
            self._pending_import = None
            self._cached_upload = None
            details = response_body.get("details") or {}
            plan_id = details.get("plan_id")
            logger.debug("Plan import succeeded plan_id=%s", plan_id)
            self.plan_imported.emit(plan_id)
        else:
            self.handle_import_error(str(response_body))

    def handle_import_error(self, error: str):
        logger.debug("Plan import failed error=%s", error)
        self._pending_import = None
        if "Plan already exists." not in error:
            # Keep the uploaded file cached only for the force-retry of an existing plan
            self._cached_upload = None
        self.plan_import_failed.emit(f"error: {error}")

    def _send_import_plan_request(self, s3_key: str):
        if self._pending_import is None:
            return
        payload: dict[str, Any] = {
            "data": {"s3_key": s3_key, "extra_data": self._pending_import["extra_data"]},
        }
        if self._pending_import["force"]:
            payload["force"] = True

        self._client.post_action(action=LambdaClient.ACTION_IMPORT_PLAN, payload=payload)
