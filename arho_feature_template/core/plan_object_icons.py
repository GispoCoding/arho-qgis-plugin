from __future__ import annotations

from PyQt5.QtGui import QColor, QFont, QFontMetrics, QPainter, QPixmap
from qgis.core import (
    QgsExpressionContext,
    QgsExpressionContextUtils,
    QgsFeature,
    QgsRenderContext,
    QgsSymbol,
    QgsSymbolLayerUtils,
    QgsVectorLayer,
    QgsWkbTypes,
)
from qgis.PyQt.QtCore import QSize, Qt

from arho_feature_template.exceptions import NotPlanObjectLayerError
from arho_feature_template.project.layers.plan_layers import PlanObjectLayer, plan_feature_layers
from arho_feature_template.utils.misc_utils import iface


class PlanObjectIconRenderer:
    BASE_FONT_SIZE: int = 16
    BASE_ICON_SIZE: int = 40

    # TODO: Cache icons for each PlanObjectLayer? Need to be careful when cache invalidates and/or
    # icons need to be added, modified or removed.

    @classmethod
    def render_icons_for_layer(
        cls, layer: PlanObjectLayer, symbol_width: int = 40, symbol_height: int = 40
    ) -> dict[str, QPixmap]:
        if layer not in plan_feature_layers:
            raise NotPlanObjectLayerError(layer.name)

        icons: dict[str, QPixmap] = {}
        failed_count = 0

        vlayer = layer.get_from_project()
        for feat, symbol in cls.get_symbols_for_layer_features(vlayer):
            if symbol is None:
                failed_count += 1
                continue

            icons[feat["id"]] = cls.render_pixmap(
                symbol=symbol,
                letter_code=PlanObjectLayer.feature_letter_codes_as_text(feat),
                geometry_type=vlayer.geometryType(),
                symbol_width=symbol_width,
                symbol_height=symbol_height,
            )

        if failed_count > 0:
            iface.messageBar().pushCritical(
                "", f"Kuvakkeen luominen epäonnistui {failed_count!s} kaavakohteelle tasolle {layer.name}"
            )

        return icons

    @staticmethod
    def get_symbols_for_layer_features(layer: QgsVectorLayer, feats: list[QgsFeature] | None = None):
        renderer = layer.renderer()

        expression_context = QgsExpressionContext()
        expression_context.appendScopes(QgsExpressionContextUtils.globalProjectLayerScopes(layer))

        render_context = QgsRenderContext()
        render_context.setExpressionContext(expression_context)

        renderer.startRender(render_context, layer.fields())
        try:
            if not feats:
                feats = layer.getFeatures()
            for feat in feats:  # type: ignore
                expression_context.setFeature(feat)
                render_context.setExpressionContext(expression_context)
                symbols = renderer.symbolsForFeature(feat, render_context)
                yield feat, (symbols[0] if symbols else None)
        finally:
            renderer.stopRender(render_context)

    @classmethod
    def render_pixmap(
        cls,
        symbol: QgsSymbol,
        letter_code: str,
        geometry_type: QgsWkbTypes.GeometryType,
        symbol_width: int = 40,  # 35px might be the smallest meaningful symbol size
        symbol_height: int = 40,
        padding: int = 3,
        # scale_font_size: bool = True
    ) -> QPixmap:
        # TODO: What if letter code is long and/or multiple letter codes are drawn on one symbol?
        # Might need to adjust pixmap or font size

        # --- 1. Render symbol pixmap ---
        symbol_pixmap = cls._render_symbol(symbol, symbol_width, symbol_height)

        # --- 2. Setup letter code text ---
        # Setup font
        font = QFont()
        font.setPixelSize(cls.BASE_FONT_SIZE)

        # Create bounding rect with padding for letter code text
        letter_code_rect = QFontMetrics(font).boundingRect(letter_code)
        letter_code_rect = letter_code_rect.adjusted(-padding, -padding, padding, padding)

        # --- 3. Setup final pixmap dimensions ---
        if cls._place_text_inside(letter_code, geometry_type):
            pixmap_width = symbol_width
            pixmap_height = symbol_height
            pixmap = QPixmap(pixmap_width, pixmap_height)

            pixmap_y = 0

            letter_code_rect.moveCenter(pixmap.rect().center())
        else:
            letter_code_height = letter_code_rect.height()
            pixmap_width = symbol_width
            pixmap_height = symbol_height + letter_code_height
            pixmap = QPixmap(pixmap_width, pixmap_height)

            pixmap_y = letter_code_height

            letter_code_rect.moveCenter(pixmap.rect().center())
            letter_code_rect.setY(0)

        # --- 4. Render final pixmap ---
        pixmap.fill(QColor(255, 255, 255, 0))  # Transparent background

        painter = QPainter(pixmap)
        painter.setFont(font)
        painter.drawPixmap(0, pixmap_y, symbol_pixmap)
        painter.drawText(letter_code_rect, Qt.AlignCenter, letter_code)
        painter.end()

        return pixmap

    @staticmethod
    def _render_symbol(symbol: QgsSymbol, width: int, height: int) -> QPixmap:
        # NOTE: It seems point symbols don't scale with the size
        return QgsSymbolLayerUtils.symbolPreviewPixmap(symbol=symbol, size=QSize(width, height))

    @staticmethod
    def _place_text_inside(letter_code: str, geometry_type: QgsWkbTypes.GeometryType) -> bool:
        is_polygon = geometry_type == QgsWkbTypes.PolygonGeometry
        is_point_with_short_text = geometry_type == QgsWkbTypes.PointGeometry and len(letter_code) == 1
        return is_polygon or is_point_with_short_text

    @classmethod
    def _scale_font_size(cls, font: QFont, pixmap: QPixmap) -> None:
        """Draft version, not in use right now."""
        min_dimension = min(pixmap.width(), pixmap.height())
        scale = min_dimension / cls.BASE_ICON_SIZE
        font.setPixelSize(int(cls.BASE_FONT_SIZE * scale))
