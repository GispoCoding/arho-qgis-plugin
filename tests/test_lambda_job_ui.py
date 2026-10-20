"""What the user sees while a lambda job runs: disabled actions, the job status, no second start."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from qgis.PyQt import sip

from arho_feature_template.core.lambda_client import JobStatus
from arho_feature_template.core.lambda_service import LambdaService

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
