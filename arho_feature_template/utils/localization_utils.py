from __future__ import annotations

from typing import TYPE_CHECKING, Any

from arho_feature_template.core.settings_manager import SettingsManager
from arho_feature_template.project.layers.code_layers import LanguageLayer

if TYPE_CHECKING:
    from arho_feature_template.core.models import LocalizedText


def _primary_language_code() -> str:
    return SettingsManager.get_primary_language()


def get_localized_text(localized_text: LocalizedText | None | Any, language_code: str | None = None) -> str | None:
    """Returns text for one language from input LocalizedText (dict).

    If `language_code` is not defined, primary language from settings is used."""
    if not isinstance(localized_text, dict):
        return None

    return localized_text.get(language_code if language_code else _primary_language_code())


def localized_text_as_str(localized_text: LocalizedText | None = None, indent_size: int = 0) -> str:
    if not localized_text:
        return ""

    indent = " " * indent_size

    result = ""
    for language_code, text in localized_text.items():
        result += f"{indent}{language_code}: {text}\n"

    return result


def str_as_localized_text(text: str, language_id: str) -> LocalizedText | None:
    language_code = LanguageLayer.get_language_code_by_id(language_id)
    if not language_code or not text:
        return None

    return {language_code: text}


def read_localized_field_backward_compatible(value: LocalizedText | str | None) -> LocalizedText | None:
    """Interprets given value as {"fin": value} if value is a string."""
    if isinstance(value, str):
        return {"fin": value}

    return value
