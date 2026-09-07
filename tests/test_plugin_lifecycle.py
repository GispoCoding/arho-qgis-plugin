"""The plugin can start, register its UI, react to projectRead, and unload cleanly.

Asserts through the fake interface helpers, so it needs the fake. The same ground inside
the real QGIS application is covered by ``tests/test_smoke_in_qgis.py``.
"""

from __future__ import annotations

import pytest
import qgis.utils
from qgis.PyQt.QtWidgets import QDockWidget

from arho_feature_template.core.plan_manager import PlanManager
from arho_feature_template.plugin import Plugin

pytestmark = pytest.mark.fake_iface

TOOLBAR_TITLE = "ARHO Toolbar"


def test_init_gui_registers_ui(plugin, iface):
    assert TOOLBAR_TITLE in [toolbar.windowTitle() for toolbar in iface.toolbars()]

    docks = iface.dock_widgets()
    manager = plugin.plan_manager
    for dock in (
        manager.new_feature_dock,
        manager.regulation_groups_dock,
        manager.features_dock,
        plugin.validation_dock,
    ):
        assert dock in docks
        assert dock.isHidden()

    assert iface.plugin_menu_actions(Plugin.name)
    assert len(iface.options_factories) == 1


def test_missing_pgtz_shows_a_warning(plugin_factory, messages, monkeypatch):
    monkeypatch.delenv("PGTZ", raising=False)
    plugin_factory()
    assert messages.warnings
    assert messages.warnings[0][0] == "Varoitus"


def test_unload_leaves_iface_clean(plugin_factory, iface):
    show_exception_before = qgis.utils.showException
    plugin = plugin_factory()
    assert qgis.utils.showException is not show_exception_before

    plugin.unload()

    assert iface.toolbars() == [iface.pluginToolBar()]
    assert iface.dock_widgets() == [iface.cadDockWidget()]
    assert iface.plugin_menu_actions(Plugin.name) == []
    assert iface.toolbar_icons() == []
    assert iface.options_factories == []
    assert qgis.utils.showException is show_exception_before


def test_unload_unparents_the_docks(plugin_factory, iface):
    """removeDockWidget only hides a dock, and deleteLater waits for the event loop.

    Plugin Reloader reloads the plugin without returning to the event loop, so a dock
    that is still a child of the main window collides with its fresh copy by object name.
    """
    plugin = plugin_factory()
    manager = plugin.plan_manager
    docks = [
        manager.new_feature_dock,
        manager.regulation_groups_dock,
        manager.features_dock,
        plugin.validation_dock,
    ]

    plugin.unload()

    children = iface.mainWindow().findChildren(QDockWidget)
    assert [dock for dock in docks if dock in children] == []


def test_project_read_reinitializes_until_unload(plugin_factory, iface, monkeypatch):
    calls = []
    monkeypatch.setattr(PlanManager, "on_project_loaded", lambda _self: calls.append(1))

    plugin = plugin_factory()
    assert calls == [1]  # initGui() calls it once right away

    iface.projectRead.emit()
    assert calls == [1, 1]

    plugin.unload()
    iface.projectRead.emit()
    assert calls == [1, 1]
