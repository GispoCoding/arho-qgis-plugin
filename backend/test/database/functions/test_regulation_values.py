from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from database.enums import AttributeValueDataType
from database.models import PlanRegulation

if TYPE_CHECKING:
    import psycopg
    from sqlalchemy.orm import Session

    from database.codes import TypeOfPlanRegulation
    from database.models import LandUseArea, Line, PlanRegulationGroup
    from test.conftest import ReturnSame


@pytest.fixture
def density_regulation_group(
    temp_session_feature: ReturnSame,
    land_use_regulation_group: PlanRegulationGroup,
    density_regulation_type: TypeOfPlanRegulation,
) -> PlanRegulationGroup:
    regulation = PlanRegulation(
        plan_regulation_group=land_use_regulation_group,
        type_of_plan_regulation=density_regulation_type,
        value_data_type=AttributeValueDataType.POSITIVE_DECIMAL,
        numeric_value=0.2,
        unit="m2/k-m2",
    )
    temp_session_feature(regulation)

    return land_use_regulation_group


@pytest.fixture
def land_use_area_with_regulation_value(
    session: Session,
    land_use_area: LandUseArea,
    density_regulation_group: PlanRegulationGroup,
) -> LandUseArea:
    land_use_area.plan_regulation_groups.append(density_regulation_group)
    session.add(land_use_area)
    session.commit()
    return land_use_area


def test_regulation_values(
    conn: psycopg.Connection, land_use_area_with_regulation_value: LandUseArea
) -> None:
    with conn.cursor() as cur:
        cur.execute(
            "select hame.regulation_values('land_use_area', %s)",
            (land_use_area_with_regulation_value.id,),
        )
        row = cur.fetchone()
    assert row is not None
    assert row[0] == {"valjyysluku": {"numeric_value": 0.2, "unit": "m2/k-m2"}}


def test_regulation_values_should_not_contain_regulations_without_value(
    conn: psycopg.Connection,
    line_with_regulation_value_and_additional_info_with_value: Line,
) -> None:
    with conn.cursor() as cur:
        cur.execute(
            "select hame.regulation_values('line', %s)",
            (line_with_regulation_value_and_additional_info_with_value.id,),
        )
        row = cur.fetchone()
    assert row is not None
    assert row[0] == {"valjyysluku": {"numeric_value": 0.2, "unit": "m2/k-m2"}}
