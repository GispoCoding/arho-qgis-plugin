import inspect
import json

import psycopg2
import pytest
import requests
from sqlalchemy.orm import Session

from database import models
from database.test.conftest import assert_database_is_alright, deepcompare, drop_hame_db
from lambdas.koodistot_loader.koodistot_loader import codes


@pytest.fixture(scope="module")
def db_manager_url(docker_ip, docker_services):
    port = docker_services.port_for("db_manager", 8080)
    return f"http://{docker_ip}:{port}/2015-03-31/functions/function/invocations"


@pytest.fixture(scope="module")
def koodistot_loader_url(docker_ip, docker_services):
    port = docker_services.port_for("koodistot_loader", 8080)
    return f"http://{docker_ip}:{port}/2015-03-31/functions/function/invocations"


@pytest.fixture(scope="module")
def ryhti_client_url(docker_ip, docker_services):
    port = docker_services.port_for("ryhti_client", 8080)
    return f"http://{docker_ip}:{port}/2015-03-31/functions/function/invocations"


@pytest.fixture(scope="module")
def mml_loader_url(docker_ip, docker_services):
    port = docker_services.port_for("mml_loader", 8080)
    return f"http://{docker_ip}:{port}/2015-03-31/functions/function/invocations"


@pytest.fixture()
def create_db(db_manager_url, main_db_params, root_db_params):
    payload = {
        "action": "create_db",
    }
    r = requests.post(db_manager_url, data=json.dumps(payload))
    data = r.json()
    assert data["statusCode"] == 200, data["body"]
    yield

    drop_hame_db(main_db_params, root_db_params)


@pytest.fixture()
def populate_koodistot(koodistot_loader_url, main_db_params, create_db):
    payload = {}
    r = requests.post(koodistot_loader_url, data=json.dumps(payload))
    data = r.json()
    assert data["statusCode"] == 200, data["body"]


@pytest.fixture()
def populate_suomifi_koodistot(koodistot_loader_url, main_db_params, create_db):
    payload = {"local_codes": False}
    r = requests.post(koodistot_loader_url, data=json.dumps(payload))
    data = r.json()
    assert data["statusCode"] == 200, data["body"]


@pytest.fixture()
def populate_local_koodistot(koodistot_loader_url, main_db_params, create_db):
    payload = {"suomifi_codes": False}
    r = requests.post(koodistot_loader_url, data=json.dumps(payload))
    data = r.json()
    assert data["statusCode"] == 200, data["body"]


def test_create_db(create_db, main_db_params_with_root_user):
    """
    Test the whole lambda endpoint
    """
    conn = psycopg2.connect(**main_db_params_with_root_user)
    try:
        with conn.cursor() as cur:
            assert_database_is_alright(cur)
    finally:
        conn.close()


def test_populate_koodistot(populate_koodistot, main_db_params):
    """
    Test the whole lambda endpoint
    """
    conn = psycopg2.connect(**main_db_params)
    try:
        with conn.cursor() as cur:
            for name, value in inspect.getmembers(codes, inspect.isclass):
                if issubclass(value, codes.CodeBase) and (
                    # some code tables have external source, some have local source, some have both
                    value.code_list_uri
                    or value.local_codes
                ):
                    print(value)
                    cur.execute(f"SELECT count(*) FROM codes.{value.__tablename__}")
                    code_count = cur.fetchone()[0]
                    assert code_count > 0
    finally:
        conn.close()


def test_populate_suomifi_koodistot(populate_suomifi_koodistot, main_db_params):
    """
    Test only suomi.fi codes
    """
    conn = psycopg2.connect(**main_db_params)
    try:
        with conn.cursor() as cur:
            for name, value in inspect.getmembers(codes, inspect.isclass):
                if (
                    value is not codes.CodeBase
                    and issubclass(value, codes.CodeBase)
                    and (
                        # some code tables have external source, some have local source, some have both
                        value.code_list_uri
                    )
                ):
                    cur.execute(f"SELECT count(*) FROM codes.{value.__tablename__}")
                    code_count = cur.fetchone()[0]
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
                    code_count = cur.fetchone()[0]
                    assert code_count == 0
    finally:
        conn.close()


