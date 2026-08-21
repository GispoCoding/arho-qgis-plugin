from __future__ import annotations

import json
import os
from typing import TYPE_CHECKING, cast
from uuid import uuid4

import pytest
from geoalchemy2.shape import from_shape
from requests import PreparedRequest
from requests_mock.request import _RequestObjectProxy
from shapely.geometry import shape
from sqlalchemy.exc import MultipleResultsFound
from sqlalchemy.orm import Session

from database import models
from database.base import PROJECT_SRID
from ryhti_client.database_client import DatabaseClient
from ryhti_client.ryhti_client import RyhtiClient

from .conftest import ReturnSame, deepcompare

if TYPE_CHECKING:
    from collections.abc import Callable, Generator

    from requests import PreparedRequest
    from requests_mock import Mocker
    from requests_mock.request import _RequestObjectProxy
    from sqlalchemy.orm import Session

    from database import codes

mock_rule = "random_rule"
mock_error_string = "There is something wrong with your plan! Good luck!"
mock_instance = "some field in your plan"


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
def database_client(dba_connection_string: str) -> DatabaseClient:
    """Return DatabaseClient connected to the test database."""
    return DatabaseClient(dba_connection_string)


@pytest.fixture
def ryhti_client() -> RyhtiClient:
    """Return RyhtiClient that is configured to use the mock Ryhti APIs."""
    # Let's mock production x-road with gispo organization client here.
    return RyhtiClient(
        public_api_url="http://mock.url",
        xroad_server_address="http://mock2.url",
        xroad_instance="FI",
        xroad_member_class="COM",
        xroad_member_code="2455538-5",
        xroad_member_client_name="ryhti-gispo-client",
        xroad_syke_client_id="test-id",
        xroad_syke_client_secret="test-secret",
    )


def test_related_land_use_area(
    complete_test_plan: models.Plan,
    land_use_area_instance: models.LandUseArea,
    other_area_instance: models.OtherArea,
    database_client: DatabaseClient,
) -> None:
    """Test that the land use area that contains the other area of type 'rakennusala'
    is added to the related plan objects list.
    """
    plan = database_client.get_plan(complete_test_plan.id)
    plan_dict = database_client.get_plan_dictionary(plan)
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


def test_related_land_use_area_multiple_containers(
    complete_test_plan: models.Plan,
    land_use_area_instance: models.LandUseArea,
    other_area_instance: models.OtherArea,
    preparation_status_instance: codes.LifeCycleStatus,
    type_of_underground_instance: codes.TypeOfUnderground,
    plan_instance: models.Plan,
    temp_session_feature: ReturnSame[models.LandUseArea],
    database_client: DatabaseClient,
) -> None:
    """Test that serialization raises if several land use areas contain the same
    plan object that needs a containing land use area.
    """
    overlapping_land_use_area = models.LandUseArea(
        geom=land_use_area_instance.geom,
        name={"fin": "test_overlapping_land_use_area"},
        description={"fin": "test_overlapping_land_use_area"},
        height_min=0.0,
        height_max=1.0,
        height_unit="m",
        ordering=3,
        lifecycle_status=preparation_status_instance,
        type_of_underground=type_of_underground_instance,
        plan=plan_instance,
    )
    temp_session_feature(overlapping_land_use_area)

    plan = database_client.get_plan(complete_test_plan.id)
    with pytest.raises(MultipleResultsFound):
        database_client.get_plan_dictionary(plan)


