from datetime import datetime

import codes
import models
from geoalchemy2.shape import from_shape
from shapely.geometry import MultiLineString, MultiPoint, MultiPolygon
from sqlalchemy.orm import Session


def test_modified_at_triggers(
    session: Session,
    plan_instance: models.Plan,
    land_use_area_instance: models.LandUseArea,
    other_area_instance: models.OtherArea,
    line_instance: models.Line,
    land_use_point_instance: models.LandUsePoint,
    other_point_instance: models.OtherPoint,
    plan_regulation_group_instance: models.PlanRegulationGroup,
    plan_regulation_instance: models.PlanRegulation,
    plan_proposition_instance: models.PlanProposition,
    source_data_instance: models.SourceData,
    type_of_source_data_instance: codes.TypeOfSourceData,
    organisation_instance: models.Organisation,
    document_instance: models.Document,
    lifecycle_date_instance: models.LifeCycleDate,
):
    # Save old modified_at timestamps
    plan_old_modified_at = plan_instance.modified_at
    land_use_area_instance_old_modified_at = land_use_area_instance.modified_at
    other_area_instance_old_modified_at = other_area_instance.modified_at
    line_instance_old_modified_at = line_instance.modified_at
    land_use_point_instance_old_modified_at = land_use_point_instance.modified_at
    other_point_instance_old_modified_at = other_point_instance.modified_at
    plan_regulation_group_instance_old_modified_at = (
        plan_regulation_group_instance.modified_at
    )
    plan_regulation_old_modified_at = plan_regulation_instance.modified_at
    plan_proposition_instance_old_modified_at = plan_proposition_instance.modified_at
    source_data_instance_old_modified_at = source_data_instance.modified_at
    organisation_instance_old_modified_at = organisation_instance.modified_at
    document_instance_old_modified_at = document_instance.modified_at
    lifecycle_date_instance_old_modified_at = lifecycle_date_instance.modified_at

    # Edit tables to fire the triggers
    plan_instance.exported_at = datetime.now()
    land_use_area_instance.ordering = 1
    other_area_instance.ordering = 1
    line_instance.ordering = 1
    land_use_point_instance.ordering = 1
    other_point_instance.ordering = 1
    plan_regulation_group_instance.short_name = "foo"
    plan_regulation_instance.text_value = "foo"
    plan_proposition_instance.text_value = "foo"
    source_data_instance.type_of_source_data = type_of_source_data_instance
    organisation_instance.business_id = "foo"
    document_instance.name = "foo"
    lifecycle_date_instance.ending_at = datetime.now()
    session.flush()

    assert plan_instance.modified_at != plan_old_modified_at
    assert land_use_area_instance.modified_at != land_use_area_instance_old_modified_at
    assert other_area_instance.modified_at != other_area_instance_old_modified_at
    assert line_instance.modified_at != line_instance_old_modified_at
    assert (
        land_use_point_instance.modified_at != land_use_point_instance_old_modified_at
    )
    assert other_point_instance.modified_at != other_point_instance_old_modified_at
    assert (
        plan_regulation_group_instance.modified_at
        != plan_regulation_group_instance_old_modified_at
    )
    assert plan_regulation_instance.modified_at != plan_regulation_old_modified_at
    assert (
        plan_proposition_instance.modified_at
        != plan_proposition_instance_old_modified_at
    )
    assert source_data_instance.modified_at != source_data_instance_old_modified_at
    assert organisation_instance.modified_at != organisation_instance_old_modified_at
    assert document_instance != document_instance_old_modified_at
    assert (
        lifecycle_date_instance.modified_at != lifecycle_date_instance_old_modified_at
    )


def test_new_lifecycle_date_triggers(
    session: Session,
    plan_instance: models.Plan,
    plan_regulation_instance: models.PlanRegulation,
    plan_proposition_instance: models.PlanProposition,
    code_instance: codes.LifeCycleStatus,
    another_code_instance: codes.LifeCycleStatus,
):
    session.flush()
    session.refresh(code_instance)
    session.refresh(another_code_instance)
    assert plan_instance.lifecycle_status_id != another_code_instance.id
    assert plan_regulation_instance.lifecycle_status_id != another_code_instance.id
    assert plan_proposition_instance.lifecycle_status_id != another_code_instance.id

    # Update lifecycle_statuses to fire the triggers
    plan_instance.lifecycle_status = another_code_instance
    plan_regulation_instance.lifecycle_status = another_code_instance
    plan_proposition_instance.lifecycle_status = another_code_instance

    # Get new entries in lifecycle_date table
    plan_new_lifecycle_date = plan_instance.lifecycle_dates[0]
    plan_regulation_new_lifecycle_date = plan_regulation_instance.lifecycle_dates[0]
    plan_proposition_new_lifecycle_date = plan_proposition_instance.lifecycle_dates[0]
    session.flush()

    assert plan_new_lifecycle_date.lifecycle_status_id == another_code_instance.id
    assert plan_new_lifecycle_date.starting_at is not None
    assert plan_new_lifecycle_date.ending_at is not None
    assert (
        plan_regulation_new_lifecycle_date.lifecycle_status_id
        == another_code_instance.id
    )
    assert plan_regulation_new_lifecycle_date.starting_at is not None
    assert plan_regulation_new_lifecycle_date.ending_at is not None
    assert (
        plan_proposition_new_lifecycle_date.lifecycle_status_id
        == another_code_instance.id
    )
    assert plan_proposition_new_lifecycle_date.starting_at is not None
    assert plan_proposition_new_lifecycle_date.ending_at is not None


