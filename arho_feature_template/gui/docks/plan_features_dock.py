from __future__ import annotations

from importlib import resources
from typing import TYPE_CHECKING, Iterable, cast

from qgis.core import QgsFeature, QgsProject, QgsVectorLayer
from qgis.gui import QgsDockWidget, QgsFilterLineEdit
from qgis.PyQt import uic
from qgis.PyQt.QtCore import QModelIndex, QPoint, QRegularExpression, QSortFilterProxyModel, Qt
from qgis.PyQt.QtGui import QStandardItem, QStandardItemModel
from qgis.PyQt.QtWidgets import QMenu, QTableView

from arho_feature_template.core.feature_editing import save_plan_feature
from arho_feature_template.gui.dialogs.plan_feature_form import PlanFeatureForm
from arho_feature_template.project.layers.plan_layers import (
    get_plan_feature_layer_class_by_layer_name,
    get_plan_feature_layer_class_by_model,
    plan_feature_layers,
)
from arho_feature_template.utils.misc_utils import iface

ui_path = resources.files(__package__) / "plan_features_dock.ui"
FormClass, _ = uic.loadUiType(ui_path)

if TYPE_CHECKING:
    from arho_feature_template.core.models import PlanFeature
    from arho_feature_template.core.plan_manager import PlanManager

DATA_COLUMN = 0
DATA_ROLE = Qt.UserRole


class PlanFeaturesDockFilterProxyModel(QSortFilterProxyModel):
    def __init__(self, model: QStandardItemModel):
        super().__init__()
        self.setSourceModel(model)
        self.setFilterCaseSensitivity(Qt.CaseInsensitive)

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:  # noqa: N802
        model: QStandardItemModel = self.sourceModel()
        if not model:
            return False

        filter_text = self.filterRegularExpression().pattern()
        if not filter_text:
            return True

        for column in range(model.columnCount()):
            index = model.index(source_row, column, source_parent)
            data = model.data(index)
            if data and filter_text.lower() in data.lower():
                return True

        return False


