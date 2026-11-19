from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import psycopg

    from database.models import Line


def test_type_regulations(
    conn: psycopg.Connection,
    line_with_regulation_value_and_additional_info_with_value: Line,
) -> None:
    with conn.cursor() as cur:
        cur.execute(
            "select hame.type_regulations('line', %s)",
            (line_with_regulation_value_and_additional_info_with_value.id,),
        )
        row = cur.fetchone()

    assert row is not None
    assert row[0] == {
        "puuTaiPuurivi": {
            "kayttotarkoituskohdistus": [{"text_value": {"fin": "Lisätieto"}}]
        }
    }
