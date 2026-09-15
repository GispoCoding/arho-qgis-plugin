"""New plan objects, regulations and propositions get the plan's lifecycle status from the plugin.

The database no longer moves the rows along with the plan, so the plugin sets the status of a new
row. Matching is about content: a template group finds its saved twin whatever status or validity
period the saved rows carry. Template libraries never carry the status.
"""

from __future__ import annotations

import copy
import dataclasses
from typing import TYPE_CHECKING, Iterator

import pytest
from qgis.core import Qgis, QgsDefaultValue, QgsExpressionContextUtils, QgsProject
from qgis.PyQt.QtCore import QDate

from arho_feature_template.core import feature_editing
from arho_feature_template.core.models import (
    PlanObject,
    Proposition,
    Regulation,
    RegulationGroup,
    RegulationGroupLibrary,
)
from arho_feature_template.project.layers.code_layers import PlanRegulationTypeLayer, UndergroundTypeLayer
from arho_feature_template.project.layers.plan_layers import PlanLayer, RegulationGroupLayer
from arho_feature_template.utils.project_utils import PLAN_LAYER_GROUP_NAME
from tests.test_model_readers import _add_feature, _add_layer, _build_family, _fill_family

if TYPE_CHECKING:
    from qgis.core import QgsVectorLayer

PLAN_URI = "None?field=id:string&field=lifecycle_status_id:string"
STATUS = "status-1"


# ------------------------------------------------------------------ model helpers


def _new_group(**kwargs) -> RegulationGroup:
    return RegulationGroup(
        letter_code="A",
        regulations=[Regulation(regulation_type_id="type-1")],
        propositions=[Proposition(value={"fin": "Suositus"})],
        **kwargs,
    )


def test_new_children_get_the_status_and_saved_ones_keep_theirs():
    group = _new_group()
    group.regulations.append(Regulation(regulation_type_id="type-2", id_="regulation-9", lifecycle_status_id="old"))
    group.regulations.append(Regulation(regulation_type_id="type-3", lifecycle_status_id="chosen"))
    assert group.lacks_lifecycle_status()

    group.set_lifecycle_status_of_new(STATUS)

    assert not group.lacks_lifecycle_status()
    assert [regulation.lifecycle_status_id for regulation in group.regulations] == [STATUS, "old", "chosen"]
    assert group.propositions[0].lifecycle_status_id == STATUS


def test_a_saved_child_without_a_status_is_left_to_the_database():
    group = RegulationGroup(regulations=[Regulation(regulation_type_id="type-1", id_="regulation-9")])

    assert not group.lacks_lifecycle_status()
    group.set_lifecycle_status_of_new(STATUS)
    assert group.regulations[0].lifecycle_status_id is None


def test_without_a_plan_status_nothing_changes():
    group = _new_group()

    group.set_lifecycle_status_of_new(None)

    assert group.lacks_lifecycle_status()
    assert group.regulations[0].lifecycle_status_id is None


def test_digitising_does_not_stamp_the_library_template():
    template = PlanObject(layer_name="Aluevaraus", regulation_groups=[_new_group()])

    # As the plan manager builds the new object from the feature template
    new = PlanObject(layer_name="Aluevaraus", regulation_groups=copy.deepcopy(template.regulation_groups))
    new.set_lifecycle_status_of_new(STATUS)

    assert new.regulation_groups[0].regulations[0].lifecycle_status_id == STATUS
    assert template.regulation_groups[0].regulations[0].lifecycle_status_id is None
    assert template.lacks_lifecycle_status()


def test_a_plan_object_reaches_its_groups():
    plan_object = PlanObject(layer_name="Aluevaraus", regulation_groups=[_new_group()])
    assert plan_object.lacks_lifecycle_status()

    plan_object.set_lifecycle_status_of_new(STATUS)

    assert plan_object.lifecycle_status_id == STATUS
    assert not plan_object.lacks_lifecycle_status()
    (group,) = plan_object.regulation_groups
    assert group.regulations[0].lifecycle_status_id == STATUS
    assert group.propositions[0].lifecycle_status_id == STATUS

    saved = PlanObject(layer_name="Aluevaraus", id_="area-1", regulation_groups=[_new_group()])
    assert saved.lacks_lifecycle_status()  # the object has a row, its template group does not
    saved.set_lifecycle_status_of_new(STATUS)
    assert saved.lifecycle_status_id is None


