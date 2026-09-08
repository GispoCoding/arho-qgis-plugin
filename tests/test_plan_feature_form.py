"""The plan object form disables saving when it is given a reason, and shows the reason."""

from __future__ import annotations

from typing import Iterator

import pytest
from qgis.core import QgsFeature, QgsProject, QgsVectorLayer
from qgis.PyQt.QtWidgets import QDialogButtonBox

from arho_feature_template.core.models import PlanObject, RegulationGroupLibrary
from arho_feature_template.gui.dialogs.plan_feature_form import (
    PLAN_LOCKED_MESSAGE,
    VALID_PLAN_OBJECT_READ_ONLY_MESSAGE,
    PlanObjectForm,
)
from arho_feature_template.project.layers.code_layers import UndergroundTypeLayer
from arho_feature_template.project.layers.plan_layers import LandUseAreaLayer, PlanMatterLayer
from arho_feature_template.utils.project_utils import CODE_LAYER_GROUP_NAME, PLAN_LAYER_GROUP_NAME


def _add_layer(project: QgsProject, group_name: str, layer_name: str, uri: str) -> QgsVectorLayer:
    root = project.layerTreeRoot()
    group = root.findGroup(group_name) or root.addGroup(group_name)
    layer = QgsVectorLayer(uri, layer_name, "memory")
    assert layer.isValid()
    project.addMapLayer(layer, addToLegend=False)
    group.addLayer(layer)
    return layer


@pytest.fixture
def form_project(new_project: QgsProject) -> Iterator[QgsProject]:
    """The layers the form reads while it opens: the underground codes and the plan matter."""
    codes = _add_layer(
        new_project,
        CODE_LAYER_GROUP_NAME,
        UndergroundTypeLayer.name,
        "None?field=id:string&field=value:string&field=name:map",
    )
    for id_, value, name in (("ug-1", "01", "Maanpäällinen"), ("ug-2", "02", "Maanalainen")):
        feature = QgsFeature(codes.fields())
        feature.setAttribute("id", id_)
        feature.setAttribute("value", value)
        feature.setAttribute("name", {"fin": name})
        assert codes.dataProvider().addFeatures([feature])[0]
    _add_layer(
        new_project, PLAN_LAYER_GROUP_NAME, PlanMatterLayer.name, "None?field=id:string&field=plan_type_id:string"
    )
    yield new_project
    # The code layer cache is class-level and would outlive this project
    UndergroundTypeLayer._cache.clear()
    UndergroundTypeLayer._field_names.clear()


@pytest.fixture
def make_form() -> Iterator:
    forms: list[PlanObjectForm] = []

    def make(save_disabled_reason: str | None) -> PlanObjectForm:
        form = PlanObjectForm(
            PlanObject(layer_name=LandUseAreaLayer.name),
            "Testi",
            [RegulationGroupLibrary(name="Testikirjasto")],
            save_disabled_reason=save_disabled_reason,
        )
        forms.append(form)
        return form

    yield make
    for form in forms:
        form.deleteLater()


@pytest.mark.parametrize("reason", [VALID_PLAN_OBJECT_READ_ONLY_MESSAGE, PLAN_LOCKED_MESSAGE])
def test_a_reason_disables_saving_and_is_shown_as_the_tooltip(form_project, make_form, reason: str):  # noqa: ARG001
    form = make_form(reason)

    ok_button = form.button_box.button(QDialogButtonBox.StandardButton.Ok)
    assert not ok_button.isEnabled()
    assert ok_button.toolTip() == reason
    assert form.button_box.button(QDialogButtonBox.StandardButton.Cancel).isEnabled()


def test_without_a_reason_saving_is_enabled(form_project, make_form):  # noqa: ARG001
    form = make_form(None)

    ok_button = form.button_box.button(QDialogButtonBox.StandardButton.Ok)
    assert ok_button.isEnabled()
    assert ok_button.toolTip() == ""
