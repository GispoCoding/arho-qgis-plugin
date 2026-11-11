from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import psycopg

    from database.models import LandUseArea


def test_primary_use_regulations_simple_land_use_area(
    conn: psycopg.Connection,
    land_use_area_with_living_area_primary_use_regulation: LandUseArea,
) -> None:
    with conn.cursor() as cur:
        cur.execute(
            "select hame.primary_use_regulations(%s)",
            (land_use_area_with_living_area_primary_use_regulation.id,),
        )
        row = cur.fetchone()
    assert row is not None
    assert row[0] == {"asumisenAlue": {}}


def test_primary_use_regulations_land_use_area_with_reserved_additional_info(
    conn: psycopg.Connection,
    land_use_area_with_living_area_primary_use_reserved_regulation: LandUseArea,
) -> None:
    with conn.cursor() as cur:
        cur.execute(
            "select hame.primary_use_regulations(%s)",
            (land_use_area_with_living_area_primary_use_reserved_regulation.id,),
        )
        row = cur.fetchone()
    assert row is not None
    assert row[0] == {"asumisenAlue": {"varattuKunnanKayttoon": [{}]}}


def test_primary_use_regulations_land_use_area_with_two_same_additional_info(
    conn: psycopg.Connection,
    land_use_area_with_living_area_primary_use_two_same_additional_info: LandUseArea,
) -> None:
    with conn.cursor() as cur:
        cur.execute(
            "select hame.primary_use_regulations(%s)",
            (land_use_area_with_living_area_primary_use_two_same_additional_info.id,),
        )
        row = cur.fetchone()
    assert row is not None
    assert row[0] == {
        "asumisenAlue": {
            "kayttotarkoituskohdistus": [{"code_value": "123"}, {"code_value": "abc"}]
        }
    }
