from __future__ import annotations

import datetime
import logging
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from string import Template
from typing import TYPE_CHECKING, Any, cast
from uuid import UUID

import simplejson as json
from sqlalchemy import create_engine, select, text, update
from sqlalchemy.orm import sessionmaker

from database import base, codes, models
from ryhti_client.deserializer import (
    Deserializer,
    extra_import_data_from_dict,
    ryhti_plan_from_json,
)
from ryhti_client.lifecycles import (
    LifeCycleStatusValue,
    UnderAppealScopeOption,
    is_under_appeal,
)
from ryhti_client.plan_copier import CopyPlanData, PlanCopier
from ryhti_client.profiling import attach_query_profiler
from ryhti_client.serializer import LOCAL_TZ, PlanSerializer

if TYPE_CHECKING:
    from collections.abc import Generator

    from ryhti_api_client import Plan as RyhtiPlan
    from sqlalchemy.orm import Session

    from database.base import DbId
    from ryhti_client.ryhti_client import RyhtiResponse

LOGGER = logging.getLogger(__name__)


class PlanAlreadyExistsError(Exception):
    def __init__(self, plan_id: str) -> None:
        self.plan_id = plan_id
        super().__init__(f"Plan '{plan_id}' already exists.")


class PlanMatterNotFoundError(Exception):
    def __init__(self, plan_matter_id: UUID) -> None:
        self.plan_matter_id = plan_matter_id
        super().__init__(f"Plan matter '{plan_matter_id}' does not exist.")


class PlanNotFoundError(Exception):
    def __init__(self, plan_id: UUID) -> None:
        super().__init__(f"Plan '{plan_id}' does not exist.")


class LifeCycleStatusNotFoundError(Exception):
    def __init__(self, lifecycle_status_id: UUID) -> None:
        super().__init__(f"Lifecycle status '{lifecycle_status_id} does not exist.")


class ApprovalDateRequiredError(Exception):
    def __init__(self) -> None:
        super().__init__(
            "Approval date must be provided when copying plan to approved status or later."
        )


class StartDateRequiredError(Exception):
    def __init__(self) -> None:
        super().__init__(
            "Period of validity start date must be provided when copying plan "
            "to valid status or later or is set partially valid."
        )


class PlanAlreadyFinalError(Exception):
    def __init__(self, plan_id: str) -> None:
        super().__init__(f"Plan '{plan_id}' is already final.")


class PlanNotValidError(Exception):
    def __init__(self, plan_id: str) -> None:
        super().__init__(
            f"Plan '{plan_id}' must have lifecycle status "
            f"'{LifeCycleStatusValue.VALID}' and be valid today before it can "
            f"be made final."
        )


class RepealedStatusNotFoundError(Exception):
    def __init__(self) -> None:
        super().__init__(
            f"Lifecycle status '{LifeCycleStatusValue.REPEALED}' does not exist."
        )


# The plan object tables with the column of hame.plan_object_cancellation_info
# that names an object of each, see CancelledPlanObjectMixin in
# database/models.py.
CANCELLED_PLAN_OBJECTS = (
    (models.LandUseArea, models.PlanObjectCancellationInfo.land_use_area_id),
    (models.OtherArea, models.PlanObjectCancellationInfo.other_area_id),
    (models.Line, models.PlanObjectCancellationInfo.line_id),
    (models.Point, models.PlanObjectCancellationInfo.point_id),
)


@dataclass
class FinalizeResult:
    """Counts of what making a plan final repealed."""

    repealed_plans: int = 0
    repealed_plan_objects: int = 0

    def to_details(self) -> dict[str, Any]:
        return asdict(self)


def is_valid_plan(plan: models.Plan) -> bool:
    """Check that the plan is valid today, the way hame.plan_valid does.

    The plan must have the valid lifecycle status and its period of validity
    must cover the current date. A missing start date counts as -infinity and a
    missing end date as +infinity, see valid_today in database/valid_views.py.
    """
    today = datetime.datetime.now(tz=LOCAL_TZ).date()
    return (
        plan.lifecycle_status.value == LifeCycleStatusValue.VALID
        and (
            plan.period_of_validity_start is None
            or plan.period_of_validity_start <= today
        )
        and (
            plan.period_of_validity_end is None or today <= plan.period_of_validity_end
        )
    )