def test_related_land_use_area_no_container(
    complete_test_plan: models.Plan,
    preparation_status_instance: codes.LifeCycleStatus,
    type_of_underground_instance: codes.TypeOfUnderground,
    plan_instance: models.Plan,
    construction_area_plan_regulation_group_instance: models.PlanRegulationGroup,
    temp_session_feature: ReturnSame[models.OtherArea],
    database_client: DatabaseClient,
) -> None:
    """Test that no related plan objects are added for a plan object that no
    land use area contains.
    """
    outside_other_area = models.OtherArea(
        geom=from_shape(
            shape(
                {
                    "type": "MultiPolygon",
                    "coordinates": [
                        [
                            [
                                [390000, 6690000],
                                [390000, 6691000],
                                [391000, 6691000],
                                [391000, 6690000],
                                [390000, 6690000],
                            ]
                        ]
                    ],
                }
            ),
            srid=PROJECT_SRID,
            extended=True,
        ),
        lifecycle_status=preparation_status_instance,
        type_of_underground=type_of_underground_instance,
        plan=plan_instance,
        plan_regulation_groups=[construction_area_plan_regulation_group_instance],
    )
    temp_session_feature(outside_other_area)

    plan = database_client.get_plan(complete_test_plan.id)
    plan_dict = database_client.get_plan_dictionary(plan)
    outside_other_area_in_dict = next(
        (
            plan_object
            for plan_object in plan_dict["planObjects"]
            if plan_object["planObjectKey"] == outside_other_area.id
        ),
        None,
    )

    assert outside_other_area_in_dict
    assert "relatedPlanObjectKeys" not in outside_other_area_in_dict


def test_get_containing_land_use_area_ids(
    land_use_area_instance: models.LandUseArea,
    other_area_instance: models.OtherArea,
    point_instance: models.Point,
    construction_area_plan_regulation_instance: models.PlanRegulation,
    point_text_plan_regulation_instance: models.PlanRegulation,
    database_client: DatabaseClient,
) -> None:
    """Test that the batch query returns a mapping only for plan objects that
    need a containing land use area.

    The other area has a regulation of type "rakennusala", so it needs one.
    The point is inside the land use area, but its regulation type does not
    need one.
    """
    mapping = database_client._get_containing_land_use_area_ids(  # noqa: SLF001
        [other_area_instance, point_instance]
    )
    assert mapping == {other_area_instance.id: land_use_area_instance.id}

    assert (
        database_client._get_containing_land_use_area_ids(  # noqa: SLF001
            [point_instance]
        )
        == {}
    )


@pytest.fixture
def plan_in_wrong_region(
    session: Session,
    complete_test_plan: models.Plan,
    another_organisation_instance: models.Organisation,
) -> models.Plan:
    """Return a plan that is owned by an organisation in another region."""
    session.add(complete_test_plan)
    complete_test_plan.plan_matter.organisation = another_organisation_instance
    session.commit()
    return complete_test_plan


def test_get_plan_dictionary(
    database_client: DatabaseClient,
    complete_test_plan: models.Plan,
    desired_plan_dict: dict,
) -> None:
    """Check that correct JSON structure is generated for the plan."""
    plan = database_client.get_plan(complete_test_plan.id)
    result_plan_dict = database_client.get_plan_dictionary(plan)
    deepcompare(
        result_plan_dict,
        desired_plan_dict,
        ignore_order_for_keys=[
            "planRegulationGroupRelations",
            "additionalInformations",
        ],
    )


def test_validate_plan(
    database_client: DatabaseClient,
    ryhti_client: RyhtiClient,
    complete_test_plan: models.Plan,
    mock_public_ryhti_validate_invalid: Callable,
) -> None:
    """Check that JSON is posted and response received"""
    plan = database_client.get_plan(complete_test_plan.id)
    plan_dict = database_client.get_plan_dictionary(plan)
    response = ryhti_client.validate_plan(plan, plan_dict)
    assert response["errors"] == [
        {"ruleId": mock_rule, "message": mock_error_string, "instance": mock_instance}
    ]


def test_save_plan_validation_response(
    session: Session,
    database_client: DatabaseClient,
    ryhti_client: RyhtiClient,
    complete_test_plan: models.Plan,
    mock_public_ryhti_validate_invalid: Callable,
) -> None:
    """Check that Ryhti validation error is saved to database."""
    plan = database_client.get_plan(complete_test_plan.id)
    plan_dict = database_client.get_plan_dictionary(plan)
    response = ryhti_client.validate_plan(plan, plan_dict)
    database_client.save_plan_validation_response(plan.id, response)
    session.refresh(complete_test_plan)
    assert complete_test_plan.validated_at
    assert complete_test_plan.validation_errors == response["errors"]


