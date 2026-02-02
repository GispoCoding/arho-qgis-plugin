from datetime import datetime, timedelta

import pytest
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.orm import Session

from database import codes, models


def test_validate_lifecycle_dates(
    session: Session,
    plan_instance: models.Plan,
    lifecycle_date_instance: models.LifeCycleDate,
) -> None:
    assert (
        lifecycle_date_instance.ending_at
        and lifecycle_date_instance.starting_at < lifecycle_date_instance.ending_at
    )
    session.add(lifecycle_date_instance)
    # check that modified date cannot start after ending
    with pytest.raises(ProgrammingError):
        lifecycle_date_instance.starting_at = (
            lifecycle_date_instance.ending_at + timedelta(days=1)
        )
        session.flush()
    session.rollback()
    # check that new date cannot start after ending
    with pytest.raises(ProgrammingError):
        new_lifecycle_date_instance = models.LifeCycleDate(
            plan=plan_instance,
            starting_at=datetime.now() + timedelta(days=1),
            ending_at=datetime.now(),
        )
        session.add(new_lifecycle_date_instance)
        session.flush()
    session.rollback()


def test_validate_event_dates(
    session: Session,
    preparation_date_instance: models.LifeCycleDate,
    interaction_event_date_instance: models.EventDate,
) -> None:
    assert (
        interaction_event_date_instance.ending_at
        and interaction_event_date_instance.starting_at
        < interaction_event_date_instance.ending_at
    )
    session.add(interaction_event_date_instance)
    # check that modified event cannot start after ending
    with pytest.raises(ProgrammingError):
        interaction_event_date_instance.starting_at = (
            interaction_event_date_instance.ending_at + timedelta(days=1)
        )
        session.flush()
    session.rollback()
    # check that new event cannot start after ending
    with pytest.raises(ProgrammingError):
        new_event_date_instance = models.EventDate(
            lifecycle_date=preparation_date_instance,
            starting_at=datetime.now() + timedelta(days=1),
            ending_at=datetime.now(),
        )
        session.add(new_event_date_instance)
        session.flush()
    session.rollback()


def test_validate_event_dates_inside_status_dates(
    session: Session,
    preparation_date_instance: models.LifeCycleDate,
    interaction_event_date_instance: models.EventDate,
) -> None:
    assert (
        interaction_event_date_instance.starting_at
        > preparation_date_instance.starting_at
    )
    assert (
        preparation_date_instance.ending_at
        and interaction_event_date_instance.ending_at
        and interaction_event_date_instance.ending_at
        < preparation_date_instance.ending_at
    )
    # check that modified event cannot start before status starts
    with pytest.raises(ProgrammingError):
        interaction_event_date_instance.starting_at = (
            preparation_date_instance.starting_at - timedelta(days=1)
        )
        session.flush()
    session.rollback()
    # check that modified event cannot end after status ends
    with pytest.raises(ProgrammingError):
        interaction_event_date_instance.ending_at = (
            preparation_date_instance.ending_at + timedelta(days=1)
        )
        session.flush()
    session.rollback()
    # check that new event cannot start before status starts
    with pytest.raises(ProgrammingError):
        new_event_date_instance = models.EventDate(
            lifecycle_date=preparation_date_instance,
            starting_at=preparation_date_instance.starting_at - timedelta(days=1),
        )
        session.add(new_event_date_instance)
        session.flush()
    session.rollback()
    # check that new event cannot end after status ends
    with pytest.raises(ProgrammingError):
        new_event_date_instance = models.EventDate(
            lifecycle_date=preparation_date_instance,
            starting_at=preparation_date_instance.ending_at + timedelta(days=1),
        )
        session.add(new_event_date_instance)
        session.flush()
    session.rollback()


def test_validate_event_types(
    session: Session,
    preparation_date_instance: models.LifeCycleDate,
    approved_date_instance: models.LifeCycleDate,
    decision_date_instance: models.EventDate,
    participation_plan_presenting_for_public_decision: codes.NameOfPlanCaseDecision,
    plan_proposal_presenting_for_public_decision: codes.NameOfPlanCaseDecision,
) -> None:
    assert decision_date_instance.lifecycle_date == preparation_date_instance
    assert (
        decision_date_instance.decision
        == participation_plan_presenting_for_public_decision
    )
    session.add(decision_date_instance)
    # check that modified event cannot be added to wrong status
    with pytest.raises(ProgrammingError):
        decision_date_instance.lifecycle_date = approved_date_instance
        decision_date_instance.starting_at = approved_date_instance.starting_at
        decision_date_instance.ending_at = (
            approved_date_instance.starting_at + timedelta(days=30)
        )
        session.flush()
    session.rollback()
    # check that modified event cannot be added to wrong event type
    with pytest.raises(ProgrammingError):
        decision_date_instance.decision = plan_proposal_presenting_for_public_decision
        session.flush()
    session.rollback()
    # check that new event cannot be added to wrong status/event type combination
    with pytest.raises(ProgrammingError):
        new_event_date_instance = models.EventDate(
            lifecycle_date=approved_date_instance,
            starting_at=approved_date_instance.starting_at,
            decision=participation_plan_presenting_for_public_decision,
        )
        session.add(new_event_date_instance)
        session.flush()
    session.rollback()