# ------------------------------------------------------------------ templates


def _keys(data: object) -> set[str]:
    if isinstance(data, dict):
        return set(data) | {key for value in data.values() for key in _keys(value)}
    if isinstance(data, list):
        return {key for value in data for key in _keys(value)}
    return set()


def test_template_dicts_carry_no_lifecycle_status(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(PlanRegulationTypeLayer, "get_type_by_id", classmethod(lambda cls, id_: "tyyppi"))  # noqa: ARG005
    monkeypatch.setattr(UndergroundTypeLayer, "get_attribute_by_id", classmethod(lambda cls, attr, id_: "01"))  # noqa: ARG005
    plan_object = PlanObject(layer_name="Aluevaraus", regulation_groups=[_new_group()], type_of_underground_id="ug-1")
    plan_object.set_lifecycle_status_of_new(STATUS)

    keys = _keys(plan_object.into_template_dict())

    assert "lifecycle_status_id" not in keys
    assert not {key for key in keys if key.startswith("period_of_validity")}


# ------------------------------------------------------------------ hashing


def test_an_empty_letter_code_is_no_letter_code():
    empty = RegulationGroup(letter_code="", color_code="")
    none = RegulationGroup(letter_code=None, color_code=None)

    assert empty == none
    assert empty.data_hash() == none.data_hash()
    assert empty.letter_code is None


def test_a_text_of_empty_strings_is_no_text():
    """The database default of a multilanguage column is empty strings in every language."""
    from arho_feature_template.core.models import AdditionalInformation, AttributeValue

    empty = AttributeValue(text_value={"eng": "", "fin": "", "swe": ""})
    assert empty.text_value is None
    assert empty == AttributeValue()
    assert AdditionalInformation(additional_information_type_id="info-1", value=empty).value is None

    assert Proposition(value={"fin": "", "swe": ""}) == Proposition(value=None)
    assert Proposition(value={"fin": "Suositus", "swe": ""}).value == {"fin": "Suositus"}


def test_no_subject_identifiers_is_an_empty_list():
    none = Regulation(regulation_type_id="type-1", subject_identifiers=None)  # type: ignore[arg-type]
    empty = Regulation(regulation_type_id="type-1")

    assert none.subject_identifiers == []
    assert none == empty
    assert none.data_hash() == empty.data_hash()


def test_a_status_change_is_still_a_modification():
    one = Regulation(regulation_type_id="type-1", lifecycle_status_id="a")
    other = Regulation(regulation_type_id="type-1", lifecycle_status_id="b", period_of_validity_end=QDate(2026, 1, 1))

    assert one != other  # the widget saves the change
    assert one.data_hash() == other.data_hash()  # the form still finds the twin


@pytest.fixture
def layers(new_project: QgsProject) -> Iterator[dict[str, QgsVectorLayer]]:
    """Plan 1 in status 1, area 1 with group 1 whose regulation and proposition carry the status."""
    new_project.setTransactionMode(Qgis.TransactionMode.BufferedGroups)
    layers = _build_family(new_project, PLAN_LAYER_GROUP_NAME, "Aluevaraus")
    _fill_family(layers)
    layers["plans"] = _add_layer(new_project, PLAN_LAYER_GROUP_NAME, PlanLayer.name, PLAN_URI)
    _add_feature(layers["plans"], id="plan-1", lifecycle_status_id=STATUS)
    for name in ("regulations", "propositions"):
        layer = layers[name]
        assert layer.dataProvider().changeAttributeValues({1: {layer.fields().indexOf("lifecycle_status_id"): STATUS}})
        # A new row gets an id, as it does from the database
        layer.setDefaultValueDefinition(layer.fields().indexOf("id"), QgsDefaultValue("uuid()"))
    layers["groups"].setDefaultValueDefinition(layers["groups"].fields().indexOf("id"), QgsDefaultValue("uuid()"))
    yield layers
    new_project.rollBack(stopEditing=True)


def _read_group(layers: dict[str, QgsVectorLayer], group_id: str = "group-1") -> RegulationGroup:
    feature = next(layers["groups"].getFeatures(f"\"id\" = '{group_id}'"))
    return RegulationGroupLayer.model_from_feature(feature)


def _as_template(group: RegulationGroup) -> RegulationGroup:
    """The same content as a library template has it: no ids, no status, an empty letter code."""
    return dataclasses.replace(
        group,
        id_=None,
        letter_code=group.letter_code or "",
        regulations=[
            dataclasses.replace(
                regulation,
                id_=None,
                regulation_group_id=None,
                lifecycle_status_id=None,
                additional_information=[
                    dataclasses.replace(info, id_=None, plan_regulation_id=None)
                    for info in regulation.additional_information
                ],
            )
            for regulation in group.regulations
        ],
        propositions=[
            dataclasses.replace(proposition, id_=None, regulation_group_id=None, lifecycle_status_id=None)
            for proposition in group.propositions
        ],
    )


def test_a_template_group_finds_its_saved_twin_whatever_the_status(layers: dict[str, QgsVectorLayer]):
    saved = _read_group(layers)
    assert saved.regulations[0].lifecycle_status_id == STATUS
    # The plan moved on since the group was saved, and a proposition was given an end date
    saved.regulations[0].lifecycle_status_id = "status-0"
    saved.propositions[0].period_of_validity_end = QDate(2026, 1, 1)
    hash_map = RegulationGroupLibrary(name="Kaava", regulation_groups=[saved]).into_hash_map()
    template = _as_template(saved)

    assert hash_map.get(template.matching_hash()) == [saved]  # before the form stamps the status

    template.set_lifecycle_status_of_new(STATUS)

    assert hash_map.get(template.matching_hash()) == [saved]


def test_a_coloured_template_finds_its_uncoloured_twin(layers: dict[str, QgsVectorLayer]):
    saved = _read_group(layers)
    hash_map = RegulationGroupLibrary(name="Kaava", regulation_groups=[saved]).into_hash_map()
    template = dataclasses.replace(_as_template(saved), color_code="#ff0000")

    assert hash_map.get(template.matching_hash()) == [saved]
    assert template.data_hash() != saved.data_hash()  # the library manager still sees a colour edit


def test_a_template_group_with_more_content_finds_nothing(layers: dict[str, QgsVectorLayer]):
    saved = _read_group(layers)
    hash_map = RegulationGroupLibrary(name="Kaava", regulation_groups=[saved]).into_hash_map()
    template = _as_template(saved)
    template.regulations.append(Regulation(regulation_type_id="type-2"))

    template.set_lifecycle_status_of_new(STATUS)

    assert hash_map.get(template.matching_hash()) is None


# ------------------------------------------------------------------ plan layer and saving


def test_the_plan_layer_gives_the_status_of_the_active_plan(layers: dict[str, QgsVectorLayer]):  # noqa: ARG001
    assert PlanLayer.get_lifecycle_status_id() is None  # no active plan
    assert PlanLayer.get_lifecycle_status_id("plan-1") == STATUS

    QgsExpressionContextUtils.setProjectVariable(QgsProject.instance(), "active_plan_id", "plan-1")

    assert PlanLayer.get_lifecycle_status_id() == STATUS


def test_saving_gives_a_new_regulation_the_plan_status(layers: dict[str, QgsVectorLayer]):
    group = RegulationGroup(letter_code="C", regulations=[Regulation(regulation_type_id="type-1")])

    group_id = feature_editing.add_regulation_group_to_edit_buffer(group, plan_id="plan-1")
    assert feature_editing.commit_edit_buffer(stop_editing=False)

    assert group.regulations[0].lifecycle_status_id == STATUS
    row = next(layers["regulations"].getFeatures(f"\"plan_regulation_group_id\" = '{group_id}'"))
    assert row["lifecycle_status_id"] == STATUS


def test_saving_a_read_group_does_not_touch_its_children(layers: dict[str, QgsVectorLayer]):
    saved = _read_group(layers)
    assert not saved.lacks_lifecycle_status()

    saved.set_lifecycle_status_of_new("other")

    assert saved.regulations[0].lifecycle_status_id == STATUS