class DatabaseClient:
    def __init__(self, connection_string: str) -> None:
        engine = create_engine(connection_string)
        self.query_profiler = attach_query_profiler(engine)
        self.Session = sessionmaker(bind=engine)
        self.serializer = PlanSerializer(self.Session)

    def log_query_summary(self) -> None:
        """Log the executed SQL statements when SQL profiling is switched on."""
        if self.query_profiler:
            self.query_profiler.log_summary()

    def get_plan(self, plan_id: str) -> models.Plan:
        """Fetch a single plan from the database.

        The returned instance is detached. Since the session does not expire on
        commit, plan data remains accessible without a session. Relationships
        configured with lazy loading require reattaching the instance to a new
        session (see PlanSerializer.serialize_plan).

        Raises PlanNotFoundError if the plan does not exist.
        """
        with self.Session(expire_on_commit=False) as session:
            plan = session.get(models.Plan, plan_id)
            if plan is None:
                raise PlanNotFoundError(UUID(plan_id))
            return plan

    def save_plan_validation_response(
        self, plan_id: DbId, response: RyhtiResponse
    ) -> str:
        """Save open validation API response data to the database and return lambda
        response.

        If validation is successful, update validated_at field and validation_errors
        field

        If validation/post is unsuccessful, save the error JSON in plan
        validation_errors json field (in addition to saving it to AWS logs and
        returning them in lambda return value).

        If Ryhti request fails unexpectedly, save the returned error.
        """
        LOGGER.info(f"Saving response for plan {plan_id}...")
        LOGGER.info(response)
        # In case Ryhti API does not respond in the expected manner,
        # save the response for debugging.
        if "status" not in response or "errors" not in response:
            detail = f"RYHTI API returned unexpected response: {response}"
            values: dict[str, Any] = {
                "validation_errors": f"RYHTI API ERROR: {response}"
            }
        elif response["status"] == 200:
            detail = f"Plan validation successful for {plan_id}!"
            values = {
                "validation_errors": (
                    "Kaava on validi. Kaava-asiaa ei ole vielä validoitu."
                ),
                "validated_at": datetime.datetime.now(tz=LOCAL_TZ),
            }
        else:
            detail = f"Plan validation FAILED for {plan_id}."
            values = {
                "validation_errors": response["errors"],
                "validated_at": datetime.datetime.now(tz=LOCAL_TZ),
            }

        with self.Session() as session:
            # Update the plan with a single statement. There is no need to fetch
            # the whole plan with its relationships just to save the result.
            result = session.execute(
                update(models.Plan)
                .where(models.Plan.id == plan_id)
                .values(**values)
                .returning(models.Plan.id)
            )
            if result.first() is None:
                # Plan has been deleted in the middle of validation. Nothing
                # to see here, move on
                detail = f"Plan {plan_id} no longer found in database!"
                LOGGER.info(detail)
                return detail
            session.commit()

        LOGGER.info(detail)
        LOGGER.info("Ryhti response: %s", json.dumps(response))
        return detail

    def finalize_plan(self, plan_id: str) -> FinalizeResult:
        """Mark the plan final and repeal the plans and plan objects it cancels.

        The cancellation info is refreshed first, while the plans it names are
        still valid: hame.repealed_plans reads hame.plan_valid, which a repealed
        plan leaves as soon as it gets the repealed lifecycle status. Only whole
        cancellations are repealed; a partly cancelled plan or plan object stays
        valid and its remaining valid geometry says what is left of it.

        When a whole plan is repealed, hame.trg_plan_repealed (see
        generate_plan_repealed_triggers in database/triggers.py) repeals its
        plan objects, regulations and propositions as well. The plan object
        updates below are for plan objects repealed one by one.

        Raises PlanNotFoundError if the plan does not exist and
        PlanAlreadyFinalError if it is final already.
        """
        with self.Session() as session:
            # Read and lock only the columns that are needed. session.get would
            # load the eagerly joined code tables as well, and PostgreSQL cannot
            # lock the nullable side of an outer join.
            row = session.execute(
                select(models.Plan.final, models.Plan.period_of_validity_start)
                .where(models.Plan.id == plan_id)
                .with_for_update()
            ).first()
            if row is None:
                raise PlanNotFoundError(UUID(plan_id))
            already_final, period_of_validity_start = row
            if already_final:
                raise PlanAlreadyFinalError(plan_id)

            repealed_status_id = session.scalar(
                select(codes.LifeCycleStatus.id).where(
                    codes.LifeCycleStatus.value == LifeCycleStatusValue.REPEALED
                )
            )
            if repealed_status_id is None:
                raise RepealedStatusNotFoundError

            # The update trigger of hame.plan refreshes the cancellation info
            # only when the geometry or the plan matter changes, so the rows may
            # be older than the plans they name.
            session.execute(
                text("select hame.refresh_plan_cancellation_info(:plan_id)"),
                {"plan_id": plan_id},
            )

            # A repealed plan ends on the day this plan begins, as Ryhti does.
            # hame.plan_valid treats the end date as inclusive, so both plans
            # show as valid on that one day; this matches Ryhti.
            start_date = (
                period_of_validity_start or datetime.datetime.now(tz=LOCAL_TZ).date()
            )
            repealed_values: dict[str, Any] = {
                "lifecycle_status_id": repealed_status_id,
                "period_of_validity_end": start_date,
            }

            cancelled_plan_ids = select(
                models.PlanCancellationInfo.cancelled_plan_id
            ).where(
                models.PlanCancellationInfo.plan_id == plan_id,
                models.PlanCancellationInfo.cancels_entire_plan,
            )
            result = FinalizeResult(
                repealed_plans=len(
                    session.execute(
                        update(models.Plan)
                        .where(models.Plan.id.in_(cancelled_plan_ids))
                        .values(**repealed_values)
                        .returning(models.Plan.id)
                    ).all()
                )
            )

            for plan_object, id_column in CANCELLED_PLAN_OBJECTS:
                cancelled_object_ids = (
                    select(id_column)
                    .join(models.PlanObjectCancellationInfo.plan_cancellation_info)
                    .where(
                        models.PlanCancellationInfo.plan_id == plan_id,
                        models.PlanObjectCancellationInfo.cancels_entire_plan_object,
                        id_column.is_not(None),
                    )
                )
                result.repealed_plan_objects += len(
                    session.execute(
                        update(plan_object)
                        .where(plan_object.id.in_(cancelled_object_ids))
                        .values(**repealed_values)
                        .returning(plan_object.id)
                    ).all()
                )

            session.execute(
                update(models.Plan).where(models.Plan.id == plan_id).values(final=True)
            )
            session.commit()

        return result

    def set_plan_documents(
        self,
        plan: models.Plan,
        responses: list[RyhtiResponse],
        ryhti_plan: RyhtiPlan | None = None,
    ) -> None:
        """Save uploaded plan document keys, export times and etags to the database.

        The responses must come from upload_plan_documents called with the *same*
        plan instance, so that they pair up with plan.documents in order.

        If a Ryhti plan is provided, the documents are also added to it.
        """
        with self.Session(expire_on_commit=False) as session:
            session.add(plan)
            for document, document_response in zip(
                plan.documents, responses, strict=True
            ):
                session.add(document)
                if document_response["status"] == 201:
                    document.exported_file_key = UUID(document_response["detail"])
                    document.exported_at = datetime.datetime.now(tz=LOCAL_TZ)
                    # Save the etag of the uploaded file, piggybacked in response
                    if document_response["warnings"]:
                        document.exported_file_etag = document_response["warnings"][
                            "ETag"
                        ]
                # We can only serialize the document after it has been uploaded
                if ryhti_plan is not None:
                    self.serializer.add_document_to_plan(document, ryhti_plan)
            session.commit()

    def set_permanent_plan_identifier(
        self, plan_matter: models.PlanMatter, response: RyhtiResponse
    ) -> str:
        """Save permanent plan identifier returned by RYHTI API to the database."""
        detail = ""
        with self.Session(expire_on_commit=False) as session:
            # Make sure that the plan matter instance stays up to date
            session.add(plan_matter)
            if response["status"] == 200:
                plan_matter.permanent_plan_identifier = response["detail"]
                detail = cast("str", response["detail"])
            elif response["status"] == 401:
                detail = "Sinulla ei ole oikeuksia luoda kaavaa tälle alueelle."
            elif response["status"] == 400:
                detail = "Kaava-asialta puuttuu tuottajan kaavatunnus."
            session.commit()
        return detail

    def import_plan(
        self, plan_json: str, extra_data_dict: dict[str, Any], overwrite: bool = False
    ) -> DbId | None:
        ryhti_plan = ryhti_plan_from_json(plan_json)
        extra_data = extra_import_data_from_dict(extra_data_dict)

        with self.Session(autoflush=False, expire_on_commit=False) as session:
            plan_matter = session.get(models.PlanMatter, extra_data.plan_matter_id)
            if not plan_matter:
                raise PlanMatterNotFoundError(extra_data.plan_matter_id)

            existing_plan = session.get(models.Plan, ryhti_plan.plan_key)
            if existing_plan:
                if overwrite is True:
                    session.delete(existing_plan)
                    session.flush()
                else:
                    raise PlanAlreadyExistsError(str(ryhti_plan.plan_key))

            desesrializer = Deserializer(session)
            plan = desesrializer.deserialise_ryhti_plan(
                ryhti_plan, plan_matter.plan_type, extra_data.name
            )

            plan_matter.plans.append(plan)
            session.add(plan_matter)
            session.commit()

        return plan.id

    @contextmanager
    def _disable_edit_triggers(self, session: Session) -> Generator[None]:
        """Temporarily disable all triggers on all tables in hame schema."""
        triggers_to_disable = [
            Template("trg_${table}_created_at"),
            Template("trg_${table}_001_no_created_at_update"),
            Template("trg_${table}_modified_at"),
        ]

        def _alter_triggers(state: str) -> None:
            for schema, table in base.VersionedBase.subclass_names():
                if schema != "hame":
                    continue
                for trigger_template in triggers_to_disable:
                    trigger_name = trigger_template.substitute(table=table)
                    disable_sql = text(
                        f"ALTER TABLE {schema}.{table} {state} TRIGGER {trigger_name}"
                    )
                    session.execute(disable_sql)

        _alter_triggers("DISABLE")
        try:
            yield
        finally:
            _alter_triggers("ENABLE")

    def copy_plan(self, plan_id: str, copy_data: CopyPlanData) -> DbId | None:
        """Deep copy plan instance with all associated child objects and relationships."""
        with self.Session(autoflush=False, expire_on_commit=False) as session:
            plan = session.get(models.Plan, plan_id)
            if plan is None:
                raise PlanNotFoundError(UUID(plan_id))

            new_lifecycle_status = None
            approval_date = None
            period_of_validity_start = None
            if not copy_data.deep_copy:
                new_lifecycle_status = session.get(
                    codes.LifeCycleStatus, copy_data.lifecycle_status_id
                )
                if new_lifecycle_status is None:
                    raise LifeCycleStatusNotFoundError(
                        UUID(copy_data.lifecycle_status_id)
                    )

                approval_date = copy_data.approval_date or plan.approval_date
                if (
                    int(new_lifecycle_status.value)
                    >= int(LifeCycleStatusValue.APPORVED)
                    and not approval_date
                ):
                    raise ApprovalDateRequiredError

                period_of_validity_start = (
                    copy_data.period_of_validity_start or plan.period_of_validity_start
                )
                if (
                    int(new_lifecycle_status.value) >= int(LifeCycleStatusValue.VALID)
                    or (
                        is_under_appeal(
                            LifeCycleStatusValue(new_lifecycle_status.value)
                        )
                        and copy_data.under_appeal_scope
                        == UnderAppealScopeOption.PARTIALLY_VALID
                    )
                ) and not period_of_validity_start:
                    raise StartDateRequiredError

            plan_copier = PlanCopier(
                session=session,
                plan=plan,
                lifecycle_status=new_lifecycle_status,
                plan_name=copy_data.plan_name,
                under_appeal_scope=copy_data.under_appeal_scope,
                keep_under_appeal_lifecycle=copy_data.keep_under_appeal_lifecycle,
                deep_copy=copy_data.deep_copy,
                approval_date=approval_date,
                period_of_validity_start=period_of_validity_start,
                lock=copy_data.lock,
            )
            with self._disable_edit_triggers(session):
                copied_plan = plan_copier.copy_plan()
                session.add(copied_plan)
                # do the actual insert while the triggers are still disabled to avoid
                # created_at and modified_at updates.
                session.flush()
            session.commit()

            return copied_plan.id
