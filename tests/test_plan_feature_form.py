"""The plan object form disables saving when it is given a reason, and shows the reason.

Opening the form for a stored object counts the other users of its regulation groups in one
read of the association layer, and never reads the plan matter row.

The regulation groups view, shared with the import form, matches a new group against the saved
groups of the target layer's type, also when there is no plan object yet.
"""

from __future__ import annotations

from typing import Iterator

import pytest
from qgis.core import QgsFeature, QgsProject, QgsVectorLayer
from qgis.PyQt.QtWidgets import QDialogButtonBox

from arho_feature_template.core.models import PlanObject, RegulationGroup, RegulationGroupLibrary
from arho_feature_template.gui.components.regulation_groups_view import RegulationGroupsView
from arho_feature_template.gui.dialogs.plan_feature_form import (
    PLAN_LOCKED_MESSAGE,
    VALID_PLAN_OBJECT_READ_ONLY_MESSAGE,
    PlanObjectForm,
)
from arho_feature_template.project.layers.code_layers import PlanRegulationGroupTypeLayer, UndergroundTypeLayer
from arho_feature_template.project.layers.plan_layers import (
    LandUseAreaLayer,
    OtherAreaLayer,
    PlanMatterLayer,
    RegulationGroupAssociationLayer,
)
from arho_feature_template.utils.project_utils import CODE_LAYER_GROUP_NAME, PLAN_LAYER_GROUP_NAME

ASSOCIATION_URI = (
    "None?field=id:string&field=plan_regulation_group_id:string&field=plan_id:string"
    "&field=land_use_area_id:string&field=other_area_id:string&field=line_id:string&field=point_id:string"
)


def _add_layer(project: QgsProject, group_name: str, layer_name: str, uri: str) -> QgsVectorLayer:
    root = project.layerTreeRoot()
    group = root.findGroup(group_name) or root.addGroup(group_name)
    layer = QgsVectorLayer(uri, layer_name, "memory")
    assert layer.isValid()
    project.addMapLayer(layer, addToLegend=False)
    group.addLayer(layer)
    return layer


def _add_rows(layer: QgsVectorLayer, rows: list[dict]) -> None:
    for row in rows:
        feature = QgsFeature(layer.fields())
        for key, value in row.items():
            feature.setAttribute(key, value)
        assert layer.dataProvider().addFeatures([feature])[0]


@pytest.fixture
def form_project(new_project: QgsProject) -> Iterator[QgsProject]:
    """The layers the form reads while it opens: the underground codes and the plan matter."""
    codes = _add_layer(
        new_project,
        CODE_LAYER_GROUP_NAME,
        UndergroundTypeLayer.name,
        "None?field=id:string&field=value:string&field=name:map",
    )
    _add_rows(
        codes,
        [
            {"id": "ug-1", "value": "01", "name": {"fin": "Maanpäällinen"}},
            {"id": "ug-2", "value": "02", "name": {"fin": "Maanalainen"}},
        ],
    )
    _add_layer(
        new_project, PLAN_LAYER_GROUP_NAME, PlanMatterLayer.name, "None?field=id:string&field=plan_type_id:string"
    )
    yield new_project
    # The code layer cache is class-level and would outlive this project
    UndergroundTypeLayer._cache.clear()
    UndergroundTypeLayer._field_names.clear()


@pytest.fixture
def stored_groups_project(form_project: QgsProject) -> Iterator[QgsProject]:
    """Two stored groups of object `obj-1`: `group-shared` is also used by two other objects."""
    group_types = _add_layer(
        form_project,
        CODE_LAYER_GROUP_NAME,
        PlanRegulationGroupTypeLayer.name,
        "None?field=id:string&field=value:string",
    )
    _add_rows(
        group_types,
        [
            {"id": "gt-land-use", "value": "landUseRegulations"},
            {"id": "gt-other-area", "value": "otherAreaRegulations"},
        ],
    )
    associations = _add_layer(
        form_project, PLAN_LAYER_GROUP_NAME, RegulationGroupAssociationLayer.name, ASSOCIATION_URI
    )
    _add_rows(
        associations,
        [
            {"id": "a-1", "plan_regulation_group_id": "group-shared", "land_use_area_id": "obj-1"},
            {"id": "a-2", "plan_regulation_group_id": "group-shared", "land_use_area_id": "obj-2"},
            {"id": "a-3", "plan_regulation_group_id": "group-shared", "point_id": "point-9"},
            {"id": "a-4", "plan_regulation_group_id": "group-own", "land_use_area_id": "obj-1"},
            {"id": "a-5", "plan_regulation_group_id": "group-a", "land_use_area_id": "obj-3"},
        ],
    )
    yield form_project
    PlanRegulationGroupTypeLayer._cache.clear()
    PlanRegulationGroupTypeLayer._field_names.clear()


