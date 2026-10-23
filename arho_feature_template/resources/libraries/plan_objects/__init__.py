from __future__ import annotations

from pathlib import Path
from typing import Iterable

from qgis.PyQt.QtCore import QSettings

USER_PLAN_OBJECT_TEMPLATE_LIBRARIES_KEY = "arho/user_plan_object_library_paths"
# Key of an earlier version, which called plan objects plan features
_OLD_USER_PLAN_OBJECT_TEMPLATE_LIBRARIES_KEY = "arho/user_plan_feature_library_paths"


def get_user_plan_object_library_config_files() -> list[Path]:
    """Get all user plan object library configuration files."""

    paths_str = QSettings().value(USER_PLAN_OBJECT_TEMPLATE_LIBRARIES_KEY, None)
    return [Path(path) for path in paths_str.split(";")] if paths_str else []


def set_user_plan_object_library_config_files(paths: Iterable[str]):
    """Set all user plan object library configuration files."""

    QSettings().setValue(USER_PLAN_OBJECT_TEMPLATE_LIBRARIES_KEY, ";".join(str(path) for path in paths))


def migrate_user_plan_object_library_paths_key():
    """Move the library paths away from the key an earlier version wrote them to."""
    settings = QSettings()
    value = settings.value(_OLD_USER_PLAN_OBJECT_TEMPLATE_LIBRARIES_KEY, None)
    if value is not None:
        if settings.value(USER_PLAN_OBJECT_TEMPLATE_LIBRARIES_KEY, None) is None:
            settings.setValue(USER_PLAN_OBJECT_TEMPLATE_LIBRARIES_KEY, value)
        settings.remove(_OLD_USER_PLAN_OBJECT_TEMPLATE_LIBRARIES_KEY)
