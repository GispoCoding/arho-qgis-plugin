from __future__ import annotations

from collections.abc import Generator
from typing import TYPE_CHECKING

import psycopg
import pytest
from geoalchemy2.shape import from_shape
from shapely import MultiLineString, MultiPolygon, Polygon

from database.base import PROJECT_SRID
from database.codes import (
    LifeCycleStatus,
    TypeOfAdditionalInformation,
    TypeOfPlanRegulation,
    TypeOfPlanRegulationGroup,
    TypeOfUnderground,
)
from database.enums import AttributeValueDataType
from database.models import (
    AdditionalInformation,
    LandUseArea,
    Line,
    Plan,
    PlanRegulation,
    PlanRegulationGroup,
)

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

    from database.db_helper import ConnectionParameters
    from test.conftest import ReturnSame


@pytest.fixture(scope="module")
def conn(
    main_db_params_with_root_user: ConnectionParameters, hame_database_created: None
) -> Generator[psycopg.Connection]:
    with psycopg.connect(**main_db_params_with_root_user) as conn:
        yield conn


@pytest.fixture
def land_use_regulation_group_type(
    temp_session_feature: ReturnSame,
) -> TypeOfPlanRegulationGroup:
    instance = TypeOfPlanRegulationGroup(value="landUseRegulations", status="LOCAL")
    return temp_session_feature(instance)


@pytest.fixture
def living_area_regulation_type(
    temp_session_feature: ReturnSame,
) -> TypeOfPlanRegulation:
    instance = TypeOfPlanRegulation(value="asumisenAlue", status="LOCAL")
    return temp_session_feature(instance)


@pytest.fixture
def tree_row_regulation_type(temp_session_feature: ReturnSame) -> TypeOfPlanRegulation:
    instance = TypeOfPlanRegulation(value="puuTaiPuurivi", status="LOCAL")
    return temp_session_feature(instance)


@pytest.fixture
def density_regulation_type(temp_session_feature: ReturnSame) -> TypeOfPlanRegulation:
    instance = TypeOfPlanRegulation(value="valjyysluku", status="LOCAL")
    return temp_session_feature(instance)


@pytest.fixture
def primary_use_additional_information_type(
    temp_session_feature: ReturnSame,
) -> TypeOfAdditionalInformation:
    instance = TypeOfAdditionalInformation(value="paakayttotarkoitus", status="LOCAL")
    return temp_session_feature(instance)


@pytest.fixture
def reserved_additional_information_type(
    temp_session_feature: ReturnSame,
) -> TypeOfAdditionalInformation:
    instance = TypeOfAdditionalInformation(
        value="varattuKunnanKayttoon", status="LOCAL"
    )
    return temp_session_feature(instance)


@pytest.fixture
def intented_additional_information_type(
    temp_session_feature: ReturnSame,
) -> TypeOfAdditionalInformation:
    instance = TypeOfAdditionalInformation(
        value="kayttotarkoituskohdistus", status="LOCAL"
    )
    return temp_session_feature(instance)


@pytest.fixture
def land_use_area(
    temp_session_feature: ReturnSame,
    plan_instance: Plan,
    type_of_underground_instance: TypeOfUnderground,
) -> LandUseArea:
    instance = LandUseArea(
        plan=plan_instance,
        type_of_underground=type_of_underground_instance,
        geom=from_shape(
            MultiPolygon(
                [
                    Polygon(
                        (
                            (381849, 6677967),
                            (381849, 6680000),
                            (386378, 6680000),
                            (386378, 6677967),
                            (381849, 6677967),
                        )
                    )
                ]
            ),
            srid=PROJECT_SRID,
            extended=True,
        ),
    )
    temp_session_feature(instance)
    return instance


