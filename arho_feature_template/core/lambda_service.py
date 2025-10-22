from __future__ import annotations

import json
import re
import uuid
from http import HTTPStatus
from typing import Any, Callable, cast

from qgis.PyQt.QtCore import QByteArray, QObject, QUrl, pyqtSignal
from qgis.PyQt.QtNetwork import QNetworkAccessManager, QNetworkProxy, QNetworkReply, QNetworkRequest
from qgis.PyQt.QtWidgets import QMessageBox
from qgis.utils import iface

from arho_feature_template.core.settings_manager import SettingsManager
from arho_feature_template.utils.misc_utils import get_active_plan_id


class LambdaService(QObject):
    plan_matter_data_received = pyqtSignal(dict)
    plan_data_received = pyqtSignal(dict, dict)
    validation_received = pyqtSignal(dict)
    validation_failed = pyqtSignal(str)
    plan_matter_received = pyqtSignal(dict)
    plan_identifier_received = pyqtSignal(dict)
    plan_imported = pyqtSignal(str)
    plan_import_failed = pyqtSignal(str)

    ActionAttribute = cast(QNetworkRequest.Attribute, QNetworkRequest.User + 1)
    ACTION_VALIDATE_PLANS = "validate_plans"
    ACTION_VALIDATE_PLAN_MATTERS = "validate_plan_matters"
    ACTION_GET_PLANS = "get_plans"
    ACTION_GET_PLAN_MATTERS = "get_plan_matters"
    ACTION_POST_PLAN_MATTERS = "post_plan_matters"
    ACTION_GET_PERMANENT_IDENTIFIERS = "get_permanent_plan_identifiers"
    ACTION_IMPORT_PLAN = "import_plan"

    def __init__(self):
        super().__init__()
        self.network_manager = QNetworkAccessManager()
        self.network_manager.finished.connect(self._handle_response)

    def export_plan(self, plan_id: str):
        self._send_request(action=self.ACTION_GET_PLANS, plan_id=plan_id)

    def export_plan_matter(self, plan_id: str):
        self._send_request(action=self.ACTION_GET_PLAN_MATTERS, plan_id=plan_id)

    def validate_plan(self, plan_id: str):
        self._send_request(action=self.ACTION_VALIDATE_PLANS, plan_id=plan_id)

    def validate_plan_matter(self, plan_id: str):
        self._send_request(action=self.ACTION_VALIDATE_PLAN_MATTERS, plan_id=plan_id)

    def post_plan_matter(self, plan_id: str):
        self._send_request(action=self.ACTION_POST_PLAN_MATTERS, plan_id=plan_id)

    def get_permanent_identifier(self, plan_id: str):
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

        self._send_request(action=self.ACTION_IMPORT_PLAN, payload=payload)

    def _send_request(self, action: str, plan_id: str | None = None, payload: dict | None = None):
        """Sends a request to the lambda function."""
        proxy_host = SettingsManager.get_proxy_host()
        proxy_port = SettingsManager.get_proxy_port()
        self.lambda_url = SettingsManager.get_lambda_url()

        # Initialize or reset proxy each time a request is sent. Incase settings have changed.
        if proxy_host and proxy_port:
            # Set up SOCKS5 Proxy if values are provided
            proxy = QNetworkProxy()
            proxy.setType(QNetworkProxy.Socks5Proxy)
            proxy.setHostName(proxy_host)
            proxy.setPort(int(proxy_port))
            self.network_manager.setProxy(proxy)
        else:
            self.network_manager.setProxy(QNetworkProxy())

        if not payload or plan_id:
            payload = {"plan_uuid": plan_id}
        payload["action"] = action

        payload_bytes = QByteArray(json.dumps(payload, ensure_ascii=False).encode("utf-8"))
        request = QNetworkRequest(QUrl(self.lambda_url))
        request.setAttribute(LambdaService.ActionAttribute, action)
        request.setHeader(QNetworkRequest.ContentTypeHeader, "application/json")
        self.network_manager.post(request, payload_bytes)

    def _is_api_gateway_request(self) -> bool:
        """Determines if the lambda request is going through the API Gateway."""
        match = re.match(r"^https://.*execute-api.*amazonaws\.com.*$", self.lambda_url)
        return bool(match)

    def _get_response_handler(self, action: str) -> Callable[[dict], None]:
        handlers = {
            self.ACTION_GET_PLANS: self._process_export_plan_response,
            self.ACTION_GET_PLAN_MATTERS: self._process_export_plan_matter_response,
            self.ACTION_IMPORT_PLAN: self._process_import_plan_response,
            self.ACTION_VALIDATE_PLANS: self._process_validation_response,
            self.ACTION_VALIDATE_PLAN_MATTERS: self._process_validation_response,
            self.ACTION_POST_PLAN_MATTERS: self._process_plan_matter_response,
            self.ACTION_GET_PERMANENT_IDENTIFIERS: self._process_identifier_response,
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
        }
        return handlers[action]

    def _handle_response(self, response: QNetworkReply):
        action = response.request().attribute(LambdaService.ActionAttribute)
        response_handler = self._get_response_handler(action)
        error_handler = self._get_error_handler(action)
        if response.error() != QNetworkReply.NoError:  # type: ignore  # wrong type annotation in the stubs
            error = response.errorString()
            QMessageBox.critical(None, "API Virhe", f"Lambda kutsu epäonnistui: {error}")
            error_handler(error)
            response.deleteLater()
            return

        try:
            response_json = response.readAll().data().decode("utf-8")
            response_data = json.loads(response_json)

            if not self._is_api_gateway_request():
                # If calling the lambda directly, the response includes status code and body
                if int(response_data.get("statusCode", 0)) != HTTPStatus.OK:
                    error = response_data["body"] if "body" in response_data else response_data["errorMessage"]
                    QMessageBox.critical(None, "API Virhe", f"Lambda kutsu epäonnistui: {error}")
                    error_handler(error)
                    response.deleteLater()
                    return
                response_body = response_data["body"]
            else:
                response_body = response_data

        except (json.JSONDecodeError, KeyError) as e:
            QMessageBox.critical(None, "JSON Virhe", f"Vastauksen JSON-tiedoston jäsennys epäonnistui: {e}")
            error_handler(str(e))
            return
        finally:
            response.deleteLater()
        response_handler(response_body)

    def _handle_validation_error(self, error: str):
        self.validation_failed.emit(error)

    def _process_plan_matter_response(self, response_body: dict):
        """Processes the post plan matter reply from the lambda and emits a signal."""
        ryhti_responses = response_body.get("ryhti_responses")

        self.plan_matter_received.emit(ryhti_responses)

    def _process_identifier_response(self, response_body: dict):
        """Process the identifier reply and update project variable for the active plan."""
        ryhti_responses = response_body.get("ryhti_responses", {})

        plan_id = get_active_plan_id()

        value = ryhti_responses.get(plan_id)

        if value and value.get("status") == HTTPStatus.OK:
            identifier = value.get("detail")
            iface.messageBar().pushSuccess(
                "Success", f"Pysyvän kaavatunnuksen haku onnistui kaavasuunnitelman {plan_id} kaava-asialle."
            )
            self.plan_identifier_received.emit({"plan_id": plan_id, "status": "success", "identifier": identifier})
        else:
            iface.messageBar().pushWarning(
                "Virhe",
                f"Pysyvän kaavatunnuksen haku epäonnistui kaavasuunnitelmalla {plan_id} kaava-asialle statuksella {value.get('status') if value else 'N/A'}.",
            )
            # self.plan_identifiers_received.emit({"plan_id": plan_id, "status": "failure"})

    def _process_validation_response(self, response_body: dict):
        """Processes the validation reply from the lambda and emits a signal."""
        validation_errors = response_body["ryhti_responses"]
        plan_id = get_active_plan_id()

        validation_errors_of_active_plan = validation_errors.get(plan_id)
        if not validation_errors_of_active_plan:
            self.validation_failed.emit(f"Arhovirhe - Lambdavastaus ei odotetun muotoinen: {validation_errors}")
            return

        SERVER_ERROR_MIN_STATUS = 500  # noqa: N806
        SERVER_ERROR_MAX_STATUS = 599  # noqa: N806
        if (
            status := validation_errors_of_active_plan.get("status")
        ) and SERVER_ERROR_MIN_STATUS <= status <= SERVER_ERROR_MAX_STATUS:
            self.validation_failed.emit(f"Ryhtivirhe: {validation_errors_of_active_plan}")
            return

        self.validation_received.emit(validation_errors)

    def _process_export_plan_response(self, response_body: dict):
        """Processes the reply from the lambda and emits signal."""
        plan_id = get_active_plan_id()

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

    def _process_export_plan_matter_response(self, response_body: dict):
        """Processes the reply from the lambda and emits signal."""
        plan_id = get_active_plan_id()

        details = response_body.get("details", {})

        # Extract the plan matter data for the given plan_id
        plan_matter = details.get(plan_id, {})
        if not isinstance(plan_matter, dict):
            plan_matter = {}

        # Emit the signal with the JSON
        self.plan_matter_data_received.emit(plan_matter)

    def _process_import_plan_response(self, response_body: dict):
        title = response_body.get("title")
        if title == "Plan imported.":
            details = response_body.get("details") or {}
            plan_id = details.get("plan_id")
            self.plan_imported.emit(plan_id)
        else:
            self._handle_import_error(str(response_body))

    def _handle_import_error(self, error: str):
        self.plan_import_failed.emit(f"error: {error}")
