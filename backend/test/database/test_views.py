from __future__ import annotations

from collections.abc import Generator
from textwrap import dedent
from typing import TYPE_CHECKING, cast
from uuid import UUID, uuid4

import psycopg
import pytest
from psycopg import sql
from psycopg.types.json import Jsonb
from shapely import MultiPolygon, Polygon
from sqlalchemy.dialects import postgresql

from database.models import LandUseArea

if TYPE_CHECKING:
    from sqlalchemy import Table

    from database.codes import TypeOfUnderground
    from database.db_helper import ConnectionParameters
    from database.models import Plan

from psycopg.types import TypeInfo
from psycopg.types.shapely import register_shapely


@pytest.fixture(scope="module")
def conn(
    main_db_params_with_root_user: ConnectionParameters, hame_database_created: None
) -> Generator[psycopg.Connection]:
    with psycopg.connect(**main_db_params_with_root_user) as conn:
        yield conn


@pytest.mark.parametrize("table_name", ["land_use_area", "other_area", "line", "point"])
def test_plan_object_view_has_all_columns(
    table_name: str, conn: psycopg.Connection
) -> None:
    """Test that all columns in the base table are also in the view.

    We have created a view for each plan object table to include computed columns for
    visualization purposes. Views should have all the columns of the base table.
    Even if views are created with "SELECT *", if the base table is altered later,
    the view does not automatically get the new columns. This test ensures that all
    columns in the base table are also in the view.
    """
    columns_statement = dedent(
        """\
            SELECT column_name
            FROM information_schema.columns
            WHERE
                table_schema = 'hame'
                AND table_name = %s
            """
    )
    with conn.cursor() as cur:
        table_columns = {
            record[0] for record in cur.execute(columns_statement, (table_name,))
        }
        view_columns = {
            record[0] for record in cur.execute(columns_statement, (f"{table_name}_v",))
        }
    assert table_columns.issubset(view_columns)


def test_instead_of_insert_trigger_for_land_use_view(
    conn: psycopg.Connection,
    plan_instance: Plan,
    type_of_underground_instance: TypeOfUnderground,
) -> None:
    geom_type_info = TypeInfo.fetch(conn, "geometry")
    assert geom_type_info
    register_shapely(geom_type_info, conn)

    values = {
        "id": uuid4(),
        "plan_id": UUID(plan_instance.id),
        "type_of_underground_id": UUID(type_of_underground_instance.id),
        "name": {"fin": "test"},
        "description": {"fin": "test description"},
        "source_data_object": "test source",
        "height_min": 10.5,
        "height_max": 20.5,
        "height_unit": "m",
        "height_reference_point": "point",
        "ordering": 1,
        "geom": MultiPolygon(
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
    }

    land_use_area_table = cast("Table", LandUseArea.__table__)
    insert_statement = land_use_area_table.insert().values(
        {
            column: Jsonb(value) if isinstance(value, dict) else value
            for column, value in values.items()
        }
    )

    compiled = insert_statement.compile(dialect=postgresql.dialect())
    # The insert statement is for the base table, but we want to test the insert into
    # the view
    insert_sql = str(compiled).replace("hame.land_use_area", "hame.land_use_area_v")
    insert_params = compiled.params

    select_statement = sql.SQL(
        "SELECT {fields} FROM hame.land_use_area WHERE id = %s"
    ).format(fields=sql.SQL(",").join(sql.Identifier(f) for f in values))

    with conn.cursor() as cur:
        # Insert into the view
        cur.execute(insert_sql, insert_params)
        # Select from the base table
        cur.execute(select_statement, (values["id"],))
        row = cur.fetchone()

    try:
        assert row is not None
        result = dict(zip(values.keys(), row, strict=True))
        assert result == values
    finally:
        conn.rollback()
