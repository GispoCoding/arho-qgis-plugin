from uuid import UUID

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import models
from ryhti_client.database_client import DatabaseClient, PlanAlreadyExistsError


@pytest.fixture
def database_client(rw_connection_string: str) -> DatabaseClient:
    return DatabaseClient(rw_connection_string)


@pytest.fixture
def extra_data(plan_type_instance, organisation_instance) -> dict:
    return {
        "name": "test_plan",
        "plan_type_id": plan_type_instance.id,
        "organization_id": organisation_instance.id,
    }


def test_import_plan(
    codes_loaded: None,
    database_client: DatabaseClient,
    session: Session,
    extra_data: dict,
    complete_plan_json: str,
):
    """Imports complete_test_plan.json and checks that the data was imported correctly."""
    COMPLETE_PLAN_ID = "09c62caa-c56f-474d-9c0a-1ba4c4188cb2"
    # delete_plan_after_test(COMPLETE_PLAN_ID)

    imported_plan_id = database_client.import_plan(
        complete_plan_json,
        extra_data=extra_data,
    )
    assert imported_plan_id == UUID(COMPLETE_PLAN_ID)

    plan = session.get(models.Plan, COMPLETE_PLAN_ID)
    assert plan is not None
    assert plan.name == {"fin": "test_plan"}
    assert plan.lifecycle_status.value == "03"
    assert {e.value for e in plan.legal_effects_of_master_plan} == {"2"}
    assert plan.scale == 1
    # TODO: plan.geographicalArea
    assert plan.description == {"fin": "test_plan"}

    general_regulation_group = session.get(
        models.PlanRegulationGroup, "2757a7e0-df7d-4946-88ac-bf86579680d3"
    )
    assert general_regulation_group is not None
    assert plan.general_plan_regulation_groups == [general_regulation_group]
    assert general_regulation_group.name == {"fin": "test_general_regulation_group"}
    assert general_regulation_group.ordering == 6
    assert general_regulation_group.plan_propositions == []

    general_regulation = session.get(
        models.PlanRegulation, "ebacd48a-693f-47ed-a114-7e041e994824"
    )
    assert general_regulation is not None
    assert general_regulation_group.plan_regulations == [general_regulation]
    assert general_regulation.lifecycle_status.value == "03"
    assert general_regulation.type_of_plan_regulation.value == "asumisenAlue"
    assert {t.value for t in general_regulation.plan_themes} == {"01"}
    assert general_regulation.subject_identifiers == ["#test_regulation"]
    assert general_regulation.ordering == 1
    assert general_regulation.value_data_type == "LocalizedText"
    assert general_regulation.text_value == {"fin": "test_value"}

    land_use_area_1 = session.get(
        models.LandUseArea, "36178236-ead0-4e10-af3b-d9ce4e9ac330"
    )
    assert land_use_area_1 is not None
    assert land_use_area_1.lifecycle_status.value == "03"
    assert land_use_area_1.type_of_underground.value == "01"
    # TODO: land_use_area_1.geographical_area
    assert land_use_area_1.name == {"fin": "test_land_use_area"}
    assert land_use_area_1.description == {"fin": "test_land_use_area"}
    assert land_use_area_1.ordering == 1
    assert land_use_area_1.height_min == 0.0
    assert land_use_area_1.height_max == 1.0
    assert land_use_area_1.height_unit == "m"

    pedestrian_street = session.get(
        models.LandUseArea, "9e5ce5a7-f1ec-4290-a8cc-17af306a6865"
    )
    assert pedestrian_street is not None
    assert pedestrian_street.lifecycle_status.value == "03"
    assert pedestrian_street.type_of_underground.value == "01"
    # TODO: pedestrian_street.geographical_area
    assert pedestrian_street.name == {"fin": "test_pedestrian_street"}
    assert pedestrian_street.description == {"fin": "test_pedestrian_street"}
    assert pedestrian_street.ordering == 2
    assert pedestrian_street.height_min == 0.0
    assert pedestrian_street.height_max == 1.0
    assert pedestrian_street.height_unit == "m"

    sub_area = session.get(models.OtherArea, "40a54a87-c363-4a37-91bb-2f5f71fe7a53")
    assert sub_area is not None
    assert sub_area.lifecycle_status.value == "03"
    assert sub_area.type_of_underground.value == "01"
    assert sub_area.name is None
    assert sub_area.description is None

    land_use_point = session.get(
        models.LandUsePoint, "bb50b5a0-ef60-40e7-bee0-a1ae927d020f"
    )
    assert land_use_point is not None
    assert land_use_point.lifecycle_status.value == "03"
    assert land_use_point.type_of_underground.value == "01"
    assert land_use_point.name == {"fin": "test_land_use_point"}
    assert land_use_point.description == {"fin": "test_land_use_point"}
    assert land_use_point.ordering is None

    assert plan.land_use_areas == [land_use_area_1, pedestrian_street]
    assert plan.land_use_points == [land_use_point]
    assert plan.other_areas == [sub_area]

    point_plan_regulation_group = session.get(
        models.PlanRegulationGroup, "a804b7a3-eeb2-467e-a5fb-1d74d273e467"
    )
    assert point_plan_regulation_group is not None
    assert point_plan_regulation_group.name == {
        "fin": "test_point_plan_regulation_group"
    }
    assert point_plan_regulation_group.short_name == "L"
    assert point_plan_regulation_group.ordering == 1

    point_plan_regulation = session.get(
        models.PlanRegulation, "03f71bf5-e08c-4530-8e65-b86c20db26cf"
    )
    assert point_plan_regulation is not None
    assert point_plan_regulation_group.plan_regulations == [point_plan_regulation]
    assert point_plan_regulation.lifecycle_status.value == "03"
    assert point_plan_regulation.type_of_plan_regulation.value == "asumisenAlue"
    assert {t.value for t in point_plan_regulation.plan_themes} == {"01"}
    assert point_plan_regulation.subject_identifiers == ["#test_regulation"]
    assert point_plan_regulation.ordering == 1
    assert point_plan_regulation.additional_information == []
    assert point_plan_regulation.value_data_type == "LocalizedText"
    assert point_plan_regulation.text_value == {"fin": "test_value"}

    plan_regulation_with_additional_info = session.get(
        models.PlanRegulation, "ca5bc558-9fa4-4896-a42f-df3a1c750632"
    )
    assert plan_regulation_with_additional_info is not None
    assert {
        ai.type_of_additional_information.value
        for ai in plan_regulation_with_additional_info.additional_information
    } == {"paakayttotarkoitus", "kayttotarkoituksenOsuusKerrosalastaK-m2"}
    ai_with_value = next(
        (
            ai
            for ai in plan_regulation_with_additional_info.additional_information
            if ai.type_of_additional_information.value
            == "kayttotarkoituksenOsuusKerrosalastaK-m2"
        ),
        None,
    )
    assert ai_with_value is not None
    assert ai_with_value.value_data_type == "PositiveNumeric"
    assert ai_with_value.numeric_value == 2500
    assert ai_with_value.unit == "k-m2"

    # TODO: rest of plan_regulation_groups
    # TODO: periodOfValidity - not implemented yet
    # TODO: approvalDate
    # TODO: planMaps
    # TODO: planAnnexes
    # TODO: otherPlanMaterials - not implemented yet
    # TODO: planReport - not implemented yet


