from datetime import datetime

from geoalchemy2.shape import from_shape
from shapely.geometry import MultiLineString, MultiPoint, MultiPolygon, shape
from sqlalchemy.orm import Session

from database import codes, models


def test_modified_at_triggers(
    session: Session,
    plan_instance: models.Plan,
    land_use_area_instance: models.LandUseArea,
    other_area_instance: models.OtherArea,
    line_instance: models.Line,
    land_use_point_instance: models.LandUsePoint,
    other_point_instance: models.OtherPoint,
    plan_regulation_group_instance: models.PlanRegulationGroup,
    text_plan_regulation_instance: models.PlanRegulation,
    plan_proposition_instance: models.PlanProposition,
    source_data_instance: models.SourceData,
    organisation_instance: models.Organisation,
    plan_map_instance: models.Document,
    lifecycle_date_instance: models.LifeCycleDate,
) -> None:
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
    plan_regulation_old_modified_at = text_plan_regulation_instance.modified_at
    plan_proposition_instance_old_modified_at = plan_proposition_instance.modified_at
    source_data_instance_old_modified_at = source_data_instance.modified_at
    organisation_instance_old_modified_at = organisation_instance.modified_at
    plan_map_instance_old_modified_at = plan_map_instance.modified_at
    lifecycle_date_instance_old_modified_at = lifecycle_date_instance.modified_at

    # Edit tables to fire the triggers
    plan_instance.exported_at = datetime.now()
    land_use_area_instance.height_unit = "blah"
    other_area_instance.height_unit = "blah"
    line_instance.height_unit = "blah"
    land_use_point_instance.height_unit = "blah"
    other_point_instance.height_unit = "blah"
    plan_regulation_group_instance.short_name = "foo"
    text_plan_regulation_instance.text_value = {"fin": "foo"}
    plan_proposition_instance.text_value = {"fin": "foo"}
    source_data_instance.additional_information_uri = "http://test2.fi"
    organisation_instance.business_id = "foo"
    plan_map_instance.name = {"fin": "foo"}
    lifecycle_date_instance.ending_at = datetime.now()
    session.flush()
    session.refresh(plan_instance)
    session.refresh(land_use_area_instance)
    session.refresh(other_area_instance)
    session.refresh(line_instance)
    session.refresh(land_use_point_instance)
    session.refresh(other_point_instance)
    session.refresh(plan_regulation_group_instance)
    session.refresh(text_plan_regulation_instance)
    session.refresh(plan_proposition_instance)
    session.refresh(source_data_instance)
    session.refresh(organisation_instance)
    session.refresh(plan_map_instance)
    session.refresh(lifecycle_date_instance)

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
    assert text_plan_regulation_instance.modified_at != plan_regulation_old_modified_at
    assert (
        plan_proposition_instance.modified_at
        != plan_proposition_instance_old_modified_at
    )
    assert source_data_instance.modified_at != source_data_instance_old_modified_at
    assert organisation_instance.modified_at != organisation_instance_old_modified_at
    assert plan_map_instance != plan_map_instance_old_modified_at
    assert (
        lifecycle_date_instance.modified_at != lifecycle_date_instance_old_modified_at
    )


