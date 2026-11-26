from __future__ import annotations

from typing import TYPE_CHECKING

from qgis.PyQt.QtCore import QObject

from arho_feature_template.core.lambda_client import JobStatus

if TYPE_CHECKING:
    from qgis.PyQt.QtWidgets import QLabel

    from arho_feature_template.core.lambda_service import LambdaService


def job_status_text(status: str) -> str:
    """The text that tells the user what a job does now."""
    texts: dict[str, str] = {JobStatus.QUEUED: "Jonossa…", JobStatus.RUNNING: "Käynnissä…"}
    return texts.get(status, "Käynnissä…")


class LambdaJobStatus(QObject):
    """Shows the state of a dialog's lambda job in a label, and keeps the dialog open while the job runs.

    A job cannot be cancelled. If the dialog closed, the user could start the same job again
    while the first one still runs, and the backend does not stop two jobs on the same plan.
    """

    SENDING_TEXT = "Lähetetään…"
    WAIT_TEXT = "Odota, toiminto on käynnissä taustapalvelussa."

    def __init__(self, service: LambdaService, label: QLabel):
        super().__init__(label)
        self._service = service
        self._label = label
        service.busy_changed.connect(self._on_busy_changed)
        service.job_status_changed.connect(self._on_job_status_changed)

    def refuse_close(self) -> bool:
        """True, and asks the user to wait, while a request or job of the dialog runs."""
        if not self._service.is_busy():
            return False
        self._label.setText(self.WAIT_TEXT)
        return True

    def _on_busy_changed(self, _action: str, busy: bool):  # noqa: FBT001
        self._label.setText(self.SENDING_TEXT if busy else "")

    def _on_job_status_changed(self, _action: str, status: str):
        self._label.setText(job_status_text(status))