@pytest.fixture
def land_use_regulation_group(
    temp_session_feature: ReturnSame,
    plan_instance: Plan,
    land_use_regulation_group_type: TypeOfPlanRegulationGroup,
) -> PlanRegulationGroup:
    instance = PlanRegulationGroup(
        plan=plan_instance, type_of_plan_regulation_group=land_use_regulation_group_type
    )
    temp_session_feature(instance)
    return instance


@pytest.fixture
def living_area_primary_use_regulation_group(
    temp_session_feature: ReturnSame,
    land_use_regulation_group: PlanRegulationGroup,
    living_area_regulation_type: TypeOfPlanRegulation,
    primary_use_additional_information_type: TypeOfAdditionalInformation,
) -> PlanRegulationGroup:
    regulation = PlanRegulation(
        plan_regulation_group=land_use_regulation_group,
        type_of_plan_regulation=living_area_regulation_type,
    )
    temp_session_feature(regulation)

    ai = AdditionalInformation(
        type_of_additional_information=primary_use_additional_information_type,
        plan_regulation=regulation,
    )
    temp_session_feature(ai)

    return land_use_regulation_group


@pytest.fixture
def living_area_primary_use_with_reserved_regulation_group(
    temp_session_feature: ReturnSame,
    land_use_regulation_group: PlanRegulationGroup,
    living_area_regulation_type: TypeOfPlanRegulation,
    primary_use_additional_information_type: TypeOfAdditionalInformation,
    reserved_additional_information_type: TypeOfAdditionalInformation,
) -> PlanRegulationGroup:
    regulation = PlanRegulation(
        plan_regulation_group=land_use_regulation_group,
        type_of_plan_regulation=living_area_regulation_type,
    )
    temp_session_feature(regulation)

    ai = AdditionalInformation(
        type_of_additional_information=primary_use_additional_information_type,
        plan_regulation=regulation,
    )
    temp_session_feature(ai)

    reserved = AdditionalInformation(
        type_of_additional_information=reserved_additional_information_type,
        plan_regulation=regulation,
    )
    temp_session_feature(reserved)

    return land_use_regulation_group


@pytest.fixture
def living_area_primary_use_with_two_intented_uses_regulation_group(
    temp_session_feature: ReturnSame,
    land_use_regulation_group: PlanRegulationGroup,
    living_area_regulation_type: TypeOfPlanRegulation,
    primary_use_additional_information_type: TypeOfAdditionalInformation,
    intented_additional_information_type: TypeOfAdditionalInformation,
) -> PlanRegulationGroup:
    regulation = PlanRegulation(
        plan_regulation_group=land_use_regulation_group,
        type_of_plan_regulation=living_area_regulation_type,
    )
    temp_session_feature(regulation)

    primary = AdditionalInformation(
        type_of_additional_information=primary_use_additional_information_type,
        plan_regulation=regulation,
    )
    temp_session_feature(primary)
    intented_1 = AdditionalInformation(
        type_of_additional_information=intented_additional_information_type,
        plan_regulation=regulation,
        value_data_type=AttributeValueDataType.CODE,
        code_value="123",
    )
    temp_session_feature(intented_1)

    intented_2 = AdditionalInformation(
        type_of_additional_information=intented_additional_information_type,
        plan_regulation=regulation,
        value_data_type=AttributeValueDataType.CODE,
        code_value="abc",
    )
    temp_session_feature(intented_2)

    return land_use_regulation_group


@pytest.fixture
def land_use_area_with_living_area_primary_use_regulation(
    session: Session,
    land_use_area: LandUseArea,
    living_area_primary_use_regulation_group: PlanRegulationGroup,
) -> LandUseArea:
    land_use_area.plan_regulation_groups.append(
        living_area_primary_use_regulation_group
    )
    session.add(land_use_area)
    session.commit()
    return land_use_area


@pytest.fixture
def land_use_area_with_living_area_primary_use_reserved_regulation(
    session: Session,
    land_use_area: LandUseArea,
    living_area_primary_use_with_reserved_regulation_group: PlanRegulationGroup,
) -> LandUseArea:
    land_use_area.plan_regulation_groups.append(
        living_area_primary_use_with_reserved_regulation_group
    )
    session.add(land_use_area)
    session.commit()
    return land_use_area