def test_new_object_add_lifecycle_date_triggers(
    plan_instance: models.Plan,
    text_plan_regulation_instance: models.PlanRegulation,
    plan_proposition_instance: models.PlanProposition,
    land_use_area_instance: models.LandUseArea,
    other_area_instance: models.OtherArea,
    line_instance: models.Line,
    land_use_point_instance: models.LandUsePoint,
    other_point_instance: models.OtherPoint,
) -> None:
    assert plan_instance.lifecycle_dates
    lifecycle_date = next(iter(plan_instance.lifecycle_dates))
    assert lifecycle_date.lifecycle_status == plan_instance.lifecycle_status
    assert lifecycle_date.starting_at
    assert not lifecycle_date.ending_at

    assert text_plan_regulation_instance.lifecycle_status
    lifecycle_date = next(iter(text_plan_regulation_instance.lifecycle_dates))
    assert (
        lifecycle_date.lifecycle_status
        == text_plan_regulation_instance.lifecycle_status
    )
    assert lifecycle_date.starting_at
    assert not lifecycle_date.ending_at

    assert plan_proposition_instance.lifecycle_dates
    lifecycle_date = next(iter(plan_proposition_instance.lifecycle_dates))
    assert lifecycle_date.lifecycle_status == plan_proposition_instance.lifecycle_status
    assert lifecycle_date.starting_at
    assert not lifecycle_date.ending_at

    assert land_use_area_instance.lifecycle_dates
    lifecycle_date = next(iter(land_use_area_instance.lifecycle_dates))
    assert lifecycle_date.lifecycle_status == land_use_area_instance.lifecycle_status
    assert lifecycle_date.starting_at
    assert not lifecycle_date.ending_at

    assert other_area_instance.lifecycle_dates
    lifecycle_date = next(iter(other_area_instance.lifecycle_dates))
    assert lifecycle_date.lifecycle_status == other_area_instance.lifecycle_status
    assert lifecycle_date.starting_at
    assert not lifecycle_date.ending_at

    assert line_instance.lifecycle_dates
    lifecycle_date = next(iter(line_instance.lifecycle_dates))
    assert lifecycle_date.lifecycle_status == line_instance.lifecycle_status
    assert lifecycle_date.starting_at
    assert not lifecycle_date.ending_at

    assert land_use_point_instance.lifecycle_dates
    lifecycle_date = next(iter(land_use_point_instance.lifecycle_dates))
    assert lifecycle_date.lifecycle_status == land_use_point_instance.lifecycle_status
    assert lifecycle_date.starting_at
    assert not lifecycle_date.ending_at

    assert other_point_instance.lifecycle_dates
    lifecycle_date = next(iter(other_point_instance.lifecycle_dates))
    assert lifecycle_date.lifecycle_status == other_point_instance.lifecycle_status
    assert lifecycle_date.starting_at
    assert not lifecycle_date.ending_at


