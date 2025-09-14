from __future__ import annotations

import json
import os
import re
from typing import TYPE_CHECKING, cast
from uuid import uuid4

import pytest
from requests import PreparedRequest
from requests_mock.request import _RequestObjectProxy
from simplejson import JSONEncoder
from sqlalchemy.orm import Session

from database import codes, models
from ryhti_client.database_client import DatabaseClient
from ryhti_client.ryhti_client import RyhtiClient

from .conftest import deepcompare

if TYPE_CHECKING:
    from collections.abc import Callable, Generator
    from json.encoder import JSONEncoder as StdJSONEncoder

    from requests import PreparedRequest
    from requests_mock import Mocker
    from requests_mock.request import _RequestObjectProxy
    from sqlalchemy.orm import Session

    from database import codes, models

mock_rule = "random_rule"
mock_matter_rule = "another_random_rule"
mock_error_string = "There is something wrong with your plan! Good luck!"
mock_matter_error_string = (
    "There is something wrong with your plan matter as well! Have fun!"
)
mock_instance = "some field in your plan"
mock_matter_instance = "some field in your plan matter"


@pytest.fixture
def mock_public_ryhti_validate_invalid(requests_mock: Mocker) -> None:
    requests_mock.post(
        "http://mock.url/Plan/validate",
        text=json.dumps(
            {
                "type": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/422",
                "title": "One or more validation errors occurred.",
                "status": 422,
                "detail": "Validation failed: \r\n -- Type: Geometry coordinates do not match with geometry type. Severity: Error",
                "errors": [
                    {
                        "ruleId": mock_rule,
                        "message": mock_error_string,
                        "instance": mock_instance,
                    }
                ],
                "warnings": [],
                "traceId": "00-f5288710d1eb2265175052028d4b77c4-6ed94a9caece4333-00",
            }
        ),
        status_code=422,
    )


@pytest.fixture
def mock_public_ryhti_validate_valid(requests_mock: Mocker) -> None:
    requests_mock.post(
        "http://mock.url/Plan/validate",
        json={
            "key": "string",
            "uri": "string",
            "warnings": [
                {
                    "ruleId": "string",
                    "message": "string",
                    "instance": "string",
                    "classKey": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                }
            ],
        },
        status_code=200,
    )


@pytest.fixture
def mock_public_map_document(requests_mock: Mocker) -> Generator[None]:
    path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "test_ryhti_client_plan_map.tif"
    )
    with open(path, "rb") as plan_map:
        requests_mock.get(
            "https://raw.githubusercontent.com/GeoTIFF/test-data/refs/heads/main/files/GeogToWGS84GeoKey5.tif",
            body=plan_map,
            headers={"Content-type": "image/tiff", "ETag": "same old file"},
            status_code=200,
        )
        requests_mock.head(
            "https://raw.githubusercontent.com/GeoTIFF/test-data/refs/heads/main/files/GeogToWGS84GeoKey5.tif",
            headers={"Content-type": "image/tiff", "ETag": "same old file"},
            status_code=200,
        )
        yield


@pytest.fixture
def mock_public_attachment_document(requests_mock: Mocker):
    path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "test_ryhti_client_plan_attachment.pdf",
    )
    with open(path, "rb") as plan_attachment:
        requests_mock.get(
            "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
            body=plan_attachment,
            headers={"Content-type": "application/pdf", "ETag": "same old file"},
            status_code=200,
        )
        requests_mock.head(
            "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
            headers={"Content-type": "application/pdf", "ETag": "same old file"},
            status_code=200,
        )
        yield


@pytest.fixture
def mock_xroad_ryhti_authenticate(requests_mock: Mocker) -> None:
    def match_request_body(request: _RequestObjectProxy) -> bool:
        # Oh great, looks like requests json method will not parse minimal json consisting of just string.
        # Instead, we'll have to match the request text.
        return request.text == '"test-secret"'

    requests_mock.post(
        "http://mock2.url:8080/r1/FI/GOV/0996189-5/Ryhti-Syke-Service/planService/api/Authenticate?clientId=test-id",
        json="test-token",
        request_headers={
            "X-Road-Client": "FI/COM/2455538-5/ryhti-gispo-client",
            "Accept": "application/json",
            "Content-type": "application/json",
        },
        additional_matcher=match_request_body,
        status_code=200,
    )


