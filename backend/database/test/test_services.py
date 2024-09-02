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
def mml_loader_url(docker_ip, docker_services):
    port = docker_services.port_for("mml_loader", 8080)
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
    populate_koodistot: None,
    complete_test_plan: models.Plan,
    land_use_area_instance: models.LandUseArea,
    text_plan_regulation_instance: models.PlanRegulation,
    numeric_plan_regulation_instance: models.PlanRegulation,
    verbal_plan_regulation_instance: models.PlanRegulation,
    general_plan_regulation_instance: models.PlanRegulation,
    plan_proposition_instance: models.PlanProposition,
):
    """
    Valid Ryhti plan in preparation phase.

    Complete test plan is not yet a valid plan, because it contains test code values.
    Replace them with actual imported Ryhti codes to pass validation:
    """
    session.add(complete_test_plan)
    session.add(land_use_area_instance)
    session.add(text_plan_regulation_instance)
    session.add(numeric_plan_regulation_instance)
    session.add(verbal_plan_regulation_instance)
    session.add(plan_proposition_instance)
    session.add(general_plan_regulation_instance)

    # Elinkaaren vaihe
    preparation_lifecycle_status = (
        session.query(codes.LifeCycleStatus).filter_by(value="03").first()
    )
    complete_test_plan.lifecycle_status = preparation_lifecycle_status
    land_use_area_instance.lifecycle_status = preparation_lifecycle_status
    text_plan_regulation_instance.lifecycle_status = preparation_lifecycle_status
    numeric_plan_regulation_instance.lifecycle_status = preparation_lifecycle_status
    verbal_plan_regulation_instance.lifecycle_status = preparation_lifecycle_status
    general_plan_regulation_instance.lifecycle_status = preparation_lifecycle_status
    plan_proposition_instance.lifecycle_status = preparation_lifecycle_status

    # Kaavoitusteema
    community_structure_theme = (
        session.query(codes.PlanTheme).filter_by(value="01").first()
    )
    plan_proposition_instance.plan_theme = community_structure_theme
    text_plan_regulation_instance.plan_theme = community_structure_theme
    numeric_plan_regulation_instance.plan_theme = community_structure_theme
    verbal_plan_regulation_instance.plan_theme = community_structure_theme
    general_plan_regulation_instance.plan_theme = community_structure_theme

    # Kaavamääräyksen tyyppi
    detached_houses_type = (
        session.query(codes.TypeOfPlanRegulation)
        .filter_by(value="asumisenAlue")
        .first()
    )
    text_plan_regulation_instance.type_of_plan_regulation = detached_houses_type
    numeric_plan_regulation_instance.type_of_plan_regulation = detached_houses_type
    general_plan_regulation_instance.type_of_plan_regulation = detached_houses_type
    verbal_type = (
        session.query(codes.TypeOfPlanRegulation)
        .filter_by(value="sanallinenMaarays")
        .first()
    )
    verbal_plan_regulation_instance.type_of_plan_regulation = verbal_type

    # Sanallisen kaavamääräyksen laji
    foundation_type_of_verbal_regulation = (
        session.query(codes.TypeOfVerbalPlanRegulation)
        .filter_by(value="perustaminen")
        .first()
    )
    verbal_plan_regulation_instance.type_of_verbal_plan_regulation = (
        foundation_type_of_verbal_regulation
    )

    # Kaavamääräyksen lisätiedon laji
    principal_intended_use_type_of_additional_information = (
        session.query(codes.TypeOfAdditionalInformation)
        .filter_by(value="paakayttotarkoitus")
        .first()
    )
    text_plan_regulation_instance.intended_use = (
        principal_intended_use_type_of_additional_information
    )
    numeric_plan_regulation_instance.intended_use = (
        principal_intended_use_type_of_additional_information
    )
    # General and verbal regulation type may *not* be intended use regulation!
    verbal_plan_regulation_instance.intended_use = None
    general_plan_regulation_instance.intended_use = None

    # Kaavan tyyppi
    overall_regional_plan_plan_type = (
        session.query(codes.PlanType).filter_by(value="11").first()
    )
    complete_test_plan.plan_type = overall_regional_plan_plan_type

    # Hallinnollinen alue
    uusimaa_administrative_region = (
        session.query(codes.AdministrativeRegion).filter_by(value="01").first()
    )
    complete_test_plan.organisation.administrative_region = (
        uusimaa_administrative_region
    )

    # Maanalaisuuden laji
    overground_type_of_underground = (
        session.query(codes.TypeOfUnderground).filter_by(value="01").first()
    )
    land_use_area_instance.type_of_underground = overground_type_of_underground

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
        data["details"][valid_plan_in_preparation.id]
        == f"Validation successful for {valid_plan_in_preparation.id}!"
    )
    assert data["ryhti_responses"][valid_plan_in_preparation.id]["status"] == 200
    assert not data["ryhti_responses"][valid_plan_in_preparation.id]["errors"]


def test_validate_valid_plan_in_preparation(
    validate_valid_plan_in_preparation, main_db_params
):
    """
    Test the whole lambda endpoint with a valid plan in preparation stage
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
