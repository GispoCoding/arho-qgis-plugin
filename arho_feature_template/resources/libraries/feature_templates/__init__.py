from __future__ import annotations

from pathlib import Path
from typing import Iterable

from qgis.PyQt.QtCore import QSettings

USER_PLAN_FEATURE_TEMPLATE_LIBRARIES_KEY = "arho/user_plan_feature_library_paths"


def get_user_plan_feature_library_config_files() -> list[Path]:
    """Get all user plan feature configuration files."""

    paths_str = QSettings().value(USER_PLAN_FEATURE_TEMPLATE_LIBRARIES_KEY, None)
    return [Path(path) for path in paths_str.split(";")] if paths_str else []


def set_user_plan_feature_library_config_files(paths: Iterable[str]):
    """Set all user plan feature library configuration files."""

    QSettings().setValue(USER_PLAN_FEATURE_TEMPLATE_LIBRARIES_KEY, ";".join(str(path) for path in paths))
