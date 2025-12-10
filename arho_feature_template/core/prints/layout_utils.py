from __future__ import annotations

from qgis.core import (
    QgsLayoutItem,
    QgsLayoutItemLabel,
    QgsLayoutItemMarker,
    QgsLayoutItemPolygon,
    QgsLayoutItemPolyline,
    QgsLayoutPoint,
    QgsUnitTypes,
)

from arho_feature_template.utils.misc_utils import iface


def move_label_on_symbol(
    label_item: QgsLayoutItemLabel, symbol_item: QgsLayoutItemMarker | QgsLayoutItemPolyline
) -> None:
    symbol_size = symbol_item.sizeWithUnits()
    label_size = label_item.sizeWithUnits()

    label_item.attemptMove(
        QgsLayoutPoint(
            symbol_item.x() + symbol_size.width() / 2 - label_size.width() / 2,
            symbol_item.y() + symbol_size.height() / 2 - label_size.height() / 2,
            QgsUnitTypes.LayoutMillimeters,
        )
    )


def move_label_above_symbol(
    label_item: QgsLayoutItemLabel,
    symbol_item: QgsLayoutItemMarker | QgsLayoutItemPolyline | QgsLayoutItemPolygon,
    line_symbol_width: float,
) -> None:
    symbol_size = symbol_item.sizeWithUnits()
    label_size = label_item.sizeWithUnits()

    if isinstance(symbol_item, QgsLayoutItemMarker):
        label_item.attemptMove(
            QgsLayoutPoint(
                symbol_item.x() + symbol_size.width() / 2 - label_size.width() / 2,
                symbol_item.y() - label_size.height(),
                QgsUnitTypes.LayoutMillimeters,
            )
        )
    elif isinstance(symbol_item, QgsLayoutItemPolyline):
        label_item.attemptMove(
            QgsLayoutPoint(
                symbol_item.x() + symbol_size.width() / 2 - label_size.width() / 2,
                symbol_item.y() - label_size.height() - line_symbol_width,
                QgsUnitTypes.LayoutMillimeters,
            )
        )
    else:
        iface.messageBar().pushCritical(
            "", f"Centre label above symbol not defined for layout item type {type(symbol_item)}"
        )


def move_label_next_to_item(
    label_item: QgsLayoutItemLabel, item: QgsLayoutItem, line_symbol_width: float, x_move: float | None = None
) -> None:
    extra_y_move = -line_symbol_width / 2 if isinstance(item, QgsLayoutItemPolyline) else 0.0
    label_item.attemptMove(
        QgsLayoutPoint(
            # Use item width if x move not defined
            item.x() + x_move if x_move is not None else item.sizeWithUnits().width(),
            item.y() + extra_y_move,
            QgsUnitTypes.LayoutMillimeters,
        )
    )


def move_label_below_item(label_item: QgsLayoutItemLabel, item: QgsLayoutItem) -> None:
    label_item.attemptMove(
        QgsLayoutPoint(item.x(), item.y() + item.sizeWithUnits().height(), QgsUnitTypes.LayoutMillimeters)
    )
