from __future__ import annotations

from importlib import resources
from pathlib import Path
from typing import TYPE_CHECKING, Iterable

from qgis.PyQt.QtCore import QSettings

if TYPE_CHECKING:
    from collections.abc import Iterator


USER_PLAN_FEATURE_TEMPLATE_LIBRARIES_KEY = "arho/user_plan_feature_library_paths"


def get_default_plan_feature_library_config_files() -> Iterator[Path]:
    """Get all default plan feature library configuration files."""

    for resource in resources.files(__package__).iterdir():
        with resources.as_file(resource) as resource_path:
            if resource_path.suffix == ".yaml":
                yield resource_path


def get_user_plan_feature_library_config_files() -> list[Path]:
    """Get all user plan feature configuration files."""

    paths_str = QSettings().value(USER_PLAN_FEATURE_TEMPLATE_LIBRARIES_KEY, None)
    return [Path(path) for path in paths_str.split(";")] if paths_str else []


def set_user_plan_feature_library_config_files(paths: Iterable[str]):
    """Set all user plan feature library configuration files."""

    QSettings().setValue(USER_PLAN_FEATURE_TEMPLATE_LIBRARIES_KEY, ";".join(str(path) for path in paths))
