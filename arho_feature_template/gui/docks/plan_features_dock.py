from __future__ import annotations

from contextlib import suppress
from importlib import resources
from typing import TYPE_CHECKING, Iterable, cast

from qgis.core import Qgis, QgsApplication, QgsFeature, QgsProject, QgsVectorLayer
from qgis.gui import QgsDockWidget, QgsFilterLineEdit
from qgis.PyQt import uic
from qgis.PyQt.QtCore import (
    QItemSelection,
    QItemSelectionModel,
    QModelIndex,
    QPoint,
    QRegularExpression,
    QSortFilterProxyModel,
    Qt,
)
from qgis.PyQt.QtGui import QStandardItem, QStandardItemModel
from qgis.PyQt.QtWidgets import QMenu, QPushButton, QTableView

from arho_feature_template.core.feature_editing import save_plan_feature
from arho_feature_template.core.template_manager import TemplateManager
from arho_feature_template.exceptions import LayerNotFoundError
from arho_feature_template.gui.dialogs.plan_feature_form import PlanObjectForm
from arho_feature_template.project.layers.plan_layers import (
    LandUseAreaLayer,
    LineLayer,
    OtherAreaLayer,
    PointLayer,
    get_plan_feature_layer_class_by_layer_name,
    get_plan_feature_layer_class_by_model,
    plan_feature_layers,
)
from arho_feature_template.utils.misc_utils import iface
from arho_feature_template.utils.project_utils import get_vector_layer_from_project

ui_path = resources.files(__package__) / "plan_features_dock.ui"
FormClass, _ = uic.loadUiType(ui_path)

if TYPE_CHECKING:
    from arho_feature_template.core.models import PlanFeatureLibrary, PlanObject
    from arho_feature_template.core.plan_manager import PlanManager

DATA_COLUMN = 0
PLAN_OBJECT_TYPE_COLUMN = 1
DATA_ROLE = Qt.UserRole
LAYER_NAME_TO_FEATURE_TYPE = {
    LineLayer.name: "Viiva",
    OtherAreaLayer.name: "Osa-alue",
    LandUseAreaLayer.name: "Aluevaraus",
    PointLayer.name: "Piste",
}


class PlanObjectsDockFilterProxyModel(QSortFilterProxyModel):
    def __init__(self, model: QStandardItemModel):
        super().__init__()
        self.setSourceModel(model)
        self.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.allowed_types: set[str] = set()

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:  # noqa: N802
        model: QStandardItemModel = self.sourceModel()
        if not model:
            return False

        # 1. Filter by text
        text_match = False
        filter_text = self.filterRegularExpression().pattern()
        if not filter_text:
            text_match = True
        else:
            for column in range(model.columnCount()):
                index = model.index(source_row, column, source_parent)
                data = model.data(index)
                if data and filter_text.lower() in data.lower():
                    text_match = True
                    break

        # 2. Filter by type
        type_match = False
        if not self.allowed_types:
            type_match = True
        else:
            type_index = model.index(source_row, PLAN_OBJECT_TYPE_COLUMN, source_parent)
            feature_type = model.data(type_index)
            type_match = feature_type in self.allowed_types

        return text_match and type_match


