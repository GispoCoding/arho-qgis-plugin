from __future__ import annotations

import base64
import gzip
import json
import logging
from http import HTTPStatus
from typing import Any, cast

from qgis.PyQt.QtCore import QByteArray, QObject, QUrl, pyqtSignal
from qgis.PyQt.QtNetwork import QNetworkAccessManager, QNetworkProxy, QNetworkReply, QNetworkRequest

from arho_feature_template.core.settings_manager import SettingsManager
from arho_feature_template.utils.network_utils import is_api_gateway_url

logger = logging.getLogger(__name__)


class LambdaClient(QObject):
    """Owns the network manager: proxy config, the lambda request/response envelope and raw presigned S3 transfers.

    Decoded lambda response bodies are emitted through ``response_received``; transport and
    envelope errors through ``request_failed`` / ``parse_failed``. Replies to presigned S3
    requests are not lambda envelopes and are passed through raw via ``s3_reply_received`` —
    the receiver owns the reply and must call ``deleteLater()`` on it.
    """

    # On PyQt5 QNetworkRequest.Attribute.User is an int, but on PyQt6 it is an Enum.
    _USER_ATTR = cast(int, getattr(QNetworkRequest.Attribute.User, "value", QNetworkRequest.Attribute.User))
    ActionAttribute = QNetworkRequest.Attribute(_USER_ATTR + 1)
    ACTION_VALIDATE_PLAN = "validate_plan"
    ACTION_VALIDATE_PLAN_MATTERS = "validate_plan_matters"
    ACTION_GET_PLAN = "get_plan"
    ACTION_GET_PLAN_MATTERS = "get_plan_matters"
    ACTION_POST_PLAN_MATTERS = "post_plan_matters"
    ACTION_GET_PERMANENT_IDENTIFIER = "get_permanent_plan_identifier"
    ACTION_IMPORT_PLAN = "import_plan"
    ACTION_COPY_PLAN = "copy_plan"
    ACTION_GET_UPLOAD_URL = "get_upload_url"
    # Pseudo-actions tagging presigned S3 requests; never sent to the lambda
    S3_DOWNLOAD_PLAN = "s3_download_plan"
    S3_UPLOAD_PLAN = "s3_upload_plan"
    _RAW_S3_ACTIONS = frozenset({S3_DOWNLOAD_PLAN, S3_UPLOAD_PLAN})

    response_received = pyqtSignal(str, dict)  # (action, decoded response body)
    request_failed = pyqtSignal(str, str)  # (action, error) network error or non-OK lambda status
    parse_failed = pyqtSignal(str, str)  # (action, error) response could not be decoded
    # (tag, reply) — typed as object so test doubles can pass through the signal
    s3_reply_received = pyqtSignal(str, object)

    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)
        self.network_manager = QNetworkAccessManager(self)
        self.network_manager.finished.connect(self._handle_response)
        logger.debug("LambdaClient initialized and network response handler connected")

    def abort_pending(self) -> int:
        """Cancels every reply still in flight without running the response handlers.

        Call this when the owner of the client goes away before the answer arrives.
        `QNetworkReply.abort` emits `QNetworkAccessManager.finished` synchronously, so the
        handler is disconnected first and reconnected afterwards: otherwise the cancelled
        reply would raise an error box on a dialog that is already closing. The client
        stays usable, so a dock can cancel one request and go on to make another.
        """
        replies = self.network_manager.findChildren(QNetworkReply)
        if not replies:
            return 0
        self.network_manager.finished.disconnect(self._handle_response)
        try:
            for reply in replies:
                reply.abort()
                reply.deleteLater()
        finally:
            self.network_manager.finished.connect(self._handle_response)
        logger.debug("Aborted in-flight replies count=%s", len(replies))
        return len(replies)

    def post_action(self, action: str, plan_id: str | None = None, payload: dict[str, Any] | None = None):
        """Sends a request to the lambda function."""
        lambda_url = SettingsManager.get_lambda_url()
        logger.debug("Preparing lambda request action=%s plan_id=%s lambda_url=%s", action, plan_id, lambda_url)
        self._apply_proxy()

        if payload is None:
            payload = {}
        if plan_id:
            payload["plan_uuid"] = plan_id
        payload["action"] = action
        payload["save_json"] = True  # Uncomment for debugging to save the payload and response json in the lambda

        request = QNetworkRequest(QUrl(lambda_url))
        request.setAttribute(LambdaClient.ActionAttribute, action)
        request.setHeader(QNetworkRequest.KnownHeaders.ContentTypeHeader, "application/json")
        if is_api_gateway_url(lambda_url):
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

    def get(self, request: QNetworkRequest):
        self.network_manager.get(request)

    def put(self, request: QNetworkRequest, body: QByteArray):
        self.network_manager.put(request, body)

    def _apply_proxy(self):
        """Initializes or resets the proxy each time a request is sent, in case settings have changed."""
        proxy_host = SettingsManager.get_proxy_host()
        proxy_port = SettingsManager.get_proxy_port()
        if proxy_host and proxy_port:
            # Set up SOCKS5 Proxy if values are provided
            proxy = QNetworkProxy()
            proxy.setType(QNetworkProxy.ProxyType.Socks5Proxy)
            proxy.setHostName(proxy_host)
            proxy.setPort(int(proxy_port))
            self.network_manager.setProxy(proxy)
            logger.debug("Using SOCKS5 proxy host=%s port=%s", proxy_host, proxy_port)
        else:
            self.network_manager.setProxy(QNetworkProxy())
            logger.debug("Using direct connection without proxy")

    @staticmethod
    def _read_error_body(response: QNetworkReply) -> dict | None:
        """Reads and parses the lambda response body of a failed reply, or None.

        Qt delivers the body of HTTP 4xx/5xx replies, but connection-level failures
        have no body. The backend gzips error bodies like success bodies; Qt does not
        decompress them transparently here because the Accept-Encoding header is set
        manually, so sniff the gzip magic bytes.
        """
        try:
            raw = bytes(response.readAll().data())
            if not raw:
                return None
            if raw[:2] == b"\x1f\x8b":
                raw = gzip.decompress(raw)
            body = json.loads(raw.decode("utf-8"))
        except (OSError, json.JSONDecodeError, UnicodeDecodeError):
            return None
        return body if isinstance(body, dict) else None

    @staticmethod
    def _format_error_body(body: dict) -> str:
        """Formats a flat lambda error body ({title, details, ...}) into one message string."""
        title = body.get("title") or ""
        details = body.get("details")
        detail_text = details.get("error", "") if isinstance(details, dict) else (details or "")
        return " ".join(part for part in (str(title), str(detail_text)) if part) or str(body)

    def _handle_response(self, response: QNetworkReply):
        action = response.request().attribute(LambdaClient.ActionAttribute)
        logger.debug("Handling lambda response action=%s", action)
        # Presigned S3 replies are raw HTTP, not lambda response envelopes;
        # the receiver of the signal owns the reply and calls deleteLater() on it
        if action in self._RAW_S3_ACTIONS:
            self.s3_reply_received.emit(action, response)
            return

        if response.error() != QNetworkReply.NetworkError.NoError:  # type: ignore  # wrong type annotation in the stubs
            error = response.errorString()
            # HTTP 4xx/5xx replies carry the lambda error body; prefer its message
            error_body = self._read_error_body(response)
            if error_body is not None:
                error = self._format_error_body(error_body)
            logger.debug("Network error for action=%s error=%s", action, error)
            self.request_failed.emit(action, error)
            response.deleteLater()
            return

        try:
            response_bytes = response.readAll().data()
            if is_api_gateway_url(response.request().url().toString()):
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
                    # Error handlers emit str-typed signals, so format the body into a string
                    body = response_data.get("body")
                    if isinstance(body, dict):
                        error = self._format_error_body(body)
                    else:
                        error = str(body if body is not None else response_data.get("errorMessage"))
                    logger.debug("Non-OK lambda status for action=%s status=%s", action, status_code)
                    self.request_failed.emit(action, error)
                    return
                response_body = response_data["body"]

        except (json.JSONDecodeError, KeyError) as e:
            logger.debug("Failed to parse lambda response action=%s error=%s", action, e)
            self.parse_failed.emit(action, str(e))
            return
        finally:
            response.deleteLater()
        self.response_received.emit(action, response_body)
