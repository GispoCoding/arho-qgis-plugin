"""Listing the validation results in the validation dock.

The features the results point to are fetched with one query per layer, not one per
result: a query costs ~140 ms on a remote database and a large result has hundreds
of entries.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any

import pytest
from qgis.core import QgsGeometry

from arho_feature_template.gui.components.validation_tree_view import ValidationModel
from arho_feature_template.project.layers import AbstractLayer
from arho_feature_template.project.layers.plan_layers import (
    AdditionalInformationLayer,
    OtherAreaLayer,
    PlanPropositionLayer,
    PlanRegulationLayer,
    RegulationGroupLayer,
    plan_object_layers,
)

if TYPE_CHECKING:
    from collections.abc import Iterator

    from qgis.PyQt.QtGui import QStandardItem

    from arho_feature_template.plugin import Plugin

pytestmark = pytest.mark.fake_iface


class _Feature(dict):
    """Stands in for a QgsFeature: attributes by name and a geometry."""

    def geometry(self) -> QgsGeometry:
        return QgsGeometry()


class _Database:
    """Features by layer. Records the layer of every query."""

    def __init__(self) -> None:
        self.features: dict[type[AbstractLayer], list[_Feature]] = {}
        self.queries: list[type[AbstractLayer]] = []

    def add(self, layer: type[AbstractLayer], **attributes: Any) -> str:
        id_ = str(uuid.uuid4())
        self.features.setdefault(layer, []).append(_Feature(id=id_, **attributes))
        return id_


@pytest.fixture
def database(monkeypatch: pytest.MonkeyPatch) -> _Database:
    database = _Database()

    def get_features_by_attribute_value(cls, attribute, value, no_geometries=True) -> Iterator[_Feature]:  # noqa: ARG001
        values = {value} if isinstance(value, str) else set(value)
        if not values:
            return
        database.queries.append(cls)
        yield from (feature for feature in database.features.get(cls, []) if feature[attribute] in values)

    def get_attribute_values_by_another_attribute_value(cls, target_attribute, filter_attribute, filter_value):
        for feature in get_features_by_attribute_value(cls, filter_attribute, filter_value):
            yield feature[target_attribute]

    monkeypatch.setattr(AbstractLayer, "get_features_by_attribute_value", classmethod(get_features_by_attribute_value))
    monkeypatch.setattr(
        AbstractLayer,
        "get_attribute_values_by_another_attribute_value",
        classmethod(get_attribute_values_by_another_attribute_value),
    )
    return database


def _error(instance: str, class_key: str) -> dict:
    return {"ruleId": "rule__x", "message": "Virhe", "instance": instance, "classKey": class_key}


def _child(parent: QStandardItem, text: str) -> QStandardItem:
    for row in range(parent.rowCount()):
        if parent.child(row, 0).text() == text:
            return parent.child(row, 0)
    texts = [parent.child(row, 0).text() for row in range(parent.rowCount())]
    msg = f"No child {text!r} in {texts}"
    raise AssertionError(msg)


def _errors(plugin: Plugin) -> QStandardItem:
    return plugin.validation_dock.validation_result_tree_view.model.item(ValidationModel.ERROR_INDEX, 0)


def test_plan_object_errors_query_each_layer_once(plugin: Plugin, database: _Database):
    ids = [database.add(OtherAreaLayer, name={"fin": f"Alue {i}"}) for i in range(200)]
    errors = [_error(f"plan.planObjects[{i}].geometry", id_) for i, id_ in enumerate(ids)]

    plugin.validation_dock.list_validation_errors({"status": 400, "errors": errors, "warnings": []})

    assert len(database.queries) == len(plan_object_layers)
    plan_objects = _child(_child(_errors(plugin), "Kaavasuunnitelma"), "Kaavakohteet")
    assert plan_objects.rowCount() == 200
    assert plan_objects.child(0, 0).text() == "Alue 0"


def test_regulation_groups_are_found_through_regulations_propositions_and_additional_informations(
    plugin: Plugin, database: _Database
):
    group_ids = [database.add(RegulationGroupLayer, name={"fin": f"Ryhmä {i}"}) for i in range(3)]
    regulation_id = database.add(PlanRegulationLayer, plan_regulation_group_id=group_ids[0], name=None)
    proposition_id = database.add(PlanPropositionLayer, plan_regulation_group_id=group_ids[1], name=None)
    information_regulation_id = database.add(PlanRegulationLayer, plan_regulation_group_id=group_ids[2], name=None)
    information_id = database.add(
        AdditionalInformationLayer, plan_regulation_id=information_regulation_id, name={"fin": "Lisätieto"}
    )
    dock = plugin.validation_dock

    dock.load_features(
        [
            _error("plan.planRegulationGroups[0].planRegulations[0].value", regulation_id),
            _error("plan.planRegulationGroups[1].planRecommendations[0].value", proposition_id),
            _error("plan.planRegulationGroups[2].planRegulations[0].additionalInformations[0].type", information_id),
        ]
    )

    assert dock.regulation_group_ids == {
        regulation_id: group_ids[0],
        proposition_id: group_ids[1],
        information_id: group_ids[2],
    }
    assert set(dock.layer_features) == {regulation_id, proposition_id, information_id, *group_ids}
    assert dock.layer_features[group_ids[2]][1] is RegulationGroupLayer
    # The regulation of the additional information is only a step to its group
    assert information_regulation_id not in dock.layer_features
    assert database.queries.count(PlanRegulationLayer) == 1
    assert database.queries.count(RegulationGroupLayer) == 1
