# Qt lifetime findings not yet fixed

Found during the unload/reload review that produced the signal cleanup commits
(`Disconnect only the slots we connected, drop disconnect_signal` and the four bug fixes
before it). None of these are fixed. Line numbers are from that point in history.

The rule the fixed items followed, repeated here because most of the items below are the
same shape:

- If the plugin owns the sender and deletes it, Qt drops the connection in `~QObject`.
- If a long-lived object owns the sender (`iface`, `QgsProject.instance()`, a project
  layer, a module level singleton), the plugin has to undo the connection itself.
- An exception raised in a slot that C++ invoked makes PyQt call `abort()`. A stale
  connection is therefore a crash, not a log line.

## 1. Dialogs that own a network request and die when `exec()` returns

`plugin.py:618`

```python
dialog = PostPlanDialog()
dialog.exec()
```

`PostPlanDialog` has no parent, builds its own `LambdaService` → `LambdaClient` →
`QNetworkAccessManager` (`gui/dialogs/post_plan.py:39`), and starts the POST from
`QTimer.singleShot(0, self.start_post_plan)`. When `exec()` returns, `dialog` is the only
reference, so the whole tree is destroyed while the request may still be in flight.

Same `dialog = X(); dialog.exec()` shape at `plugin.py:596` (`PluginAbout`),
`plugin.py:602` (`PlanObjectIconPreview`) and about 20 call sites in
`core/plan_manager.py`, `gui/docks/plan_features_dock.py`, `gui/dialogs/manage_plans.py`
and `gui/components/library_display_widget.py`. Only the ones that own a
`LambdaService` are dangerous; the rest are merely untidy.

## 2. Dialogs with no parent at all

Twelve classes call `super().__init__()` with no parent, so they are top level windows
instead of children of the QGIS main window:

`load_plan_matter_dialog.py:31`, `manage_libraries.py:30`, `manage_plans.py:48`,
`new_plan_dialog.py:102`, `plan_feature_form.py:46`, `plan_regulation_group_form.py:57`,
`plugin_settings.py:263`, `regulation_group_selection_view.py:18`,
`regulations_print_settings_dialog.py:24`, `serialize_plan.py:23`,
`serialize_plan_matter.py:22`, `template_selection_form.py:42`.

Compare `gui/dialogs/import_features_form.py:58`, which does pass
`parent=iface.mainWindow()`.

## 3. `previous_map_tool` holds an unowned pointer

`core/plan_manager.py:476`, `:479`, `:484`, `:513`, `:668`

```python
self.previous_map_tool = iface.mapCanvas().mapTool()
...
iface.mapCanvas().setMapTool(self.previous_map_tool)
```

The plugin does not own that tool. If it belonged to a plugin that was unloaded in the
meantime, restoring it uses a dangling pointer. There is no `sip.isdeleted` check and no
connection to `destroyed`.

`previous_map_tool` is also never initialised in `__init__`; it only exists after one of
those three assignments has run.

There is no `unsetMapTool` call anywhere in the repository. `PlanManager.unload` relies
on `iface.actionPan().trigger()` to take our tools off the canvas.

## 4. `QTranslator` is installed and never removed

`plugin.py:65-68`

```python
self.translator = QTranslator()
self.translator.load(file_path)
QCoreApplication.installTranslator(self.translator)
```

`QCoreApplication.removeTranslator` is never called, so every load stacks another
translator on the application.

## 5. `PlanManager` → `Plugin` connections are never undone

`plugin.py:536-547` wires eight signals (`inspect_plan_feature_tool.deactivated` plus
`plan_set`, `plan_matter_set`, `plan_unset`, `project_loaded`, `project_cleared`,
`plan_lock_status_changed`, `plan_identifier_set`) to `Plugin` methods. `Plugin` is a
plain class, not a `QObject`, so cleanup depends on Python collecting the `Plugin`
object. Plugin Reloader does not return to the event loop between unload and re-init, so
the old `Plugin` is still wired while the new one starts.

## 6. `import_features_form` is shown and forgotten

`core/plan_manager.py:348` creates `ImportFeaturesForm` and calls `show()` (non modal).
`PlanManager.unload` never closes or deletes it. If it is open at unload it stays as a
live child of the main window pointing at destroyed managers and docks.

## 7. Widgets removed from a layout without being unparented

`layout().removeWidget(w)` does not change the parent, so the widget stays a visible
child at (0, 0) until the deferred delete runs. This is the same root cause as the dock
fix in `Unparent the docks explicitly at unload`.

Sites: `gui/components/regulation_groups_view.py:191`,
`gui/components/general_regulation_group_widget.py:90` and `:106`,
`gui/components/plan_regulation_group_widget.py:158` and `:172`,
`gui/dialogs/plan_regulation_group_form.py:203` and `:219`,
`gui/dialogs/plan_attribute_form.py:222` and `:240`.

## 8. Parentless `QMenu`s kept alive by a binding annotation

`gui/docks/regulation_groups_dock.py:100` and `:106`,
`gui/components/push_button_edit_lifecycle.py:17`,
`gui/components/library_display_widget.py:163`,
`gui/components/general_regulation_group_widget.py:54`, and the two anonymous menus in
`Plugin.initGui`, are created with no parent and survive only because
`QAbstractButton.setMenu` is annotated `/KeepReference/` in the PyQt bindings. It works,
but the lifetime is an implementation detail rather than a decision.

`gui/components/plan_proposition_widget.py:61`, `plan_document_widget.py:101` and
`plan_regulation_widget.py:152/158/173` pass `self` and show the intended shape.

## 9. Actions are deleted before the code that calls back into them

`Plugin.unload` runs `action.deleteLater()` for every action, then calls
`self.plan_manager.unload()`, which starts with `iface.actionPan().trigger()`. That
triggers `deactivated` → `identify_plan_features_action.setChecked(False)` →
`toggle_identify_plan_features`, so the chain calls `setChecked` and `setEnabled` on
actions already scheduled for deletion. It is safe only because `deleteLater` is
deferred.

## Checked and found to be fine

`iface.addToolBar()` is annotated `/Factory/` (`python/gui/auto_generated/qgisinterface.sip.in`),
so Python owns the returned toolbar. `Plugin.unload` does
`iface.mainWindow().removeToolBar(self.toolbar)` and then `self.toolbar = None`, which
drops the last reference and deletes the C++ object. The toolbar, both `QToolButton`s
and their menus do not leak. Verified with a live PyQt test.
