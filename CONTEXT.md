# ARHO feature template

A QGIS plugin for drawing Finnish land use plans in the Ryhti data model and sending
them to Ryhti. UI text is Finnish, code is English; each term lists both.

## Language

**Plan matter (kaava-asia)**:
One planning case of an organisation. It owns the plans that are made for it and is
always of one plan type.
_Avoid_: Case, project

**Plan (kaava)**:
One version of the plan of a plan matter with its own area, regulations and life cycle.
_Avoid_: Plan version, map

**Valid plan (voimassa oleva kaava)**:
A plan whose life-cycle status says it is in force now.

**Repealing plan matter (kumoava kaava-asia)**:
A plan matter whose plans repeal the valid plans of the same top-level plan type that
they cover.
_Avoid_: Kumoamiskaava, cancelling plan matter

**Repeal (kumoaminen)**:
The act by which a plan or a decision ends the validity of an earlier plan or of a part
of it.
_Avoid_: Cancellation, revoke

**Final plan (lopullinen kaava)**:
A plan whose content is complete and that has been made final. Only the backend can
make a plan final, and it cannot be undone. Making a plan final also repeals the plans
and plan objects it cancels in whole. Final is separate from locked: a final plan may
still change life-cycle status, for example to repealed.
_Avoid_: Confirmed plan, published plan

**Up-to-date plan (ajantasakaava)**:
The plan data that is in force now, seen across plan matters. It shows only plans that
are both valid plans and final plans.
_Avoid_: Valid layers, current plan