def test_import_duplicate_plan(
    codes_loaded: None,
    database_client: DatabaseClient,
    extra_data: dict,
    simple_plan_json: str,
):
    database_client.import_plan(simple_plan_json, extra_data=extra_data)
    with pytest.raises(PlanAlreadyExistsError):
        database_client.import_plan(simple_plan_json, extra_data=extra_data)


def test_import_duplicate_plan_with_overwriting(
    codes_loaded: None,
    database_client: DatabaseClient,
    session: Session,
    extra_data: dict,
    simple_plan_json: str,
):
    SIMPLE_PLAN_ID = "7f522b2f-8b45-4a17-b433-5f47271b579e"

    database_client.import_plan(simple_plan_json, extra_data=extra_data)
    original_created = session.scalars(
        select(models.Plan.created_at).where(models.Plan.id == SIMPLE_PLAN_ID)
    ).one()

    database_client.import_plan(simple_plan_json, extra_data=extra_data, overwrite=True)
    overwritten_created = session.scalars(
        select(models.Plan.created_at).where(models.Plan.id == SIMPLE_PLAN_ID)
    ).one()

    assert original_created < overwritten_created


def test_import_invalid_plan(
    database_client: DatabaseClient,
    extra_data: dict,
    invalid_plan_json: str,
):
    """Tries to import invalid_plan.json and checks that the import fails.

    invalid_plan.json is missing a required field (lifeCycleStatus)
    """

    with pytest.raises(ValueError) as excinfo:
        database_client.import_plan(invalid_plan_json, extra_data)

    error_message = str(excinfo.value)
    assert "Invalid plan data:" in error_message
    assert "lifeCycleStatus" in error_message


def test_import_invalid_extra_data(
    database_client: DatabaseClient,
    simple_plan_json: str,
):
    """Tries to import a plan with invalid extra_data and checks that the import fails."""

    extra_data = {
        "name": "test_plan",
        # "plan_type_id" is missing
        "organization_id": "invalid-uuid",  # invalid UUID
    }

    with pytest.raises(ValueError) as excinfo:
        database_client.import_plan(simple_plan_json, extra_data)

    error_message = str(excinfo.value)
    assert "Invalid extra data" in error_message
    assert "plan_type_id" in error_message
    assert "organization_id" in error_message
