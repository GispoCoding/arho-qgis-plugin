from collections.abc import Callable
from datetime import date
from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from database import codes, models
from ryhti_client.database_client import DatabaseClient
from ryhti_client.plan_copier import PlanCopier


@pytest.fixture
def database_client(dba_connection_string: str) -> DatabaseClient:
    return DatabaseClient(dba_connection_string)


def test_clone_model(
    proportion_of_intended_use_additional_information_instance: models.AdditionalInformation,
):
    """Clones a model and checks that all non-relationship data was copied correctly."""
    copied_model = PlanCopier.clone_model(
        proportion_of_intended_use_additional_information_instance, id=uuid4()
    )
    copied_model_attributes = list(copied_model.__dict__.keys())
    original_model_attributes = list(
        proportion_of_intended_use_additional_information_instance.__dict__.keys()
    )
    # type_of_additional_information is a relationship attribute so it is not cloned
    original_model_attributes.remove("type_of_additional_information")
    assert sorted(original_model_attributes) == sorted(copied_model_attributes)
    assert (
        proportion_of_intended_use_additional_information_instance.value_data_type
        == copied_model.value_data_type
    )
    assert (
        proportion_of_intended_use_additional_information_instance.numeric_value
        == copied_model.numeric_value
    )
    assert (
        proportion_of_intended_use_additional_information_instance.numeric_range_min
        == copied_model.numeric_range_min
    )
    assert (
        proportion_of_intended_use_additional_information_instance.numeric_range_max
        == copied_model.numeric_range_max
    )
    assert (
        proportion_of_intended_use_additional_information_instance.text_value
        == copied_model.text_value
    )
    assert (
        proportion_of_intended_use_additional_information_instance.text_syntax
        == copied_model.text_syntax
    )
    assert (
        proportion_of_intended_use_additional_information_instance.code_list
        == copied_model.code_list
    )
    assert (
        proportion_of_intended_use_additional_information_instance.code_value
        == copied_model.code_value
    )
    assert (
        proportion_of_intended_use_additional_information_instance.code_title
        == copied_model.code_title
    )
    assert (
        proportion_of_intended_use_additional_information_instance.height_reference_point
        == copied_model.height_reference_point
    )
    assert (
        proportion_of_intended_use_additional_information_instance.unit
        == copied_model.unit
    )


