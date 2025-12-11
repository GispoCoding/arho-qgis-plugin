from __future__ import annotations

import os
from typing import TYPE_CHECKING, Callable

from qgis.core import QgsApplication, QgsExpressionContextUtils, QgsProject
from qgis.PyQt.QtCore import QCoreApplication, Qt, QTranslator
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QMenu, QToolButton, QWidget

from arho_feature_template.core.geotiff_creator import GeoTiffCreator
from arho_feature_template.core.plan_manager import PlanManager
from arho_feature_template.core.prints.regulations_print_generator import RegulationsPrintGenerator
from arho_feature_template.core.settings_manager import SettingsManager
from arho_feature_template.gui.dialogs.plan_object_icon_preview import PlanObjectIconPreview
from arho_feature_template.gui.dialogs.plugin_about import PluginAbout
from arho_feature_template.gui.dialogs.plugin_settings import ArhoOptionsPageFactory
from arho_feature_template.gui.dialogs.post_plan import PostPlanDialog
from arho_feature_template.gui.docks.validation_dock import ValidationDock
from arho_feature_template.qgis_plugin_tools.tools.custom_logging import setup_logger, teardown_logger
from arho_feature_template.qgis_plugin_tools.tools.i18n import setup_translation
from arho_feature_template.qgis_plugin_tools.tools.resources import plugin_name, resources_path
from arho_feature_template.utils.misc_utils import disconnect_signal, iface

if TYPE_CHECKING:
    from qgis.gui import QgsDockWidget


