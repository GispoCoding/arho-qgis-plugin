from __future__ import annotations

from qgis.PyQt.QtCore import QDate, pyqtSignal
from qgis.PyQt.QtWidgets import QPushButton, QWidget

from arho_feature_template.core.lifecycles import LifeCycleStatusValue
from arho_feature_template.gui.components.edit_lifecycle_menu import EditLifecycleMenu
from arho_feature_template.utils.widget_utils import remove_widget


class PushButtonEditLifecycle(QPushButton):
    lifecycle_change_requested = pyqtSignal(LifeCycleStatusValue, object)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

    def populate_menu(self):
        """Rebuilds the lifecycle menu. Runs again on every project read.

        The menu is parented so its lifetime is a decision rather than a side effect of
        the `/KeepReference/` that `setMenu` carries in the bindings. That reference used
        to be what collected the previous menu, so the previous one is now deleted here.
        """
        previous_menu = self.menu()
        lifecycle_tools_menu = EditLifecycleMenu(self)
        lifecycle_tools_menu.lifecycle_change_requested.connect(self.on_lifecycle_change_requested)
        self.setMenu(lifecycle_tools_menu)
        if previous_menu is not None:
            remove_widget(previous_menu)

    def on_lifecycle_change_requested(self, lifecycle_value: LifeCycleStatusValue, date: QDate | None):
        self.lifecycle_change_requested.emit(lifecycle_value, date)
