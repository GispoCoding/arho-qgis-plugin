"""Tests for the job mode of LambdaClient: submit, poll get_job, hand the result to the action handler."""

from __future__ import annotations

import gzip
import json

import pytest
from qgis.PyQt.QtNetwork import QNetworkReply

import arho_feature_template.core.lambda_client as lambda_client_module
import arho_feature_template.core.lambda_service as lambda_service_module
from arho_feature_template.core.lambda_client import (
    ACTION_RUNNING_MESSAGE,
    JOB_DEADLINE_MESSAGE,
    JOB_DEADLINE_S,
    JOB_FAILED_MESSAGE,
    JOB_NOT_STARTED_MESSAGE,
    JOB_POLL_FAILED_MESSAGE,
    JobStatus,
    LambdaClient,
)
from arho_feature_template.core.lambda_service import LambdaService
from tests.lambda_fakes import DIRECT_URL, GATEWAY_URL, FakeNetworkManager, FakeReply

pytestmark = pytest.mark.fake_iface

PLAN_ID = "11111111-1111-1111-1111-111111111111"
JOB_ID = "8d0bd5a4-0000-4000-8000-000000000000"
EXPORTED = {"title": "Plan exported.", "details": {"download_url": "https://s3/x", "key": "x"}, "ryhti_response": None}
SUBMITTED = {"title": "Job submitted.", "details": {"job_id": JOB_ID}, "ryhti_response": None}
NOT_FOUND = {"title": "Plan not found.", "details": {"error": "No plan with that id."}, "ryhti_response": None}

# Qt reports an HTTP error status as a network error; any error value will do for the client
HTTP_ERRORS = {
    400: QNetworkReply.NetworkError.ProtocolInvalidOperationError,
    401: QNetworkReply.NetworkError.AuthenticationRequiredError,
    403: QNetworkReply.NetworkError.ContentAccessDenied,
    404: QNetworkReply.NetworkError.ContentNotFoundError,
    429: QNetworkReply.NetworkError.UnknownServerError,
    500: QNetworkReply.NetworkError.InternalServerError,
    502: QNetworkReply.NetworkError.UnknownServerError,
    503: QNetworkReply.NetworkError.ServiceUnavailableError,
    504: QNetworkReply.NetworkError.UnknownServerError,
}


class FakeClock:
    def __init__(self):
        self.now = 1000.0

    def __call__(self):
        return self.now


class Backend:
    """Feeds answers to the requests a LambdaClient sent to a FakeNetworkManager."""

    def __init__(self, client: LambdaClient, url: str):
        self.client = client
        self.url = url
        self.network = FakeNetworkManager()
        client.network_manager = self.network

    def last_payload(self) -> dict:
        return self.network.post_requests[-1][1]

    def answer(self, status: int | None, body: dict | None = None, *, compress: bool = False):
        """Answers the last request sent with the HTTP status and JSON body (gateway), or the envelope (direct)."""
        request, payload = self.network.post_requests[-1]
        job_id = payload.get("job_id")
        action = payload["action"]
        if status is None:  # connection error: no HTTP status, no body
            reply = FakeReply(
                error=QNetworkReply.NetworkError.ConnectionRefusedError,
                error_string="Connection refused",
                status_code=None,
                action=action,
                url=self.url,
                job_id=job_id,
            )
        elif self.url == DIRECT_URL:
            envelope = {"statusCode": status, "body": body}
            reply = FakeReply(json.dumps(envelope).encode("utf-8"), action=action, url=self.url, job_id=job_id)
        else:
            data = json.dumps(body).encode("utf-8") if body is not None else b""
            if compress:
                data = gzip.compress(data)
            reply = FakeReply(
                data,
                error=HTTP_ERRORS.get(status, QNetworkReply.NetworkError.NoError),
                error_string=f"server replied: {status}",
                status_code=status,
                action=action,
                url=self.url,
                job_id=job_id,
                content_encoding=b"gzip" if compress else b"",
            )
        assert request.attribute(LambdaClient.ActionAttribute) == action
        self.client._handle_response(reply)
        assert reply.deleted

    def poll(self):
        """Lets the poll interval pass: the one waiting job timer fires."""
        jobs = list(self.client._jobs.values())
        assert len(jobs) == 1
        assert jobs[0].timer.isActive()
        jobs[0].timer.stop()
        sent = len(self.network.post_requests)
        self.client._poll(jobs[0].job_id)
        assert len(self.network.post_requests) == sent + 1
        assert self.last_payload() == {"action": "get_job", "job_id": jobs[0].job_id} | (
            {"headers": {"Accept-Encoding": "gzip"}} if self.url == DIRECT_URL else {}
        )


