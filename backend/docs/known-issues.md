# Known issues

Differences between this repository and the Ryhti rules that are known but not fixed
yet. The rule numbers refer to SYKE's plan validation rules (Kaavatiedon
validointisäännöt ja paluuarvot).

## Plan cancellation (kumoaminen)

### `cancels_entire_plan` is false when all plan objects are repealed

**Rule 248** (`quality/req-plan-cancellation-info-must-have-at-least-one-plan-object-cancelled`):
repealing every plan object of a plan repeals the whole plan, so `cancelsEntirePlan`
must be true.

**Where:** `hame.repealed_plans` in `database/functions.py` sets `cancels_entire_plan`
only from `st_coveredby(cancelled.geom, repealing.geom)`, that is from the plan
borders. When the repealing plan covers every plan object of the old plan but not its
whole area, the flag stays false and the plan object cancellation infos list every
object as repealed entirely.

**Effect:** Ryhti rejects the repealing plan when it is validated in the valid
lifecycle status. In this database the old plan keeps the valid status with no plan
objects left.

**Possible fix:** in `hame.repealed_plans`, also set the flag true when
`hame.repealed_plan_objects` returns every valid plan object of the old plan with
`cancels_entire_plan_object = true` and the old plan has at least one plan object.

### The import skips a cancellation info whose target is not in this database

`Deserializer.deserialize_plan_cancellation_info` in
`lambdas/ryhti_client/ryhti_client/deserializer.py` looks up the repealed plan, plan
object and regulation group of every cancellation info by the key in its uri. A
cancellation info whose plan is not in this database is skipped with a warning in the
log, and so is a plan object cancellation info or a cancelled group relation whose plan
object or group is not. The rest of the plan imports.

**Effect:** a plan imported into a database that does not hold the plans it repeals
(for example before `import_wfs_plans` has brought them in) loses those cancellation
infos silently, apart from the log. The next validation writes the plan object rows
again from the geometry, but a cancelled group relation is gone for good.

**Possible fix:** import the plans the file refers to first, or make the import fail
instead of warn when a target is missing.

### The public validation API cannot check a repealed plan that is not in Ryhti

The public validation API (`Plan/validate`) looks the repealed plans and plan objects
up in Ryhti. A repealing plan whose cancellation infos point at plans this database
holds but Ryhti does not (a plan drawn here for a test, for example) fails with
`quality__req_must_be_valid_plan` and `quality__req_uri_resource_not_exists`. When
such an info has `cancelsEntirePlan` true, the API answers 500 Internal Server Error
instead of a validation error (seen on 2026-09-08).

**Effect:** a repealing plan can only be validated once the plans it repeals are in
Ryhti, which they are for the valid national plans `import_wfs_plans` brings in. The
live test in `test/test_services.py` asserts the two validation errors.

### Repeal by decision is not modelled

Ryhti has two ways to repeal a plan: a new plan (`Plan.planCancellationInfos`, rule
239) and a separate decision (`PlanDecision.planCancellationInfos`, rule 238).
`hame.plan_cancellation_info` links only to a repealing plan, so a repeal by decision
cannot be stored.
