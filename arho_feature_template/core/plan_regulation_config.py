from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

import yaml

if TYPE_CHECKING:
    from pathlib import Path

logger = logging.getLogger(__name__)


class ConfigSyntaxError(Exception):
    def __init__(self, message: str):
        super().__init__(f"Invalid config syntax: {message}")


class ValueType(Enum):
    POSITIVE_DECIMAL = "positiivinen desimaali"
    POSITIVE_INTEGER = "positiivinen kokonaisluku"
    POSITIVE_INTEGER_RANGE = "positiivinen kokonaisluku arvoväli"
    VERSIONED_TEXT = "kieliversioitu teksti"


class Unit(Enum):
    SQUARE_METERS = "k-m2"
    CUBIC_METERS = "m3"
    EFFICIENCY_RATIO = "k-m2/m2"
    PERCENTAGE = "prosentti"
    AREA_RATIO = "m2/k-m2"


@dataclass
class PlanRegulationsConfig:
    """Describes the configurations of plan regulations."""

    version: str
    regulations: list[PlanRegulationConfig]

    @classmethod
    def from_dict(cls, data: dict) -> PlanRegulationsConfig:
        file_version = data["version"]
        try:
            return cls(
                version=file_version,
                regulations=[PlanRegulationConfig.from_dict(template) for template in data["plan_regulations"]],
            )
        except KeyError as e:
            raise ConfigSyntaxError(str(e)) from e


@dataclass
class PlanRegulationConfig:
    """Describes the configuration of a plan regulation."""

    regulation_code: str
    parent_regulation: str | None
    heading_only: bool
    letter_code: str | None
    value_type: ValueType | None
    unit: Unit | None

    @classmethod
    def from_dict(cls, data: dict) -> PlanRegulationConfig:
        return cls(
            regulation_code=data["regulation_code"],
            parent_regulation=data.get("parent_regulation"),
            heading_only=data.get("heading_only", False),
            letter_code=data.get("letter_code"),
            value_type=ValueType(data["value_type"]) if "value_type" in data else None,
            unit=Unit(data["unit"]) if "unit" in data else None,
        )


def parse_plan_regulations_config(plan_regulations_config_path: Path) -> PlanRegulationsConfig:
    with plan_regulations_config_path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
        return PlanRegulationsConfig.from_dict(data)