class Plugin:
    """QGIS Plugin Implementation."""

    name = plugin_name()

    def __init__(self) -> None:
        setup_logger(Plugin.name)
        self.digitizing_tool = None

        # initialize locale
        locale, file_path = setup_translation()
        if file_path:
            self.translator = QTranslator()
            self.translator.load(file_path)
            # noinspection PyCallByClass
            QCoreApplication.installTranslator(self.translator)
        else:
            pass
        self.actions: list[QAction] = []
        self.menu = Plugin.name

        self.toolbar = iface.addToolBar("ARHO Toolbar")
        # self.toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

    def check_timezone_variable(self):
        """Check if PGTZ environment variable is correctly set."""

        if os.environ.get("PGTZ") != "Europe/Helsinki":
            iface.messageBar().pushWarning(
                "Varoitus",
                (
                    "Ympäristömuuttuja PGTZ ei ole asetettu arvoon 'Europe/Helsinki'."
                    "Tämä voi johtaa väärään aikavyöhykkeeseen tallennettuihin kellonaikoihin."
                ),
            )

    def add_action(
        self,
        text: str,
        icon: QIcon | None = None,
        triggered_callback: Callable | None = None,
        *,
        toggled_callback: Callable | None = None,
        object_name: str | None = None,
        enabled_flag: bool = True,
        add_to_menu: bool = True,
        add_to_toolbar: bool = True,
        status_tip: str | None = None,
        whats_this: str | None = None,
        parent: QWidget | None = None,
        checkable: bool = False,
    ) -> QAction:
        """Add a toolbar icon to the toolbar.

        :param icon: Icon for this action.

        :param text: Text that should be shown in menu items for this action.

        :param callback: Function to be called when the action is triggered.

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.

        :param parent: Parent widget for the new action. Defaults None.

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """
        if not icon:
            icon = QIcon("")
        action = QAction(icon, text, parent)
        # noinspection PyUnresolvedReferences
        if triggered_callback:
            action.triggered.connect(triggered_callback)

        if toggled_callback:
            action.toggled.connect(toggled_callback)

        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if object_name:
            action.setObjectName(object_name)

        if checkable:
            action.setCheckable(True)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            iface.addPluginToMenu(self.menu, action)

        self.actions.append(action)

        return action

    def initGui(self) -> None:  # noqa N802
        # Plan manager
        self.plan_manager = PlanManager()

        # Docks
        iface.addDockWidget(Qt.RightDockWidgetArea, self.plan_manager.new_feature_dock)

        iface.addDockWidget(Qt.RightDockWidgetArea, self.plan_manager.regulation_groups_dock)
        iface.mainWindow().tabifyDockWidget(
            self.plan_manager.new_feature_dock, self.plan_manager.regulation_groups_dock
        )

        iface.addDockWidget(Qt.RightDockWidgetArea, self.plan_manager.features_dock)
        iface.mainWindow().tabifyDockWidget(self.plan_manager.regulation_groups_dock, self.plan_manager.features_dock)

        self.validation_dock = ValidationDock(self.plan_manager)
        iface.addDockWidget(Qt.RightDockWidgetArea, self.validation_dock)
        iface.mainWindow().tabifyDockWidget(self.plan_manager.new_feature_dock, self.validation_dock)

        # Hide the docks because they cannot be used before a plan has been selected/activated
        self.plan_manager.new_feature_dock.hide()
        self.plan_manager.regulation_groups_dock.hide()
        self.plan_manager.features_dock.hide()
        self.validation_dock.hide()

        # Actions

        #####  PLAN MATTER  #####
        self.plan_matter_button = QToolButton()
        self.plan_matter_button.setText("Kaava-asia ")
        self.plan_matter_button.setPopupMode(QToolButton.InstantPopup)
        plan_matter_menu = QMenu()
        self.plan_matter_button.setMenu(plan_matter_menu)
        self.plan_matter_action = self.toolbar.addWidget(self.plan_matter_button)

        self.new_plan_matter_action = self.add_action(
            text="Uusi kaava-asia",
            icon=QgsApplication.getThemeIcon("mActionAdd.svg"),
            triggered_callback=self.plan_manager.new_plan_matter,
            add_to_menu=True,
            add_to_toolbar=False,
            status_tip="Luo uusi kaava-asia",
        )
        plan_matter_menu.addAction(self.new_plan_matter_action)

        self.load_plan_matter_action = self.add_action(
            text="Avaa kaava-asia",
            icon=QgsApplication.getThemeIcon("mActionFileOpen.svg"),
            triggered_callback=self.load_existing_plan_matter,
            parent=iface.mainWindow(),
            add_to_menu=True,
            add_to_toolbar=False,
            status_tip="Lataa/avaa kaava-asia",
        )
        plan_matter_menu.addAction(self.load_plan_matter_action)

        self.edit_plan_matter_action = self.add_action(
            text="Kaava-asian tiedot",
            icon=QgsApplication.getThemeIcon("mActionOpenTable.svg"),
            triggered_callback=self.plan_manager.edit_plan_matter,
            parent=iface.mainWindow(),
            add_to_menu=True,
            add_to_toolbar=False,
            status_tip="Muokkaa aktiivisen kaava-asian tietoja",
        )
        plan_matter_menu.addAction(self.edit_plan_matter_action)

        self.serialize_plan_matter_action = self.add_action(
            text="Tallenna kaava-asian JSON",
            icon=QgsApplication.getThemeIcon("mActionFileSaveAs.svg"),
            triggered_callback=self.export_plan_matter,
            add_to_menu=True,
            add_to_toolbar=False,
            status_tip="Tallenna aktiivisen kaavan kaava-asia JSON muodossa",
        )
        plan_matter_menu.addAction(self.serialize_plan_matter_action)

        if SettingsManager.get_data_exchange_layer_enabled():
            self.get_permanent_identifier_action = self.add_action(
                text="Hae pysyvä kaavatunnus",
                triggered_callback=self.plan_manager.get_permanent_plan_identifier,
                add_to_menu=False,
                add_to_toolbar=False,
                status_tip="Hae kaavalle pysyvä kaavatunnus",
            )
            self.get_permanent_identifier_action.setEnabled(False)  # Disable action by default
            plan_matter_menu.addAction(self.get_permanent_identifier_action)

            self.post_plan_matter_action = self.add_action(
                text="Lähetä kaava-asia Ryhtiin",
                icon=QgsApplication.getThemeIcon("mActionSharingExport.svg"),
                triggered_callback=self.post_plan_matter,
                add_to_menu=False,
                add_to_toolbar=False,
                status_tip="Lähetä kaava-asia Ryhtiin",
            )
            self.post_plan_matter_action.setEnabled(False)  # Disable action by default
            plan_matter_menu.addAction(self.post_plan_matter_action)

        self.toolbar.addSeparator()

        #####  PLAN  #####
        self.plan_button = QToolButton()
        self.plan_button.setText("Kaavasuunnitelma ")
        self.plan_button.setPopupMode(QToolButton.InstantPopup)
        plan_menu = QMenu()
        self.plan_button.setMenu(plan_menu)
        self.plan_action = self.toolbar.addWidget(self.plan_button)

        self.new_plan_menu = QMenu("Uusi kaavasuunnitelma")
        self.new_plan_menu.setIcon(QgsApplication.getThemeIcon("mActionAdd.svg"))
        plan_menu.addMenu(self.new_plan_menu)

        self.draw_new_plan_action = self.add_action(
            text="Luo uusi kaavasuunnitelma piirtämällä ulkoraja",
            icon=QIcon(resources_path("icons", "toolbar", "planBorderNew.svg")),
            triggered_callback=self.plan_manager.digitize_plan_geometry,
            add_to_menu=False,
            add_to_toolbar=False,
            status_tip="Luo uusi kaavasuunnitelman ulkoraja piirtämällä kaavarajaus",
        )
        self.new_plan_menu.addAction(self.draw_new_plan_action)

        self.new_plan_from_border_action = self.add_action(
            text="Luo uusi kaavasuunnitelma tuomalla ulkoraja",
            icon=QIcon(resources_path("icons", "toolbar", "planBorderSelect.svg")),
            triggered_callback=self.plan_manager.import_plan_geometry,
            add_to_menu=False,
            add_to_toolbar=False,
            status_tip="Luo uusi kaavasuunnitelman ulkoraja valitsemalla kaavarajauksen geometria toiselta tasolta",
        )
        self.new_plan_menu.addAction(self.new_plan_from_border_action)

        # self.new_plan_action = self.add_action(
        #     text="Luo uusi kaavasuunnitelma nykyisestä ulkorajasta",
        #     icon=QIcon(resources_path("icons", "toolbar", "planBorder.svg")),
        #     triggered_callback=self.plan_manager.digitize_plan_geometry,
        #     add_to_menu=False,
        #     add_to_toolbar=False,
        #     status_tip="Luo uusi kaavasuunnitelman käyttämällä nykyistä ulkorajaa",
        # )
        # self.new_plan_menu.addAction(self.new_plan_action)

        self.manage_plans_action = self.add_action(
            text="Kaavasuunnitelmat",
            triggered_callback=self.open_manage_plans,
            add_to_menu=False,
            add_to_toolbar=False,
            status_tip="Näytä kaavasuunnitelmat",
        )
        plan_menu.addAction(self.manage_plans_action)

        self.edit_plan_action = self.add_action(
            text="Kaavasuunnitelman tiedot",
            icon=QgsApplication.getThemeIcon("mActionOpenTable.svg"),
            triggered_callback=self.plan_manager.edit_plan,
            parent=iface.mainWindow(),
            add_to_menu=False,
            add_to_toolbar=False,
            status_tip="Näytä aktiivisen kaavasuunnitelman tiedot",
        )
        plan_menu.addAction(self.edit_plan_action)

        self.import_plan_action = self.add_action(
            text="Tuo kaavasuunnitelma",
            icon=QgsApplication.getThemeIcon("mActionSharingImport.svg"),
            triggered_callback=self.plan_manager.open_import_plan_dialog,
            add_to_menu=False,
            add_to_toolbar=False,
            status_tip="Tuo kaavasuunnitelman JSON tietokantaan",
        )
        plan_menu.addAction(self.import_plan_action)

        self.plan_regulations_print = self.add_action(
            text="Luo tulosteen määräysosa",
            triggered_callback=self.generate_plan_regulations_print,
            add_to_menu=True,
            add_to_toolbar=False,
        )
        plan_menu.addAction(self.plan_regulations_print)

        self.save_plan_menu = QMenu("Tallenna kaavasuunnitelma")
        self.save_plan_menu.setIcon(QgsApplication.getThemeIcon("mActionFileSaveAs.svg"))
        plan_menu.addMenu(self.save_plan_menu)

        self.serialize_plan_action = self.add_action(
            text="Tallenna kaavasuunnitelma JSON",
            icon=QgsApplication.getThemeIcon("mActionFileSaveAs.svg"),
            triggered_callback=self.export_plan,
            add_to_menu=False,
            add_to_toolbar=False,
            status_tip="Tallenna aktiivinen kaavasuunnitelma JSON-muodossa",
        )
        self.save_plan_menu.addAction(self.serialize_plan_action)

        self.create_geotiff_action = self.add_action(
            text="Tallenna kaavakartta",
            icon=QgsApplication.getThemeIcon("mActionAddRasterLayer.svg"),
            triggered_callback=self.create_geotiff,
            add_to_menu=False,
            add_to_toolbar=False,
            status_tip="Tallenna aktiivinen kaavasuunnitelma GeoTIFF-muodossa",
        )
        self.save_plan_menu.addAction(self.create_geotiff_action)

        self.toolbar.addSeparator()

        #####  PLAN OBJECTS  #####
        self.plan_features_dock_action = self.add_action(
            text="Kaavakohteet",
            icon=QIcon(resources_path("icons", "toolbar", "planObjectsTable.svg")),
            triggered_callback=lambda _: self.toggle_dock_visibility(self.plan_manager.features_dock),
            add_to_menu=True,
            add_to_toolbar=True,
        )

        self.new_feature_dock_action = self.add_action(
            text="Luo kaavakohde",
            icon=QIcon(resources_path("icons", "toolbar", "planObjectsNew.svg")),
            triggered_callback=lambda _: self.toggle_dock_visibility(self.plan_manager.new_feature_dock),
            add_to_menu=True,
            add_to_toolbar=True,
        )

        self.identify_plan_features_action = self.add_action(
            text="Muokkaa kaavakohteita",
            icon=QIcon(resources_path("icons", "toolbar", "planObjectsEdit.svg")),
            toggled_callback=self.plan_manager.toggle_identify_plan_features,
            add_to_menu=False,
            add_to_toolbar=True,
            checkable=True,
        )

        self.import_features_action = self.add_action(
            text="Tuo kaavakohteita",
            icon=QIcon(resources_path("icons", "toolbar", "planObjectsImport.svg")),
            triggered_callback=self.plan_manager.open_import_features_dialog,
            add_to_menu=False,
            add_to_toolbar=True,
            status_tip="Tuo kaavakohteita tietokantaan toisilta vektoritasoilta",
        )

        self.toolbar.addSeparator()

        #####  REGULATION GROUPS #####
        self.regulation_groups_dock_action = self.add_action(
            text="Kaavamääräysryhmät",
            triggered_callback=lambda _: self.toggle_dock_visibility(self.plan_manager.regulation_groups_dock),
            add_to_menu=True,
            add_to_toolbar=True,
        )

        self.toolbar.addSeparator()

        #####  VALIDATION  #####
        self.validation_dock_action = self.add_action(
            text="Validointi",
            icon=QIcon(resources_path("icons", "toolbar", "kaavan_validointi2.svg")),
            triggered_callback=lambda _: self.toggle_dock_visibility(self.validation_dock),
            add_to_menu=True,
            add_to_toolbar=True,
        )

        #####  LIBRARIES  #####
        self.manage_libraries_action = self.add_action(
            text="Kirjastot",
            triggered_callback=self.plan_manager.manage_libraries,
            add_to_menu=True,
            add_to_toolbar=True,
        )

        #####  OTHER  #####
        self.plugin_about = self.add_action(
            text="Tietoja",
            triggered_callback=self.open_about,
            add_to_menu=True,
            add_to_toolbar=False,
            status_tip="Tarkastele pluginin tietoja",
        )

        self.plan_object_icons_preview = self.add_action(
            text="Kaavakohdekuvakkaiden esikatselu",
            triggered_callback=self.open_plan_object_icons_preview,
            add_to_menu=True,
            add_to_toolbar=False,
        )

        self._arho_options_page_factory = ArhoOptionsPageFactory()
        iface.registerOptionsWidgetFactory(self._arho_options_page_factory)
        self.plugin_settings_action = self.add_action(
            text="Asetukset",
            triggered_callback=lambda _: iface.showOptionsDialog(iface.mainWindow(), "ARHO"),
            add_to_menu=True,
            add_to_toolbar=True,
            status_tip="Muokkaa pluginin asetuksia",
        )

        self.project_depending_actions = [self.plan_matter_action]
        self.plan_matter_depending_actions = [
            self.edit_plan_matter_action,
            self.serialize_plan_matter_action,
            self.plan_button,
        ]
        self.plan_depending_actions = [
            self.edit_plan_action,
            self.new_feature_dock_action,
            # self.new_plan_action,
            self.plan_features_dock_action,
            self.identify_plan_features_action,
            self.regulation_groups_dock_action,
            self.manage_libraries_action,
            self.validation_dock_action,
            self.save_plan_menu,
            self.import_features_action,
        ]
        if SettingsManager.get_data_exchange_layer_enabled():
            self.plan_depending_actions += [self.get_permanent_identifier_action, self.post_plan_matter_action]

        # Initially actions are disabled because no plan is selected
        self.on_active_plan_matter_unset()
        self.on_active_plan_unset()
        # Check if project opened and if not disable actions
        if not self.plan_manager.check_required_layers():
            self.on_project_cleared()

        # Connect signals
        self.plan_manager.inspect_plan_feature_tool.deactivated.connect(
            lambda: self.identify_plan_features_action.setChecked(False)
        )
        self.plan_manager.plan_set.connect(self.on_active_plan_set)
        self.plan_manager.plan_matter_set.connect(self.on_active_plan_matter_set)
        self.plan_manager.plan_unset.connect(self.on_active_plan_unset)
        self.plan_manager.project_loaded.connect(self.on_project_loaded)
        self.plan_manager.project_cleared.connect(self.on_project_cleared)
        if SettingsManager.get_data_exchange_layer_enabled():
            self.plan_manager.plan_identifier_set.connect(self.update_ryhti_buttons)
        self.plan_manager.plan_identifier_set.connect(self.validation_dock.on_permanent_identifier_set)

        # (Re)initialize whenever a project is opened
        iface.projectRead.connect(self.plan_manager.on_project_loaded)
        # Try initializing the plugin immediately in case the project is already open
        self.plan_manager.on_project_loaded()

        self.check_timezone_variable()

    def toggle_dock_visibility(self, dock_widget: QgsDockWidget):
        if dock_widget.isUserVisible():
            dock_widget.hide()
        else:
            dock_widget.show()
            dock_widget.raise_()

    def load_existing_plan_matter(self):
        self.plan_manager.load_plan_matter()

    def export_plan(self):
        """Export the active plan to json."""
        self.plan_manager.export_plan()

    def open_manage_plans(self):
        self.plan_manager.open_manage_plans()

    def export_plan_matter(self):
        """Export the plan matter of the activate plan."""
        self.plan_manager.export_plan_matter()

    def open_about(self):
        """Open the plugin about dialog."""
        about = PluginAbout()
        about.exec()

    def open_plan_object_icons_preview(self):
        """Open plan object icons preview dialog."""
        preview = PlanObjectIconPreview()
        preview.exec()

    def generate_plan_regulations_print(self):
        RegulationsPrintGenerator.new_regulations_print_layout()

    def create_geotiff(self):
        """Create geotiff from currently active plan."""
        geotiff_creator = GeoTiffCreator()
        geotiff_creator.select_output_file()

    def post_plan_matter(self):
        """Exports plan matter to Ryhti."""
        dialog = PostPlanDialog()
        dialog.exec_()

    def update_ryhti_buttons(self):
        """Update the UI buttons based on whether the active plan has a permanent identifier."""
        permanent_identifier = QgsExpressionContextUtils.projectScope(QgsProject.instance()).variable(
            "permanent_identifier"
        )

        if permanent_identifier:
            self.get_permanent_identifier_action.setEnabled(False)
            self.get_permanent_identifier_action.setToolTip(f"Pysyvä kaavatunnus: {permanent_identifier}")
            self.post_plan_matter_action.setEnabled(True)
            # self.post_plan_matter_action.setToolTip("Vie kaava-asia Ryhtiin")
        else:
            self.post_plan_matter_action.setEnabled(False)
            # self.post_plan_matter_action.setToolTip("Hae kaavalle ensin pysyvä kaavatunnus")
            self.get_permanent_identifier_action.setEnabled(True)
            self.get_permanent_identifier_action.setToolTip("Hae pysyvä kaavatunnus")

    def on_active_plan_matter_set(self):
        for action in self.plan_matter_depending_actions:
            action.setEnabled(True)

    def on_active_plan_matter_unset(self):
        for action in self.plan_matter_depending_actions:
            action.setEnabled(False)

    def on_active_plan_set(self):
        for action in self.plan_depending_actions:
            action.setEnabled(True)

    def on_active_plan_unset(self):
        for action in self.plan_depending_actions:
            action.setEnabled(False)

    def on_project_loaded(self):
        for action in self.project_depending_actions:
            action.setEnabled(True)

    def on_project_cleared(self):
        for action in self.project_depending_actions:
            action.setEnabled(False)
        for action in self.plan_depending_actions:
            action.setEnabled(False)
        for action in self.plan_matter_depending_actions:
            action.setEnabled(False)

    def unload(self) -> None:
        """Removes the plugin menu item and icon from QGIS GUI."""
        # Handle signals
        disconnect_signal(self.plan_manager.new_feature_dock.visibilityChanged)
        iface.projectRead.disconnect()

        # Handle actions
        for action in self.actions:
            iface.removePluginMenu(Plugin.name, action)
            iface.removeToolBarIcon(action)
            action.deleteLater()
        self.actions.clear()

        # Handle toolbar
        iface.mainWindow().removeToolBar(self.toolbar)
        self.toolbar = None

        # Handle plan manager
        self.plan_manager.unload()

        # Handle validation dock
        iface.removeDockWidget(self.validation_dock)
        self.validation_dock.deleteLater()

        # Handle logger
        teardown_logger(Plugin.name)
