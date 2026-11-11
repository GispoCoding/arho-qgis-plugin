"""Making the active plan final from the toolbar.

The button "Aseta lopulliseksi" shows only for a valid plan that is not final yet. It asks
first, then sends the finalize_plan action. The backend answer either hides the button
and reports what was repealed, or lands the validation errors in the validation dock.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from qgis.PyQt.QtWidgets import QMessageBox

import arho_feature_template.core.plan_manager as plan_manager_module
from arho_feature_template.core.lifecycles import LifeCycleStatusValue
from arho_feature_template.core.models import Plan
from arho_feature_template.gui.components.validation_tree_view import ValidationModel

if TYPE_CHECKING:
    from collections.abc import Callable

    from arho_feature_template.plugin import Plugin
    from tests.fake_iface import MessageRecorder

pytestmark = pytest.mark.fake_iface

PLAN_ID = "11111111-1111-1111-1111-111111111111"
VALIDATION_ERRORS = {"status": 400, "errors": [{"ruleId": "plan.1", "message": "Puuttuu"}], "warnings": []}


def _plan(**attributes) -> Plan:
    return Plan(id_=PLAN_ID, name="Kaava", lifecycle_status_id="status-id", **attributes)


@pytest.fixture
def _active_plan(plugin: Plugin, monkeypatch: pytest.MonkeyPatch) -> None:  # noqa: ARG001 (plugin starts with no plan)
    """The plan under test is the active plan and nothing is unsaved."""
    monkeypatch.setattr(plan_manager_module, "get_active_plan_id", lambda: PLAN_ID)
    monkeypatch.setattr(plan_manager_module, "check_layer_changes", lambda: False)


@pytest.fixture
def lifecycle(monkeypatch: pytest.MonkeyPatch) -> Callable[[LifeCycleStatusValue], None]:
    """Sets the life-cycle status every plan status id resolves to."""

    def _set(value: LifeCycleStatusValue) -> None:
        monkeypatch.setattr(plan_manager_module.LifeCycleStatusLayer, "get_lifecycle_status_by_id", lambda _id: value)

    return _set


@pytest.fixture
def finalize_requests(plugin: Plugin, monkeypatch: pytest.MonkeyPatch) -> list[str]:
    requests: list[str] = []
    monkeypatch.setattr(plugin.plan_manager.lambda_service, "finalize_plan", requests.append)
    return requests


@pytest.fixture
def answer(monkeypatch: pytest.MonkeyPatch) -> Callable[[QMessageBox.StandardButton], None]:
    def _answer(button: QMessageBox.StandardButton) -> None:
        monkeypatch.setattr(plan_manager_module.QMessageBox, "question", lambda *_args, **_kwargs: button)

    return _answer


# ------------------------------------------------------------------ the button rule


def test_the_button_is_hidden_until_a_plan_is_open(plugin: Plugin):
    assert not plugin.finalize_plan_action.isVisible()


@pytest.mark.usefixtures("_active_plan")
def test_the_button_shows_for_a_valid_plan_that_is_not_final(plugin: Plugin, lifecycle):
    lifecycle(LifeCycleStatusValue.VALID)

    plugin.plan_manager.update_finalizable_status(_plan())

    assert plugin.finalize_plan_action.isVisible()


@pytest.mark.usefixtures("_active_plan")
def test_the_button_hides_for_a_plan_that_is_already_final(plugin: Plugin, lifecycle):
    lifecycle(LifeCycleStatusValue.VALID)
    plugin.plan_manager.update_finalizable_status(_plan())

    plugin.plan_manager.update_finalizable_status(_plan(final=True))

    assert not plugin.finalize_plan_action.isVisible()


@pytest.mark.usefixtures("_active_plan")
@pytest.mark.parametrize(
    "status", [LifeCycleStatusValue.APPORVED, LifeCycleStatusValue.LEGALLY_VALID, LifeCycleStatusValue.REPEALED]
)
def test_the_button_hides_for_a_plan_that_is_not_valid(plugin: Plugin, lifecycle, status):
    lifecycle(LifeCycleStatusValue.VALID)
    plugin.plan_manager.update_finalizable_status(_plan())

    lifecycle(status)
    plugin.plan_manager.update_finalizable_status(_plan())

    assert not plugin.finalize_plan_action.isVisible()


@pytest.mark.usefixtures("_active_plan")
def test_a_plan_that_is_not_active_leaves_the_button_alone(plugin: Plugin, lifecycle):
    lifecycle(LifeCycleStatusValue.VALID)

    plugin.plan_manager.update_finalizable_status(Plan(id_="other", name="Toinen", lifecycle_status_id="status-id"))

    assert not plugin.finalize_plan_action.isVisible()


@pytest.mark.usefixtures("_active_plan")
def test_closing_the_plan_hides_the_button(plugin: Plugin, lifecycle):
    lifecycle(LifeCycleStatusValue.VALID)
    plugin.plan_manager.update_finalizable_status(_plan())

    plugin.plan_manager.plan_unset.emit()

    assert not plugin.finalize_plan_action.isVisible()


@pytest.mark.usefixtures("_active_plan")
def test_clearing_the_project_hides_the_button(plugin: Plugin, lifecycle):
    lifecycle(LifeCycleStatusValue.VALID)
    plugin.plan_manager.update_finalizable_status(_plan())

    plugin.plan_manager.project_cleared.emit()

    assert not plugin.finalize_plan_action.isVisible()


# ------------------------------------------------------------------ the click


@pytest.mark.usefixtures("_active_plan")
def test_finalizing_asks_first_and_sends_on_yes(plugin: Plugin, finalize_requests, answer):
    answer(QMessageBox.StandardButton.Yes)

    plugin.plan_manager.finalize_plan()

    assert finalize_requests == [PLAN_ID]


@pytest.mark.usefixtures("_active_plan")
def test_finalizing_sends_nothing_on_no(plugin: Plugin, finalize_requests, answer):
    answer(QMessageBox.StandardButton.No)

    plugin.plan_manager.finalize_plan()

    assert finalize_requests == []


@pytest.mark.usefixtures("_active_plan")
def test_unsaved_changes_block_finalizing(plugin: Plugin, finalize_requests, messages: MessageRecorder, monkeypatch):
    monkeypatch.setattr(plan_manager_module, "check_layer_changes", lambda: True)
    monkeypatch.setattr(plan_manager_module.QMessageBox, "question", lambda *_a, **_k: pytest.fail("must not ask"))

    plugin.plan_manager.finalize_plan()

    assert finalize_requests == []
    assert len(messages.warnings) == 1


# ------------------------------------------------------------------ the answer


@pytest.mark.usefixtures("_active_plan")
def test_a_plan_made_final_hides_the_button_and_reports_the_counts(
    plugin: Plugin, lifecycle, messages: MessageRecorder, monkeypatch
):
    """The plan is read again from the database, which now says it is final."""
    lifecycle(LifeCycleStatusValue.VALID)
    plugin.plan_manager.update_finalizable_status(_plan())
    monkeypatch.setattr(plan_manager_module.PlanLayer, "get_active_plan", lambda: _plan(final=True))

    plugin.plan_manager.lambda_service.plan_finalized.emit({"repealed_plans": 1, "repealed_plan_objects": 2})

    assert not plugin.finalize_plan_action.isVisible()
    assert len(messages.successes) == 1
    assert "Kumoutuneita kaavoja: 1, kaavakohteita: 2" in messages.successes[0][1]


def test_validation_errors_from_finalizing_land_in_the_validation_dock(plugin: Plugin, messages: MessageRecorder):
    plugin.validation_dock.hide()

    plugin.plan_manager.lambda_service.plan_finalize_validation_failed.emit(VALIDATION_ERRORS)

    assert not plugin.validation_dock.isHidden()
    errors = plugin.validation_dock.validation_result_tree_view.model.item(ValidationModel.ERROR_INDEX, 0)
    assert errors.rowCount() == 1
    assert len(messages.warnings) == 1
