from __future__ import annotations

import base64
import enum
import gzip
import json
import logging
import time
from dataclasses import dataclass
from http import HTTPStatus
from typing import Any, cast

from qgis.PyQt.QtCore import QByteArray, QObject, QTimer, QUrl, pyqtSignal
from qgis.PyQt.QtNetwork import QNetworkAccessManager, QNetworkProxy, QNetworkReply, QNetworkRequest

from arho_feature_template.core.settings_manager import SettingsManager
from arho_feature_template.utils.network_utils import is_api_gateway_url

logger = logging.getLogger(__name__)

# The API gateway stops a request after 29 s, but the lambda runs up to 900 s. So every action
# is submitted as a job and polled until the job ends.
POLL_INTERVAL_MS = 2000
# The backend job time limit (900 s) plus a margin. Matters only when the polls keep failing.
JOB_DEADLINE_S = 16 * 60
# A poll that hangs counts as a failed poll and is retried
POLL_TIMEOUT_MS = 30000


class JobStatus(enum.StrEnum):
    """The `status` of a `get_job` answer."""

    QUEUED = "queued"
    RUNNING = "running"
    DONE = "done"  # the action ran; `result` holds its answer, which can be an error
    FAILED = "failed"  # no answer: the job crashed, never started or ran past the time limit


JOB_FAILED_MESSAGE = "Taustapalvelun ajo epäonnistui. Yritä uudelleen."
JOB_NOT_STARTED_MESSAGE = "Taustapalvelun ajoa ei voitu käynnistää. Yritä myöhemmin uudelleen."
JOB_DEADLINE_MESSAGE = "Taustapalvelu ei vastannut 16 minuutissa. Toiminto voi silti valmistua taustapalvelussa."
JOB_POLL_FAILED_MESSAGE = "Ajon tilaa ei voitu hakea:"
_JOB_NOT_STARTED_TITLE = "Job could not be started."


@dataclass
class _Answer:
    """One decoded lambda answer: HTTP status, JSON body and whether the action succeeded.

    ``error`` is the transport error text, for answers without a usable body.
    """

    status: int | None
    body: Any
    ok: bool
    error: str = ""


@dataclass
class _Job:
    action: str
    job_id: str
    deadline: float
    timer: QTimer
    status: JobStatus = JobStatus.QUEUED


