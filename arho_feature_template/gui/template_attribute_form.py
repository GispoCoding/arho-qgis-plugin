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

    from arho_feature_template.core.template_library_config import Feature, FeatureTemplate

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
        self.scroll_area_spacer = None
        self.available_plan_regulation_group_configs: list[Feature] = []

        self.setWindowTitle(feature_template_config.name)
        self.init_plan_regulation_groups(feature_template_config)
        self.init_add_plan_regulation_group_btn()

    def add_spacer(self):
        self.scroll_area_spacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.plan_regulation_group_scrollarea_contents.layout().addItem(self.scroll_area_spacer)

    def remove_spacer(self):
        if self.scroll_area_spacer is not None:
            self.plan_regulation_group_scrollarea_contents.layout().removeItem(self.scroll_area_spacer)
            self.scroll_area_spacer = None

    def add_plan_regulation_group(self, feature_config: Feature):
        new_plan_regulation_group = PlanRegulationGroupWidget(feature_config)
        new_plan_regulation_group.delete_signal.connect(self.remove_plan_regulation_group)
        self.remove_spacer()
        self.plan_regulation_group_scrollarea_contents.layout().addWidget(new_plan_regulation_group)
        self.add_spacer()

    def remove_plan_regulation_group(self, plan_regulation_group_widget: PlanRegulationGroupWidget):
        self.plan_regulation_group_scrollarea_contents.layout().removeWidget(plan_regulation_group_widget)
        plan_regulation_group_widget.deleteLater()

    def init_add_plan_regulation_group_btn(self):
        menu = QMenu()
        for config in self.available_plan_regulation_group_configs:
            plan_regulation_group_name = ""
            for attribute in config.attributes:
                if attribute.attribute == "name":
                    plan_regulation_group_name = attribute.display()

            action = menu.addAction(plan_regulation_group_name)
            action.triggered.connect(lambda _, config=config: self.add_plan_regulation_group(config))

        self.add_plan_regulation_group_btn.setMenu(menu)

    def init_plan_regulation_groups(self, feature_template_config: FeatureTemplate):
        if feature_template_config.feature.child_features is None:
            return
        for child_feature in feature_template_config.feature.child_features:
            if child_feature.layer == "plan_requlation_group":
                # Collect encountered plan regulation groups in init
                # This does not need to be done if Katja config file is read beforehand and
                # that handles available plan regulation groups
                self.available_plan_regulation_group_configs.append(child_feature)
                self.add_plan_regulation_group(child_feature)
            else:
                # TODO
                print(f"Encountered child feature with unrecognized layer: {child_feature.layer}")

    def _on_ok_clicked(self):
        self.accept()
