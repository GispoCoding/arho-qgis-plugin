# Project load performance: parked ideas

Measured on 2026-09-15 against the AWS dev database with `qgisprojekti.qgz`
(logs: `ARHOfeaturetemplate-load.log` + QGIS query log). One DB round trip is
~45-65 ms. One `getFeatures()` on a Postgres layer is three round trips
(`BEGIN/DECLARE`, `FETCH`, `CLOSE/COMMIT`) = ~130 ms. One *changed*
`setSubsetString` is one round trip (`SELECT ... LIMIT 0` validation); an
unchanged subset string costs nothing.

Before any fix the open took ~37 s: 18.5 s in QGIS's own widget auto-conf probe
(fixed by giving every JSON field an explicit widget in the project), 10.7 s in
`PlanManager.on_project_loaded` (58 feature requests + 28 subset validations).

Done so far: code caches for `PlanTypeLayer`, `UndergroundTypeLayer`,
`PlanRegulationGroupTypeLayer`; plan type resolved once for the four style
applications; `get_features()` now shows up in the TIMING log.

Ideas 1-5 are done (2026-09-15, one commit each on `fast-create-feature`,
with tests in `tests/test_set_active_plan_matter.py`, `tests/test_set_active_plan.py`,
`tests/test_docks_shared_plan_features.py` and `tests/test_model_readers.py`).
Ideas 6 and 7 are not done. Line numbers are from the 2026-09-15 code before
the changes.

## 1. Do not set the plan to None and then restore it (~1.5 s) - done

`PlanManager.set_active_plan_matter` ends with `self.set_active_plan(None)`
(`core/plan_manager.py:917`), and `on_project_loaded` then calls
`set_active_plan(active_plan_id)` (`:1200`). The None pass costs 14 subset
validations, 4 empty plan-feature-layer scans (`WHERE false`), a regulation
group library rebuild and a features dock rebuild; then it all runs again.

Idea: `set_active_plan_matter(plan_matter_id, plan_id: str | None = None)` that
ends with `self.set_active_plan(plan_id)`; `on_project_loaded` passes the
stored plan id. Other callers keep the default.

## 2. Read the plan matter once in `set_active_plan_matter` (~0.7 s) - done

The same plan matter row is read for the name (`:892`), the permanent
identifier (`:896`) and the plan type (`:912`), plus a full scan of the plan
matter layer for a membership test (`:1192`) and one more read in
`EditLifecycleMenu.__init__` (`gui/components/edit_lifecycle_menu.py:31-32`).

Idea: `PlanMatterLayer.get_feature_by_id(...)` once, take `name`,
`permanent_plan_identifier` and `plan_type_id` from the feature. The membership
test can use the same read (missing feature -> warn path).

## 3. Reuse the active-plan regulation group library in the features dock (~0.8 s) - done

`PlanObjectsDock.create_plan_feature_view` (`gui/docks/plan_features_dock.py:279`)
calls `layer.models_from_features(features)` without `regulation_groups`, so
`PlanObjectReader.models_from_features` (`project/layers/model_readers.py:102-106`)
re-reads the groups and their regulations, additional information, theme and
verbal-regulation associations and propositions: 6 requests. The same groups
were just read by `update_active_plan_regulation_group_library()`
(`plan_manager.py:966`, one line before `:967`).

Idea: pass `self.active_plan_regulation_group_library.regulation_groups` and
make the parameter a *seed*: fetch only the group ids that are not in it. The
library leaves out `generalRegulations` groups on purpose, so a plan object
that referenced one would otherwise lose it.

## 4. Scan the four plan feature layers once for both docks (~0.5 s) - done

`RegulationGroupsDock.update_regulation_groups` (`gui/docks/regulation_groups_dock.py:209-215`)
reads the four plan feature layers (id + geometry, used to flash/select the
objects of a group) and `create_plan_feature_view`
(`plan_features_dock.py:276-277`) reads them again in full, right after.

Idea: read once in `set_active_plan` and pass the features to both; keep the
self-fetching behaviour when the argument is `None` for the other callers.

## 5. Read the plan row once in `set_active_plan` (~0.4 s) - done

`:952` model, `:984` zoom (`zoom_to_active_plan` scans the layer), `:975` name,
and `plan_features_dock.py:200` lifecycle status: four reads of one row.

Idea: `PlanLayer.get_feature_by_id(plan_id, no_geometries=False)` once; build
the model, the name and the bounding box from it.

Done as: a plan id that is not found now logs a warning and unsets the plan
(it used to crash on `model_from_feature(None)`). The lifecycle status id is
passed to the features dock. The plan matter's plan type id is kept on the
manager (`active_plan_matter_plan_type_id`) for the layer styles; the one
remaining plan matter read is in `EditLifecycleMenu.__init__`.

## 6. Subset-string validations (~1.5 s, ~0.7 s after idea 1)

Every changed filter costs a `SELECT * FROM ... LIMIT 0`. 14 plan layers × 2
passes = 28 on load. The plan matter layer filters cost nothing because the
project was saved with the same filters. Nothing to change in the plugin
beyond idea 1; just be aware when adding layers to `plan_layers`.

## 7. Project file size (~2 s parse)

`qgisprojekti.qgs` inside the `.qgz` is 9.4 MB; 5 MB of it is `<labeling>`
in the two Pisteet layers (rule-based labeling, ~2 MB each) and ~0.9 MB the
renderers. That is the 2 s gap between the layers opening and the widget
probe. Check whether the label rules can be trimmed, or kept in a `.qml`
that `_apply_style` loads anyway.

## 8. Plugin-side guard for other project files

QGIS emits `QgsProject.readProject` inside `QgsProject::read()`
(`src/core/project/qgsproject.cpp:2653`), before `QgisApp` resolves widget
dependencies (`src/app/qgisapp.cpp:6526`), which is where the JSON probe runs.
A handler there could set `KeyValue` on every JSON field with a null widget
setup, for any project file a user opens. Risk: a JSON field holding an array
would get `KeyValue` where auto-conf would pick `List`; the ARHO schema has
none today. Not needed for the repo project, which is fixed in the file.
