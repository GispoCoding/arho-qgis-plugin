from __future__ import annotations

from qgis.PyQt.QtCore import QDate, pyqtSignal
from qgis.PyQt.QtWidgets import QPushButton, QWidget

from arho_feature_template.core.lifecycles import LifeCycleStatusValue
from arho_feature_template.gui.components.edit_lifecycle_menu import EditLifecycleMenu


class PushButtonEditLifecycle(QPushButton):
    lifecycle_change_requested = pyqtSignal(LifeCycleStatusValue, object)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

    def populate_menu(self):
        lifecycle_tools_menu = EditLifecycleMenu()
        lifecycle_tools_menu.lifecycle_change_requested.connect(self.on_lifecycle_change_requested)
        self.setMenu(lifecycle_tools_menu)

    def on_lifecycle_change_requested(self, lifecycle_value: LifeCycleStatusValue, date: QDate | None):
        self.lifecycle_change_requested.emit(lifecycle_value, date)
