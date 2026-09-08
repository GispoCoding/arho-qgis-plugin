"""The plan object readers build the same models from the editable layers and the valid views.

Only the layer tree group of the family under test exists in the project. A reader that
reached for a layer of the other family would fail with `LayerGroupNotFoundError`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from qgis.core import QgsFeature, QgsGeometry, QgsProject, QgsVectorLayer

from arho_feature_template.core.models import RegulationGroup
from arho_feature_template.project.layers.plan_layers import LandUseAreaLayer, RegulationGroupLayer
from arho_feature_template.project.layers.valid_layers import ValidLandUseAreaLayer, ValidRegulationGroupLayer
from arho_feature_template.utils.project_utils import PLAN_LAYER_GROUP_NAME, VALID_LAYER_GROUP_NAME

if TYPE_CHECKING:
    from arho_feature_template.project.layers.model_readers import PlanObjectReader

VALUE_FIELDS = (
    "&field=value_data_type:string&field=numeric_value:double&field=numeric_range_min:double"
    "&field=numeric_range_max:double&field=unit:string&field=text_value:map&field=text_syntax:string"
    "&field=code_list:string&field=code_value:string&field=code_title:map&field=height_reference_point:string"
)
VALIDITY_FIELDS = (
    "&field=lifecycle_status_id:string&field=period_of_validity_start:date&field=period_of_validity_end:date"
)

OBJECT_URI = (
    "Polygon?crs=EPSG:3067&field=id:string&field=name:map&field=description:map"
    "&field=type_of_underground_id:string&field=plan_id:string" + VALIDITY_FIELDS
)
ASSOCIATION_URI = (
    "None?field=id:string&field=plan_regulation_group_id:string&field=plan_id:string"
    "&field=land_use_area_id:string&field=other_area_id:string&field=line_id:string&field=point_id:string"
)
GROUP_URI = (
    "None?field=id:string&field=short_name:string&field=name:map"
    "&field=type_of_plan_regulation_group_id:string&field=plan_id:string&field=ordering:integer"
)
REGULATION_URI = (
    "None?field=id:string&field=plan_regulation_group_id:string&field=type_of_plan_regulation_id:string"
    "&field=ordering:integer&field=subject_identifiers:stringlist" + VALIDITY_FIELDS + VALUE_FIELDS
)
PROPOSITION_URI = (
    "None?field=id:string&field=plan_regulation_group_id:string&field=text_value:map&field=ordering:integer"
    + VALIDITY_FIELDS
)
ADDITIONAL_INFORMATION_URI = (
    "None?field=id:string&field=plan_regulation_id:string&field=type_additional_information_id:string" + VALUE_FIELDS
)
THEME_ASSOCIATION_URI = (
    "None?field=id:string&field=plan_regulation_id:string&field=plan_proposition_id:string&field=plan_theme_id:string"
)
VERBAL_TYPE_ASSOCIATION_URI = "None?field=plan_regulation_id:string&field=type_of_verbal_plan_regulation_id:string"


def _add_layer(project: QgsProject, group_name: str, layer_name: str, uri: str) -> QgsVectorLayer:
    root = project.layerTreeRoot()
    group = root.findGroup(group_name) or root.addGroup(group_name)
    layer = QgsVectorLayer(uri, layer_name, "memory")
    assert layer.isValid(), layer_name
    project.addMapLayer(layer, addToLegend=False)
    group.addLayer(layer)
    return layer


def _add_feature(layer: QgsVectorLayer, geometry: QgsGeometry | None = None, **attributes) -> QgsFeature:
    feature = QgsFeature(layer.fields())
    if geometry is not None:
        feature.setGeometry(geometry)
    for name, value in attributes.items():
        assert layer.fields().indexOf(name) != -1, name
        feature.setAttribute(name, value)
    ok, added = layer.dataProvider().addFeatures([feature])
    assert ok
    return added[0]


def _build_family(project: QgsProject, group_name: str, object_layer_name: str) -> dict[str, QgsVectorLayer]:
    """One object layer with its sibling layers, all inside `group_name`."""
    return {
        "objects": _add_layer(project, group_name, object_layer_name, OBJECT_URI),
        "associations": _add_layer(project, group_name, "Kaavamääräysryhmien assosiaatiot", ASSOCIATION_URI),
        "groups": _add_layer(project, group_name, "Kaavamääräysryhmät", GROUP_URI),
        "regulations": _add_layer(project, group_name, "Kaavamääräys", REGULATION_URI),
        "propositions": _add_layer(project, group_name, "Kaavasuositus", PROPOSITION_URI),
        "infos": _add_layer(project, group_name, "Kaavamääräyksen lisätiedot", ADDITIONAL_INFORMATION_URI),
        "themes": _add_layer(project, group_name, "Kaavoitusteemojen assosiaatiot", THEME_ASSOCIATION_URI),
        "verbal_types": _add_layer(
            project, group_name, "Sanallisten kaavamääräyksien lajien assosiaatiot", VERBAL_TYPE_ASSOCIATION_URI
        ),
    }


def _fill_family(layers: dict[str, QgsVectorLayer]) -> tuple[QgsFeature, QgsFeature]:
    """An area with one regulation group, and an area without groups."""
    square = QgsGeometry.fromWkt("POLYGON((0 0, 10 0, 10 10, 0 10, 0 0))")
    linked = _add_feature(
        layers["objects"],
        square,
        id="area-1",
        name={"fin": "Asuinalue"},
        description={"fin": "Kuvaus"},
        type_of_underground_id="underground-1",
        plan_id="plan-1",
        lifecycle_status_id="status-1",
    )
    unlinked = _add_feature(layers["objects"], square, id="area-2", name={"fin": "Tyhjä"}, plan_id="plan-1")

    _add_feature(layers["associations"], id="assoc-1", plan_regulation_group_id="group-1", land_use_area_id="area-1")
    _add_feature(
        layers["groups"],
        id="group-1",
        short_name="A",
        name={"fin": "Asuinrakennusten alue"},
        type_of_plan_regulation_group_id="group-type-1",
        plan_id="plan-1",
        ordering=3,
    )
    _add_feature(
        layers["regulations"],
        id="regulation-1",
        plan_regulation_group_id="group-1",
        type_of_plan_regulation_id="regulation-type-1",
        subject_identifiers=["kohde-1"],
        value_data_type="Numeric",
        numeric_value=2.0,
        unit="kpl",
    )
    _add_feature(
        layers["infos"],
        id="info-1",
        plan_regulation_id="regulation-1",
        type_additional_information_id="info-type-1",
        value_data_type="Code",
        code_value="code-1",
    )
    _add_feature(layers["themes"], id="theme-assoc-1", plan_regulation_id="regulation-1", plan_theme_id="theme-1")
    _add_feature(
        layers["verbal_types"], plan_regulation_id="regulation-1", type_of_verbal_plan_regulation_id="verbal-1"
    )
    _add_feature(
        layers["propositions"],
        id="proposition-1",
        plan_regulation_group_id="group-1",
        text_value={"fin": "Suositus"},
        ordering=1,
    )
    _add_feature(layers["themes"], id="theme-assoc-2", plan_proposition_id="proposition-1", plan_theme_id="theme-2")
    return linked, unlinked


FAMILIES = [
    pytest.param(ValidLandUseAreaLayer, VALID_LAYER_GROUP_NAME, "Aluevaraukset", id="valid"),
    pytest.param(LandUseAreaLayer, PLAN_LAYER_GROUP_NAME, "Aluevaraus", id="plan"),
]


@pytest.mark.parametrize(("layer_class", "group_name", "object_layer_name"), FAMILIES)
def test_reads_a_plan_object_with_its_regulation_groups(
    new_project: QgsProject, layer_class: type[PlanObjectReader], group_name: str, object_layer_name: str
):
    layers = _build_family(new_project, group_name, object_layer_name)
    linked, _ = _fill_family(layers)

    model = layer_class.model_from_feature(linked)

    assert model.id_ == "area-1"
    assert model.layer_name == "Aluevaraus"
    assert model.name == {"fin": "Asuinalue"}
    assert model.description == {"fin": "Kuvaus"}
    assert model.type_of_underground_id == "underground-1"
    assert model.plan_id == "plan-1"
    assert model.lifecycle_status_id == "status-1"
    assert model.period_of_validity_start is None
    assert model.modified is False
    assert model.geom is not None
    assert model.geom.area() == 100

    (group,) = model.regulation_groups
    assert group.id_ == "group-1"
    assert group.letter_code == "A"
    assert group.heading == {"fin": "Asuinrakennusten alue"}
    assert group.type_code_id == "group-type-1"
    assert group.group_number == 3
    assert group.modified is False

    (regulation,) = group.regulations
    assert regulation.id_ == "regulation-1"
    assert regulation.regulation_type_id == "regulation-type-1"
    assert regulation.regulation_group_id == "group-1"
    assert list(regulation.subject_identifiers) == ["kohde-1"]
    assert regulation.theme_ids == ["theme-1"]
    assert regulation.verbal_regulation_type_ids == ["verbal-1"]
    assert regulation.value is not None
    assert regulation.value.numeric_value == 2.0
    assert regulation.value.unit == "kpl"

    (info,) = regulation.additional_information
    assert info.id_ == "info-1"
    assert info.additional_information_type_id == "info-type-1"
    assert info.plan_regulation_id == "regulation-1"
    assert info.value is not None
    assert info.value.code_value == "code-1"

    (proposition,) = group.propositions
    assert proposition.id_ == "proposition-1"
    assert proposition.value == {"fin": "Suositus"}
    assert proposition.proposition_number == 1
    assert proposition.theme_ids == ["theme-2"]


@pytest.mark.parametrize(("layer_class", "group_name", "object_layer_name"), FAMILIES)
def test_an_object_without_associations_has_no_regulation_groups(
    new_project: QgsProject, layer_class: type[PlanObjectReader], group_name: str, object_layer_name: str
):
    layers = _build_family(new_project, group_name, object_layer_name)
    _, unlinked = _fill_family(layers)

    model = layer_class.model_from_feature(unlinked)

    assert model.id_ == "area-2"
    assert model.regulation_groups == []


def test_given_regulation_groups_are_used_instead_of_the_layer(new_project: QgsProject):
    layers = _build_family(new_project, VALID_LAYER_GROUP_NAME, "Aluevaraukset")
    linked, _ = _fill_family(layers)
    given = RegulationGroup(id_="group-1", heading={"fin": "Annettu"})

    (model,) = ValidLandUseAreaLayer.models_from_features([linked], regulation_groups=[given])

    assert model.regulation_groups == [given]
    assert model.regulation_groups[0].heading == {"fin": "Annettu"}


def test_each_family_reads_its_own_sibling_layers():
    assert ValidLandUseAreaLayer.family.regulation_group is ValidRegulationGroupLayer
    assert LandUseAreaLayer.family.regulation_group is RegulationGroupLayer
    assert ValidLandUseAreaLayer.association_attribute == LandUseAreaLayer.association_attribute == "land_use_area_id"
