import pytest
from qgis.PyQt.QtCore import QSettings

from arho_feature_template.resources.libraries.plan_objects import (
    USER_PLAN_OBJECT_TEMPLATE_LIBRARIES_KEY,
    get_user_plan_object_library_config_files,
    migrate_user_plan_object_library_paths_key,
)

OLD_KEY = "arho/user_plan_feature_library_paths"


@pytest.fixture(autouse=True)
def _clean_library_path_settings():
    settings = QSettings()
    saved = {key: settings.value(key, None) for key in (OLD_KEY, USER_PLAN_OBJECT_TEMPLATE_LIBRARIES_KEY)}
    for key in saved:
        settings.remove(key)
    yield
    for key, value in saved.items():
        settings.remove(key)
        if value is not None:
            settings.setValue(key, value)


def test_migration_moves_the_old_key():
    QSettings().setValue(OLD_KEY, "a.yaml;b.yaml")

    migrate_user_plan_object_library_paths_key()

    assert [path.name for path in get_user_plan_object_library_config_files()] == ["a.yaml", "b.yaml"]
    assert QSettings().value(OLD_KEY, None) is None


def test_migration_keeps_the_new_key_when_both_are_set():
    QSettings().setValue(OLD_KEY, "old.yaml")
    QSettings().setValue(USER_PLAN_OBJECT_TEMPLATE_LIBRARIES_KEY, "new.yaml")

    migrate_user_plan_object_library_paths_key()

    assert [path.name for path in get_user_plan_object_library_config_files()] == ["new.yaml"]
    assert QSettings().value(OLD_KEY, None) is None


def test_migration_without_the_old_key_changes_nothing():
    migrate_user_plan_object_library_paths_key()

    assert QSettings().value(USER_PLAN_OBJECT_TEMPLATE_LIBRARIES_KEY, None) is None
