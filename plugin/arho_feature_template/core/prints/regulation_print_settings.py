from __future__ import annotations

from typing import TYPE_CHECKING, NamedTuple

if TYPE_CHECKING:
    from qgis.PyQt.QtGui import QFont


class RegulationPrintSettings(NamedTuple):
    include_regulation_headings: bool
    include_regulation_texts: bool
    symbol_width: float
    symbol_height: float
    heading_font: QFont
    text_font: QFont
    x_margins: float
    y_margins: float
    languages: list[str]  # list of language codes, e.g. "fin" or "swe". Should be 1 or 2
