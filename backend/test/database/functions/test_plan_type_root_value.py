"""Tests for hame.plan_type_root_value in database/functions.py.

The function walks up codes.plan_type to the level 1 code and returns its
value. hame.repealed_plans uses it to compare the plan type of a repealing plan
with the plan_type column of hame.plan_matter_valid.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from database.codes import PlanType

if TYPE_CHECKING:
    import psycopg
    from sqlalchemy.orm import Session


@pytest.fixture
def regional_plan_type(session: Session) -> PlanType:
    """The level 1 code 1 Maakuntakaava of RY_Kaavalaji."""
    instance = PlanType(value="1", level=1, status="LOCAL")
    session.add(instance)
    session.commit()
    return instance


@pytest.fixture
def whole_regional_plan_type(
    session: Session, regional_plan_type: PlanType
) -> PlanType:
    """The level 2 code 11 Kokonaismaakuntakaava, a child of code 1."""
    instance = PlanType(value="11", level=2, status="LOCAL", parent=regional_plan_type)
    session.add(instance)
    session.commit()
    return instance


def plan_type_root_value(conn: psycopg.Connection, plan_type: PlanType) -> str | None:
    with conn.cursor() as cur:
        cur.execute("select hame.plan_type_root_value(%s)", (plan_type.id,))
        row = cur.fetchone()
        assert row is not None
        return row[0]


def test_plan_type_root_value_of_a_level_1_code(
    conn: psycopg.Connection, regional_plan_type: PlanType
) -> None:
    """A level 1 code is its own level 1 code."""
    assert plan_type_root_value(conn, regional_plan_type) == "1"


def test_plan_type_root_value_of_a_child_code(
    conn: psycopg.Connection, whole_regional_plan_type: PlanType
) -> None:
    assert plan_type_root_value(conn, whole_regional_plan_type) == "1"


def test_plan_type_root_value_of_a_grandchild_code(
    conn: psycopg.Connection, session: Session, whole_regional_plan_type: PlanType
) -> None:
    """The walk up the chain does not stop at the first parent."""
    grandchild = PlanType(
        value="111", level=3, status="LOCAL", parent=whole_regional_plan_type
    )
    session.add(grandchild)
    session.commit()

    assert plan_type_root_value(conn, grandchild) == "1"


def test_plan_type_root_value_without_a_level_1_ancestor(
    conn: psycopg.Connection, session: Session
) -> None:
    """A code that descends from no level 1 code has no level 1 value."""
    orphan = PlanType(value="99", level=2, status="LOCAL")
    session.add(orphan)
    session.commit()

    assert plan_type_root_value(conn, orphan) is None
