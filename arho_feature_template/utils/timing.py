"""Small timing helpers for diagnosing slow save paths.

Every block logs one line to the `arho_feature_template.timing` logger:

    TIMING  |   +-- add_to_edit_buffer[Kaavamaarays] 412.3 ms

Indentation shows nesting, so a slow parent and its slow child are easy to pair.
Set the logger to INFO to see the lines, or to WARNING to silence them.
"""

from __future__ import annotations

import logging
import threading
from contextlib import contextmanager
from functools import wraps
from time import perf_counter
from typing import Any, Callable, Generator, TypeVar

logger = logging.getLogger("arho_feature_template.timing")

_local = threading.local()

F = TypeVar("F", bound=Callable[..., Any])


def _depth() -> int:
    return getattr(_local, "depth", 0)


def _set_depth(value: int) -> None:
    _local.depth = value


@contextmanager
def timed(label: str, **context: Any) -> Generator[None]:
    """Log how long the block took."""
    depth = _depth()
    _set_depth(depth + 1)
    start = perf_counter()
    try:
        yield
    finally:
        elapsed_ms = (perf_counter() - start) * 1000
        _set_depth(depth)
        if logger.isEnabledFor(logging.INFO):
            indent = "|   " * depth
            extra = " ".join(f"{key}={value}" for key, value in context.items())
            logger.info("TIMING %s+-- %s %.1f ms %s", indent, label, elapsed_ms, extra)


def timed_function(label: str | None = None) -> Callable[[F], F]:
    """Decorator form of `timed`."""

    def decorator(func: F) -> F:
        name = label or func.__qualname__

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            with timed(name):
                return func(*args, **kwargs)

        return wrapper  # type: ignore[return-value]

    return decorator
