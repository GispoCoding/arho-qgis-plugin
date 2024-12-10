from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from qgis.core import QgsGeometry


@dataclass
class Regulation:
    type_code: str
    value_string: str | None
    value_int: int | None
    value_float: float | None
    unit: str | None
    id_: int | None = None


@dataclass
class RegulationGroup:
    name: str
    short_name: str | None
    type_code: str
    regulations: list[Regulation]
    id_: int | None = None


@dataclass
class Plan:
    name: str
    description: str | None
    plan_type_id: str
    lifecycle_status_id: str
    record_number: str | None
    matter_management_identifier: str | None
    permanent_plan_identifier: str | None
    producers_plan_identifier: str | None
    organisation_id: str | None = None
    general_regulations: list[RegulationGroup] = field(default_factory=list)
    geom: QgsGeometry | None = None
    id_: int | None = None