@pytest.fixture
def mock_xroad_ryhti_fileupload(requests_mock: Mocker) -> None:
    def match_request_body(request: PreparedRequest) -> bool:
        # Check that the file is uploaded:
        assert "multipart/form-data; boundary=" in request.headers["Content-Type"]
        return (
            b'Content-Disposition: form-data; name="file"; filename="GeogToWGS84GeoKey5.tif"'
            in cast("bytes", request.body)
        ) or (
            b'Content-Disposition: form-data; name="file"; filename="dummy.pdf"'
            in cast("bytes", request.body)
        )

    requests_mock.post(
        "http://mock2.url:8080/r1/FI/GOV/0996189-5/Ryhti-Syke-service/planService/api/File?regionId=01",
        # Return random file id
        json=str(uuid4()),
        request_headers={
            "X-Road-Client": "FI/COM/2455538-5/ryhti-gispo-client",
            "Authorization": "Bearer test-token",
            "Accept": "application/json",
        },
        additional_matcher=match_request_body,  # type: ignore[arg-type]  # _RequestObjectProxy doesn't have body defined
        status_code=201,
    )


@pytest.fixture
def mock_xroad_ryhti_permanentidentifier(requests_mock: Mocker) -> None:
    def match_request_body_with_correct_region(request: _RequestObjectProxy):
        return request.json()["administrativeAreaIdentifier"] == "01"

    requests_mock.post(
        "http://mock2.url:8080/r1/FI/GOV/0996189-5/Ryhti-Syke-Service/planService/api/RegionalPlanMatter/PermanentPlanIdentifier",
        json="MK-123456",
        request_headers={
            "X-Road-Client": "FI/COM/2455538-5/ryhti-gispo-client",
            "Authorization": "Bearer test-token",
            "Accept": "application/json",
            "Content-type": "application/json",
        },
        additional_matcher=match_request_body_with_correct_region,
        status_code=200,
    )

    def match_request_body_with_wrong_region(request: _RequestObjectProxy):
        return request.json()["administrativeAreaIdentifier"] == "02"

    requests_mock.post(
        "http://mock2.url:8080/r1/FI/GOV/0996189-5/Ryhti-Syke-Service/planService/api/RegionalPlanMatter/PermanentPlanIdentifier",
        json={
            "type": "https://httpstatuses.io/401",
            "title": "Unauthorized",
            "status": 401,
            "traceId": "00-82a0a8d02f7824c2dcda16e481f4d2e8-3797b905d05ed6c3-00",
        },
        request_headers={
            "X-Road-Client": "FI/COM/2455538-5/ryhti-gispo-client",
            "Authorization": "Bearer test-token",
            "Accept": "application/json",
            "Content-type": "application/json",
        },
        additional_matcher=match_request_body_with_wrong_region,
        status_code=401,
    )


@pytest.fixture
def mock_xroad_ryhti_validate_invalid(requests_mock: Mocker) -> None:
    requests_mock.post(
        "http://mock2.url:8080/r1/FI/GOV/0996189-5/Ryhti-Syke-Service/planService/api/RegionalPlanMatter/MK-123456/validate",
        json={
            "type": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/422",
            "title": "One or more validation errors occurred.",
            "status": 422,
            "detail": "Validation failed: \r\n -- Type: Geometry coordinates do not match with geometry type. Severity: Error",
            "errors": [
                {
                    "ruleId": mock_matter_rule,
                    "message": mock_matter_error_string,
                    "instance": mock_matter_instance,
                }
            ],
            "warnings": [],
            "traceId": "00-f5288710d1eb2265175052028d4b77c4-6ed94a9caece4333-00",
        },
        request_headers={
            "X-Road-Client": "FI/COM/2455538-5/ryhti-gispo-client",
            "Authorization": "Bearer test-token",
            "Accept": "application/json",
            "Content-type": "application/json",
        },
        status_code=422,
    )


@pytest.fixture
def mock_xroad_ryhti_validate_valid(requests_mock: Mocker) -> None:
    requests_mock.post(
        "http://mock2.url:8080/r1/FI/GOV/0996189-5/Ryhti-Syke-Service/planService/api/RegionalPlanMatter/MK-123456/validate",
        json={
            "key": "string",
            "uri": "string",
            "warnings": [
                {
                    "ruleId": "string",
                    "message": "string",
                    "instance": "string",
                    "classKey": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                }
            ],
        },
        request_headers={
            "X-Road-Client": "FI/COM/2455538-5/ryhti-gispo-client",
            "Authorization": "Bearer test-token",
            "Accept": "application/json",
            "Content-type": "application/json",
        },
        status_code=200,
    )