def test_authenticate_to_xroad_ryhti_api(
    ryhti_client: RyhtiClient, mock_xroad_ryhti_authenticate: Callable
) -> None:
    """Test authenticating to mock X-Road Ryhti API."""
    ryhti_client.xroad_ryhti_authenticate()
    assert ryhti_client.xroad_headers["Authorization"] == "Bearer test-token"


@pytest.fixture
def authenticated_ryhti_client(
    ryhti_client: RyhtiClient, mock_xroad_ryhti_authenticate: Callable
) -> RyhtiClient:
    """Return RyhtiClient that is authenticated to our mock X-Road API."""
    ryhti_client.xroad_ryhti_authenticate()
    assert ryhti_client.xroad_headers["Authorization"] == "Bearer test-token"
    return ryhti_client


def test_set_permanent_plan_identifier_in_wrong_region(
    session: Session,
    database_client: DatabaseClient,
    authenticated_ryhti_client: RyhtiClient,
    plan_in_wrong_region: models.Plan,
    another_organisation_instance: models.Organisation,
    mock_xroad_ryhti_permanentidentifier: Callable,
) -> None:
    """Check that Ryhti permanent plan identifier is left empty, if Ryhti API reports that
    the organization has no permission to create plans in the region.
    """
    plan = database_client.get_plan(plan_in_wrong_region.id)
    response = authenticated_ryhti_client.get_permanent_plan_identifier(
        plan.plan_matter
    )
    assert response
    message = database_client.set_permanent_plan_identifier(plan.plan_matter, response)
    session.refresh(plan_in_wrong_region)
    assert (
        plan_in_wrong_region.plan_matter.organisation is another_organisation_instance
    )
    assert not plan_in_wrong_region.plan_matter.permanent_plan_identifier
    assert message == "Sinulla ei ole oikeuksia luoda kaavaa tälle alueelle."


def test_set_permanent_plan_identifier(
    session: Session,
    database_client: DatabaseClient,
    authenticated_ryhti_client: RyhtiClient,
    complete_test_plan: models.Plan,
    plan_matter_instance: models.PlanMatter,
    mock_xroad_ryhti_permanentidentifier: Callable,
) -> None:
    """Check that Ryhti permanent plan identifier is received and saved to the database, if
    Ryhti API returns a permanent plan identifier.
    """
    plan = database_client.get_plan(complete_test_plan.id)
    response = authenticated_ryhti_client.get_permanent_plan_identifier(
        plan.plan_matter
    )
    assert response
    message = database_client.set_permanent_plan_identifier(plan.plan_matter, response)
    session.refresh(plan_matter_instance)
    assert plan_matter_instance.permanent_plan_identifier == response["detail"]
    assert message == response["detail"]


@pytest.fixture
def plan_with_permanent_identifier(
    database_client: DatabaseClient,
    authenticated_ryhti_client: RyhtiClient,
    complete_test_plan: models.Plan,
    mock_xroad_ryhti_permanentidentifier: Callable,
) -> models.Plan:
    """Return a plan that has its permanent identifier set.

    The returned detached plan instance must be used for both uploading and
    saving documents, so that the document responses pair up with the plan
    documents.
    """
    plan = database_client.get_plan(complete_test_plan.id)
    response = authenticated_ryhti_client.get_permanent_plan_identifier(
        plan.plan_matter
    )
    assert response
    database_client.set_permanent_plan_identifier(plan.plan_matter, response)
    assert plan.plan_matter.permanent_plan_identifier == response["detail"]
    return plan


