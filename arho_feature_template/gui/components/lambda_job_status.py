from __future__ import annotations

from arho_feature_template.core.lambda_client import JobStatus


def job_status_text(status: str) -> str:
    """The text that tells the user what a job does now."""
    texts: dict[str, str] = {JobStatus.QUEUED: "Jonossa…", JobStatus.RUNNING: "Käynnissä…"}
    return texts.get(status, "Käynnissä…")