@pytest.fixture
def land_use_area_with_living_area_primary_use_two_same_additional_info(
    session: Session,
    land_use_area: LandUseArea,
    living_area_primary_use_with_two_intented_uses_regulation_group: PlanRegulationGroup,
) -> LandUseArea:
    land_use_area.plan_regulation_groups.append(
        living_area_primary_use_with_two_intented_uses_regulation_group
    )
    session.add(land_use_area)
    session.commit()
    return land_use_area


@pytest.fixture
def line_regulation_group_with_numeric_value(
    temp_session_feature: ReturnSame,
    plan_instance: Plan,
    preparation_status_instance: LifeCycleStatus,
    type_of_line_plan_regulation_group_instance: TypeOfPlanRegulationGroup,
    density_regulation_type: TypeOfPlanRegulation,
) -> PlanRegulationGroup:
    group = PlanRegulationGroup(
        plan=plan_instance,
        type_of_plan_regulation_group=type_of_line_plan_regulation_group_instance,
        name={"fin": "Line regulation with value"},
    )
    group = temp_session_feature(group)

    regulation = PlanRegulation(
        plan_regulation_group=group,
        type_of_plan_regulation=density_regulation_type,
        lifecycle_status=preparation_status_instance,
        value_data_type=AttributeValueDataType.POSITIVE_NUMERIC,
        numeric_value=0.2,
        unit="m2/k-m2",
    )
    temp_session_feature(regulation)

    return group


@pytest.fixture
def line_regulation_group_with_additional_info_value(
    temp_session_feature: ReturnSame,
    plan_instance: Plan,
    preparation_status_instance: LifeCycleStatus,
    type_of_line_plan_regulation_group_instance: TypeOfPlanRegulationGroup,
    tree_row_regulation_type: TypeOfPlanRegulation,
    intented_additional_information_type: TypeOfAdditionalInformation,
) -> PlanRegulationGroup:
    group = PlanRegulationGroup(
        plan=plan_instance,
        type_of_plan_regulation_group=type_of_line_plan_regulation_group_instance,
        name={"fin": "Line regulation with additional info"},
    )
    group = temp_session_feature(group)

    regulation = PlanRegulation(
        plan_regulation_group=group,
        type_of_plan_regulation=tree_row_regulation_type,
        lifecycle_status=preparation_status_instance,
        ordering=1,
    )
    regulation = temp_session_feature(regulation)

    additional_info = AdditionalInformation(
        plan_regulation=regulation,
        type_of_additional_information=intented_additional_information_type,
        value_data_type=AttributeValueDataType.LOCALIZED_TEXT,
        text_value={"fin": "Lisätieto"},
    )
    temp_session_feature(additional_info)

    return group


@pytest.fixture
def line(
    temp_session_feature: ReturnSame,
    preparation_status_instance: LifeCycleStatus,
    type_of_underground_instance: TypeOfUnderground,
    plan_instance: Plan,
) -> Line:
    line = Line(
        geom=from_shape(
            MultiLineString([[[382000.0, 6678000.0], [383000.0, 6678100.0]]]),
            srid=PROJECT_SRID,
            extended=True,
        ),
        lifecycle_status=preparation_status_instance,
        type_of_underground=type_of_underground_instance,
        plan=plan_instance,
    )
    return temp_session_feature(line)


@pytest.fixture
def line_with_regulation_value_and_additional_info_with_value(
    session: Session,
    line: Line,
    line_regulation_group_with_numeric_value: PlanRegulationGroup,
    line_regulation_group_with_additional_info_value: PlanRegulationGroup,
) -> Line:
    session.add(line)
    line.plan_regulation_groups = [
        line_regulation_group_with_numeric_value,
        line_regulation_group_with_additional_info_value,
    ]
    session.commit()

    return line
