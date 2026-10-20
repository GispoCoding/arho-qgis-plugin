"""What the user sees while a lambda job runs: disabled actions, the job status, no second start."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from qgis.PyQt import sip

from arho_feature_template.core.lambda_client import JobStatus
from arho_feature_template.core.lambda_service import LambdaService
from arho_feature_template.gui.components.lambda_job_status import LambdaJobStatus
from arho_feature_template.gui.dialogs.import_plan_form import ImportPlanForm
from arho_feature_template.gui.dialogs.post_plan import PostPlanDialog

if TYPE_CHECKING:
    from qgis.gui import QgisInterface

    from arho_feature_template.plugin import Plugin

pytestmark = pytest.mark.fake_iface


def _job_items(iface: QgisInterface) -> list:
    return [item for item in iface.messageBar().items() if not sip.isdeleted(item)]


def test_export_action_is_disabled_while_its_job_runs(plugin: Plugin, iface: QgisInterface):
    service = plugin.plan_manager.lambda_service
    action = plugin.serialize_plan_action
    assert action.isEnabled()

    service.busy_changed.emit(LambdaService.ACTION_GET_PLAN, True)
    assert not action.isEnabled()
    [item] = _job_items(iface)
    assert item.title() == "Kaavasuunnitelman tallennus"

    service.job_status_changed.emit(LambdaService.ACTION_GET_PLAN, JobStatus.RUNNING)
    assert item.text() == "Käynnissä…"

    service.busy_changed.emit(LambdaService.ACTION_GET_PLAN, False)
    assert action.isEnabled()
    assert plugin.lambda_job_messages == {}


def test_plan_change_keeps_a_busy_action_disabled(plugin: Plugin, monkeypatch: pytest.MonkeyPatch):
    service = plugin.plan_manager.lambda_service
    monkeypatch.setattr(service, "is_busy", lambda action=None: action == LambdaService.ACTION_GET_PERMANENT_IDENTIFIER)
    service.busy_changed.emit(LambdaService.ACTION_GET_PERMANENT_IDENTIFIER, True)

    plugin.on_active_plan_set()

    assert not plugin.get_permanent_identifier_action.isEnabled()
    assert plugin.edit_plan_action.isEnabled()


@pytest.fixture
def import_form(iface: QgisInterface):
    form = ImportPlanForm(iface.mainWindow())
    form.show()
    yield form
    form.done(0)
    form.deleteLater()


def _set_busy(service: LambdaService, action: str, busy: bool):
    """Puts the service in the state it has while the action waits for its answer."""
    if busy:
        service._client._busy.add(action)
    else:
        service._client._busy.discard(action)
    service.busy_changed.emit(action, busy)


def test_dialog_shows_the_job_status(import_form: ImportPlanForm):
    service = import_form.lambda_service
    _set_busy(service, LambdaService.ACTION_IMPORT_PLAN, True)
    assert import_form.label_job_status.text() == LambdaJobStatus.SENDING_TEXT
    service.job_status_changed.emit(LambdaService.ACTION_IMPORT_PLAN, JobStatus.QUEUED)
    assert import_form.label_job_status.text() == "Jonossa…"
    service.job_status_changed.emit(LambdaService.ACTION_IMPORT_PLAN, JobStatus.RUNNING)
    assert import_form.label_job_status.text() == "Käynnissä…"
    _set_busy(service, LambdaService.ACTION_IMPORT_PLAN, False)
    assert import_form.label_job_status.text() == ""


def test_dialog_stays_open_while_its_job_runs(import_form: ImportPlanForm):
    service = import_form.lambda_service
    _set_busy(service, LambdaService.ACTION_IMPORT_PLAN, True)

    import_form.reject()  # Cancel, Esc and the window close button
    assert import_form.isVisible()
    assert import_form.label_job_status.text() == LambdaJobStatus.WAIT_TEXT

    _set_busy(service, LambdaService.ACTION_IMPORT_PLAN, False)
    import_form.reject()
    assert not import_form.isVisible()


def test_failed_post_stops_the_busy_indicator(iface: QgisInterface):
    dialog = PostPlanDialog(iface.mainWindow())
    dialog.start_timer.stop()
    dialog.show()
    dialog.progress_bar.show()

    _set_busy(dialog.lambda_service, LambdaService.ACTION_POST_PLAN_MATTERS, True)
    _set_busy(dialog.lambda_service, LambdaService.ACTION_POST_PLAN_MATTERS, False)

    assert not dialog.progress_bar.isVisible()
    dialog.done(0)
    dialog.deleteLater()


def test_closed_job_message_is_not_touched_again(plugin: Plugin, iface: QgisInterface):
    service = plugin.plan_manager.lambda_service
    # Qt reports a hidden action as disabled; the button shows for a plan that can be made final
    plugin.on_plan_finalizable_changed(True)
    service.busy_changed.emit(LambdaService.ACTION_FINALIZE_PLAN, True)
    assert not plugin.finalize_plan_action.isEnabled()
    iface.messageBar().clearWidgets()  # the user closes the message
    for item in _job_items(iface):
        sip.delete(item)

    service.job_status_changed.emit(LambdaService.ACTION_FINALIZE_PLAN, JobStatus.RUNNING)
    service.busy_changed.emit(LambdaService.ACTION_FINALIZE_PLAN, False)

    assert plugin.finalize_plan_action.isEnabled()


def test_import_dialog_does_not_block_qgis(plugin: Plugin, monkeypatch: pytest.MonkeyPatch):
    manager = plugin.plan_manager
    activated: list[str | None] = []
    monkeypatch.setattr(manager, "set_active_plan", activated.append)

    manager.open_import_plan_dialog()
    form = manager.import_plan_form
    assert form is not None
    assert form.isVisible()
    assert not form.isModal()

    # A second click brings the open dialog to the front, so there is one import at a time
    manager.open_import_plan_dialog()
    assert manager.import_plan_form is form

    form.plan_imported("22222222-2222-2222-2222-222222222222")
    assert activated == ["22222222-2222-2222-2222-222222222222"]
    assert manager.import_plan_form is None


def test_post_dialog_does_not_block_qgis(plugin: Plugin, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(PostPlanDialog, "start_post_plan", lambda _self: None)
    plugin.post_plan_matter()
    dialog = plugin.post_plan_dialog
    assert dialog is not None
    assert dialog.isVisible()
    assert not dialog.isModal()

    plugin.post_plan_matter()
    assert plugin.post_plan_dialog is dialog

    dialog.reject()
    assert plugin.post_plan_dialog is None


def test_unload_closes_dialogs_with_a_running_job(plugin_factory, monkeypatch, flush_deferred_deletes):
    monkeypatch.setattr(PostPlanDialog, "start_post_plan", lambda _self: None)
    plugin = plugin_factory()
    plugin.plan_manager.open_import_plan_dialog()
    plugin.post_plan_matter()
    form = plugin.plan_manager.import_plan_form
    dialog = plugin.post_plan_dialog
    _set_busy(form.lambda_service, LambdaService.ACTION_IMPORT_PLAN, True)
    _set_busy(dialog.lambda_service, LambdaService.ACTION_POST_PLAN_MATTERS, True)

    plugin.unload()
    flush_deferred_deletes()

    assert sip.isdeleted(form)
    assert sip.isdeleted(dialog)
    assert plugin.plan_manager.import_plan_form is None
    assert plugin.post_plan_dialog is None
