# Plan object form open performance

Measured on 2026-09-15 against the AWS dev database with `qgisprojekti.qgz`
(logs: `ARHOfeaturetemplate-form-open.log` + QGIS query log). One `getFeatures()`
on a Postgres layer is three round trips (`BEGIN/DECLARE`, `FETCH`, `CLOSE/COMMIT`)
= ~125 ms. See `load-performance-ideas.md` for the project load side.

Clicking a land use area with the inspect tool (3 regulation groups, 7 regulations)
and getting its form took ~3.7 s: 27 layer reads.

| Phase | Reads | Time | What |
|---|---|---|---|
| Identify click | 8 | ~1.1 s | one spatial read per layer: 4 editable plan layers + 4 Ajantasakaava (valid) layers |
| Model build | 8 | ~1.0 s | associations, groups, regulations, additional information, themes, verbal types, propositions |
| Form widgets | 8 | ~1.0 s | the same plan matter row, read once per lifecycle menu (one per regulation widget) and once by the regulation group view, only for its plan type |
| Form widgets | 3 | ~0.4 s | one association read per stored regulation group, to count the other objects using it |

## Done (2026-09-15, one commit each on `fast-create-feature`)

1. **Plan type as a project variable.** `set_active_plan_matter` stores the plan
   matter's `plan_type_id` with `set_active_plan_matter_plan_type_id`; the lifecycle
   menu, the regulation group view, the template selection form and the new plan
   dialog resolve the plan type from the cached `PlanTypeLayer`. 8 reads -> 0.
   `PlanMatterLayer.is_regional_plan` is gone. Tests: `tests/test_edit_lifecycle_menu.py`,
   `tests/test_set_active_plan_matter.py`.
2. **One association read for all groups.** `RegulationGroupsView.add_stored_plan_regulation_groups`
   counts the other linked objects of every stored group with
   `RegulationGroupAssociationLayer.count_other_linked_objects` and hands the count to
   each `RegulationGroupWidget`. A group added later into an open form still reads its
   own count. N reads -> 1. Tests: `tests/test_plan_feature_form.py`.
3. **Editable layers first on click.** `InspectPlanFeatures` takes
   `fallback_layer_classes`; the valid layers are searched only when the editable
   layers give nothing. 8 reads -> 4 for an editable object. A valid object under an
   editable one is no longer offered in the pick menu. Tests:
   `tests/test_inspect_plan_features_tool.py`.

Measured after the three (2026-09-15 20:43, `logs/*-form-open-after.*`, a land use
area with 2 groups and 3 regulations): 13 reads, ~1.9 s from the click to the form.
4 spatial reads, 8 model-build reads, 1 association read, no plan matter read.

One more read appeared once per session: the full `codes.type_of_verbal_plan_regulation`
table, the lazy cache build of `VerbalRegulationType` on its first use in the form.
Moved to `PlanManager.cache_code_layers`, so it is part of the project load now.

## Parked

### Seed the model build from the active plan library (~0.75 s)

`PlanManager.edit_plan_feature` calls `model_from_feature(feature)` without the
`regulation_groups` seed that `PlanObjectReader.models_from_features` supports and
the features dock already uses. Seeding with
`active_plan_regulation_group_library.regulation_groups` would skip 6 of the 8
model-build reads.

Not done on purpose: the form would show the in-memory copy of the groups, so a
change made by another user in the database between the library refresh and the
form open would not be seen, and the save diff would start from stale `stored`
ids. The seeded models are also shared objects: `RegulationGroupWidget.__init__`
sets `type_code_id` on the group it is given, so the form would need copies.
Decision of 2026-09-15: fresh data over ~0.75 s. Revisit if single-user editing
of a plan becomes a stated assumption.

### The identify request itself

`QgsMapToolIdentify` fetches every column and the geometry of each candidate
layer. Nothing to change in the plugin; a leaner request would need a custom
spatial `getFeatures` per layer instead of the identify tool.
