"""Tests for job mode, run inside the test process.

The local Lambda emulator cannot run an Event invocation, so the starter that
JOB_RUNNER=lambda uses, and the handler with that starter, are tested here with
a fake Lambda client. The rest of job mode is tested through the lambda
endpoint in test/test_services.py.
"""

from __future__ import annotations

import importlib.util
import json
import logging
import re
import sys
from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest
from botocore.exceptions import ClientError
from sqlalchemy import func, update

from database.enums import JobStatus
from database.models import Job
from ryhti_client.jobs import (
    JOB_FAILED_ERROR,
    JobNotStartedError,
    JobState,
    JobStore,
    lambda_job_starter,
)

if TYPE_CHECKING:
    from collections.abc import Callable
    from types import ModuleType

    from sqlalchemy.orm import Session

# The qualified ARN the current invocation was called with, here the live alias.
FUNCTION_ARN = "arn:aws:lambda:eu-north-1:123456789012:function:arho-ryhti_client:live"

REQUEST = {"action": "get_plan", "plan_uuid": "0b3c1e58-5d3e-4f4a-9b0e-6f7d2a1c9e11"}

# What the action runner answers for REQUEST.
ANSWER = {
    "statusCode": 404,
    "body": {"title": "Plan not found.", "details": None, "ryhti_response": None},
}


class FakeLambdaClient:
    """Records the invocations instead of sending them to AWS."""

    def __init__(self, error: Exception | None = None) -> None:
        self.invocations: list[dict[str, Any]] = []
        # Raised by every invocation, as boto3 raises a refused invocation.
        self.error = error

    def invoke(
        self,
        *,
        FunctionName: str,  # noqa: N803  # the boto3 argument names
        InvocationType: str,  # noqa: N803
        Payload: str,  # noqa: N803
    ) -> dict[str, Any]:
        self.invocations.append(
            {
                "FunctionName": FunctionName,
                "InvocationType": InvocationType,
                "Payload": json.loads(Payload),
            }
        )
        if self.error is not None:
            raise self.error
        return {"StatusCode": 202}


@pytest.fixture
def store(dba_connection_string: str) -> JobStore:
    return JobStore(dba_connection_string)


def leave_queued(job_id: str) -> None:
    """A starter that does not start the job, so that the test can run it."""


def answer(request: dict[str, Any]) -> dict[str, Any]:
    """An action runner that answers like the action would."""
    return ANSWER


def crash(request: dict[str, Any]) -> dict[str, Any]:
    """An action runner that crashes."""
    raise RuntimeError("Lost the database connection.")


def make_older(session: Session, job_id: str, age: timedelta) -> None:
    """Move the creation of the job age into the past."""
    session.execute(
        update(Job).where(Job.id == job_id).values(created_at=func.now() - age)
    )
    session.commit()


def test_lambda_starter_invokes_this_function_with_the_job_id(store: JobStore) -> None:
    """The job starts in an Event invocation of the same function version."""
    client = FakeLambdaClient()

    job_id = store.submit(REQUEST, lambda_job_starter(store, client, FUNCTION_ARN))

    assert client.invocations == [
        {
            "FunctionName": FUNCTION_ARN,
            "InvocationType": "Event",
            "Payload": {"job_id": job_id},
        }
    ]
    job = store.get(job_id)
    assert job is not None
    assert job.status is JobStatus.QUEUED


def test_failed_invocation_fails_the_job(store: JobStore) -> None:
    """A job that cannot be started is failed, so that nobody polls it forever."""
    refused = ClientError(
        {"Error": {"Code": "AccessDeniedException", "Message": "Not allowed."}},
        "Invoke",
    )
    client = FakeLambdaClient(error=refused)

    with pytest.raises(JobNotStartedError) as raised:
        store.submit(REQUEST, lambda_job_starter(store, client, FUNCTION_ARN))

    job_id = raised.value.job_id
    assert store.get(job_id) == JobState(
        job_id=job_id, status=JobStatus.FAILED, result=None, error=JOB_FAILED_ERROR
    )


def test_job_that_is_not_queued_is_not_run(store: JobStore) -> None:
    """A second delivery of the same worker event leaves the job as it is."""
    job_id = store.submit(REQUEST, leave_queued)
    store.run(job_id, answer)
    second_run: list[dict[str, Any]] = []

    def record(request: dict[str, Any]) -> dict[str, Any]:
        second_run.append(request)
        return {"statusCode": 200, "body": {}}

    store.run(job_id, record)

    assert second_run == []
    assert store.get(job_id) == JobState(
        job_id=job_id, status=JobStatus.DONE, result=ANSWER, error=None
    )


def test_job_past_the_time_limit_is_not_run(store: JobStore, session: Session) -> None:
    """A late worker event cannot run a job that get_job already shows as failed."""
    job_id = store.submit(REQUEST, leave_queued)
    make_older(session, job_id, TIME_LIMIT + timedelta(minutes=1))
    late_run: list[dict[str, Any]] = []

    def record(request: dict[str, Any]) -> dict[str, Any]:
        late_run.append(request)
        return ANSWER

    store.run(job_id, record)

    assert late_run == []
    assert store.get(job_id) == JobState(
        job_id=job_id, status=JobStatus.FAILED, result=None, error=JOB_FAILED_ERROR
    )