def test_new_lifecycle_date_triggers(
    session: Session,
    plan_instance: models.Plan,
    text_plan_regulation_instance: models.PlanRegulation,
    plan_proposition_instance: models.PlanProposition,
    land_use_area_instance: models.LandUseArea,
    other_area_instance: models.OtherArea,
    line_instance: models.Line,
    land_use_point_instance: models.LandUsePoint,
    other_point_instance: models.OtherPoint,
    code_instance: codes.LifeCycleStatus,
    another_code_instance: codes.LifeCycleStatus,
) -> None:
    assert plan_instance.lifecycle_status_id != another_code_instance.id
    assert text_plan_regulation_instance.lifecycle_status_id != another_code_instance.id
    assert plan_proposition_instance.lifecycle_status_id != another_code_instance.id
    assert land_use_area_instance.lifecycle_status_id != another_code_instance.id
    assert other_area_instance.lifecycle_status_id != another_code_instance.id
    assert line_instance.lifecycle_status_id != another_code_instance.id
    assert land_use_point_instance.lifecycle_status_id != another_code_instance.id
    assert other_point_instance.lifecycle_status_id != another_code_instance.id

    # Update lifecycle_statuses to populate starting_at fields
    plan_instance.lifecycle_status = another_code_instance
    text_plan_regulation_instance.lifecycle_status = another_code_instance
    plan_proposition_instance.lifecycle_status = another_code_instance
    land_use_area_instance.lifecycle_status = another_code_instance
    other_area_instance.lifecycle_status = another_code_instance
    line_instance.lifecycle_status = another_code_instance
    land_use_point_instance.lifecycle_status = another_code_instance
    other_point_instance.lifecycle_status = another_code_instance
    session.flush()

    # Update again to populate ending_at fields
    plan_instance.lifecycle_status = code_instance
    text_plan_regulation_instance.lifecycle_status = code_instance
    plan_proposition_instance.lifecycle_status = code_instance
    land_use_area_instance.lifecycle_status = code_instance
    other_area_instance.lifecycle_status = code_instance
    line_instance.lifecycle_status = code_instance
    land_use_point_instance.lifecycle_status = code_instance
    other_point_instance.lifecycle_status = code_instance
    session.flush()
    session.refresh(plan_instance)
    session.refresh(text_plan_regulation_instance)
    session.refresh(plan_proposition_instance)
    session.refresh(land_use_area_instance)
    session.refresh(other_area_instance)
    session.refresh(line_instance)
    session.refresh(land_use_point_instance)
    session.refresh(other_point_instance)

    # Get old and new entries in lifecycle_date table
    def get_new_lifecycle_date(instance: models.PlanBase) -> models.LifeCycleDate:
        return next(
            date
            for date in instance.lifecycle_dates
            if date.lifecycle_status == code_instance
        )

    def get_old_lifecycle_date(instance: models.PlanBase) -> models.LifeCycleDate:
        return next(
            date
            for date in instance.lifecycle_dates
            if date.lifecycle_status == another_code_instance
        )

    plan_new_lifecycle_date = get_new_lifecycle_date(plan_instance)
    plan_regulation_new_lifecycle_date = get_new_lifecycle_date(
        text_plan_regulation_instance
    )
    plan_proposition_new_lifecycle_date = get_new_lifecycle_date(
        plan_proposition_instance
    )
    land_use_area_new_lifecycle_date = get_new_lifecycle_date(land_use_area_instance)
    other_area_new_lifecycle_date = get_new_lifecycle_date(other_area_instance)
    line_new_lifecycle_date = get_new_lifecycle_date(line_instance)
    land_use_point_new_lifecycle_date = get_new_lifecycle_date(land_use_point_instance)
    other_point_new_lifecycle_date = get_new_lifecycle_date(other_point_instance)
    plan_old_lifecycle_date = get_old_lifecycle_date(plan_instance)
    plan_regulation_old_lifecycle_date = get_old_lifecycle_date(
        text_plan_regulation_instance
    )
    plan_proposition_old_lifecycle_date = get_old_lifecycle_date(
        plan_proposition_instance
    )
    land_use_area_old_lifecycle_date = get_old_lifecycle_date(land_use_area_instance)
    other_area_old_lifecycle_date = get_old_lifecycle_date(other_area_instance)
    line_old_lifecycle_date = get_old_lifecycle_date(line_instance)
    land_use_point_old_lifecycle_date = get_old_lifecycle_date(land_use_point_instance)
    other_point_old_lifecycle_date = get_old_lifecycle_date(other_point_instance)

    assert plan_new_lifecycle_date.lifecycle_status_id == code_instance.id
    assert plan_new_lifecycle_date.starting_at is not None
    assert plan_old_lifecycle_date.ending_at is not None

    assert plan_regulation_new_lifecycle_date.lifecycle_status_id == code_instance.id
    assert plan_regulation_new_lifecycle_date.starting_at is not None
    assert plan_regulation_old_lifecycle_date.ending_at is not None

    assert plan_proposition_new_lifecycle_date.lifecycle_status_id == code_instance.id
    assert plan_proposition_new_lifecycle_date.starting_at is not None
    assert plan_proposition_old_lifecycle_date.ending_at is not None

    assert land_use_area_instance.lifecycle_status_id == code_instance.id
    assert land_use_area_new_lifecycle_date.starting_at is not None
    assert land_use_area_old_lifecycle_date.ending_at is not None

    assert other_area_instance.lifecycle_status_id == code_instance.id
    assert other_area_new_lifecycle_date.starting_at is not None
    assert other_area_old_lifecycle_date.ending_at is not None

    assert line_instance.lifecycle_status_id == code_instance.id
    assert line_new_lifecycle_date.starting_at is not None
    assert line_old_lifecycle_date.ending_at is not None

    assert land_use_point_instance.lifecycle_status_id == code_instance.id
    assert land_use_point_new_lifecycle_date.starting_at is not None
    assert land_use_point_old_lifecycle_date.ending_at is not None

    assert other_point_instance.lifecycle_status_id == code_instance.id
    assert other_point_new_lifecycle_date.starting_at is not None
    assert other_point_old_lifecycle_date.ending_at is not None