def job(status: str, result: dict | None = None, error: str | None = None) -> dict:
    details: dict = {"job_id": JOB_ID, "status": status, "result": result}
    if error:
        details["error"] = error
    return {"title": "Job found.", "details": details, "ryhti_response": None}


def signal_spy(signal) -> list:
    emitted = []
    signal.connect(lambda *args: emitted.append(args))
    return emitted


@pytest.fixture(params=[GATEWAY_URL, DIRECT_URL], ids=["api_gateway", "direct"])
def lambda_url(request, monkeypatch):
    monkeypatch.setattr(lambda_client_module.SettingsManager, "get_lambda_url", lambda: request.param)
    monkeypatch.setattr(lambda_client_module.SettingsManager, "get_proxy_port", lambda: 0)
    return request.param


@pytest.fixture
def client(qgis_app):  # noqa: ARG001
    client = LambdaClient()
    client._now = FakeClock()
    yield client
    client.abort_pending()


@pytest.fixture
def backend(client, lambda_url):
    return Backend(client, lambda_url)


@pytest.fixture
def spies(client):
    return {
        "received": signal_spy(client.response_received),
        "failed": signal_spy(client.request_failed),
        "parse_failed": signal_spy(client.parse_failed),
        "status": signal_spy(client.job_status_changed),
    }


def test_every_request_is_submitted_as_a_job(client, backend):
    client.post_action(LambdaClient.ACTION_GET_PLAN, plan_id=PLAN_ID)
    payload = backend.last_payload()
    assert payload["action"] == "get_plan"
    assert payload["plan_uuid"] == PLAN_ID
    assert payload["run_as_job"] is True


def test_job_is_polled_until_done(client, backend, spies):
    client.post_action(LambdaClient.ACTION_GET_PLAN, plan_id=PLAN_ID)
    backend.answer(202, SUBMITTED)
    assert spies["status"] == [("get_plan", JobStatus.QUEUED)]

    backend.poll()
    backend.answer(200, job("queued"))
    backend.poll()
    backend.answer(200, job("running"))
    backend.poll()
    backend.answer(200, job("running"))
    assert spies["received"] == []
    backend.poll()
    backend.answer(200, job("done", {"statusCode": 200, "body": EXPORTED}))

    assert spies["status"] == [("get_plan", JobStatus.QUEUED), ("get_plan", JobStatus.RUNNING)]
    assert spies["received"] == [("get_plan", EXPORTED)]
    assert spies["failed"] == []
    assert client._jobs == {}


def test_gzipped_poll_answer(client, spies, monkeypatch):
    monkeypatch.setattr(lambda_client_module.SettingsManager, "get_lambda_url", lambda: GATEWAY_URL)
    backend = Backend(client, GATEWAY_URL)
    client.post_action(LambdaClient.ACTION_GET_PLAN, plan_id=PLAN_ID)
    backend.answer(202, SUBMITTED, compress=True)
    backend.poll()
    backend.answer(200, job("done", {"statusCode": 200, "body": EXPORTED}), compress=True)
    assert spies["received"] == [("get_plan", EXPORTED)]


def test_done_job_with_an_error_result_goes_to_the_error_handler(client, backend, spies):
    client.post_action(LambdaClient.ACTION_GET_PLAN, plan_id=PLAN_ID)
    backend.answer(202, SUBMITTED)
    backend.poll()
    backend.answer(200, job("done", {"statusCode": 404, "body": NOT_FOUND}))

    assert spies["received"] == []
    assert spies["failed"] == [("get_plan", "Plan not found. No plan with that id.", NOT_FOUND)]
    assert client._jobs == {}


def test_failed_job_shows_a_generic_error(client, backend, spies):
    client.post_action(LambdaClient.ACTION_GET_PLAN, plan_id=PLAN_ID)
    backend.answer(202, SUBMITTED)
    backend.poll()
    backend.answer(200, job("failed", error="Job timed out."))

    assert spies["received"] == []
    [(action, error, _body)] = spies["failed"]
    assert action == "get_plan"
    assert error.startswith(JOB_FAILED_MESSAGE)
    assert client._jobs == {}


def test_job_that_could_not_be_started(client, backend, spies):
    body = {"title": "Job could not be started.", "details": {"error": "Queue is full."}, "ryhti_response": None}
    client.post_action(LambdaClient.ACTION_GET_PLAN, plan_id=PLAN_ID)
    backend.answer(502, body)

    [(action, error, failed_body)] = spies["failed"]
    assert action == "get_plan"
    assert error.startswith(JOB_NOT_STARTED_MESSAGE)
    assert failed_body == body
    assert client._jobs == {}


