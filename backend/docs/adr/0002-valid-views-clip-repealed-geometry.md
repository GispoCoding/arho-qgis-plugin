# Valid views clip repealed geometry at query time

A plan or plan object that a repealing plan repeals only in part stays valid
(lifecycle status 13) on the part the repealing plan does not cover. The
remaining valid geometry could have been written into the base tables when the
repealing plan is finalized. We do not store it: the base tables keep the
geometry as it was authored and imported, and the valid views (`plan_valid`,
`land_use_area_valid`, `other_area_valid`, `line_valid`, `point_valid`) derive
the remaining valid geometry when they are queried. For a plan the view takes
`st_difference` of the plan geometry and the union of the geometries of the
plans that repeal it. For a plan object the view takes the intersection of the
remaining valid geometries stored on its plan object cancellation infos, which
the trigger computes from the original geometry, so the two derivations agree.

A cancellation info clips only when its repealing plan is final and its
validity period has started. The status of the repealing plan does not matter:
a repeal is one way, so a repealing plan that is later repealed itself keeps
the earlier clip in force. A row whose remaining valid geometry is empty is
left out of the view, together with the rows of the other valid views that
hang off it.

## Consequences

- `hame.repealed_plans` uses `plan_valid` only to tell which plans are valid
  and tests the overlap and the cover against the stored geometry of
  `hame.plan`. Reading the clipped geometry of the view would make a final
  repealing plan miss its own target: `refresh_plan_cancellation_info` would
  delete the cancellation info row and write it again with a new id, and the
  cancelled group relations added by hand under it would go with it. Ryhti
  rule 245 tests the cover against the stored geometry as well, so the two
  agree.
- A plan whose whole area is repealed by two or more partial repeals keeps
  status 13 in the base table and only disappears from the views. The
  finalize action should set such a plan repealed; that is not done yet.
- The geometry is computed on every query, without an index. Plan counts are
  small enough for this.
- Cancelled group relations and cancelled general regulation groups are not
  reflected in the valid views.
