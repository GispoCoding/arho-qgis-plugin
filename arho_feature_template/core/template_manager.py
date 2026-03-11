from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

import yaml
from qgis.PyQt.QtCore import QObject, pyqtSignal

from arho_feature_template.resources.libraries.feature_templates import (
    get_user_plan_feature_library_config_files,
    set_user_plan_feature_library_config_files,
)
from arho_feature_template.utils.misc_utils import iface

if TYPE_CHECKING:
    from arho_feature_template.core.models import PlanFeatureLibrary, PlanObject


logger = logging.getLogger(__name__)


class SignalManager(QObject):
    feature_object_added_to_library = pyqtSignal()


class TemplateManager:
    signal_manager = SignalManager()
    # NOTE: Consider refactoring this class into utils

    @classmethod
    def _clean_data(cls, data: dict | list | str | float):
        """Recursively removes keys with None, empty string, or empty-list values from a dict or list."""
        if isinstance(data, dict):
            cleaned_dict = {}
            for key, value in data.items():
                cleaned_value = cls._clean_data(value)
                # Skip keys where the cleaned value is None, empty string, or an empty list
                if (
                    cleaned_value is None
                    or cleaned_value == ""
                    or (isinstance(cleaned_value, list) and len(cleaned_value) == 0)
                ):
                    continue
                cleaned_dict[key] = cleaned_value
            return cleaned_dict

        if isinstance(data, list):
            return [cls._clean_data(item) for item in data]

        return data

    @classmethod
    def _write_to_yaml_file(cls, config_data: dict, file_path: Path):
        logger.debug("Writing YAML file path=%s", file_path)
        cleaned_data = cls._clean_data(config_data)
        with file_path.open("w", encoding="utf-8") as yaml_file:
            yaml.safe_dump(cleaned_data, yaml_file, sort_keys=False, allow_unicode=True, default_flow_style=False)
        logger.debug("YAML write completed path=%s", file_path)

    @classmethod
    def _read_from_yaml_file(cls, file_path: Path, fail_msg: str) -> dict:
        logger.debug("Reading YAML file path=%s", file_path)
        if file_path.exists():
            try:
                with file_path.open(encoding="utf-8") as f:
                    template_data = yaml.safe_load(f)
                    logger.debug("YAML read completed path=%s has_data=%s", file_path, template_data is not None)
                    return template_data if template_data is not None else {}
            except IsADirectoryError:
                logger.error("YAML read failed path is directory path=%s", file_path)  # noqa: TRY400
                iface.messageBar().pushCritical("", fail_msg)
                return {}
        else:
            logger.error("YAML read failed path does not exist path=%s", file_path)
            iface.messageBar().pushCritical("", fail_msg)
            return {}

    # @classmethod
    # def read_regulation_group_template_file(cls, file_path: Path | str) -> dict:
    #     data = cls._read_from_yaml_file(
    #         file_path=file_path if type(file_path) is Path else Path(file_path),
    #         fail_msg=f"Kaavamääräyskirjastoa ei löytynyt määritellystä tiedostopolusta: {file_path}",
    #     )
    #     library_type = data.get("library_type")
    #     if not library_type or library_type != "regulation_group":
    #         return {}
    #     return data

    @classmethod
    def read_library_config_file(cls, file_path: Path | str, expected_library_type: str) -> dict:
        logger.debug("Reading library config path=%s expected_type=%s", file_path, expected_library_type)
        data = cls._read_from_yaml_file(
            file_path=file_path if type(file_path) is Path else Path(file_path),
            fail_msg=f"Kirjastoa ei löytynyt määritellystä tiedostopolusta: {file_path}",
        )
        library_type = data.get("library_type")
        if not library_type or library_type != expected_library_type:
            logger.warning("Library type mismatch path=%s found_type=%s", file_path, library_type)
            iface.messageBar().pushCritical("", f"Kirjaston tyyppiä ei löytynyt tai se oli väärä: {library_type}")
            return {}
        logger.debug("Library config read successfully path=%s", file_path)
        return data

    # @classmethod
    # def read_plan_feature_template_file(cls, file_path: Path | str) -> dict:
    #     data = cls._read_from_yaml_file(
    #         file_path=file_path if type(file_path) is Path else Path(file_path),
    #         fail_msg=f"Kaavakohdekirjastoa ei löytynyt määritellystä tiedostopolusta: {file_path}",
    #     )
    #     library_type = data.get("library_type")
    #     if not library_type or library_type != "plan_feature":
    #         return {}
    #     return data

    @classmethod
    def write_regulation_group_template_file(
        cls,
        regulation_group_config_data: dict,
        file_path: Path | str,
    ):
        logger.debug("Writing regulation group template file path=%s", file_path)
        regulation_group_config_data["library_type"] = "regulation_group"
        cls._write_to_yaml_file(
            config_data=regulation_group_config_data,
            file_path=file_path if type(file_path) is Path else Path(file_path),
        )

    @classmethod
    def write_plan_feature_template_file(
        cls,
        plan_feature_config_data: dict,
        file_path: Path | str,
    ):
        logger.debug("Writing plan feature template file path=%s", file_path)
        plan_feature_config_data["library_type"] = "plan_feature"
        return cls._write_to_yaml_file(
            config_data=plan_feature_config_data,
            file_path=file_path if type(file_path) is Path else Path(file_path),
        )

    @classmethod
    def save_plan_object_to_library(cls, plan_object_model: PlanObject, library: PlanFeatureLibrary):
        logger.debug("Saving plan object to library library=%s", library.name)
        if not library.file_path:
            logger.warning("Library has no file path, skipping save")
            return

        # plan_id and geom are not saved into library
        plan_object_model.plan_id = None
        plan_object_model.geom = None

        # Check if plan object is already saved into library
        library_hash_map = library.into_hash_map()
        plan_object_hash = plan_object_model.data_hash()
        if plan_object_hash in library_hash_map:
            logger.warning("Plan object already exists in library path=%s", library.file_path)
            iface.messageBar().pushMessage("", "Kaavakohde on jo tallennettu kaavakohdepohjakirjastoon.")
            return

        library.plan_features.append(plan_object_model)
        TemplateManager.write_plan_feature_template_file(
            plan_feature_config_data=library.into_template_dict(), file_path=Path(library.file_path)
        )
        logger.debug("Plan object saved to library path=%s", library.file_path)
        iface.messageBar().pushSuccess("", "Kaavakohde tallennettu kaavakohdepohjakirjastoon.")

        library_file_paths = get_user_plan_feature_library_config_files()
        library_file_paths_as_str = [str(path) for path in library_file_paths]
        set_user_plan_feature_library_config_files(library_file_paths_as_str)
        TemplateManager.signal_manager.feature_object_added_to_library.emit()
        logger.debug("Updated user plan feature library config paths and emitted update signal")
