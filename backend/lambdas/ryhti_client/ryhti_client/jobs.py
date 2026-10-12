"""Run ryhti_client actions as background jobs.

The API gateway cuts every request at 29 seconds, so a caller may submit a
request as a job and poll for its answer instead. A job row in jobs.job holds
the request, the state of the job and, when the job is done, the answer that a
synchronous call would have got.

How a job starts differs between environments, so the caller passes a starter
to submit, chosen by JOB_RUNNER in lambda_function.py. The starter for AWS,
lambda_job_starter, lives here, so that it can be tested without AWS.
"""

from __future__ import annotations

import logging
import time
import uuid
from dataclasses import dataclass
from datetime import timedelta
from typing import TYPE_CHECKING, Any, Protocol

import simplejson as json
from botocore.exceptions import BotoCoreError, ClientError
from sqlalchemy import and_, create_engine, delete, func, not_, or_, select, update
from sqlalchemy.orm import sessionmaker

from database.enums import JobStatus
from database.models import Job

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping

    from sqlalchemy import ColumnElement

LOGGER = logging.getLogger(__name__)

# Stored for a job that crashed. The exception itself goes to the log only.
JOB_FAILED_ERROR = "The job failed. Please contact Arho support team."

# A job is deleted this long after it was created, so the table does not grow
# without limit.
JOB_RETENTION = timedelta(days=7)

# Runs the action of a stored request and returns the answer, {statusCode,
# body}, exactly as a synchronous call would get it. The request is the JSON
# that submit stored. Its type belongs to the runner, so it is Any here.
type ActionRunner = Callable[[Any], Mapping[str, Any]]

# Starts the job with the given id.
type JobStarter = Callable[[str], None]


class LambdaClient(Protocol):
    """The part of the boto3 Lambda client that starts a job."""

    def invoke(
        self,
        *,
        FunctionName: str,  # noqa: N803  # the boto3 argument names
        InvocationType: str,  # noqa: N803
        Payload: str,  # noqa: N803
    ) -> Mapping[str, Any]: ...


class JobNotStartedError(Exception):
    """The job could not be started, so it is stored as failed."""

    def __init__(self, job_id: str) -> None:
        super().__init__(f"Job {job_id} could not be started.")
        self.job_id = job_id


@dataclass(frozen=True)
class JobState:
    """What a caller may see of a job."""

    job_id: str
    status: JobStatus
    result: dict[str, Any] | None
    error: str | None


@dataclass(frozen=True)
class ClaimedJob:
    """A job that a run has moved from queued to running."""

    action: str
    request: dict[str, Any]
    # From the creation of the job to its start.
    waited: timedelta


def is_uuid(value: object) -> bool:
    """Return True if the value is a string that holds a UUID."""
    if not isinstance(value, str):
        return False
    try:
        uuid.UUID(value)
    except ValueError:
        return False
    return True


def plan_id_of(request: Mapping[str, Any]) -> str | None:
    """Return the plan_uuid of the request when it is a valid UUID.

    The request check validates plan_uuid for the plan actions only. The other
    actions ignore it, so it may hold anything there and is not stored.
    """
    plan_uuid = request.get("plan_uuid")
    if is_uuid(plan_uuid):
        return plan_uuid
    return None


def past_time_limit(time_limit: timedelta) -> ColumnElement[bool]:
    """Return the condition that a job is still queued time_limit after it was
    created, or still running time_limit after it started.

    The database evaluates it with its own clock, which also sets created_at
    and started_at. JobStore.get and the claim use the same condition, so a job
    that get reports as failed is never claimed later.
    """
    cutoff = func.now() - time_limit
    return or_(
        and_(Job.status == JobStatus.QUEUED, Job.created_at < cutoff),
        and_(Job.status == JobStatus.RUNNING, Job.started_at < cutoff),
    )


