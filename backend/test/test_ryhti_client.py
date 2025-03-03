import json
import os
import re
from typing import Callable
from uuid import uuid4

import pytest
from requests_mock.request import _RequestObjectProxy
from simplejson import JSONEncoder
from sqlalchemy.orm import Session

from database import codes, models
from lambdas.ryhti_client.ryhti_client import RyhtiClient

from .conftest import deepcompare

mock_rule = "random_rule"
mock_matter_rule = "another_random_rule"
mock_error_string = "There is something wrong with your plan! Good luck!"
mock_matter_error_string = (
    "There is something wrong with your plan matter as well! Have fun!"
)
mock_instance = "some field in your plan"
mock_matter_instance = "some field in your plan matter"


@pytest.fixture()
def mock_public_ryhti_validate_invalid(requests_mock) -> None:
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


@pytest.fixture()
def mock_public_ryhti_validate_valid(requests_mock) -> None:
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


@pytest.fixture()
def mock_public_map_document(requests_mock):
    path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "test_ryhti_client_plan_map.tif"
    )
    with open(path, "rb") as plan_map:
        requests_mock.get(
            "https://raw.githubusercontent.com/GeoTIFF/test-data/refs/heads/main/files/GeogToWGS84GeoKey5.tif",
            body=plan_map,
            headers={
                "Content-type": "image/tiff",
                "Last-Modified": "Mon, 01 Jan 2024 00:00:00 GMT",
            },
            status_code=200,
        )
        requests_mock.head(
            "https://raw.githubusercontent.com/GeoTIFF/test-data/refs/heads/main/files/GeogToWGS84GeoKey5.tif",
            headers={
                "Content-type": "image/tiff",
                "Last-Modified": "Mon, 01 Jan 2024 00:00:00 GMT",
            },
            status_code=200,
        )
        yield


@pytest.fixture()
def mock_xroad_ryhti_authenticate(requests_mock) -> None:
    def match_request_body(request: _RequestObjectProxy):
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


@pytest.fixture()
def mock_xroad_ryhti_fileupload(requests_mock) -> None:
    def match_request_body(request: _RequestObjectProxy):
        # Check that the file is uploaded:
        return (
            b'Content-Disposition: form-data; name="file"; filename="GeogToWGS84GeoKey5.tif"'
            in request.body
        )

    requests_mock.post(
        "http://mock2.url:8080/r1/FI/GOV/0996189-5/Ryhti-Syke-service/planService/api/File?regionId=01",
        # Return random file id
        json=str(uuid4()),
        request_headers={
            "X-Road-Client": "FI/COM/2455538-5/ryhti-gispo-client",
            "Authorization": "Bearer test-token",
            "Accept": "application/json",
            "Content-type": "multipart/form-data",
        },
        additional_matcher=match_request_body,
        status_code=201,
    )


@pytest.fixture()
def mock_xroad_ryhti_permanentidentifier(requests_mock) -> None:
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


@pytest.fixture()
def mock_xroad_ryhti_validate_invalid(requests_mock) -> None:
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


@pytest.fixture()
def mock_xroad_ryhti_validate_valid(requests_mock) -> None:
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


@pytest.fixture()
def mock_xroad_ryhti_post_new_plan_matter(requests_mock) -> None:
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