def test_update_lifecycle_status_triggers(
    session: Session,
    plan_instance: models.Plan,
    plan_regulation_group_instance: models.PlanRegulationGroup,
    land_use_area_instance: models.LandUseArea,
    other_area_instance: models.OtherArea,
    line_instance: models.Line,
    land_use_point_instance: models.LandUsePoint,
    other_point_instance: models.OtherPoint,
    plan_regulation_instance: models.PlanRegulation,
    plan_proposition_instance: models.PlanProposition,
    code_instance: codes.LifeCycleStatus,
    another_code_instance: codes.LifeCycleStatus,
):
    # Set common plan_regulation_group
    plan_instance.plan_regulation_group = plan_regulation_group_instance
    land_use_area_instance.plan_regulation_group = plan_regulation_group_instance
    other_area_instance.plan_regulation_group = plan_regulation_group_instance
    line_instance.plan_regulation_group = plan_regulation_group_instance
    land_use_point_instance.plan_regulation_group = plan_regulation_group_instance
    other_point_instance.plan_regulation_group = plan_regulation_group_instance
    plan_regulation_instance.plan_regulation_group = plan_regulation_group_instance
    plan_proposition_instance.plan_regulation_group = plan_regulation_group_instance
    session.flush()

    # Set common lifecycle_status
    land_use_area_instance.lifecycle_status = code_instance
    other_area_instance.lifecycle_status = code_instance
    line_instance.lifecycle_status = code_instance
    land_use_point_instance.lifecycle_status = code_instance
    other_point_instance.lifecycle_status = code_instance
    plan_regulation_instance.lifecycle_status = code_instance
    plan_proposition_instance.lifecycle_status = code_instance
    plan_instance.lifecycle_status = code_instance
    session.flush()
    assert plan_instance.lifecycle_status is code_instance

    # Change lifecycle status
    plan_instance.lifecycle_status = another_code_instance
    session.commit()

    assert plan_instance.lifecycle_status_id == another_code_instance.id
    assert land_use_area_instance.lifecycle_status_id == another_code_instance.id
    assert other_area_instance.lifecycle_status_id == another_code_instance.id
    assert line_instance.lifecycle_status_id == another_code_instance.id
    assert land_use_point_instance.lifecycle_status_id == another_code_instance.id
    assert other_point_instance.lifecycle_status_id == another_code_instance.id
    assert plan_regulation_instance.lifecycle_status_id == another_code_instance.id
    assert plan_proposition_instance.lifecycle_status_id == another_code_instance.id


def test_add_plan_id_fkey_triggers(
    session: Session,
    plan_instance: models.Plan,
    code_instance: codes.LifeCycleStatus,
    type_of_underground_instance: codes.TypeOfUnderground,
    plan_regulation_group_instance: models.PlanRegulationGroup,
):
    # Create new plan objects without plan_id
    another_land_use_area_instance = models.LandUseArea(
        geom=from_shape(
            MultiPolygon([(((0.0, 1.0), (1.0, 1.0), (1.0, 0.0), (0.0, 0.0)),)])
        ),
        lifecycle_status=code_instance,
        type_of_underground=type_of_underground_instance,
        plan_regulation_group=plan_regulation_group_instance,
    )
    session.add(another_land_use_area_instance)

    another_area_instance = models.OtherArea(
        geom=from_shape(
            MultiPolygon([(((0.0, 1.0), (1.0, 1.0), (1.0, 0.0), (0.0, 0.0)),)])
        ),
        lifecycle_status=code_instance,
        type_of_underground=type_of_underground_instance,
        plan_regulation_group=plan_regulation_group_instance,
    )
    session.add(another_area_instance)

    another_line_instance = models.Line(
        geom=from_shape(MultiLineString([[[0, 0], [1, 2]], [[4, 4], [5, 6]]])),
        lifecycle_status=code_instance,
        type_of_underground=type_of_underground_instance,
        plan_regulation_group=plan_regulation_group_instance,
    )
    session.add(another_line_instance)

    another_land_use_point_instance = models.LandUsePoint(
        geom=from_shape(MultiPoint([[0.0, 0.0], [1.0, 2.0]])),
        lifecycle_status=code_instance,
        type_of_underground=type_of_underground_instance,
        plan_regulation_group=plan_regulation_group_instance,
    )
    session.add(another_land_use_point_instance)

    another_point_instance = models.OtherPoint(
        geom=from_shape(MultiPoint([[0.0, 0.0], [1.0, 2.0]])),
        lifecycle_status=code_instance,
        type_of_underground=type_of_underground_instance,
        plan_regulation_group=plan_regulation_group_instance,
    )
    session.add(another_point_instance)
    session.commit()

    assert another_land_use_area_instance.plan_id == plan_instance.id
    assert another_area_instance.plan_id == plan_instance.id
    assert another_line_instance.plan_id == plan_instance.id
    assert another_land_use_point_instance.plan_id == plan_instance.id
    assert another_point_instance.plan_id == plan_instance.id
