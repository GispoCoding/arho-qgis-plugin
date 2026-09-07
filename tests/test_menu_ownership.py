"""Menus attached with `setMenu` need an owner of their own.

`QAbstractButton.setMenu` does not take ownership (the bindings only annotate it
`/KeepReference/`), and `QMenu.addMenu(QMenu)` adds the sub menu's action without
reparenting it. Both leave the lifetime to a binding detail instead of a decision.
"""

from __future__ import annotations

import pytest
from qgis.PyQt import sip
from qgis.PyQt.QtCore import pyqtSignal
from qgis.PyQt.QtWidgets import QMenu

from arho_feature_template.gui.components.push_button_edit_lifecycle import PushButtonEditLifecycle

pytestmark = pytest.mark.fake_iface


class FakeLifecycleMenu(QMenu):
    """Stands in for `EditLifecycleMenu`, which reads the lifecycle code layer."""

    lifecycle_change_requested = pyqtSignal(object, object)


def test_toolbar_menus_have_an_owner(plugin):
    assert plugin.plan_matter_button.menu().parent() is plugin.plan_matter_button

    plan_menu = plugin.plan_button.menu()
    assert plan_menu.parent() is plugin.plan_button
    assert plugin.new_plan_menu.parent() is plan_menu
    assert plugin.save_plan_menu.parent() is plan_menu


def test_regulation_groups_dock_menus_have_an_owner(plugin):
    dock = plugin.plan_manager.regulation_groups_dock
    assert dock.new_btn.menu().parent() is dock
    assert dock.modify_selected_features_btn.menu().parent() is dock


def test_populate_menu_does_not_stack_menus(monkeypatch, flush_deferred_deletes):
    """`populate_menu` runs on every project read, and a parented menu is not collected."""
    import arho_feature_template.gui.components.push_button_edit_lifecycle as module

    monkeypatch.setattr(module, "EditLifecycleMenu", FakeLifecycleMenu)
    button = PushButtonEditLifecycle()

    button.populate_menu()
    first_menu = button.menu()
    button.populate_menu()
    flush_deferred_deletes()

    assert button.menu() is not first_menu
    assert sip.isdeleted(first_menu)
    assert button.findChildren(QMenu) == [button.menu()]
