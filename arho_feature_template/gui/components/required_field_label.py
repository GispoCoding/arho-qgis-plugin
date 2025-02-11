from __future__ import annotations

from qgis.PyQt.QtWidgets import QLabel, QWidget


class RequiredFieldLabel(QLabel):
    """QLabel that prefixes the text with a red asterisk."""

    def __init__(self, text: str, parent: QWidget | None = None):
        super().__init__(self._prefix(text), parent)

    def setText(self, text: str):  # noqa: N802
        return super().setText(self._prefix(text))

    @staticmethod
    def _prefix(text: str) -> str:
        return f'<span style="color: red;">* </span>{text}'
