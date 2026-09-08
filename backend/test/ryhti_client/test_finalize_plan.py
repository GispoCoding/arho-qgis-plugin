"""Tests for DatabaseClient.finalize_plan.

Making a plan final publishes it through the read-only valid views. The plan
must be valid today first, and everything its cancellation info repeals gets
the repealed lifecycle status. The fixtures of the repealing plan and the plan
it repeals live in test/conftest.py.
"""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

import pytest

from ryhti_client.database_client import (
    DatabaseClient,
    PlanAlreadyFinalError,
    PlanNotFoundError,
    is_valid_plan,
)
from test.conftest import yesterday

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

    from database import codes, models


@pytest.fixture
def database_client(dba_connection_string: str) -> DatabaseClient:
    return DatabaseClient(dba_connection_string)


@pytest.fixture
def valid_repealing_plan(
    session: Session,
    repealing_plan: models.Plan,
    valid_status_instance: codes.LifeCycleStatus,
    repealed_status_instance: codes.LifeCycleStatus,  # noqa: ARG001  # needed by finalize
) -> models.Plan:
    """The repealing plan, valid today but not final yet."""
    repealing_plan.lifecycle_status = valid_status_instance
    repealing_plan.period_of_validity_start = yesterday()
    session.commit()
    return repealing_plan


def status_of(session: Session, instance: models.Plan | models.PlanObjectBase) -> str:
    """The current lifecycle status value of the row, read back from the database."""
    session.refresh(instance)
    return instance.lifecycle_status.value


def named(plan: models.Plan, name: str) -> models.PlanObjectBase:
    """Look up a plan object of the plan by its Finnish name."""
    objects: list[models.PlanObjectBase] = [
        *plan.land_use_areas,
        *plan.lines,
        *plan.points,
    ]
    return next(o for o in objects if o.name is not None and o.name["fin"] == name)


def test_finalize_plan_marks_the_plan_final(
    session: Session, database_client: DatabaseClient, valid_repealing_plan: models.Plan
) -> None:
    database_client.finalize_plan(valid_repealing_plan.id)

    session.refresh(valid_repealing_plan)
    assert valid_repealing_plan.final is True


def test_finalize_plan_repeals_the_plan_objects_it_covers(
    session: Session,
    database_client: DatabaseClient,
    valid_repealing_plan: models.Plan,
    cancelled_plan: models.Plan,
) -> None:
    # The repealing plan covers the western half of the test square, so it
    # repeals the plan objects of that half but not the whole plan.
    result = database_client.finalize_plan(valid_repealing_plan.id)

    assert result.repealed_plans == 0
    assert result.repealed_plan_objects == 2
    assert status_of(session, cancelled_plan) == "13"
    assert status_of(session, named(cancelled_plan, "covered_area")) == "14"
    assert status_of(session, named(cancelled_plan, "covered_point")) == "14"


def test_finalize_plan_leaves_partly_covered_plan_objects_valid(
    session: Session,
    database_client: DatabaseClient,
    valid_repealing_plan: models.Plan,
    cancelled_plan: models.Plan,
) -> None:
    database_client.finalize_plan(valid_repealing_plan.id)

    # The remaining valid geometry of the cancellation info says what is left of
    # a plan object the repealing plan only cuts in two.
    assert status_of(session, named(cancelled_plan, "split_area")) == "13"
    assert status_of(session, named(cancelled_plan, "split_line")) == "13"
    assert status_of(session, named(cancelled_plan, "outside_point")) == "13"


def test_finalize_plan_repeals_a_plan_it_covers_entirely(
    session: Session,
    database_client: DatabaseClient,
    valid_repealing_plan: models.Plan,
    cancelled_plan: models.Plan,
) -> None:
    # Grow the repealing plan over the whole test square, so that it repeals the
    # cancelled plan itself instead of some of its plan objects.
    valid_repealing_plan.geom = cancelled_plan.geom
    session.commit()

    result = database_client.finalize_plan(valid_repealing_plan.id)

    assert result.repealed_plans == 1
    assert result.repealed_plan_objects == 0
    assert status_of(session, cancelled_plan) == "14"
    assert cancelled_plan.period_of_validity_end == yesterday() - timedelta(days=1)


def test_finalize_plan_without_cancellation_info(
    session: Session,
    database_client: DatabaseClient,
    plan_instance: models.Plan,
    valid_status_instance: codes.LifeCycleStatus,
    repealed_status_instance: codes.LifeCycleStatus,  # noqa: ARG001  # needed by finalize
) -> None:
    plan_instance.lifecycle_status = valid_status_instance
    session.commit()

    result = database_client.finalize_plan(plan_instance.id)

    assert result.repealed_plans == 0
    assert result.repealed_plan_objects == 0
    session.refresh(plan_instance)
    assert plan_instance.final is True


def test_finalize_plan_refuses_a_plan_that_is_already_final(
    session: Session, database_client: DatabaseClient, valid_repealing_plan: models.Plan
) -> None:
    valid_repealing_plan.final = True
    session.commit()

    with pytest.raises(PlanAlreadyFinalError):
        database_client.finalize_plan(valid_repealing_plan.id)


def test_finalize_plan_refuses_an_unknown_plan(
    database_client: DatabaseClient,
    valid_repealing_plan: models.Plan,  # noqa: ARG001  # keeps the codes in place
) -> None:
    with pytest.raises(PlanNotFoundError):
        database_client.finalize_plan("6ecf4cf4-1c1e-4b96-b1a2-6a4b62b1fb9c")


def test_is_valid_plan_needs_the_valid_lifecycle_status(
    session: Session,
    plan_instance: models.Plan,
    valid_status_instance: codes.LifeCycleStatus,
) -> None:
    assert is_valid_plan(plan_instance) is False

    plan_instance.lifecycle_status = valid_status_instance
    session.commit()
    assert is_valid_plan(plan_instance) is True


def test_is_valid_plan_needs_a_period_of_validity_that_covers_today(
    session: Session,
    plan_instance: models.Plan,
    valid_status_instance: codes.LifeCycleStatus,
) -> None:
    plan_instance.lifecycle_status = valid_status_instance
    plan_instance.period_of_validity_end = yesterday()
    session.commit()

    assert is_valid_plan(plan_instance) is False
