from __future__ import annotations

import math
from typing import TYPE_CHECKING

from qgis.core import (
    QgsFillSymbol,
    QgsLayoutItem,
    QgsLayoutItemGroup,
    QgsLayoutItemLabel,
    QgsLayoutItemMarker,
    QgsLayoutItemPolygon,
    QgsLayoutItemPolyline,
    QgsLayoutPoint,
    QgsLayoutSize,
    QgsLineSymbol,
    QgsMarkerSymbol,
    QgsPrintLayout,
    QgsSymbol,
)
from qgis.PyQt.QtCore import QPointF, QSizeF, Qt
from qgis.PyQt.QtGui import QPolygonF

from arho_feature_template.core.prints.layout_utils import (
    move_label_above_symbol,
    move_label_below_item,
    move_label_next_to_item,
    move_label_on_symbol,
)

if TYPE_CHECKING:
    from arho_feature_template.core.prints.regulations_print_generator import RegulationPrintElement


# NOTE: The constants below can be refactored into settings, Määräysosan asetukset

APPROX_VISUAL_LINE_WIDTH = 2.3
"""There doesn't seem to be easy way to position the label just above the rendered
polyline because the width doesn't always correspond given line_width. 2mm seems to work
ok with current settings."""

SYMBOL_ITEM_OCCUPIED_WIDTH = 10.0
"""The width that a marker/line/polygon symbol + letter code should occupy in the layout. """

POLYGON_WIDTH = 10.0
"""The width of new polygon item / `QgsLayoutItemPolygon`."""

POLYGON_HEIGHT = 10.0
"""The height of new polygon item / `QgsLayoutItemPolygon`."""

LINE_LENGTH = 10.0
"""The length of new line item / `QgsLayoutItemPolyline`."""

REGULATION_TEXT_BOX_WIDTH = 75.0
"""The width of regulation text area. Applies to both heading and verbal regulation text content labels."""

USE_PLACEHOLDER_REGULATION_TEXT = True
"""Whether to use placeholder text for verbal regulation(s) when none are found."""

PLACEHOLDER_TEXT = (
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do"
    "eiusmod tempor incididunt ut labore et dolore magna aliqua."
)


