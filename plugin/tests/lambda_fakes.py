"""Test doubles for the Qt network layer of LambdaClient."""

from __future__ import annotations

import json

from qgis.PyQt.QtCore import QByteArray, QUrl
from qgis.PyQt.QtNetwork import QNetworkReply

from arho_feature_template.core.lambda_client import LambdaClient

GATEWAY_URL = "https://abc.execute-api.eu-central-1.amazonaws.com/v0/ryhti"
DIRECT_URL = "http://localhost:8083/2015-03-31/functions/function/invocations"


class FakeRequest:
    """Stands in for QNetworkRequest carrying the action and job attributes and the request URL."""

    def __init__(self, action, url="", job_id=None):
        self._action = action
        self._url = url
        self._job_id = job_id

    def attribute(self, attribute):
        if attribute == LambdaClient.JobAttribute:
            return self._job_id
        return self._action

    def url(self):
        return QUrl(self._url)


class FakeReply:
    """Stands in for QNetworkReply in response handlers.

    `attribute` answers every attribute with `status_code`, the HTTP status.
    """

    def __init__(
        self,
        data: bytes = b"",
        error=QNetworkReply.NetworkError.NoError,
        error_string: str = "",
        status_code=200,
        action=None,
        url: str = "",
        job_id=None,
        content_encoding: bytes = b"",
    ):
        self._data = data
        self._error = error
        self._error_string = error_string
        self._status_code = status_code
        self._action = action
        self._url = url
        self._job_id = job_id
        self._content_encoding = content_encoding
        self.deleted = False

    def error(self):
        return self._error

    def errorString(self):
        return self._error_string

    def attribute(self, _attribute):
        return self._status_code

    def rawHeader(self, name):
        return QByteArray(self._content_encoding if name == b"Content-Encoding" else b"")

    def request(self):
        return FakeRequest(self._action, self._url, self._job_id)

    def readAll(self):
        return QByteArray(self._data)

    def deleteLater(self):
        self.deleted = True


class FakeNetworkManager:
    """Records the requests the client sends; no reply comes back until a test feeds one."""

    def __init__(self):
        self.get_requests = []
        self.put_requests = []
        self.post_requests = []

    def get(self, request):
        self.get_requests.append(request)

    def put(self, request, data):
        self.put_requests.append((request, data))

    def post(self, request, data):
        self.post_requests.append((request, json.loads(bytes(data).decode("utf-8"))))

    def setProxy(self, _proxy):
        pass

    def findChildren(self, _type):
        return []