def test_new_lifecycle_status_triggers(
    session: Session,
    plan_instance: models.Plan,
    plan_regulation_group_instance: models.PlanRegulationGroup,
    general_regulation_group_instance: models.PlanRegulationGroup,
    code_instance: codes.LifeCycleStatus,
    another_code_instance: codes.LifeCycleStatus,
    type_of_plan_regulation_instance: codes.TypeOfPlanRegulation,
    type_of_underground_instance: codes.TypeOfUnderground,
) -> None:
    assert plan_instance.general_plan_regulation_groups == [
        general_regulation_group_instance
    ]

    plan_instance.lifecycle_status = another_code_instance
    session.flush()

    # Create new objects in the plan area (geometry creates link to plan instance)
    land_use_area_instance = models.LandUseArea(
        lifecycle_status=code_instance,
        geom=from_shape(
            shape(
                {
                    "type": "MultiPolygon",
                    "coordinates": [
                        [
                            [
                                [381849.834412134019658, 6677967.973336197435856],
                                [381849.834412134019658, 6680613.389312859624624],
                                [386378.427863708813675, 6680613.389312859624624],
                                [386378.427863708813675, 6677967.973336197435856],
                                [381849.834412134019658, 6677967.973336197435856],
                            ]
                        ]
                    ],
                }
            )
        ),
        plan=plan_instance,
        type_of_underground=type_of_underground_instance,
        plan_regulation_groups=[plan_regulation_group_instance],
    )
    other_area_instance = models.OtherArea(
        lifecycle_status=code_instance,
        geom=from_shape(
            shape(
                {
                    "type": "MultiPolygon",
                    "coordinates": [
                        [
                            [
                                [381849.834412134019658, 6677967.973336197435856],
                                [381849.834412134019658, 6680613.389312859624624],
                                [386378.427863708813675, 6680613.389312859624624],
                                [386378.427863708813675, 6677967.973336197435856],
                                [381849.834412134019658, 6677967.973336197435856],
                            ]
                        ]
                    ],
                }
            )
        ),
        plan=plan_instance,
        type_of_underground=type_of_underground_instance,
        plan_regulation_groups=[plan_regulation_group_instance],
    )
    line_instance = models.Line(
        lifecycle_status=code_instance,
        geom=from_shape(
            MultiLineString(
                [
                    [[382000, 6678000], [383000, 6678000]],
                ]
            )
        ),
        plan=plan_instance,
        type_of_underground=type_of_underground_instance,
        plan_regulation_groups=[plan_regulation_group_instance],
    )
    land_use_point_instance = models.LandUsePoint(
        lifecycle_status=code_instance,
        geom=from_shape(MultiPoint([[382000, 6678000], [383000, 6678000]])),
        plan=plan_instance,
        type_of_underground=type_of_underground_instance,
        plan_regulation_groups=[plan_regulation_group_instance],
    )
    other_point_instance = models.OtherPoint(
        lifecycle_status=code_instance,
        geom=from_shape(MultiPoint([[382000, 6678000], [383000, 6678000]])),
        plan=plan_instance,
        type_of_underground=type_of_underground_instance,
        plan_regulation_groups=[plan_regulation_group_instance],
    )
    session.add(land_use_area_instance)
    session.add(other_area_instance)
    session.add(line_instance)
    session.add(land_use_point_instance)
    session.add(other_point_instance)
    session.flush()

    # Create new regulations in regulation groups already linked to plan
    general_regulation_instance = models.PlanRegulation(
        lifecycle_status=code_instance,
        type_of_plan_regulation=type_of_plan_regulation_instance,
        plan_regulation_group=general_regulation_group_instance,
    )
    general_proposition_instance = models.PlanProposition(
        lifecycle_status=code_instance,
        plan_regulation_group=general_regulation_group_instance,
    )
    plan_regulation_instance = models.PlanRegulation(
        lifecycle_status=code_instance,
        type_of_plan_regulation=type_of_plan_regulation_instance,
        plan_regulation_group=plan_regulation_group_instance,
    )
    plan_proposition_instance = models.PlanProposition(
        lifecycle_status=code_instance,
        plan_regulation_group=plan_regulation_group_instance,
    )
    session.add(general_regulation_instance)
    session.add(general_proposition_instance)
    session.add(plan_regulation_instance)
    session.add(plan_proposition_instance)
    session.flush()

    session.refresh(land_use_area_instance)
    session.refresh(other_area_instance)
    session.refresh(line_instance)
    session.refresh(land_use_point_instance)
    session.refresh(other_point_instance)
    session.refresh(general_regulation_instance)
    session.refresh(general_proposition_instance)
    session.refresh(plan_regulation_instance)
    session.refresh(plan_proposition_instance)

    # Check that new features and regulations have same status as plan
    print(plan_regulation_instance.lifecycle_status.value)
    print(another_code_instance.value)
    assert land_use_area_instance.lifecycle_status == another_code_instance
    assert other_area_instance.lifecycle_status == another_code_instance
    assert line_instance.lifecycle_status == another_code_instance
    assert land_use_point_instance.lifecycle_status == another_code_instance
    assert other_point_instance.lifecycle_status == another_code_instance
    assert general_regulation_instance.lifecycle_status == another_code_instance
    assert general_proposition_instance.lifecycle_status == another_code_instance
    assert plan_regulation_instance.lifecycle_status == another_code_instance
    assert plan_proposition_instance.lifecycle_status == another_code_instance

    # Delete created objects from the test database
    session.rollback()


