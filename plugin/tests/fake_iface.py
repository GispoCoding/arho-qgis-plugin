"""A fake ``QgisInterface`` for running plugin code outside the QGIS application.

``FakeQgisInterface`` subclasses the real ``qgis.gui.QgisInterface``. That gives:

* ``isinstance(iface, QgisInterface)`` holds, and the C++ signals (``projectRead``,
  ``currentLayerChanged``, ``newProjectCreated``, ...) are the real ones with the real
  argument types.
* Every abstract method that is not implemented here raises ``NotImplementedError``
  with a clear message. There is no ``__getattr__`` fallback, so a misspelled name
  raises ``AttributeError`` like on the real object.
* Where it is cheap, real Qt and QGIS objects back the fake: a ``QMainWindow``,
  a ``QgsMapCanvas``, a ``QgsMessageBar``, a ``QgsLayerTreeView`` bound to the project
  layer tree, a ``QgsAdvancedDigitizingDockWidget`` and a ``QgsStatusBar``.

Behaviour follows ``QgisApp`` where that matters for plugins: ``addDockWidget`` shows the
dock, ``setActiveLayer`` only accepts layers that are in the project layer tree, and
``removePluginMenu`` drops an empty sub menu.

This module imports only ``qgis.*`` and knows nothing about the plugin under test.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable

from qgis.core import Qgis, QgsLayerTreeModel, QgsProject, QgsRasterLayer, QgsVectorLayer
from qgis.gui import (
    QgisInterface,
    QgsAdvancedDigitizingDockWidget,
    QgsLayerTreeMapCanvasBridge,
    QgsLayerTreeView,
    QgsMapCanvas,
    QgsMapToolPan,
    QgsMessageBar,
    QgsStatusBar,
)
from qgis.PyQt import sip
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QAction, QDockWidget, QMainWindow, QMenu, QToolBar

if TYPE_CHECKING:
    from qgis.core import QgsMapLayer, QgsMasterLayoutInterface
    from qgis.gui import QgsOptionsWidgetFactory
    from qgis.PyQt.QtWidgets import QWidget


@dataclass(frozen=True)
class RecordedMessage:
    title: str
    text: str
    level: Qgis.MessageLevel


class MessageRecorder:
    """Records every message pushed to a real ``QgsMessageBar``.

    Listens to ``QgsMessageBar.widgetAdded``. That signal fires for every ``push*``
    overload, including the C++ ones (``pushInfo``, ``pushCritical``, ...) which call the
    non-virtual C++ ``pushMessage`` and would bypass a Python override.
    """

    def __init__(self, bar: QgsMessageBar) -> None:
        self._bar = bar
        self.all: list[RecordedMessage] = []
        bar.widgetAdded.connect(self._on_widget_added)

    def _on_widget_added(self, _item: object) -> None:
        item = self._bar.currentItem()
        if item is not None:
            self.all.append(RecordedMessage(item.title(), item.text(), item.level()))

    def _by_level(self, level: Qgis.MessageLevel) -> list[tuple[str, str]]:
        return [(message.title, message.text) for message in self.all if message.level == level]

    @property
    def infos(self) -> list[tuple[str, str]]:
        return self._by_level(Qgis.MessageLevel.Info)

    @property
    def warnings(self) -> list[tuple[str, str]]:
        return self._by_level(Qgis.MessageLevel.Warning)

    @property
    def criticals(self) -> list[tuple[str, str]]:
        return self._by_level(Qgis.MessageLevel.Critical)

    @property
    def successes(self) -> list[tuple[str, str]]:
        return self._by_level(Qgis.MessageLevel.Success)

    def clear(self) -> None:
        """Forget recorded messages and empty the bar.

        Emptying the bar matters: ``QgsMessageBar`` silently drops a message that
        equals one it still shows (same level, title and text).
        """
        self.all.clear()
        self._bar.clearWidgets()

    def __len__(self) -> int:
        return len(self.all)


class FakeQgisInterface(QgisInterface):
    """Test double for ``QgisInterface`` backed by real widgets.

    Create one per process after ``qgis.testing.start_app()``. Call :meth:`reset` between
    tests and :meth:`shutdown` once before ``QgsApplication.exitQgis()``.
    """

    def __init__(self) -> None:
        super().__init__()
        window = QMainWindow()
        window.setObjectName("FakeQgisMainWindow")
        self._main_window = window

        self._canvas = QgsMapCanvas(window)
        window.setCentralWidget(self._canvas)

        self._message_bar = QgsMessageBar(window)
        self.messages = MessageRecorder(self._message_bar)

        self._status_bar = QgsStatusBar()
        self._status_bar.setParentStatusBar(window.statusBar())
        window.statusBar().addPermanentWidget(self._status_bar, 10)

        root = QgsProject.instance().layerTreeRoot()
        # Keep references: the view does not own the model, the bridge owns nothing.
        self._layer_tree_model = QgsLayerTreeModel(root, window)
        self._layer_tree_view = QgsLayerTreeView(window)
        self._layer_tree_view.setModel(self._layer_tree_model)
        self._layer_tree_view.currentLayerChanged.connect(self._on_current_layer_changed)
        self._bridge = QgsLayerTreeMapCanvasBridge(root, self._canvas, window)

        self._cad_dock = QgsAdvancedDigitizingDockWidget(self._canvas, window)
        window.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self._cad_dock)

        self._plugins_menu = window.menuBar().addMenu("Plugins")
        self._plugin_menus: dict[str, QMenu] = {}

        self._plugin_toolbar = QToolBar("Plugins Toolbar", window)
        self._plugin_toolbar.setObjectName("PluginToolBar")
        window.addToolBar(self._plugin_toolbar)

        self._pan_tool = QgsMapToolPan(self._canvas)
        self._action_pan = QAction("Pan Map", window)
        self._action_pan.triggered.connect(self._activate_pan_tool)

        # Recorded calls for methods that have no cheap real counterpart.
        self.options_factories: list[QgsOptionsWidgetFactory] = []
        self.opened_layouts: list[QgsMasterLayoutInterface] = []
        self.options_dialog_pages: list[str] = []

    # ------------------------------------------------------------------ lifecycle

    def reset(self) -> None:
        """Return to the state right after construction, without touching ``QgsProject``.

        Docks and toolbars that a plugin added are removed from the window but not
        deleted: the plugin owns them.
        """
        self.messages.clear()
        self._status_bar.clearMessage()

        self._layer_tree_view.setCurrentLayer(None)
        self._canvas.setCurrentLayer(None)
        tool = self._canvas.mapTool()
        if tool is not None:
            self._canvas.unsetMapTool(tool)
        self._canvas.setLayers([])

        for dock in self.dock_widgets():
            if dock is not self._cad_dock:
                self._main_window.removeDockWidget(dock)
        for toolbar in self.toolbars():
            if toolbar is not self._plugin_toolbar:
                self._main_window.removeToolBar(toolbar)
        self._plugin_toolbar.clear()

        for menu in list(self._plugin_menus.values()):
            self._plugins_menu.removeAction(menu.menuAction())
            menu.deleteLater()
        self._plugin_menus.clear()

        self.options_factories.clear()
        self.opened_layouts.clear()
        self.options_dialog_pages.clear()

    def shutdown(self) -> None:
        """Delete the widgets. Call once, before ``QgsApplication.exitQgis()``."""
        if sip.isdeleted(self._main_window):
            return
        self.reset()
        self._layer_tree_view.currentLayerChanged.disconnect(self._on_current_layer_changed)
        sip.delete(self._main_window)

    # ------------------------------------------------------- helpers, not QGIS API

    def toolbars(self) -> list[QToolBar]:
        """Toolbars currently placed in the main window."""
        window = self._main_window
        return [
            toolbar
            for toolbar in window.findChildren(QToolBar)
            if window.toolBarArea(toolbar) != Qt.ToolBarArea.NoToolBarArea
        ]

    def dock_widgets(self) -> list[QDockWidget]:
        """Dock widgets currently placed in the main window."""
        window = self._main_window
        return [
            dock
            for dock in window.findChildren(QDockWidget)
            if window.dockWidgetArea(dock) != Qt.DockWidgetArea.NoDockWidgetArea
        ]

    def plugin_menu_actions(self, name: str) -> list[QAction]:
        """Actions in the Plugins sub menu called ``name``."""
        menu = self._plugin_menus.get(name)
        return list(menu.actions()) if menu is not None else []

    def toolbar_icons(self) -> list[QAction]:
        """Actions added with ``addToolBarIcon``."""
        return list(self._plugin_toolbar.actions())

    # ---------------------------------------------------------- QgisInterface API

    def mainWindow(self) -> QMainWindow:
        return self._main_window

    def mapCanvas(self) -> QgsMapCanvas:
        return self._canvas

    def mapCanvases(self) -> list[QgsMapCanvas]:
        return [self._canvas]

    def messageBar(self) -> QgsMessageBar:
        return self._message_bar

    def statusBarIface(self) -> QgsStatusBar:
        return self._status_bar

    def layerTreeView(self) -> QgsLayerTreeView:
        return self._layer_tree_view

    def layerTreeCanvasBridge(self) -> QgsLayerTreeMapCanvasBridge:
        return self._bridge

    def cadDockWidget(self) -> QgsAdvancedDigitizingDockWidget:
        return self._cad_dock

    def actionPan(self) -> QAction:
        return self._action_pan

    # layers

    def activeLayer(self) -> QgsMapLayer | None:
        return self._layer_tree_view.currentLayer()

    def setActiveLayer(self, layer: QgsMapLayer | None) -> bool:
        """Like ``QgisApp.setActiveLayer``: only layers in the project layer tree."""
        if layer is None:
            return False
        if QgsProject.instance().layerTreeRoot().findLayer(layer.id()) is None:
            return False
        self._layer_tree_view.setCurrentLayer(layer)
        return True

    def addVectorLayer(self, vectorLayerPath: str, baseName: str, providerKey: str) -> QgsVectorLayer | None:
        return self._add_layer(QgsVectorLayer(vectorLayerPath, baseName, providerKey))

    def addRasterLayer(
        self, rasterLayerPath: str, baseName: str = "", providerKey: str = "gdal"
    ) -> QgsRasterLayer | None:
        return self._add_layer(QgsRasterLayer(rasterLayerPath, baseName, providerKey))

    # project

    def newProject(self, promptToSaveFlag: bool = False) -> bool:
        QgsProject.instance().clear()
        self.newProjectCreated.emit()
        return True

    def addProject(self, project: str) -> bool:
        ok = QgsProject.instance().read(project)
        if ok:
            self.projectRead.emit()
        return ok

    # toolbars

    def addToolBar(
        self,
        name_or_toolbar: str | QToolBar,
        area: Qt.ToolBarArea = Qt.ToolBarArea.TopToolBarArea,
    ) -> QToolBar | None:
        """Both C++ overloads: ``addToolBar(name)`` and ``addToolBar(toolbar, area)``."""
        if isinstance(name_or_toolbar, QToolBar):
            self._main_window.addToolBar(area, name_or_toolbar)
            return None
        toolbar = QToolBar(name_or_toolbar, self._main_window)
        self._main_window.addToolBar(area, toolbar)
        return toolbar

    def pluginToolBar(self) -> QToolBar:
        return self._plugin_toolbar

    def addToolBarIcon(self, qAction: QAction) -> int:
        self._plugin_toolbar.addAction(qAction)
        return 0

    def removeToolBarIcon(self, qAction: QAction) -> None:
        self._plugin_toolbar.removeAction(qAction)

    # docks

    def addDockWidget(self, area: Qt.DockWidgetArea, dockwidget: QDockWidget) -> None:
        self._main_window.addDockWidget(area, dockwidget)
        dockwidget.show()

    def removeDockWidget(self, dockwidget: QDockWidget) -> None:
        self._main_window.removeDockWidget(dockwidget)

    # menus

    def addPluginToMenu(self, name: str, action: QAction) -> None:
        menu = self._plugin_menus.get(name)
        if menu is None:
            menu = self._plugins_menu.addMenu(name)
            self._plugin_menus[name] = menu
        menu.addAction(action)

    def removePluginMenu(self, name: str, action: QAction) -> None:
        menu = self._plugin_menus.get(name)
        if menu is None:
            return
        menu.removeAction(action)
        if not menu.actions():
            self._plugins_menu.removeAction(menu.menuAction())
            menu.deleteLater()
            del self._plugin_menus[name]

    # options and layouts

    def registerOptionsWidgetFactory(self, factory: QgsOptionsWidgetFactory) -> None:
        self.options_factories.append(factory)

    def unregisterOptionsWidgetFactory(self, factory: QgsOptionsWidgetFactory) -> None:
        self.options_factories.remove(factory)

    def showOptionsDialog(self, parent: QWidget | None = None, currentPage: str = "") -> None:
        self.options_dialog_pages.append(currentPage)

    def openLayoutDesigner(self, layout: QgsMasterLayoutInterface) -> None:
        self.opened_layouts.append(layout)

    # ------------------------------------------------------------------ internals

    def _on_current_layer_changed(self, layer: QgsMapLayer | None) -> None:
        # QgisApp does the same: the layer tree view drives the canvas and the iface signal.
        self._canvas.setCurrentLayer(layer)
        self.currentLayerChanged.emit(layer)

    def _activate_pan_tool(self) -> None:
        self._canvas.setMapTool(self._pan_tool)

    def _add_layer(self, layer: QgsMapLayer) -> QgsMapLayer | None:
        if not layer.isValid():
            return None
        QgsProject.instance().addMapLayer(layer)
        self.setActiveLayer(layer)
        return layer


def _make_stub(name: str) -> Callable[..., None]:
    def stub(self: object, *args: object, **kwargs: object) -> None:
        msg = f"FakeQgisInterface.{name}() is not implemented. Add it to tests/fake_iface.py."
        raise NotImplementedError(msg)

    stub.__name__ = name
    stub.__qualname__ = f"FakeQgisInterface.{name}"
    return stub


def _install_loud_stubs(cls: type) -> None:
    """Make every unimplemented abstract method raise instead of returning ``None``.

    SIP returns ``None`` (and prints to stderr) when Python calls a pure virtual that
    has no override. A raised ``NotImplementedError`` fails the test at the right line.
    """
    for name in getattr(QgisInterface, "__abstract_methods__", ()):
        if name not in cls.__dict__:
            setattr(cls, name, _make_stub(name))


_install_loud_stubs(FakeQgisInterface)
