"""The lifecycle menu takes the plan type from the project variable, not from the plan matter row.

The menu is built once per regulation and proposition widget of a form, so a plan matter
read here would repeat once per widget. The project has no plan matter layer at all: a
read would raise `LayerNotFoundError`.
"""

from __future__ import annotations

from typing import Iterator

import pytest
from qgis.core import QgsFeature, QgsProject, QgsVectorLayer

from arho_feature_template.core.lifecycles import LifeCycleStatusValue
from arho_feature_template.gui.components.edit_lifecycle_menu import EditLifecycleMenu
from arho_feature_template.project.layers.code_layers import LifeCycleStatusLayer, PlanTypeLayer
from arho_feature_template.utils.misc_utils import set_active_plan_matter_plan_type_id
from arho_feature_template.utils.project_utils import CODE_LAYER_GROUP_NAME

REGIONAL_TYPE_ID = "type-regional"
TOWN_TYPE_ID = "type-town"


def _add_code_layer(project: QgsProject, layer_name: str, uri: str, rows: list[dict]) -> QgsVectorLayer:
    root = project.layerTreeRoot()
    group = root.findGroup(CODE_LAYER_GROUP_NAME) or root.addGroup(CODE_LAYER_GROUP_NAME)
    layer = QgsVectorLayer(uri, layer_name, "memory")
    assert layer.isValid()
    for row in rows:
        feature = QgsFeature(layer.fields())
        for key, value in row.items():
            feature.setAttribute(key, value)
        assert layer.dataProvider().addFeature(feature)
    project.addMapLayer(layer, addToLegend=False)
    group.addLayer(layer)
    return layer


@pytest.fixture
def code_layers(new_project: QgsProject) -> Iterator[QgsProject]:
    """The lifecycle statuses and the plan types, the only layers the menu needs."""
    _add_code_layer(
        new_project,
        LifeCycleStatusLayer.name,
        "None?field=id:string&field=value:string&field=name:map",
        [{"id": f"lc-{value}", "value": value.value, "name": {"fin": value.name}} for value in LifeCycleStatusValue],
    )
    _add_code_layer(
        new_project,
        PlanTypeLayer.name,
        "None?field=id:string&field=value:string",
        [{"id": REGIONAL_TYPE_ID, "value": "11"}, {"id": TOWN_TYPE_ID, "value": "31"}],
    )
    yield new_project
    # The code layer caches are class-level and would outlive this project
    for layer_class in (LifeCycleStatusLayer, PlanTypeLayer):
        layer_class._cache.clear()
        layer_class._field_names.clear()


@pytest.fixture
def make_menu() -> Iterator:
    menus: list[EditLifecycleMenu] = []

    def make() -> EditLifecycleMenu:
        menu = EditLifecycleMenu()
        menus.append(menu)
        return menu

    yield make
    for menu in menus:
        menu.deleteLater()


def _lifecycle_values(menu: EditLifecycleMenu) -> list[LifeCycleStatusValue]:
    return [action.data() for action in menu.actions()]


def test_a_regional_plan_offers_validity_before_legal_validity(code_layers, make_menu):  # noqa: ARG001
    set_active_plan_matter_plan_type_id(REGIONAL_TYPE_ID)

    values = _lifecycle_values(make_menu())

    assert LifeCycleStatusValue.VALID_BEFORE_LEGAL_VALIDITY in values
    assert values.index(LifeCycleStatusValue.VALID_BEFORE_LEGAL_VALIDITY) == 2


def test_a_town_plan_does_not_offer_validity_before_legal_validity(code_layers, make_menu):  # noqa: ARG001
    set_active_plan_matter_plan_type_id(TOWN_TYPE_ID)

    values = _lifecycle_values(make_menu())

    assert LifeCycleStatusValue.VALID_BEFORE_LEGAL_VALIDITY not in values
    assert LifeCycleStatusValue.VALID in values


def test_without_a_plan_matter_the_menu_still_builds(code_layers, make_menu):  # noqa: ARG001
    set_active_plan_matter_plan_type_id(None)

    values = _lifecycle_values(make_menu())

    assert LifeCycleStatusValue.VALID_BEFORE_LEGAL_VALIDITY not in values
    assert len(values) == 7
