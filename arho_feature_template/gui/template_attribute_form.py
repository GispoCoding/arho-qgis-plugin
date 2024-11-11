from __future__ import annotations

from importlib import resources
from typing import TYPE_CHECKING

from qgis.gui import QgsSpinBox
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLineEdit,
    QScrollArea,
    QSizePolicy,
    QSpacerItem,
    QTreeWidget,
    QTreeWidgetItem,
)

from arho_feature_template.gui.plan_regulation_group_widget import PlanRegulationGroupWidget

if TYPE_CHECKING:
    from qgis.core import QgsFeature
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
        self.plan_regulation_group_scrollarea: QScrollArea
        self.plan_regulation_group_scrollarea_contents: QWidget
        self.plan_regulation_groups_tree: QTreeWidget
        self.button_box: QDialogButtonBox

        # SIGNALS
        self.button_box.accepted.connect(self._on_ok_clicked)
        self.plan_regulation_groups_tree.itemDoubleClicked.connect(self.add_selected_plan_regulation_group)

        # INIT
        self.attribute_widgets = {
            "name": self.feature_name,
            "description": self.feature_description,
            "type_of_underground_id": self.feature_underground,
        }
        # TODO: The 'configs' could be a mapping where keys are plan regulation group names and
        # values are the related configurations
        self.configs: dict[str, Feature] = {}
        self.scroll_area_spacer = None
        self.available_plan_regulation_group_configs: list[Feature] = []

        self.setWindowTitle(feature_template_config.name)
        self.init_feature_attributes_from_template(feature_template_config)
        self.init_plan_regulation_groups_from_template(feature_template_config)
        self.init_plan_regulation_group_library()

    def _add_spacer(self):
        self.scroll_area_spacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.plan_regulation_group_scrollarea_contents.layout().addItem(self.scroll_area_spacer)

    def _remove_spacer(self):
        if self.scroll_area_spacer is not None:
            self.plan_regulation_group_scrollarea_contents.layout().removeItem(self.scroll_area_spacer)
            self.scroll_area_spacer = None

    def add_selected_plan_regulation_group(self, item: QTreeWidgetItem, column: int):
        if not item.parent():
            return
        config = self.configs.get(item.text(column))
        if not config:
            print(f"Could not find plan regulation group configuration for {item.text(column)}")  # noqa: T201
            return
        self.add_plan_regulation_group(config)

    def add_plan_regulation_group(self, feature_config: Feature):
        new_plan_regulation_group = PlanRegulationGroupWidget(feature_config)
        new_plan_regulation_group.delete_signal.connect(self.remove_plan_regulation_group)
        self._remove_spacer()
        self.plan_regulation_group_scrollarea_contents.layout().addWidget(new_plan_regulation_group)
        self._add_spacer()

    def remove_plan_regulation_group(self, plan_regulation_group_widget: PlanRegulationGroupWidget):
        self.plan_regulation_group_scrollarea_contents.layout().removeWidget(plan_regulation_group_widget)
        plan_regulation_group_widget.deleteLater()

    def init_plan_regulation_group_library(self):
        # Now plan regulation group tree widget/view is just static placeholder for demo
        pass

    def init_feature_attributes_from_template(self, feature_template_config: FeatureTemplate):
        if feature_template_config.feature.attributes is None:
            return
        for _attribute in feature_template_config.feature.attributes:
            # TODO: TO be implemented
            pass

    def init_plan_regulation_groups_from_template(self, feature_template_config: FeatureTemplate):
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
                # TODO: Implement
                print(f"Encountered child feature with unrecognized layer: {child_feature.layer}")  # noqa: T201

    def _on_ok_clicked(self):
        self.accept()

    def set_feature_attributes(self, feature: QgsFeature):
        for attribute, widget in self.attribute_widgets.items():
            feature.setAttribute(attribute, self._get_widget_value(widget))

    def _get_widget_value(self, widget: QWidget) -> str | int | None:
        if isinstance(widget, QLineEdit):
            return widget.text()
        if isinstance(widget, QgsSpinBox):
            return widget.value()
        return None
        # TODO: Implement
