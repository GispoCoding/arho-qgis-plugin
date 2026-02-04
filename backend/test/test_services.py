from __future__ import annotations

import inspect
import json
import uuid
from http import HTTPStatus
from typing import TYPE_CHECKING, Any

import psycopg
import pytest
import requests

from database import codes

from .conftest import deepcompare

if TYPE_CHECKING:
    from pytest_docker.plugin import Services

    from database.db_helper import ConnectionParameters
    from database.models import Plan, PlanMatter
    from lambdas.koodistot_loader import koodistot_loader


@pytest.fixture(scope="module")
def db_manager_url(docker_ip: str | Any, docker_services: Services) -> str:
    port = docker_services.port_for("db_manager", 8080)
    return f"http://{docker_ip}:{port}/2015-03-31/functions/function/invocations"


@pytest.fixture(scope="module")
def koodistot_loader_url(docker_ip: str | Any, docker_services: Services) -> str:
    port = docker_services.port_for("koodistot_loader", 8080)
    return f"http://{docker_ip}:{port}/2015-03-31/functions/function/invocations"


@pytest.fixture(scope="module")
def ryhti_client_url(docker_ip: str | Any, docker_services: Services) -> str:
    port = docker_services.port_for("ryhti_client", 8080)
    return f"http://{docker_ip}:{port}/2015-03-31/functions/function/invocations"


@pytest.fixture(scope="module")
def mml_loader_url(docker_ip: str | Any, docker_services: Services) -> str:
    port = docker_services.port_for("mml_loader", 8080)
    return f"http://{docker_ip}:{port}/2015-03-31/functions/function/invocations"


@pytest.fixture
def populate_koodistot(koodistot_loader_url: str) -> None:
    payload: koodistot_loader.Event = {}
    r = requests.post(koodistot_loader_url, data=json.dumps(payload))
    data = r.json()
    assert data["statusCode"] == 200, data["body"]


@pytest.fixture
def populate_suomifi_koodistot(koodistot_loader_url: str) -> None:
    payload: koodistot_loader.Event = {"local_codes": False}
    r = requests.post(koodistot_loader_url, data=json.dumps(payload))
    data = r.json()
    assert data["statusCode"] == 200, data["body"]


@pytest.fixture
def populate_local_koodistot(koodistot_loader_url: str) -> None:
    payload: koodistot_loader.Event = {"suomifi_codes": False}
    r = requests.post(koodistot_loader_url, data=json.dumps(payload))
    data = r.json()
    assert data["statusCode"] == 200, data["body"]


def test_populate_koodistot(
    populate_koodistot: None, main_db_params: ConnectionParameters
) -> None:
    """Test the whole lambda endpoint"""
    conn = psycopg.connect(**main_db_params)
    try:
        with conn.cursor() as cur:
            for _name, value in inspect.getmembers(codes, inspect.isclass):
                if issubclass(value, codes.CodeBase) and (
                    # some code tables have external source, some have local source, some have both
                    value.code_list_uri or value.local_codes
                ):
                    print(value)
                    cur.execute(f"SELECT count(*) FROM codes.{value.__tablename__}")
                    row = cur.fetchone()
                    assert row is not None
                    code_count = row[0]
                    assert code_count > 0
    finally:
        conn.close()


def test_populate_suomifi_koodistot(
    populate_suomifi_koodistot: None, main_db_params: ConnectionParameters
) -> None:
    """Test only suomi.fi codes"""
    conn = psycopg.connect(**main_db_params)
    try:
        with conn.cursor() as cur:
            for _name, value in inspect.getmembers(codes, inspect.isclass):
                if (
                    value is not codes.CodeBase
                    and issubclass(value, codes.CodeBase)
                    and (
                        # some code tables have external source, some have local source, some have both
                        value.code_list_uri
                    )
                ):
                    cur.execute(f"SELECT count(*) FROM codes.{value.__tablename__}")
                    row = cur.fetchone()
                    assert row is not None
                    code_count = row[0]
                    assert code_count > 0
                if (
                    value is not codes.CodeBase
                    and issubclass(value, codes.CodeBase)
                    and (
                        # some code tables have external source, some have local source, some have both
                        not value.code_list_uri
                    )
                ):
                    cur.execute(f"SELECT count(*) FROM codes.{value.__tablename__}")
                    row = cur.fetchone()
                    assert row is not None
                    code_count = row[0]
                    assert code_count == 0
    finally:
        conn.close()