@pytest.mark.parametrize(
    "poll_error",
    [500, 502, 503, 504, 429, None],
    ids=["server_error", "bad_gateway", "unavailable", "gateway_timeout", "throttled", "network_error"],
)
def test_failed_poll_is_retried(client, backend, spies, poll_error):
    client.post_action(LambdaClient.ACTION_GET_PLAN, plan_id=PLAN_ID)
    backend.answer(202, SUBMITTED)
    backend.poll()
    backend.answer(poll_error, {"title": "Internal Server Error.", "details": {"error": "boom"}})
    assert spies["failed"] == []

    backend.poll()
    backend.answer(200, job("done", {"statusCode": 200, "body": EXPORTED}))
    assert spies["received"] == [("get_plan", EXPORTED)]
    assert spies["failed"] == []


@pytest.mark.parametrize("poll_status", [400, 404])
def test_unknown_job_stops_polling(client, backend, spies, poll_status):
    client.post_action(LambdaClient.ACTION_GET_PLAN, plan_id=PLAN_ID)
    backend.answer(202, SUBMITTED)
    backend.poll()
    backend.answer(poll_status, {"title": "Job not found.", "details": {"error": "No such job."}})

    [(action, error, _body)] = spies["failed"]
    assert action == "get_plan"
    assert error == f"{JOB_POLL_FAILED_MESSAGE} Job not found. No such job."
    assert client._jobs == {}


@pytest.mark.parametrize("poll_status", [401, 403])
def test_refused_poll_stops_polling(client, backend, spies, poll_status):
    """A bad API key does not get better by polling again until the deadline."""
    client.post_action(LambdaClient.ACTION_GET_PLAN, plan_id=PLAN_ID)
    backend.answer(202, SUBMITTED)
    backend.poll()
    backend.answer(poll_status, {"message": "Forbidden"})

    [(action, error, _body)] = spies["failed"]
    assert action == "get_plan"
    assert error.startswith(JOB_POLL_FAILED_MESSAGE)
    assert client._jobs == {}
    assert not client.is_busy()


def test_deadline_stops_polling(client, backend, spies):
    client.post_action(LambdaClient.ACTION_GET_PLAN, plan_id=PLAN_ID)
    backend.answer(202, SUBMITTED)
    backend.poll()
    client._now.now += JOB_DEADLINE_S - 1
    backend.answer(500, {"title": "Internal Server Error."})
    assert spies["failed"] == []

    backend.poll()
    client._now.now += 1
    backend.answer(500, {"title": "Internal Server Error."})

    assert spies["failed"] == [("get_plan", JOB_DEADLINE_MESSAGE, None)]
    assert client._jobs == {}


def test_old_backend_answers_the_submit_directly(client, backend, spies):
    client.post_action(LambdaClient.ACTION_GET_PLAN, plan_id=PLAN_ID)
    backend.answer(200, EXPORTED)

    assert spies["received"] == [("get_plan", EXPORTED)]
    assert spies["status"] == []
    assert client._jobs == {}
    assert len(backend.network.post_requests) == 1


def test_bad_request_is_refused_without_a_job(client, backend, spies):
    body = {"title": "Invalid plan_uuid.", "details": {"error": "Not a UUID."}, "ryhti_response": None}
    client.post_action(LambdaClient.ACTION_GET_PLAN, plan_id="x")
    backend.answer(400, body)

    assert spies["failed"] == [("get_plan", "Invalid plan_uuid. Not a UUID.", body)]
    assert client._jobs == {}


def test_abort_pending_stops_polling(client, backend, spies):
    client.post_action(LambdaClient.ACTION_GET_PLAN, plan_id=PLAN_ID)
    backend.answer(202, SUBMITTED)
    backend.poll()

    assert client.abort_pending() == 1
    assert client._jobs == {}
    # A poll answer that still arrives is dropped
    backend.answer(200, job("done", {"statusCode": 200, "body": EXPORTED}))
    assert spies["received"] == []
    assert spies["failed"] == []


def test_action_is_busy_until_its_job_ends(client, backend):
    busy = signal_spy(client.busy_changed)
    client.post_action(LambdaClient.ACTION_GET_PLAN, plan_id=PLAN_ID)
    backend.answer(202, SUBMITTED)
    backend.poll()
    backend.answer(200, job("running"))
    assert client.is_busy(LambdaClient.ACTION_GET_PLAN)
    assert not client.is_busy(LambdaClient.ACTION_FINALIZE_PLAN)
    assert busy == [("get_plan", True)]

    backend.poll()
    backend.answer(200, job("failed"))

    assert not client.is_busy()
    assert busy == [("get_plan", True), ("get_plan", False)]


