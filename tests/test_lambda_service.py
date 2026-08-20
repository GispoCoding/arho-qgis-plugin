"""Tests for the S3 presigned URL based plan import/export chains in LambdaService."""

from __future__ import annotations

import gzip
import json

import pytest
from qgis.PyQt.QtCore import QByteArray
from qgis.PyQt.QtNetwork import QNetworkReply

import arho_feature_template.core.lambda_service as lambda_service_module
from arho_feature_template.core.lambda_service import LambdaService

PLAN_ID = "11111111-1111-1111-1111-111111111111"
PLAN_JSON = json.dumps({"planKey": PLAN_ID, "name": "Testikaava"})
EXTRA_DATA = {"name": "Testikaava", "plan_matter_id": "22222222-2222-2222-2222-222222222222"}


class FakeReply:
    """Stands in for QNetworkReply in response handlers."""

    def __init__(
        self, data: bytes = b"", error=QNetworkReply.NetworkError.NoError, error_string: str = "", status_code=200
    ):
        self._data = data
        self._error = error
        self._error_string = error_string
        self._status_code = status_code
        self.deleted = False

    def error(self):
        return self._error

    def errorString(self):
        return self._error_string

    def attribute(self, _attribute):
        return self._status_code

    def readAll(self):
        return QByteArray(self._data)

    def deleteLater(self):
        self.deleted = True


class FakeNetworkManager:
    """Records get/put calls made by the service."""

    def __init__(self):
        self.get_requests = []
        self.put_requests = []

    def get(self, request):
        self.get_requests.append(request)

    def put(self, request, data):
        self.put_requests.append((request, data))


