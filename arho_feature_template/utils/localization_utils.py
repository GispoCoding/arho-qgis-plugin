from __future__ import annotations

from typing import TYPE_CHECKING

from arho_feature_template.core.settings_manager import SettingsManager

if TYPE_CHECKING:
    from arho_feature_template.core.models import LocalizedText


LANGUAGES = {
    "fin": "suomi",
    "swe": "ruotsi",
    "eng": "englanti",
    "sme": "pohjoissaame",
    "smn": "inarinsaame",
    "sms": "koltansaame",
}


def get_localized_text(localized_text: LocalizedText | None, language_code: str | None = None) -> str | None:
    """Returns text for one language from input LocalizedText (dict).

    If the `language_code` is not defined the first language found in order of importance is used.
    """
    if localized_text is None:
        return None

    if language_code:
        return localized_text.get(language_code)

    for language in SettingsManager.get_languages() + list(LANGUAGES.keys()):
        text = localized_text.get(language)
        if text:
            return text

    return None


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