def test_busy_action_is_not_sent_twice(client, backend):
    refused = signal_spy(client.request_refused)
    assert client.post_action(LambdaClient.ACTION_GET_PLAN, plan_id=PLAN_ID)
    backend.answer(202, SUBMITTED)

    assert not client.post_action(LambdaClient.ACTION_GET_PLAN, plan_id=PLAN_ID)
    assert len(backend.network.post_requests) == 1
    assert refused == [("get_plan",)]
    # Another action is sent
    assert client.post_action(LambdaClient.ACTION_FINALIZE_PLAN, plan_id=PLAN_ID)


def test_action_is_idle_when_its_handler_runs(client, backend):
    """A handler that starts the next step of a chain may send the same action again."""
    seen = []
    client.response_received.connect(lambda action, _body: seen.append(client.is_busy(action)))
    client.post_action(LambdaClient.ACTION_GET_PLAN, plan_id=PLAN_ID)
    backend.answer(200, EXPORTED)
    assert seen == [False]


def test_abort_pending_clears_busy(client, backend):
    client.post_action(LambdaClient.ACTION_GET_PLAN, plan_id=PLAN_ID)
    backend.answer(202, SUBMITTED)
    client.abort_pending()
    assert not client.is_busy()


@pytest.fixture
def other_client(qgis_app, lambda_url):  # noqa: ARG001
    """A second client, as in a second dialog."""
    other = LambdaClient()
    Backend(other, lambda_url)
    yield other
    other.abort_pending()


def test_action_running_in_another_client_is_refused(client, backend, other_client):
    refused = signal_spy(other_client.request_refused)
    client.post_action(LambdaClient.ACTION_GET_PLAN, plan_id=PLAN_ID)
    backend.answer(202, SUBMITTED)

    assert not other_client.post_action(LambdaClient.ACTION_GET_PLAN, plan_id=PLAN_ID)
    assert refused == [("get_plan",)]
    # The busy state of a client is its own: a dialog waits only for its own job
    assert not other_client.is_busy()

    backend.poll()
    backend.answer(200, job("done", {"statusCode": 200, "body": EXPORTED}))
    assert other_client.post_action(LambdaClient.ACTION_GET_PLAN, plan_id=PLAN_ID)


def test_abort_pending_frees_the_action_for_other_clients(client, backend, other_client):
    client.post_action(LambdaClient.ACTION_GET_PLAN, plan_id=PLAN_ID)
    backend.answer(202, SUBMITTED)
    client.abort_pending()

    assert other_client.post_action(LambdaClient.ACTION_GET_PLAN, plan_id=PLAN_ID)


@pytest.mark.usefixtures("lambda_url")
def test_refused_action_tells_the_user(qgis_app, messages, monkeypatch):  # noqa: ARG001
    monkeypatch.setattr(lambda_service_module, "get_active_plan_id", lambda: PLAN_ID)
    first, second = LambdaService(), LambdaService()
    for service in (first, second):
        service._client.network_manager = FakeNetworkManager()
    failures = signal_spy(second.validation_failed)

    first.validate_plan(PLAN_ID)
    second.validate_plan(PLAN_ID)

    assert messages.warnings == [("", ACTION_RUNNING_MESSAGE)]
    # The error handler of the action runs, so the dock leaves its waiting state
    assert failures == [(ACTION_RUNNING_MESSAGE,)]
    first.abort_pending()


@pytest.mark.usefixtures("lambda_url")
def test_refused_import_does_not_blame_the_backend_version(qgis_app, messages):  # noqa: ARG001
    first, second = LambdaService(), LambdaService()
    for service in (first, second):
        service._client.network_manager = FakeNetworkManager()
    failures = signal_spy(second.plan_import_failed)

    first.import_plan("{}", {})
    second.import_plan("{}", {})

    assert messages.warnings == [("", ACTION_RUNNING_MESSAGE)]
    assert failures == [(f"error: {ACTION_RUNNING_MESSAGE}",)]
    first.abort_pending()


def test_job_result_reaches_the_existing_action_handler(qgis_app, lambda_url, monkeypatch):  # noqa: ARG001
    """A finalize_plan job that ends in a 409 hands the Ryhti errors to the validation dock."""
    monkeypatch.setattr(lambda_service_module.QMessageBox, "critical", lambda *_args: pytest.fail("error box"))
    service = LambdaService()
    backend = Backend(service._client, lambda_url)
    validation_failed = signal_spy(service.plan_finalize_validation_failed)
    ryhti_response = {"status": 400, "errors": [{"ruleId": "plan.1"}], "warnings": []}
    body = {"title": "Plan did not pass Ryhti validation.", "details": {}, "ryhti_response": ryhti_response}

    service.finalize_plan(PLAN_ID)
    backend.answer(202, SUBMITTED)
    backend.poll()
    backend.answer(200, job("done", {"statusCode": 409, "body": body}))

    assert validation_failed == [(ryhti_response,)]
    service.abort_pending()
