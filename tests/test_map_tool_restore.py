"""`PlanManager` remembers the map tool that was active before one of ours took over.

The plugin does not own that tool. Restoring it blindly is a crash: PyQt invalidates
the wrapper when the owner is deleted, and `setMapTool` then raises `RuntimeError`
inside a slot that C++ invoked, which turns into `abort()`.
"""

from __future__ import annotations

import pytest
from qgis.gui import QgsMapToolPan
from qgis.PyQt import sip
from qgis.PyQt.QtWidgets import QWidget

pytestmark = pytest.mark.fake_iface


def test_previous_map_tool_starts_as_none(plugin):
    """It used to exist only after one of the three assignments had run."""
    assert plugin.plan_manager.previous_map_tool is None


def test_identify_restores_the_previous_tool(plugin, iface):
    canvas = iface.mapCanvas()
    tool = QgsMapToolPan(canvas)
    canvas.setMapTool(tool)

    plugin.identify_plan_features_action.setChecked(True)
    assert canvas.mapTool() is plugin.plan_manager.inspect_plan_feature_tool

    plugin.identify_plan_features_action.setChecked(False)

    assert canvas.mapTool() is tool


def test_identify_does_not_restore_a_deleted_tool(plugin, iface):
    """The previous tool can belong to a plugin that was unloaded in between."""
    canvas = iface.mapCanvas()
    owner = QWidget()
    tool = QgsMapToolPan(canvas)
    tool.setParent(owner)
    canvas.setMapTool(tool)

    plugin.identify_plan_features_action.setChecked(True)
    sip.delete(owner)
    assert sip.isdeleted(tool)

    plugin.identify_plan_features_action.setChecked(False)  # used to raise RuntimeError

    assert canvas.mapTool() is not plugin.plan_manager.inspect_plan_feature_tool
    assert plugin.plan_manager.previous_map_tool is None


def test_restore_without_a_previous_tool_falls_back_to_pan(plugin, iface):
    """`setMapTool(None)` returns immediately in QGIS, leaving our tool active."""
    canvas = iface.mapCanvas()
    plugin.plan_manager.previous_map_tool = None
    canvas.setMapTool(plugin.plan_manager.inspect_plan_feature_tool)

    plugin.plan_manager.restore_previous_map_tool()

    assert canvas.mapTool() is not plugin.plan_manager.inspect_plan_feature_tool


def test_unload_drops_the_previous_map_tool(plugin, iface):
    canvas = iface.mapCanvas()
    tool = QgsMapToolPan(canvas)  # kept on a name: the canvas does not own its map tool
    canvas.setMapTool(tool)
    plugin.identify_plan_features_action.setChecked(True)
    assert plugin.plan_manager.previous_map_tool is not None

    plugin.unload()

    assert plugin.plan_manager.previous_map_tool is None