@pytest.fixture()
def mock_xroad_ryhti_update_existing_plan_matter(
    requests_mock, desired_plan_matter_dict
) -> None:
    # The plan matter exists
    requests_mock.get(
        "http://mock2.url:8080/r1/FI/GOV/0996189-5/Ryhti-Syke-service/planService/api/RegionalPlanMatter/MK-123456",
        json=desired_plan_matter_dict,
        json_encoder=JSONEncoder,  # We need simplejson to encode decimals!!
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
        status_code=200,
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


@pytest.fixture(scope="function")
def ryhti_client(session: Session, rw_connection_string: str) -> RyhtiClient:
    """
    Return RyhtiClient that has plan data read in.

    We have to create the plan data in the database before returning the client, because the client
    reads plans from the database when initializing. Also, let's cache plan dictionaries in the
    client like done in handler method, so all methods depending on data being serialized already
    will work as expected.
    """
    # Let's mock production x-road with gispo organization client here.
    client = RyhtiClient(
        rw_connection_string,
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


@pytest.fixture(scope="function")
def client_with_plan_data(
    session: Session, rw_connection_string: str, complete_test_plan: models.Plan
) -> RyhtiClient:
    """
    Return RyhtiClient that has plan data read in.

    We have to create the plan data in the database before returning the client, because the client
    reads plans from the database when initializing. Also, let's cache plan dictionaries in the
    client like done in handler method, so all methods depending on data being serialized already
    will work as expected.
    """
    # Let's mock production x-road with gispo organization client here.
    client = RyhtiClient(
        rw_connection_string,
        public_api_url="http://mock.url",
        xroad_server_address="http://mock2.url",
        xroad_instance="FI",
        xroad_member_class="COM",
        xroad_member_code="2455538-5",
        xroad_member_client_name="ryhti-gispo-client",
        xroad_syke_client_id="test-id",
        xroad_syke_client_secret="test-secret",
    )
    client.plan_dictionaries = client.get_plan_dictionaries()
    return client


@pytest.fixture(scope="function")
def client_with_plan_data_in_proposal_phase(
    session: Session,
    rw_connection_string: str,
    complete_test_plan: models.Plan,
    plan_proposal_status_instance: codes.LifeCycleStatus,
    plan_proposal_date_instance: models.LifeCycleDate,
) -> RyhtiClient:
    """
    Return RyhtiClient that has plan data in proposal phase read in.

    We have to create the plan data in the database before returning the client, because the client
    reads plans from the database when initializing. Also, let's cache plan dictionaries in the
    client like done in handler method, so all methods depending on data being serialized already
    will work as expected.
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
    client = RyhtiClient(
        rw_connection_string,
        public_api_url="http://mock.url",
        xroad_server_address="http://mock2.url",
        xroad_instance="FI",
        xroad_member_class="COM",
        xroad_member_code="2455538-5",
        xroad_member_client_name="ryhti-gispo-client",
        xroad_syke_client_id="test-id",
        xroad_syke_client_secret="test-secret",
    )
    client.plan_dictionaries = client.get_plan_dictionaries()
    return client


def test_get_plan_dictionaries(
    client_with_plan_data: RyhtiClient,
    plan_instance: models.Plan,
    desired_plan_dict: dict,
):
    """
    Check that correct JSON structure is generated
    """
    result_plan_dict = client_with_plan_data.plan_dictionaries[plan_instance.id]
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
):
    """
    Check that JSON is posted and response received
    """
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
):
    """
    Check that Ryhti validation error is saved to database.
    """
    responses = client_with_plan_data.validate_plans()
    message = client_with_plan_data.save_plan_validation_responses(responses)
    session.refresh(plan_instance)
    assert plan_instance.validated_at
    assert plan_instance.validation_errors == next(iter(responses.values()))["errors"]


def test_authenticate_to_xroad_ryhti_api(
    session: Session,
    client_with_plan_data: RyhtiClient,
    mock_xroad_ryhti_authenticate: Callable,
):
    """
    Test authenticating to mock X-Road Ryhti API.
    """
    client_with_plan_data.xroad_ryhti_authenticate()
    assert client_with_plan_data.xroad_headers["Authorization"] == "Bearer test-token"


@pytest.fixture()
def authenticated_client_with_valid_plan(
    session: Session,
    client_with_plan_data: RyhtiClient,
    plan_instance: models.Plan,
    mock_public_ryhti_validate_valid: Callable,
    mock_xroad_ryhti_authenticate: Callable,
) -> RyhtiClient:
    """
    Return RyhtiClient that has plan data read in and validated without errors, and
    that is authenticated to our mock X-Road API.
    """
    responses = client_with_plan_data.validate_plans()
    client_with_plan_data.save_plan_validation_responses(responses)
    session.refresh(plan_instance)
    assert plan_instance.validated_at
    assert (
        plan_instance.validation_errors
        == "Kaava on validi. Kaava-asiaa ei ole vielä validoitu."
    )
    client_with_plan_data.xroad_ryhti_authenticate()
    assert client_with_plan_data.xroad_headers["Authorization"] == "Bearer test-token"
    return client_with_plan_data


@pytest.fixture()
def authenticated_client_with_valid_plan_in_wrong_region(
    session: Session,
    client_with_plan_data: RyhtiClient,
    plan_instance: models.Plan,
    organisation_instance: models.Organisation,
    another_organisation_instance: models.Organisation,
    mock_public_ryhti_validate_valid: Callable,
    mock_xroad_ryhti_authenticate: Callable,
) -> RyhtiClient:
    """
    Return RyhtiClient that has plan data in the wrong region read in and validated
    without errors, and that is authenticated to our mock X-Road API.
    """
    plan_instance.organisation = another_organisation_instance
    session.commit()

    responses = client_with_plan_data.validate_plans()
    client_with_plan_data.save_plan_validation_responses(responses)
    session.refresh(plan_instance)
    assert plan_instance.validated_at
    assert (
        plan_instance.validation_errors
        == "Kaava on validi. Kaava-asiaa ei ole vielä validoitu."
    )
    client_with_plan_data.xroad_ryhti_authenticate()
    assert client_with_plan_data.xroad_headers["Authorization"] == "Bearer test-token"
    return client_with_plan_data


@pytest.fixture()
def authenticated_client_with_valid_plan_in_proposal_phase(
    session: Session,
    client_with_plan_data_in_proposal_phase: RyhtiClient,
    plan_instance: models.Plan,
    mock_public_ryhti_validate_valid: Callable,
    mock_xroad_ryhti_authenticate: Callable,
) -> RyhtiClient:
    """
    Return RyhtiClient that has plan data in proposal phase read in and validated
    without errors, and that is authenticated to our mock X-Road API.
    """
    responses = client_with_plan_data_in_proposal_phase.validate_plans()
    client_with_plan_data_in_proposal_phase.save_plan_validation_responses(responses)
    session.refresh(plan_instance)
    assert plan_instance.validated_at
    assert (
        plan_instance.validation_errors
        == "Kaava on validi. Kaava-asiaa ei ole vielä validoitu."
    )
    client_with_plan_data_in_proposal_phase.xroad_ryhti_authenticate()
    assert (
        client_with_plan_data_in_proposal_phase.xroad_headers["Authorization"]
        == "Bearer test-token"
    )
    return client_with_plan_data_in_proposal_phase


def test_upload_plan_documents(
    session: Session,
    authenticated_client_with_valid_plan: RyhtiClient,
    plan_instance: models.Plan,
    mock_public_map_document: Callable,
    mock_xroad_ryhti_fileupload: Callable,
):
    """
    Check that plan documents are uploaded.
    """
    responses = authenticated_client_with_valid_plan.upload_plan_documents()
    for plan_id, document_responses in responses.items():
        assert plan_id == plan_instance.id
        for document_response in document_responses:
            assert document_response["status"] == 201
            assert not document_response["errors"]
            assert document_response["detail"]


def test_set_plan_documents(
    session: Session,
    authenticated_client_with_valid_plan: RyhtiClient,
    plan_instance: models.Plan,
    mock_public_map_document: Callable,
    mock_xroad_ryhti_fileupload: Callable,
):
    """
    Check that uploaded document ids are saved to the database.
    """
    responses = authenticated_client_with_valid_plan.upload_plan_documents()
    authenticated_client_with_valid_plan.set_plan_documents(responses)
    session.refresh(plan_instance.documents[0])
    assert plan_instance.documents[0].exported_at
    assert plan_instance.documents[0].exported_file_key


@pytest.fixture()
def authenticated_client_with_valid_plan_and_document(
    session: Session,
    authenticated_client_with_valid_plan: RyhtiClient,
    plan_instance: models.Plan,
    mock_public_map_document: Callable,
    mock_xroad_ryhti_fileupload: Callable,
) -> RyhtiClient:
    """
    Returns Ryhti client that has plan data read in and validated
    without errors, that is authenticated to our mock X-Road API, and that has plan
    document uploaded.
    """
    responses = authenticated_client_with_valid_plan.upload_plan_documents()
    for plan_id, document_responses in responses.items():
        assert plan_id == plan_instance.id
        for document_response in document_responses:
            assert document_response["status"] == 201
            assert not document_response["errors"]
            assert document_response["detail"]
    authenticated_client_with_valid_plan.set_plan_documents(responses)
    session.refresh(plan_instance.documents[0])
    assert plan_instance.documents[0].exported_at
    assert plan_instance.documents[0].exported_file_key
    return authenticated_client_with_valid_plan


@pytest.fixture()
def authenticated_client_with_valid_plan_and_document_in_proposal_phase(
    session: Session,
    authenticated_client_with_valid_plan_in_proposal_phase: RyhtiClient,
    plan_instance: models.Plan,
    mock_public_map_document: Callable,
    mock_xroad_ryhti_fileupload: Callable,
) -> RyhtiClient:
    """
    Returns Ryhti client that has plan data in proposal phase read in and validated
    without errors, that is authenticated to our mock X-Road API, and that has plan
    document uploaded.
    """
    responses = (
        authenticated_client_with_valid_plan_in_proposal_phase.upload_plan_documents()
    )
    for plan_id, document_responses in responses.items():
        assert plan_id == plan_instance.id
        for document_response in document_responses:
            assert document_response["status"] == 201
            assert not document_response["errors"]
            assert document_response["detail"]
    authenticated_client_with_valid_plan_in_proposal_phase.set_plan_documents(responses)
    session.refresh(plan_instance.documents[0])
    assert plan_instance.documents[0].exported_at
    assert plan_instance.documents[0].exported_file_key
    return authenticated_client_with_valid_plan_in_proposal_phase


def test_upload_unchanged_plan_documents(
    session: Session,
    authenticated_client_with_valid_plan_and_document: RyhtiClient,
    plan_instance: models.Plan,
    mock_public_map_document: Callable,
    mock_xroad_ryhti_fileupload: Callable,
):
    """
    Check that unchanged plan documents are not uploaded.
    """
    old_exported_at = plan_instance.documents[0].exported_at
    old_file_key = plan_instance.documents[0].exported_file_key
    reupload_responses = (
        authenticated_client_with_valid_plan_and_document.upload_plan_documents()
    )
    for plan_id, document_responses in reupload_responses.items():
        assert plan_id == plan_instance.id
        for document_response in document_responses:
            assert plan_id == plan_instance.id
            assert document_response["status"] is None
            assert document_response["detail"] == "File unchanged since last upload."
    authenticated_client_with_valid_plan_and_document.set_plan_documents(
        reupload_responses
    )
    session.refresh(plan_instance.documents[0])
    assert plan_instance.documents[0].exported_at == old_exported_at
    assert plan_instance.documents[0].exported_file_key == old_file_key


def test_set_permanent_plan_identifiers_in_wrong_region(
    session: Session,
    authenticated_client_with_valid_plan_in_wrong_region: RyhtiClient,
    plan_instance: models.Plan,
    mock_xroad_ryhti_permanentidentifier: Callable,
):
    """
    Check that Ryhti permanent plan identifier is left empty, if Ryhti API reports that
    the organization has no permission to create plans in the region. This requires
    that the client has already marked the plan as valid.
    """
    id_responses = (
        authenticated_client_with_valid_plan_in_wrong_region.get_permanent_plan_identifiers()
    )
    authenticated_client_with_valid_plan_in_wrong_region.set_permanent_plan_identifiers(
        id_responses
    )
    session.refresh(plan_instance)
    assert not plan_instance.permanent_plan_identifier
    assert (
        plan_instance.validation_errors
        == "Kaava on validi, mutta sinulla ei ole oikeuksia luoda kaavaa tälle alueelle."
    )


def test_set_permanent_plan_identifiers(
    session: Session,
    authenticated_client_with_valid_plan_and_document: RyhtiClient,
    plan_instance: models.Plan,
    mock_xroad_ryhti_permanentidentifier: Callable,
):
    """
    Check that Ryhti permanent plan identifier is received and saved to the database, if
    Ryhti API returns a permanent plan identifier. This requires that the client has already
    marked the plan as valid.
    """

    id_responses = (
        authenticated_client_with_valid_plan_and_document.get_permanent_plan_identifiers()
    )
    authenticated_client_with_valid_plan_and_document.set_permanent_plan_identifiers(
        id_responses
    )
    session.refresh(plan_instance)
    received_plan_identifier = next(iter(id_responses.values()))["detail"]
    assert plan_instance.permanent_plan_identifier
    assert plan_instance.permanent_plan_identifier == received_plan_identifier
    assert (
        plan_instance.validation_errors
        == "Kaava on validi. Pysyvä kaavatunnus tallennettu. Kaava-asiaa ei ole vielä validoitu."
    )


@pytest.fixture()
def client_with_plan_with_permanent_identifier(
    session: Session,
    authenticated_client_with_valid_plan_and_document: RyhtiClient,
    plan_instance: models.Plan,
    mock_xroad_ryhti_permanentidentifier: Callable,
) -> RyhtiClient:
    """
    Return RyhtiClient that has plan data read in, validated, documents uploaded and its permanent
    identifier set.
    """
    id_responses = (
        authenticated_client_with_valid_plan_and_document.get_permanent_plan_identifiers()
    )
    authenticated_client_with_valid_plan_and_document.set_permanent_plan_identifiers(
        id_responses
    )
    session.refresh(plan_instance)
    print(id_responses)
    received_plan_identifier = next(iter(id_responses.values()))["detail"]
    assert plan_instance.permanent_plan_identifier
    assert plan_instance.permanent_plan_identifier == received_plan_identifier
    authenticated_client_with_valid_plan_and_document.plan_matter_dictionaries = (
        authenticated_client_with_valid_plan_and_document.get_plan_matters()
    )
    assert (
        authenticated_client_with_valid_plan_and_document.plan_matter_dictionaries[
            plan_instance.id
        ]["permanentPlanIdentifier"]
        == received_plan_identifier
    )
    return authenticated_client_with_valid_plan_and_document


@pytest.fixture()
def client_with_plan_with_permanent_identifier_in_proposal_phase(
    session: Session,
    authenticated_client_with_valid_plan_and_document_in_proposal_phase: RyhtiClient,
    plan_instance: models.Plan,
    mock_xroad_ryhti_permanentidentifier: Callable,
) -> RyhtiClient:
    """
    Return RyhtiClient that has plan data in proposal phase read in, validated, documents uploaded and
    its permanent identifier set.
    """
    id_responses = (
        authenticated_client_with_valid_plan_and_document_in_proposal_phase.get_permanent_plan_identifiers()
    )
    authenticated_client_with_valid_plan_and_document_in_proposal_phase.set_permanent_plan_identifiers(
        id_responses
    )
    session.refresh(plan_instance)
    print(id_responses)
    received_plan_identifier = next(iter(id_responses.values()))["detail"]
    assert plan_instance.permanent_plan_identifier
    assert plan_instance.permanent_plan_identifier == received_plan_identifier
    authenticated_client_with_valid_plan_and_document_in_proposal_phase.plan_matter_dictionaries = (
        authenticated_client_with_valid_plan_and_document_in_proposal_phase.get_plan_matters()
    )
    assert (
        authenticated_client_with_valid_plan_and_document_in_proposal_phase.plan_matter_dictionaries[
            plan_instance.id
        ][
            "permanentPlanIdentifier"
        ]
        == received_plan_identifier
    )
    return authenticated_client_with_valid_plan_and_document_in_proposal_phase


def test_get_plan_matters(
    client_with_plan_with_permanent_identifier: RyhtiClient,
    plan_instance: models.Plan,
    desired_plan_matter_dict: dict,
):
    """
    Check that correct JSON structure is generated for plan matter. This requires that
    the client has already marked the plan as valid and fetched a permanent identifer
    for the plan.
    """
    plan_matter = client_with_plan_with_permanent_identifier.plan_matter_dictionaries[
        plan_instance.id
    ]
    deepcompare(
        plan_matter,
        desired_plan_matter_dict,
        ignore_keys=[
            "planMatterPhaseKey",
            "handlingEventKey",
            "interactionEventKey",
            "planDecisionKey",
            "planMapKey",
            "fileKey",
        ],
        ignore_order_for_keys=[
            "planRegulationGroupRelations",
            "additionalInformations",
        ],
    )


def test_validate_plan_matters(
    client_with_plan_with_permanent_identifier: RyhtiClient,
    plan_instance: models.Plan,
    mock_xroad_ryhti_validate_invalid: Callable,
):
    """
    Check that JSON is posted and response received
    """
    responses = client_with_plan_with_permanent_identifier.validate_plan_matters()
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
    client_with_plan_with_permanent_identifier: RyhtiClient,
    plan_instance: models.Plan,
    mock_xroad_ryhti_validate_invalid: Callable,
):
    """
    Check that Ryhti X-Road validation error is saved to database.
    """
    responses = client_with_plan_with_permanent_identifier.validate_plan_matters()
    message = client_with_plan_with_permanent_identifier.save_plan_matter_validation_responses(
        responses
    )
    session.refresh(plan_instance)
    assert plan_instance.validated_at
    assert plan_instance.validation_errors == next(iter(responses.values()))["errors"]


@pytest.fixture()
def client_with_plan_matter_to_be_posted(
    session: Session,
    client_with_plan_with_permanent_identifier: RyhtiClient,
    plan_instance: models.Plan,
    mock_xroad_ryhti_validate_valid: Callable,
) -> RyhtiClient:
    """
    Return RyhtiClient that has plan data read in, validated, its permanent
    identifier set and plan matter validated and marked to be exported.
    """
    responses = client_with_plan_with_permanent_identifier.validate_plan_matters()
    message = client_with_plan_with_permanent_identifier.save_plan_matter_validation_responses(
        responses
    )
    session.refresh(plan_instance)
    # Mark plan instance to be exported
    plan_instance.to_be_exported = True
    session.commit()

    assert not next(iter(responses.values()))["errors"]
    assert plan_instance.validated_at
    assert (
        plan_instance.validation_errors
        == "Kaava-asia on validi ja sen voi viedä Ryhtiin."
    )
    return client_with_plan_with_permanent_identifier


@pytest.fixture()
def client_with_plan_matter_in_new_phase_to_be_posted(
    session: Session,
    client_with_plan_with_permanent_identifier_in_proposal_phase: RyhtiClient,
    plan_instance: models.Plan,
    mock_xroad_ryhti_validate_valid: Callable,
) -> RyhtiClient:
    """
    Return RyhtiClient that has plan data in proposal phase read in, validated,
    its permanent identifier set and plan matter validated and marked to be exported.
    """
    responses = (
        client_with_plan_with_permanent_identifier_in_proposal_phase.validate_plan_matters()
    )
    message = client_with_plan_with_permanent_identifier_in_proposal_phase.save_plan_matter_validation_responses(
        responses
    )
    session.refresh(plan_instance)
    # Mark plan instance to be exported
    plan_instance.to_be_exported = True
    session.commit()

    assert not next(iter(responses.values()))["errors"]
    assert plan_instance.validated_at
    assert (
        plan_instance.validation_errors
        == "Kaava-asia on validi ja sen voi viedä Ryhtiin."
    )
    return client_with_plan_with_permanent_identifier_in_proposal_phase


def test_post_new_plan_matters(
    client_with_plan_matter_to_be_posted: RyhtiClient,
    plan_instance: models.Plan,
    mock_xroad_ryhti_post_new_plan_matter: Callable,
):
    """
    Check that JSON is posted and response received when the plan matter does not
    exist in Ryhti yet.
    """
    responses = client_with_plan_matter_to_be_posted.post_plan_matters()
    for plan_id, response in responses.items():
        assert plan_id == plan_instance.id
        assert response["warnings"]
        assert not response["errors"]


def test_save_new_plan_matter_post_responses(
    session: Session,
    client_with_plan_matter_to_be_posted: RyhtiClient,
    plan_instance: models.Plan,
    mock_xroad_ryhti_post_new_plan_matter: Callable,
):
    """
    Check that export time is saved to database.
    """
    responses = client_with_plan_matter_to_be_posted.post_plan_matters()
    message = client_with_plan_matter_to_be_posted.save_plan_matter_post_responses(
        responses
    )
    session.refresh(plan_instance)
    assert plan_instance.exported_at
    assert not plan_instance.to_be_exported
    assert plan_instance.validation_errors == "Uusi kaava-asian vaihe on viety Ryhtiin."


def test_update_existing_plan_matters(
    session: Session,
    client_with_plan_matter_in_new_phase_to_be_posted: RyhtiClient,
    plan_instance: models.Plan,
    mock_xroad_ryhti_update_existing_plan_matter: Callable,
):
    """
    Check that JSON is posted and response received when the plan matter exists in Ryhti
    and a new plan matter phase must be posted.
    """
    responses = client_with_plan_matter_in_new_phase_to_be_posted.post_plan_matters()
    for plan_id, response in responses.items():
        assert plan_id == plan_instance.id
        assert response["warnings"]
        assert not response["errors"]


def test_save_update_existing_matter_post_responses(
    session: Session,
    client_with_plan_matter_in_new_phase_to_be_posted: RyhtiClient,
    plan_instance: models.Plan,
    mock_xroad_ryhti_update_existing_plan_matter: Callable,
):
    """
    Check that export time is saved to database.
    """
    responses = client_with_plan_matter_in_new_phase_to_be_posted.post_plan_matters()
    message = client_with_plan_matter_in_new_phase_to_be_posted.save_plan_matter_post_responses(
        responses
    )
    session.refresh(plan_instance)
    assert plan_instance.exported_at
    assert not plan_instance.to_be_exported
    assert plan_instance.validation_errors == "Uusi kaava-asian vaihe on viety Ryhtiin."


def test_update_existing_plan_matter_phase(
    session: Session,
    client_with_plan_matter_to_be_posted: RyhtiClient,
    plan_instance: models.Plan,
    mock_xroad_ryhti_update_existing_plan_matter: Callable,
):
    """
    Check that JSON is posted and response received when the plan matter and the plan matter
    phase exist in Ryhti and the plan matter phase must be updated.
    """
    responses = client_with_plan_matter_to_be_posted.post_plan_matters()
    for plan_id, response in responses.items():
        assert plan_id == plan_instance.id
        assert response["warnings"]
        assert not response["errors"]


def test_save_update_existing_matter_phase_post_responses(
    session: Session,
    client_with_plan_matter_to_be_posted: RyhtiClient,
    plan_instance: models.Plan,
    mock_xroad_ryhti_update_existing_plan_matter: Callable,
):
    """
    Check that export time is saved to database.
    """
    responses = client_with_plan_matter_to_be_posted.post_plan_matters()
    message = client_with_plan_matter_to_be_posted.save_plan_matter_post_responses(
        responses
    )
    session.refresh(plan_instance)
    assert plan_instance.exported_at
    assert not plan_instance.to_be_exported
    assert plan_instance.validation_errors == "Kaava-asian vaihe on päivitetty Ryhtiin."


def test_related_land_use_area(
    plan_instance: models.Plan,
    land_use_area_instance: models.LandUseArea,
    other_area_instance: models.OtherArea,
    construction_area_plan_regulation_instance: models.PlanRegulation,
    ryhti_client: RyhtiClient,
):
    """Test that the land use area that contains the other area of type 'rakennusala' is added to the related plan objects list."""

    plan_dict = ryhti_client.get_plan_dictionaries()[plan_instance.id]
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