@pytest.fixture
def service(monkeypatch):
    service = LambdaService()
    # Never show blocking message boxes in tests
    monkeypatch.setattr(lambda_service_module.QMessageBox, "critical", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(lambda_service_module, "get_active_plan_id", lambda: PLAN_ID)
    return service


@pytest.fixture
def network(service):
    manager = FakeNetworkManager()
    service.network_manager = manager
    return manager


@pytest.fixture
def sent_requests(service, monkeypatch):
    requests = []
    monkeypatch.setattr(
        service, "_send_request", lambda action, _plan_id=None, payload=None: requests.append((action, payload))
    )
    return requests


def signal_spy(signal) -> list:
    emitted = []
    signal.connect(lambda *args: emitted.append(args))
    return emitted


# _prepare_presigned_request


def test_presigned_request_rewrites_minio_host():
    url = "http://minio:9000/bucket/import/abc.json?X-Amz-Signature=xyz"
    request = LambdaService._prepare_presigned_request(url)
    assert request.url().host() == "localhost"
    assert request.url().port() == 9000
    assert request.url().path() == "/bucket/import/abc.json"
    assert bytes(request.rawHeader(b"Host")) == b"minio:9000"


def test_presigned_request_rewrites_minio_host_without_port():
    request = LambdaService._prepare_presigned_request("http://minio/bucket/key.json")
    assert request.url().host() == "localhost"
    assert bytes(request.rawHeader(b"Host")) == b"minio"


def test_presigned_request_leaves_aws_url_untouched():
    url = "https://bucket.s3.eu-central-1.amazonaws.com/export/abc.json?X-Amz-Signature=xyz"
    request = LambdaService._prepare_presigned_request(url)
    assert request.url().toString() == url
    assert not request.hasRawHeader(b"Host")


# Export chain


def test_export_response_starts_download(service, network):
    service._process_export_plan_response(
        {"details": {"download_url": "https://bucket.s3.amazonaws.com/export/abc.json?sig", "key": "export/abc.json"}}
    )
    assert len(network.get_requests) == 1
    request = network.get_requests[0]
    assert request.attribute(LambdaService.ActionAttribute) == LambdaService.S3_DOWNLOAD_PLAN
    assert request.url().host() == "bucket.s3.amazonaws.com"


def test_export_response_old_backend_format_is_rejected(service, network):
    emitted = signal_spy(service.plan_data_received)
    service._process_export_plan_response({"details": {PLAN_ID: {"planKey": PLAN_ID}}})
    assert not network.get_requests
    assert not emitted


def test_download_response_emits_plan_and_outline(service):
    emitted = signal_spy(service.plan_data_received)
    plans_by_id = {
        PLAN_ID: {
            "planKey": PLAN_ID,
            "geographicalArea": {"srid": "3067", "geometry": {"type": "MultiPolygon", "coordinates": []}},
        }
    }
    reply = FakeReply(json.dumps(plans_by_id).encode("utf-8"))
    service._handle_s3_download_response(reply)
    assert reply.deleted
    assert len(emitted) == 1
    plan_data, outline_data = emitted[0]
    assert plan_data["planKey"] == PLAN_ID
    assert outline_data == {"srid": "3067", "geometry": {"type": "MultiPolygon", "coordinates": []}}


def test_download_response_decompresses_gzip_manually(service):
    emitted = signal_spy(service.plan_data_received)
    body = gzip.compress(json.dumps({PLAN_ID: {"planKey": PLAN_ID}}).encode("utf-8"))
    service._handle_s3_download_response(FakeReply(body))
    assert len(emitted) == 1
    assert emitted[0][0]["planKey"] == PLAN_ID


def test_download_response_redirect_status_emits_nothing(service):
    """S3 replies like 307 TemporaryRedirect are not Qt network errors but must not be parsed as plans."""
    emitted = signal_spy(service.plan_data_received)
    body = b'<?xml version="1.0" encoding="UTF-8"?><Error><Code>TemporaryRedirect</Code></Error>'
    reply = FakeReply(body, status_code=307)
    service._handle_s3_download_response(reply)
    assert reply.deleted
    assert not emitted


def test_download_response_network_error_emits_nothing(service):
    emitted = signal_spy(service.plan_data_received)
    reply = FakeReply(error=QNetworkReply.NetworkError.ContentNotFoundError, error_string="Not found")
    service._handle_s3_download_response(reply)
    assert reply.deleted
    assert not emitted


# Import chain


def test_import_plan_requests_upload_url(service, sent_requests):
    service.import_plan(PLAN_JSON, EXTRA_DATA)
    assert len(sent_requests) == 1
    action, _payload = sent_requests[0]
    assert action == LambdaService.ACTION_GET_UPLOAD_URL
    assert service._pending_import == {"plan_json": PLAN_JSON, "extra_data": EXTRA_DATA, "force": False}


def test_upload_url_response_uploads_plan_file(service, network):
    service._pending_import = {"plan_json": PLAN_JSON, "extra_data": EXTRA_DATA, "force": False}
    service._process_get_upload_url_response(
        {"details": {"upload_url": "http://minio:9000/bucket/import/abc.json?sig", "key": "import/abc.json"}}
    )
    assert len(network.put_requests) == 1
    request, data = network.put_requests[0]
    assert request.attribute(LambdaService.ActionAttribute) == LambdaService.S3_UPLOAD_PLAN
    assert bytes(data) == PLAN_JSON.encode("utf-8")
    assert service._pending_import["s3_key"] == "import/abc.json"


def test_upload_url_response_missing_url_fails_import(service, network):
    emitted = signal_spy(service.plan_import_failed)
    service._pending_import = {"plan_json": PLAN_JSON, "extra_data": EXTRA_DATA, "force": False}
    service._process_get_upload_url_response({"details": {}})
    assert not network.put_requests
    assert len(emitted) == 1
    assert service._pending_import is None


def test_upload_response_sends_import_request(service, sent_requests):
    service._pending_import = {
        "plan_json": PLAN_JSON,
        "extra_data": EXTRA_DATA,
        "force": False,
        "s3_key": "import/abc.json",
    }
    service._handle_s3_upload_response(FakeReply())
    assert service._cached_upload == (PLAN_JSON, "import/abc.json")
    assert len(sent_requests) == 1
    action, payload = sent_requests[0]
    assert action == LambdaService.ACTION_IMPORT_PLAN
    assert payload["data"]["s3_key"] == "import/abc.json"
    assert payload["data"]["extra_data"] == EXTRA_DATA
    assert "plan_json" not in payload["data"]
    assert "force" not in payload


def test_upload_response_error_fails_import(service, sent_requests):
    emitted = signal_spy(service.plan_import_failed)
    service._pending_import = {
        "plan_json": PLAN_JSON,
        "extra_data": EXTRA_DATA,
        "force": False,
        "s3_key": "import/abc.json",
    }
    reply = FakeReply(error=QNetworkReply.NetworkError.ConnectionRefusedError, error_string="Connection refused")
    service._handle_s3_upload_response(reply)
    assert reply.deleted
    assert not sent_requests
    assert len(emitted) == 1
    assert service._pending_import is None
    assert service._cached_upload is None


def test_upload_response_redirect_status_fails_import(service, sent_requests):
    emitted = signal_spy(service.plan_import_failed)
    service._pending_import = {
        "plan_json": PLAN_JSON,
        "extra_data": EXTRA_DATA,
        "force": False,
        "s3_key": "import/abc.json",
    }
    reply = FakeReply(b"<Error><Code>TemporaryRedirect</Code></Error>", status_code=307)
    service._handle_s3_upload_response(reply)
    assert reply.deleted
    assert not sent_requests
    assert len(emitted) == 1
    assert "307" in emitted[0][0]
    assert service._cached_upload is None


def test_import_success_emits_plan_id_and_clears_cache(service):
    emitted = signal_spy(service.plan_imported)
    service._pending_import = {"plan_json": PLAN_JSON, "extra_data": EXTRA_DATA, "force": False}
    service._cached_upload = (PLAN_JSON, "import/abc.json")
    service._process_import_plan_response({"title": "Plan imported.", "details": {"plan_id": PLAN_ID}})
    assert emitted == [(PLAN_ID,)]
    assert service._pending_import is None
    assert service._cached_upload is None


def test_force_retry_reuses_uploaded_file(service, sent_requests):
    failed = signal_spy(service.plan_import_failed)
    service._cached_upload = (PLAN_JSON, "import/abc.json")

    service._process_import_plan_response({"title": "Plan already exists.", "details": {"plan_id": PLAN_ID}})
    assert len(failed) == 1
    assert "Plan already exists." in failed[0][0]
    assert service._cached_upload == (PLAN_JSON, "import/abc.json")

    service.import_plan(PLAN_JSON, EXTRA_DATA, force=True)
    # No new get_upload_url request; the import request is sent directly with the cached key
    assert len(sent_requests) == 1
    action, payload = sent_requests[0]
    assert action == LambdaService.ACTION_IMPORT_PLAN
    assert payload["data"]["s3_key"] == "import/abc.json"
    assert payload["force"] is True


def test_other_import_errors_clear_cached_upload(service):
    failed = signal_spy(service.plan_import_failed)
    service._cached_upload = (PLAN_JSON, "import/abc.json")
    service._process_import_plan_response({"title": "Uploaded plan file not found.", "details": {}})
    assert len(failed) == 1
    assert service._cached_upload is None


def test_get_upload_url_error_hints_about_backend_version(service):
    emitted = signal_spy(service.plan_import_failed)
    service._pending_import = {"plan_json": PLAN_JSON, "extra_data": EXTRA_DATA, "force": False}
    service._handle_get_upload_url_error("Unknown action.")
    assert len(emitted) == 1
    assert "Unknown action." in emitted[0][0]
    assert "päivitetty" in emitted[0][0]
    assert service._pending_import is None


# Reply routing


def test_s3_replies_are_routed_past_lambda_handlers(service, monkeypatch):
    routed = []
    monkeypatch.setattr(service, "_handle_s3_download_response", lambda reply: routed.append(("download", reply)))
    monkeypatch.setattr(service, "_handle_s3_upload_response", lambda reply: routed.append(("upload", reply)))

    def handler_lookup_fails(action):
        pytest.fail(f"S3 reply reached lambda handler lookup with action={action}")

    monkeypatch.setattr(service, "_get_response_handler", handler_lookup_fails)

    class FakeRequest:
        def __init__(self, action):
            self._action = action

        def attribute(self, _attribute):
            return self._action

    class FakeRoutedReply:
        def __init__(self, action):
            self._request = FakeRequest(action)

        def request(self):
            return self._request

    service._handle_response(FakeRoutedReply(LambdaService.S3_DOWNLOAD_PLAN))
    service._handle_response(FakeRoutedReply(LambdaService.S3_UPLOAD_PLAN))
    assert [kind for kind, _reply in routed] == ["download", "upload"]
