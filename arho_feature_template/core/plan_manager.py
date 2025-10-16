from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Generator, Iterable, cast

from qgis.core import (
    QgsExpressionContextUtils,
    QgsFeature,
    QgsGeometry,
    QgsProject,
    QgsVariantUtils,
    QgsVectorLayer,
    QgsWkbTypes,
)
from qgis.gui import QgsMapToolDigitizeFeature
from qgis.PyQt.QtCore import QObject, pyqtSignal
from qgis.PyQt.QtWidgets import QDialog

from arho_feature_template import SUPPORTED_PROJECT_VERSION
from arho_feature_template.core.feature_editing import (
    delete_feature,
    delete_regulation_group,
    save_plan,
    save_plan_feature,
    save_plan_matter,
    save_regulation_group,
    save_regulation_group_association,
)
from arho_feature_template.core.lambda_service import LambdaService
from arho_feature_template.core.models import (
    Plan,
    PlanFeatureLibrary,
    PlanMatter,
    PlanObject,
    RegulationGroup,
    RegulationGroupLibrary,
)
from arho_feature_template.core.template_manager import TemplateManager
from arho_feature_template.exceptions import UnsavedChangesError
from arho_feature_template.gui.dialogs.import_features_form import ImportFeaturesForm
from arho_feature_template.gui.dialogs.import_plan_form import ImportPlanForm
from arho_feature_template.gui.dialogs.lifecycle_editor import LifecycleEditor
from arho_feature_template.gui.dialogs.load_plan_dialog import LoadPlanDialog
from arho_feature_template.gui.dialogs.load_plan_matter_dialog import LoadPlanMatterDialog
from arho_feature_template.gui.dialogs.manage_libraries import ManageLibrariesForm
from arho_feature_template.gui.dialogs.manage_plans import ManagePlans
from arho_feature_template.gui.dialogs.plan_attribute_form import PlanAttributeForm
from arho_feature_template.gui.dialogs.plan_feature_form import PlanObjectForm
from arho_feature_template.gui.dialogs.plan_matter_attribute_form import PlanMatterAttributeForm
from arho_feature_template.gui.dialogs.plan_regulation_group_form import PlanRegulationGroupForm
from arho_feature_template.gui.dialogs.serialize_plan import SerializePlan
from arho_feature_template.gui.dialogs.serialize_plan_matter import SerializePlanMatter
from arho_feature_template.gui.docks.new_feature_dock import NewFeatureDock
from arho_feature_template.gui.docks.plan_features_dock import PlanObjectsDock
from arho_feature_template.gui.docks.regulation_groups_dock import RegulationGroupsDock
from arho_feature_template.gui.tools.inspect_plan_features_tool import InspectPlanFeatures
from arho_feature_template.project.layers.code_layers import (
    AdditionalInformationTypeLayer,
    PlanRegulationGroupTypeLayer,
    PlanRegulationTypeLayer,
    PlanType,
    code_layers,
)
from arho_feature_template.project.layers.plan_layers import (
    FEATURE_LAYER_NAME_TO_CLASS_MAP,
    PlanLayer,
    PlanMatterLayer,
    PlanTypeLayer,
    RegulationGroupAssociationLayer,
    RegulationGroupLayer,
    plan_feature_layers,
    plan_layers,
    plan_matter_layers,
)
from arho_feature_template.qgis_plugin_tools.tools.resources import plugin_path
from arho_feature_template.resources.libraries.feature_templates import (
    get_user_plan_feature_library_config_files,
    set_user_plan_feature_library_config_files,
)
from arho_feature_template.resources.libraries.regulation_groups import (
    get_default_regulation_group_library_config_files,
    get_user_regulation_group_library_config_files,
    set_user_regulation_group_library_config_files,
)
from arho_feature_template.utils.db_utils import get_existing_database_connection_names
from arho_feature_template.utils.misc_utils import (
    check_layer_changes,
    disconnect_signal,
    get_active_plan_id,
    get_active_plan_matter_id,
    handle_unsaved_changes,
    iface,
    set_active_plan_id,
    set_active_plan_matter_id,
    set_imported_layer_invisible,
    use_wait_cursor,
)

logger = logging.getLogger(__name__)

QML_MAP = {
    "Aluevaraus": "land_use_area.qml",
    "Osa-alue": "other_area.qml",
    "Viivat": "line.qml",
    "Pisteet": "point.qml",
}


class PlanDigitizeMapTool(QgsMapToolDigitizeFeature): ...


class PlanFeatureDigitizeMapTool(QgsMapToolDigitizeFeature):
    def __init__(self, mode: QgsMapToolDigitizeFeature.CaptureMode):
        super().__init__(iface.mapCanvas(), iface.cadDockWidget(), mode)


