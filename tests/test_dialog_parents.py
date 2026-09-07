"""Every dialog takes a parent, and a parented dialog is deleted again after use.

A parentless `QDialog` is a top level window instead of a child of the QGIS window.
Giving it a parent hands ownership to C++, so letting the Python name go out of scope
is no longer enough: without `deleted_after_use` it stays a child of the window for the
rest of the session, one more every time it is opened.
"""

from __future__ import annotations

import importlib
import inspect
import pkgutil

import pytest
from qgis.PyQt import sip
from qgis.PyQt.QtWidgets import QDialog

import arho_feature_template.gui.dialogs as dialogs_package
from arho_feature_template.gui.dialogs.import_plan_form import ImportPlanForm
from arho_feature_template.gui.dialogs.load_plan_matter_dialog import LoadPlanMatterDialog
from arho_feature_template.gui.dialogs.manage_libraries import ManageLibrariesForm
from arho_feature_template.gui.dialogs.plugin_about import PluginAbout
from arho_feature_template.gui.dialogs.regulation_group_selection_view import RegulationGroupSelectionView
from arho_feature_template.gui.dialogs.regulations_print_settings_dialog import RegulationsPrintSettingsDialog
from arho_feature_template.gui.dialogs.serialize_plan import SerializePlan
from arho_feature_template.gui.dialogs.serialize_plan_matter import SerializePlanMatter
from arho_feature_template.utils.widget_utils import deleted_after_use

pytestmark = pytest.mark.fake_iface


def _dialog_classes():
    for info in pkgutil.iter_modules(dialogs_package.__path__):
        module = importlib.import_module(f"{dialogs_package.__name__}.{info.name}")
        for name, obj in vars(module).items():
            if inspect.isclass(obj) and issubclass(obj, QDialog) and obj.__module__ == module.__name__:
                yield f"{info.name}.{name}", obj


def test_every_dialog_takes_a_parent():
    without_parent = [
        name for name, cls in _dialog_classes() if "parent" not in inspect.signature(cls.__init__).parameters
    ]
    assert without_parent == []


@pytest.mark.parametrize(
    "build",
    [
        pytest.param(lambda parent: SerializePlan(parent), id="SerializePlan"),
        pytest.param(lambda parent: SerializePlanMatter(parent), id="SerializePlanMatter"),
        pytest.param(lambda parent: RegulationsPrintSettingsDialog(parent), id="RegulationsPrintSettingsDialog"),
        pytest.param(lambda parent: PluginAbout(parent), id="PluginAbout"),
        pytest.param(lambda parent: ManageLibrariesForm([], [], parent), id="ManageLibrariesForm"),
        pytest.param(lambda parent: RegulationGroupSelectionView([], parent), id="RegulationGroupSelectionView"),
        pytest.param(lambda parent: LoadPlanMatterDialog(parent, []), id="LoadPlanMatterDialog"),
        pytest.param(lambda parent: ImportPlanForm(parent), id="ImportPlanForm"),
        # PostPlanDialog is not here: it starts a POST from its constructor, so building
        # one without running it belongs in tests/test_lambda_service.py
    ],
)
def test_dialog_becomes_a_child_of_its_parent(build, iface, flush_deferred_deletes):
    with deleted_after_use(build(iface.mainWindow())) as dialog:
        assert dialog.parent() is iface.mainWindow()

    flush_deferred_deletes()
    assert sip.isdeleted(dialog)


def test_plugin_dialogs_are_parented_and_deleted(plugin, iface, monkeypatch, flush_deferred_deletes):
    """`exec()` is stubbed out: the real one would block on a modal window."""
    opened = []
    monkeypatch.setattr(PluginAbout, "exec", lambda self: opened.append(self) or 0)

    plugin.open_about()

    dialog = opened[0]
    assert dialog.parent() is iface.mainWindow()
    flush_deferred_deletes()
    assert sip.isdeleted(dialog)
