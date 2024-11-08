import inspect
import json

import models
import psycopg2
import pytest
import requests
from koodistot_loader.koodistot_loader import codes
from sqlalchemy.orm import Session

from .conftest import assert_database_is_alright, assert_dicts_equal, drop_hame_db


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


@pytest.fixture()
def populate_admin_region_geometries(
    koodistot_loader_url, mml_loader_url, main_db_params, create_db
):
    payload = {}
    r = requests.post(koodistot_loader_url, data=json.dumps(payload))
    r = requests.post(mml_loader_url, data=json.dumps(payload))
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


def test_populate_admin_region_geometries(
    populate_admin_region_geometries, populate_koodistot, main_db_params
):
    """
    Test that maakunta geometries are populated
    """
    conn = psycopg2.connect(**main_db_params)
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT count(*) FROM codes.administrative_region WHERE geom IS NOT NULL"
            )
            geom_count = cur.fetchone()[0]
            assert geom_count == 19
    finally:
        conn.close()


@pytest.fixture()
def get_plan(ryhti_client_url, complete_test_plan, desired_plan_dict):
    """
    Get invalid plan JSON from lambda. The plan should be validated separately.

    Getting plan should make lambda return http 200 OK (to indicate that serialization
    has been run successfully), with the ryhti_responses dict empty, and details
    dict containing the serialized plan(s).
    """
    payload = {"action": "get_plans", "save_json": True}
    r = requests.post(ryhti_client_url, data=json.dumps(payload))
    data = r.json()
    print(data)
    assert data["statusCode"] == 200
    assert data["title"] == "Returning serialized plans from database."
    assert_dicts_equal(data["details"][complete_test_plan.id], desired_plan_dict)
    assert not data["ryhti_responses"]


def test_get_plan(get_plan, main_db_params):
    """
    Test the whole lambda endpoint with an invalid plan
    """
    # getting plan JSON from lambda should not run validations
    conn = psycopg2.connect(**main_db_params)
    try:
        with conn.cursor() as cur:
            cur.execute(f"SELECT validated_at, validation_errors FROM hame.plan")
            validation_date, errors = cur.fetchone()
            assert not validation_date
            assert not errors
    finally:
        conn.close()


@pytest.fixture()
def validate_invalid_plan(ryhti_client_url, complete_test_plan):
    """
    Validate an invalid Ryhti plan against the Ryhti API. Complete test plan is not yet a
    valid plan, because it contains test code values.

    An invalid plan should make lambda return http 200 OK (to indicate that the validation
    has been run successfully), with the validation errors returned in the payload.
    """
    payload = {"action": "validate_plans", "save_json": True}
    r = requests.post(ryhti_client_url, data=json.dumps(payload))
    data = r.json()
    print(data)
    assert data["statusCode"] == 200
    assert data["title"] == "Plan and plan matter validations run."
    assert (
        data["details"][complete_test_plan.id]
        == f"Validation FAILED for {complete_test_plan.id}."
    )
    # our invalid plan is not valid, because it has certain invalid code combinations
    assert data["ryhti_responses"][complete_test_plan.id]["status"] == 422
    assert data["ryhti_responses"][complete_test_plan.id]["errors"]


def test_validate_invalid_plan(validate_invalid_plan, main_db_params):
    """
    Test the whole lambda endpoint with an invalid plan
    """
    conn = psycopg2.connect(**main_db_params)
    try:
        with conn.cursor() as cur:
            cur.execute(f"SELECT validated_at, validation_errors FROM hame.plan")
            validation_date, errors = cur.fetchone()
            assert validation_date
            assert errors
    finally:
        conn.close()


@pytest.fixture()
def valid_plan_in_preparation(
    session: Session,
    complete_test_plan: models.Plan,
    land_use_area_instance: models.LandUseArea,
    land_use_point_instance: models.LandUsePoint,
    empty_value_plan_regulation_instance: models.PlanRegulation,
    text_plan_regulation_instance: models.PlanRegulation,
    point_text_plan_regulation_instance: models.PlanRegulation,
    numeric_plan_regulation_instance: models.PlanRegulation,
    verbal_plan_regulation_instance: models.PlanRegulation,
    general_plan_regulation_instance: models.PlanRegulation,
    plan_proposition_instance: models.PlanProposition,
):
    """
    Valid Ryhti plan in preparation phase.

    Complete test plan is not yet quite valid. Fulfil some validation rules regarding
    code values.
    """
    session.add(point_text_plan_regulation_instance)
    session.add(numeric_plan_regulation_instance)
    session.add(verbal_plan_regulation_instance)
    session.add(general_plan_regulation_instance)

    # General and verbal regulation type may *not* be intended use regulation!
    verbal_plan_regulation_instance.intended_use = None
    general_plan_regulation_instance.intended_use = None
    # Also, points cannot have intended use at the moment, though they should
    # be able to, they have detached houses type after all.
    point_text_plan_regulation_instance.intended_use = None

    # Numeric plan regulations are actually not allowed in maakuntakaava. So let's
    # put in a text value instead:
    numeric_plan_regulation_instance.numeric_value = None
    numeric_plan_regulation_instance.text_value = {
        "fin": "Olisimme kovasti halunneet tähän numeerisen määräyksen."
    }

    session.commit()
    return complete_test_plan


@pytest.fixture()
def validate_valid_plan_in_preparation(ryhti_client_url, valid_plan_in_preparation):
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
    assert data["title"] == "Plan and plan matter validations run."
    assert (
        data["details"][valid_plan_in_preparation.id]
        == f"Plan matter validation successful for {valid_plan_in_preparation.id}!"
    )
    assert data["ryhti_responses"][valid_plan_in_preparation.id]["status"] == 200
    assert data["ryhti_responses"][valid_plan_in_preparation.id]["warnings"]
    assert not data["ryhti_responses"][valid_plan_in_preparation.id]["errors"]


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
def post_valid_plan_in_preparation(ryhti_client_url, valid_plan_in_preparation):
    """
    Validate and POST a valid plan to the mock X-Road API. As earlier, the plan is first
    validated with public API and plan matter validated with mock X-Road API.

    A POSTed plan should make lambda return http 200 OK (to indicate that the POST
    has been run successfully), with the validation errors list empty and validation
    warnings returned.
    """
    payload = {"action": "post_plans", "save_json": True}
    r = requests.post(ryhti_client_url, data=json.dumps(payload))
    data = r.json()
    print(data)
    assert data["statusCode"] == 200
    assert (
        data["title"]
        == "Plan and plan matter validations run. Marked plan matters POSTed."
    )
    assert (
        data["details"][valid_plan_in_preparation.id]
        == f"Plan matter or plan matter phase POST successful for {valid_plan_in_preparation.id}!"
    )
    assert data["ryhti_responses"][valid_plan_in_preparation.id]["status"] == 201
    assert data["ryhti_responses"][valid_plan_in_preparation.id]["warnings"]
    assert not data["ryhti_responses"][valid_plan_in_preparation.id]["errors"]


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
                f"SELECT validated_at, validation_errors, permanent_plan_identifier, to_be_exported, exported_at FROM hame.plan"
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
    finally:
        conn.close()