class PlanFeaturesDock(QgsDockWidget, FormClass):  # type: ignore
    def __init__(self, plan_manager_ref: PlanManager, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        # TYPES
        self.table: QTableView
        self.filter_line: QgsFilterLineEdit

        # INIT
        # Reference to get regulation group libraries for PlanFeatureForm
        self.plan_manager_ref = plan_manager_ref
        # Used for finding rows to delete when a plan feature is deleted
        self.feat_id_to_model_id_map: dict[int, str] = {}

        self.model = QStandardItemModel()
        self.model.setColumnCount(2)
        self.model.setHorizontalHeaderLabels(
            [
                "Nimi",
                "Kuvaus",
            ]
        )
        self.filter_proxy_model = PlanFeaturesDockFilterProxyModel(self.model)
        self.table.setModel(self.filter_proxy_model)

        self.table.doubleClicked.connect(self._open_form)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._open_context_menu)
        self.filter_line.textChanged.connect(self._filter_table)

        for layer in plan_feature_layers:
            vector_layer = layer.get_from_project()
            vector_layer.committedFeaturesAdded.connect(self._on_feats_added)
            vector_layer.committedFeaturesRemoved.connect(self._on_feats_removed)
            vector_layer.committedAttributeValuesChanges.connect(self._on_feat_attributes_changed)

    def unload(self) -> None:
        for layer in plan_feature_layers:
            vector_layer = layer.get_from_project()
            vector_layer.committedFeaturesAdded.disconnect(self._on_feats_added)
            vector_layer.committedFeaturesRemoved.disconnect(self._on_feats_removed)
            vector_layer.committedAttributeValuesChanges.disconnect(self._on_feat_attributes_changed)

    def create_plan_feature_view(self):
        # Clear table
        self.model.setRowCount(0)
        self.feat_id_to_model_id_map.clear()

        # Add all plan features to table view
        # Idea: add `get_models` method for all layer classes
        for layer in plan_feature_layers:
            for feature in layer.get_features():
                plan_feature_model = layer.model_from_feature(feature)
                self._add_plan_feature_to_view(plan_feature_model, feature.id())

    def _add_plan_feature_to_view(self, plan_feature_model: PlanFeature, feat_id: int):
        self.model.appendRow(self._plan_feature_into_items(plan_feature_model, feat_id))
        self.feat_id_to_model_id_map[feat_id] = cast(str, plan_feature_model.id_)

    def _remove_plan_feature_from_view(self, plan_feature_id: str, feat_id: int):
        row = self._find_row_by_plan_feature_id(plan_feature_id)
        if row is not None:
            self.model.removeRow(row)
            self.feat_id_to_model_id_map.pop(feat_id)

    def _filter_table(self):
        search_text = self.filter_line.text()
        if search_text:
            self.filter_proxy_model.setFilterRegularExpression(QRegularExpression(search_text))
        else:
            self.filter_proxy_model.setFilterRegularExpression("")

    def _update_row(self, row: int, plan_feature_model: PlanFeature):
        self.model.item(row, 0).setText(plan_feature_model.name or "")
        self.model.item(row, 1).setText(plan_feature_model.description or "")
        # Feat ID remains the same
        feat_id = self.model.item(row, DATA_COLUMN).data(DATA_ROLE)[1]
        self.model.item(row, DATA_COLUMN).setData((plan_feature_model, feat_id), DATA_ROLE)

    def _open_form(self, index: QModelIndex):
        plan_feature_model = self._plan_feature_from_index(index)
        if not plan_feature_model:
            iface.messageBar().pushWarning("", "Kaavakohdetta ei löydetty.")
            return

        form = PlanFeatureForm(
            plan_feature=plan_feature_model,
            form_title=plan_feature_model.name or plan_feature_model.layer_name or "",
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
        menu.addAction("Näytä lomake", lambda: self._open_form(index))
        menu.addAction("Zoomaa kohteeseen", lambda: self._on_zoom_to_feature(plan_feature_model))
        menu.addAction("Vieritä kohteeseen", lambda: self._on_pan_to_feature(plan_feature_model))
        menu.addAction("Väläytä kohdetaa", lambda: self._on_highlight_feature(plan_feature_model))
        menu.exec_(self.table.viewport().mapToGlobal(pos))

    def _on_zoom_to_feature(self, plan_feature_model: PlanFeature):
        layer_class = get_plan_feature_layer_class_by_model(plan_feature_model)
        feat = layer_class.feature_from_model(plan_feature_model)

        iface.mapCanvas().setExtent(feat.geometry().boundingBox().buffered(1000))
        iface.mapCanvas().redrawAllLayers()

    def _on_pan_to_feature(self, plan_feature_model: PlanFeature):
        layer_class = get_plan_feature_layer_class_by_model(plan_feature_model)
        feat = layer_class.feature_from_model(plan_feature_model)

        iface.mapCanvas().setCenter(feat.geometry().centroid().asPoint())
        iface.mapCanvas().redrawAllLayers()

    def _on_highlight_feature(self, plan_feature_model: PlanFeature):
        iface.mapCanvas().flashGeometries(geometries=[plan_feature_model.geom])
        iface.mapCanvas().redrawAllLayers()

    # Helpers
    def _plan_feature_into_items(self, plan_feature_model: PlanFeature, feat_id: int) -> list[QStandardItem]:
        items = [
            QStandardItem(plan_feature_model.name or ""),
            QStandardItem(plan_feature_model.description or ""),
        ]

        # Set the whole PlanFeature model and QGIS feature ID as data tuple
        items[DATA_COLUMN].setData((plan_feature_model, feat_id), DATA_ROLE)

        return items

    def _plan_feature_from_index(self, proxy_index: QModelIndex) -> PlanFeature | None:
        row_items = self._row_items_from_index(proxy_index)
        if len(row_items) == 0:
            return None
        return row_items[DATA_COLUMN].data(DATA_ROLE)[0]

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
            plan_feature_model: PlanFeature = item.data(DATA_ROLE)[0]
            if plan_feature_model and plan_feature_model.id_ == plan_feature_id:
                return row
        return None

    def _on_feats_added(self, layer_id: str, added_features: Iterable[QgsFeature]):
        vector_layer: QgsVectorLayer = QgsProject.instance().mapLayer(layer_id)
        layer = get_plan_feature_layer_class_by_layer_name(vector_layer.name())
        for feat in added_features:
            plan_feature_model = layer.model_from_feature(feat)
            self._add_plan_feature_to_view(plan_feature_model, feat.id())

    def _on_feats_removed(self, _layer_id: int, feature_ids: Iterable[int]):
        for feat_id in feature_ids:
            model_id = self.feat_id_to_model_id_map.get(feat_id)
            if model_id:
                self._remove_plan_feature_from_view(model_id, feat_id)

    def _on_feat_attributes_changed(self, layer_id: int, changed_attribute_values_map: dict):
        vector_layer: QgsVectorLayer = QgsProject.instance().mapLayer(layer_id)
        layer = get_plan_feature_layer_class_by_layer_name(vector_layer.name())
        for feat_id in changed_attribute_values_map:
            feat = vector_layer.getFeature(feat_id)
            plan_feature_model = layer.model_from_feature(feat)

            row = self._find_row_by_plan_feature_id(cast(str, plan_feature_model.id_))
            if row:
                self._update_row(row, plan_feature_model)
