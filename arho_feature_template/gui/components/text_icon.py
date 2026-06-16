from __future__ import annotations

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QColor, QFont, QPainter, QPixmap


def text_icon(text: str, color: QColor | None = None, size: int = 24, font_size: int = 20) -> QPixmap:
    color = color or QColor(0, 0, 0)
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    font = QFont()
    font.setPixelSize(font_size)
    painter.setFont(font)

    painter.setPen(color)
    painter.drawText(pixmap.rect(), Qt.AlignCenter, text)

    painter.end()

    return pixmap
