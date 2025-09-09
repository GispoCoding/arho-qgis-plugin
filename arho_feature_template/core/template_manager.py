from __future__ import annotations

import os
from pathlib import Path

import yaml

from arho_feature_template.utils.misc_utils import iface


class TemplateManager:
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
    def _write_to_yaml_file(cls, config_data: dict, file_path: Path, overwrite: bool):  # noqa: FBT001
        if not overwrite and os.path.exists(file_path):
            return

        cleaned_data = cls._clean_data(config_data)

        with file_path.open("w", encoding="utf-8") as yaml_file:
            yaml.safe_dump(cleaned_data, yaml_file, sort_keys=False, allow_unicode=True, default_flow_style=False)

    @classmethod
    def _read_from_yaml_file(cls, file_path: Path, fail_msg: str) -> dict:
        if file_path.exists():
            try:
                with file_path.open(encoding="utf-8") as f:
                    template_data = yaml.safe_load(f)
                    return template_data if template_data is not None else {}
            except IsADirectoryError:
                iface.messageBar().pushCritical("", fail_msg)
                return {}
        else:
            iface.messageBar().pushCritical("", fail_msg)
            return {}

    @classmethod
    def read_regulation_group_template_file(cls, file_path: Path | str) -> dict:
        data = cls._read_from_yaml_file(
            file_path=file_path if type(file_path) is Path else Path(file_path),
            fail_msg=f"Kaavamääräyskirjastoa ei löytynyt määritellystä tiedostopolusta: {file_path}",
        )
        library_type = data.get("library_type")
        if not library_type or library_type != "regulation_group":
            return {}
        return data

    @classmethod
    def read_plan_feature_template_file(cls, file_path: Path | str) -> dict:
        data = cls._read_from_yaml_file(
            file_path=file_path if type(file_path) is Path else Path(file_path),
            fail_msg=f"Kaavakohdekirjastoa ei löytynyt määritellystä tiedostopolusta: {file_path}",
        )
        library_type = data.get("library_type")
        if not library_type or library_type != "plan_feature":
            return {}
        return data

    @classmethod
    def write_regulation_group_template_file(
        cls,
        regulation_group_config_data: dict,
        file_path: Path | str,
        overwrite: bool = True,  # noqa: FBT001, FBT002
    ):
        regulation_group_config_data["library_type"] = "regulation_group"
        cls._write_to_yaml_file(
            config_data=regulation_group_config_data,
            file_path=file_path if type(file_path) is Path else Path(file_path),
            overwrite=overwrite,
        )

    @classmethod
    def write_plan_feature_template_file(
        cls,
        plan_feature_config_data: dict,
        file_path: Path | str,
        overwrite: bool = True,  # noqa: FBT001, FBT002
    ):
        plan_feature_config_data["library_type"] = "plan_feature"
        cls._write_to_yaml_file(
            config_data=plan_feature_config_data,
            file_path=file_path if type(file_path) is Path else Path(file_path),
            overwrite=overwrite,
        )

    @classmethod
    def delete_template_file(cls, file_path: Path | str) -> bool:
        file_path = file_path if type(file_path) is Path else Path(file_path)
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
