"""Workaround for qgis/QGIS#65323: json values of a multi-feature insert batch are deferred to a
second commit on QGIS older than 4.2, where the PostgreSQL provider would write them as NULL."""

from __future__ import annotations

from typing import Iterator

import pytest
from qgis.core import Qgis, QgsFeature, QgsProject, QgsUnsetAttributeValue, QgsVariantUtils, QgsVectorLayer

from arho_feature_template.core import feature_editing
from arho_feature_template.core.feature_editing import (
    apply_deferred_json_values,
    commit_edit_buffer,
    defer_differing_json_values,
)

URI = "None?field=id:string&field=name:map&field=description:map&field=note:string"


@pytest.fixture
def layer(new_project: QgsProject, monkeypatch: pytest.MonkeyPatch) -> Iterator[QgsVectorLayer]:
    # The memory provider calls its json-like column type "map"
    monkeypatch.setattr(feature_editing, "JSON_FIELD_TYPE_NAMES", (*feature_editing.JSON_FIELD_TYPE_NAMES, "map"))
    layer = QgsVectorLayer(URI, "Kohteet", "memory")
    assert layer.isValid()
    new_project.addMapLayer(layer, addToLegend=False)
    # `QgsProject.commitChanges()` without a layer, as `commit_edit_buffer` does, needs this mode
    new_project.setTransactionMode(Qgis.TransactionMode.BufferedGroups)
    new_project.startEditing(layer)
    yield layer
    # A project cleared with an open buffered-groups edit session breaks the next session
    if layer.isEditable():
        new_project.rollBack(stopEditing=True)


def _add(layer: QgsVectorLayer, id_: str, name: dict | None, description: dict | None = None) -> None:
    feature = QgsFeature(layer.fields())
    feature["id"] = id_
    feature["name"] = name
    feature["description"] = description
    feature["note"] = id_
    assert layer.addFeature(feature)


def _stored(layer: QgsVectorLayer, field: str) -> dict[str, object]:
    return {feature["id"]: feature[field] for feature in layer.getFeatures()}


def test_differing_values_are_stripped_and_returned(layer: QgsVectorLayer):
    _add(layer, "a", {"fin": "A"})
    _add(layer, "b", {"fin": "B"})

    deferred = defer_differing_json_values()

    assert {(item.id_, item.field_index, item.value["fin"]) for item in deferred} == {("a", 1, "A"), ("b", 1, "B")}
    assert all(item.layer is layer for item in deferred)
    buffered = {feature["id"]: feature["name"] for feature in layer.editBuffer().addedFeatures().values()}
    assert all(QgsVariantUtils.isNull(value) for value in buffered.values())


def test_a_map_next_to_a_null_is_deferred(layer: QgsVectorLayer):
    _add(layer, "a", {"fin": "A"})
    _add(layer, "b", None)

    deferred = defer_differing_json_values()

    assert [(item.id_, item.value) for item in deferred] == [("a", {"fin": "A"})]


def test_a_single_feature_or_equal_values_are_left_alone(layer: QgsVectorLayer):
    _add(layer, "a", {"fin": "A"})
    assert defer_differing_json_values() == []

    _add(layer, "b", {"fin": "A"})
    assert defer_differing_json_values() == []
    assert {feature["name"]["fin"] for feature in layer.editBuffer().addedFeatures().values()} == {"A"}


def test_values_come_back_after_the_rows_exist(layer: QgsVectorLayer):
    _add(layer, "a", {"fin": "A"}, {"fin": "kuvaus"})
    _add(layer, "b", {"fin": "B"})

    deferred = defer_differing_json_values()
    assert layer.commitChanges(stopEditing=False)
    assert _stored(layer, "name") == {"a": None, "b": None}

    assert apply_deferred_json_values(deferred)
    assert layer.commitChanges(stopEditing=False)

    assert _stored(layer, "name") == {"a": {"fin": "A"}, "b": {"fin": "B"}}
    assert _stored(layer, "description") == {"a": {"fin": "kuvaus"}, "b": None}
    assert _stored(layer, "note") == {"a": "a", "b": "b"}


def test_commit_edit_buffer_keeps_the_values_on_old_qgis(layer: QgsVectorLayer, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(feature_editing, "JSON_BATCH_INSERT_BROKEN", True)
    applied: list[str] = []
    feature_editing._after_commit.append(lambda: applied.append("done"))
    _add(layer, "a", {"fin": "A"})
    _add(layer, "b", {"fin": "B"})

    assert commit_edit_buffer(stop_editing=True)

    assert _stored(layer, "name") == {"a": {"fin": "A"}, "b": {"fin": "B"}}
    assert applied == ["done"]
    assert not layer.isEditable()


def test_commit_edit_buffer_does_nothing_extra_on_fixed_qgis(layer: QgsVectorLayer, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(feature_editing, "JSON_BATCH_INSERT_BROKEN", False)
    calls: list[int] = []
    monkeypatch.setattr(feature_editing, "defer_differing_json_values", lambda: calls.append(1))
    _add(layer, "a", {"fin": "A"})
    _add(layer, "b", {"fin": "B"})

    assert commit_edit_buffer(stop_editing=False)

    assert calls == []
    assert _stored(layer, "name") == {"a": {"fin": "A"}, "b": {"fin": "B"}}
    assert layer.isEditable()


def test_column_default_is_kept_as_placeholder(layer: QgsVectorLayer, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(type(layer.dataProvider()), "defaultValueClause", lambda _self, _idx: "'{}'::jsonb")
    _add(layer, "a", {"fin": "A"})
    _add(layer, "b", {"fin": "B"})

    defer_differing_json_values()

    placeholders = [feature["name"] for feature in layer.editBuffer().addedFeatures().values()]
    assert all(isinstance(value, QgsUnsetAttributeValue) for value in placeholders)