def test_update_lifecycle_status_triggers(
    session: Session,
    plan_instance: models.Plan,
    plan_regulation_group_instance: models.PlanRegulationGroup,
    construction_area_plan_regulation_group_instance: models.PlanRegulationGroup,
    numeric_plan_regulation_group_instance: models.PlanRegulationGroup,
    decimal_plan_regulation_group_instance: models.PlanRegulationGroup,
    point_plan_regulation_group_instance: models.PlanRegulationGroup,
    general_regulation_group_instance: models.PlanRegulationGroup,
    land_use_area_instance: models.LandUseArea,
    other_area_instance: models.OtherArea,
    line_instance: models.Line,
    land_use_point_instance: models.LandUsePoint,
    other_point_instance: models.OtherPoint,
    empty_value_plan_regulation_instance: models.PlanRegulation,
    construction_area_plan_regulation_instance: models.PlanRegulation,
    numeric_plan_regulation_instance: models.PlanRegulation,
    decimal_plan_regulation_instance: models.PlanRegulation,
    text_plan_regulation_instance: models.PlanRegulation,
    general_plan_regulation_instance: models.PlanRegulation,
    plan_proposition_instance: models.PlanProposition,
    code_instance: codes.LifeCycleStatus,
    another_code_instance: codes.LifeCycleStatus,
) -> None:
    """We must test that the trigger also updates everything in plan objects and plan regulations
    on the plan that *do not* have the same plan regulation group as the plan.
    """
    plan_instance.lifecycle_status = code_instance
    session.flush()
    assert plan_instance.lifecycle_status != another_code_instance
    assert (
        empty_value_plan_regulation_instance.lifecycle_status != another_code_instance
    )
    assert (
        empty_value_plan_regulation_instance.plan_regulation_group
        == plan_regulation_group_instance
    )
    assert numeric_plan_regulation_instance.lifecycle_status != another_code_instance
    assert (
        numeric_plan_regulation_instance.plan_regulation_group
        == numeric_plan_regulation_group_instance
    )
    assert decimal_plan_regulation_instance.lifecycle_status != another_code_instance
    assert (
        decimal_plan_regulation_instance.plan_regulation_group
        == decimal_plan_regulation_group_instance
    )
    assert text_plan_regulation_instance.lifecycle_status != another_code_instance
    assert (
        text_plan_regulation_instance.plan_regulation_group
        == plan_regulation_group_instance
    )
    assert general_plan_regulation_instance.lifecycle_status != another_code_instance
    assert (
        general_plan_regulation_instance.plan_regulation_group
        == general_regulation_group_instance
    )
    assert plan_proposition_instance.lifecycle_status != another_code_instance
    assert (
        plan_proposition_instance.plan_regulation_group
        == plan_regulation_group_instance
    )

    assert land_use_area_instance.lifecycle_status != another_code_instance
    assert other_area_instance.lifecycle_status != another_code_instance
    assert line_instance.lifecycle_status != another_code_instance
    assert land_use_point_instance.lifecycle_status != another_code_instance
    assert other_point_instance.lifecycle_status != another_code_instance
    assert plan_instance.general_plan_regulation_groups == [
        general_regulation_group_instance
    ]
    assert set(land_use_area_instance.plan_regulation_groups) == {
            numeric_plan_regulation_group_instance,
            decimal_plan_regulation_group_instance,
            plan_regulation_group_instance,
        }
    assert other_area_instance.plan_regulation_groups == [
        construction_area_plan_regulation_group_instance
    ]
    assert line_instance.plan_regulation_groups == [plan_regulation_group_instance]
    assert land_use_point_instance.plan_regulation_groups == [
        point_plan_regulation_group_instance
    ]
    assert other_point_instance.plan_regulation_groups == [
        point_plan_regulation_group_instance
    ]

    # Change lifecycle status to fire the triggers
    plan_instance.lifecycle_status = another_code_instance
    session.flush()
    session.refresh(land_use_area_instance)
    session.refresh(other_area_instance)
    session.refresh(line_instance)
    session.refresh(land_use_point_instance)
    session.refresh(other_point_instance)
    session.refresh(empty_value_plan_regulation_instance)
    session.refresh(construction_area_plan_regulation_instance)
    session.refresh(numeric_plan_regulation_instance)
    session.refresh(decimal_plan_regulation_instance)
    session.refresh(text_plan_regulation_instance)
    session.refresh(general_plan_regulation_instance)
    session.refresh(plan_proposition_instance)

    # Check that features and regulations have same status as plan
    assert plan_instance.lifecycle_status == another_code_instance
    assert land_use_area_instance.lifecycle_status == another_code_instance
    assert other_area_instance.lifecycle_status == another_code_instance
    assert line_instance.lifecycle_status == another_code_instance
    assert land_use_point_instance.lifecycle_status == another_code_instance
    assert other_point_instance.lifecycle_status == another_code_instance
    assert (
        empty_value_plan_regulation_instance.lifecycle_status == another_code_instance
    )
    assert (
        construction_area_plan_regulation_instance.lifecycle_status
        == another_code_instance
    )
    assert numeric_plan_regulation_instance.lifecycle_status == another_code_instance
    assert decimal_plan_regulation_instance.lifecycle_status == another_code_instance
    assert text_plan_regulation_instance.lifecycle_status == another_code_instance
    assert general_plan_regulation_instance.lifecycle_status == another_code_instance
    assert plan_proposition_instance.lifecycle_status == another_code_instance