def test_populate_local_koodistot(
    populate_local_koodistot: None, main_db_params: ConnectionParameters
) -> None:
    """Test only local codes"""
    conn = psycopg.connect(**main_db_params)
    try:
        with conn.cursor() as cur:
            for _name, value in inspect.getmembers(codes, inspect.isclass):
                if (
                    value is not codes.CodeBase
                    and issubclass(value, codes.CodeBase)
                    and (
                        # some code tables have external source, some have local source, some have both
                        not value.local_codes
                    )
                ):
                    cur.execute(f"SELECT count(*) FROM codes.{value.__tablename__}")
                    row = cur.fetchone()
                    assert row is not None
                    code_count = row[0]
                    assert code_count == 0
                if (
                    value is not codes.CodeBase
                    and issubclass(value, codes.CodeBase)
                    and (
                        # some code tables have external source, some have local source, some have both
                        value.local_codes
                    )
                ):
                    cur.execute(f"SELECT count(*) FROM codes.{value.__tablename__}")
                    row = cur.fetchone()
                    assert row is not None
                    code_count = row[0]
                    assert code_count > 0
    finally:
        conn.close()


# Test getting all plans with both direct lambda call and HTTPS API call.
# The HTTPS API call body will be a JSON string.
@pytest.fixture(
    params=[
        {"action": "get_plans", "save_json": True},
        {
            "version": "2.0",
            "routeKey": "",
            "rawPath": "",
            "rawQueryString": "",
            "cookies": [],
            "headers": {},
            "queryStringParameters": {},
            "requestContext": {},
            "body": '{"action": "get_plans", "save_json": true}',
            "pathParameters": {},
            "isBase64Encoded": False,
            "stageVariables": {},
        },
    ]
)
def get_all_plans(
    request: pytest.FixtureRequest,
    ryhti_client_url: str,
    complete_test_plan: Plan,
    another_test_plan: Plan,
    desired_plan_dict: dict,
    another_plan_dict: dict,
) -> None:
    """Get invalid plan JSONs from lambda. The plans should be validated separately.

    Getting plans should make lambda return http 200 OK (to indicate that serialization
    has been run successfully), with the ryhti_responses dict empty, and details
    dict containing the serialized plans.

    If the request is coming through the API Gateway with stringified JSON body, the
    response to the API gateway must similarly contain stringified JSON body.
    """
    r = requests.post(ryhti_client_url, data=json.dumps(request.param))
    data = r.json()
    print(data)
    assert data["statusCode"] == 200
    body = data["body"]
    if request.param != {"action": "get_plans", "save_json": True}:
        # API gateway response must have JSON body stringified.
        body = json.loads(body)
    assert body["title"] == "Returning serialized plans from database."
    deepcompare(
        body["details"][complete_test_plan.id],
        desired_plan_dict,
        ignore_order_for_keys=[
            "planRegulationGroups",
            "planRegulationGroupRelations",
            "additionalInformations",
        ],
    )
    deepcompare(
        body["details"][another_test_plan.id],
        another_plan_dict,
        ignore_order_for_keys=[
            "planRegulationGroups",
            "planRegulationGroupRelations",
            "additionalInformations",
        ],
    )
    assert not body["ryhti_responses"]


def test_get_all_plans(
    get_all_plans: None, main_db_params: ConnectionParameters
) -> None:
    """Test the whole lambda endpoint with an invalid plan"""
    # getting plan JSON from lambda should not run validations
    conn = psycopg.connect(**main_db_params)
    try:
        with conn.cursor() as cur:
            # Check that plans are NOT validated
            cur.execute("SELECT validated_at, validation_errors FROM hame.plan")
            row = cur.fetchone()
            assert row is not None
            validation_date, errors = row
            assert not validation_date
            assert not errors

            row = cur.fetchone()
            assert row is not None
            validation_date, errors = row
            assert not validation_date
            assert not errors
    finally:
        conn.close()


@pytest.fixture
def get_single_plan(
    ryhti_client_url: str,
    complete_test_plan: Plan,
    another_test_plan: Plan,
    desired_plan_dict: dict,
) -> None:
    """Get single plan JSON from lambda by id. Another plan in the database should not be
    serialized.

    Getting plan should make lambda return http 200 OK (to indicate that serialization
    has been run successfully), with the ryhti_responses dict empty, and details
    dict containing the serialized plan.
    """
    payload = {
        "action": "get_plans",
        "plan_uuid": complete_test_plan.id,
        "save_json": True,
    }
    r = requests.post(ryhti_client_url, data=json.dumps(payload))
    data = r.json()
    print(data)
    assert data["statusCode"] == 200
    body = data["body"]
    assert body["title"] == "Returning serialized plans from database."
    # Check that other plan is NOT returned
    assert len(body["details"]) == 1
    deepcompare(
        body["details"][complete_test_plan.id],
        desired_plan_dict,
        ignore_order_for_keys=[
            "planRegulationGroups",
            "planRegulationGroupRelations",
            "additionalInformations",
        ],
    )
    assert not body["ryhti_responses"]