class PlanManager(QObject):
    plan_set = pyqtSignal()
    plan_unset = pyqtSignal()
    plan_matter_set = pyqtSignal()
    plan_matter_unset = pyqtSignal()
    project_loaded = pyqtSignal()
    project_cleared = pyqtSignal()
    plan_identifier_set = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.json_plan_path = None
        self.json_plan_outline_path = None
        self.json_plan_matter_path = None

        self.plan_feature_libraries = []
        self.regulation_group_libraries = []

        # Initialize new feature dock
        self.new_feature_dock = NewFeatureDock(iface.mainWindow())
        self.new_feature_dock.tool_activated.connect(self.add_new_plan_feature)
        self.new_feature_dock.hide()

        # Initialize regulation groups dock
        self.regulation_groups_dock = RegulationGroupsDock(iface.mainWindow())
        self.regulation_groups_dock.request_new_regulation_group.connect(self.create_new_regulation_group)
        self.regulation_groups_dock.request_edit_regulation_group.connect(self.edit_regulation_group)
        self.regulation_groups_dock.request_delete_regulation_groups.connect(self.delete_regulation_groups)
        self.regulation_groups_dock.request_remove_all_regulation_groups.connect(
            self.remove_all_regulation_groups_from_features
        )
        self.regulation_groups_dock.request_remove_selected_groups.connect(
            self.remove_selected_regulation_groups_from_features
        )
        self.regulation_groups_dock.request_add_groups_to_features.connect(self.add_regulation_groups_to_features)

        self.update_active_plan_regulation_group_library()
        self.regulation_groups_dock.hide()

        # Initialize plan features dock
        self.features_dock = PlanObjectsDock(self, iface.mainWindow())
        self.features_dock.hide()

        # Initialize digitize tools
        self.plan_digitize_map_tool = PlanDigitizeMapTool(iface.mapCanvas(), iface.cadDockWidget())
        self.plan_digitize_map_tool.digitizingCompleted.connect(self._plan_geom_ready)

        self.feature_digitize_map_tool = None
        self.initialize_feature_digitize_map_tool()

        # Initialize plan feature inspect tool
        self.inspect_plan_feature_tool = InspectPlanFeatures(
            iface.mapCanvas(), list(FEATURE_LAYER_NAME_TO_CLASS_MAP.values())
        )
        self.inspect_plan_feature_tool.edit_feature_requested.connect(self.edit_plan_feature)

        # Initialize lambda service
        self.lambda_service = LambdaService()
        self.lambda_service.plan_identifier_received.connect(
            lambda value: self.set_permanent_identifier(value["identifier"])
        )
        self.lambda_service.plan_data_received.connect(self.save_exported_plan)
        self.lambda_service.plan_matter_data_received.connect(self.save_exported_plan_matter)

    def initialize_from_project(self):
        self.cache_code_layers()
        self.initialize_libraries()

    def check_compatible_project_version(self) -> bool:
        project_version, ok = QgsProject.instance().readEntry("arho", "project_version")
        if not ok:
            msg = "Projektitiedostosta ei löytynyt ARHO versiomerkintää. Käytäthän varmasti yhteensopivaa projektiedostoa?"
            iface.messageBar().pushCritical("", msg)
            return False

        if float(project_version) != SUPPORTED_PROJECT_VERSION:
            msg = (
                "Projektitiedosto ei ole yhteensopiva lisäosan version kanssa "
                f"(havaittu versio {project_version}, vaadittu {SUPPORTED_PROJECT_VERSION})"
            )
            iface.messageBar().pushCritical("", msg)
            return False

        return True

    def check_required_layers(self) -> bool:
        missing_layers = []
        for layer in code_layers + plan_layers:
            if not layer.exists():
                missing_layers.append(layer.name)  # noqa: PERF401
        if len(missing_layers) > 0:  # noqa: SIM103
            # iface.messageBar().pushWarning("", f"Project is missing required layers: {', '.join(missing_layers)}")
            return False
        return True

    def cache_code_layers(self):
        # Cannot cache code layers if layers are not present
        if not self.check_required_layers():
            return

        @use_wait_cursor
        def _cache_code_layers():
            PlanRegulationTypeLayer.build_cache()
            AdditionalInformationTypeLayer.build_cache()

        _cache_code_layers()

    def initialize_libraries(self):
        self._initialize_regulation_group_libraries()
        self._initialize_plan_feature_libraries()

    def _initialize_regulation_group_libraries(self):
        # Cannot initialize regulation group librarires if regulation layer is not found
        if not self.check_required_layers():
            return

        self.regulation_group_libraries: list[RegulationGroupLibrary] = []
        self.regulation_group_libraries = [
            RegulationGroupLibrary.from_template_dict(
                data=TemplateManager.read_library_config_file(file_path, "regulation_group"),
                library_type=RegulationGroupLibrary.LibraryType.DEFAULT,
                file_path=str(file_path),
            )
            for file_path in get_default_regulation_group_library_config_files()
        ]
        self.regulation_group_libraries.extend(
            RegulationGroupLibrary.from_template_dict(
                data=TemplateManager.read_library_config_file(file_path, "regulation_group"),
                library_type=RegulationGroupLibrary.LibraryType.CUSTOM,
                file_path=str(file_path),
            )
            for file_path in get_user_regulation_group_library_config_files()
        )

    def _initialize_plan_feature_libraries(self):
        """Make sure regulation group libraries are updated before initializing plan feature libraries."""
        self.plan_feature_libraries = [
            PlanFeatureLibrary.from_template_dict(
                data=TemplateManager.read_library_config_file(file_path, "plan_feature"),
                library_type=PlanFeatureLibrary.LibraryType.CUSTOM,
                file_path=str(file_path),
            )
            for file_path in get_user_plan_feature_library_config_files()
        ]
        self.new_feature_dock.initialize_plan_feature_libraries(self.plan_feature_libraries)

    def open_manage_plans(self):
        dialog = ManagePlans(self.regulation_group_libraries)
        if dialog.exec():
            selected_plan = dialog.selected_plan
            # If the active plan was changed, update state
            if selected_plan.id_ and selected_plan.id_ != get_active_plan_id():
                self.set_active_plan(selected_plan.id_)

    def open_import_plan_dialog(self):
        dialog = ImportPlanForm(iface.mainWindow())
        if dialog.exec_() and dialog.imported_plan_id:
            self.set_active_plan(dialog.imported_plan_id)

    def open_import_features_dialog(self):
        import_features_form = ImportFeaturesForm(
            self.regulation_group_libraries, self.active_plan_regulation_group_library
        )
        if import_features_form.exec_():
            pass

    def update_active_plan_regulation_group_library(self):
        self.active_plan_regulation_group_library = regulation_group_library_from_active_plan()
        self.regulation_groups_dock.update_regulation_groups(self.active_plan_regulation_group_library)

    def create_new_regulation_group(self):
        self._open_regulation_group_form(RegulationGroup())

    def edit_regulation_group(self, regulation_group: RegulationGroup):
        self._open_regulation_group_form(regulation_group)

    def manage_libraries(self):
        manage_libraries_form = ManageLibrariesForm(self.regulation_group_libraries, self.plan_feature_libraries)
        result = manage_libraries_form.exec_()
        # Even if user clicked cancel, we retrieve the list of updated libraries in case a library was deleted
        updated_regulation_group_libraries = (
            manage_libraries_form.regulation_group_library_widget.get_current_libraries()
        )
        updated_plan_feature_libraries = manage_libraries_form.plan_feature_library_widget.get_current_libraries()
        if result:
            # Rewrite all new and remaining library config files and reinitialize libraries
            for library in updated_regulation_group_libraries:
                TemplateManager.write_regulation_group_template_file(
                    library.into_template_dict(), Path(library.file_path), overwrite=True
                )
            for library in updated_plan_feature_libraries:
                TemplateManager.write_plan_feature_template_file(
                    library.into_template_dict(), Path(library.file_path), overwrite=True
                )
        set_user_regulation_group_library_config_files(
            library.file_path for library in updated_regulation_group_libraries
        )
        set_user_plan_feature_library_config_files(library.file_path for library in updated_plan_feature_libraries)
        self.initialize_libraries()

    def _open_regulation_group_form(self, regulation_group: RegulationGroup):
        regulation_group_form = PlanRegulationGroupForm(regulation_group, self.active_plan_regulation_group_library)

        if regulation_group_form.exec_():
            model = regulation_group_form.model
            if save_regulation_group(model) is None:
                return None
            # NOTE: Should we reinitialize regulation group dock even if saving failed?
            self.update_active_plan_regulation_group_library()
            return model

        return None

    def delete_regulation_groups(self, groups: Iterable[RegulationGroup]):
        groups_changed = False
        for group in groups:
            if delete_regulation_group(group):
                groups_changed = True

        if groups_changed:
            self.update_active_plan_regulation_group_library()

    def remove_all_regulation_groups_from_features(self, features: list[tuple[str, Generator[str]]]):
        for feat_layer_name, feat_ids in features:
            for feat_id in feat_ids:
                for association in RegulationGroupAssociationLayer.get_associations_for_feature(
                    feat_id, feat_layer_name
                ):
                    if not delete_feature(
                        association,
                        RegulationGroupAssociationLayer.get_from_project(),
                        "Kaavamääräysryhmän assosiaation poisto",
                    ):
                        iface.messageBar().pushCritical("", "Kaavamääräysryhmän assosiaation poistaminen epäonnistui.")

    def add_regulation_groups_to_features(
        self, groups: list[RegulationGroup], features: list[tuple[str, Generator[str]]]
    ):
        for feat_layer_name, feat_ids in features:
            for feat_id in feat_ids:
                for group in groups:
                    save_regulation_group_association(cast(str, group.id_), feat_layer_name, feat_id)

    def remove_selected_regulation_groups_from_features(
        self, groups: list[RegulationGroup], features: list[tuple[str, Generator[str]]]
    ):
        group_ids = [cast(str, group.id_) for group in groups]
        for feat_layer_name, feat_ids in features:
            for feat_id in feat_ids:
                for association in RegulationGroupAssociationLayer.get_associations_for_feature(
                    feat_id, feat_layer_name
                ):
                    if association["plan_regulation_group_id"] in group_ids:  # noqa: SIM102
                        if not delete_feature(
                            association,
                            RegulationGroupAssociationLayer.get_from_project(),
                            "Kaavamääräysryhmän assosiaation poisto",
                        ):
                            iface.messageBar().pushCritical(
                                "", "Kaavamääräysryhmän assosiaation poistaminen epäonnistui."
                            )

    def toggle_identify_plan_features(self, activate: bool):  # noqa: FBT001
        if activate:
            self.previous_map_tool = iface.mapCanvas().mapTool()
            iface.mapCanvas().setMapTool(self.inspect_plan_feature_tool)
        else:
            iface.mapCanvas().setMapTool(self.previous_map_tool)

    def initialize_feature_digitize_map_tool(self, layer: QgsVectorLayer | None = None):
        # Get matcing capture mode for given layer
        if layer is None:
            mode = PlanFeatureDigitizeMapTool.CaptureMode.CaptureNone
        elif layer.geometryType() == QgsWkbTypes.PointGeometry:
            mode = PlanFeatureDigitizeMapTool.CaptureMode.CapturePoint
        elif layer.geometryType() == QgsWkbTypes.LineGeometry:
            mode = PlanFeatureDigitizeMapTool.CaptureMode.CaptureLine
        elif layer.geometryType() == QgsWkbTypes.PolygonGeometry:
            mode = PlanFeatureDigitizeMapTool.CaptureMode.CapturePolygon

        # Disconnect signals first to not trigger them unwantedly
        if self.feature_digitize_map_tool:
            disconnect_signal(self.feature_digitize_map_tool.digitizingCompleted)
            disconnect_signal(self.feature_digitize_map_tool.digitizingFinished)

        # Reinitialize and reconnect signals
        self.feature_digitize_map_tool = PlanFeatureDigitizeMapTool(mode)
        self.feature_digitize_map_tool.digitizingCompleted.connect(self._plan_feature_geom_digitized)
        self.feature_digitize_map_tool.digitizingFinished.connect(self.new_feature_dock.deactivate_and_clear_selections)

        # Set layer if given
        if layer:
            self.feature_digitize_map_tool.setLayer(layer)

    # check this
    def digitize_plan_geometry(self):
        self.previous_map_tool = iface.mapCanvas().mapTool()
        self.previous_active_plan_id = get_active_plan_id()

        if not handle_unsaved_changes():
            return

        plan_layer = PlanLayer.get_from_project()
        if not plan_layer:
            return
        self.previously_editable = plan_layer.isEditable()

        self.set_active_plan(None)

        iface.setActiveLayer(plan_layer)
        plan_layer.startEditing()
        self.plan_digitize_map_tool.setLayer(plan_layer)
        iface.mapCanvas().setMapTool(self.plan_digitize_map_tool)

    def import_plan_geometry(self):
        plan_layer = PlanLayer.get_from_project()
        if not plan_layer:
            return
        self.previously_editable = plan_layer.isEditable()
        self.previous_active_plan_id = get_active_plan_id()
        self.previous_map_tool = iface.mapCanvas().mapTool()

        layer: QgsVectorLayer = iface.activeLayer()
        plan_layer_names = [plan_layer.name for plan_layer in plan_layers]
        if layer.name() in plan_layer_names:
            iface.messageBar().pushWarning("", "Kaavan ulkorajaa ei voi tuoda ARHOn tasoilta.")
            return
        if layer.geometryType() != QgsWkbTypes.PolygonGeometry:
            iface.messageBar().pushWarning("", "Kaavan ulkorajaksi valittu geometria ei ole polygoni.")
            return
        features = layer.selectedFeatures()
        if not features:
            iface.messageBar().pushWarning("", "Ei valittuja kohteita kaavan ulkorajaksi.")
            return

        plan_saved = self._plan_geom_ready(features)
        if plan_saved:
            set_imported_layer_invisible(layer)

    def edit_plan(self):
        plan_layer = PlanLayer.get_from_project()
        if not plan_layer:
            return

        feature = PlanLayer.get_feature_by_id(get_active_plan_id(), no_geometries=False)
        if feature is None:
            iface.messageBar().pushWarning("", "Mikään kaava ei ole avattuna.")
            return
        plan_model = PlanLayer.model_from_feature(feature)

        attribute_form = PlanAttributeForm(plan_model, self.regulation_group_libraries)
        if attribute_form.exec_():
            plan_id = save_plan(attribute_form.model)
            if plan_id is not None:
                self.update_active_plan_regulation_group_library()

    def edit_plan_matter(self):
        plan_matter_layer = PlanMatterLayer.get_from_project()
        if not plan_matter_layer:
            return

        feature = PlanMatterLayer.get_feature_by_id(get_active_plan_matter_id(), no_geometries=True)
        if feature is None:
            iface.messageBar().pushWarning("", "Ei aktiivista kaava-asiaa.")
            return
        plan_matter_model = PlanMatterLayer.model_from_feature(feature)

        attribute_form = PlanMatterAttributeForm(plan_matter_model)
        if attribute_form.exec_():
            save_plan_matter(attribute_form.model)

    def new_plan_matter(self):
        """Creates and saves a new geometryless Plan Matter feature."""

        # Handle unsaved changes first
        if not handle_unsaved_changes():
            return

        # Get the layer
        plan_matter_layer = PlanMatterLayer.get_from_project()
        if not plan_matter_layer:
            iface.messageBar().pushWarning("", "Kaava-asia tasoa ei löytynyt projektista.")
            return

        self.previously_editable = plan_matter_layer.isEditable()

        iface.setActiveLayer(plan_matter_layer)

        if not plan_matter_layer.isEditable():
            plan_matter_layer.startEditing()

        plan_matter_model = PlanMatter()
        attribute_form = PlanMatterAttributeForm(plan_matter_model, parent=iface.mainWindow())

        if attribute_form.exec_():
            saved_id = save_plan_matter(attribute_form.model)

            self.set_active_plan_matter(saved_id)

    def edit_lifecycles(self):
        plan_layer = PlanLayer.get_from_project()
        if not plan_layer:
            return

        feature = PlanLayer.get_feature_by_id(get_active_plan_id(), no_geometries=False)
        if feature is None:
            return
        plan_model = PlanLayer.model_from_feature(feature)

        lifecycle_editor = LifecycleEditor(plan=plan_model)

        if lifecycle_editor.exec_():
            save_plan(plan_model)

    def add_new_plan_feature(self):
        if not handle_unsaved_changes():
            return

        layer_name = self.new_feature_dock.active_feature_layer
        if layer_name is None:
            msg = "No plan feature type selected"
            iface.messageBar().pushWarning("", msg)
            return

        layer_class = FEATURE_LAYER_NAME_TO_CLASS_MAP.get(layer_name)
        if not layer_class:
            msg = f"Could not find plan feature layer class for layer name {layer_name}"
            raise ValueError(msg)
        layer = layer_class.get_from_project()

        iface.setActiveLayer(layer)
        layer.startEditing()

        self.initialize_feature_digitize_map_tool(layer)
        iface.mapCanvas().setMapTool(self.feature_digitize_map_tool)

    def _plan_geom_ready(self, features: QgsFeature | list[QgsFeature]) -> bool:
        """Callback for when new feature(s) is added to the Kaava layer."""
        plan_layer = PlanLayer.get_from_project()
        if not plan_layer:
            return False

        if isinstance(features, QgsFeature):
            geom = features.geometry()
        else:
            geom = QgsGeometry.unaryUnion([feature.geometry() for feature in features if feature.geometry()])

        plan_model = Plan(geom=geom)
        attribute_form = PlanAttributeForm(plan_model, self.regulation_group_libraries)
        if attribute_form.exec_():
            plan_id = save_plan(attribute_form.model)
            if plan_id is not None:
                plan_to_be_activated = plan_id
                plan_saved = True
            else:
                plan_to_be_activated = self.previous_active_plan_id
                plan_saved = False
        else:
            plan_to_be_activated = self.previous_active_plan_id
            plan_saved = False

        self.set_active_plan(plan_to_be_activated)

        if self.previously_editable:
            plan_layer.startEditing()

        iface.mapCanvas().setMapTool(self.previous_map_tool)

        return plan_saved

    def _plan_feature_geom_digitized(self, feature: QgsFeature):
        # NOTE: What if user has changed dock selections while digitizng?
        if self.new_feature_dock.active_template:
            plan_feat_template = self.new_feature_dock.active_template
            plan_feature = PlanObject(
                type_of_underground_id=plan_feat_template.type_of_underground_id,
                layer_name=plan_feat_template.layer_name,
                name=plan_feat_template.name,
                description=plan_feat_template.description,
                regulation_groups=plan_feat_template.regulation_groups,  # Check if ok
            )
            title = plan_feature.name
        else:
            plan_feature = PlanObject(layer_name=self.new_feature_dock.active_feature_layer)
            title = self.new_feature_dock.active_feature_type

        plan_feature.geom = feature.geometry()
        attribute_form = PlanObjectForm(
            plan_feature,
            title if title else "",
            self.regulation_group_libraries,
            self.active_plan_regulation_group_library,
        )
        if attribute_form.exec_() and save_plan_feature(attribute_form.model) is not None:
            self.update_active_plan_regulation_group_library()

    def edit_plan_feature(self, feature: QgsFeature, layer_name: str):
        layer_class = FEATURE_LAYER_NAME_TO_CLASS_MAP[layer_name]
        plan_feature = layer_class.model_from_feature(feature)

        title = plan_feature.name if plan_feature.name else layer_name
        attribute_form = PlanObjectForm(
            plan_feature, title, self.regulation_group_libraries, self.active_plan_regulation_group_library
        )
        if attribute_form.exec_() and save_plan_feature(attribute_form.model) is not None:
            self.update_active_plan_regulation_group_library()

    def set_active_plan_matter(self, plan_matter_id: str) -> None:
        if check_layer_changes():
            raise UnsavedChangesError

        plan_matter_layer = PlanMatterLayer.get_from_project()
        previously_in_edit_mode = plan_matter_layer.isEditable()
        if previously_in_edit_mode:
            plan_matter_layer.rollBack()

        set_active_plan_matter_id(plan_matter_id)

        # Plan matter filtering
        if plan_matter_id:
            self.plan_matter_set.emit()
            for layer in plan_matter_layers:
                layer.filter_layer_by_plan_matter_id(plan_matter_id)
        else:
            for layer in plan_matter_layers:
                layer.hide_all_features()
            self.plan_matter_unset.emit()

        self.set_active_plan(None)
        PlanLayer.hide_all_features()

        if previously_in_edit_mode:
            plan_matter_layer.startEditing()

        permanent_plan_identifier = PlanMatterLayer.get_attribute_by_id("permanent_plan_identifier", plan_matter_id)
        if QgsVariantUtils.isNull(permanent_plan_identifier):
            permanent_plan_identifier = None

        self.set_permanent_identifier(permanent_plan_identifier)

    def set_active_plan(self, plan_id: str | None) -> None:
        """Update the project layers based on the selected land use plan and its plan matter.

        Layers to be filtered cannot be in edit mode.
        This method disables edit mode temporarily if needed.
        Therefore if there are unsaved changes, this method will raise an exception.
        """

        if check_layer_changes():
            raise UnsavedChangesError

        plan_layer = PlanLayer.get_from_project()
        previously_in_edit_mode = plan_layer.isEditable()
        if previously_in_edit_mode:
            plan_layer.rollBack()

        set_active_plan_id(plan_id)
        if plan_id:
            self.plan_set.emit()
            for layer in plan_layers:
                if layer.filter_template:
                    layer.filter_layer_by_plan_id(plan_id)
                else:
                    layer.show_all_features()
        else:
            self.plan_unset.emit()
            for layer in plan_layers:
                if layer.name == "Kaava":
                    layer.show_all_features()
                else:
                    layer.hide_all_features()

        if previously_in_edit_mode:
            plan_layer.startEditing()

        self.update_active_plan_regulation_group_library()
        self.features_dock.create_plan_feature_view()

        if plan_id:
            for feature_layer in plan_feature_layers:
                layer = feature_layer.get_from_project()
                _apply_style(layer)
            self.zoom_to_active_plan()

    def zoom_to_active_plan(self):
        """Zoom to the active plan layer."""
        active_plan_feature = next(PlanLayer.get_features(), None)
        if active_plan_feature:
            bounding_box = active_plan_feature.geometry().boundingBox()
            canvas = iface.mapCanvas()
            canvas.zoomToFeatureExtent(bounding_box.buffered(50))
            canvas.refresh()

    def load_plan(self):
        """Load an existing land use plan using a dialog selection."""
        connection_names = get_existing_database_connection_names()

        if not connection_names:
            iface.messageBar().pushCritical("", "Tietokantayhteyksiä ei löytynyt.")
            return

        if not handle_unsaved_changes():
            return

        dialog = LoadPlanDialog(None, connection_names)

        if dialog.exec_() == QDialog.Accepted:
            selected_plan_id = dialog.get_selected_plan_id()
            self.commit_all_editable_layers()

            self.set_active_plan(selected_plan_id)

    def load_plan_matter(self):
        """Load an existing plan matter using a dialog selection."""
        connection_names = get_existing_database_connection_names()

        if not connection_names:
            iface.messageBar().pushCritical("", "Tietokantayhteyksiä ei löytynyt.")
            return

        if not handle_unsaved_changes():
            return

        dialog = LoadPlanMatterDialog(None, connection_names)

        if dialog.exec_() == QDialog.Accepted:
            selected_plan_matter_id = dialog.get_selected_plan_matter_id()
            self.set_active_plan_matter(selected_plan_matter_id)

    def commit_all_editable_layers(self):
        """Commit all changes in any editable layers."""
        for layer in QgsProject.instance().mapLayers().values():
            if isinstance(layer, QgsVectorLayer) and layer.isEditable():
                layer.commitChanges()

    def export_plan(self):
        """Starts the plan export process

        Calls async export_plan method of lambda services.
        The plan_data_received signal is emitted when response is received."""
        plan_id = get_active_plan_id()
        if not plan_id:
            iface.messageBar().pushWarning("", "Mikään kaava ei ole avattuna.")
            return

        dialog = SerializePlan()
        if dialog.exec_() == QDialog.Accepted:
            self.json_plan_path = str(dialog.plan_file.filePath())
            self.json_plan_outline_path = str(dialog.plan_outline_file.filePath())

            self.lambda_service.export_plan(plan_id)

    def export_plan_matter(self):
        """Starts the plan matter export process

        Calls async export_plan_matter method of lambda services.
        The plan_matter_data_received signal is emitted when response is received."""
        plan_id = get_active_plan_id()
        if not plan_id:
            iface.messageBar().pushWarning("", "Mikään kaava ei ole avattuna.")
            return

        dialog = SerializePlanMatter()
        if dialog.exec_() == QDialog.Accepted:
            self.json_plan_matter_path = str(dialog.plan_matter_file.filePath())

            self.lambda_service.export_plan_matter(plan_id)

    def get_permanent_plan_identifier(self):
        """Gets the permanent plan identifier for the active plan."""
        plan_matter_id = get_active_plan_matter_id()
        if not plan_matter_id:
            iface.messageBar().pushWarning("", "Mikään kaava-asia ei ole aktiivisena.")
            return
        if not PlanMatterLayer.get_plan_matter_producers_plan_identifier(plan_matter_id):
            iface.messageBar().pushCritical(
                "VIRHE",
                "Kaava-asialta puuttuu tuottajan kaavatunnus, joka vaaditaan pysyvän kaavatunnuksen hakemista varten.",
            )
            return

        self.lambda_service.get_permanent_identifier(get_active_plan_id())

    def set_permanent_identifier(self, identifier):
        QgsExpressionContextUtils.setProjectVariable(QgsProject.instance(), "permanent_identifier", identifier)
        self.plan_identifier_set.emit(identifier)

    def save_exported_plan(self, plan_data: dict, outline_data: dict):
        """This slot saves the plan and outline data to JSON files."""
        if plan_data is None or outline_data is None:
            iface.messageBar().pushCritical("", "Kaavaa tai sen ulkorajaa ei löytynyt.")
            return

        # Retrieve paths
        if self.json_plan_path is None or self.json_plan_outline_path is None:
            iface.messageBar().pushCritical("", "Tiedostopolut eivät ole saatavilla.")
            return

        # Save the JSONs
        with open(self.json_plan_path, "w", encoding="utf-8") as full_file:
            json.dump(plan_data, full_file, ensure_ascii=False, indent=2)

        with open(self.json_plan_outline_path, "w", encoding="utf-8") as outline_file:
            json.dump(outline_data, outline_file, ensure_ascii=False, indent=2)

        iface.messageBar().pushSuccess("", "Kaava ja kaavan ulkoraja tallennettu.")

    def save_exported_plan_matter(self, plan_matter_data):
        """Saves the plan matter data to a JSON file."""
        if plan_matter_data is None:
            iface.messageBar().pushCritical("", "Kaava-asiaa ei löytynyt.")
            return

        # Retrieve path
        if self.json_plan_matter_path is None:
            iface.messageBar().pushCritical("", "Tiedostopolku ei ole saatavilla.")
            return

        # Save the JSON
        with open(self.json_plan_matter_path, "w", encoding="utf-8") as file:
            json.dump(plan_matter_data, file, ensure_ascii=False, indent=2)

        iface.messageBar().pushSuccess("", "Kaava-asia tallennettu.")

    def on_project_loaded(self):
        if QgsProject.instance().fileName() == "":
            # No project is open. Ignoring signal.
            return

        self.initialize_from_project()
        self.features_dock.initialize()

        if self.check_compatible_project_version() and self.check_required_layers():
            QgsProject.instance().cleared.connect(self.on_project_cleared)
            self.project_loaded.emit()

            active_plan_matter_id = get_active_plan_matter_id()
            active_plan_id = get_active_plan_id()

            if active_plan_matter_id:
                self.set_active_plan_matter(active_plan_matter_id)
            if active_plan_id:
                self.set_active_plan(active_plan_id)

    def on_project_cleared(self):
        QgsProject.instance().cleared.disconnect(self.on_project_cleared)

        self.project_cleared.emit()

    def unload(self):
        # Set pan map tool as active (to deactivate our custom tools to avoid errors)
        iface.actionPan().trigger()

        # Lambda service
        disconnect_signal(self.lambda_service.plan_data_received)
        disconnect_signal(self.lambda_service.plan_matter_data_received)
        self.lambda_service.deleteLater()

        # Feature digitize tool
        if self.feature_digitize_map_tool:
            disconnect_signal(self.feature_digitize_map_tool.digitizingCompleted)
            disconnect_signal(self.feature_digitize_map_tool.digitizingFinished)
            self.feature_digitize_map_tool.deleteLater()

        # Plan digitize tool
        disconnect_signal(self.plan_digitize_map_tool.digitizingCompleted)
        self.plan_digitize_map_tool.deleteLater()

        # Inspect plan feature tool
        self.inspect_plan_feature_tool.unload()
        self.inspect_plan_feature_tool.deleteLater()

        # New feature dock
        disconnect_signal(self.new_feature_dock.tool_activated)
        iface.removeDockWidget(self.new_feature_dock)
        self.new_feature_dock.deleteLater()

        # Regulation group dock
        self.regulation_groups_dock.unload()
        iface.removeDockWidget(self.regulation_groups_dock)
        self.regulation_groups_dock.deleteLater()

        # Plan features dock
        self.features_dock.unload()
        iface.removeDockWidget(self.features_dock)
        self.features_dock.deleteLater()

        disconnect_signal(self.plan_set)