def test_populate_local_koodistot(populate_local_koodistot, main_db_params):
    """
    Test only local codes
    """
    conn = psycopg2.connect(**main_db_params)
    try:
        with conn.cursor() as cur:
            for name, value in inspect.getmembers(codes, inspect.isclass):
                if (
                    value is not codes.CodeBase
                    and issubclass(value, codes.CodeBase)
                    and (
                        # some code tables have external source, some have local source, some have both
                        not value.local_codes
                    )
                ):
                    cur.execute(f"SELECT count(*) FROM codes.{value.__tablename__}")
                    code_count = cur.fetchone()[0]
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
                    code_count = cur.fetchone()[0]
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
    ],
)
def get_all_plans(
    request,
    ryhti_client_url,
    complete_test_plan,
    another_test_plan,
    desired_plan_dict,
    another_plan_dict,
):
    """
    Get invalid plan JSONs from lambda. The plans should be validated separately.

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


def test_get_all_plans(get_all_plans, main_db_params):
    """
    Test the whole lambda endpoint with an invalid plan
    """
    # getting plan JSON from lambda should not run validations
    conn = psycopg2.connect(**main_db_params)
    try:
        with conn.cursor() as cur:
            # Check that plans are NOT validated
            cur.execute(f"SELECT validated_at, validation_errors FROM hame.plan")
            validation_date, errors = cur.fetchone()
            assert not validation_date
            assert not errors
            validation_date, errors = cur.fetchone()
            assert not validation_date
            assert not errors
    finally:
        conn.close()


@pytest.fixture()
def get_single_plan(
    ryhti_client_url, complete_test_plan, another_test_plan, desired_plan_dict
):
    """
    Get single plan JSON from lambda by id. Another plan in the database should not be
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


def test_get_single_plan(get_single_plan, main_db_params):
    """
    Test the whole lambda endpoint with single_plan
    """
    # getting plan JSON from lambda should not run validations
    conn = psycopg2.connect(**main_db_params)
    try:
        with conn.cursor() as cur:
            # Check that plans are NOT validated
            cur.execute(f"SELECT validated_at, validation_errors FROM hame.plan")
            validation_date, errors = cur.fetchone()
            assert not validation_date
            assert not errors
            validation_date, errors = cur.fetchone()
            assert not validation_date
            assert not errors
    finally:
        conn.close()


@pytest.fixture()
def validate_all_plans(ryhti_client_url, complete_test_plan, another_test_plan):
    """
    Validate valid and invalid Ryhti plans against the Ryhti API.

    An invalid plan should make lambda return http 200 OK (to indicate that the validation
    has been run successfully), with the validation errors returned in the payload.
    """
    payload = {"action": "validate_plans", "save_json": True}
    r = requests.post(ryhti_client_url, data=json.dumps(payload))
    data = r.json()
    print(data)
    assert data["statusCode"] == 200
    body = data["body"]
    assert body["title"] == "Plan and plan matter validations run."
    assert (
        body["details"][complete_test_plan.id]
        == f"Plan matter validation successful for {complete_test_plan.id}!"
    )
    assert (
        body["details"][another_test_plan.id]
        == f"Validation FAILED for {another_test_plan.id}."
    )
    # Our test plan is valid
    assert body["ryhti_responses"][complete_test_plan.id]["status"] == 200
    assert not body["ryhti_responses"][complete_test_plan.id]["errors"]
    # Another test plan contains nothing really
    assert body["ryhti_responses"][another_test_plan.id]["status"] == 400
    assert body["ryhti_responses"][another_test_plan.id]["errors"]


def test_validate_all_plans(validate_all_plans, main_db_params):
    """
    Test the whole lambda endpoint with valid and invalid plans
    """
    conn = psycopg2.connect(**main_db_params)
    try:
        with conn.cursor() as cur:
            cur.execute(f"SELECT validated_at, validation_errors FROM hame.plan")
            validation_date, errors = cur.fetchone()
            assert validation_date
            assert errors
            validation_date, errors = cur.fetchone()
            assert validation_date
            assert errors == "Kaava-asia on validi ja sen voi viedä Ryhtiin."
    finally:
        conn.close()