class LambdaClient(QObject):
    """Owns the network manager: proxy config, the lambda request/response envelope and raw presigned S3 transfers.

    Every action is sent in job mode. A ``202`` answer with ``details.job_id`` starts polling
    ``get_job`` until the job ends; the result of the job is then handled like the direct
    answer of the action. Any other submit answer (an old backend, a bad request) is the
    direct answer.

    Decoded lambda response bodies are emitted through ``response_received``; transport and
    envelope errors through ``request_failed`` / ``parse_failed``. Replies to presigned S3
    requests are not lambda envelopes and are passed through raw via ``s3_reply_received`` —
    the receiver owns the reply and must call ``deleteLater()`` on it.
    """

    # On PyQt5 QNetworkRequest.Attribute.User is an int, but on PyQt6 it is an Enum.
    _USER_ATTR = cast(int, getattr(QNetworkRequest.Attribute.User, "value", QNetworkRequest.Attribute.User))
    ActionAttribute = QNetworkRequest.Attribute(_USER_ATTR + 1)
    JobAttribute = QNetworkRequest.Attribute(_USER_ATTR + 2)  # job_id of a get_job poll
    ACTION_VALIDATE_PLAN = "validate_plan"
    ACTION_VALIDATE_PLAN_MATTERS = "validate_plan_matters"
    ACTION_GET_PLAN = "get_plan"
    ACTION_GET_PLAN_MATTERS = "get_plan_matters"
    ACTION_POST_PLAN_MATTERS = "post_plan_matters"
    ACTION_GET_PERMANENT_IDENTIFIER = "get_permanent_plan_identifier"
    ACTION_IMPORT_PLAN = "import_plan"
    ACTION_COPY_PLAN = "copy_plan"
    ACTION_FINALIZE_PLAN = "finalize_plan"
    ACTION_GET_UPLOAD_URL = "get_upload_url"
    ACTION_GET_JOB = "get_job"
    # Pseudo-actions tagging presigned S3 requests; never sent to the lambda
    S3_DOWNLOAD_PLAN = "s3_download_plan"
    S3_UPLOAD_PLAN = "s3_upload_plan"
    _RAW_S3_ACTIONS = frozenset({S3_DOWNLOAD_PLAN, S3_UPLOAD_PLAN})

    response_received = pyqtSignal(str, dict)  # (action, decoded response body)
    # (action, error, body) network error or non-OK lambda status; body is the parsed lambda
    # error body when there was one, else None
    request_failed = pyqtSignal(str, str, object)
    parse_failed = pyqtSignal(str, str)  # (action, error) response could not be decoded
    # (tag, reply) — typed as object so test doubles can pass through the signal
    s3_reply_received = pyqtSignal(str, object)
    job_status_changed = pyqtSignal(str, str)  # (action, JobStatus.QUEUED or JobStatus.RUNNING)

    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)
        self.network_manager = QNetworkAccessManager(self)
        self.network_manager.finished.connect(self._handle_response)
        self._jobs: dict[str, _Job] = {}
        self._now = time.monotonic  # clock for the job deadline; tests replace it
        logger.debug("LambdaClient initialized and network response handler connected")

    def abort_pending(self) -> int:
        """Cancels every reply still in flight and stops polling every job, without running the handlers.

        Call this when the owner of the client goes away before the answer arrives. A job
        cannot be cancelled: it runs to its end in the backend, only the polling stops.
        `QNetworkReply.abort` emits `QNetworkAccessManager.finished` synchronously, so the
        handler is disconnected first and reconnected afterwards: otherwise the cancelled
        reply would raise an error box on a dialog that is already closing. The client
        stays usable, so a dock can cancel one request and go on to make another.

        Returns the number of cancelled replies and jobs.
        """
        jobs = list(self._jobs.values())
        for job in jobs:
            self._end_job(job)
        replies = self.network_manager.findChildren(QNetworkReply)
        if replies:
            self.network_manager.finished.disconnect(self._handle_response)
            try:
                for reply in replies:
                    reply.abort()
                    reply.deleteLater()
            finally:
                self.network_manager.finished.connect(self._handle_response)
        logger.debug("Aborted in-flight replies count=%s jobs=%s", len(replies), len(jobs))
        return len(replies) + len(jobs)

    def post_action(self, action: str, plan_id: str | None = None, payload: dict[str, Any] | None = None):
        """Sends a request to the lambda function in job mode."""
        logger.debug("Preparing lambda request action=%s plan_id=%s", action, plan_id)
        if payload is None:
            payload = {}
        if plan_id:
            payload["plan_uuid"] = plan_id
        payload["action"] = action
        payload["save_json"] = True  # Uncomment for debugging to save the payload and response json in the lambda
        # A backend without job mode ignores the flag, and so do get_upload_url and get_job
        payload["run_as_job"] = True
        self._post(action, payload)

    def get(self, request: QNetworkRequest):
        self.network_manager.get(request)

    def put(self, request: QNetworkRequest, body: QByteArray):
        self.network_manager.put(request, body)

    def _post(self, action: str, payload: dict[str, Any], job_id: str | None = None):
        lambda_url = SettingsManager.get_lambda_url()
        self._apply_proxy()

        request = QNetworkRequest(QUrl(lambda_url))
        request.setAttribute(LambdaClient.ActionAttribute, action)
        request.setHeader(QNetworkRequest.KnownHeaders.ContentTypeHeader, "application/json")
        # A submit has no transfer timeout: in local development the job runs inside the submit call
        if job_id is not None:
            request.setAttribute(LambdaClient.JobAttribute, job_id)
            request.setTransferTimeout(POLL_TIMEOUT_MS)
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
        logger.debug(
            "Lambda request sent action=%s lambda_url=%s payload_size_bytes=%s",
            action,
            lambda_url,
            payload_bytes.size(),
        )

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

    @staticmethod
    def _is_success(status: int | None) -> bool:
        return status is not None and HTTPStatus.OK <= status < HTTPStatus.MULTIPLE_CHOICES

    def _decode_reply(self, response: QNetworkReply) -> _Answer:
        """Decodes a lambda reply, through API Gateway or by direct invocation, into one `_Answer`.

        Raises `ValueError` (bad JSON or text), `KeyError` or `OSError` (bad gzip) when the
        body of a successful reply cannot be decoded.
        """
        http_status = response.attribute(QNetworkRequest.Attribute.HttpStatusCodeAttribute)
        status = int(http_status) if http_status is not None else None
        if response.error() != QNetworkReply.NetworkError.NoError:  # type: ignore  # wrong type annotation in the stubs
            # HTTP 4xx/5xx replies carry the lambda error body; connection errors have neither
            # a body nor an HTTP status
            return _Answer(status, self._read_error_body(response), ok=False, error=response.errorString())

        response_bytes = response.readAll().data()
        if is_api_gateway_url(response.request().url().toString()):
            is_compressed = bytes(response.rawHeader(b"Content-Encoding")).decode("utf-8") == "gzip"
            logger.debug("API Gateway response compressed=%s", is_compressed)
            if is_compressed:
                response_bytes = gzip.decompress(response_bytes)
            return _Answer(status, json.loads(response_bytes.decode("utf-8")), ok=True)

        # In developement environment lambda is called directly without API Gateway
        # and has a different response format
        response_data = json.loads(response_bytes.decode("utf-8"))
        is_compressed = response_data.get("encoding") == "gzip+base64"
        logger.debug("Direct lambda response compressed=%s", is_compressed)
        if is_compressed:
            compressed_data = base64.b64decode(response_data["body"])
            response_data["body"] = json.loads(gzip.decompress(compressed_data).decode("utf-8"))
        status = int(response_data.get("statusCode", 0))
        body = response_data.get("body")
        error = str(response_data.get("errorMessage")) if body is None else ""
        return _Answer(status, body, ok=self._is_success(status), error=error)

    def _handle_response(self, response: QNetworkReply):
        action = response.request().attribute(LambdaClient.ActionAttribute)
        logger.debug("Handling lambda response action=%s", action)
        # Presigned S3 replies are raw HTTP, not lambda response envelopes;
        # the receiver of the signal owns the reply and calls deleteLater() on it
        if action in self._RAW_S3_ACTIONS:
            self.s3_reply_received.emit(action, response)
            return
        if action == self.ACTION_GET_JOB:
            self._handle_poll_reply(response)
            return

        try:
            answer = self._decode_reply(response)
        except (ValueError, KeyError, OSError) as e:
            logger.debug("Failed to parse lambda response action=%s error=%s", action, e)
            self.parse_failed.emit(action, str(e))
            return
        finally:
            response.deleteLater()
        self._dispatch(action, answer)

    def _dispatch(self, action: str, answer: _Answer):
        """Hands the answer of an action to the signals, or starts polling when the action became a job."""
        body = answer.body
        if answer.ok and answer.status == HTTPStatus.ACCEPTED and self._job_id(body):
            self._start_job(action, self._job_id(body))
            return
        if answer.ok:
            if not isinstance(body, dict):
                self.parse_failed.emit(action, f"Odottamaton vastaus: {body!r}")
                return
            self.response_received.emit(action, body)
            return

        if isinstance(body, dict):
            error = self._format_error_body(body)
            if body.get("title") == _JOB_NOT_STARTED_TITLE:
                error = f"{JOB_NOT_STARTED_MESSAGE} ({error})"
        else:
            # Error handlers emit str-typed signals, so format the body into a string
            error = answer.error or str(body)
        logger.debug("Lambda action failed action=%s status=%s error=%s", action, answer.status, error)
        self.request_failed.emit(action, error, body if isinstance(body, dict) else None)

    @staticmethod
    def _job_id(body: Any) -> str:
        details = body.get("details") if isinstance(body, dict) else None
        job_id = details.get("job_id") if isinstance(details, dict) else None
        return str(job_id) if job_id else ""

    # Job polling

    def _start_job(self, action: str, job_id: str):
        timer = QTimer(self)
        timer.setSingleShot(True)
        timer.setInterval(POLL_INTERVAL_MS)
        timer.timeout.connect(lambda: self._poll(job_id))
        self._jobs[job_id] = _Job(action, job_id, self._now() + JOB_DEADLINE_S, timer)
        logger.debug("Job submitted action=%s job_id=%s", action, job_id)
        self.job_status_changed.emit(action, JobStatus.QUEUED)
        timer.start()

    def _end_job(self, job: _Job):
        job.timer.stop()
        job.timer.deleteLater()
        self._jobs.pop(job.job_id, None)

    def _poll(self, job_id: str):
        if job_id in self._jobs:
            self._post(self.ACTION_GET_JOB, {"action": self.ACTION_GET_JOB, "job_id": job_id}, job_id=job_id)

    def _poll_again(self, job: _Job):
        """Polls the job again after the interval, or fails the action when the deadline has passed."""
        if self._now() >= job.deadline:
            logger.debug("Job deadline passed action=%s job_id=%s", job.action, job.job_id)
            self._end_job(job)
            self.request_failed.emit(job.action, JOB_DEADLINE_MESSAGE, None)
            return
        job.timer.start()

    @staticmethod
    def _poll_error_is_temporary(status: int | None) -> bool:
        """True when a failed poll is worth repeating: other client errors (4xx) fail again."""
        # No status: a network error, or a crashed lambda in a direct call
        if not status:
            return True
        return status == HTTPStatus.TOO_MANY_REQUESTS or status >= HTTPStatus.INTERNAL_SERVER_ERROR

    def _handle_poll_reply(self, response: QNetworkReply):
        job = self._jobs.get(response.request().attribute(LambdaClient.JobAttribute))
        if job is None:  # polling was stopped
            response.deleteLater()
            return
        try:
            answer = self._decode_reply(response)
        except (ValueError, KeyError, OSError) as e:
            # A poll that cannot be read says nothing about the job
            logger.debug("Failed to parse job poll error=%s", e)
            self._poll_again(job)
            return
        finally:
            response.deleteLater()

        body = answer.body if isinstance(answer.body, dict) else {}
        if not answer.ok:
            if not self._poll_error_is_temporary(answer.status):
                # An unknown or expired job, a bad poll or a refused API key: polling again does not help
                self._end_job(job)
                error = self._format_error_body(body) if body else answer.error
                self.request_failed.emit(job.action, f"{JOB_POLL_FAILED_MESSAGE} {error}", body or None)
                return
            # A server, gateway, throttling or network error says nothing about the job
            logger.debug("Job poll failed job_id=%s status=%s error=%s", job.job_id, answer.status, answer.error)
            self._poll_again(job)
            return

        details = body.get("details")
        details = details if isinstance(details, dict) else {}
        status = details.get("status")
        logger.debug("Job poll action=%s job_id=%s status=%s", job.action, job.job_id, status)
        if status == JobStatus.DONE:
            # The action ran; its result is the answer the action gives without job mode
            self._end_job(job)
            result = details.get("result")
            if not isinstance(result, dict):
                self.request_failed.emit(job.action, JOB_FAILED_MESSAGE, body)
                return
            result_status = result.get("statusCode")
            result_status = int(result_status) if result_status is not None else None
            self._dispatch(job.action, _Answer(result_status, result.get("body"), ok=self._is_success(result_status)))
        elif status == JobStatus.FAILED:
            # No answer at all: the job crashed, never started or ran past the time limit
            self._end_job(job)
            job_error = details.get("error")
            message = f"{JOB_FAILED_MESSAGE} ({job_error})" if job_error else JOB_FAILED_MESSAGE
            self.request_failed.emit(job.action, message, body)
        else:
            if status in (JobStatus.QUEUED, JobStatus.RUNNING) and status != job.status:
                job.status = JobStatus(status)
                self.job_status_changed.emit(job.action, job.status)
            self._poll_again(job)
