from __future__ import annotations

import logging
from collections import defaultdict
from typing import TYPE_CHECKING

from qgis.gui import QgsMapToolDigitizeFeature
from qgis.PyQt.QtCore import QItemSelectionModel
from qgis.PyQt.QtGui import QStandardItem, QStandardItemModel
from qgis.utils import iface

from arho_feature_template.core.plan_manager import save_plan_feature
from arho_feature_template.core.template_library_config import (
    FeatureTemplate,
    TemplateLibraryConfig,
    TemplateLibraryVersionError,
    TemplateSyntaxError,
    parse_template_library_config,
)
from arho_feature_template.exceptions import LayerNotFoundError, LayerNotVectorTypeError
from arho_feature_template.gui.dialogs.plan_feature_form import PlanFeatureForm
from arho_feature_template.gui.docks.template_dock import TemplateLibraryDock
from arho_feature_template.resources.template_libraries import library_config_files
from arho_feature_template.utils.project_utils import get_vector_layer_from_project

if TYPE_CHECKING:
    from qgis.core import QgsFeature, QgsVectorLayer

logger = logging.getLogger(__name__)


class TemplateItem(QStandardItem):
    def __init__(self, template_config: FeatureTemplate) -> None:
        self.config = template_config
        super().__init__(template_config.name)

    def is_valid(self) -> bool:
        """Check if the template is valid agains current QGIS project

        Checks if the layer and attributes defined in the template acutally exists"""
        try:
            get_vector_layer_from_project(self.config.feature.layer)  # TODO: check child features recursively
        except (LayerNotFoundError, LayerNotVectorTypeError):
            return False
        else:
            return True


class TemplateGeometryDigitizeMapTool(QgsMapToolDigitizeFeature): ...


class FeatureTemplater:
    def __init__(self) -> None:
        self.library_configs: dict[str, TemplateLibraryConfig] = {}

        self.template_dock = TemplateLibraryDock()
        self.template_dock.hide()

        self.template_model = QStandardItemModel()
        self.template_dock.template_list.setModel(self.template_model)

        # Set the selection mode to allow single selection
        self.template_dock.template_list.setSelectionMode(self.template_dock.template_list.SingleSelection)

        self._read_library_configs()

        self.template_dock.library_selection.addItems(self.get_library_names())

        # Update template tree when library selection changes
        self.template_dock.library_selection.currentIndexChanged.connect(
            lambda: self.set_active_library(self.template_dock.library_selection.currentText())
        )

        # Activate map tool when template is selected
        self.template_dock.template_list.clicked.connect(self.on_template_item_clicked)

        self.digitize_map_tool = TemplateGeometryDigitizeMapTool(iface.mapCanvas(), iface.cadDockWidget())
        self.digitize_map_tool.digitizingCompleted.connect(self.ask_for_feature_attributes)
        self.digitize_map_tool.deactivated.connect(self.on_digitizing_deactivated)

        # Digitize from empty feature
        self.template_dock.new_feature_grid.feature_type_clicked.connect(self.on_empty_feature_digitize_clicked)

    def on_template_item_clicked(self, index):
        item = self.template_model.itemFromIndex(index)

        # Do nothing if clicked item is a group
        if item.hasChildren():
            return

        try:
            layer = get_vector_layer_from_project(item.config.feature.layer)
        except (LayerNotFoundError, LayerNotVectorTypeError):
            logger.exception("Failed to activate template")
            return

        self.active_template = item
        self.template_dock.new_feature_grid.clear_selections()
        self.active_empty_feature_template = None
        self.start_digitizing_for_layer(layer)

        # Reselect as a workaround for first selection visual clarity
        self.template_dock.template_list.selectionModel().select(
            index, QItemSelectionModel.Select | QItemSelectionModel.Rows
        )

    def on_empty_feature_digitize_clicked(self, feature_name: str, layer_name: str):
        self.active_empty_feature_template = (feature_name, layer_name)
        self.template_dock.template_list.clearSelection()
        self.active_template = None
        self.start_digitizing_for_layer(get_vector_layer_from_project(layer_name))

    def on_digitizing_deactivated(self):
        # Clear selections
        self.template_dock.template_list.clearSelection()
        self.template_dock.new_feature_grid.clear_selections()

    def start_digitizing_for_layer(self, layer: QgsVectorLayer) -> None:
        self.digitize_map_tool.clean()
        self.digitize_map_tool.setLayer(layer)
        if not layer.isEditable():
            succeeded = layer.startEditing()
            if not succeeded:
                logger.warning("Failed to start editing layer %s", layer.name())
                return
        iface.mapCanvas().setMapTool(self.digitize_map_tool)

    def ask_for_feature_attributes(self, feature: QgsFeature) -> None:
        """Shows a dialog to ask for feature attributes and creates the feature"""

        if self.active_template:
            name = self.active_template.config.name
            target_layer_name = self.active_template.config.group
        elif self.active_empty_feature_template:
            name, target_layer_name = self.active_empty_feature_template
        else:
            return

        attribute_form = PlanFeatureForm(name, target_layer_name, feature.geometry())
        if attribute_form.exec_():
            save_plan_feature(attribute_form.model)

    def get_library_names(self) -> list[str]:
        return list(self.library_configs.keys())

    def set_active_library(self, library_name: str) -> None:
        self.template_model.clear()

        grouped_templates: defaultdict[str, defaultdict[str, list[FeatureTemplate]]] = defaultdict(
            lambda: defaultdict(list)
        )

        # Group templates by 'group' and 'sub_group'
        for template in self.library_configs[library_name].templates:
            group = getattr(template, "group", None) or "Ryhmittelemättömät"
            sub_group = getattr(template, "sub_group", None)
            if sub_group:
                grouped_templates[group][sub_group].append(template)
            else:
                grouped_templates[group][""].append(template)

        for group_name, sub_group_dict in grouped_templates.items():
            group_item = QStandardItem(group_name)
            group_item.setEditable(False)

            for sub_group_name, templates in sub_group_dict.items():
                if sub_group_name:
                    sub_group_item = QStandardItem(sub_group_name)
                    sub_group_item.setEditable(False)
                    group_item.appendRow(sub_group_item)
                    target_item = sub_group_item
                else:
                    # If template has no sub_group set, list it directly under group
                    target_item = group_item

                for template in templates:
                    template_item = TemplateItem(template)
                    template_item.setEditable(False)
                    target_item.appendRow(template_item)

            self.template_model.appendRow(group_item)

        self.template_dock.template_list.expandAll()

    def _read_library_configs(self) -> None:
        for config_file in library_config_files():
            try:
                config = parse_template_library_config(config_file)
                self.library_configs[config.meta.name] = config
            except (TemplateLibraryVersionError, TemplateSyntaxError) as e:
                logger.warning("Failed to parse template library configuration: %s", e)

        first_library_name = next(iter(self.library_configs), None)
        if first_library_name:
            self.set_active_library(first_library_name)