@pytest.fixture
def mock_xroad_ryhti_post_new_plan_matter(requests_mock: Mocker) -> None:
    requests_mock.get(
        "http://mock2.url:8080/r1/FI/GOV/0996189-5/Ryhti-Syke-service/planService/api/RegionalPlanMatter/MK-123456",
        request_headers={
            "X-Road-Client": "FI/COM/2455538-5/ryhti-gispo-client",
            "Authorization": "Bearer test-token",
            "Accept": "application/json",
            "Content-type": "application/json",
        },
        status_code=404,
    )
    requests_mock.post(
        "http://mock2.url:8080/r1/FI/GOV/0996189-5/Ryhti-Syke-service/planService/api/RegionalPlanMatter/MK-123456",
        json={
            "key": "string",
            "uri": "string",
            "warnings": [
                {
                    "ruleId": "string",
                    "message": "string",
                    "instance": "string",
                    "classKey": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                }
            ],
        },
        request_headers={
            "X-Road-Client": "FI/COM/2455538-5/ryhti-gispo-client",
            "Authorization": "Bearer test-token",
            "Accept": "application/json",
            "Content-type": "application/json",
        },
        status_code=201,
    )


@pytest.fixture
def mock_xroad_ryhti_update_existing_plan_matter(
    requests_mock: Mocker, desired_plan_matter_dict
) -> None:
    # The plan matter exists
    requests_mock.get(
        "http://mock2.url:8080/r1/FI/GOV/0996189-5/Ryhti-Syke-service/planService/api/RegionalPlanMatter/MK-123456",
        json=desired_plan_matter_dict,
        json_encoder=cast(
            "type[StdJSONEncoder]", JSONEncoder
        ),  # We need simplejson to encode decimals!!
        request_headers={
            "X-Road-Client": "FI/COM/2455538-5/ryhti-gispo-client",
            "Authorization": "Bearer test-token",
            "Accept": "application/json",
            "Content-type": "application/json",
        },
        status_code=200,
    )
    # Existing phase may be updated.
    requests_mock.put(
        # *Only* path used by the existing phase is valid. Check that we use an existing path when updating a phase.
        "http://mock2.url:8080/r1/FI/GOV/0996189-5/Ryhti-Syke-service/planService/api/RegionalPlanMatter/MK-123456/phase/third_phase_test",
        json={
            "key": "string",
            "uri": "string",
            "warnings": [
                {
                    "ruleId": "string",
                    "message": "string",
                    "instance": "string",
                    "classKey": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                }
            ],
        },
        request_headers={
            "X-Road-Client": "FI/COM/2455538-5/ryhti-gispo-client",
            "Authorization": "Bearer test-token",
            "Accept": "application/json",
            "Content-type": "application/json",
        },
        # TODO: Currently, Ryhti responses with HTTP 201 to PUT requests. Change this back to
        # HTTP 200 when Ryhti API is fixed, or the API spec is updated:
        status_code=201,
    )
    # New phase may be created.
    requests_mock.post(
        # *Any* path that is *not* used by the existing phase is valid. Check that we don't use the
        # existing path when creating a new phase.
        re.compile(
            r"^http://mock2\.url:8080/r1/FI/GOV/0996189\-5/Ryhti\-Syke\-service/planService/api/RegionalPlanMatter/MK\-123456/phase/(?!third_phase_test).*$"
        ),
        json={
            "key": "string",
            "uri": "string",
            "warnings": [
                {
                    "ruleId": "string",
                    "message": "string",
                    "instance": "string",
                    "classKey": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                }
            ],
        },
        request_headers={
            "X-Road-Client": "FI/COM/2455538-5/ryhti-gispo-client",
            "Authorization": "Bearer test-token",
            "Accept": "application/json",
            "Content-type": "application/json",
        },
        status_code=201,
    )


@pytest.fixture
def client_with_plan_data(
    session: Session, rw_connection_string: str, complete_test_plan: models.Plan
) -> RyhtiClient:
    """Return RyhtiClient that has plan data read in and serialized.

    Plan data must exist in the database before we return the client, because the client
    reads plans from the database when initializing.
    """
    # Let's mock production x-road with gispo organization client here.
    database_client = DatabaseClient(rw_connection_string)
    client = RyhtiClient(
        database_client,
        public_api_url="http://mock.url",
        xroad_server_address="http://mock2.url",
        xroad_instance="FI",
        xroad_member_class="COM",
        xroad_member_code="2455538-5",
        xroad_member_client_name="ryhti-gispo-client",
        xroad_syke_client_id="test-id",
        xroad_syke_client_secret="test-secret",
    )

    return client


