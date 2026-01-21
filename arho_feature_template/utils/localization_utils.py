from __future__ import annotations

from typing import TYPE_CHECKING, Any

from arho_feature_template.core.settings_manager import SettingsManager

if TYPE_CHECKING:
    from arho_feature_template.core.models import LocalizedText


def _primary_language_code() -> str:
    return SettingsManager.get_primary_language()


def serialize_localized_text(
    text: str | None, language_code: str | None = None, localized_text_instance: LocalizedText | None = None
) -> LocalizedText | None:
    """Serializes input text into LocalizedText (dict) format.

    If `language_code` parameter is not defined, primary language from settings is used.

    If `localized_text_instance` is defined, a merged instance is created and returned (given instance is not
    modified). If given language existed already in input instance, new value will override the old."""
    if not isinstance(text, str):
        return None

    localized_text: LocalizedText = {language_code if language_code else _primary_language_code(): text.strip()}
    return (localized_text_instance | localized_text) if localized_text_instance else localized_text


def deserialize_localized_text(
    localized_text: LocalizedText | None | Any, language_code: str | None = None
) -> str | None:
    """Deserializes input LocalizedText (dict) and returns text for one language.

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


def read_localized_field_backward_compatible(value: LocalizedText | str | None) -> LocalizedText | None:
    """Interprets given value as {"fin": value} if value is a string."""
    if isinstance(value, str):
        return {"fin": value}

    return value