@pytest.fixture()
def validate_single_invalid_plan(
    ryhti_client_url, complete_test_plan, another_test_plan
):
    """
    Validate an invalid Ryhti plan against the Ryhti API.

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
    assert body["title"] == "Plan and plan matter validations run."
    # Check that other plan is NOT reported validated
    assert len(body["details"]) == 1
    assert (
        body["details"][another_test_plan.id]
        == f"Validation FAILED for {another_test_plan.id}."
    )
    assert len(body["ryhti_responses"]) == 1
    assert body["ryhti_responses"][another_test_plan.id]["status"] == 400
    assert body["ryhti_responses"][another_test_plan.id]["errors"]


def test_validate_single_invalid_plan(validate_single_invalid_plan, main_db_params):
    """
    Test the whole lambda endpoint with an invalid plan
    """
    conn = psycopg2.connect(**main_db_params)
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"SELECT validated_at, validation_errors FROM hame.plan ORDER BY modified_at DESC"
            )
            validation_date, errors = cur.fetchone()
            assert validation_date
            assert errors
            # Check that other plan is NOT marked validated
            validation_date, errors = cur.fetchone()
            assert not validation_date
            assert not errors
    finally:
        conn.close()


@pytest.fixture()
def validate_valid_plan_in_preparation(ryhti_client_url, complete_test_plan):
    """
    Validate a valid Ryhti plan against the Ryhti API. This guarantees that the Ryhti
    plan is formed according to spec and passes open Ryhti API validation.

    After Ryhti reports the plan as valid, the client proceeds to validate the plan
    matter.

    Since local tests or CI/CD cannot connect to X-Road servers, we validate the plan
    *matter* against a Mock X-Road API that returns a permanent plan identifier and
    responds with 200 OK. Therefore, for the X-Road APIs, this only guarantees that
    the lambda runs correctly, not that the plan *matter* is formed according to spec.

    A valid plan should make lambda return http 200 OK (to indicate that the validation
    has been run successfully), with the validation errors list empty and validation
    warnings returned.
    """
    payload = {"action": "validate_plans", "save_json": True}
    r = requests.post(ryhti_client_url, data=json.dumps(payload))
    data = r.json()
    print(data)
    assert data["statusCode"] == 200
    body = data["body"]
    assert body["title"] == "Plan and plan matter validations run."
    assert (
        body["details"][complete_test_plan.id]
        == f"Plan matter validation successful for {complete_test_plan.id}!"
    )
    assert body["ryhti_responses"][complete_test_plan.id]["status"] == 200
    assert body["ryhti_responses"][complete_test_plan.id]["warnings"]
    assert not body["ryhti_responses"][complete_test_plan.id]["errors"]


def test_validate_valid_plan_matter_in_preparation(
    validate_valid_plan_in_preparation, main_db_params
):
    """
    Test the whole lambda endpoint with a valid plan and plan matter in preparation
    stage. Plan is validated with public Ryhti API. Validate plan matter with mock
    X-Road API.

    The mock X-Road should return a permanent identifier and report the plan matter
    as valid.
    """
    conn = psycopg2.connect(**main_db_params)
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"SELECT validated_at, validation_errors, permanent_plan_identifier FROM hame.plan"
            )
            validation_date, errors, permanent_plan_identifier = cur.fetchone()
            assert validation_date
            assert errors == "Kaava-asia on validi ja sen voi viedä Ryhtiin."
            assert permanent_plan_identifier == "MK-123456"
    finally:
        conn.close()


@pytest.fixture()
def post_plans_in_preparation(ryhti_client_url, complete_test_plan, another_test_plan):
    """
    Validate and POST all valid plans to the mock X-Road API. As earlier, plans are first
    validated with public API, and valid plan matters validated with mock X-Road API.

    POSTing plans should make lambda return http 200 OK (to indicate that the validations/POSTs
    have been run successfully), with the validation errors list empty and validation
    warnings returned (if plan was valid) or validation errors (if plan was invalid).
    """
    payload = {"action": "post_plans", "save_json": True}
    r = requests.post(ryhti_client_url, data=json.dumps(payload))
    data = r.json()
    print(data)
    assert data["statusCode"] == 200
    body = data["body"]
    assert (
        body["title"]
        == "Plan and plan matter validations run. Valid marked plan matters POSTed."
    )
    assert (
        body["details"][complete_test_plan.id]
        == f"Plan matter or plan matter phase POST successful for {complete_test_plan.id}!"
    )
    assert (
        body["details"][another_test_plan.id]
        == f"Validation FAILED for {another_test_plan.id}."
    )
    # Valid plan was posted
    assert body["ryhti_responses"][complete_test_plan.id]["status"] == 201
    assert body["ryhti_responses"][complete_test_plan.id]["warnings"]
    assert not body["ryhti_responses"][complete_test_plan.id]["errors"]
    # Another plan was invalid and not posted
    assert body["ryhti_responses"][another_test_plan.id]["status"] == 400
    assert not body["ryhti_responses"][another_test_plan.id]["warnings"]
    assert body["ryhti_responses"][another_test_plan.id]["errors"]


def test_post_plans_in_preparation(post_plans_in_preparation, main_db_params):
    """
    Test the whole lambda endpoint with multiple plans and plan matters in preparation
    stage. Plans are validated with public Ryhti API. Validate and POST plan matters with
    mock X-Road API.

    The mock X-Road should return permanent identifier and report the plan matter
    as valid for the valid plan. Non-valid plan is not processed with X-Road.

    After reporting the plan matter as valid, the mock X-Road should accept POSTed
    plan matter and report the plan matter as being created in Ryhti.
    """
    conn = psycopg2.connect(**main_db_params)
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"SELECT validated_at, validation_errors, permanent_plan_identifier, to_be_exported, exported_at FROM hame.plan ORDER BY modified_at DESC"
            )
            (
                validation_date,
                errors,
                permanent_plan_identifier,
                to_be_exported,
                exported_at,
            ) = cur.fetchone()
            assert validation_date
            assert errors == "Uusi kaava-asian vaihe on viety Ryhtiin."
            assert permanent_plan_identifier == "MK-123456"
            assert not to_be_exported
            assert exported_at
            # Check that other plan is not marked exported because it is not valid
            (
                validation_date,
                errors,
                permanent_plan_identifier,
                to_be_exported,
                exported_at,
            ) = cur.fetchone()
            assert validation_date
            assert errors
            assert not permanent_plan_identifier
            assert to_be_exported
            assert not exported_at
    finally:
        conn.close()


@pytest.fixture()
def post_valid_plan_in_preparation(
    ryhti_client_url, complete_test_plan, another_test_plan
):
    """
    Validate and POST single valid plan to the mock X-Road API. As earlier, the plan is first
    validated with public API and plan matter validated with mock X-Road API.

    A POSTed plan should make lambda return http 200 OK (to indicate that the POST
    has been run successfully), with the validation errors list empty and validation
    warnings returned.
    """
    payload = {
        "action": "post_plans",
        "plan_uuid": complete_test_plan.id,
        "save_json": True,
    }
    r = requests.post(ryhti_client_url, data=json.dumps(payload))
    data = r.json()
    print(data)
    assert data["statusCode"] == 200
    body = data["body"]
    assert (
        body["title"]
        == "Plan and plan matter validations run. Valid marked plan matters POSTed."
    )
    # Check that other plan is NOT reported exported
    assert len(body["details"]) == 1
    assert (
        body["details"][complete_test_plan.id]
        == f"Plan matter or plan matter phase POST successful for {complete_test_plan.id}!"
    )
    assert len(body["ryhti_responses"]) == 1
    assert body["ryhti_responses"][complete_test_plan.id]["status"] == 201
    assert body["ryhti_responses"][complete_test_plan.id]["warnings"]
    assert not body["ryhti_responses"][complete_test_plan.id]["errors"]


def test_post_valid_plan_matter_in_preparation(
    post_valid_plan_in_preparation, main_db_params
):
    """
    Test the whole lambda endpoint with a valid plan and plan matter in preparation
    stage. Plan is validated with public Ryhti API. Validate and POST plan matter with
    mock X-Road API.

    The mock X-Road should return a permanent identifier and report the plan matter
    as valid.

    After reporting the plan matter as valid, the mock X-Road should accept POSTed
    plan matter and report the plan matter as being created in Ryhti.
    """
    conn = psycopg2.connect(**main_db_params)
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"SELECT validated_at, validation_errors, permanent_plan_identifier, to_be_exported, exported_at FROM hame.plan ORDER BY modified_at DESC"
            )
            (
                validation_date,
                errors,
                permanent_plan_identifier,
                to_be_exported,
                exported_at,
            ) = cur.fetchone()
            assert validation_date
            assert errors == "Uusi kaava-asian vaihe on viety Ryhtiin."
            assert permanent_plan_identifier == "MK-123456"
            assert not to_be_exported
            assert exported_at
            # Check that other plan is NOT validated or marked exported
            (
                validation_date,
                errors,
                permanent_plan_identifier,
                to_be_exported,
                exported_at,
            ) = cur.fetchone()
            assert not validation_date
            assert not errors
            assert not permanent_plan_identifier
            assert to_be_exported
            assert not exported_at
    finally:
        conn.close()
