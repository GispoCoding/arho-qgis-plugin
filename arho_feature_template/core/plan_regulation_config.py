from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, cast

import yaml
from qgis.core import QgsProject
from qgis.utils import iface

from arho_feature_template.qgis_plugin_tools.tools.resources import resources_path

if TYPE_CHECKING:
    from typing import Literal

    from qgis.core import QgsMapLayer
    from qgis.gui import QgisInterface

    iface: QgisInterface = cast("QgisInterface", iface)  # type: ignore[no-redef]


logger = logging.getLogger(__name__)

DEFAULT_PLAN_REGULATIONS_CONFIG_PATH = Path(os.path.join(resources_path(), "kaavamaaraykset.yaml"))


class ConfigSyntaxError(Exception):
    def __init__(self, message: str):
        super().__init__(f"Invalid config syntax: {message}")


class UninitializedError(Exception):
    def __init__(self):
        super().__init__("PlanRegulationsSet is not initialized. Call 'load_config' first")


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


# TODO: Same as in PlanManager, should refactor
def get_layer_by_name(layer_name: str) -> QgsMapLayer | None:
    """Retrieve a layer by name from the project."""
    layers = QgsProject.instance().mapLayersByName(layer_name)
    if layers:
        return layers[0]
    iface.messageBar().pushMessage("Error", f"Layer '{layer_name}' not found", level=3)
    return None


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

    _instance: PlanRegulationsSet | None = None

    @classmethod
    def get_instance(cls) -> PlanRegulationsSet:
        """Get the singleton instance, if initialized."""
        if cls._instance is None:
            raise UninitializedError
        return cls._instance

    @classmethod
    def get_regulations(cls) -> list[PlanRegulationConfig]:
        """Get the list of regulation configs, if instance is initialized."""
        instance = cls.get_instance()
        return instance.regulations

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

        # Add names from plan regulation layer
        mapping = get_name_mapping_for_plan_regulations(type_of_plan_regulations_layer_name)
        if mapping:
            for regulation in cls.get_regulations():
                regulation.add_name(mapping, language)

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
