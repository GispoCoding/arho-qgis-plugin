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

**Effect:** Ryhti rejects the repealing plan once its cancellation infos are sent (see
the next item; they are not sent yet). In this database the old plan keeps the valid
status with no plan objects left.

**Possible fix:** in `hame.repealed_plans`, also set the flag true when
`hame.repealed_plan_objects` returns every valid plan object of the old plan with
`cancels_entire_plan_object = true` and the old plan has at least one plan object.

### The serializer does not send `planCancellationInfos`

`PlanSerializer.serialize_plan` in `lambdas/ryhti_client/ryhti_client/serializer.py`
leaves `planCancellationInfos` out. **Rule 240** requires cancellation infos on a plan
that overlaps valid plans, and **rule 218** allows them only in lifecycle status 13
(Voimassa) or 14 (Kumoutunut). When the infos are added to the serializer, include
them only in those statuses.

### Repeal by decision is not modelled

Ryhti has two ways to repeal a plan: a new plan (`Plan.planCancellationInfos`, rule
239) and a separate decision (`PlanDecision.planCancellationInfos`, rule 238).
`hame.plan_cancellation_info` links only to a repealing plan, so a repeal by decision
cannot be stored.
