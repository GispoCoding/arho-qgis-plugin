import inspect
import json

import psycopg2
import pytest
import requests
from sqlalchemy.orm import Session

from database import models
from lambdas.koodistot_loader.koodistot_loader import codes

from .conftest import assert_database_is_alright, deepcompare, drop_hame_db


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
            assert errors == "Kaava on validi. Kaava-asiaa ei ole vielä validoitu."
            validation_date, errors = cur.fetchone()
            assert validation_date
            assert errors
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
def get_permanent_plan_identifier(
    ryhti_client_url, complete_test_plan, another_test_plan, desired_plan_dict
):
    """
    Get a permanent plan identifier from X-road. Another plan in the database should not
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


def test_get_permanent_plan_identifier(get_permanent_plan_identifier, main_db_params):
    """
    Test the whole lambda endpoint with single_plan
    """
    # getting permanent identifier from lambda should not run validations
    conn = psycopg2.connect(**main_db_params)
    try:
        with conn.cursor() as cur:
            # Check that plans are NOT validated
            cur.execute(
                f"SELECT validated_at, validation_errors, permanent_plan_identifier FROM hame.plan"
            )
            validation_date, errors, permanent_plan_identifier = cur.fetchone()
            assert not validation_date
            assert not errors
            assert not permanent_plan_identifier
            validation_date, errors, permanent_plan_identifier = cur.fetchone()
            assert not validation_date
            assert not errors
            assert permanent_plan_identifier == "MK-123456"
    finally:
        conn.close()


@pytest.fixture()
def validate_valid_plan_matter_in_preparation(ryhti_client_url, complete_test_plan):
    """
    Validate a valid Ryhti plan and plan matter against the Ryhti API. This guarantees
    that the Ryhti plan is formed according to spec and passes open Ryhti API validation.

    If the plan has a permanent plan identifier, the client proceeds to also validate
    the plan matter.

    Since local tests or CI/CD cannot connect to X-Road servers, we validate the plan
    *matter* against a Mock X-Road API that  responds with 200 OK. Therefore, for the
    X-Road APIs, this only guarantees that the lambda runs correctly, not that the plan
    *matter* is formed according to spec.

    A valid plan should make lambda return http 200 OK (to indicate that the validation
    has been run successfully), with the validation errors list empty and validation
    warnings returned.
    """
    payload = {
        "action": "get_permanent_plan_identifiers",
        "plan_uuid": complete_test_plan.id,
        "save_json": True,
    }
    r = requests.post(ryhti_client_url, data=json.dumps(payload))
    # now the plan has permanent identifier, we can proceed:
    payload = {
        "action": "validate_plan_matters",
        "plan_uuid": complete_test_plan.id,
        "save_json": True,
    }
    r = requests.post(ryhti_client_url, data=json.dumps(payload))
    data = r.json()
    print(data)
    assert data["statusCode"] == 200
    body = data["body"]
    assert body["title"] == "Plan matter validations run."
    assert (
        body["details"][complete_test_plan.id]
        == f"Plan matter validation successful for {complete_test_plan.id}!"
    )
    assert body["ryhti_responses"][complete_test_plan.id]["status"] == 200
    assert body["ryhti_responses"][complete_test_plan.id]["warnings"]
    assert not body["ryhti_responses"][complete_test_plan.id]["errors"]


def test_validate_valid_plan_matter_in_preparation(
    validate_valid_plan_matter_in_preparation, main_db_params
):
    """
    Test the whole lambda endpoint with a valid plan and plan matter in preparation
    stage. Plan is validated with public Ryhti API. Validate plan matter with mock
    X-Road API.

    The mock X-Road should return a permanent identifier and report the plan matter
    as valid. Also, validating plan matter should make sure that plan documents
    are included in the plan matter.
    """
    conn = psycopg2.connect(**main_db_params)
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"SELECT id, validated_at, validation_errors, permanent_plan_identifier FROM hame.plan"
            )
            (
                exported_plan_id,
                validation_date,
                errors,
                permanent_plan_identifier,
            ) = cur.fetchone()
            assert validation_date
            assert errors == "Kaava-asia on validi ja sen voi viedä Ryhtiin."
            assert permanent_plan_identifier == "MK-123456"
            # Document should be exported
            cur.execute(
                f"SELECT plan_id, exported_at, exported_file_key FROM hame.document"
            )
            plan_id, exported_at, exported_file_key = cur.fetchone()
            assert plan_id == exported_plan_id
            assert exported_at
            assert exported_file_key
    finally:
        conn.close()


@pytest.fixture()
def post_plan_matters_in_preparation(
    ryhti_client_url, complete_test_plan, another_test_plan
):
    """
    POST all plans to the mock X-Road API. Plans need not be validated, but they need
    to have permanent identifiers set.

    POSTing plans should make lambda return http 200 OK (to indicate that POSTs
    have been run successfully), with the validation errors list empty and validation
    warnings returned (if plan was valid) or validation errors (if plan was invalid).
    """
    payload = {
        "action": "get_permanent_plan_identifiers",
        "plan_uuid": complete_test_plan.id,
        "save_json": True,
    }
    r = requests.post(ryhti_client_url, data=json.dumps(payload))
    # now one plan has a permanent identifier, the other does not:
    payload = {"action": "post_plan_matters", "save_json": True}
    r = requests.post(ryhti_client_url, data=json.dumps(payload))
    data = r.json()
    print(data)
    assert data["statusCode"] == 200
    body = data["body"]
    assert body["title"] == "Plan matters POSTed."
    assert (
        body["details"][complete_test_plan.id]
        == f"Plan matter or plan matter phase POST successful for {complete_test_plan.id}."
    )
    assert (
        body["details"][another_test_plan.id]
        == f"Plan {another_test_plan.id} had no permanent identifier. Could not create plan matter!"
    )
    # Valid plan was posted
    assert body["ryhti_responses"][complete_test_plan.id]["status"] == 201
    assert body["ryhti_responses"][complete_test_plan.id]["warnings"]
    assert not body["ryhti_responses"][complete_test_plan.id]["errors"]
    # Another plan had no identifier and has no ryhti response
    assert another_test_plan.id not in body["ryhti_responses"]


def test_post_plan_matters_in_preparation(
    post_plan_matters_in_preparation, main_db_params
):
    """
    Test the whole lambda endpoint with multiple plans and plan matters in preparation
    stage. POST plan matters with mock X-Road API.

    The mock X-Road should accept POSTed plan matter and report the plan matter as being
    created in Ryhti. The plan matter without identifier should not be exported. Also,
    POSTing plan matter should make sure that plan documents are included in the plan matter.
    """
    conn = psycopg2.connect(**main_db_params)
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"SELECT id, validated_at, validation_errors, permanent_plan_identifier, exported_at FROM hame.plan ORDER BY modified_at DESC"
            )
            # Exported plan should also be reported validated
            (
                exported_plan_id,
                validation_date,
                errors,
                permanent_plan_identifier,
                exported_at,
            ) = cur.fetchone()
            assert validation_date
            assert errors == "Uusi kaava-asian vaihe on viety Ryhtiin."
            assert permanent_plan_identifier == "MK-123456"
            assert exported_at
            # Check that other plan is NOT modified because it had no identifier
            (
                other_plan_id,
                validation_date,
                errors,
                permanent_plan_identifier,
                exported_at,
            ) = cur.fetchone()
            assert not validation_date
            assert not errors
            assert not permanent_plan_identifier
            assert not exported_at
            # Document should be exported
            cur.execute(
                f"SELECT plan_id, exported_at, exported_file_key FROM hame.document"
            )
            plan_id, exported_at, exported_file_key = cur.fetchone()
            assert plan_id == exported_plan_id
            assert exported_at
            assert exported_file_key
    finally:
        conn.close()


@pytest.fixture()
def post_valid_plan_matter_in_preparation(
    ryhti_client_url, complete_test_plan, another_test_plan
):
    """
    POST single valid plan to the mock X-Road API. Plan needs not be validated.

    A POSTed plan should make lambda return http 200 OK (to indicate that the POST
    has been run successfully), with the validation errors list empty and validation
    warnings returned.
    """
    payload = {
        "action": "get_permanent_plan_identifiers",
        "plan_uuid": complete_test_plan.id,
        "save_json": True,
    }
    r = requests.post(ryhti_client_url, data=json.dumps(payload))
    # now the plan has permanent identifier, we can proceed:
    payload = {
        "action": "post_plan_matters",
        "plan_uuid": complete_test_plan.id,
        "save_json": True,
    }
    r = requests.post(ryhti_client_url, data=json.dumps(payload))
    data = r.json()
    print(data)
    assert data["statusCode"] == 200
    body = data["body"]
    assert body["title"] == "Plan matters POSTed."
    # Check that other plan is NOT processed
    assert len(body["details"]) == 1
    assert (
        body["details"][complete_test_plan.id]
        == f"Plan matter or plan matter phase POST successful for {complete_test_plan.id}."
    )
    assert len(body["ryhti_responses"]) == 1
    assert body["ryhti_responses"][complete_test_plan.id]["status"] == 201
    assert body["ryhti_responses"][complete_test_plan.id]["warnings"]
    assert not body["ryhti_responses"][complete_test_plan.id]["errors"]


def test_post_valid_plan_matter_in_preparation(
    post_valid_plan_matter_in_preparation, main_db_params
):
    """
    Test the whole lambda endpoint with a valid plan and plan matter in preparation
    stage. POST plan matter with mock X-Road API.

    The mock X-Road should accept POSTed plan matter and report the plan matter as
    being created in Ryhti. Also, POSTing plan matter should make sure that plan
    documents are included in the plan matter.
    """
    conn = psycopg2.connect(**main_db_params)
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"SELECT id, validated_at, validation_errors, permanent_plan_identifier, exported_at FROM hame.plan ORDER BY modified_at DESC"
            )
            # Exported plan should also be reported validated
            (
                exported_plan_id,
                validation_date,
                errors,
                permanent_plan_identifier,
                exported_at,
            ) = cur.fetchone()
            assert validation_date
            assert errors == "Uusi kaava-asian vaihe on viety Ryhtiin."
            assert permanent_plan_identifier == "MK-123456"
            assert exported_at
            # Check that other plan is NOT modified
            (
                other_plan_id,
                validation_date,
                errors,
                permanent_plan_identifier,
                exported_at,
            ) = cur.fetchone()
            assert not validation_date
            assert not errors
            assert not permanent_plan_identifier
            assert not exported_at
            # Document should be exported
            cur.execute(
                f"SELECT plan_id, exported_at, exported_file_key FROM hame.document"
            )
            plan_id, exported_at, exported_file_key = cur.fetchone()
            assert plan_id == exported_plan_id
            assert exported_at
            assert exported_file_key
    finally:
        conn.close()
