from __future__ import annotations

import base64
import gzip
import json
import logging
import re
import uuid
from http import HTTPStatus
from typing import TYPE_CHECKING, Any, Callable, cast

from qgis.PyQt.QtCore import QByteArray, QObject, QUrl, pyqtSignal
from qgis.PyQt.QtNetwork import QNetworkAccessManager, QNetworkProxy, QNetworkReply, QNetworkRequest
from qgis.PyQt.QtWidgets import QMessageBox
from qgis.utils import iface

from arho_feature_template.core.settings_manager import SettingsManager
from arho_feature_template.utils.misc_utils import get_active_plan_id

if TYPE_CHECKING:
    from datetime import date


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

    ActionAttribute = cast(QNetworkRequest.Attribute, QNetworkRequest.User + 1)
    ACTION_VALIDATE_PLANS = "validate_plans"
    ACTION_VALIDATE_PLAN_MATTERS = "validate_plan_matters"
    ACTION_GET_PLANS = "get_plans"
    ACTION_GET_PLAN_MATTERS = "get_plan_matters"
    ACTION_POST_PLAN_MATTERS = "post_plan_matters"
    ACTION_GET_PERMANENT_IDENTIFIERS = "get_permanent_plan_identifiers"
    ACTION_IMPORT_PLAN = "import_plan"
    ACTION_COPY_PLAN = "copy_plan"

    def __init__(self):
        super().__init__()
        self.network_manager = QNetworkAccessManager()
        self.network_manager.finished.connect(self._handle_response)
        logger.debug("LambdaService initialized and network response handler connected")

    def export_plan(self, plan_id: str):
        logger.debug("Requesting plan export plan_id=%s", plan_id)
        self._send_request(action=self.ACTION_GET_PLANS, plan_id=plan_id)

    def export_plan_matter(self, plan_id: str):
        logger.debug("Requesting plan matter export plan_id=%s", plan_id)
        self._send_request(action=self.ACTION_GET_PLAN_MATTERS, plan_id=plan_id)

    def validate_plan(self, plan_id: str):
        logger.debug("Requesting plan validation plan_id=%s", plan_id)
        self._send_request(action=self.ACTION_VALIDATE_PLANS, plan_id=plan_id)

    def validate_plan_matter(self, plan_id: str):
        logger.debug("Requesting plan matter validation plan_id=%s", plan_id)
        self._send_request(action=self.ACTION_VALIDATE_PLAN_MATTERS, plan_id=plan_id)

    def post_plan_matter(self, plan_id: str):
        logger.debug("Posting plan matter plan_id=%s", plan_id)
        self._send_request(action=self.ACTION_POST_PLAN_MATTERS, plan_id=plan_id)

    def get_permanent_identifier(self, plan_id: str):
        logger.debug("Requesting permanent identifier plan_id=%s", plan_id)
        self._send_request(action=self.ACTION_GET_PERMANENT_IDENTIFIERS, plan_id=plan_id)

    def import_plan(self, plan_json: str, extra_data: dict, force: bool = False):  # noqa: FBT001, FBT002
        payload: dict[str, Any] = {
            # For now use a random non existing UUID so backend won't find any existing plan
            # TODO: Change this when backend supports importing without UUID
            "plan_uuid": str(uuid.uuid4()),
            "data": {"plan_json": plan_json, "extra_data": extra_data},
        }
        if force:
            payload["force"] = True

        logger.debug("Importing plan force=%s extra_data_keys=%s", force, list(extra_data.keys()))

        self._send_request(action=self.ACTION_IMPORT_PLAN, payload=payload)

    def copy_plan(
        self,
        plan_id: str,
        lifecycle_status_id: str,
        plan_name: str,
        period_of_validity_start: date | None,
        approval_date: date | None,
    ):
        payload: dict[str, Any] = {
            # For now use a random non existing UUID so backend won't find any existing plan
            # TODO: Change this when backend supports importing without UUID
            "plan_uuid": plan_id,
            "data": {
                "lifecycle_status_uuid": lifecycle_status_id,
                "plan_name": {"fin": plan_name},
            },
        }
        if period_of_validity_start:
            payload["data"]["period_of_validity_start"] = period_of_validity_start.isoformat()
        if approval_date:
            payload["data"]["approval_date"] = approval_date.isoformat()

        logger.debug(
            "Copying plan source_plan_id=%s lifecycle_status_id=%s has_period_start=%s has_approval_date=%s",
            plan_id,
            lifecycle_status_id,
            bool(period_of_validity_start),
            bool(approval_date),
        )

        self._send_request(action=self.ACTION_COPY_PLAN, payload=payload)

    def _send_request(self, action: str, plan_id: str | None = None, payload: dict[str, Any] | None = None):
        """Sends a request to the lambda function."""
        proxy_host = SettingsManager.get_proxy_host()
        proxy_port = SettingsManager.get_proxy_port()
        self.lambda_url = SettingsManager.get_lambda_url()
        logger.debug(
            "Preparing lambda request action=%s plan_id=%s lambda_url=%s proxy_enabled=%s",
            action,
            plan_id,
            self.lambda_url,
            bool(proxy_host and proxy_port),
        )

        # Initialize or reset proxy each time a request is sent. Incase settings have changed.
        if proxy_host and proxy_port:
            # Set up SOCKS5 Proxy if values are provided
            proxy = QNetworkProxy()
            proxy.setType(QNetworkProxy.Socks5Proxy)
            proxy.setHostName(proxy_host)
            proxy.setPort(int(proxy_port))
            self.network_manager.setProxy(proxy)
            logger.debug("Using SOCKS5 proxy host=%s port=%s", proxy_host, proxy_port)
        else:
            self.network_manager.setProxy(QNetworkProxy())
            logger.debug("Using direct connection without proxy")

        if not payload or plan_id:
            payload = {"plan_uuid": plan_id}
        payload["action"] = action

        request = QNetworkRequest(QUrl(self.lambda_url))
        request.setAttribute(LambdaService.ActionAttribute, action)
        request.setHeader(QNetworkRequest.ContentTypeHeader, "application/json")
        if self._is_api_gateway_request():
            request.setRawHeader(b"Accept-Encoding", b"gzip")
            logger.debug("Request marked as API Gateway call, using Accept-Encoding header")
        else:
            # When calling the lambda directly in development environment,
            # we need to set the Accept-Encoding header in the payload
            payload["headers"] = {"Accept-Encoding": "gzip"}
            logger.debug("Request marked as direct lambda call, using payload headers")

        payload_bytes = QByteArray(json.dumps(payload, ensure_ascii=False).encode("utf-8"))
        self.network_manager.post(request, payload_bytes)
        logger.debug("Lambda request sent action=%s payload_size_bytes=%s", action, payload_bytes.size())

    def _is_api_gateway_request(self) -> bool:
        """Determines if the lambda request is going through the API Gateway."""
        match = re.match(r"^https://.*execute-api.*amazonaws\.com.*$", self.lambda_url)
        is_api_gateway = bool(match)
        logger.debug("Lambda URL classified as api_gateway=%s", is_api_gateway)
        return is_api_gateway

    def _get_response_handler(self, action: str) -> Callable[[dict], None]:
        handlers = {
            self.ACTION_GET_PLANS: self._process_export_plan_response,
            self.ACTION_GET_PLAN_MATTERS: self._process_export_plan_matter_response,
            self.ACTION_IMPORT_PLAN: self._process_import_plan_response,
            self.ACTION_VALIDATE_PLANS: self._process_validation_response,
            self.ACTION_VALIDATE_PLAN_MATTERS: self._process_validation_response,
            self.ACTION_POST_PLAN_MATTERS: self._process_plan_matter_response,
            self.ACTION_GET_PERMANENT_IDENTIFIERS: self._process_identifier_response,
            self.ACTION_COPY_PLAN: self._process_copy_plan_response,
        }
        return handlers[action]

    def _get_error_handler(self, action: str) -> Callable[[str], None]:
        handlers = {
            self.ACTION_GET_PLANS: lambda x: None,  # noqa: ARG005
            self.ACTION_GET_PLAN_MATTERS: lambda x: None,  # noqa: ARG005
            self.ACTION_IMPORT_PLAN: self._handle_import_error,
            self.ACTION_VALIDATE_PLANS: self._handle_validation_error,
            self.ACTION_VALIDATE_PLAN_MATTERS: self._handle_validation_error,
            self.ACTION_POST_PLAN_MATTERS: lambda x: None,  # noqa: ARG005
            self.ACTION_GET_PERMANENT_IDENTIFIERS: lambda x: None,  # noqa: ARG005
            self.ACTION_COPY_PLAN: self._handle_copy_error,
        }
        return handlers[action]

    def _handle_response(self, response: QNetworkReply):
        action = response.request().attribute(LambdaService.ActionAttribute)
        logger.debug("Handling lambda response action=%s", action)
        response_handler = self._get_response_handler(action)
        error_handler = self._get_error_handler(action)
        if response.error() != QNetworkReply.NoError:  # type: ignore  # wrong type annotation in the stubs
            error = response.errorString()
            logger.debug("Network error for action=%s error=%s", action, error)
            QMessageBox.critical(None, "API Virhe", f"Lambda kutsu epäonnistui: {error}")
            error_handler(error)
            response.deleteLater()
            return

        try:
            response_bytes = response.readAll().data()
            if self._is_api_gateway_request():
                is_compressed = bytes(response.rawHeader(b"Content-Encoding")).decode("utf-8") == "gzip"
                logger.debug("API Gateway response compressed=%s action=%s", is_compressed, action)
                if is_compressed:
                    decompressed_data = gzip.decompress(response_bytes)
                    response_json = decompressed_data.decode("utf-8")
                else:
                    response_json = response_bytes.decode("utf-8")
                response_body = json.loads(response_json)
            else:
                # In developement environment lambda is called directly without API Gateway
                # and has a different response format
                response_json = response_bytes.decode("utf-8")
                response_data = json.loads(response_json)

                encoding = response_data.get("encoding")
                is_compressed = encoding == "gzip+base64"
                logger.debug("Direct lambda response compressed=%s action=%s", is_compressed, action)
                if is_compressed:
                    compressed_data = base64.b64decode(response_data["body"])
                    decompressed_data = gzip.decompress(compressed_data)
                    response_data["body"] = json.loads(decompressed_data.decode("utf-8"))

                status_code = int(response_data.get("statusCode", 0))
                if status_code != HTTPStatus.OK:
                    error = response_data["body"] if "body" in response_data else response_data["errorMessage"]
                    logger.debug("Non-OK lambda status for action=%s status=%s", action, status_code)
                    QMessageBox.critical(None, "API Virhe", f"Lambda kutsu epäonnistui: {error}")
                    error_handler(error)
                    response.deleteLater()
                    return
                response_body = response_data["body"]

        except (json.JSONDecodeError, KeyError) as e:
            logger.debug("Failed to parse lambda response action=%s error=%s", action, e)
            QMessageBox.critical(None, "JSON Virhe", f"Vastauksen JSON-tiedoston jäsennys epäonnistui: {e}")
            error_handler(str(e))
            return
        finally:
            response.deleteLater()
        logger.debug("Dispatching response handler for action=%s", action)
        response_handler(response_body)

    def _handle_validation_error(self, error: str):
        logger.debug("Validation request failed error=%s", error)
        self.validation_failed.emit(error)

    def _process_plan_matter_response(self, response_body: dict):
        """Processes the post plan matter reply from the lambda and emits a signal."""
        ryhti_responses = response_body.get("ryhti_responses")
        logger.debug("Processed plan matter post response keys=%s", list(response_body.keys()))

        self.plan_matter_received.emit(ryhti_responses)

    def _process_identifier_response(self, response_body: dict):
        """Process the identifier reply and update project variable for the active plan."""
        ryhti_responses = response_body.get("ryhti_responses", {})

        plan_id = get_active_plan_id()

        value = ryhti_responses.get(plan_id)

        if value and value.get("status") == HTTPStatus.OK:
            identifier = value.get("detail")
            logger.debug("Permanent identifier fetch succeeded plan_id=%s", plan_id)
            iface.messageBar().pushSuccess(
                "Success", f"Pysyvän kaavatunnuksen haku onnistui kaavasuunnitelman {plan_id} kaava-asialle."
            )
            self.plan_identifier_received.emit({"plan_id": plan_id, "status": "success", "identifier": identifier})
        else:
            logger.debug(
                "Permanent identifier fetch failed plan_id=%s status=%s",
                plan_id,
                value.get("status") if value else None,
            )
            iface.messageBar().pushWarning(
                "Virhe",
                f"Pysyvän kaavatunnuksen haku epäonnistui kaavasuunnitelmalla {plan_id} kaava-asialle statuksella {value.get('status') if value else 'N/A'}.",
            )
            # self.plan_identifiers_received.emit({"plan_id": plan_id, "status": "failure"})

    def _process_validation_response(self, response_body: dict):
        """Processes the validation reply from the lambda and emits a signal."""
        validation_errors = response_body["ryhti_responses"]
        plan_id = get_active_plan_id()
        logger.debug("Processing validation response for active_plan_id=%s", plan_id)

        validation_errors_of_active_plan = validation_errors.get(plan_id)
        if not validation_errors_of_active_plan:
            logger.debug("Validation response missing active plan entry plan_id=%s", plan_id)
            self.validation_failed.emit(f"Arhovirhe - Lambdavastaus ei odotetun muotoinen: {validation_errors}")
            return

        SERVER_ERROR_MIN_STATUS = 500  # noqa: N806
        SERVER_ERROR_MAX_STATUS = 599  # noqa: N806
        if (
            status := validation_errors_of_active_plan.get("status")
        ) and SERVER_ERROR_MIN_STATUS <= status <= SERVER_ERROR_MAX_STATUS:
            logger.debug("Validation response indicates server error status=%s", status)
            self.validation_failed.emit(f"Ryhtivirhe: {validation_errors_of_active_plan}")
            return

        logger.debug("Validation response accepted for plan_id=%s", plan_id)
        self.validation_received.emit(validation_errors)

    def _process_export_plan_response(self, response_body: dict):
        """Processes the reply from the lambda and emits signal."""
        plan_id = get_active_plan_id()
        logger.debug("Processing plan export response for plan_id=%s", plan_id)

        details = response_body.get("details", {})

        # Extract the plan JSON for the given plan_id
        plan_data = details.get(plan_id, {})
        if not isinstance(plan_data, dict):
            plan_data = {}

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

    def _process_import_plan_response(self, response_body: dict):
        title = response_body.get("title")
        logger.debug("Processing import plan response title=%s", title)
        if title == "Plan imported.":
            details = response_body.get("details") or {}
            plan_id = details.get("plan_id")
            logger.debug("Plan import succeeded plan_id=%s", plan_id)
            self.plan_imported.emit(plan_id)
        else:
            self._handle_import_error(str(response_body))

    def _handle_import_error(self, error: str):
        logger.debug("Plan import failed error=%s", error)
        self.plan_import_failed.emit(f"error: {error}")

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