def test_get_single_plan(
    get_single_plan: None, main_db_params: ConnectionParameters
) -> None:
    """Test the whole lambda endpoint with single_plan"""
    # getting plan JSON from lambda should not run validations
    conn = psycopg.connect(**main_db_params)
    try:
        with conn.cursor() as cur:
            # Check that plans are NOT validated
            cur.execute("SELECT validated_at, validation_errors FROM hame.plan")
            row = cur.fetchone()
            assert row is not None
            validation_date, errors = row
            assert not validation_date
            assert not errors

            row = cur.fetchone()
            assert row is not None
            validation_date, errors = row
            assert not validation_date
            assert not errors
    finally:
        conn.close()


@pytest.fixture
def validate_all_plans(
    ryhti_client_url: str, complete_test_plan: Plan, another_test_plan
) -> None:
    """Validate valid and invalid Ryhti plans against the Ryhti API.

    An invalid plan should make lambda return http 200 OK (to indicate that the validation
    has been run successfully), with the validation errors returned in the payload.
    """
    payload = {"action": "validate_plans", "save_json": True}
    r = requests.post(ryhti_client_url, data=json.dumps(payload))
    data = r.json()
    print(data)
    assert data["statusCode"] == 200
    body = data["body"]
    assert body["title"] == "Plan validations run."
    assert (
        body["details"][complete_test_plan.id]
        == f"Plan validation successful for {complete_test_plan.id}!"
    )
    assert (
        body["details"][another_test_plan.id]
        == f"Plan validation FAILED for {another_test_plan.id}."
    )
    # Our test plan is valid
    assert body["ryhti_responses"][complete_test_plan.id]["status"] == 200
    assert not body["ryhti_responses"][complete_test_plan.id]["errors"]
    # Another test plan contains nothing really
    assert body["ryhti_responses"][another_test_plan.id]["status"] == 400
    assert body["ryhti_responses"][another_test_plan.id]["errors"]


def test_validate_all_plans(
    validate_all_plans: None, main_db_params: ConnectionParameters
) -> None:
    """Test the whole lambda endpoint with valid and invalid plans"""
    conn = psycopg.connect(**main_db_params)
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT validated_at, validation_errors FROM hame.plan")
            row = cur.fetchone()
            assert row is not None
            validation_date, errors = row
            assert validation_date
            assert errors == "Kaava on validi. Kaava-asiaa ei ole vielä validoitu."

            row = cur.fetchone()
            assert row is not None
            validation_date, errors = row
            assert validation_date
            assert errors
    finally:
        conn.close()


@pytest.fixture
def validate_single_invalid_plan(
    ryhti_client_url: str, complete_test_plan: Plan, another_test_plan
) -> None:
    """Validate an invalid Ryhti plan against the Ryhti API.

    An invalid plan should make lambda return http 200 OK (to indicate that the validation
    has been run successfully), with the validation errors returned in the payload.
    """
    payload = {
        "action": "validate_plans",
        "plan_uuid": another_test_plan.id,
        "save_json": True,
    }
    r = requests.post(ryhti_client_url, data=json.dumps(payload))
    data = r.json()
    print(data)
    assert data["statusCode"] == 200
    body = data["body"]
    assert body["title"] == "Plan validations run."
    # Check that other plan is NOT reported validated
    assert len(body["details"]) == 1
    assert (
        body["details"][another_test_plan.id]
        == f"Plan validation FAILED for {another_test_plan.id}."
    )
    assert len(body["ryhti_responses"]) == 1
    assert body["ryhti_responses"][another_test_plan.id]["status"] == 400
    assert body["ryhti_responses"][another_test_plan.id]["errors"]


def test_validate_single_invalid_plan(
    validate_single_invalid_plan: None, main_db_params: ConnectionParameters
) -> None:
    """Test the whole lambda endpoint with an invalid plan"""
    conn = psycopg.connect(**main_db_params)
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT validated_at, validation_errors FROM hame.plan ORDER BY modified_at DESC"
            )
            row = cur.fetchone()
            assert row is not None
            validation_date, errors = row
            assert validation_date
            assert errors

            # Check that other plan is NOT marked validated
            row = cur.fetchone()
            assert row is not None
            validation_date, errors = row
            assert not validation_date
            assert not errors
    finally:
        conn.close()