class JobStore:
    """Submit, run and read the jobs in jobs.job."""

    def __init__(self, connection_string: str, time_limit: timedelta) -> None:
        """Connect to the database.

        Args:
            connection_string: The database to keep the jobs in.
            time_limit: A job still queued or running this long after it was
                created or started has crashed. It equals the lambda timeout.
        """
        # The answers are written with simplejson, as the handler writes them.
        engine = create_engine(connection_string, json_serializer=json.dumps)
        self.Session = sessionmaker(bind=engine)
        self.time_limit = time_limit

    def submit(self, request: dict[str, Any], start: JobStarter) -> str:
        """Store the request as a queued job, start the job and return its id.

        Jobs older than JOB_RETENTION are deleted at the same time.
        """
        job = Job(
            action=request["action"],
            plan_id=plan_id_of(request),
            request=request,
            status=JobStatus.QUEUED,
        )
        with self.Session() as session:
            session.add(job)
            session.execute(
                delete(Job).where(Job.created_at < func.now() - JOB_RETENTION)
            )
            session.commit()
            job_id = job.id
        start(job_id)
        return job_id

    def run(self, job_id: str, run_action: ActionRunner) -> str | None:
        """Run a queued job, store how it ended and return its action.

        The job is claimed from queued to running in one statement, so a job
        that is started twice runs only once. A job that is not queued, or is
        past the time limit, is left as it is, and None is returned.
        """
        job = self._claim(job_id)
        if job is None:
            LOGGER.warning(
                "Job %s is not queued or is past the time limit, so it is not run.",
                job_id,
            )
            return None
        start = time.perf_counter()
        try:
            answer = run_action(job.request)
        except Exception:
            LOGGER.exception("Job %s crashed.", job_id)
            self.fail(job_id)
        else:
            self._finish(job_id, status=JobStatus.DONE, result=dict(answer))
        # Not "arho_timing action=", so that the per-invocation duration query
        # does not count job runs twice.
        LOGGER.info(
            "arho_timing job_id=%s action=%s wait_ms=%d duration_ms=%d",
            job_id,
            job.action,
            round(job.waited.total_seconds() * 1000),
            round((time.perf_counter() - start) * 1000),
        )
        return job.action

    def fail(self, job_id: str) -> None:
        """Store the job as failed, with the generic error."""
        self._finish(job_id, status=JobStatus.FAILED, error=JOB_FAILED_ERROR)

    def get(self, job_id: str) -> JobState | None:
        """Return the state of the job, or None if there is no such job.

        A job that crashed hard (a lambda timeout, out of memory) cannot store
        its own failure, so a job past the time limit is reported as failed.
        """
        with self.Session() as session:
            row = session.execute(
                select(Job, past_time_limit(self.time_limit)).where(Job.id == job_id)
            ).one_or_none()
            if row is None:
                return None
            job, is_past_time_limit = row
            if is_past_time_limit:
                return JobState(
                    job_id=job.id,
                    status=JobStatus.FAILED,
                    result=None,
                    error=JOB_FAILED_ERROR,
                )
            return JobState(
                job_id=job.id, status=job.status, result=job.result, error=job.error
            )

    def _claim(self, job_id: str) -> ClaimedJob | None:
        """Move a queued job to running and return what the run needs.

        Returns None when the job is not queued, or when it is past the time
        limit: get already reports such a job as failed, so a late worker event
        must not run it.
        """
        with self.Session() as session:
            row = session.execute(
                update(Job)
                .where(
                    Job.id == job_id,
                    Job.status == JobStatus.QUEUED,
                    not_(past_time_limit(self.time_limit)),
                )
                .values(status=JobStatus.RUNNING, started_at=func.now())
                .returning(Job.action, Job.request, Job.started_at - Job.created_at)
            ).one_or_none()
            session.commit()
        if row is None:
            return None
        action, request, waited = row
        return ClaimedJob(action=action, request=request, waited=waited)

    def _finish(self, job_id: str, **values: Any) -> None:  # noqa: ANN401
        """Store the end state of a job."""
        with self.Session() as session:
            session.execute(
                update(Job)
                .where(Job.id == job_id)
                .values(finished_at=func.now(), **values)
            )
            session.commit()


def worker_event(job_id: str) -> dict[str, str]:
    """Return the event that runs the job in a new invocation: its id only."""
    return {"job_id": job_id}


def is_worker_event(event: object) -> bool:
    """Return True if the event is a worker event, as worker_event builds it.

    Only a direct invocation can be one: an API gateway request has more keys
    than the job id, so a caller of the API cannot run a job.
    """
    return isinstance(event, dict) and event.keys() == {"job_id"}


def lambda_job_starter(
    store: JobStore, client: LambdaClient, function_arn: str
) -> JobStarter:
    """Return a starter that runs each job in a new invocation of this function.

    The Event invocation answers at once, and the job runs in the background.
    function_arn is the qualified ARN the current invocation was called with,
    so the job runs on the same code as its submit call.

    If the invocation fails, the job is stored as failed and the starter raises
    JobNotStartedError.
    """

    def invoke(job_id: str) -> None:
        try:
            client.invoke(
                FunctionName=function_arn,
                InvocationType="Event",
                Payload=json.dumps(worker_event(job_id)),
            )
        except (BotoCoreError, ClientError) as error:
            LOGGER.exception("Job %s could not be started.", job_id)
            store.fail(job_id)
            raise JobNotStartedError(job_id) from error

    return invoke
