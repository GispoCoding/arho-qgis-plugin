from __future__ import annotations

from importlib import resources
from typing import TYPE_CHECKING

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog, QTreeWidget, QTreeWidgetItem

from arho_feature_template.gui.new_plan_regulation_widget import NewPlanRegulationWidget

if TYPE_CHECKING:
    from qgis.PyQt.QtWidgets import QBoxLayout, QWidget

ui_path = resources.files(__package__) / "new_plan_regulation_group_form.ui"
FormClass, _ = uic.loadUiType(ui_path)


class NewPlanRegulationGroupForm(QDialog, FormClass):  # type: ignore
    """Form to create a new plan regulation group."""

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # TYPES
        self.plan_regulations_view: QTreeWidget
        self.plan_regulations_scroll_area_contents: QWidget
        self.plan_regulations_layout: QBoxLayout

        # INIT
        self.initialize_plan_regulations()
        self.plan_regulations_view.itemDoubleClicked.connect(self.add_selected_plan_regulation)

    def initialize_plan_regulations(self):
        # NOTE: Replace the dummy plan regulation codes below with codes from DB
        plan_regulation_codes = {
            "category 1": ["regulation 1", "regulation 2"],
            "category 2": ["regulation 3"],
            "category 3": ["regulation 4", "regulation 5", "regulation 6"],
        }

        # Initialize categories
        for category_name, plan_regulations in plan_regulation_codes.items():
            category_item = QTreeWidgetItem()
            category_item.setText(0, category_name)
            self.plan_regulations_view.addTopLevelItem(category_item)

            # Initialize plan regulations under the categories
            for plan_regulation_type in plan_regulations:
                plan_regulation_item = QTreeWidgetItem(category_item)
                plan_regulation_item.setText(0, plan_regulation_type)
                self.plan_regulations_view.addTopLevelItem(plan_regulation_item)

    def add_selected_plan_regulation(self, item: QTreeWidgetItem, column: int):
        # If user double clicked category, don't add plan regulation
        if not item.parent():
            return
        self.add_plan_regulation(item.text(column))

    def add_plan_regulation(self, regulation_type: str):
        new_plan_regulation_widget = NewPlanRegulationWidget(
            regulation_type=regulation_type, parent=self.plan_regulations_scroll_area_contents
        )
        new_plan_regulation_widget.delete_signal.connect(self.delete_plan_regulation)
        index = self.plan_regulations_layout.count() - 1
        self.plan_regulations_layout.insertWidget(index, new_plan_regulation_widget)

    def delete_plan_regulation(self, plan_regulation_widget: NewPlanRegulationWidget):
        self.plan_regulations_layout.removeWidget(plan_regulation_widget)
        plan_regulation_widget.deleteLater()