def test_job_whose_action_raises_fails(store: JobStore) -> None:
    """A crash is stored as failed with the generic error, not the exception."""
    job_id = store.submit(REQUEST, leave_queued)

    store.run(job_id, crash)

    assert store.get(job_id) == JobState(
        job_id=job_id, status=JobStatus.FAILED, result=None, error=JOB_FAILED_ERROR
    )


# The line starts with "arho_timing job_id=", so the Logs Insights queries that
# filter on "arho_timing action=" or "arho_timing step=" do not match it.
JOB_TIMING_LINE = re.compile(
    r"arho_timing job_id=(?P<job_id>\S+) action=(?P<action>\S+) "
    r"wait_ms=(?P<wait_ms>\d+) duration_ms=(?P<duration_ms>\d+)"
)


@pytest.mark.parametrize("run_action", [answer, crash])
def test_job_run_logs_its_wait_and_run_time(
    store: JobStore,
    session: Session,
    caplog: pytest.LogCaptureFixture,
    run_action: Callable[[dict[str, Any]], dict[str, Any]],
) -> None:
    """Every job run, done or failed, logs one timing line with its job_id."""
    job_id = store.submit(REQUEST, leave_queued)
    # The job has waited three seconds for its worker.
    make_older(session, job_id, timedelta(seconds=3))

    with caplog.at_level(logging.INFO):
        store.run(job_id, run_action)

    timing_lines = [
        record.getMessage()
        for record in caplog.records
        if record.getMessage().startswith("arho_timing")
    ]
    assert len(timing_lines) == 1
    line = JOB_TIMING_LINE.fullmatch(timing_lines[0])
    assert line is not None, timing_lines[0]
    assert line["job_id"] == job_id
    assert line["action"] == "get_plan"
    assert 3000 <= int(line["wait_ms"]) < 60000


LAMBDA_FUNCTION = (
    Path(__file__).parents[2] / "lambdas" / "ryhti_client" / "lambda_function.py"
)


@dataclass(frozen=True)
class FakeContext:
    """The part of the Lambda context that the handler reads."""

    invoked_function_arn: str = FUNCTION_ARN


@pytest.fixture
def lambda_function(monkeypatch: pytest.MonkeyPatch) -> ModuleType:
    """The ryhti_client handler module with the job settings of AWS.

    The module reads its settings when it is imported, at the cold start of the
    lambda, so each test imports it anew.
    """
    monkeypatch.setenv("JOB_RUNNER", "lambda")
    monkeypatch.setenv("JOB_TIME_LIMIT_SECONDS", str(int(TIME_LIMIT.total_seconds())))
    monkeypatch.setenv("RYHTI_FILES_BUCKET", "ryhti-files")
    monkeypatch.setenv("SYKE_APIKEY", "test-apikey")
    monkeypatch.setenv("AWS_REGION_NAME", "eu-north-1")
    monkeypatch.delenv("READ_FROM_AWS", raising=False)
    monkeypatch.delenv("DEBUGPY", raising=False)
    spec = importlib.util.spec_from_file_location("lambda_function", LAMBDA_FUNCTION)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, "lambda_function", module)
    spec.loader.exec_module(module)
    return module


def test_submit_answers_502_when_the_job_cannot_be_started(
    lambda_function: ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The caller is told at once, instead of polling a job that never runs."""
    refused = ClientError(
        {"Error": {"Code": "TooManyRequestsException", "Message": "Rate exceeded."}},
        "Invoke",
    )
    monkeypatch.setattr(
        lambda_function, "lambda_client", FakeLambdaClient(error=refused)
    )

    answer = lambda_function.handler({**REQUEST, "run_as_job": True}, FakeContext())

    assert answer == {
        "statusCode": 502,
        "body": {
            "title": "Job could not be started.",
            "details": {
                "error": "The job could not be started. Please try again later."
            },
            "ryhti_response": None,
        },
    }


# The per-invocation line that the per-action duration query reads.
INVOCATION_TIMING_LINE = re.compile(
    r"arho_timing action=(?P<action>\S+) duration_ms=(?P<duration_ms>\d+)"
)


def logged_actions(caplog: pytest.LogCaptureFixture) -> list[str]:
    """Return the action names of the per-invocation timing lines, in order."""
    return [
        line["action"]
        for record in caplog.records
        if (line := INVOCATION_TIMING_LINE.fullmatch(record.getMessage()))
    ]


def test_submit_job_run_and_call_without_the_flag_log_separate_actions(
    lambda_function: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """The per-action duration query shows submits, job runs and calls without
    the job flag as separate rows.
    """
    client = FakeLambdaClient()
    monkeypatch.setattr(lambda_function, "lambda_client", client)

    with caplog.at_level(logging.INFO):
        lambda_function.handler({**REQUEST, "run_as_job": True}, FakeContext())
        worker_event = client.invocations[0]["Payload"]
        lambda_function.handler(worker_event, FakeContext())
        lambda_function.handler(REQUEST, FakeContext())

    assert logged_actions(caplog) == ["submit:get_plan", "job:get_plan", "get_plan"]


def test_get_job_ignores_the_job_flag_in_its_timing_line(
    lambda_function: ModuleType, caplog: pytest.LogCaptureFixture
) -> None:
    """A poll is no submit, even when the client sends the flag on every request."""
    poll = {
        "action": "get_job",
        "job_id": "8d0bd5a4-6a4f-4f0e-9a5e-0d1c7b0c5b9e",
        "run_as_job": True,
    }

    with caplog.at_level(logging.INFO):
        lambda_function.handler(poll, FakeContext())

    assert logged_actions(caplog) == ["get_job"]
