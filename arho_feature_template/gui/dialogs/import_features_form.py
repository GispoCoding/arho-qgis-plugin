from __future__ import annotations

from importlib import resources
from typing import TYPE_CHECKING

from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsFeature,
    QgsFieldProxyModel,
    QgsGeometry,
    QgsMapLayerProxyModel,
    QgsProject,
    QgsVectorLayer,
    QgsWkbTypes,
)
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QCheckBox, QDialog, QDialogButtonBox, QProgressBar

from arho_feature_template.core.feature_editing import save_plan_feature, save_regulation_group
from arho_feature_template.core.models import PlanObject, RegulationGroupLibrary
from arho_feature_template.gui.components.regulation_groups_view import RegulationGroupsView
from arho_feature_template.project.layers.code_layers import (
    PlanRegulationGroupTypeLayer,
    UndergroundTypeLayer,
    code_layers,
)
from arho_feature_template.project.layers.plan_layers import (
    PlanLayer,
    plan_feature_layers,
    plan_layers,
)
from arho_feature_template.utils.misc_utils import iface, use_wait_cursor

if TYPE_CHECKING:
    from qgis.gui import QgsFieldComboBox, QgsMapLayerComboBox

    from arho_feature_template.gui.components.code_combobox import CodeComboBox


ui_path = resources.files(__package__) / "import_features_form.ui"
FormClass, _ = uic.loadUiType(ui_path)


