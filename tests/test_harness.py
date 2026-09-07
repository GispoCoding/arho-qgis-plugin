"""Self-test of the test harness (tests/conftest.py and tests/fake_iface.py)."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest
import qgis.utils
from qgis.core import QgsApplication, QgsProject, QgsVectorLayer
from qgis.gui import QgisInterface

from tests.fake_iface import FakeQgisInterface

pytestmark = pytest.mark.fake_iface


def test_iface_is_a_real_qgis_interface(iface):
    assert isinstance(iface, QgisInterface)
    assert isinstance(iface, FakeQgisInterface)
    assert qgis.utils.iface is iface


def test_settings_live_in_a_temporary_profile():
    """Neither the plugin settings nor its log files may touch the real user profile."""
    settings_dir = Path(QgsApplication.qgisSettingsDirPath()).resolve()
    temp_dir = Path(tempfile.gettempdir()).resolve()
    assert temp_dir in settings_dir.parents
    config_dir = Path(os.environ["QGIS_CUSTOM_CONFIG_PATH"]).resolve()
    assert config_dir in settings_dir.parents or settings_dir == config_dir


def test_message_bar_records_every_push_overload(iface, messages):
    bar = iface.messageBar()
    bar.pushWarning("title", "warn")
    bar.pushSuccess("title", "ok")
    bar.pushCritical("title", "bad")
    bar.pushMessage("only text")
    assert messages.warnings == [("title", "warn")]
    assert messages.successes == [("title", "ok")]
    assert messages.criticals == [("title", "bad")]
    assert messages.infos == [("", "only text")]
    assert len(messages) == 4


def test_unimplemented_method_raises_with_a_hint(iface):
    with pytest.raises(NotImplementedError, match="zoomFull.*fake_iface.py"):
        iface.zoomFull()


def test_unknown_attribute_raises_attribute_error(iface):
    with pytest.raises(AttributeError):
        iface.mapCanvass()


def test_project_read_is_a_real_signal(iface):
    fired = []
    iface.projectRead.connect(lambda: fired.append(True))
    try:
        iface.projectRead.emit()
    finally:
        iface.projectRead.disconnect()
    assert fired == [True]


def test_set_active_layer_needs_a_project_layer(iface, new_project):
    layer = QgsVectorLayer("Point?crs=EPSG:4326", "points", "memory")
    fired = []
    iface.currentLayerChanged.connect(fired.append)
    try:
        assert iface.setActiveLayer(layer) is False
        assert iface.activeLayer() is None

        new_project.addMapLayer(layer)
        assert iface.setActiveLayer(layer) is True
        assert iface.activeLayer() is layer
        assert iface.mapCanvas().currentLayer() is layer
        assert fired == [layer]
    finally:
        iface.currentLayerChanged.disconnect(fired.append)


def test_add_vector_layer_adds_to_project_and_activates(iface, new_project):
    layer = iface.addVectorLayer("Point?crs=EPSG:4326", "points", "memory")
    assert layer is not None
    assert new_project.mapLayer(layer.id()) is layer
    assert iface.activeLayer() is layer
    assert iface.addVectorLayer("nonsense", "broken", "ogr") is None


@pytest.mark.usefixtures("new_project")
def test_reset_clears_everything_a_plugin_can_leave_behind(iface):
    from qgis.PyQt.QtCore import Qt
    from qgis.PyQt.QtWidgets import QAction, QDockWidget

    toolbar = iface.addToolBar("Test Toolbar")
    dock = QDockWidget("Test Dock", iface.mainWindow())
    iface.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock)
    action = QAction("Do it", iface.mainWindow())
    iface.addPluginToMenu("TestPlugin", action)
    iface.addToolBarIcon(action)
    iface.statusBarIface().showMessage("busy")
    iface.messageBar().pushInfo("t", "m")
    assert toolbar in iface.toolbars()
    assert dock in iface.dock_widgets()
    assert iface.plugin_menu_actions("TestPlugin") == [action]
    assert iface.toolbar_icons() == [action]

    iface.reset()

    assert iface.toolbars() == [iface.pluginToolBar()]
    assert iface.dock_widgets() == [iface.cadDockWidget()]
    assert iface.plugin_menu_actions("TestPlugin") == []
    assert iface.toolbar_icons() == []
    assert iface.statusBarIface().currentMessage() == ""
    assert len(iface.messages) == 0
    assert iface.messageBar().currentItem() is None


def test_new_project_fixture_gives_an_empty_project(new_project):
    assert isinstance(new_project, QgsProject)
    assert new_project.mapLayers() == {}
