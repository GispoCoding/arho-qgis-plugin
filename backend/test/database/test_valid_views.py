"""Tests for the read-only valid views in database/valid_views.py.

A plan only reaches the valid views when it is marked final. The other valid
views select through hame.plan_valid, so they inherit the check.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

import pytest
import shapely
import sqlalchemy
from geoalchemy2.shape import from_shape, to_shape
from shapely import MultiPolygon, Polygon

from database import codes, models
from database.base import PROJECT_SRID
from test.conftest import MIDDLE, SIDE, area, line, named, point, yesterday

if TYPE_CHECKING:
    from shapely.geometry.base import BaseGeometry
    from sqlalchemy.orm import Session


@pytest.fixture
def valid_plan_instance(
    session: Session,
    plan_matter_instance: models.PlanMatter,
    valid_status_instance: codes.LifeCycleStatus,
) -> models.Plan:
    """A plan that passes every plan_valid check apart from the final flag."""
    instance = models.Plan(
        id=uuid.uuid4(),
        plan_matter=plan_matter_instance,
        name={"fin": "Valid Test Plan"},
        geom=from_shape(
            MultiPolygon(
                [
                    Polygon(
                        (
                            (381849, 6677967),
                            (381849, 6680613),
                            (386378, 6680613),
                            (386378, 6677967),
                            (381849, 6677967),
                        )
                    )
                ]
            ),
            srid=PROJECT_SRID,
        ),
        lifecycle_status=valid_status_instance,
        # Yesterday with no end date, so the period covers the current
        # date of the database whatever its time zone is.
        period_of_validity_start=datetime.now(UTC).date() - timedelta(days=1),
    )
    session.add(instance)
    session.commit()
    return instance


def ids_in_view(session: Session, view_name: str) -> set[str]:
    """Read the ids of the rows currently in a valid view."""
    statement = sqlalchemy.text(f"select id from hame.{view_name}")  # noqa: S608
    return {str(row[0]) for row in session.execute(statement)}


def test_plan_valid_requires_final(
    session: Session, valid_plan_instance: models.Plan
) -> None:
    assert str(valid_plan_instance.id) not in ids_in_view(session, "plan_valid")

    valid_plan_instance.final = True
    session.commit()

    assert str(valid_plan_instance.id) in ids_in_view(session, "plan_valid")


def test_plan_matter_valid_requires_final_plan(
    session: Session, valid_plan_instance: models.Plan
) -> None:
    """A view that selects through plan_valid inherits the final check."""
    plan_matter_id = str(valid_plan_instance.plan_matter_id)
    assert plan_matter_id not in ids_in_view(session, "plan_matter_valid")

    valid_plan_instance.final = True
    session.commit()

    assert plan_matter_id in ids_in_view(session, "plan_matter_valid")


@pytest.fixture
def regional_plan_type_instance(
    session: Session, plan_type_instance: codes.PlanType
) -> codes.PlanType:
    """The level 1 code 1 Maakuntakaava, made the parent of the plan type.

    plan_type_instance is code 11 Kokonaismaakuntakaava, which is a level 2
    code in RY_Kaavalaji. The code fixtures do not set the hierarchy, so the
    test builds it here.
    """
    instance = codes.PlanType(value="1", level=1, status="LOCAL")
    plan_type_instance.parent = instance
    plan_type_instance.level = 2
    session.add(instance)
    session.commit()
    return instance


def plan_types_in_view(session: Session) -> dict[str, str | None]:
    """Read the plan_type column of the rows in hame.plan_matter_valid."""
    statement = sqlalchemy.text("select id, plan_type from hame.plan_matter_valid")
    return {str(row[0]): row[1] for row in session.execute(statement)}


def test_plan_matter_valid_shows_level_1_plan_type(
    session: Session,
    valid_plan_instance: models.Plan,
    regional_plan_type_instance: codes.PlanType,
) -> None:
    """plan_type is the level 1 ancestor of the code the plan matter refers to."""
    valid_plan_instance.final = True
    session.commit()

    plan_matter_id = str(valid_plan_instance.plan_matter_id)
    assert plan_types_in_view(session)[plan_matter_id] == "1"


def test_plan_matter_valid_plan_type_of_a_level_1_code(
    session: Session,
    valid_plan_instance: models.Plan,
    plan_type_instance: codes.PlanType,
) -> None:
    """A plan type that is already a level 1 code is its own level 1 code."""
    plan_type_instance.value = "3"
    valid_plan_instance.final = True
    session.commit()

    plan_matter_id = str(valid_plan_instance.plan_matter_id)
    assert plan_types_in_view(session)[plan_matter_id] == "3"


# Tests for the remaining valid geometry of partly repealed plans and plan
# objects. The fixtures come from test/conftest.py: cancelled_plan covers the
# test square and repealing_plan its western half, so the eastern half stays
# valid. See docs/adr/0002-valid-views-clip-repealed-geometry.md.


@pytest.fixture
def final_repealing_plan(session: Session, repealing_plan: models.Plan) -> models.Plan:
    """The repealing plan made final with a validity period that has started."""
    repealing_plan.final = True
    repealing_plan.period_of_validity_start = yesterday()
    session.commit()
    return repealing_plan


def geom_in_view(session: Session, view_name: str, row_id: object) -> BaseGeometry:
    """Read the geometry of one row of a valid view."""
    statement = sqlalchemy.text(
        f"select st_asbinary(geom) from hame.{view_name} where id = :id"  # noqa: S608
    )
    return shapely.wkb.loads(session.execute(statement, {"id": row_id}).scalar_one())


def test_plan_valid_clips_a_partly_repealed_plan(
    session: Session, cancelled_plan: models.Plan, final_repealing_plan: models.Plan
) -> None:
    """Only the part outside the repealing plan is shown."""
    assert final_repealing_plan.id is not None
    remaining = geom_in_view(session, "plan_valid", cancelled_plan.id)
    assert remaining.equals(to_shape(area(MIDDLE, 0, SIDE, SIDE)))


def test_plan_valid_ignores_a_repealing_plan_that_is_not_final(
    session: Session, cancelled_plan: models.Plan, repealing_plan: models.Plan
) -> None:
    """A cancellation info of a draft repeals nothing yet."""
    assert repealing_plan.final is False
    remaining = geom_in_view(session, "plan_valid", cancelled_plan.id)
    assert remaining.equals(to_shape(area(0, 0, SIDE, SIDE)))


def test_plan_valid_ignores_a_repealing_plan_whose_validity_has_not_started(
    session: Session, cancelled_plan: models.Plan, final_repealing_plan: models.Plan
) -> None:
    final_repealing_plan.period_of_validity_start = yesterday() + timedelta(days=2)
    session.commit()

    remaining = geom_in_view(session, "plan_valid", cancelled_plan.id)
    assert remaining.equals(to_shape(area(0, 0, SIDE, SIDE)))


@pytest.fixture
def second_repealing_plan(
    session: Session,
    repealing_plan_matter: models.PlanMatter,
    cancelled_plan: models.Plan,  # noqa: ARG001  # must exist before the insert
    preparation_status_instance: codes.LifeCycleStatus,
) -> models.Plan:
    """A second final repealing plan that covers the south eastern quarter."""
    plan = models.Plan(
        id=str(uuid.uuid4()),
        plan_matter=repealing_plan_matter,
        name={"fin": "Toinen kumoava kaava"},
        geom=area(MIDDLE, 0, SIDE, MIDDLE),
        lifecycle_status=preparation_status_instance,
        final=True,
        period_of_validity_start=yesterday(),
    )
    session.add(plan)
    session.commit()
    return plan


def test_plan_valid_subtracts_every_repealing_plan(
    session: Session,
    cancelled_plan: models.Plan,
    final_repealing_plan: models.Plan,
    second_repealing_plan: models.Plan,
) -> None:
    assert final_repealing_plan.id is not None
    assert second_repealing_plan.id is not None
    remaining = geom_in_view(session, "plan_valid", cancelled_plan.id)
    assert remaining.equals(to_shape(area(MIDDLE, MIDDLE, SIDE, SIDE)))


def test_plan_valid_drops_a_plan_with_nothing_left(
    session: Session,
    cancelled_plan: models.Plan,
    final_repealing_plan: models.Plan,
    second_repealing_plan: models.Plan,
) -> None:
    """Two partial repeals that together cover the plan leave nothing valid."""
    assert final_repealing_plan.id is not None
    second_repealing_plan.geom = area(MIDDLE, 0, SIDE, SIDE)
    session.commit()

    assert str(cancelled_plan.id) not in ids_in_view(session, "plan_valid")
    assert str(cancelled_plan.plan_matter_id) not in ids_in_view(
        session, "plan_matter_valid"
    )


def test_plan_object_valid_shows_the_remaining_valid_geometry(
    session: Session, cancelled_plan: models.Plan, final_repealing_plan: models.Plan
) -> None:
    """A partly repealed plan object shows its remaining valid geometry."""
    assert final_repealing_plan.id is not None
    split_area = named(cancelled_plan, "split_area")
    split_line = named(cancelled_plan, "split_line")

    remaining_area = geom_in_view(session, "land_use_area_valid", split_area.id)
    remaining_line = geom_in_view(session, "line_valid", split_line.id)

    assert remaining_area.equals(to_shape(area(MIDDLE, 10, 60, 30)))
    assert remaining_line.equals(to_shape(line(MIDDLE, 50, 60, 50)))


def test_plan_object_valid_drops_an_object_repealed_entirely(
    session: Session, cancelled_plan: models.Plan, final_repealing_plan: models.Plan
) -> None:
    """An object the repealing plan covers has nothing left, whatever its status."""
    assert final_repealing_plan.id is not None
    covered_area = named(cancelled_plan, "covered_area")
    covered_point = named(cancelled_plan, "covered_point")
    outside_point = named(cancelled_plan, "outside_point")

    assert str(covered_area.id) not in ids_in_view(session, "land_use_area_valid")
    assert str(covered_point.id) not in ids_in_view(session, "point_valid")
    remaining = geom_in_view(session, "point_valid", outside_point.id)
    assert remaining.equals(to_shape(point(80, 70)))


def test_plan_object_valid_intersects_every_remaining_valid_geometry(
    session: Session,
    cancelled_plan: models.Plan,
    final_repealing_plan: models.Plan,
    second_repealing_plan: models.Plan,
) -> None:
    """Two partial repeals leave the part that both leave valid."""
    assert final_repealing_plan.id is not None
    second_repealing_plan.geom = area(55, 0, SIDE, SIDE)
    session.commit()
    split_area = named(cancelled_plan, "split_area")

    remaining = geom_in_view(session, "land_use_area_valid", split_area.id)
    assert remaining.equals(to_shape(area(MIDDLE, 10, 55, 30)))


def test_plan_object_valid_drops_an_object_with_nothing_left(
    session: Session,
    cancelled_plan: models.Plan,
    final_repealing_plan: models.Plan,
    second_repealing_plan: models.Plan,
) -> None:
    """Two partial repeals that together cover the object leave nothing valid."""
    assert final_repealing_plan.id is not None
    assert second_repealing_plan.id is not None
    split_area = named(cancelled_plan, "split_area")

    assert str(split_area.id) not in ids_in_view(session, "land_use_area_valid")


def test_plan_object_valid_drops_an_object_one_of_two_repeals_covers(
    session: Session,
    cancelled_plan: models.Plan,
    final_repealing_plan: models.Plan,
    second_repealing_plan: models.Plan,
) -> None:
    """One whole repeal wins over another partial repeal of the same object."""
    assert final_repealing_plan.id is not None
    second_repealing_plan.geom = area(20, 0, SIDE, SIDE)
    session.commit()
    covered_area = named(cancelled_plan, "covered_area")

    assert str(covered_area.id) not in ids_in_view(session, "land_use_area_valid")