def test_related_land_use_area(
    complete_test_plan: models.Plan,
    land_use_area_instance: models.LandUseArea,
    other_area_instance: models.OtherArea,
    client_with_plan_data: RyhtiClient,
) -> None:
    """Test that the land use area that contains the other area of type 'rakennusala'
    is added to the related plan objects list.
    """
    plan_dict = client_with_plan_data.database_client.plan_dictionaries[
        complete_test_plan.id
    ]
    other_area_in_dict = next(
        (
            plan_object
            for plan_object in plan_dict["planObjects"]
            if plan_object["planObjectKey"] == other_area_instance.id
        ),
        None,
    )

    assert other_area_in_dict

    assert other_area_in_dict["relatedPlanObjectKeys"] == [land_use_area_instance.id]


@pytest.fixture
def client_with_plan_data_in_wrong_region(
    session: Session,
    rw_connection_string: str,
    complete_test_plan: models.Plan,
    another_organisation_instance: models.Organisation,
) -> RyhtiClient:
    """Return RyhtiClient that has plan data in the wrong region read in.

    We have to create the plan data in the database before returning the client, because the client
    reads plans from the database when initializing.
    """
    # Client will cache plan phase when it is initialized, so we have to make
    # sure to update the plan owner in the database *before* that.
    session.add(complete_test_plan)
    complete_test_plan.organisation = another_organisation_instance
    session.commit()

    # Let's mock production x-road with gispo organization client here.
    database_client = DatabaseClient(rw_connection_string)
    client = RyhtiClient(
        database_client=database_client,
        public_api_url="http://mock.url",
        xroad_server_address="http://mock2.url",
        xroad_instance="FI",
        xroad_member_class="COM",
        xroad_member_code="2455538-5",
        xroad_member_client_name="ryhti-gispo-client",
        xroad_syke_client_id="test-id",
        xroad_syke_client_secret="test-secret",
    )

    return client


@pytest.fixture
def client_with_plan_data_in_proposal_phase(
    session: Session,
    rw_connection_string: str,
    complete_test_plan: models.Plan,
    plan_proposal_status_instance: codes.LifeCycleStatus,
    plan_proposal_date_instance: models.LifeCycleDate,
) -> RyhtiClient:
    """Return RyhtiClient that has plan data in proposal phase read in.

    We have to create the plan data in the database before returning the client, because the client
    reads plans from the database when initializing.
    """
    # Client will cache plan phase when it is initialized, so we have to make
    # sure to update the plan phase in the database *before* that.
    session.add(complete_test_plan)
    session.add(plan_proposal_status_instance)
    complete_test_plan.lifecycle_status = plan_proposal_status_instance
    session.commit()
    # Delete the new additional date for proposal phase that just appeared. Our fixture already
    # has a proposal date.
    session.refresh(complete_test_plan)
    session.delete(complete_test_plan.lifecycle_dates[2])
    session.commit()

    # Let's mock production x-road with gispo organization client here.
    database_client = DatabaseClient(rw_connection_string)
    client = RyhtiClient(
        database_client=database_client,
        public_api_url="http://mock.url",
        xroad_server_address="http://mock2.url",
        xroad_instance="FI",
        xroad_member_class="COM",
        xroad_member_code="2455538-5",
        xroad_member_client_name="ryhti-gispo-client",
        xroad_syke_client_id="test-id",
        xroad_syke_client_secret="test-secret",
    )

    return client


def test_get_plan_dictionaries(
    client_with_plan_data: RyhtiClient,
    plan_instance: models.Plan,
    desired_plan_dict: dict,
) -> None:
    """Check that correct JSON structure is generated when client is initialized."""
    result_plan_dict = client_with_plan_data.database_client.plan_dictionaries[
        plan_instance.id
    ]
    deepcompare(
        result_plan_dict,
        desired_plan_dict,
        ignore_order_for_keys=[
            "planRegulationGroupRelations",
            "additionalInformations",
        ],
    )


def test_validate_plans(
    client_with_plan_data: RyhtiClient,
    plan_instance: models.Plan,
    mock_public_ryhti_validate_invalid: Callable,
) -> None:
    """Check that JSON is posted and response received"""
    responses = client_with_plan_data.validate_plans()
    for plan_id, response in responses.items():
        assert plan_id == plan_instance.id
        assert response["errors"] == [
            {
                "ruleId": mock_rule,
                "message": mock_error_string,
                "instance": mock_instance,
            }
        ]


