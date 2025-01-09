from __future__ import annotations

from qgis.PyQt.QtCore import QSize, Qt, pyqtSignal
from qgis.PyQt.QtGui import QPalette
from qgis.PyQt.QtWidgets import QListWidget, QListWidgetItem, QPushButton

FEATURE_TYPES = ["Aluevaraus", "Osa-alue", "Viiva", "Maankäytön\nkohde", "Muu piste"]
FEATURE_TYPE_TO_LAYER_NAME = {
    "Viiva": "Viivat",
    "Osa-alue": "Osa-alue",
    "Aluevaraus": "Aluevaraus",
    "Maankäytön\nkohde": "Maankäytön kohteet",
    "Muu piste": "Muut pisteet",
}

FEATURE_BUTTON_WIDTH = 90
FEATURE_BUTTON_HEIGHT = 90


class NewFeatureGridWidget(QListWidget):
    feature_type_clicked = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        self.viewport().setBackgroundRole(QPalette.Window)
        self.setFlow(self.LeftToRight)
        self.setWrapping(True)
        self.setMovement(self.Static)
        self.setResizeMode(self.Adjust)
        self.setGridSize(QSize(FEATURE_BUTTON_WIDTH + 4, FEATURE_BUTTON_HEIGHT + 4))
        self.setHorizontalScrollMode(self.ScrollPerPixel)
        self.setVerticalScrollMode(self.ScrollPerPixel)

        self.buttons = {feature_type: FeatureButton(feature_type) for feature_type in FEATURE_TYPES}
        for btn in self.buttons.values():
            self.add_button(btn)
            btn.clicked.connect(lambda _, name=btn.text(): self.handle_button_click(name))  # noqa: B008

    def add_button(self, button: QPushButton):
        item = QListWidgetItem()
        item.setFlags(item.flags() & ~(Qt.ItemIsSelectable | Qt.ItemIsEnabled))
        self.addItem(item)
        item.setSizeHint(button.sizeHint())
        self.setItemWidget(item, button)

    def resizeEvent(self, event):  # noqa: N802
        super().resizeEvent(event)
        self.update_height()

    def update_height(self):
        """Adjust the height of the list widget dynamically based on the number of rows."""
        available_width = self.viewport().width()
        items_per_row = max(1, available_width // (FEATURE_BUTTON_WIDTH + 4 + 2))
        rows_needed = (self.count() + items_per_row - 1) // items_per_row
        new_height = rows_needed * (FEATURE_BUTTON_HEIGHT + 4 + 2)
        self.setFixedHeight(new_height)

    def handle_button_click(self, text: str):
        # Clear other button selections
        self.clear_selections(text)

        # Map button texts to layer names
        self.feature_type_clicked.emit(text, FEATURE_TYPE_TO_LAYER_NAME[text])

    def clear_selections(self, exclude: str | None = None):
        for txt, btn in self.buttons.items():
            if exclude and txt == exclude:
                continue
            btn.setChecked(False)


class FeatureButton(QPushButton):
    def __init__(self, text: str):
        super().__init__()
        self.setText(text)
        self.setFixedSize(FEATURE_BUTTON_WIDTH, FEATURE_BUTTON_HEIGHT)
        self.setCheckable(True)
