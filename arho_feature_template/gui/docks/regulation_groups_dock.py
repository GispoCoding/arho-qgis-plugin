from __future__ import annotations

from importlib import resources
from typing import TYPE_CHECKING, Generator

from qgis.core import Qgis, QgsApplication, QgsFeature, QgsFeatureRequest, QgsGeometry
from qgis.gui import QgsDockWidget
from qgis.PyQt import uic
from qgis.PyQt.QtCore import QModelIndex, QPoint, QRegularExpression, QSortFilterProxyModel, Qt, pyqtSignal
from qgis.PyQt.QtGui import QStandardItem, QStandardItemModel
from qgis.PyQt.QtWidgets import QHeaderView, QMenu, QMessageBox, QPushButton, QTableView

from arho_feature_template.core.models import RegulationGroup, RegulationGroupLibrary
from arho_feature_template.project.layers.plan_layers import (
    RegulationGroupAssociationLayer,
    get_plan_feature_layer_class_by_layer_name,
    plan_feature_layers,
)
from arho_feature_template.utils.localization_utils import get_localized_text
from arho_feature_template.utils.misc_utils import disconnect_signal, iface

if TYPE_CHECKING:
    from qgis.gui import QgsFilterLineEdit
    from qgis.PyQt.QtWidgets import QWidget


ui_path = resources.files(__package__) / "regulation_groups_dock.ui"
DockClass, _ = uic.loadUiType(ui_path)


# COLUMNS
DATA_COLUMN = 0
DATA_ROLE = Qt.UserRole


class RegulationGroupsDockFilterProxyModel(QSortFilterProxyModel):
    def __init__(self, model: QStandardItemModel):
        super().__init__()
        self.setSourceModel(model)
        self.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.allowed_types: set[str] = set()

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:  # noqa: N802
        model: QStandardItemModel = self.sourceModel()
        if not model:
            return False

        # Filter by text
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

        return text_match