def test_save_plan_validation_responses(
    session: Session,
    client_with_plan_data: RyhtiClient,
    plan_instance: models.Plan,
    mock_public_ryhti_validate_invalid: Callable,
) -> None:
    """Check that Ryhti validation error is saved to database."""
    responses = client_with_plan_data.validate_plans()
    message = client_with_plan_data.database_client.save_plan_validation_responses(
        responses
    )
    session.refresh(plan_instance)
    assert plan_instance.validated_at
    assert plan_instance.validation_errors == next(iter(responses.values()))["errors"]


def test_authenticate_to_xroad_ryhti_api(
    session: Session,
    client_with_plan_data: RyhtiClient,
    mock_xroad_ryhti_authenticate: Callable,
) -> None:
    """Test authenticating to mock X-Road Ryhti API."""
    client_with_plan_data.xroad_ryhti_authenticate()
    assert client_with_plan_data.xroad_headers["Authorization"] == "Bearer test-token"


@pytest.fixture
def authenticated_client_with_plan(
    session: Session,
    client_with_plan_data: RyhtiClient,
    mock_xroad_ryhti_authenticate: Callable,
):
    """Return RyhtiClient that has plan data read in and that is authenticated to our
    mock X-Road API.
    """
    client_with_plan_data.xroad_ryhti_authenticate()
    assert client_with_plan_data.xroad_headers["Authorization"] == "Bearer test-token"
    return client_with_plan_data


@pytest.fixture
def authenticated_client_with_plan_in_proposal_phase(
    session: Session,
    client_with_plan_data_in_proposal_phase: RyhtiClient,
    mock_xroad_ryhti_authenticate: Callable,
):
    """Return RyhtiClient that has plan data in the wrong region read in and that is
    authenticated to our mock X-Road API.
    """
    client_with_plan_data_in_proposal_phase.xroad_ryhti_authenticate()
    assert (
        client_with_plan_data_in_proposal_phase.xroad_headers["Authorization"]
        == "Bearer test-token"
    )
    return client_with_plan_data_in_proposal_phase


@pytest.fixture
def authenticated_client_with_plan_in_wrong_region(
    session: Session,
    client_with_plan_data_in_wrong_region: RyhtiClient,
    mock_xroad_ryhti_authenticate: Callable,
):
    """Return RyhtiClient that has plan data in the wrong region read in and that is
    authenticated to our mock X-Road API.
    """
    client_with_plan_data_in_wrong_region.xroad_ryhti_authenticate()
    assert (
        client_with_plan_data_in_wrong_region.xroad_headers["Authorization"]
        == "Bearer test-token"
    )
    return client_with_plan_data_in_wrong_region


def test_set_permanent_plan_identifiers_in_wrong_region(
    session: Session,
    authenticated_client_with_plan_in_wrong_region: RyhtiClient,
    plan_instance: models.Plan,
    another_organisation_instance: models.Organisation,
    mock_xroad_ryhti_permanentidentifier: Callable,
) -> None:
    """Check that Ryhti permanent plan identifier is left empty, if Ryhti API reports that
    the organization has no permission to create plans in the region.
    """
    id_responses = (
        authenticated_client_with_plan_in_wrong_region.get_permanent_plan_identifiers()
    )
    message = authenticated_client_with_plan_in_wrong_region.database_client.set_permanent_plan_identifiers(
        id_responses
    )
    session.refresh(plan_instance)
    assert plan_instance.organisation is another_organisation_instance
    assert not plan_instance.permanent_plan_identifier
    assert (
        message[plan_instance.id]
        == "Sinulla ei ole oikeuksia luoda kaavaa tälle alueelle."
    )


def test_set_permanent_plan_identifiers(
    session: Session,
    authenticated_client_with_plan: RyhtiClient,
    plan_instance: models.Plan,
    mock_xroad_ryhti_permanentidentifier: Callable,
) -> None:
    """Check that Ryhti permanent plan identifier is received and saved to the database, if
    Ryhti API returns a permanent plan identifier.
    """
    id_responses = authenticated_client_with_plan.get_permanent_plan_identifiers()
    message = (
        authenticated_client_with_plan.database_client.set_permanent_plan_identifiers(
            id_responses
        )
    )
    session.refresh(plan_instance)
    received_plan_identifier = next(iter(id_responses.values()))["detail"]
    assert plan_instance.permanent_plan_identifier
    assert plan_instance.permanent_plan_identifier == received_plan_identifier
    assert message[plan_instance.id] == received_plan_identifier


