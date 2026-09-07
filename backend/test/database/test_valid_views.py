"""Tests for the read-only valid views in database/valid_views.py.

A plan only reaches the valid views when it is marked final. The other valid
views select through hame.plan_valid, so they inherit the check.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

import pytest
import sqlalchemy
from geoalchemy2.shape import from_shape
from shapely import MultiPolygon, Polygon

from database import models
from database.base import PROJECT_SRID

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

    from database import codes


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