def test_add_plan_id_fkey_triggers(
    session: Session,
    plan_instance: models.Plan,
    plan_type_instance: codes.PlanType,
    code_instance: codes.LifeCycleStatus,
    type_of_underground_instance: codes.TypeOfUnderground,
    plan_regulation_group_instance: models.PlanRegulationGroup,
    organisation_instance: models.Organisation,
) -> None:
    # Add another plan instance
    another_plan_instance = models.Plan(
        name={"fin": "Test Plan"},
        geom=from_shape(
            MultiPolygon([(((1.0, 2.0), (2.0, 2.0), (2.0, 1.0), (1.0, 1.0)),)])
        ),
        plan_type=plan_type_instance,
        lifecycle_status=code_instance,
        organisation=organisation_instance,
    )
    session.add(another_plan_instance)

    # Geometries inside either plan instance
    polygon_1 = MultiPolygon(
        [
            (
                (
                    (382000.0, 6678000.0),
                    (386000.0, 6678000.0),
                    (386000.0, 6680000.0),
                    (382000.0, 6680000.0),
                ),
            )
        ]
    )
    point_1 = MultiPoint([[(383000.0, 6678500.0)], [384000.0, 6679500.0]])
    polygon_2 = MultiPolygon([(((1.0, 2.0), (2.0, 2.0), (2.0, 1.0), (1.0, 1.0)),)])
    point_2 = MultiPoint([[1.25, 1.25], [1.75, 1.75]])
    line_1 = MultiLineString(
        [
            [[383000.0, 6678500.0], [384000.0, 6679500.0]],
        ]
    )
    line_2 = MultiLineString(
        [
            [[1.25, 1.25], [1.75, 1.75]],
        ]
    )

    # Add new plan object instances to fire the triggers
    another_land_use_area_instance = models.LandUseArea(
        geom=from_shape(polygon_1),
        lifecycle_status=code_instance,
        type_of_underground=type_of_underground_instance,
        plan_regulation_groups=[plan_regulation_group_instance],
    )
    session.add(another_land_use_area_instance)

    another_area_instance = models.OtherArea(
        geom=from_shape(polygon_2),
        lifecycle_status=code_instance,
        type_of_underground=type_of_underground_instance,
        plan_regulation_groups=[plan_regulation_group_instance],
    )
    session.add(another_area_instance)

    another_line_instance = models.Line(
        geom=from_shape(line_1),
        lifecycle_status=code_instance,
        type_of_underground=type_of_underground_instance,
        plan_regulation_groups=[plan_regulation_group_instance],
    )
    session.add(another_line_instance)
    another_another_line_instance = models.Line(
        geom=from_shape(line_2),
        lifecycle_status=code_instance,
        type_of_underground=type_of_underground_instance,
        plan_regulation_groups=[plan_regulation_group_instance],
    )
    session.add(another_another_line_instance)

    another_land_use_point_instance = models.LandUsePoint(
        geom=from_shape(point_1),
        lifecycle_status=code_instance,
        type_of_underground=type_of_underground_instance,
        plan_regulation_groups=[plan_regulation_group_instance],
    )
    session.add(another_land_use_point_instance)

    another_point_instance = models.OtherPoint(
        geom=from_shape(point_2),
        lifecycle_status=code_instance,
        type_of_underground=type_of_underground_instance,
        plan_regulation_groups=[plan_regulation_group_instance],
    )
    session.add(another_point_instance)
    session.flush()

    session.refresh(another_land_use_area_instance)
    session.refresh(another_area_instance)
    session.refresh(another_line_instance)
    session.refresh(another_another_line_instance)
    session.refresh(another_land_use_point_instance)
    session.refresh(another_point_instance)

    assert another_land_use_area_instance.plan_id == plan_instance.id
    assert another_area_instance.plan_id == another_plan_instance.id
    assert another_line_instance.plan_id == plan_instance.id
    assert another_another_line_instance.plan_id == another_plan_instance.id
    assert another_land_use_point_instance.plan_id == plan_instance.id
    assert another_point_instance.plan_id == another_plan_instance.id

    # Delete created objects from the test database
    session.rollback()
