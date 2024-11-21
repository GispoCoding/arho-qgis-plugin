from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, cast

import yaml
from qgis.utils import iface

from arho_feature_template.qgis_plugin_tools.tools.resources import resources_path
from arho_feature_template.utils.misc_utils import get_layer_by_name

if TYPE_CHECKING:
    from numbers import Number
    from typing import Literal

    from qgis.gui import QgisInterface

    iface: QgisInterface = cast("QgisInterface", iface)  # type: ignore[no-redef]


logger = logging.getLogger(__name__)

DEFAULT_PLAN_REGULATIONS_CONFIG_PATH = Path(os.path.join(resources_path(), "kaavamaaraykset.yaml"))


class ConfigSyntaxError(Exception):
    def __init__(self, message: str):
        super().__init__(f"Invalid config syntax: {message}")


class UninitializedError(Exception):
    def __init__(self):
        super().__init__("PlanRegulationsSet is not initialized. Call 'initialize' first")


class ValueType(Enum):
    DECIMAL = "desimaali"
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
    DEGREES = "°"
    DECIBEL = "dB"


def get_name_mapping_for_plan_regulations(layer_name: str) -> dict[str, dict[str, str]] | None:
    layer = get_layer_by_name(layer_name)
    if not layer:
        return None
    return {feature["value"]: feature["name"] for feature in layer.getFeatures()}


@dataclass
class PlanRegulationsSet:
    """Describes the set of plan regulations."""

    version: str
    regulations: list[PlanRegulationConfig]
    regulations_dict: dict[str, PlanRegulationConfig] = field(default_factory=dict)

    _instance: PlanRegulationsSet | None = None

    @classmethod
    def get_instance(cls) -> PlanRegulationsSet:
        """Get the singleton instance, if initialized."""
        if cls._instance is None:
            raise UninitializedError
        return cls._instance

    @classmethod
    def get_regulations(cls) -> list[PlanRegulationConfig]:
        """Get the list of top-level regulation configs, if instance is initialized."""
        return cls.get_instance().regulations

    @classmethod
    def get_regulations_dict(cls) -> dict[str, PlanRegulationConfig]:
        """Get all regulations in a dictionary where keys are regulations codes and values PlanRegulationConfigs."""
        return cls.get_instance().regulations_dict

    @classmethod
    def get_regulation_by_code(cls, regulation_code: str) -> PlanRegulationConfig | None:
        """Get a regulation by it's regulation code (if exists)."""
        return cls.get_instance().regulations_dict.get(regulation_code)

    @classmethod
    def initialize(
        cls,
        config_path: Path = DEFAULT_PLAN_REGULATIONS_CONFIG_PATH,
        type_of_plan_regulations_layer_name="Kaavamääräyslaji",
        language: Literal["fin", "eng", "swe"] = "fin",
    ) -> PlanRegulationsSet:
        # Initialize PlanRegulationsSet and PlanRegulationConfigs from config file
        with config_path.open(encoding="utf-8") as f:
            data = yaml.safe_load(f)
            cls._instance = cls.from_dict(data)

        regulations = cls.get_regulations()
        regulations_dict: dict[str, PlanRegulationConfig] = {}
        mapping = get_name_mapping_for_plan_regulations(type_of_plan_regulations_layer_name)

        # Add names to dictionary, add names to regulations
        for regulation in regulations:
            regulation.add_to_dictionary(regulations_dict)
            if mapping:
                regulation.add_name(mapping, language)

        cls._instance.regulations_dict = regulations_dict
        logger.info("PlanRegulationsSet initialized successfully.")
        return cls._instance

    @classmethod
    def from_dict(cls, data: dict) -> PlanRegulationsSet:
        file_version = data["version"]
        try:
            return cls(
                version=file_version,
                regulations=[PlanRegulationConfig.from_dict(config) for config in data["plan_regulations"]],
            )
        except KeyError as e:
            raise ConfigSyntaxError(str(e)) from e


@dataclass
class PlanRegulationConfig:
    """Describes the configuration of a plan regulation."""

    regulation_code: str
    name: str
    category_only: bool
    value_type: ValueType | None
    unit: Unit | None
    child_regulations: list[PlanRegulationConfig]

    @classmethod
    def from_dict(cls, data: dict) -> PlanRegulationConfig:
        """
        Initialize PlanRegulationConfig from dict.

        Intializes child regulations recursively.
        """
        return cls(
            regulation_code=data["regulation_code"],
            name=data["regulation_code"],
            category_only=data.get("category_only", False),
            value_type=ValueType(data["value_type"]) if "value_type" in data else None,
            unit=Unit(data["unit"]) if "unit" in data else None,
            child_regulations=[PlanRegulationConfig.from_dict(config) for config in data.get("child_regulations", [])],
        )

    def add_name(self, code_to_name_mapping: dict[str, dict[str, str]], language: Literal["fin", "eng", "swe"]):
        language_to_name_dict = code_to_name_mapping.get(self.regulation_code)
        self.name = language_to_name_dict[language] if language_to_name_dict else self.regulation_code
        for regulation in self.child_regulations:
            regulation.add_name(code_to_name_mapping, language)

    def add_to_dictionary(self, dictionary: dict[str, PlanRegulationConfig]):
        dictionary[self.regulation_code] = self
        for regulation in self.child_regulations:
            regulation.add_to_dictionary(dictionary)


@dataclass
class PlanRegulationDefinition:
    """Associates a PlanRegulationConfig with an optional default value and additional data."""

    regulation_config: PlanRegulationConfig
    default_value: str | Number | None
    additional_information: list[
        dict[str, str | Number | None]
    ]  # NOTE: Correct typing for additional information values?
    regulation_number: int | None
    attached_files: list[Path]

    @classmethod
    def from_dict(cls, data: dict) -> PlanRegulationDefinition:
        return cls(
            regulation_config=data["config"],
            default_value=data.get("default_value"),
            additional_information=data.get("additional_information", []),
            regulation_number=data.get("regulation_number"),
            attached_files=data.get("attached_files", []),
        )
