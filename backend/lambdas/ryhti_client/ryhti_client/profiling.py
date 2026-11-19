"""Timing and profiling helpers for debugging slow ryhti_client actions.

Step timings are always logged, because they are cheap. Counting SQL statements
and profiling Python calls costs more, so those are switched on with the
PROFILE_SQL and PROFILE_PYTHON environment variables.
"""

from __future__ import annotations

import cProfile
import io
import logging
import os
import pstats
import time
from collections import defaultdict
from contextlib import contextmanager
from typing import TYPE_CHECKING

from sqlalchemy import event

if TYPE_CHECKING:
    from collections.abc import Generator

    from sqlalchemy.engine import Connection, Engine

LOGGER = logging.getLogger(__name__)

# Statements are grouped by their first characters, so that the same query with
# different parameters is counted together.
SQL_KEY_LENGTH = 120
# How many rows of the Python profile and the SQL summary are logged.
PROFILE_ROW_COUNT = 30
SQL_SUMMARY_ROW_COUNT = 15


def sql_profiling_enabled() -> bool:
    return os.environ.get("PROFILE_SQL") == "1"


def python_profiling_enabled() -> bool:
    return os.environ.get("PROFILE_PYTHON") == "1"


@contextmanager
def log_duration(step: str) -> Generator[None]:
    """Log the wall time of a single step of an action.

    The line uses the same arho_timing prefix as the handler duration log, so
    CloudWatch Logs Insights can query steps and whole actions together.
    """
    start = time.perf_counter()
    try:
        yield
    finally:
        LOGGER.info(
            "arho_timing step=%s duration_ms=%d",
            step,
            round((time.perf_counter() - start) * 1000),
        )


@contextmanager
def profile_python(label: str) -> Generator[None]:
    """Log the slowest Python calls in the block when PROFILE_PYTHON is set."""
    if not python_profiling_enabled():
        yield
        return

    profile = cProfile.Profile()
    profile.enable()
    try:
        yield
    finally:
        profile.disable()
        stream = io.StringIO()
        stats = pstats.Stats(profile, stream=stream).sort_stats("cumulative")
        stats.print_stats(PROFILE_ROW_COUNT)
        LOGGER.info("arho_profile label=%s\n%s", label, stream.getvalue())


class QueryProfiler:
    """Counts the SQL statements executed on one engine and how long they took."""

    def __init__(self) -> None:
        self.counts: defaultdict[str, int] = defaultdict(int)
        self.durations: defaultdict[str, float] = defaultdict(float)

    def attach(self, engine: Engine) -> None:
        """Start recording every statement executed on the engine."""
        event.listen(engine, "before_cursor_execute", self._before_cursor_execute)
        event.listen(engine, "after_cursor_execute", self._after_cursor_execute)

    def _before_cursor_execute(self, conn: Connection, *_: object) -> None:
        # Start times are stored on the connection, so that statements on
        # different connections cannot mix up their timers.
        conn.info.setdefault("query_start_times", []).append(time.perf_counter())

    def _after_cursor_execute(
        self, conn: Connection, _cursor: object, statement: str, *_: object
    ) -> None:
        elapsed = time.perf_counter() - conn.info["query_start_times"].pop()
        key = " ".join(statement.split())[:SQL_KEY_LENGTH]
        self.counts[key] += 1
        self.durations[key] += elapsed

    def log_summary(self) -> None:
        """Log the total SQL time and the statements that took most of it.

        A high count on a single statement means the same query is repeated,
        which is the usual sign of a missing eager load.
        """
        LOGGER.info(
            "arho_timing step=sql_total duration_ms=%d queries=%d",
            round(sum(self.durations.values()) * 1000),
            sum(self.counts.values()),
        )
        slowest = sorted(self.durations.items(), key=lambda item: item[1], reverse=True)
        for key, seconds in slowest[:SQL_SUMMARY_ROW_COUNT]:
            LOGGER.info(
                "arho_sql count=%d duration_ms=%d sql=%s",
                self.counts[key],
                round(seconds * 1000),
                key,
            )


def attach_query_profiler(engine: Engine) -> QueryProfiler | None:
    """Returns a profiler recording the engine queries, or None when switched off."""
    if not sql_profiling_enabled():
        return None
    profiler = QueryProfiler()
    profiler.attach(engine)
    return profiler