def test_upload_plan_documents(
    authenticated_ryhti_client: RyhtiClient,
    plan_with_permanent_identifier: models.Plan,
    mock_public_attachment_document: Callable,
    mock_public_map_document: Callable,
    mock_xroad_ryhti_fileupload: Callable,
) -> None:
    """Check that plan documents are uploaded. This does not require plan to be valid,
    but we only upload documents for plans that have permanent identifiers.
    """
    responses = authenticated_ryhti_client.upload_plan_documents(
        plan_with_permanent_identifier
    )
    assert responses
    for document_response in responses:
        assert document_response["status"] == 201
        assert not document_response["errors"]
        assert document_response["detail"]


def test_set_plan_documents(
    session: Session,
    database_client: DatabaseClient,
    authenticated_ryhti_client: RyhtiClient,
    plan_with_permanent_identifier: models.Plan,
    complete_test_plan: models.Plan,
    mock_public_attachment_document: Callable,
    mock_public_map_document: Callable,
    mock_xroad_ryhti_fileupload: Callable,
) -> None:
    """Check that uploaded document ids are saved to the database. This does not
    require plan to be valid, but we only upload documents for plans that have
    permanent identifiers.
    """
    responses = authenticated_ryhti_client.upload_plan_documents(
        plan_with_permanent_identifier
    )
    database_client.set_plan_documents(plan_with_permanent_identifier, responses)
    session.refresh(complete_test_plan.documents[0])
    assert complete_test_plan.documents[0].exported_at
    assert complete_test_plan.documents[0].exported_file_key
    assert complete_test_plan.documents[0].exported_file_etag


@pytest.fixture
def plan_with_permanent_identifier_and_documents(
    session: Session,
    database_client: DatabaseClient,
    authenticated_ryhti_client: RyhtiClient,
    plan_with_permanent_identifier: models.Plan,
    complete_test_plan: models.Plan,
    mock_public_attachment_document: Callable,
    mock_public_map_document: Callable,
    mock_xroad_ryhti_fileupload: Callable,
) -> models.Plan:
    """Return a plan that has its permanent identifier set and its documents
    uploaded.
    """
    plan = plan_with_permanent_identifier
    responses = authenticated_ryhti_client.upload_plan_documents(plan)
    assert responses
    for document_response in responses:
        assert document_response["status"] == 201
        assert not document_response["errors"]
        assert document_response["detail"]
    database_client.set_plan_documents(plan, responses)
    session.refresh(complete_test_plan.documents[0])
    assert complete_test_plan.documents[0].exported_at
    assert complete_test_plan.documents[0].exported_file_key
    return plan


def test_upload_unchanged_plan_documents(
    session: Session,
    database_client: DatabaseClient,
    authenticated_ryhti_client: RyhtiClient,
    plan_with_permanent_identifier_and_documents: models.Plan,
    complete_test_plan: models.Plan,
    mock_public_attachment_document: Callable,
    mock_public_map_document: Callable,
    mock_xroad_ryhti_fileupload: Callable,
) -> None:
    """Check that unchanged plan documents are not uploaded."""
    plan = plan_with_permanent_identifier_and_documents
    old_exported_at = complete_test_plan.documents[0].exported_at
    old_file_key = complete_test_plan.documents[0].exported_file_key
    old_file_etag = complete_test_plan.documents[0].exported_file_etag
    assert old_exported_at
    assert old_file_key
    assert old_file_etag
    reupload_responses = authenticated_ryhti_client.upload_plan_documents(plan)
    assert reupload_responses
    for document_response in reupload_responses:
        assert document_response["status"] is None
        assert document_response["detail"] == "File unchanged since last upload."
    database_client.set_plan_documents(plan, reupload_responses)
    session.refresh(complete_test_plan.documents[0])
    assert complete_test_plan.documents[0].exported_at == old_exported_at
    assert complete_test_plan.documents[0].exported_file_key == old_file_key
    assert complete_test_plan.documents[0].exported_file_etag == old_file_etag