class RegulationGroupsDock(QgsDockWidget, DockClass):  # type: ignore
    request_new_regulation_group_empty = pyqtSignal()
    request_new_regulation_group_template = pyqtSignal()

    request_edit_regulation_group = pyqtSignal(RegulationGroup)
    request_delete_regulation_groups = pyqtSignal(object)  # Type: list[RegulationGroup]
    request_remove_all_regulation_groups = pyqtSignal(object)  # Type: list[tuple[str, Generator[str]]]
    request_remove_selected_groups = pyqtSignal(
        object, object
    )  # Types: list[RegulationGroup],  list[tuple[str, Generator[str]]
    request_add_groups_to_features = pyqtSignal(
        object, object
    )  # Types: list[RegulationGroup],  list[tuple[str, Generator[str]]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        # TYPES
        self.filter_line: QgsFilterLineEdit
        self.dockWidgetContents: QWidget
        self.table: QTableView

        self.new_btn: QPushButton
        self.delete_btn: QPushButton
        self.edit_btn: QPushButton
        self.modify_selected_features_btn: QPushButton

        # INIT
        self.new_btn.setIcon(QgsApplication.getThemeIcon("mActionAdd.svg"))
        self.delete_btn.setIcon(QgsApplication.getThemeIcon("mActionDeleteSelected.svg"))
        self.edit_btn.setIcon(QgsApplication.getThemeIcon("mActionEditTable.svg"))

        new_regulation_group_menu = QMenu()
        self.new_group_empty_action = new_regulation_group_menu.addAction("Tyhjä")
        self.new_group_from_template_action = new_regulation_group_menu.addAction("Pohjasta")
        new_regulation_group_menu.addActions([self.new_group_empty_action, self.new_group_from_template_action])
        self.new_btn.setMenu(new_regulation_group_menu)

        plan_object_actions_menu = QMenu()
        self.add_selected_action = plan_object_actions_menu.addAction("Lisää valitut ryhmät valituille kohteille")
        self.remove_all_action = plan_object_actions_menu.addAction("Poista kaikki ryhmät valituilta kohteilta")
        self.remove_selected_action = plan_object_actions_menu.addAction("Poista valitut ryhmät valituilta kohteilta")
        self.modify_selected_features_btn.setMenu(plan_object_actions_menu)

        self._connect_signals()

        # Create the model
        self.model = QStandardItemModel()
        self.model.setColumnCount(4)
        self.model.setHorizontalHeaderLabels(["#", "Kirjaintunnus", "Otsikko", "Kohteiden lkm."])
        self.filter_proxy_model = RegulationGroupsDockFilterProxyModel(self.model)

        self.table.setModel(self.filter_proxy_model)
        self.table.resizeColumnsToContents()
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._open_context_menu)
        self.table.doubleClicked.connect(self._open_form)

        self.selection_model = self.table.selectionModel()

        self.plan_locked = False

    def initialize(self):
        # Connect feat remove signals for each plan object layer so the linked plan object counts
        # stay updated
        for plan_object_layer in plan_feature_layers:
            plan_object_layer.get_from_project().committedFeaturesRemoved.connect(
                lambda _layer_id, ids, layer_name=plan_object_layer.name: self._on_feats_removed(layer_name, ids)
            )

    def _disconnect_signals(self):
        disconnect_signal(self.new_group_empty_action.triggered)
        disconnect_signal(self.new_group_from_template_action.triggered)
        disconnect_signal(self.edit_btn.clicked)
        disconnect_signal(self.delete_btn.clicked)
        disconnect_signal(self.remove_all_action.triggered)
        disconnect_signal(self.remove_selected_action.triggered)
        disconnect_signal(self.add_selected_action.triggered)
        disconnect_signal(self.filter_line.textChanged)

    def _connect_signals(self):
        self._disconnect_signals()

        self.new_group_empty_action.triggered.connect(self.request_new_regulation_group_empty.emit)
        self.new_group_from_template_action.triggered.connect(self.request_new_regulation_group_template.emit)
        self.edit_btn.clicked.connect(self.on_edit_btn_clicked)
        self.delete_btn.clicked.connect(self.on_delete_btn_clicked)
        self.remove_all_action.triggered.connect(self.on_remove_all_btn_clicked)
        self.remove_selected_action.triggered.connect(self.on_remove_selected_btn_clicked)
        self.add_selected_action.triggered.connect(self.on_add_selected_btn_clicked)
        self.filter_line.textChanged.connect(self._filter_table)

    def update_lock_status(self, locked: bool):  # noqa: FBT001
        self.plan_locked = locked
        self.new_btn.setEnabled(not locked)
        self.delete_btn.setEnabled(not locked)
        self.modify_selected_features_btn.setEnabled(not locked)

        if locked:
            self.new_btn.setToolTip("Kaavasuunnitelma on lukittu, kaavamääräysryhmiä ei voi lisätä.")
            self.delete_btn.setToolTip("Kaavasuunnitelma on lukittu, kaavamääräysryhmiä ei voi poistaa.")
            self.modify_selected_features_btn.setToolTip("Kaavasuunnitelma on lukittu, kaavakohteita ei voi muokata.")
        else:
            self.new_btn.setToolTip("")
            self.delete_btn.setToolTip("")
            self.modify_selected_features_btn.setToolTip("")

    def _filter_table(self):
        # Set text filter
        search_text = self.filter_line.text()
        regex = QRegularExpression(search_text) if search_text else QRegularExpression("")
        self.filter_proxy_model.setFilterRegularExpression(regex)
        self.filter_proxy_model.invalidateFilter()

    def update_regulation_groups(self, regulation_group_library: RegulationGroupLibrary):
        # Clear table
        self.model.setRowCount(0)

        if len(regulation_group_library.regulation_groups) == 0:
            return

        # Get regulation group associations only once
        plan_object_ids_by_group_id: dict[str, dict[str, list[str]]] = (
            RegulationGroupAssociationLayer.get_plan_object_ids_by_regulation_group(
                associations=list(RegulationGroupAssociationLayer.get_features())
            )
        )

        # Get plan objects for each layer only once
        plan_objects_by_layer: dict[str, list[QgsFeature]] = {}
        for plan_object_layer in plan_feature_layers:
            layer = plan_object_layer.get_from_project()
            request = QgsFeatureRequest()
            request.setSubsetOfAttributes(["id"], layer.fields())
            plan_objects_by_layer[plan_object_layer.name] = list(layer.getFeatures(request))

        for group in regulation_group_library.regulation_groups:
            plan_object_ids_map = plan_object_ids_by_group_id.get(group.id_)  # type: ignore
            self.model.appendRow(self._regulation_group_into_items(group, plan_object_ids_map, plan_objects_by_layer))

    def _regulation_group_into_items(
        self,
        group: RegulationGroup,
        plan_object_ids_map: dict[str, list[str]] | None,
        plan_objects_by_layer: dict[str, list[QgsFeature]],
    ) -> list[QStandardItem]:
        if group.id_ is None:
            return []

        # Create items
        items = [
            QStandardItem(str(group.group_number) if group.group_number else ""),
            QStandardItem(group.letter_code or ""),
            QStandardItem(get_localized_text(group.heading) or ""),
            QStandardItem(str(sum(len(v) for v in plan_object_ids_map.values()) if plan_object_ids_map else 0)),
        ]

        # Set tooltips
        tooltip_text = group.as_tooltip(long=True)
        for item in items:
            item.setToolTip(tooltip_text)

        # Save FIDS and geometries of associated plan objects
        associated_plan_object_fids_and_geoms: dict[str, dict[int, QgsGeometry]] = {}
        if plan_object_ids_map:
            for layer_name, ids in plan_object_ids_map.items():
                fids_to_geoms: dict[int, QgsGeometry] = {
                    feat.id(): feat.geometry() for feat in plan_objects_by_layer[layer_name] if feat["id"] in ids
                }
                associated_plan_object_fids_and_geoms[layer_name] = fids_to_geoms

        # Set data
        items[DATA_COLUMN].setData((group, associated_plan_object_fids_and_geoms), DATA_ROLE)
        return items

    def get_selected_plan_object_ids(self) -> list[tuple[str, Generator[str]]]:
        """Returns selected plan object IDs for each plan object layer (name)."""
        return [(layer_class.name, layer_class.get_selected_feature_ids()) for layer_class in plan_feature_layers]

    def get_selected_regulation_groups(self) -> list[RegulationGroup]:
        groups: list[RegulationGroup] = []
        for proxy_index in self.selection_model.selectedRows(DATA_COLUMN):
            group = self._regulation_group_from_index(proxy_index)
            if group is not None:
                groups.append(group)
        return groups

    def on_edit_btn_clicked(self):
        selected = self.get_selected_regulation_groups()
        if len(selected) == 0:
            return
        if len(selected) == 1:
            self.request_edit_regulation_group.emit(selected[0])
        else:
            iface.messageBar().pushWarning("", "Valitse vain yksi kaavamääräysryhmä kerrallaan muokkaamista varten.")

    def _row_items_from_index(self, proxy_index: QModelIndex) -> list[QStandardItem]:
        if not proxy_index.isValid():
            return []
        model_index = self.filter_proxy_model.mapToSource(proxy_index)
        row = model_index.row()
        return [self.model.item(row, i) for i in range(self.model.columnCount())]

    def _data_from_index(
        self, proxy_index: QModelIndex
    ) -> tuple[RegulationGroup, dict[str, dict[int, QgsGeometry]]] | None:
        """
        Data is tuple of RegulationGroup model and dictionary of associated plan object FIDs and geoms
        (keys are plan object layer names).
        """
        row_items = self._row_items_from_index(proxy_index)
        if len(row_items) == 0:
            return None
        return row_items[DATA_COLUMN].data(DATA_ROLE)

    def _regulation_group_from_index(self, proxy_index: QModelIndex) -> RegulationGroup | None:
        data = self._data_from_index(proxy_index)
        return data[0] if data else None

    def _update_row_data(self, row: int, group: RegulationGroup, assoc_data: dict[str, dict[int, QgsGeometry]]) -> None:
        item = self.model.item(row, DATA_COLUMN)
        if item:
            item.setData((group, assoc_data), DATA_ROLE)

            # Update row linked plan objects count
            total = sum(len(fid_map) for fid_map in assoc_data.values()) if assoc_data else 0
            count_item = self.model.item(row, 3)
            if count_item:
                count_item.setText(str(total))

    def _open_form(self, index: QModelIndex):
        group_model = self._regulation_group_from_index(index)
        if not group_model:
            iface.messageBar().pushWarning("", "Kaavamääräysryhmää ei löytynyt.")
            return

        self.request_edit_regulation_group.emit(group_model)

    def on_delete_btn_clicked(self):
        selected_groups = self.get_selected_regulation_groups()
        nr_of_groups = len(selected_groups)
        if nr_of_groups > 0:
            response = QMessageBox.question(
                None,
                "Kaavamääräysryhmän poisto" if nr_of_groups == 1 else "Kaavamääräysryhmien poisto",
                "Haluatko varmasti poistaa kaavamääräysryhmän?"
                if nr_of_groups == 1
                else "Haluatko varmasti poistaa kaavamääräysryhmät?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if response == QMessageBox.Yes:
                self.request_delete_regulation_groups.emit(selected_groups)

    def on_remove_all_btn_clicked(self):
        self.request_remove_all_regulation_groups.emit(self.get_selected_plan_object_ids())

    def on_remove_selected_btn_clicked(self):
        selected_groups = self.get_selected_regulation_groups()
        if len(selected_groups) > 0:
            self.request_remove_selected_groups.emit(selected_groups, self.get_selected_plan_object_ids())

    def on_add_selected_btn_clicked(self):
        selected_groups = self.get_selected_regulation_groups()
        if len(selected_groups) > 0:
            self.request_add_groups_to_features.emit(selected_groups, self.get_selected_plan_object_ids())

    def _open_context_menu(self, pos: QPoint):
        index = self.table.indexAt(pos)
        data = self._data_from_index(index)
        if not data:
            return

        # associated_plan_object_fids_and_geoms = data[1]
        nr_of_selected_groups = len(self.get_selected_regulation_groups())

        menu = QMenu()
        menu.addAction(
            QgsApplication.getThemeIcon("mActionOpenTable.svg"), "Näytä lomake", lambda: self._open_form(index)
        )
        menu.addSeparator()
        menu.addAction(
            QgsApplication.getThemeIcon("mActionZoomTo.svg"),
            "Valitse kaavakohteet joilla on kaavamääräysryhmä"
            if nr_of_selected_groups == 1
            else "Valitse kaavakohteet, joilla on valitut kaavamääräysryhmät",
            self._on_select_plan_objects,
        )
        menu.addAction(
            QgsApplication.getThemeIcon("mActionHighlightFeature.svg"),
            "Väläytä kaavakohteita, joilla on kaavamääräysryhmä"
            if nr_of_selected_groups == 1
            else "Väläytä kaavakohteita, joilla on valitut kaavamääräysryhmät",
            self._on_highlight_plan_objects,
        )
        menu.addSeparator()
        del_action = menu.addAction(
            QgsApplication.getThemeIcon("mActionDeleteSelected.svg"),
            "Poista kaavamääräysryhmä" if nr_of_selected_groups == 1 else "Poista valitut kaavamääräysryhmät",
            self.on_delete_btn_clicked,
        )
        del_action.setEnabled(not self.plan_locked)

        menu.exec_(self.table.viewport().mapToGlobal(pos))

    def _on_select_plan_objects(self):
        fids_and_geoms_map = self._get_common_associated_plan_object_fids_and_geoms_for_selected_groups()
        for layer_name, fids_and_geoms in fids_and_geoms_map.items():
            layer_class = get_plan_feature_layer_class_by_layer_name(layer_name)
            layer_class.get_from_project().selectByIds(list(fids_and_geoms.keys()), Qgis.SelectBehavior.SetSelection)

    def _on_highlight_plan_objects(self):
        fids_and_geoms_map = self._get_common_associated_plan_object_fids_and_geoms_for_selected_groups()
        for fids_and_geoms in fids_and_geoms_map.values():
            iface.mapCanvas().flashGeometries(geometries=list(fids_and_geoms.values()))
        iface.mapCanvas().redrawAllLayers()

    def _get_common_associated_plan_object_fids_and_geoms_for_selected_groups(
        self,
    ) -> dict[str, dict[int, QgsGeometry]]:
        assoc_data = []
        for proxy_index in self.selection_model.selectedRows(DATA_COLUMN):
            data = self._data_from_index(proxy_index)
            if not data:
                continue
            assoc_data.append(data[1])

        if not assoc_data:
            return {}

        if len(assoc_data) == 1:
            return assoc_data[0]

        common: dict[str, dict[int, QgsGeometry]] = assoc_data[0].copy()

        # Intersect all fids per layer
        for assoc in assoc_data[1:]:
            for layer_name in common:
                next_map = assoc.get(layer_name)
                if not next_map:
                    common[layer_name] = {}
                    continue
                current_map = common[layer_name]
                common_fids = set(current_map.keys()) & set(next_map.keys())
                common[layer_name] = {fid: current_map[fid] for fid in common_fids}

        return common

    def unload(self):
        self._disconnect_signals()

        disconnect_signal(self.request_new_regulation_group_empty)
        disconnect_signal(self.request_new_regulation_group_template)
        disconnect_signal(self.request_edit_regulation_group)
        disconnect_signal(self.request_delete_regulation_groups)
        disconnect_signal(self.request_remove_all_regulation_groups)
        disconnect_signal(self.request_remove_selected_groups)
        disconnect_signal(self.request_add_groups_to_features)

    def _on_feats_removed(self, layer_name: str, feat_ids):
        feat_ids_set = set(feat_ids)

        for row in range(self.model.rowCount()):
            item = self.model.item(row, DATA_COLUMN)
            if not item:
                continue

            data = item.data(DATA_ROLE)
            if not data:
                continue

            group: RegulationGroup = data[0]
            assoc_data: dict[str, dict[int, QgsGeometry]] = data[1]
            layer_map: dict[int, QgsGeometry] | None = assoc_data.get(layer_name)
            if not layer_map:
                continue

            # Remove deleted fids from this row's association map for layer
            removed_any = False
            for fid in feat_ids_set:
                if fid in layer_map:
                    layer_map.pop(fid)
                    removed_any = True

            if not removed_any:
                continue

            # Delete layer map if empty
            if not layer_map:
                assoc_data.pop(layer_name)

            # Set the updated association map to table
            self._update_row_data(row, group, assoc_data)
