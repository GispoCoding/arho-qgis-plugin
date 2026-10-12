"""Run ryhti_client actions as background jobs.

The API gateway cuts every request at 29 seconds, so a caller may submit a
request as a job and poll for its answer instead. A job row in jobs.job holds
the request, the state of the job and, when the job is done, the answer that a
synchronous call would have got.

How a job starts differs between environments, so the caller passes a starter
to submit. The starters live in lambda_function.py, chosen by JOB_RUNNER.
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import simplejson as json
from sqlalchemy import create_engine, func, update
from sqlalchemy.orm import sessionmaker

from database.enums import JobStatus
from database.models import Job

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping

LOGGER = logging.getLogger(__name__)

# Stored for a job that crashed. The exception itself goes to the log only.
JOB_FAILED_ERROR = "The job failed. Please contact Arho support team."

# Runs the action of a stored request and returns the answer, {statusCode,
# body}, exactly as a synchronous call would get it.
type ActionRunner = Callable[[dict[str, Any]], Mapping[str, Any]]

# Starts the job with the given id.
type JobStarter = Callable[[str], None]


@dataclass(frozen=True)
class JobState:
    """What a caller may see of a job."""

    job_id: str
    status: JobStatus
    result: dict[str, Any] | None
    error: str | None


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


class JobStore:
    """Submit, run and read the jobs in jobs.job."""

    def __init__(self, connection_string: str) -> None:
        # The answers are written with simplejson, as the handler writes them.
        engine = create_engine(connection_string, json_serializer=json.dumps)
        self.Session = sessionmaker(bind=engine)

    def submit(self, request: dict[str, Any], start: JobStarter) -> str:
        """Store the request as a queued job, start the job and return its id."""
        job = Job(
            action=request["action"],
            plan_id=plan_id_of(request),
            request=request,
            status=JobStatus.QUEUED,
        )
        with self.Session() as session:
            session.add(job)
            session.commit()
            job_id = job.id
        start(job_id)
        return job_id

    def run(self, job_id: str, run_action: ActionRunner) -> None:
        """Run a queued job and store how it ended.

        The job is claimed from queued to running in one statement, so a job
        that is started twice runs only once. A job that is not queued is left
        as it is.
        """
        request = self._claim(job_id)
        if request is None:
            LOGGER.warning("Job %s is not queued, so it is not run.", job_id)
            return
        try:
            answer = run_action(request)
        except Exception:
            LOGGER.exception("Job %s crashed.", job_id)
            self._finish(job_id, status=JobStatus.FAILED, error=JOB_FAILED_ERROR)
        else:
            self._finish(job_id, status=JobStatus.DONE, result=dict(answer))

    def get(self, job_id: str) -> JobState | None:
        """Return the state of the job, or None if there is no such job."""
        with self.Session() as session:
            job = session.get(Job, job_id)
            if job is None:
                return None
            return JobState(
                job_id=job.id, status=job.status, result=job.result, error=job.error
            )

    def _claim(self, job_id: str) -> dict[str, Any] | None:
        """Move a queued job to running and return its request.

        Returns None when the job is not queued.
        """
        with self.Session() as session:
            request = session.execute(
                update(Job)
                .where(Job.id == job_id, Job.status == JobStatus.QUEUED)
                .values(status=JobStatus.RUNNING, started_at=func.now())
                .returning(Job.request)
            ).scalar_one_or_none()
            session.commit()
        return request

    def _finish(self, job_id: str, **values: Any) -> None:  # noqa: ANN401
        """Store the end state of a running job."""
        with self.Session() as session:
            session.execute(
                update(Job)
                .where(Job.id == job_id)
                .values(finished_at=func.now(), **values)
            )
            session.commit()