class LayoutItemFactory:
    @classmethod
    def new_regulation_print_item(
        cls, element: RegulationPrintElement, layout: QgsPrintLayout, coords: tuple[float, float]
    ) -> QgsLayoutItemGroup:
        # --- 1. Create the icon / symbol element ---
        icon_element: QgsLayoutItem = cls.new_symbol_item(element.symbol, layout)

        # Create letter code label even if it is empty, this makes positioning markers easier
        label_item = LayoutItemFactory.new_letter_code_label(element.letter_code, layout)
        icon_element = LayoutItemFactory.group_and_align_label_and_symbol_items(label_item, icon_element, layout)

        # Position the symbol
        icon_element.attemptMove(QgsLayoutPoint(*coords))

        # --- 2. Create the text element ---
        heading_element = LayoutItemFactory.new_regulation_heading_label(layout, element.heading)
        move_label_next_to_item(heading_element, icon_element, APPROX_VISUAL_LINE_WIDTH, SYMBOL_ITEM_OCCUPIED_WIDTH)

        # Verbal regulation contents
        previous_element = heading_element
        text_elements = []
        if len(element.regulation_texts) > 0:
            for i, text in enumerate(element.regulation_texts):
                verbal_regulation_label = LayoutItemFactory.new_regulation_text_label(layout, text)
                # Include 4.4 mm extra space if multiple verbal regulation exist
                move_label_below_item(verbal_regulation_label, previous_element, 4.4 if i > 0 else 0)
                text_elements.append(verbal_regulation_label)
                previous_element = verbal_regulation_label
            text_element = layout.groupItems([heading_element, *text_elements])
        else:
            text_element = heading_element

        # --- 3. Combine them ---
        return layout.groupItems([icon_element, text_element])

    @classmethod
    def new_symbol_item(
        cls, symbol: QgsSymbol, layout: QgsPrintLayout
    ) -> QgsLayoutItemMarker | QgsLayoutItemPolyline | QgsLayoutItemPolygon | None:
        if isinstance(symbol, QgsMarkerSymbol):
            return cls.new_point_item(symbol, layout)
        if isinstance(symbol, QgsLineSymbol):
            return cls.new_line_item(symbol, layout)
        if isinstance(symbol, QgsFillSymbol):
            return cls.new_polygon_item(symbol, layout)

        return None

    @classmethod
    def new_point_item(cls, symbol: QgsSymbol, layout: QgsPrintLayout) -> QgsLayoutItemMarker:
        point_item = QgsLayoutItemMarker(layout)
        point_item.setSymbol(symbol)
        layout.addLayoutItem(point_item)

        return point_item

    @classmethod
    def new_line_item(cls, symbol: QgsSymbol, layout: QgsPrintLayout) -> QgsLayoutItemPolyline:
        line_width = LINE_LENGTH / 2.0
        polyline = QPolygonF(
            [
                QPointF(0.0, line_width),
                QPointF(LINE_LENGTH, line_width),
            ]
        )
        line_item = QgsLayoutItemPolyline(polyline, layout)
        line_item.setSymbol(symbol)
        layout.addLayoutItem(line_item)

        return line_item

    @classmethod
    def new_polygon_item(cls, symbol: QgsSymbol, layout: QgsPrintLayout) -> QgsLayoutItemPolygon:
        polygon = QPolygonF(
            [
                QPointF(0.0, 0.0),
                QPointF(POLYGON_WIDTH, 0.0),
                QPointF(POLYGON_WIDTH, POLYGON_HEIGHT),
                QPointF(0.0, POLYGON_HEIGHT),
            ]
        )
        polygon_item = QgsLayoutItemPolygon(polygon, layout)
        polygon_item.setSymbol(symbol)
        layout.addLayoutItem(polygon_item)

        return polygon_item

    @classmethod
    def new_letter_code_label(cls, letter_code: str, layout: QgsPrintLayout) -> QgsLayoutItemLabel:
        label = QgsLayoutItemLabel(layout)
        label.setMode(QgsLayoutItemLabel.Mode.ModeHtml)
        label.setText(letter_code)
        # Set code label width to `SYMBOL_ITEM_OCCUPIED_WIDTH`, this is the easiest way to ensure
        # uniform space is used for all kind of symbol layout items
        label.attemptResize(QgsLayoutSize(SYMBOL_ITEM_OCCUPIED_WIDTH, 4.4))
        label.setHAlign(Qt.AlignHCenter)
        label.setVAlign(Qt.AlignVCenter)
        layout.addLayoutItem(label)

        return label

    @classmethod
    def new_regulation_heading_label(cls, layout: QgsPrintLayout, heading: str) -> QgsLayoutItemLabel:
        label = QgsLayoutItemLabel(layout)
        label.setMode(QgsLayoutItemLabel.Mode.ModeHtml)
        label.setText(f"<b>{heading}</b>")
        label.setMarginX(2)
        # label.setMarginY(2)
        label.attemptResize(QgsLayoutSize(REGULATION_TEXT_BOX_WIDTH, 6.4))
        label.adjustSizeToText()
        layout.addLayoutItem(label)

        return label

    @classmethod
    def new_regulation_text_label(cls, layout: QgsPrintLayout, text: str) -> QgsLayoutItemLabel:
        label = QgsLayoutItemLabel(layout)
        label.setMode(QgsLayoutItemLabel.Mode.ModeHtml)
        # html = f"<b>{title}</b><br/>{text}"
        label.setText(text)
        label.setMarginX(2)
        label.attemptResize(
            QgsLayoutSize(width=REGULATION_TEXT_BOX_WIDTH, height=cls._get_approx_required_height_for_label(label))
        )
        layout.addLayoutItem(label)

        return label

    @classmethod
    def group_and_align_label_and_symbol_items(
        cls,
        label_item: QgsLayoutItemLabel,
        symbol_item: QgsLayoutItemMarker | QgsLayoutItemPolyline | QgsLayoutItemPolygon,
        layout: QgsPrintLayout,
    ) -> QgsLayoutItemGroup:
        if isinstance(symbol_item, QgsLayoutItemMarker):
            # Position code above if it's long
            if len(label_item.text()) > 1:
                move_label_above_symbol(label_item, symbol_item, APPROX_VISUAL_LINE_WIDTH)
            else:
                move_label_on_symbol(label_item, symbol_item)
        elif isinstance(symbol_item, QgsLayoutItemPolyline):
            move_label_above_symbol(label_item, symbol_item, APPROX_VISUAL_LINE_WIDTH)
        elif isinstance(symbol_item, QgsLayoutItemPolygon):
            move_label_on_symbol(label_item, symbol_item)

        return layout.groupItems([symbol_item, label_item])

    @classmethod
    def _get_approx_required_height_for_label(cls, label: QgsLayoutItemLabel) -> float:
        required_size: QSizeF = label.sizeForText()
        # Mulitply by 1.1, a random number that should approximately account for whitespace
        # at row ends that`sizeForText` does not consider properly for us
        required_rows = math.ceil(1.1 * required_size.width() / REGULATION_TEXT_BOX_WIDTH)
        return required_rows * required_size.height()
