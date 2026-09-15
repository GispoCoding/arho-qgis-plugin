import pytest
from qgis.core import QgsSettings

from arho_feature_template.core.settings_manager import SettingsManager
from arho_feature_template.qgis_plugin_tools.tools.custom_logging import (
    LogTarget,
    get_log_level_key,
    get_log_level_name,
)
from arho_feature_template.qgis_plugin_tools.tools.settings import setting_key


@pytest.fixture(autouse=True)
def _clean_log_level_settings():
    yield
    settings = QgsSettings()
    for target in LogTarget:
        settings.remove(get_log_level_key(target))
        settings.remove(setting_key(get_log_level_key(target)))


@pytest.mark.parametrize("target", list(LogTarget))
def test_log_level_round_trip(target: LogTarget):
    SettingsManager.set_log_level(target, "WARNING")

    assert SettingsManager.get_log_level(target) == "WARNING"


@pytest.mark.parametrize("target", list(LogTarget))
def test_log_level_is_visible_to_plugin_tools_logger(target: LogTarget):
    SettingsManager.set_log_level(target, "ERROR")

    assert get_log_level_name(target) == "ERROR"


@pytest.mark.parametrize("target", list(LogTarget))
def test_log_level_defaults_when_not_set(target: LogTarget):
    assert not SettingsManager.log_level_is_set(target)
    assert SettingsManager.get_log_level(target) == target.default_level

    SettingsManager.set_log_level(target, "DEBUG")

    assert SettingsManager.log_level_is_set(target)


def test_migrate_log_level_keys_moves_doubled_key():
    target = LogTarget.STREAM
    old_key = setting_key(get_log_level_key(target))
    QgsSettings().setValue(old_key, "CRITICAL")

    SettingsManager.migrate_log_level_keys()

    assert SettingsManager.get_log_level(target) == "CRITICAL"
    assert QgsSettings().value(old_key, None) is None