class ImportFeaturesForm(QDialog, FormClass):  # type: ignore
    def __init__(
        self,
        regulation_group_libraries: list[RegulationGroupLibrary],
        active_plan_regulation_groups_library: RegulationGroupLibrary,
    ):
        super().__init__()
        self.setupUi(self)

        # TYPES
        self.source_layer_selection: QgsMapLayerComboBox
        self.selected_features_only: QCheckBox

        self.name_selection: QgsFieldComboBox
        self.description_selection: QgsFieldComboBox
        self.feature_type_of_underground_selection: CodeComboBox

        self.target_layer_selection: QgsMapLayerComboBox

        self.progress_bar: QProgressBar
        self.process_button_box: QDialogButtonBox

        # INIT
        self.process_button_box.button(QDialogButtonBox.Ok).setText("Import")
        self.process_button_box.accepted.connect(self.import_features)
        self.process_button_box.rejected.connect(self.reject)

        self.target_crs: QgsCoordinateReferenceSystem | None = None

        # Source layer initialization
        # Exclude all project layers from valid source layers
        # NOTE: Some project layers are not included in either `plan_layers` or `code_layers`?
        self.source_layer_selection.setFilters(QgsMapLayerProxyModel.VectorLayer)
        excluded_layers = [layer.get_from_project() for layer in plan_layers + code_layers]
        excluded_layers += [
            layer
            for layer in QgsProject.instance().mapLayers().values()
            if isinstance(layer, QgsVectorLayer) and not layer.isSpatial()
        ]

        self.source_layer_selection.setExceptedLayerList(excluded_layers)

        if isinstance(iface.activeLayer(), QgsVectorLayer) and iface.activeLayer().isSpatial():
            self.source_layer_selection.setLayer(iface.activeLayer())
        self.source_layer_selection.layerChanged.connect(self._on_layer_selections_changed)

        # Target layer initialization
        # Set only plan feature layers as valid target layers
        self.target_layer_selection.setFilters(QgsMapLayerProxyModel.VectorLayer)
        self.target_layer_selection.clear()
        self.target_layer_selection.setAdditionalLayers(layer.get_from_project() for layer in plan_feature_layers)
        self.target_layer_selection.setCurrentIndex(0)
        self.target_layer_selection.layerChanged.connect(self._on_layer_selections_changed)

        # Name field initialization
        self.name_selection.setAllowEmptyFieldName(True)
        self.name_selection.setFilters(QgsFieldProxyModel.Filter.String)
        self.name_selection.setField("")

        # Description field initialization
        self.description_selection.setAllowEmptyFieldName(True)
        self.description_selection.setFilters(QgsFieldProxyModel.Filter.String)
        self.description_selection.setField("")

        # Underground type initialization
        # Remove NULL from the selections and set Maanpäällinen as default
        self.feature_type_of_underground_selection.populate_from_code_layer(UndergroundTypeLayer)
        self.feature_type_of_underground_selection.remove_item_by_text("NULL")
        self.feature_type_of_underground_selection.setCurrentIndex(1)  # Set default to Maanpäällinen (index 1)

        self.regulation_groups_view = RegulationGroupsView(
            regulation_group_libraries, active_plan_regulation_groups_library
        )
        self.regulation_groups_view.regulation_groups_label.setText("Kaavakohteiden kaavamääräysryhmät")
        self.layout().insertWidget(3, self.regulation_groups_view)

        self._on_layer_selections_changed(self.source_layer_selection.currentLayer())

    def _on_layer_selections_changed(self, _: QgsVectorLayer):
        self.source_layer: QgsVectorLayer = self.source_layer_selection.currentLayer()
        self.target_layer: QgsVectorLayer = self.target_layer_selection.currentLayer()
        if not self.source_layer:
            return
        self.source_layer_name: str = self.source_layer.name()
        self.target_layer_name: str = self.target_layer.name()

        self.name_selection.setLayer(self.source_layer)
        self.description_selection.setLayer(self.source_layer)

        if self.source_and_target_layer_types_match():
            self.process_button_box.button(QDialogButtonBox.Ok).setEnabled(True)
        else:
            self.process_button_box.button(QDialogButtonBox.Ok).setEnabled(False)

    def source_and_target_layer_types_match(self) -> bool:
        if not self.source_layer or not self.target_layer:
            return False

        source_type = QgsWkbTypes.geometryType(self.source_layer.wkbType())
        target_type = QgsWkbTypes.geometryType(self.target_layer.wkbType())
        return source_type == target_type

    @use_wait_cursor
    def import_features(self):
        self.progress_bar.setValue(0)

        if not self.source_layer or not self.target_layer:
            return

        if not self.target_crs:
            self.target_crs = PlanLayer.get_from_project().crs()

        source_features = list(self.get_source_features(self.source_layer))

        if not source_features:
            iface.messageBar().pushInfo("", "Yhtään kohdetta ei tuotu.")
            return

        # Create and add new plan features
        self.create_and_save_plan_features(source_features)

    def get_source_features(self, source_layer: QgsVectorLayer) -> list[QgsFeature]:
        return (
            source_layer.selectedFeatures() if self.selected_features_only.isChecked() else source_layer.getFeatures()
        )

    def create_and_save_plan_features(self, source_features: list[QgsFeature]):
        crs_mismatch = self.source_layer.crs() != self.target_crs
        transform = QgsCoordinateTransform(
            self.source_layer.crs(), PlanLayer.get_from_project().crs(), QgsProject.instance()
        )

        def _check_geom(geometry: QgsGeometry):
            if crs_mismatch:
                geometry.transform(transform)

            if not geometry.isMultipart():
                geometry.convertToMultiType()
            return geometry

        type_of_underground_id = self.feature_type_of_underground_selection.value()
        source_layer_name_field = self.name_selection.currentField()
        source_layer_description_field = self.description_selection.currentField()
        regulation_groups = self.regulation_groups_view.into_model()
        target_layer_id = PlanRegulationGroupTypeLayer.get_id_by_feature_layer_name(self.target_layer_name)
        for group in regulation_groups:
            # Assign feature layer type for each group based on target layer (will overwrite type_code_id for
            # existing regulation groups)
            group.type_code_id = target_layer_id
            # If the group is not yet in DB, save it now to get an ID and use the same group object for each
            # plan feature
            if group.id_ is None:
                id_ = save_regulation_group(group)
                group.id_ = id_
                group.modified = False

        # Save plan features and track progress
        total_count = len(source_features)
        failed_count = 0
        success_count = 0
        for i, feature in enumerate(source_features):
            model = PlanObject(
                geom=_check_geom(feature.geometry()),
                type_of_underground_id=type_of_underground_id,
                layer_name=self.target_layer_name,
                name=feature[source_layer_name_field] if source_layer_name_field else None,
                description=feature[source_layer_description_field] if source_layer_description_field else None,
                regulation_groups=regulation_groups,
            )
            self.progress_bar.setValue(int((i + 1) / total_count * 100))
            if save_plan_feature(model):
                success_count += 1
            else:
                failed_count += 1

        self.progress_bar.setValue(100)

        if failed_count == 0:
            iface.messageBar().pushSuccess("", "Kaavakohteet tuotiin onnistuneesti.")
        else:
            iface.messageBar().pushInfo("", f"Osa kaavakohteista tuotiin epäonnistuneesti ({failed_count}).")
