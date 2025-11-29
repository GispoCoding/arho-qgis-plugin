from __future__ import annotations

import os
from typing import TYPE_CHECKING, Callable

from qgis.core import QgsApplication, QgsExpressionContextUtils, QgsProject
from qgis.PyQt.QtCore import QCoreApplication, Qt, QTranslator
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QMenu, QToolButton, QWidget

from qgis.core import Qgis, QgsMessageLog

from arho_feature_template.core.geotiff_creator import GeoTiffCreator
from arho_feature_template.core.plan_manager import PlanManager
from arho_feature_template.core.settings_manager import SettingsManager
from arho_feature_template.gui.dialogs.plugin_about import PluginAbout
from arho_feature_template.gui.dialogs.plugin_settings import ArhoOptionsPageFactory
from arho_feature_template.gui.dialogs.post_plan import PostPlanDialog
from arho_feature_template.gui.docks.validation_dock import ValidationDock
from arho_feature_template.qgis_plugin_tools.tools.custom_logging import setup_logger, teardown_logger
from arho_feature_template.qgis_plugin_tools.tools.i18n import setup_translation, tr
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
        self.locale, file_path = setup_translation()
        if file_path:
            self.translator = QTranslator()
            self.translator.load(file_path)
            # noinspection PyCallByClass
            QCoreApplication.installTranslator(self.translator)
        else:
            pass
        self.actions: list[QAction] = []
        self.menu = Plugin.name

        # QgsMessageLog.logMessage(self.locale, 'ARHO', level=Qgis.Info)

        if self.locale == 'fi':
            self.toolbar = iface.addToolBar("ARHO Työkalupalkki")
        elif self.locale == 'en_US':
            self.toolbar = iface.addToolBar("ARHO Toolbar")
        else:
            self.toolbar = iface.addToolBar(tr("ARHO Työkalupalkki"))
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

        # QgsMessageLog.logMessage(self.locale, 'ARHO', level=Qgis.Info)

        # Actions

        #####  PLAN MATTER  #####
        
        if self.locale == 'fi':
            plan_matter_text = "Kaava-asia "
            new_plan_matter_text = "Uusi kaava-asia"
            create_new_plan_matter_text = "Luo uusi kaava-asia"
            open_plan_matter_text = "Avaa kaava-asia"
            load_plan_matter_text = "Lataa/avaa kaava-asia"
            plan_matter_attributes_text = "Kaava-asian tiedot"
            edit_active_plan_matter_attributes_text = "Muokkaa aktiivisen kaava-asian tietoja"
            save_plan_matter_json_text = "Tallenna kaava-asian JSON"
            save_plan_matter_json_text_tip = "Tallenna aktiivisen kaavan kaava-asia JSON muodossa"
            fetch_permanent_plan_identifier_text = "Hae pysyvä kaavatunnus"
            fetch_permanent_plan_identifier_text_tip = "Hae kaavalle pysyvä kaavatunnus"
            send_plan_matter_text = "Lähetä kaava-asia Ryhtiin"
            send_plan_matter_text_tip = "Lähetä kaava-asia Ryhtiin"
        elif self.locale == 'en_US':
            plan_matter_text = "Plan matter "
            new_plan_matter_text = "New plan matter"
            create_new_plan_matter_text = "Create new plan matter"
            open_plan_matter_text = "Open plan matter"
            load_plan_matter_text = "Load/open plan matter"
            plan_matter_attributes_text = "Plan matter attributes"
            edit_active_plan_matter_attributes_text = "Edit attributes of the active plan matter"
            save_plan_matter_json_text = "Save plan matter JSON"
            save_plan_matter_json_text_tip = "Save the plan matter of the active plan scheme in JSON format"
            fetch_permanent_plan_identifier_text = "Retrieve permanent plan identifier"
            fetch_permanent_plan_identifier_text_tip = "Retrieve permanent plan identifier for the plan scheme"
            send_plan_matter_text = "Send plan matter to Ryhti"
            send_plan_matter_text_tip = "Send plan matter to Ryhti"
        else:
            plan_matter_text = tr("Kaava-asia ")
            new_plan_matter_text = tr("Uusi kaava-asia")
            create_new_plan_matter_text = tr("Luo uusi kaava-asia")
            open_plan_matter_text = tr("Avaa kaava-asia")
            load_plan_matter_text = tr("Lataa/avaa kaava-asia")
            plan_matter_attributes_text = tr("Kaava-asian tiedot")
            edit_active_plan_matter_attributes_text = tr("Muokkaa aktiivisen kaava-asian tietoja")
            save_plan_matter_json_text = tr("Tallenna kaava-asian JSON")
            save_plan_matter_json_text_tip = tr("Tallenna aktiivisen kaavan kaava-asia JSON muodossa")
            fetch_permanent_plan_identifier_text = tr("Hae pysyvä kaavatunnus")
            fetch_permanent_plan_identifier_text_tip = tr("Hae kaavalle pysyvä kaavatunnus")
            send_plan_matter_text = tr("Lähetä kaava-asia Ryhtiin")
            send_plan_matter_text_tip = tr("Lähetä kaava-asia Ryhtiin")

        self.plan_matter_button = QToolButton()
        self.plan_matter_button.setText(plan_matter_text)
        self.plan_matter_button.setPopupMode(QToolButton.InstantPopup)
        plan_matter_menu = QMenu()
        self.plan_matter_button.setMenu(plan_matter_menu)
        self.plan_matter_action = self.toolbar.addWidget(self.plan_matter_button)

        self.new_plan_matter_action = self.add_action(
            text=new_plan_matter_text,
            icon=QgsApplication.getThemeIcon("mActionAdd.svg"),
            triggered_callback=self.plan_manager.new_plan_matter,
            add_to_menu=True,
            add_to_toolbar=False,
            status_tip=create_new_plan_matter_text,
        )
        plan_matter_menu.addAction(self.new_plan_matter_action)

        self.load_plan_matter_action = self.add_action(
            text=open_plan_matter_text,
            icon=QgsApplication.getThemeIcon("mActionFileOpen.svg"),
            triggered_callback=self.load_existing_plan_matter,
            parent=iface.mainWindow(),
            add_to_menu=True,
            add_to_toolbar=False,
            status_tip=load_plan_matter_text,
        )
        plan_matter_menu.addAction(self.load_plan_matter_action)

        self.edit_plan_matter_action = self.add_action(
            text=plan_matter_attributes_text,
            icon=QgsApplication.getThemeIcon("mActionOpenTable.svg"),
            triggered_callback=self.plan_manager.edit_plan_matter,
            parent=iface.mainWindow(),
            add_to_menu=True,
            add_to_toolbar=False,
            status_tip=edit_active_plan_matter_attributes_text,
        )
        plan_matter_menu.addAction(self.edit_plan_matter_action)

        self.serialize_plan_matter_action = self.add_action(
            text=save_plan_matter_json_text,
            icon=QgsApplication.getThemeIcon("mActionFileSaveAs.svg"),
            triggered_callback=self.export_plan_matter,
            add_to_menu=True,
            add_to_toolbar=False,
            status_tip=save_plan_matter_json_text_tip,
        )
        plan_matter_menu.addAction(self.serialize_plan_matter_action)

        if SettingsManager.get_data_exchange_layer_enabled():
            self.get_permanent_identifier_action = self.add_action(
                text=fetch_permanent_plan_identifier_text,
                triggered_callback=self.plan_manager.get_permanent_plan_identifier,
                add_to_menu=False,
                add_to_toolbar=False,
                status_tip=fetch_permanent_plan_identifier_text_tip,
            )
            self.get_permanent_identifier_action.setEnabled(False)  # Disable action by default
            plan_matter_menu.addAction(self.get_permanent_identifier_action)

            self.post_plan_matter_action = self.add_action(
                text=send_plan_matter_text,
                icon=QgsApplication.getThemeIcon("mActionSharingExport.svg"),
                triggered_callback=self.post_plan_matter,
                add_to_menu=False,
                add_to_toolbar=False,
                status_tip=send_plan_matter_text_tip,
            )
            self.post_plan_matter_action.setEnabled(False)  # Disable action by default
            plan_matter_menu.addAction(self.post_plan_matter_action)

        self.toolbar.addSeparator()

        #####  PLAN  #####
        
        if self.locale == 'fi':
            plan_scheme_text = "Kaavasuunnitelma "
            new_plan_scheme_text = "Uusi kaavasuunnitelma"
            create_new_plan_scheme_by_drawing_text = "Luo uusi kaavasuunnitelma piirtämällä ulkoraja"
            create_new_plan_scheme_by_drawing_text_tip = "Luo uusi kaavasuunnitelman ulkoraja piirtämällä kaavarajaus"
            create_new_plan_scheme_by_importing_text = "Luo uusi kaavasuunnitelma tuomalla ulkoraja"
            create_new_plan_scheme_by_importing_text_tip = "Luo uusi kaavasuunnitelman ulkoraja valitsemalla kaavarajauksen geometria toiselta tasolta"
            plan_schemes_text = "Kaavasuunnitelmat"
            plan_schemes_text_tip = "Näytä kaavasuunnitelmat"
            plan_scheme_attributes_text = "Kaavasuunnitelman tiedot"
            plan_scheme_attributes_text_tip = "Näytä aktiivisen kaavasuunnitelman tiedot"
            import_plan_scheme_text = "Tuo kaavasuunnitelma"
            import_plan_scheme_text_tip = "Tuo kaavasuunnitelman JSON tietokantaan"
            save_plan_scheme_text = "Tallenna kaavasuunnitelma"
            save_plan_scheme_json_text = "Tallenna kaavasuunnitelma JSON"
            save_plan_scheme_json_text_tip = "Tallenna aktiivinen kaavasuunnitelma JSON-muodossa"
            save_plan_map_text = "Tallenna kaavakartta"
            save_plan_map_text_tip = "Tallenna aktiivinen kaavasuunnitelma GeoTIFF-muodossa"
        elif self.locale == 'en_US':
            plan_scheme_text = "Plan scheme "
            new_plan_scheme_text = "New plan scheme"
            create_new_plan_scheme_by_drawing_text = "Create new plan scheme by drawing geographical boundaries"
            create_new_plan_scheme_by_drawing_text_tip = "Create new plan scheme border by drawing the geographical border"
            create_new_plan_scheme_by_importing_text = "Create new plan scheme by importing geographical boundaries"
            create_new_plan_scheme_by_importing_text_tip = "Create new plan scheme border by selecting the plan border geometry from other layer"
            plan_schemes_text = "Plan schemes"
            plan_schemes_text_tip = "Show plan schemes"
            plan_scheme_attributes_text = "Attributes of the plan scheme"
            plan_scheme_attributes_text_tip = "Show attributes of the active plan scheme"
            import_plan_scheme_text = "Import plan scheme"
            import_plan_scheme_text_tip = "Import plan scheme JSON to database"
            save_plan_scheme_text = "Save plan scheme"
            save_plan_scheme_json_text = "Save plan scheme JSON"
            save_plan_scheme_json_text_tip = "Save active plan scheme as JSON"
            save_plan_map_text = "Save plan map"
            save_plan_map_text_tip = "Save active plan scheme in GeoTIFF format"
        else:
            plan_scheme_text = tr("Kaavasuunnitelma ")
            new_plan_scheme_text = tr("Uusi kaavasuunnitelma")
            create_new_plan_scheme_by_drawing_text = tr("Luo uusi kaavasuunnitelma piirtämällä ulkoraja")
            create_new_plan_scheme_by_drawing_text_tip = tr("Luo uusi kaavasuunnitelman ulkoraja piirtämällä kaavarajaus")
            create_new_plan_scheme_by_importing_text = tr("Luo uusi kaavasuunnitelma tuomalla ulkoraja")
            create_new_plan_scheme_by_importing_text_tip = tr("Luo uusi kaavasuunnitelman ulkoraja valitsemalla kaavarajauksen geometria toiselta tasolta")
            plan_schemes_text = tr("Kaavasuunnitelmat")
            plan_schemes_text_tip = tr("Näytä kaavasuunnitelmat")
            plan_scheme_attributes_text = tr("Kaavasuunnitelman tiedot")
            plan_scheme_attributes_text_tip = tr("Näytä aktiivisen kaavasuunnitelman tiedot")
            import_plan_scheme_text = tr("Tuo kaavasuunnitelma")
            import_plan_scheme_text_tip = tr("Tuo kaavasuunnitelman JSON tietokantaan")
            save_plan_scheme_text = tr("Tallenna kaavasuunnitelma")
            save_plan_scheme_json_text = tr("Tallenna kaavasuunnitelma JSON")
            save_plan_scheme_json_text_tip = tr("Tallenna aktiivinen kaavasuunnitelma JSON-muodossa")
            save_plan_map_text = tr("Tallenna kaavakartta")
            save_plan_map_text_tip = tr("Tallenna aktiivinen kaavasuunnitelma GeoTIFF-muodossa")

        self.plan_button = QToolButton()
        self.plan_button.setText(plan_scheme_text)
        self.plan_button.setPopupMode(QToolButton.InstantPopup)
        plan_menu = QMenu()
        self.plan_button.setMenu(plan_menu)
        self.plan_action = self.toolbar.addWidget(self.plan_button)

        self.new_plan_menu = QMenu(new_plan_scheme_text)
        self.new_plan_menu.setIcon(QgsApplication.getThemeIcon("mActionAdd.svg"))
        plan_menu.addMenu(self.new_plan_menu)

        self.draw_new_plan_action = self.add_action(
            text=create_new_plan_scheme_by_drawing_text,
            icon=QIcon(resources_path("icons", "toolbar", "planBorderNew.svg")),
            triggered_callback=self.plan_manager.digitize_plan_geometry,
            add_to_menu=False,
            add_to_toolbar=False,
            status_tip=create_new_plan_scheme_by_drawing_text_tip,
        )
        self.new_plan_menu.addAction(self.draw_new_plan_action)

        self.new_plan_from_border_action = self.add_action(
            text=create_new_plan_scheme_by_importing_text,
            icon=QIcon(resources_path("icons", "toolbar", "planBorderSelect.svg")),
            triggered_callback=self.plan_manager.import_plan_geometry,
            add_to_menu=False,
            add_to_toolbar=False,
            status_tip=create_new_plan_scheme_by_importing_text_tip,
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
            text=plan_schemes_text,
            triggered_callback=self.open_manage_plans,
            add_to_menu=False,
            add_to_toolbar=False,
            status_tip=plan_schemes_text_tip,
        )
        plan_menu.addAction(self.manage_plans_action)

        self.edit_plan_action = self.add_action(
            text=plan_scheme_attributes_text,
            icon=QgsApplication.getThemeIcon("mActionOpenTable.svg"),
            triggered_callback=self.plan_manager.edit_plan,
            parent=iface.mainWindow(),
            add_to_menu=False,
            add_to_toolbar=False,
            status_tip=plan_scheme_attributes_text_tip,
        )
        plan_menu.addAction(self.edit_plan_action)

        self.import_plan_action = self.add_action(
            text=import_plan_scheme_text,
            icon=QgsApplication.getThemeIcon("mActionSharingImport.svg"),
            triggered_callback=self.plan_manager.open_import_plan_dialog,
            add_to_menu=False,
            add_to_toolbar=False,
            status_tip=import_plan_scheme_text_tip,
        )
        plan_menu.addAction(self.import_plan_action)

        self.save_plan_menu = QMenu(save_plan_scheme_text)
        self.save_plan_menu.setIcon(QgsApplication.getThemeIcon("mActionFileSaveAs.svg"))
        plan_menu.addMenu(self.save_plan_menu)

        self.serialize_plan_action = self.add_action(
            text=save_plan_scheme_json_text,
            icon=QgsApplication.getThemeIcon("mActionFileSaveAs.svg"),
            triggered_callback=self.export_plan,
            add_to_menu=False,
            add_to_toolbar=False,
            status_tip=save_plan_scheme_json_text_tip,
        )
        self.save_plan_menu.addAction(self.serialize_plan_action)

        self.create_geotiff_action = self.add_action(
            text=save_plan_map_text,
            icon=QgsApplication.getThemeIcon("mActionAddRasterLayer.svg"),
            triggered_callback=self.create_geotiff,
            add_to_menu=False,
            add_to_toolbar=False,
            status_tip=save_plan_map_text_tip,
        )
        self.save_plan_menu.addAction(self.create_geotiff_action)

        self.toolbar.addSeparator()

        #####  PLAN OBJECTS  #####

        if self.locale == 'fi':
            plan_objects_text = "Kaavakohteet"
            create_plan_object_text = "Luo kaavakohde"
            edit_plan_objects_text = "Muokkaa kaavakohteita"
            import_plan_objects_text = "Tuo kaavakohteita"
            import_plan_objects_text_tip = "Tuo kaavakohteita tietokantaan toisilta vektoritasoilta"
        elif self.locale == 'en_US':
            plan_objects_text = "Plan objects"
            create_plan_object_text = "Create plan object"
            edit_plan_objects_text = "Edit plan objects"
            import_plan_objects_text = "Import plan objects"
            import_plan_objects_text_tip = "Import plan objects to the database from other vector layers"
        else:
            plan_objects_text = tr("Kaavakohteet")
            create_plan_object_text = tr("Luo kaavakohde")
            edit_plan_objects_text = tr("Muokkaa kaavakohteita")
            import_plan_objects_text = tr("Tuo kaavakohteita")
            import_plan_objects_text_tip = tr("Tuo kaavakohteita tietokantaan toisilta vektoritasoilta")

        self.plan_features_dock_action = self.add_action(
            text=plan_objects_text,
            icon=QIcon(resources_path("icons", "toolbar", "planObjectsTable.svg")),
            triggered_callback=lambda _: self.toggle_dock_visibility(self.plan_manager.features_dock),
            add_to_menu=True,
            add_to_toolbar=True,
        )

        self.new_feature_dock_action = self.add_action(
            text=create_plan_object_text,
            icon=QIcon(resources_path("icons", "toolbar", "planObjectsNew.svg")),
            triggered_callback=lambda _: self.toggle_dock_visibility(self.plan_manager.new_feature_dock),
            add_to_menu=True,
            add_to_toolbar=True,
        )

        self.identify_plan_features_action = self.add_action(
            text=edit_plan_objects_text,
            icon=QIcon(resources_path("icons", "toolbar", "planObjectsEdit.svg")),
            toggled_callback=self.plan_manager.toggle_identify_plan_features,
            add_to_menu=False,
            add_to_toolbar=True,
            checkable=True,
        )

        self.import_features_action = self.add_action(
            text=import_plan_objects_text,
            icon=QIcon(resources_path("icons", "toolbar", "planObjectsImport.svg")),
            triggered_callback=self.plan_manager.open_import_features_dialog,
            add_to_menu=False,
            add_to_toolbar=True,
            status_tip=import_plan_objects_text_tip,
        )

        self.toolbar.addSeparator()

        #####  REGULATION GROUPS #####

        if self.locale == 'fi':
            plan_regulation_groups_text = "Kaavamääräysryhmät"
        elif self.locale == 'en_US':
            plan_regulation_groups_text = "Plan regulation groups"
        else:
            plan_regulation_groups_text = tr("Kaavamääräysryhmät")

        self.regulation_groups_dock_action = self.add_action(
            text=plan_regulation_groups_text,
            triggered_callback=lambda _: self.toggle_dock_visibility(self.plan_manager.regulation_groups_dock),
            add_to_menu=True,
            add_to_toolbar=True,
        )

        self.toolbar.addSeparator()

        #####  VALIDATION  #####

        if self.locale == 'fi':
            validation_text = "Validointi"
        elif self.locale == 'en_US':
            validation_text = "Validation"
        else:
            validation_text = tr("Validointi")

        self.validation_dock_action = self.add_action(
            text=validation_text,
            icon=QIcon(resources_path("icons", "toolbar", "kaavan_validointi2.svg")),
            triggered_callback=lambda _: self.toggle_dock_visibility(self.validation_dock),
            add_to_menu=True,
            add_to_toolbar=True,
        )

        #####  LIBRARIES  #####

        if self.locale == 'fi':
            libraries_text = "Kirjastot"
        elif self.locale == 'en_US':
            libraries_text = "Libraries"
        else:
            libraries_text = tr("Kirjastot")

        self.manage_libraries_action = self.add_action(
            text=libraries_text,
            triggered_callback=self.plan_manager.manage_libraries,
            add_to_menu=True,
            add_to_toolbar=True,
        )

        #####  OTHER  #####

        if self.locale == 'fi':
            about_text = "Tietoja"
            about_text_tip = "Tarkastele pluginin tietoja"
            settings_text = "Asetukset"
            settings_text_tip = "Muokkaa pluginin asetuksia"
        elif self.locale == 'en_US':
            about_text = "About"
            about_text_tip = "View about the plugin"
            settings_text = "Settings"
            settings_text_tip = "Edit plugin settings"
        else:
            about_text = tr("Tietoja")
            about_text_tip = tr("Tarkastele pluginin tietoja")
            settings_text = tr("Asetukset")
            settings_text_tip = tr("Muokkaa pluginin asetuksia")

        self.plugin_about = self.add_action(
            text=about_text,
            triggered_callback=self.open_about,
            add_to_menu=True,
            add_to_toolbar=False,
            status_tip=about_text_tip,
        )

        self._arho_options_page_factory = ArhoOptionsPageFactory()
        iface.registerOptionsWidgetFactory(self._arho_options_page_factory)
        self.plugin_settings_action = self.add_action(
            text=settings_text,
            triggered_callback=lambda _: iface.showOptionsDialog(iface.mainWindow(), "ARHO"),
            add_to_menu=True,
            add_to_toolbar=True,
            status_tip=settings_text_tip,
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
            self.get_permanent_identifier_action.setToolTip(tr("Pysyvä kaavatunnus: ") + f"{permanent_identifier}")
            self.post_plan_matter_action.setEnabled(True)
            # self.post_plan_matter_action.setToolTip("Vie kaava-asia Ryhtiin")
        else:
            self.post_plan_matter_action.setEnabled(False)
            # self.post_plan_matter_action.setToolTip("Hae kaavalle ensin pysyvä kaavatunnus")
            self.get_permanent_identifier_action.setEnabled(True)
            self.get_permanent_identifier_action.setToolTip(tr("Hae pysyvä kaavatunnus"))

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
