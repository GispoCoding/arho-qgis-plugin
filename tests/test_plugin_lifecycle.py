"""The plugin can start, register its UI, react to projectRead, and unload cleanly.

Asserts through the fake interface helpers, so it needs the fake. The same ground inside
the real QGIS application is covered by ``tests/test_smoke_in_qgis.py``.
"""

from __future__ import annotations

import pytest
import qgis.utils
from qgis.core import QgsProject
from qgis.PyQt.QtWidgets import QDockWidget

from arho_feature_template.core.plan_manager import PlanManager
from arho_feature_template.core.template_manager import TemplateManager
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


def test_unload_keeps_other_project_read_receivers(plugin_factory, iface):
    """A bare projectRead.disconnect() would drop QGIS' and other plugins' handlers too."""
    calls = []
    iface.projectRead.connect(lambda: calls.append(1))

    plugin = plugin_factory()
    plugin.unload()

    iface.projectRead.emit()
    assert calls == [1]


def test_unload_disconnects_template_library_singleton(plugin_factory):
    """`TemplateManager.signal_manager` is created at import time and outlives the plugin."""
    plugin = plugin_factory()
    dock = plugin.plan_manager.new_feature_dock

    plugin.unload()

    with pytest.raises(TypeError):
        TemplateManager.signal_manager.feature_object_added_to_library.disconnect(dock.update_template_list)


def test_unload_disconnects_project_cleared(plugin_factory):
    """QgsProject outlives the plugin, so the connection has to be undone at unload.

    Asserted by disconnecting again instead of by emitting: ``QgsProject.instance()`` is
    shared by the whole test session, and a stray ``cleared`` reaches managers left over
    from other tests.
    """
    plugin = plugin_factory()
    manager = plugin.plan_manager
    # What a successfully loaded project does
    manager.connect_project_cleared_signal()

    plugin.unload()

    with pytest.raises(TypeError):
        QgsProject.instance().cleared.disconnect(manager.on_project_cleared)


def test_unload_runs_the_plan_manager_before_deleting_the_actions(plugin_factory, monkeypatch):
    """`PlanManager.unload` triggers actionPan, which reaches back into the actions.

    `deactivated` -> `identify_plan_features_action.setChecked(False)` used to run on
    actions that had already been passed to `deleteLater`.
    """
    plugin = plugin_factory()
    action_count = len(plugin.actions)
    assert action_count > 0
    seen = []
    real_unload = plugin.plan_manager.unload

    def spy():
        seen.append((len(plugin.actions), plugin.toolbar is not None))
        real_unload()

    monkeypatch.setattr(plugin.plan_manager, "unload", spy)

    plugin.unload()

    # The actions and the toolbar were still alive when the plan manager unloaded
    assert seen == [(action_count, True)]
    assert plugin.actions == []


def test_unload_with_the_identify_tool_active(plugin_factory, iface):
    """The pan trigger inside `PlanManager.unload` takes our tool off the canvas."""
    plugin = plugin_factory()
    plugin.identify_plan_features_action.setChecked(True)
    inspect_tool = plugin.plan_manager.inspect_plan_feature_tool
    assert iface.mapCanvas().mapTool() is inspect_tool

    plugin.unload()

    assert iface.mapCanvas().mapTool() is not inspect_tool


def test_unload_disconnects_the_plan_manager_signals(plugin_factory):
    """`Plugin` is not a QObject, so Qt drops none of these when the plugin goes away.

    Plugin Reloader re-inits before Python collects the old `Plugin`, so a leftover
    connection calls into the old plugin while the new one is starting.
    """
    plugin = plugin_factory()
    manager = plugin.plan_manager
    pairs = [
        (manager.inspect_plan_feature_tool.deactivated, plugin.on_inspect_tool_deactivated),
        (manager.plan_set, plugin.on_active_plan_set),
        (manager.plan_matter_set, plugin.on_active_plan_matter_set),
        (manager.plan_unset, plugin.on_active_plan_unset),
        (manager.project_loaded, plugin.on_project_loaded),
        (manager.project_cleared, plugin.on_project_cleared),
        (manager.plan_lock_status_changed, plugin.on_plan_lock_status_changed),
        (manager.plan_identifier_set, plugin.validation_dock.on_permanent_identifier_set),
    ]

    plugin.unload()

    for signal, slot in pairs:
        with pytest.raises(TypeError):
            signal.disconnect(slot)


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
