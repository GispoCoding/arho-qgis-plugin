from __future__ import annotations

import ast
from typing import TYPE_CHECKING, Any

from qgis.core import QgsSettings
from qgis.PyQt.QtCore import QObject, QSettings, QTimer, pyqtSignal

if TYPE_CHECKING:
    from arho_feature_template.project.layers.code_layers import PlanType
    from arho_feature_template.project.layers.plan_layers import PlanObjectLayer

LAYER_NAME_TRANSLATION_MAP = {
    "Aluevaraus": "land_use_area",
    "Osa-alue": "other_area",
    "Viivat": "line",
    "Pisteet": "point",
}


class SettingsNotifier(QObject):
    settings_saved = pyqtSignal()


class SettingsManager:
    GROUP = "plugins/arho"
    MIGRATIONS_RUN = False

    notifier = SettingsNotifier()

    @classmethod
    def _full_key(cls, key: str) -> str:
        return f"{cls.GROUP}/{key}"

    @classmethod
    def _set(cls, key: str, value: Any):
        QgsSettings().setValue(cls._full_key(key), value)

    @classmethod
    def _get(cls, key: str, default: Any) -> Any:
        if not cls.MIGRATIONS_RUN:
            cls._migrate_keys()
        return QgsSettings().value(cls._full_key(key), default, type(default))

    @classmethod
    def finish(cls):
        """Call after setting keys to emit the `settings_saved` signal via `notifier`."""

        # Wait a tick to ensure settings are saved and applied
        def _emit_changed_signal():
            SettingsManager.notifier.settings_saved.emit()

        QTimer.singleShot(0, _emit_changed_signal)

    # LAMBDA SETTINGS
    @classmethod
    def get_proxy_host(cls, default: str = "localhost") -> str:
        return cls._get("proxy_host", default)

    @classmethod
    def set_proxy_host(cls, value: int):
        cls._set("proxy_host", value)

    @classmethod
    def get_proxy_port(cls, default: int = 5443) -> int | None:
        port = cls._get("proxy_port", default)
        return port if port > 0 else None

    @classmethod
    def set_proxy_port(cls, value: int | None):
        cls._set("proxy_port", 0 if value is None else value)

    @classmethod
    def get_lambda_url(cls, default: str = "https://t5w26iqnsf.execute-api.eu-central-1.amazonaws.com/v0/ryhti") -> str:
        return cls._get("lambda_url", default)

    @classmethod
    def set_lambda_url(cls, value: str):
        cls._set("lambda_url", value)

    # SERVICE BUS SETTINGS
    @classmethod
    def get_data_exchange_layer_enabled(cls, default: bool = True) -> bool:  # noqa: FBT001, FBT002
        return cls._get("data_exchange_layer_enabled", default)

    @classmethod
    def set_data_exchange_layer_enabled(cls, value: bool):  # noqa: FBT001
        cls._set("data_exchange_layer_enabled", value)

    # VISUALISATIONS
    @classmethod
    def get_layer_style_path(cls, plan_type: PlanType, layer: type[PlanObjectLayer], default: str) -> str:
        return cls._get(f"{plan_type.value}_{LAYER_NAME_TRANSLATION_MAP[layer.name]}_style_path", default)

    @classmethod
    def set_layer_style_path(cls, plan_type: PlanType, layer: type[PlanObjectLayer], value: str):
        cls._set(f"{plan_type.value}_{LAYER_NAME_TRANSLATION_MAP[layer.name]}_style_path", value)

    # LANGUAGES
    @classmethod
    def get_primary_language(cls, default: str = "fin") -> str:
        """Language as language code (e.g. "fin")."""
        return cls._get("primary_language", default)

    @classmethod
    def set_primary_language(cls, value: str):
        """Language as language code (e.g. "fin")."""
        cls._set("primary_language", value)

    @classmethod
    def get_languages(cls, default: str = "['fin']") -> list[str]:
        """Languages as language codes (e.g. "fin")."""
        return ast.literal_eval(cls._get("languages", default))

    @classmethod
    def set_languages(cls, value: list[str]):
        """Languages as language codes (e.g. "fin")."""
        value_to_save = str(value)
        cls._set("languages", value_to_save)  # Save list as str

    @classmethod
    def get_show_only_primary_language(cls, default: bool = False) -> bool:  # noqa: FBT001, FBT002
        return cls._get("show_only_primary_language", default)

    @classmethod
    def set_show_only_primary_language(cls, value: bool):  # noqa: FBT001
        return cls._set("show_only_primary_language", value)

    @classmethod
    def set_add_only_selected_languages(cls, value: bool):  # noqa: FBT001
        return cls._set("add_only_selected_languages", value)

    @classmethod
    def get_add_only_selected_languages(cls, default: bool = False) -> bool:  # noqa: FBT001, FBT002
        return cls._get("add_only_selected_languages", default)

    @classmethod
    def _migrate_keys(cls):
        # Old settings
        settings = QSettings("ArhoFeatureTemplate")

        proxy_host = settings.value("proxy_host", None)
        if proxy_host is not None:
            cls.set_proxy_host(proxy_host)
            settings.remove("proxy_host")

        proxy_port = settings.value("proxy_port", None)
        if proxy_port is not None:
            try:
                cls.set_proxy_port(int(proxy_port))
            except ValueError:
                cls.set_proxy_port(0)
            settings.remove("proxy_port")

        lambda_url = settings.value("lambda_url", None)
        if lambda_url is not None:
            cls.set_lambda_url(lambda_url)
            settings.remove("lambda_url")

        cls.MIGRATIONS_RUN = True
