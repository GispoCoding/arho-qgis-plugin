from __future__ import annotations

import logging
import re
from http import HTTPStatus

from qgis.PyQt.QtCore import QUrl
from qgis.PyQt.QtNetwork import QNetworkReply, QNetworkRequest

logger = logging.getLogger(__name__)


def is_api_gateway_url(url: str) -> bool:
    """Determines if the lambda request is going through the API Gateway."""
    match = re.match(r"^https://.*execute-api.*amazonaws\.com.*$", url)
    is_api_gateway = bool(match)
    logger.debug("Lambda URL classified as api_gateway=%s", is_api_gateway)
    return is_api_gateway


def prepare_presigned_request(url: str) -> QNetworkRequest:
    """Builds a request for a presigned S3 URL.

    In the local development environment the presigned URLs point at the MinIO container
    host ``minio``, which only resolves inside the docker compose network. Rewrite the host
    to ``localhost`` (keeping the port) but send the original host as the raw ``Host``
    header so the URL signature stays valid. Real AWS URLs pass through untouched.

    No auth, Content-Type or Accept-Encoding headers may be added: the signature covers the
    request, and Qt only decompresses gzip responses transparently when it manages the
    Accept-Encoding header itself.
    """
    qurl = QUrl(url)
    request = QNetworkRequest(qurl)
    if qurl.host() == "minio":
        original_host = qurl.host() + (f":{qurl.port()}" if qurl.port() != -1 else "")
        qurl.setHost("localhost")
        request.setUrl(qurl)
        request.setRawHeader(b"Host", original_host.encode("utf-8"))
        logger.debug("Rewrote presigned MinIO URL host to localhost, Host header=%s", original_host)
    return request


def presigned_reply_error(response: QNetworkReply) -> str | None:
    """Returns an error description if a presigned S3 request failed, otherwise None.

    Qt does not treat 3xx statuses as network errors and does not follow redirects, so
    the HTTP status must be checked in addition to the network error. For example S3
    responds with 307 TemporaryRedirect (an XML body) when a newly created bucket is
    accessed through the global endpoint before DNS has propagated.
    """
    if response.error() != QNetworkReply.NetworkError.NoError:  # type: ignore  # wrong type annotation in the stubs
        return response.errorString()
    status_code = response.attribute(QNetworkRequest.Attribute.HttpStatusCodeAttribute)
    if status_code is not None and not HTTPStatus.OK <= status_code < HTTPStatus.MULTIPLE_CHOICES:
        body_excerpt = response.readAll().data()[:500].decode("utf-8", errors="replace")
        return f"HTTP {status_code}: {body_excerpt}"
    return None