@pytest.fixture
def get_permanent_plan_identifier(
    ryhti_client_url: str,
    complete_test_plan: Plan,
    another_test_plan: Plan,
    desired_plan_dict: dict,
) -> None:
    """Get a permanent plan identifier from X-road. Another plan in the database should not
    get a permanent plan identifier.

    Since local tests or CI/CD cannot connect to X-Road servers, we use a Mock X-Road API
    that returns a permanent plan identifier and responds with 200 OK.

    Getting an identifier should make lambda return http 200 OK, with the ryhti_responses dict
    and details both containing the identifier.
    """
    payload = {
        "action": "get_permanent_plan_identifiers",
        "plan_uuid": complete_test_plan.id,
        "save_json": True,
    }
    r = requests.post(ryhti_client_url, data=json.dumps(payload))
    data = r.json()
    print(data)
    assert data["statusCode"] == 200
    body = data["body"]
    assert body["title"] == "Possible permanent plan identifiers set."
    # Check that other plan was NOT processed
    assert len(body["details"]) == 1
    assert len(body["ryhti_responses"]) == 1


def test_get_permanent_plan_identifier(
    get_permanent_plan_identifier: None, main_db_params: ConnectionParameters
) -> None:
    """Test the whole lambda endpoint with single_plan"""
    # getting permanent identifier from lambda should not run validations
    conn = psycopg.connect(**main_db_params)
    try:
        with conn.cursor() as cur:
            # Check that plans are NOT validated
            cur.execute(
                """
                SELECT validated_at, validation_errors, pm.permanent_plan_identifier
                FROM hame.plan p JOIN hame.plan_matter pm
                ON p.plan_matter_id = pm.id
                ORDER BY p.modified_at DESC
                """
            )
            row = cur.fetchone()
            assert row is not None
            validation_date, errors, permanent_plan_identifier = row
            assert not validation_date
            assert not errors
            assert not permanent_plan_identifier

            row = cur.fetchone()
            assert row is not None
            validation_date, errors, permanent_plan_identifier = row
            assert not validation_date
            assert not errors
            assert permanent_plan_identifier == "MK-123456"
    finally:
        conn.close()


@pytest.fixture
def extra_data(plan_matter_instance: PlanMatter) -> dict:
    return {"name": "test_plan", "plan_matter_id": plan_matter_instance.id}


@pytest.fixture
def import_payload(extra_data):
    return {
        "action": "import_plan",
        "plan_uuid": str(
            uuid.uuid4()
        ),  # Dummy non existing UUID that must be added for now
        "data": {"plan_json": None, "extra_data": extra_data},
    }


def test_import_plan(
    codes_loaded, import_payload, ryhti_client_url, simple_plan_json: str
):
    """Test importing a plan"""
    import_payload["data"]["plan_json"] = simple_plan_json

    r = requests.post(ryhti_client_url, data=json.dumps(import_payload))
    assert r.status_code == HTTPStatus.OK

    data = r.json()
    assert data["body"]["title"] == "Plan imported."
    assert data["body"]["details"]["plan_id"] == "7f522b2f-8b45-4a17-b433-5f47271b579e"


def test_import_duplicate_plan(
    codes_loaded,
    import_payload: dict[str, Any],
    ryhti_client_url: str,
    simple_plan_json: str,
):
    """Test importing a plan"""
    import_payload["data"]["plan_json"] = simple_plan_json

    r = requests.post(ryhti_client_url, data=json.dumps(import_payload))
    assert r.status_code == HTTPStatus.OK

    r = requests.post(ryhti_client_url, data=json.dumps(import_payload))
    assert (
        r.status_code == HTTPStatus.OK
    )  # TODO: This should be a 400 or 409. Fix after plugin fixed.

    data = r.json()
    assert data["body"]["title"] == "Plan already exists."


def test_import_invalid_plan(ryhti_client_url, import_payload, invalid_plan_json: str):
    import_payload["data"]["plan_json"] = invalid_plan_json

    r = requests.post(ryhti_client_url, data=json.dumps(import_payload))

    # Status code from the lambda container
    # (API Gateway would follow the status code returned from the lambda function)
    assert r.status_code == HTTPStatus.OK

    data = r.json()
    assert (
        data["statusCode"] == HTTPStatus.BAD_REQUEST
    )  # Status code from our lambda function
    assert data["body"]["title"] == "Error in provided data."
    assert "Invalid plan data:" in data["body"]["details"]["error"]