@pytest.fixture
def client_with_plan_with_permanent_identifier(
    session: Session,
    authenticated_client_with_plan: RyhtiClient,
    plan_instance: models.Plan,
    mock_xroad_ryhti_permanentidentifier: Callable,
) -> RyhtiClient:
    """Return RyhtiClient that has plan data read in and its permanent
    identifier set.
    """
    id_responses = authenticated_client_with_plan.get_permanent_plan_identifiers()
    authenticated_client_with_plan.database_client.set_permanent_plan_identifiers(
        id_responses
    )
    session.refresh(plan_instance)
    received_plan_identifier = next(iter(id_responses.values()))["detail"]
    assert plan_instance.permanent_plan_identifier
    assert plan_instance.permanent_plan_identifier == received_plan_identifier
    return authenticated_client_with_plan


@pytest.fixture
def client_with_plan_with_permanent_identifier_in_proposal_phase(
    session: Session,
    authenticated_client_with_plan_in_proposal_phase: RyhtiClient,
    plan_instance: models.Plan,
    mock_xroad_ryhti_permanentidentifier: Callable,
) -> RyhtiClient:
    """Return RyhtiClient that has plan data in proposal phase read in and
    its permanent identifier set.
    """
    id_responses = authenticated_client_with_plan_in_proposal_phase.get_permanent_plan_identifiers()
    authenticated_client_with_plan_in_proposal_phase.database_client.set_permanent_plan_identifiers(
        id_responses
    )
    session.refresh(plan_instance)
    received_plan_identifier = next(iter(id_responses.values()))["detail"]
    assert plan_instance.permanent_plan_identifier
    assert plan_instance.permanent_plan_identifier == received_plan_identifier
    return authenticated_client_with_plan_in_proposal_phase


def test_upload_plan_documents(
    session: Session,
    client_with_plan_with_permanent_identifier: RyhtiClient,
    plan_instance: models.Plan,
    mock_public_attachment_document: Callable,
    mock_public_map_document: Callable,
    mock_xroad_ryhti_fileupload: Callable,
) -> None:
    """Check that plan documents are uploaded. This does not require plan to be valid,
    but we only upload documents for plans that have permanent identifiers.
    """
    responses = client_with_plan_with_permanent_identifier.upload_plan_documents()
    for plan_id, document_responses in responses.items():
        assert plan_id == plan_instance.id
        for document_response in document_responses:
            assert document_response["status"] == 201
            assert not document_response["errors"]
            assert document_response["detail"]


def test_set_plan_documents(
    session: Session,
    client_with_plan_with_permanent_identifier: RyhtiClient,
    plan_instance: models.Plan,
    mock_public_attachment_document: Callable,
    mock_public_map_document: Callable,
    mock_xroad_ryhti_fileupload: Callable,
) -> None:
    """Check that uploaded document ids are saved to the database. This does not
    require plan to be valid, but we only upload documents for plans that have
    permanent identifiers.
    """
    responses = client_with_plan_with_permanent_identifier.upload_plan_documents()
    client_with_plan_with_permanent_identifier.database_client.set_plan_documents(
        responses
    )
    session.refresh(plan_instance.documents[0])
    assert plan_instance.documents[0].exported_at
    assert plan_instance.documents[0].exported_file_key
    assert plan_instance.documents[0].exported_file_etag


@pytest.fixture
def client_with_plan_with_permanent_identifier_and_documents(
    session: Session,
    client_with_plan_with_permanent_identifier: RyhtiClient,
    plan_instance: models.Plan,
    mock_public_attachment_document: Callable,
    mock_public_map_document: Callable,
    mock_xroad_ryhti_fileupload: Callable,
) -> RyhtiClient:
    """Returns Ryhti client that has plan data in proposal phase read in, that is
    authenticated to our mock X-Road API, and that has plan documents uploaded.
    """
    responses = client_with_plan_with_permanent_identifier.upload_plan_documents()
    for plan_id, document_responses in responses.items():
        assert plan_id == plan_instance.id
        for document_response in document_responses:
            assert document_response["status"] == 201
            assert not document_response["errors"]
            assert document_response["detail"]
    client_with_plan_with_permanent_identifier.database_client.set_plan_documents(
        responses
    )
    session.refresh(plan_instance.documents[0])
    assert plan_instance.documents[0].exported_at
    assert plan_instance.documents[0].exported_file_key
    return client_with_plan_with_permanent_identifier


