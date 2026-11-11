# Cancellation info rows are data of the plan

A repealing plan (kumoamiskaava) needs cancellation infos in its Ryhti JSON: one
per earlier plan it repeals, with the plan objects, regulation group relations
and general regulation groups that end (rules 218 and 240). The rows could have
been computed from the geometry at serialization time and never stored. We
store them instead, in `hame.plan_cancellation_info` and its child tables, and
treat them as data of the plan: the serializer only reads them, the import
writes the rows of the file as they are, and the copier clones them with the
copy.

The reason is that not every row can be computed. A cancelled group relation
(a phase plan that removes one regulation group from one plan object of the
earlier plan) is a decision of the planner, added by hand under a plan level
row. A row that lived only in the serializer could not hold it, and an export
and import round trip would lose it.

The geometry-driven trigger (`generate_plan_cancellation_info_triggers` in
`database/triggers.py`) keeps the stored rows in step with the plan. It writes
them again when the plan geometry or the plan matter changes, and when the
validate or finalize action calls `refresh_plan_cancellation_info` before
serializing. The plan level rows are upserted, so a hand-added group relation
under a plan that stays repealed survives a refresh. The plan object rows hold
nothing added by hand and are written again from the geometry every time.

## Consequences

- The Ryhti keys of the cancellation infos are the row ids, so two validations
  of the same plan send the same keys and Ryhti sees an update.
- The trigger only makes rows when the plan matter is repealing, and a refresh
  of a plan whose matter is not repealing deletes all its rows. The import
  therefore marks the plan matter repealing when the file has cancellation
  infos.
- The import and the copy insert with the refresh triggers of `hame.plan` and
  `hame.plan_matter` disabled, or the trigger would write the rows again from
  the geometry over the rows of the file or the source plan.
- The plan object rows of an imported plan are written again from the geometry
  the first time the plan is validated. If they must survive verbatim, the
  refresh has to learn to leave them alone.
