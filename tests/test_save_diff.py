"""Saving compares the edited model against its `stored` snapshot, not against the database.

The readers put the snapshot on the model. An unchanged save then makes no query at all; a
removed child costs one lookup on its layer, so the row can be deleted by feature id. After
the commit, the model mirrors the database again, so a second save does not link twice.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Iterator

import pytest
from qgis.core import Qgis, QgsGeometry

from arho_feature_template.core import feature_editing
from arho_feature_template.core.models import PlanObject, StoredPlanObject, StoredRegulation, StoredRegulationGroup
from arho_feature_template.project.layers.plan_layers import LandUseAreaLayer, PlanLayer, RegulationGroupLayer
from arho_feature_template.utils.project_utils import PLAN_LAYER_GROUP_NAME
from tests.test_model_readers import _add_feature, _add_layer, _build_family, _fill_family

if TYPE_CHECKING:
    from qgis.core import QgsProject, QgsVectorLayer

TIMING_LOGGER = "arho_feature_template.timing"


@pytest.fixture
def layers(new_project: QgsProject) -> Iterator[dict[str, QgsVectorLayer]]:
    """Area 1 with group 1 (one regulation, one proposition) and an unused group 2."""
    # The save path commits the whole project at once, as it does with a database transaction
    new_project.setTransactionMode(Qgis.TransactionMode.BufferedGroups)
    layers = _build_family(new_project, PLAN_LAYER_GROUP_NAME, "Aluevaraus")
    _fill_family(layers)
    # New rows get the plan's lifecycle status from the plan row
    layers["plans"] = _add_layer(
        new_project, PLAN_LAYER_GROUP_NAME, PlanLayer.name, "None?field=id:string&field=lifecycle_status_id:string"
    )
    _add_feature(layers["plans"], id="plan-1", lifecycle_status_id="status-1")
    _add_feature(
        layers["groups"],
        id="group-2",
        short_name="B",
        name={"fin": "Toinen"},
        type_of_plan_regulation_group_id="group-type-1",
        plan_id="plan-1",
        ordering=4,
    )
    yield layers
    # The project's edit buffer group is a singleton that `clear()` leaves in editing state,
    # and its `startEditing()` returns early then, without edit buffers for the new layers.
    new_project.rollBack(stopEditing=True)


def _read_area(layers: dict[str, QgsVectorLayer], area_id: str = "area-1") -> PlanObject:
    feature = next(layers["objects"].getFeatures(f"\"id\" = '{area_id}'"))
    return LandUseAreaLayer.model_from_feature(feature)


def _read_group(layers: dict[str, QgsVectorLayer], group_id: str):
    feature = next(layers["groups"].getFeatures(f"\"id\" = '{group_id}'"))
    return RegulationGroupLayer.model_from_feature(feature)


def _attribute_values(layer: QgsVectorLayer, attribute: str) -> list:
    return sorted(feature[attribute] for feature in layer.getFeatures())


class _QueryLog(logging.Handler):
    """Collects the timing lines of the layer queries. Hooked straight onto the timing logger,
    because the plugin logger does not propagate to the root once it has been set up."""

    def __init__(self) -> None:
        super().__init__(logging.DEBUG)
        self.lines: list[str] = []

    def emit(self, record: logging.LogRecord) -> None:
        message = record.getMessage()
        if "+-- query[" in message:
            self.lines.append(message)

    def of(self, layer_name: str) -> list[str]:
        return [line for line in self.lines if f"query[{layer_name}]" in line]


@pytest.fixture
def query_log() -> Iterator[_QueryLog]:
    logger = logging.getLogger(TIMING_LOGGER)
    level_before = logger.level
    handler = _QueryLog()
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    yield handler
    logger.removeHandler(handler)
    logger.setLevel(level_before)


def _save(plan_object: PlanObject) -> str | None:
    object_id = feature_editing.add_plan_object_to_edit_buffer(plan_object)
    assert feature_editing.commit_edit_buffer(stop_editing=False)
    return object_id


def test_the_readers_set_the_stored_snapshot(layers: dict[str, QgsVectorLayer]):
    area = _read_area(layers)

    assert area.stored == StoredPlanObject(regulation_group_ids=frozenset({"group-1"}))
    (group,) = area.regulation_groups
    assert group.stored == StoredRegulationGroup(
        regulation_ids=frozenset({"regulation-1"}), proposition_ids=frozenset({"proposition-1"})
    )
    (regulation,) = group.regulations
    assert regulation.stored == StoredRegulation(
        additional_information_ids=frozenset({"info-1"}),
        theme_ids=frozenset({"theme-1"}),
        verbal_regulation_type_ids=frozenset({"verbal-1"}),
    )
    (proposition,) = group.propositions
    assert proposition.stored is not None
    assert proposition.stored.theme_ids == frozenset({"theme-2"})


def test_saving_an_unchanged_object_makes_no_query(layers: dict[str, QgsVectorLayer], query_log: _QueryLog):
    area = _read_area(layers)
    query_log.lines.clear()

    assert _save(area) == "area-1"

    assert query_log.lines == []
    assert _attribute_values(layers["associations"], "plan_regulation_group_id") == ["group-1"]
    assert _attribute_values(layers["themes"], "plan_theme_id") == ["theme-1", "theme-2"]
    assert _attribute_values(layers["verbal_types"], "type_of_verbal_plan_regulation_id") == ["verbal-1"]


def test_a_removed_group_costs_one_lookup_and_loses_its_link(layers: dict[str, QgsVectorLayer], query_log: _QueryLog):
    _add_feature(layers["associations"], id="assoc-2", plan_regulation_group_id="group-2", land_use_area_id="area-1")
    area = _read_area(layers)
    assert {group.id_ for group in area.regulation_groups} == {"group-1", "group-2"}
    area.regulation_groups = [group for group in area.regulation_groups if group.id_ == "group-1"]
    query_log.lines.clear()

    _save(area)

    assert len(query_log.lines) == 1
    assert len(query_log.of("Kaavamääräysryhmien assosiaatiot")) == 1
    assert _attribute_values(layers["associations"], "plan_regulation_group_id") == ["group-1"]
    assert _attribute_values(layers["groups"], "id") == ["group-1", "group-2"]  # the group itself stays
    assert area.stored == StoredPlanObject(regulation_group_ids=frozenset({"group-1"}))


def test_an_added_group_is_linked_once_even_when_saved_twice(layers: dict[str, QgsVectorLayer]):
    area = _read_area(layers)
    area.regulation_groups.append(_read_group(layers, "group-2"))

    _save(area)
    assert _attribute_values(layers["associations"], "plan_regulation_group_id") == ["group-1", "group-2"]
    assert area.stored == StoredPlanObject(regulation_group_ids=frozenset({"group-1", "group-2"}))

    _save(area)
    assert _attribute_values(layers["associations"], "plan_regulation_group_id") == ["group-1", "group-2"]


def test_removed_children_of_a_group_are_deleted(layers: dict[str, QgsVectorLayer]):
    area = _read_area(layers)
    (group,) = area.regulation_groups
    (regulation,) = group.regulations
    regulation.theme_ids = []
    regulation.verbal_regulation_type_ids = []
    regulation.additional_information = []
    group.propositions = []

    _save(area)

    # theme-2 belongs to the deleted proposition; the database cascades that, a memory layer does not
    assert _attribute_values(layers["themes"], "plan_theme_id") == ["theme-2"]
    assert _attribute_values(layers["verbal_types"], "type_of_verbal_plan_regulation_id") == []
    assert _attribute_values(layers["infos"], "id") == []
    assert _attribute_values(layers["propositions"], "id") == []
    assert _attribute_values(layers["regulations"], "id") == ["regulation-1"]
    assert regulation.stored == StoredRegulation(frozenset(), frozenset(), frozenset())
    assert group.stored == StoredRegulationGroup(
        regulation_ids=frozenset({"regulation-1"}), proposition_ids=frozenset()
    )


def test_new_children_get_their_ids_after_the_commit(layers: dict[str, QgsVectorLayer]):
    area = _read_area(layers)
    (group,) = area.regulation_groups
    (regulation,) = group.regulations
    regulation.theme_ids.append("theme-3")

    _save(area)

    assert _attribute_values(layers["themes"], "plan_theme_id") == ["theme-1", "theme-2", "theme-3"]
    assert regulation.stored is not None
    assert regulation.stored.theme_ids == frozenset({"theme-1", "theme-3"})


def test_a_saved_model_without_a_snapshot_is_refused(layers: dict[str, QgsVectorLayer]):  # noqa: ARG001
    area = PlanObject(id_="area-1", layer_name="Aluevaraus", modified=False)

    with pytest.raises(ValueError, match="PlanObject area-1 has an id but no stored snapshot"):
        feature_editing.add_plan_object_to_edit_buffer(area)


def test_a_failed_commit_leaves_the_model_as_it_was(layers: dict[str, QgsVectorLayer], monkeypatch):
    area = _read_area(layers)
    area.regulation_groups.append(_read_group(layers, "group-2"))

    class FailingProject:
        @staticmethod
        def commitChanges(stopEditing: bool) -> tuple[bool, list[str]]:  # noqa: ARG004
            return False, ["VIRHE"]

    feature_editing.add_plan_object_to_edit_buffer(area)
    monkeypatch.setattr(feature_editing.QgsProject, "instance", staticmethod(FailingProject))
    assert feature_editing.commit_edit_buffer(stop_editing=False) is False

    assert area.stored == StoredPlanObject(regulation_group_ids=frozenset({"group-1"}))
    assert feature_editing._after_commit == []


def _save_result(plan_object: PlanObject) -> feature_editing.PlanObjectSaveResult:
    result = feature_editing.save_plan_object(plan_object, plan_id="plan-1")
    assert result is not None
    return result


def test_saving_an_unchanged_object_reports_no_group_change(layers: dict[str, QgsVectorLayer]):
    area = _read_area(layers)

    assert _save_result(area) == feature_editing.PlanObjectSaveResult("area-1", regulation_groups_changed=False)


def test_changing_only_the_object_reports_no_group_change(layers: dict[str, QgsVectorLayer]):
    area = _read_area(layers)
    area.name = {"fin": "Uusi nimi"}
    area.modified = True

    assert _save_result(area).regulation_groups_changed is False
    assert next(layers["objects"].getFeatures("\"id\" = 'area-1'"))["name"] == {"fin": "Uusi nimi"}


def test_a_new_object_without_groups_reports_no_group_change(layers: dict[str, QgsVectorLayer]):
    area = PlanObject(
        geom=QgsGeometry.fromWkt("POLYGON((20 20, 30 20, 30 30, 20 30, 20 20))"),
        layer_name="Aluevaraus",
        name={"fin": "Uusi"},
    )

    result = _save_result(area)

    assert result.regulation_groups_changed is False
    assert result.id_ == area.id_
    assert _attribute_values(layers["associations"], "plan_regulation_group_id") == ["group-1"]


def test_an_added_group_reports_a_group_change(layers: dict[str, QgsVectorLayer]):
    area = _read_area(layers)
    area.regulation_groups.append(_read_group(layers, "group-2"))

    assert _save_result(area).regulation_groups_changed is True


def test_a_removed_group_reports_a_group_change(layers: dict[str, QgsVectorLayer]):
    area = _read_area(layers)
    area.regulation_groups = []

    assert _save_result(area).regulation_groups_changed is True


def test_a_changed_regulation_link_reports_a_group_change(layers: dict[str, QgsVectorLayer]):
    area = _read_area(layers)
    (group,) = area.regulation_groups
    (regulation,) = group.regulations
    regulation.theme_ids.append("theme-3")

    assert _save_result(area).regulation_groups_changed is True