@pytest.fixture
def make_form() -> Iterator:
    forms: list[PlanObjectForm] = []

    def make(save_disabled_reason: str | None, plan_object: PlanObject | None = None) -> PlanObjectForm:
        form = PlanObjectForm(
            plan_object or PlanObject(layer_name=LandUseAreaLayer.name),
            "Testi",
            [RegulationGroupLibrary(name="Testikirjasto")],
            active_plan_regulation_groups_library=RegulationGroupLibrary(name="Kaavan ryhmät"),
            save_disabled_reason=save_disabled_reason,
        )
        forms.append(form)
        return form

    yield make
    for form in forms:
        form.deleteLater()


@pytest.fixture
def stored_plan_object() -> PlanObject:
    return PlanObject(
        layer_name=LandUseAreaLayer.name,
        id_="obj-1",
        regulation_groups=[
            RegulationGroup(id_="group-shared", letter_code="A", modified=False),
            RegulationGroup(id_="group-own", letter_code="B", modified=False),
        ],
    )


def test_opening_a_stored_object_reads_the_associations_once_and_the_plan_matter_never(
    stored_groups_project,  # noqa: ARG001
    make_form,
    stored_plan_object,
    monkeypatch,
):
    association_reads: list[tuple] = []
    original = RegulationGroupAssociationLayer.get_features_by_attribute_value

    def counting(attribute, value, no_geometries=True):
        association_reads.append((attribute, value))
        return original(attribute, value, no_geometries)

    monkeypatch.setattr(RegulationGroupAssociationLayer, "get_features_by_attribute_value", counting)
    plan_matter_reads: list[tuple] = []
    monkeypatch.setattr(
        PlanMatterLayer, "get_features_by_attribute_value", lambda *args: plan_matter_reads.append(args)
    )

    make_form(None, stored_plan_object)

    assert plan_matter_reads == []
    assert association_reads == [("plan_regulation_group_id", {"group-shared", "group-own"})]


def test_the_link_count_leaves_out_the_object_itself(stored_groups_project, make_form, stored_plan_object):  # noqa: ARG001
    form = make_form(None, stored_plan_object)

    shared, own = form.regulation_groups_view.regulation_group_widgets
    assert shared.regulation_group.id_ == "group-shared"
    assert shared.link_label_text is not None
    assert "2 toisella kaavakohteella" in shared.link_label_text.text()
    assert own.regulation_group.id_ == "group-own"
    assert own.link_label_text is None
    assert not own.link_btn.isEnabled()


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


# ------------------------------------------------------------------ matching without a plan object


@pytest.fixture
def make_view() -> Iterator:
    """A view over one saved land use group `A`, as the import form has it: no plan object."""
    views: list[RegulationGroupsView] = []
    saved = RegulationGroup(id_="group-a", type_code_id="gt-land-use", letter_code="A", modified=False)

    def make(layer_name: str | None) -> tuple[RegulationGroupsView, RegulationGroup]:
        view = RegulationGroupsView(
            [RegulationGroupLibrary(name="Testikirjasto")],
            RegulationGroupLibrary(name="Kaavan ryhmät", regulation_groups=[saved]),
            layer_name=layer_name,
        )
        views.append(view)
        return view, saved

    yield make
    for view in views:
        view.deleteLater()


def test_a_new_group_finds_its_twin_of_the_target_layer_type_without_a_plan_object(
    stored_groups_project,  # noqa: ARG001
    make_view,
):
    view, saved = make_view(LandUseAreaLayer.name)

    view.add_plan_regulation_group(RegulationGroup(letter_code="A"))

    (widget,) = view.regulation_group_widgets
    assert widget.regulation_group.type_code_id == "gt-land-use"
    assert widget.matching_groups_in_db == [saved]
    assert widget.link_btn.isEnabled()


def test_changing_the_target_layer_matches_the_groups_again(stored_groups_project, make_view):  # noqa: ARG001
    view, saved = make_view(OtherAreaLayer.name)
    view.add_plan_regulation_group(RegulationGroup(letter_code="A"))
    (widget,) = view.regulation_group_widgets
    assert widget.matching_groups_in_db == []
    assert not widget.link_btn.isEnabled()

    view.set_layer_name(LandUseAreaLayer.name)

    assert widget.regulation_group.type_code_id == "gt-land-use"
    assert widget.matching_groups_in_db == [saved]
    assert widget.link_btn.isEnabled()

    view.set_layer_name(OtherAreaLayer.name)

    assert widget.regulation_group.type_code_id == "gt-other-area"
    assert widget.matching_groups_in_db == []


def test_linking_and_unlinking_a_group_without_a_plan_object_changes_the_widget(
    stored_groups_project,  # noqa: ARG001
    make_view,
):
    view, saved = make_view(LandUseAreaLayer.name)
    view.add_plan_regulation_group(RegulationGroup(letter_code="A"))
    (widget,) = view.regulation_group_widgets

    widget.link_btn.click()

    assert widget.regulation_group.id_ == "group-a"
    assert "border" in widget.styleSheet()
    assert widget.link_btn.isEnabled()
    assert widget.link_label_text is not None
    assert "1 toisella kaavakohteella" in widget.link_label_text.text()

    widget.link_btn.click()

    assert widget.regulation_group.id_ is None
    assert widget.styleSheet() == ""
    assert widget.link_label_text is None
    assert widget.matching_groups_in_db == [saved]
    assert widget.link_btn.isEnabled()
