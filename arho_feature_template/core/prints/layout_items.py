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
    QgsUnitTypes,
)
from qgis.PyQt.QtCore import QPointF, QSizeF, Qt
from qgis.PyQt.QtGui import QPolygonF

from arho_feature_template.core.prints.layout_utils import (
    move_label_above_symbol,
    move_label_below_item,
    move_label_next_to_item,
    move_label_on_symbol,
)
from arho_feature_template.utils.localization_utils import get_localized_text

if TYPE_CHECKING:
    from arho_feature_template.core.models import LocalizedText
    from arho_feature_template.core.prints.regulation_print_settings import RegulationPrintSettings
    from arho_feature_template.core.prints.regulations_print_generator import RegulationPrintElement


DEFAULT_APPROX_VISUAL_LINE_WIDTH = 2.3
"""There doesn't seem to be easy way to position the label just above the rendered
polyline because the width doesn't always correspond given line_width. 2mm seems to work
ok with current settings."""

DEFAULT_SPACE_BETWEEN_COLUMNS = 10

DEFAULT_LETTER_CODE_LABEL_HEIGHT = 4.4


class LayoutItemFactory:
    SETTINGS: RegulationPrintSettings

    @classmethod
    def new_regulation_print_item(
        cls,
        element: RegulationPrintElement,
        layout: QgsPrintLayout,
        coords: tuple[float, float],
    ) -> QgsLayoutItemGroup | QgsLayoutItem | None:
        items = []

        # --- 1. Create the symbol + letter code element ---
        symbol_element: QgsLayoutItem = cls.new_symbol_item(element.symbol, layout)

        # Create letter code label even if it is empty, this makes positioning markers easier
        letter_code_element = LayoutItemFactory.new_letter_code_label(element.letter_code, layout)
        symbol_and_code_grouped = LayoutItemFactory.group_and_align_label_and_symbol_items(
            letter_code_element, symbol_element, layout
        )

        symbol_and_code_grouped.attemptMove(QgsLayoutPoint(*coords))
        items.append(symbol_and_code_grouped)

        # --- 2. Create the heading element in first defined language---
        first_language = cls.SETTINGS.languages[0]

        heading_element = None
        if cls.SETTINGS.include_regulation_headings:
            heading_element = LayoutItemFactory.new_regulation_heading_label(layout, element.heading, 0)
            move_label_next_to_item(
                heading_element,
                letter_code_element,
            )
            items.append(heading_element)

        # --- 3. Create the regulation text items in first defined language ---
        if cls.SETTINGS.include_regulation_texts and len(element.regulation_texts) > 0:
            cls.add_regulation_texts(
                layout, element, first_language, heading_element, symbol_and_code_grouped, items, 0
            )

        # --- 4. Create the heading and regulation text items in secondary language if defined ---
        if cls.is_multilanguage_print():
            second_language = cls.SETTINGS.languages[1]

            # 4.a Second language heading element
            second_language_heading_element = None
            if cls.SETTINGS.include_regulation_headings:
                second_language_heading_element = LayoutItemFactory.new_regulation_heading_label(
                    layout, element.heading, 1
                )
                move_label_next_to_item(
                    second_language_heading_element,
                    symbol_and_code_grouped,
                )
                cls.move_to_second_column(second_language_heading_element)
                items.append(second_language_heading_element)

            # 4.b Second language text elements
            if cls.SETTINGS.include_regulation_texts and len(element.regulation_texts) > 0:
                cls.add_regulation_texts(
                    layout, element, second_language, second_language_heading_element, symbol_and_code_grouped, items, 1
                )

        # --- 5. Remove empty headings ---
        if heading_element and heading_element.text() == "":
            items.remove(heading_element)
            layout.removeItem(heading_element)

        if (
            cls.is_multilanguage_print()
            and second_language_heading_element
            and second_language_heading_element.text() == ""
        ):
            items.remove(second_language_heading_element)
            layout.removeItem(second_language_heading_element)

        # --- 6. Return and group the elements created ---
        # Return None if no layout items were created
        if len(items) == 0:
            return None

        # Return the only valid item
        if len(items) == 1:
            return items[0]

        # Group valid items and return them
        return layout.groupItems(items)

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
        line_length = cls.SETTINGS.symbol_width
        line_width = line_length / 2.0
        polyline = QPolygonF(
            [
                QPointF(0.0, line_width),
                QPointF(line_length, line_width),
            ]
        )
        line_item = QgsLayoutItemPolyline(polyline, layout)
        line_item.setSymbol(symbol)
        layout.addLayoutItem(line_item)

        return line_item

    @classmethod
    def new_polygon_item(cls, symbol: QgsSymbol, layout: QgsPrintLayout) -> QgsLayoutItemPolygon:
        polygon_width = cls.SETTINGS.symbol_width
        polygon_height = cls.SETTINGS.symbol_height

        polygon = QPolygonF(
            [
                QPointF(0.0, 0.0),
                QPointF(polygon_width, 0.0),
                QPointF(polygon_width, polygon_height),
                QPointF(0.0, polygon_height),
            ]
        )
        polygon_item = QgsLayoutItemPolygon(polygon, layout)
        polygon_item.setSymbol(symbol)
        layout.addLayoutItem(polygon_item)

        return polygon_item

    @classmethod
    def new_letter_code_label(cls, letter_code: str, layout: QgsPrintLayout) -> QgsLayoutItemLabel:
        label = QgsLayoutItemLabel(layout)
        label.setMode(QgsLayoutItemLabel.Mode.ModeFont)
        label.setText(letter_code)
        label.attemptResize(QgsLayoutSize(cls.SETTINGS.symbol_width, DEFAULT_LETTER_CODE_LABEL_HEIGHT))
        label.setHAlign(Qt.AlignHCenter)
        label.setVAlign(Qt.AlignVCenter)
        layout.addLayoutItem(label)

        return label

    @classmethod
    def new_regulation_heading_label(
        cls, layout: QgsPrintLayout, heading: LocalizedText, language_index: int = 0
    ) -> QgsLayoutItemLabel:
        label = QgsLayoutItemLabel(layout)
        label.setMode(QgsLayoutItemLabel.Mode.ModeFont)
        text = get_localized_text(heading, cls.SETTINGS.languages[language_index])
        label.setText(text if text else "")
        label.setFont(cls.SETTINGS.heading_font)
        label.setMarginX(2)
        # label.setMarginY(2)
        label.attemptResize(
            QgsLayoutSize(
                width=cls.get_text_box_width(language_index),
                height=cls.get_approx_required_height_for_label(label, language_index),
            )
        )
        layout.addLayoutItem(label)

        return label

    @classmethod
    def new_regulation_text_label(
        cls, layout: QgsPrintLayout, text: LocalizedText, language_index: int = 0
    ) -> QgsLayoutItemLabel:
        label = QgsLayoutItemLabel(layout)
        label.setMode(QgsLayoutItemLabel.Mode.ModeFont)
        label.setText(get_localized_text(text, cls.SETTINGS.languages[language_index]) or "")
        label.setFont(cls.SETTINGS.text_font)
        label.setMarginX(2)
        label.attemptResize(
            QgsLayoutSize(
                width=cls.get_text_box_width(language_index),
                height=cls.get_approx_required_height_for_label(label, language_index),
            )
        )
        layout.addLayoutItem(label)

        return label

    @classmethod
    def group_and_align_label_and_symbol_items(
        cls,
        label_item: QgsLayoutItemLabel,
        symbol_item: QgsLayoutItemMarker | QgsLayoutItemPolyline | QgsLayoutItemPolygon | None,
        layout: QgsPrintLayout,
    ) -> QgsLayoutItemGroup:
        if symbol_item is None:
            return label_item

        if isinstance(symbol_item, QgsLayoutItemMarker):
            # Position code above if it's long
            if len(label_item.text()) > 1:
                move_label_above_symbol(label_item, symbol_item, DEFAULT_APPROX_VISUAL_LINE_WIDTH)
            else:
                move_label_on_symbol(label_item, symbol_item)
        elif isinstance(symbol_item, QgsLayoutItemPolyline):
            move_label_above_symbol(label_item, symbol_item, DEFAULT_APPROX_VISUAL_LINE_WIDTH)
        elif isinstance(symbol_item, QgsLayoutItemPolygon):
            move_label_on_symbol(label_item, symbol_item)

        return layout.groupItems([symbol_item, label_item])

    @classmethod
    def add_regulation_texts(
        cls,
        layout: QgsPrintLayout,
        element: RegulationPrintElement,
        language: str,
        heading_element: QgsLayoutItemLabel | None,
        symbol_and_code_grouped: QgsLayoutItemGroup,
        items: list,
        language_index: int = 0,
    ):
        previous_element = heading_element
        num_text_elements = 0
        for text in element.regulation_texts:
            localized_text = get_localized_text(text, language)
            if localized_text is None or localized_text == "":
                continue

            verbal_regulation_label = LayoutItemFactory.new_regulation_text_label(layout, text)
            # Include 4.4 mm extra space if multiple verbal regulations exist
            if previous_element:
                move_label_below_item(verbal_regulation_label, previous_element, 4.4 if num_text_elements > 0 else 0)
            elif symbol_and_code_grouped:
                move_label_next_to_item(
                    verbal_regulation_label,
                    symbol_and_code_grouped,
                )
                if language_index > 0:
                    cls.move_to_second_column(verbal_regulation_label)

            items.append(verbal_regulation_label)
            previous_element = verbal_regulation_label
            num_text_elements += 1

    @classmethod
    def move_to_second_column(cls, item: QgsLayoutItem):
        item.attemptMove(
            QgsLayoutPoint(
                cls.get_column_horizontal_space() + cls.SETTINGS.x_margins + DEFAULT_SPACE_BETWEEN_COLUMNS,
                item.y(),
                QgsUnitTypes.LayoutMillimeters,
            )
        )

    @classmethod
    def get_column_horizontal_space(cls) -> float:
        if len(cls.SETTINGS.languages) == 1:
            return 210 - 2 * cls.SETTINGS.x_margins
        return (210 - 2 * cls.SETTINGS.x_margins - DEFAULT_SPACE_BETWEEN_COLUMNS) / 2

    @classmethod
    def get_text_box_width(cls, language_index: int) -> float:
        # In first column text shares the column space with symbol
        # In second column, text has more space since symbols aren't duplicated
        if language_index == 0:
            return cls.get_column_horizontal_space() - cls.SETTINGS.symbol_width
        return cls.get_column_horizontal_space()

    @classmethod
    def get_approx_required_height_for_label(cls, label: QgsLayoutItemLabel, language_index: int = 0) -> float:
        required_size: QSizeF = label.sizeForText()
        required_rows = math.ceil(required_size.width() / cls.get_text_box_width(language_index))
        return required_rows * required_size.height() * 1.05

    @classmethod
    def is_multilanguage_print(cls) -> bool:
        return cls.SETTINGS and len(cls.SETTINGS.languages) > 1