def test_copy_plan(
    database_client: DatabaseClient,
    session: Session,
    complete_test_plan: models.Plan,
    valid_status_instance: codes.LifeCycleStatus,
    remove_plan: Callable[[str], None],
):
    """Copies complete_test_plan object and checks that all relationships are duplicated correctly."""
    original_plan_id = complete_test_plan.id
    approval_date = date(2026, 1, 1)
    period_of_validity_start = date(2026, 2, 1)

    copied_plan_id = database_client.copy_plan(
        original_plan_id,
        lifecycle_status_id=valid_status_instance.id,
        plan_name={"fin": "Copied plan"},
        approval_date=approval_date,
        period_of_validity_start=period_of_validity_start,
    )
    assert copied_plan_id is not None

    original_plan = session.get(models.Plan, original_plan_id)
    assert original_plan is not None

    copied_plan = session.get(models.Plan, copied_plan_id)

    assert copied_plan is not None
    assert copied_plan.id != original_plan_id

    assert copied_plan.creator == original_plan.creator
    assert copied_plan.created_at == original_plan.created_at
    assert copied_plan.modifier == original_plan.modifier
    assert copied_plan.modified_at == original_plan.modified_at

    assert copied_plan.plan_matter == original_plan.plan_matter
    assert len(copied_plan.documents) == len(original_plan.documents)

    assert copied_plan.approval_date == approval_date
    assert copied_plan.period_of_validity_start == period_of_validity_start

    assert (
        copied_plan.legal_effects_of_master_plan
        == original_plan.legal_effects_of_master_plan
    )

    # Land use areas
    assert len(copied_plan.land_use_areas) == len(original_plan.land_use_areas)
    land_use_area_1 = original_plan.land_use_areas[0]
    copied_land_use_area_1 = next(
        (
            area
            for area in copied_plan.land_use_areas
            if area.ordering == land_use_area_1.ordering
        ),
        None,
    )
    assert copied_land_use_area_1 is not None
    assert copied_land_use_area_1.lifecycle_status.value == valid_status_instance.value
    assert copied_land_use_area_1.period_of_validity_start == period_of_validity_start

    assert copied_land_use_area_1.creator == land_use_area_1.creator
    assert copied_land_use_area_1.created_at == land_use_area_1.created_at
    assert copied_land_use_area_1.modifier == land_use_area_1.modifier
    assert copied_land_use_area_1.modified_at == land_use_area_1.modified_at

    assert (
        land_use_area_1.type_of_underground
        == copied_land_use_area_1.type_of_underground
    )

    # Other areas
    assert len(copied_plan.other_areas) == len(original_plan.other_areas)
    other_area_1 = original_plan.other_areas[0]
    copied_other_area_1 = next(
        (
            area
            for area in copied_plan.other_areas
            if area.ordering == other_area_1.ordering
        ),
        None,
    )
    assert copied_other_area_1 is not None
    assert copied_other_area_1.lifecycle_status.value == valid_status_instance.value

    assert copied_other_area_1.creator == other_area_1.creator
    assert copied_other_area_1.created_at == other_area_1.created_at
    assert copied_other_area_1.modifier == other_area_1.modifier
    assert copied_other_area_1.modified_at == other_area_1.modified_at

    assert other_area_1.type_of_underground == copied_other_area_1.type_of_underground

    # complete_test_plan fixture has no lines

    # Points
    assert len(copied_plan.points) == len(original_plan.points)
    point_1 = original_plan.points[0]
    copied_point_1 = next(
        (point for point in copied_plan.points if point.ordering == point_1.ordering),
        None,
    )
    assert copied_point_1 is not None
    assert copied_point_1.lifecycle_status.value == valid_status_instance.value
    assert copied_point_1.creator == point_1.creator
    assert copied_point_1.created_at == point_1.created_at
    assert copied_point_1.modifier == point_1.modifier
    assert copied_point_1.modified_at == point_1.modified_at
    assert point_1.type_of_underground == copied_point_1.type_of_underground

    # General regulation groups
    assert len(copied_plan.general_plan_regulation_groups) == len(
        original_plan.general_plan_regulation_groups
    )
    general_regulation_group = original_plan.general_plan_regulation_groups[0]
    copied_general_regulation_group = next(
        (
            group
            for group in copied_plan.general_plan_regulation_groups
            if group.ordering == general_regulation_group.ordering
        ),
        None,
    )
    assert copied_general_regulation_group is not None
    assert copied_general_regulation_group.plan_id == copied_plan.id
    assert copied_general_regulation_group.creator == general_regulation_group.creator
    assert (
        copied_general_regulation_group.created_at
        == general_regulation_group.created_at
    )
    assert copied_general_regulation_group.modifier == general_regulation_group.modifier
    assert (
        copied_general_regulation_group.modified_at
        == general_regulation_group.modified_at
    )
    assert (
        general_regulation_group.type_of_plan_regulation_group
        == copied_general_regulation_group.type_of_plan_regulation_group
    )
    assert (
        general_regulation_group.plan_propositions
        == copied_general_regulation_group.plan_propositions
    )

    # General regulations
    general_regulation = general_regulation_group.plan_regulations[0]
    copied_general_regulation = next(
        (
            regulation
            for regulation in copied_general_regulation_group.plan_regulations
            if regulation.ordering == general_regulation.ordering
        ),
        None,
    )
    assert copied_general_regulation is not None
    assert copied_general_regulation.creator == general_regulation.creator
    assert copied_general_regulation.created_at == general_regulation.created_at
    assert copied_general_regulation.modifier == general_regulation.modifier
    assert copied_general_regulation.modified_at == general_regulation.modified_at
    assert (
        copied_general_regulation.period_of_validity_start == period_of_validity_start
    )
    assert (
        copied_general_regulation.lifecycle_status.value == valid_status_instance.value
    )
    assert (
        general_regulation.type_of_plan_regulation
        == copied_general_regulation.type_of_plan_regulation
    )
    assert len(general_regulation.plan_themes) == len(
        copied_general_regulation.plan_themes
    )
    assert len(general_regulation.additional_information) == len(
        copied_general_regulation.additional_information
    )

    # Regulation groups
    assert len(copied_plan.regulation_groups) == len(original_plan.regulation_groups)
    copied_pedestrian_group = next(
        (
            group
            for group in copied_plan.regulation_groups
            if group.short_name == "jk/pp"
        ),
        None,
    )
    assert copied_pedestrian_group is not None

    # Regulations

    pedestrian_regulation = next(
        (regulation for regulation in copied_pedestrian_group.plan_regulations), None
    )
    assert pedestrian_regulation is not None
    assert pedestrian_regulation.lifecycle_status.value == valid_status_instance.value
    assert pedestrian_regulation.period_of_validity_start == period_of_validity_start

    remove_plan(copied_plan_id)