def regulation_group_library_from_active_plan() -> RegulationGroupLibrary:
    if get_active_plan_id():
        id_of_general_regulation_group_type = (
            PlanRegulationGroupTypeLayer.get_attribute_value_by_another_attribute_value(
                "id", "value", "generalRegulations"
            )
        )
        iterator = RegulationGroupLayer.get_features()
        features = [
            feat for feat in iterator if feat["type_of_plan_regulation_group_id"] != id_of_general_regulation_group_type
        ]
        regulation_groups = RegulationGroupLayer.models_from_features(features)
    else:
        regulation_groups = []

    return RegulationGroupLibrary(
        name="Käytössä olevat kaavamääräysryhmät",
        file_path=None,
        version=None,
        description=None,
        library_type=RegulationGroupLibrary.LibraryType.ACTIVE_PLAN,
        regulation_groups=regulation_groups,
    )


def _apply_style(layer: QgsVectorLayer) -> None:
    active_plan_matter = PlanMatterLayer.get_feature_by_id(get_active_plan_matter_id(), no_geometries=False)
    if not active_plan_matter:
        return
    plan_type = PlanTypeLayer.get_plan_type(active_plan_matter["plan_type_id"])
    if plan_type == PlanType.REGIONAL:
        path = plugin_path("resources", "styles", "maakuntakaava")
    elif plan_type == PlanType.GENERAL:
        path = plugin_path("resources", "styles", "yleiskaava")
    elif plan_type == PlanType.TOWN:
        path = plugin_path("resources", "styles", "asemakaava")
    else:
        return

    # Apply style to temp layer and copy symbology and labels from there to the actual layer
    geom_type = QgsWkbTypes.displayString(layer.wkbType())
    crs = layer.crs().authid()
    temp_layer = QgsVectorLayer(f"{geom_type}?crs={crs}", "temp_layer", "memory")
    msg, result = temp_layer.loadNamedStyle(os.path.join(path, QML_MAP[layer.name()]))
    if not result:
        iface.messageBar().pushCritical("", msg)
        return
    layer.setRenderer(temp_layer.renderer().clone())
    layer.setLabeling(temp_layer.labeling().clone())
    layer.setLabelsEnabled(True)

    layer.triggerRepaint()
