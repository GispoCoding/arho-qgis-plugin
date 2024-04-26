import inspect
import json

import models
import psycopg2
import pytest
import requests
from koodistot_loader.koodistot_loader import codes
from sqlalchemy.orm import Session

from .conftest import assert_database_is_alright, drop_hame_db


@pytest.fixture()
def db_manager_url(docker_ip, docker_services):
    port = docker_services.port_for("db_manager", 8080)
    return f"http://{docker_ip}:{port}/2015-03-31/functions/function/invocations"


@pytest.fixture()
def koodistot_loader_url(docker_ip, docker_services):
    port = docker_services.port_for("koodistot_loader", 8080)
    return f"http://{docker_ip}:{port}/2015-03-31/functions/function/invocations"


@pytest.fixture()
def ryhti_client_url(docker_ip, docker_services):
    port = docker_services.port_for("ryhti_client", 8080)
    return f"http://{docker_ip}:{port}/2015-03-31/functions/function/invocations"


@pytest.fixture()
def create_db(db_manager_url, main_db_params, root_db_params):
    payload = {
        "event_type": 1,
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
def validate_invalid_plan(ryhti_client_url, complete_test_plan):
    """
    Validate an invalid Ryhti plan against the Ryhti API. Complete test plan is not yet a
    valid plan, because it contains test code values.

    An invalid plan should make lambda return http 200 OK (to indicate that the validation
    has been run successfully), with the validation errors returned in the payload.
    """
    payload = {"event_type": 1, "save_json": True}
    r = requests.post(ryhti_client_url, data=json.dumps(payload))
    data = r.json()
    print(data)
    assert data["statusCode"] == 200
    assert data["title"] == "Plan validations run."
    assert (
        data["details"][complete_test_plan.id]
        == f"Validation FAILED for {complete_test_plan.id}."
    )
    # our invalid plan has invalid code uri value. For some reason, the Ryhti API
    # currently considers this as a JSON deserialization error (which it is not),
    # so it returns HTTP 400 instead of 422.
    assert data["ryhti_responses"][complete_test_plan.id]["status"] == 400
    assert data["ryhti_responses"][complete_test_plan.id]["errors"]


@pytest.fixture()
def valid_plan(
    session: Session, populate_koodistot: None, complete_test_plan: models.Plan
):
    """
    Complete test plan is not yet a valid plan, because it contains test code values.
    Replace them with actual imported Ryhti codes to pass validation:
    """
    session.add(complete_test_plan)
    complete_test_plan.lifecycle_status = (
        session.query(codes.LifeCycleStatus).filter_by(value="01").first()
    )
    # TODO
    session.commit()
    return complete_test_plan


@pytest.fixture()
def validate_valid_plan(ryhti_client_url, valid_plan):
    """
    Validate a valid Ryhti plan against the Ryhti API.

    A valid plan should make lambda return http 200 OK (to indicate that the validation
    has been run successfully), with the validation errors list empty.
    """
    payload = {"event_type": 1, "save_json": True}
    r = requests.post(ryhti_client_url, data=json.dumps(payload))
    data = r.json()
    print(data)
    assert data["statusCode"] == 200
    assert data["title"] == "Plan validations run."
    assert (
        data["details"][valid_plan.id] == f"Validation succeeded for {valid_plan.id}!"
    )
    assert data["ryhti_responses"][valid_plan.id]["status"] == 200
    assert not data["ryhti_responses"][valid_plan.id]["errors"]


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


def test_validate_valid_plan(validate_valid_plan, main_db_params):
    """
    Test the whole lambda endpoint with a valid plan
    """
    conn = psycopg2.connect(**main_db_params)
    try:
        with conn.cursor() as cur:
            cur.execute(f"SELECT validated_at, validation_errors FROM hame.plan")
            validation_date, errors = cur.fetchone()
            assert validation_date
            assert not errors
    finally:
        conn.close()
