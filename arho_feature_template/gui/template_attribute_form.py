from __future__ import annotations

from importlib import resources
from typing import TYPE_CHECKING

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLineEdit,
    QMenu,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpacerItem,
)

from arho_feature_template.gui.plan_regulation_group_widget import PlanRegulationGroupWidget

if TYPE_CHECKING:
    from qgis.PyQt.QtWidgets import QWidget

    from arho_feature_template.core.template_library_config import FeatureTemplate

ui_path = resources.files(__package__) / "template_attribute_form.ui"
FormClass, _ = uic.loadUiType(ui_path)


class TemplateAttributeForm(QDialog, FormClass):  # type: ignore
    """Parent class for feature template forms for adding and modifying feature attribute data."""

    def __init__(self, feature_template_config: FeatureTemplate):
        super().__init__()
        self.setupUi(self)

        # TYPES
        self.feature_name: QLineEdit
        self.feature_description: QLineEdit
        self.feature_underground: QLineEdit
        self.feature_vertical_boundaries: QLineEdit
        self.plan_regulation_group_scrollarea: QScrollArea
        self.plan_regulation_group_scrollarea_contents: QWidget
        self.add_plan_regulation_group_btn: QPushButton
        self.button_box: QDialogButtonBox

        # SIGNALS
        self.button_box.accepted.connect(self._on_ok_clicked)

        # INIT
        self.setWindowTitle(feature_template_config.name)
        self.init_plan_regulation_groups(feature_template_config)
        self.scroll_area_spacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.plan_regulation_group_scrollarea_contents.layout().addItem(self.scroll_area_spacer)
        self.init_add_plan_regulation_group_btn()

    def init_add_plan_regulation_group_btn(self):
        menu = QMenu()
        self.new_mineral_system_action = menu.addAction("Kaavamääräysryhmä 1")
        self.new_mineral_system_action = menu.addAction("Kaavamääräysryhmä 2")
        self.new_mineral_system_action = menu.addAction("Kaavamääräysryhmä 3")
        self.new_mineral_system_action = menu.addAction("Kaavamääräysryhmä 4")
        self.new_mineral_system_action = menu.addAction("Kaavamääräysryhmä 5")
        self.new_mineral_system_action = menu.addAction("Kaavamääräysryhmä 6")
        self.new_mineral_system_action = menu.addAction("Kaavamääräysryhmä 7")
        self.new_mineral_system_action = menu.addAction("Kaavamääräysryhmä 8")
        self.new_mineral_system_action = menu.addAction("Kaavamääräysryhmä 9")

        self.add_plan_regulation_group_btn.setMenu(menu)

    def init_plan_regulation_groups(self, feature_template_config: FeatureTemplate):
        for child_feature in feature_template_config.feature.child_features:
            if child_feature.layer == "plan_requlation_group":
                plan_regulation_group_entry = PlanRegulationGroupWidget(child_feature)
                self.plan_regulation_group_scrollarea_contents.layout().addWidget(plan_regulation_group_entry)
            else:
                # TODO
                print(f"Encountered child feature with unrecognized layer: {child_feature.layer}")

    def _on_ok_clicked(self):
        self.accept()