@pytest.fixture
def client_with_plan_with_permanent_identifier_and_documents_in_proposal_phase(
    session: Session,
    client_with_plan_with_permanent_identifier_in_proposal_phase: RyhtiClient,
    plan_instance: models.Plan,
    mock_public_attachment_document: Callable,
    mock_public_map_document: Callable,
    mock_xroad_ryhti_fileupload: Callable,
) -> RyhtiClient:
    """Returns Ryhti client that has plan data in proposal phase read in, that is
    authenticated to our mock X-Road API, and that has plan documents uploaded.
    """
    responses = client_with_plan_with_permanent_identifier_in_proposal_phase.upload_plan_documents()
    for plan_id, document_responses in responses.items():
        assert plan_id == plan_instance.id
        for document_response in document_responses:
            assert document_response["status"] == 201
            assert not document_response["errors"]
            assert document_response["detail"]
    client_with_plan_with_permanent_identifier_in_proposal_phase.database_client.set_plan_documents(
        responses
    )
    session.refresh(plan_instance.documents[0])
    assert plan_instance.documents[0].exported_at
    assert plan_instance.documents[0].exported_file_key
    return client_with_plan_with_permanent_identifier_in_proposal_phase


def test_upload_unchanged_plan_documents(
    session: Session,
    client_with_plan_with_permanent_identifier_and_documents: RyhtiClient,
    plan_instance: models.Plan,
    mock_public_attachment_document: Callable,
    mock_public_map_document: Callable,
    mock_xroad_ryhti_fileupload: Callable,
) -> None:
    """Check that unchanged plan documents are not uploaded."""
    old_exported_at = plan_instance.documents[0].exported_at
    old_file_key = plan_instance.documents[0].exported_file_key
    old_file_etag = plan_instance.documents[0].exported_file_etag
    assert old_exported_at
    assert old_file_key
    assert old_file_etag
    reupload_responses = (
        client_with_plan_with_permanent_identifier_and_documents.upload_plan_documents()
    )
    for plan_id, document_responses in reupload_responses.items():
        assert plan_id == plan_instance.id
        for document_response in document_responses:
            assert plan_id == plan_instance.id
            assert document_response["status"] is None
            assert document_response["detail"] == "File unchanged since last upload."
    client_with_plan_with_permanent_identifier_and_documents.database_client.set_plan_documents(
        reupload_responses
    )
    session.refresh(plan_instance.documents[0])
    assert plan_instance.documents[0].exported_at == old_exported_at
    assert plan_instance.documents[0].exported_file_key == old_file_key
    assert plan_instance.documents[0].exported_file_etag == old_file_etag


def test_get_plan_matters(
    client_with_plan_with_permanent_identifier_and_documents: RyhtiClient,
    plan_instance: models.Plan,
    desired_plan_matter_dict: dict,
) -> None:
    """Check that correct JSON structure is generated for plan matter. This requires that
    the client has already fetched a permanent identifer for the plan.
    """
    plan_matter_dictionaries = client_with_plan_with_permanent_identifier_and_documents.database_client.get_plan_matters()
    plan_matter = plan_matter_dictionaries[plan_instance.id]
    deepcompare(
        plan_matter,
        desired_plan_matter_dict,
        ignore_keys=[
            "planMatterPhaseKey",
            "handlingEventKey",
            "interactionEventKey",
            "planDecisionKey",
            "planMapKey",
            "attachmentDocumentKey",
            "planReportKey",
            "otherPlanMaterialKey",
            "fileKey",
        ],
        ignore_order_for_keys=[
            "planRegulationGroupRelations",
            "additionalInformations",
        ],
    )


def test_validate_plan_matters(
    client_with_plan_with_permanent_identifier_and_documents: RyhtiClient,
    plan_instance: models.Plan,
    mock_xroad_ryhti_validate_invalid: Callable,
) -> None:
    """Check that JSON is posted and response received"""
    responses = (
        client_with_plan_with_permanent_identifier_and_documents.validate_plan_matters()
    )
    for plan_id, response in responses.items():
        assert plan_id == plan_instance.id
        assert response["errors"] == [
            {
                "ruleId": mock_matter_rule,
                "message": mock_matter_error_string,
                "instance": mock_matter_instance,
            }
        ]


def test_save_plan_matter_validation_responses(
    session: Session,
    client_with_plan_with_permanent_identifier_and_documents: RyhtiClient,
    plan_instance: models.Plan,
    mock_xroad_ryhti_validate_invalid: Callable,
) -> None:
    """Check that Ryhti X-Road validation error is saved to database."""
    responses = (
        client_with_plan_with_permanent_identifier_and_documents.validate_plan_matters()
    )
    message = client_with_plan_with_permanent_identifier_and_documents.database_client.save_plan_matter_validation_responses(
        responses
    )
    session.refresh(plan_instance)
    assert plan_instance.validated_at
    assert plan_instance.validation_errors == next(iter(responses.values()))["errors"]


