from __future__ import annotations

import json

from qgis.PyQt.QtCore import QByteArray, QObject, QUrl, pyqtSignal
from qgis.PyQt.QtNetwork import QNetworkAccessManager, QNetworkProxy, QNetworkReply, QNetworkRequest
from qgis.PyQt.QtWidgets import QMessageBox

from arho_feature_template.utils.misc_utils import get_active_plan_id, get_plan_name, get_settings


class LambdaService(QObject):
    jsons_received = pyqtSignal(dict, dict)
    validation_received = pyqtSignal(dict)
    ActionAttribute = QNetworkRequest.User + 1
    ACTION_VALIDATE_PLANS = "validate_plans"
    ACTION_GET_PLANS = "get_plans"

    def __init__(self):
        super().__init__()
        self.network_manager = QNetworkAccessManager()
        self.network_manager.finished.connect(self._handle_reply)

    def serialize_plan(self, plan_id: str):
        self._send_request(action=self.ACTION_GET_PLANS, plan_id=plan_id)

    def validate_plan(self, plan_id: str):
        self._send_request(action=self.ACTION_VALIDATE_PLANS, plan_id=plan_id)

    def _send_request(self, action: str, plan_id: str):
        """Sends a request to the lambda function."""
        proxy_host, proxy_port, self.lambda_url = get_settings()

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

        payload = {"action": action, "plan_uuid": plan_id}
        payload_bytes = QByteArray(json.dumps(payload).encode("utf-8"))
        request = QNetworkRequest(QUrl(self.lambda_url))
        request.setAttribute(LambdaService.ActionAttribute, action)
        request.setHeader(QNetworkRequest.ContentTypeHeader, "application/json")
        self.network_manager.post(request, payload_bytes)

    def _handle_reply(self, reply: QNetworkReply):
        action = reply.request().attribute(LambdaService.ActionAttribute)
        if action == self.ACTION_GET_PLANS:
            self._process_json_reply(reply)
        elif action == self.ACTION_VALIDATE_PLANS:
            self._process_validation_reply(reply)

    def _process_validation_reply(self, reply: QNetworkReply):
        """Processes the validation reply from the lambda and emits a signal."""
        if reply.error() != QNetworkReply.NoError:
            error_string = reply.errorString()
            QMessageBox.critical(None, "API Error", f"Lambda call failed: {error_string}")
            reply.deleteLater()
            return

        try:
            response_data = reply.readAll().data().decode("utf-8")
            response_json = json.loads(response_data)

            # Determine if the proxy is set up.
            if hasattr(self, "network_manager") and self.network_manager.proxy().type() == QNetworkProxy.Socks5Proxy:
                # If proxy has been set up, retrieve 'ryhti_responses' directly
                validation_errors = response_json.get("ryhti_responses", {})
            else:
                # If proxy has not been set up (using local docker lambda), the response includes 'body'.
                # In this case we need to retrieve 'ryhti_responses' from 'body' first.
                body = response_json.get("body", {})
                validation_errors = body.get("ryhti_responses", {})

            self.validation_received.emit(validation_errors)

        except json.JSONDecodeError as e:
            QMessageBox.critical(None, "JSON Error", f"Failed to parse response JSON: {e}")
        finally:
            reply.deleteLater()

    def _process_json_reply(self, reply: QNetworkReply):
        """Processes the reply from the lambda and emits signal."""
        plan_id = get_active_plan_id()

        if reply.error() != QNetworkReply.NoError:
            error_string = reply.errorString()
            QMessageBox.critical(None, "API Virhe", f"Lambdan kutsu epäonnistui: {error_string}")
            reply.deleteLater()
            return

        try:
            response_data = reply.readAll().data().decode("utf-8")
            response_json = json.loads(response_data)

            # Determine if the proxy is set up.
            if hasattr(self, "network_manager") and self.network_manager.proxy().type() == QNetworkProxy.Socks5Proxy:
                # If proxy has been set up, retrieve 'details' directly
                details = response_json.get("details", {})
            else:
                # If proxy has not been set up (using local docker lambda), the response includes 'body'.
                # In this case we need to retrieve 'details' from 'body' first.
                body = response_json.get("body", {})
                details = body.get("details", {})

            # Extract the plan JSON for the given plan_id
            plan_json = details.get(plan_id, {})
            if not isinstance(plan_json, dict):
                plan_json = {}

            outline_json = {}
            if plan_json:
                geographical_area = plan_json.get("geographicalArea")
                if geographical_area:
                    outline_name = get_plan_name(plan_id, language="fin")
                    outline_json = {
                        "type": "Feature",
                        "properties": {"name": outline_name},
                        "srid": geographical_area.get("srid"),
                        "geometry": geographical_area.get("geometry"),
                    }

            # Emit the signal with the two JSONs
            self.jsons_received.emit(plan_json, outline_json)

        except json.JSONDecodeError as e:
            QMessageBox.critical(None, "JSON Virhe", f"Failed to parse response JSON: {e}")
        finally:
            reply.deleteLater()