class PlanObjectsDock(QgsDockWidget, FormClass):  # type: ignore
    def __init__(self, plan_manager_ref: PlanManager, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        # TYPES
        self.land_use_area_btn: QPushButton
        self.other_area_btn: QPushButton
        self.line_btn: QPushButton
        self.point_btn: QPushButton

        self.table: QTableView
        self.filter_line: QgsFilterLineEdit

        # INIT
        # Reference to get regulation group libraries for PlanObjectForm
        self.plan_manager_ref = plan_manager_ref
        # Used to reapply selections after filtering
        self.selected_plan_feature_ids: set[int] = set()
        # Used for avoiding looping updates between table and map canvas (
        # table select -> trigger map select -> trigger table select.. etc.)
        self._syncing_selections = False
        self._initialized = False

        self.model = QStandardItemModel()
        self.model.setColumnCount(3)
        self.model.setHorizontalHeaderLabels(
            [
                "Nimi",
                "Tyyppi",
                "Kuvaus",
            ]
        )
        self.filter_proxy_model = PlanObjectsDockFilterProxyModel(self.model)
        self.table.setModel(self.filter_proxy_model)

        self.selection_model = self.table.selectionModel()

        # Connect signals
        self.plan_manager_ref.plan_set.connect(lambda: self.model.setRowCount(0))
        self.table.doubleClicked.connect(self._open_form)
        self.selection_model.selectionChanged.connect(self._on_table_selection_changed)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._open_context_menu)
        self.filter_line.textChanged.connect(self._filter_table)

        for btn in (
            self.land_use_area_btn,
            self.other_area_btn,
            self.line_btn,
            self.point_btn,
        ):
            btn.toggled.connect(self._filter_table)

    def initialize(self):
        for layer in plan_feature_layers:
            vector_layer = layer.get_from_project()
            vector_layer.selectionChanged.connect(self._on_feature_selection_changed)
            vector_layer.committedFeaturesAdded.connect(self._on_feats_added)
            vector_layer.committedFeaturesRemoved.connect(self._on_feats_removed)
            vector_layer.committedAttributeValuesChanges.connect(self._on_feat_attributes_changed)

    def unload(self) -> None:
        # Disconnect signals
        self.table.doubleClicked.disconnect(self._open_form)
        self.selection_model.selectionChanged.disconnect(self._on_table_selection_changed)
        self.table.customContextMenuRequested.disconnect(self._open_context_menu)
        self.filter_line.textChanged.disconnect(self._filter_table)

        for layer in plan_feature_layers:
            # If we are closing QGIS, layers are gone already at this point. If we are reloading the plugin,
            # the signals need to be disconnected to avoid duplicate connections
            with suppress(LayerNotFoundError):
                vector_layer = layer.get_from_project()
                vector_layer.selectionChanged.disconnect(self._on_feature_selection_changed)
                vector_layer.committedFeaturesAdded.disconnect(self._on_feats_added)
                vector_layer.committedFeaturesRemoved.disconnect(self._on_feats_removed)
                vector_layer.committedAttributeValuesChanges.disconnect(self._on_feat_attributes_changed)

    def create_plan_feature_view(self):
        # Clear table
        self.model.setRowCount(0)

        # Add all plan features to table view
        # Idea: add `get_models` method for all layer classes
        for layer in plan_feature_layers:
            features = list(layer.get_features())
            for plan_feature_model, feature in zip(layer.models_from_features(features), features):
                self._add_plan_feature_to_view(plan_feature_model, feature.id())

    def update_selected_rows(self):
        self.selection_model.clearSelection()

        for row in range(self.filter_proxy_model.rowCount()):
            item = self.model.item(row, DATA_COLUMN)
            feat_id: int = item.data(DATA_ROLE)[1]
            if feat_id in self.selected_plan_feature_ids:
                proxy_index = self.filter_proxy_model.index(row, 0)
                self.selection_model.select(proxy_index, QItemSelectionModel.Select | QItemSelectionModel.Rows)

    def _add_plan_feature_to_view(self, plan_feature_model: PlanObject, feat_id: int):
        self.model.appendRow(self._plan_feature_into_items(plan_feature_model, feat_id))

    def _remove_plan_feature_from_view(self, row: int):
        self.model.removeRow(row)

    def _filter_table(self):
        # Set text filter
        search_text = self.filter_line.text()
        regex = QRegularExpression(search_text) if search_text else QRegularExpression("")
        self.filter_proxy_model.setFilterRegularExpression(regex)

        # Set type filter
        allowed_types = set()
        if self.land_use_area_btn.isChecked():
            allowed_types.add("Aluevaraus")
        if self.other_area_btn.isChecked():
            allowed_types.add("Osa-alue")
        if self.line_btn.isChecked():
            allowed_types.add("Viiva")
        if self.point_btn.isChecked():
            allowed_types.add("Piste")
        self.filter_proxy_model.allowed_types = allowed_types
        self.filter_proxy_model.invalidateFilter()

        self.update_selected_rows()

    def _update_row(self, row: int, plan_feature_model: PlanObject):
        self.model.item(row, 0).setText(plan_feature_model.name or "")
        self.model.item(row, 2).setText(plan_feature_model.description or "")
        # Feat ID remains the same
        feat_id = self.model.item(row, DATA_COLUMN).data(DATA_ROLE)[1]
        self.model.item(row, DATA_COLUMN).setData((plan_feature_model, feat_id), DATA_ROLE)

    def _plan_feature_into_items(self, plan_feature_model: PlanObject, feat_id: int) -> list[QStandardItem]:
        items = [
            QStandardItem(plan_feature_model.name or ""),
            QStandardItem(LAYER_NAME_TO_FEATURE_TYPE.get(plan_feature_model.layer_name or "", "")),
            QStandardItem(plan_feature_model.description or ""),
        ]

        # Set the whole PlanObject model and QGIS feature ID as data tuple
        items[DATA_COLUMN].setData((plan_feature_model, feat_id), DATA_ROLE)
        return items

    def _data_from_index(self, proxy_index: QModelIndex) -> tuple[PlanObject, int] | None:
        row_items = self._row_items_from_index(proxy_index)
        if len(row_items) == 0:
            return None
        return row_items[DATA_COLUMN].data(DATA_ROLE)

    def _plan_feature_from_index(self, proxy_index: QModelIndex) -> PlanObject | None:
        data = self._data_from_index(proxy_index)
        return data[0] if data else None

    def _row_items_from_index(self, proxy_index: QModelIndex) -> list[QStandardItem]:
        if not proxy_index.isValid():
            return []
        model_index = self.filter_proxy_model.mapToSource(proxy_index)
        row = model_index.row()
        return [self.model.item(row, i) for i in range(self.model.columnCount())]

    def _find_row_by_plan_feature_id(self, plan_feature_id: str) -> int | None:
        # Loop all rows
        for row in range(self.model.rowCount()):
            item = self.model.item(row, DATA_COLUMN)
            plan_feature_model: PlanObject = item.data(DATA_ROLE)[0]
            if plan_feature_model and plan_feature_model.id_ == plan_feature_id:
                return row
        return None

    def _open_form(self, index: QModelIndex):
        plan_feature_model = self._plan_feature_from_index(index)
        if not plan_feature_model:
            iface.messageBar().pushWarning("", "Kaavakohdetta ei löydetty.")
            return

        form = PlanObjectForm(
            plan_feature=plan_feature_model,
            form_title=plan_feature_model.name or plan_feature_model.layer_name or "",
            plan_feature_libraries=self.plan_manager_ref.plan_feature_libraries,
            regulation_group_libraries=self.plan_manager_ref.regulation_group_libraries,
            active_plan_regulation_groups_library=self.plan_manager_ref.active_plan_regulation_group_library,
        )
        if form.exec():
            updated_plan_feature_model = form.model
            if save_plan_feature(updated_plan_feature_model) is not None:
                # Update table row if saving was succesfull
                model_index = self.filter_proxy_model.mapToSource(index)
                row = model_index.row()
                self._update_row(row, updated_plan_feature_model)

    def _open_context_menu(self, pos: QPoint):
        index = self.table.indexAt(pos)
        plan_feature_model = self._plan_feature_from_index(index)
        if not plan_feature_model:
            return

        menu = QMenu()
        menu.addAction(
            QgsApplication.getThemeIcon("mActionOpenTable.svg"), "Näytä lomake", lambda: self._open_form(index)
        )
        menu.addAction(
            QgsApplication.getThemeIcon("mActionZoomTo.svg"),
            "Zoomaa kohteeseen",
            lambda: self._on_zoom_to_feature(plan_feature_model),
        )
        menu.addAction(
            QgsApplication.getThemeIcon("mActionPanTo.svg"),
            "Vieritä kohteeseen",
            lambda: self._on_pan_to_feature(plan_feature_model),
        )
        menu.addAction(
            QgsApplication.getThemeIcon("mActionHighlightFeature.svg"),
            "Väläytä kohdetta",
            lambda: self._on_highlight_feature(plan_feature_model),
        )
        plan_object_library_menu = QMenu("Tallenna kaavakohdepohjakirjastoon")
        menu.addMenu(plan_object_library_menu)
        plan_object_libraries = self.plan_manager_ref.plan_feature_libraries
        if not plan_object_libraries:
            plan_object_library_menu.setEnabled(False)
        else:
            for library in plan_object_libraries:
                plan_object_library_menu.addAction(
                    library.name,
                    lambda library=library: self._on_save_plan_object_to_library(plan_feature_model, library),
                )
        menu.exec_(self.table.viewport().mapToGlobal(pos))

    def _on_zoom_to_feature(self, plan_feature_model: PlanObject):
        layer_class = get_plan_feature_layer_class_by_model(plan_feature_model)
        feat = layer_class.feature_from_model(plan_feature_model)

        iface.mapCanvas().setExtent(feat.geometry().boundingBox().buffered(1000))
        iface.mapCanvas().redrawAllLayers()

    def _on_pan_to_feature(self, plan_feature_model: PlanObject):
        layer_class = get_plan_feature_layer_class_by_model(plan_feature_model)
        feat = layer_class.feature_from_model(plan_feature_model)

        iface.mapCanvas().setCenter(feat.geometry().centroid().asPoint())
        iface.mapCanvas().redrawAllLayers()

    def _on_highlight_feature(self, plan_feature_model: PlanObject):
        iface.mapCanvas().flashGeometries(geometries=[plan_feature_model.geom])
        iface.mapCanvas().redrawAllLayers()

    def _on_save_plan_object_to_library(self, plan_feature_model: PlanObject, library: PlanFeatureLibrary):
        TemplateManager.save_plan_object_to_library(plan_feature_model, library)

    def _on_feats_added(self, layer_id: str, added_features: Iterable[QgsFeature]):
        vector_layer: QgsVectorLayer = QgsProject.instance().mapLayer(layer_id)
        layer = get_plan_feature_layer_class_by_layer_name(vector_layer.name())
        features = list(added_features)
        for plan_feature_model, feat in zip(layer.models_from_features(features), features):
            self._add_plan_feature_to_view(plan_feature_model, feat.id())

    def _on_feats_removed(self, layer_id: int, feature_ids: Iterable[int]):
        vector_layer: QgsVectorLayer = QgsProject.instance().mapLayer(layer_id)
        layer_name = vector_layer.name()

        feats_to_delete = list(feature_ids)
        # Loop all rows
        for row in range(self.model.rowCount()):
            item = self.model.item(row, DATA_COLUMN)
            plan_feature_model: PlanObject = item.data(DATA_ROLE)[0]
            if plan_feature_model.layer_name != layer_name:
                continue
            plan_feat_id = item.data(DATA_ROLE)[1]
            if plan_feat_id in feature_ids:
                self._remove_plan_feature_from_view(row)
                feats_to_delete.remove(plan_feat_id)

            # We have deleted all features that needed to be deleted
            if len(feats_to_delete) == 0:
                return

    def _on_feat_attributes_changed(self, layer_id: int, changed_attribute_values_map: dict):
        vector_layer: QgsVectorLayer = QgsProject.instance().mapLayer(layer_id)
        layer = get_plan_feature_layer_class_by_layer_name(vector_layer.name())
        features = [vector_layer.getFeature(feat_id) for feat_id in changed_attribute_values_map]
        for plan_feature_model in layer.models_from_features(features):
            row = self._find_row_by_plan_feature_id(cast(str, plan_feature_model.id_))
            if row:
                self._update_row(row, plan_feature_model)

    def _on_feature_selection_changed(self, selected: Iterable[int], deselected: Iterable[int], _):
        if self._syncing_selections:
            return
        self._syncing_selections = True
        try:
            for selected_feat_id in selected:
                self.selected_plan_feature_ids.add(selected_feat_id)
            for deselected_feat_id in deselected:
                self.selected_plan_feature_ids.discard(deselected_feat_id)

            self.update_selected_rows()
        finally:
            self._syncing_selections = False

    def _on_table_selection_changed(self, selected: QItemSelection, deselected: QItemSelection):
        if self._syncing_selections:
            return
        self._syncing_selections = True
        try:
            # SELECT
            # NOTE: It seems every time we select a table row, two selected indexes are returned that
            # give the same plan feature
            for index in selected.indexes():
                data = self._data_from_index(index)
                if data is None:
                    continue
                plan_feature = data[0]
                feat_id = data[1]
                layer = get_vector_layer_from_project(cast(str, plan_feature.layer_name))
                layer.selectByIds([feat_id], Qgis.SelectBehavior.AddToSelection)
                self.selected_plan_feature_ids.add(feat_id)

            # DESELECT
            for index in deselected.indexes():
                data = self._data_from_index(index)
                if data is None:
                    continue
                plan_feature = data[0]
                feat_id = data[1]
                layer = get_vector_layer_from_project(cast(str, plan_feature.layer_name))
                layer.deselect(feat_id)
                self.selected_plan_feature_ids.discard(feat_id)
        finally:
            self._syncing_selections = False