def test_post_new_plan_matters(
    client_with_plan_with_permanent_identifier_and_documents: RyhtiClient,
    plan_instance: models.Plan,
    mock_xroad_ryhti_post_new_plan_matter: Callable,
) -> None:
    """Check that JSON is posted and response received when the plan matter does not
    exist in Ryhti yet.
    """
    responses = (
        client_with_plan_with_permanent_identifier_and_documents.post_plan_matters()
    )
    for plan_id, response in responses.items():
        assert plan_id == plan_instance.id
        assert response["warnings"]
        assert not response["errors"]


def test_save_new_plan_matter_post_responses(
    session: Session,
    client_with_plan_with_permanent_identifier_and_documents: RyhtiClient,
    plan_instance: models.Plan,
    mock_xroad_ryhti_post_new_plan_matter: Callable,
) -> None:
    """Check that export time is saved to database."""
    responses = (
        client_with_plan_with_permanent_identifier_and_documents.post_plan_matters()
    )
    message = client_with_plan_with_permanent_identifier_and_documents.database_client.save_plan_matter_post_responses(
        responses
    )
    session.refresh(plan_instance)
    assert plan_instance.exported_at
    assert plan_instance.validation_errors == "Uusi kaava-asian vaihe on viety Ryhtiin."


def test_update_existing_plan_matters(
    session: Session,
    client_with_plan_with_permanent_identifier_and_documents_in_proposal_phase: RyhtiClient,
    plan_instance: models.Plan,
    mock_xroad_ryhti_update_existing_plan_matter: Callable,
) -> None:
    """Check that JSON is posted and response received when the plan matter exists in Ryhti
    and a new plan matter phase must be posted.
    """
    responses = client_with_plan_with_permanent_identifier_and_documents_in_proposal_phase.post_plan_matters()
    for plan_id, response in responses.items():
        assert plan_id == plan_instance.id
        assert response["warnings"]
        assert not response["errors"]


def test_save_update_existing_matter_post_responses(
    session: Session,
    client_with_plan_with_permanent_identifier_and_documents_in_proposal_phase: RyhtiClient,
    plan_instance: models.Plan,
    mock_xroad_ryhti_update_existing_plan_matter: Callable,
) -> None:
    """Check that export time is saved to database."""
    responses = client_with_plan_with_permanent_identifier_and_documents_in_proposal_phase.post_plan_matters()
    message = client_with_plan_with_permanent_identifier_and_documents_in_proposal_phase.database_client.save_plan_matter_post_responses(
        responses
    )
    session.refresh(plan_instance)
    assert plan_instance.exported_at
    assert plan_instance.validation_errors == "Uusi kaava-asian vaihe on viety Ryhtiin."


def test_update_existing_plan_matter_phase(
    session: Session,
    client_with_plan_with_permanent_identifier_and_documents: RyhtiClient,
    plan_instance: models.Plan,
    mock_xroad_ryhti_update_existing_plan_matter: Callable,
) -> None:
    """Check that JSON is posted and response received when the plan matter and the plan matter
    phase exist in Ryhti and the plan matter phase must be updated.
    """
    responses = (
        client_with_plan_with_permanent_identifier_and_documents.post_plan_matters()
    )
    for plan_id, response in responses.items():
        assert plan_id == plan_instance.id
        assert response["warnings"]
        assert not response["errors"]


def test_save_update_existing_matter_phase_post_responses(
    session: Session,
    client_with_plan_with_permanent_identifier_and_documents: RyhtiClient,
    plan_instance: models.Plan,
    mock_xroad_ryhti_update_existing_plan_matter: Callable,
) -> None:
    """Check that export time is saved to database."""
    responses = (
        client_with_plan_with_permanent_identifier_and_documents.post_plan_matters()
    )
    message = client_with_plan_with_permanent_identifier_and_documents.database_client.save_plan_matter_post_responses(
        responses
    )
    session.refresh(plan_instance)
    assert plan_instance.exported_at
    # TODO: switch to using correct message once Ryhti responds correctly. Currently, Ryhti
    # claims a new phase is created every time the existing phase is updated.
    # assert plan_instance.validation_errors == "Kaava-asian vaihe on päivitetty Ryhtiin."
    assert plan_instance.validation_errors == "Uusi kaava-asian vaihe on viety Ryhtiin."
