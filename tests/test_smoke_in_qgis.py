"""Smoke tests that only run inside the real QGIS application.

They check the parts that the fake interface cannot prove: that QGIS itself can load and
start the plugin, that ``initGui`` puts the toolbar into the real main window, and that a
plugin unload and reload cycle works.

Marked ``real_qgis``, so they are skipped in a normal pytest run and only execute under
``ci/qgis_pytest_runner.py``. CI runs that in the ``qgis_app_tests`` job of
``.github/workflows/tests.yml``.
"""

from __future__ import annotations

import pytest
import qgis.utils
from qgis.gui import QgisInterface, QgsMessageBar
from qgis.PyQt.QtWidgets import QMenuBar, QToolBar

pytestmark = pytest.mark.real_qgis

PLUGIN_PACKAGE = "arho_feature_template"


def test_iface_is_the_real_qgis_interface(iface):
    from tests.fake_iface import FakeQgisInterface

    assert isinstance(iface, QgisInterface)
    assert not isinstance(iface, FakeQgisInterface)
    # The real application window, not a bare QMainWindow: it has a populated menu bar.
    menu_bar = iface.mainWindow().findChild(QMenuBar)
    assert menu_bar is not None
    assert menu_bar.actions()
    assert isinstance(iface.messageBar(), QgsMessageBar)


def test_qgis_started_the_plugin(iface):
    assert PLUGIN_PACKAGE in qgis.utils.active_plugins

    plugin = qgis.utils.plugins[PLUGIN_PACKAGE]
    assert plugin.toolbar in iface.mainWindow().findChildren(QToolBar)
    assert plugin.actions


def test_message_bar_records_plugin_messages(iface, messages):
    iface.messageBar().pushWarning("Smoke", "message from the smoke test")
    assert messages.warnings == [("Smoke", "message from the smoke test")]


def test_unload_and_reload(iface):
    """Runs last: it replaces the plugin instance that the tests above inspected."""
    qgis.utils.unloadPlugin(PLUGIN_PACKAGE)
    assert PLUGIN_PACKAGE not in qgis.utils.active_plugins

    assert qgis.utils.loadPlugin(PLUGIN_PACKAGE)
    assert qgis.utils.startPlugin(PLUGIN_PACKAGE)
    assert PLUGIN_PACKAGE in qgis.utils.active_plugins
    assert qgis.utils.plugins[PLUGIN_PACKAGE].toolbar in iface.mainWindow().findChildren(QToolBar)
