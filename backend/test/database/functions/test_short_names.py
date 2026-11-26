from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from database.models import LandUseArea, Plan, PlanRegulationGroup

if TYPE_CHECKING:
    import psycopg
    from sqlalchemy.orm import Session

    from database.codes import TypeOfPlanRegulationGroup
    from test.conftest import ReturnSame


@pytest.fixture
def land_use_regulation_with_a_identifier_group(
    temp_session_feature: ReturnSame,
    plan_instance: Plan,
    land_use_regulation_group_type: TypeOfPlanRegulationGroup,
) -> PlanRegulationGroup:
    instance = PlanRegulationGroup(
        plan=plan_instance,
        type_of_plan_regulation_group=land_use_regulation_group_type,
        short_name="A",
    )
    temp_session_feature(instance)
    return instance


@pytest.fixture
def land_use_regulation_with_b_identifier_group(
    temp_session_feature: ReturnSame,
    plan_instance: Plan,
    land_use_regulation_group_type: TypeOfPlanRegulationGroup,
) -> PlanRegulationGroup:
    instance = PlanRegulationGroup(
        plan=plan_instance,
        type_of_plan_regulation_group=land_use_regulation_group_type,
        short_name="B",
    )
    temp_session_feature(instance)
    return instance


@pytest.fixture
def land_use_area_with_one_group_with_short_name(
    session: Session,
    land_use_area: LandUseArea,
    land_use_regulation_with_a_identifier_group: PlanRegulationGroup,
) -> LandUseArea:
    land_use_area.plan_regulation_groups = [land_use_regulation_with_a_identifier_group]

    session.add(land_use_area)
    session.commit()
    return land_use_area


@pytest.fixture
def land_use_area_with_two_groups_with_short_name(
    session: Session,
    land_use_area: LandUseArea,
    land_use_regulation_with_a_identifier_group: PlanRegulationGroup,
    land_use_regulation_with_b_identifier_group: PlanRegulationGroup,
) -> LandUseArea:
    land_use_area.plan_regulation_groups = [
        land_use_regulation_with_a_identifier_group,
        land_use_regulation_with_b_identifier_group,
    ]

    session.add(land_use_area)
    session.commit()
    return land_use_area


def test_short_names_on_land_use_area_without_names(
    conn: psycopg.Connection, land_use_area: LandUseArea
) -> None:
    with conn.cursor() as cur:
        cur.execute("select hame.short_names('land_use_area', %s)", (land_use_area.id,))
        row = cur.fetchone()
        assert row is not None
        assert row[0] == []


def test_short_names_on_land_use_area_with_one_name(
    conn: psycopg.Connection, land_use_area_with_one_group_with_short_name: LandUseArea
) -> None:
    with conn.cursor() as cur:
        cur.execute(
            "select hame.short_names('land_use_area', %s)",
            (land_use_area_with_one_group_with_short_name.id,),
        )
        row = cur.fetchone()
        assert row is not None
        assert row[0] == ["A"]


def test_short_names_on_land_use_area_with_two_names(
    conn: psycopg.Connection, land_use_area_with_two_groups_with_short_name: LandUseArea
) -> None:
    with conn.cursor() as cur:
        cur.execute(
            "select hame.short_names('land_use_area', %s)",
            (land_use_area_with_two_groups_with_short_name.id,),
        )
        row = cur.fetchone()
        assert row is not None
        assert row[0] == ["A", "B"]
