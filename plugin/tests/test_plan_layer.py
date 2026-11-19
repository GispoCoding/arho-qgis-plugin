"""The plan layer reads the final flag of a plan and never writes it.

Only the backend makes a plan final. The plugin shows the flag and leaves the column
alone, so an old database without the column still works.
"""

from __future__ import annotations

import pytest
from qgis.core import QgsFeature, QgsGeometry, QgsProject, QgsVariantUtils, QgsVectorLayer

from arho_feature_template.core.models import Plan
from arho_feature_template.project.layers import plan_layers as plan_layers_module
from arho_feature_template.project.layers.plan_layers import PlanLayer
from arho_feature_template.utils.project_utils import PLAN_LAYER_GROUP_NAME

PLAN_FIELDS = (
    "field=id:string&field=name:map&field=description:map&field=scale:integer"
    "&field=lifecycle_status_id:string&field=plan_matter_id:string&field=approval_date:date"
    "&field=period_of_validity_start:date&field=period_of_validity_end:date&field=locked:boolean"
)
PLAN_URI = f"MultiPolygon?crs=EPSG:3067&{PLAN_FIELDS}&field=final:boolean"
OLD_PLAN_URI = f"MultiPolygon?crs=EPSG:3067&{PLAN_FIELDS}"

OUTLINE = QgsGeometry.fromWkt("MULTIPOLYGON (((0 0, 10 0, 10 10, 0 10, 0 0)))")


@pytest.fixture
def _no_sibling_layers(monkeypatch: pytest.MonkeyPatch) -> None:
    """The regulation group, legal effect and document layers are not part of this seam."""
    for layer_class in (
        plan_layers_module.RegulationGroupAssociationLayer,
        plan_layers_module.LegalEffectAssociationLayer,
        plan_layers_module.DocumentLayer,
    ):
        monkeypatch.setattr(layer_class, "get_features_by_attribute_value", lambda *_args, **_kwargs: [])


def _add_plan_layer(project: QgsProject, uri: str) -> QgsVectorLayer:
    root = project.layerTreeRoot()
    group = root.addGroup(PLAN_LAYER_GROUP_NAME)
    layer = QgsVectorLayer(uri, PlanLayer.name, "memory")
    assert layer.isValid()
    project.addMapLayer(layer, addToLegend=False)
    group.addLayer(layer)
    return layer


@pytest.fixture
def plan_layer(new_project: QgsProject) -> QgsVectorLayer:
    return _add_plan_layer(new_project, PLAN_URI)


@pytest.fixture
def old_plan_layer(new_project: QgsProject) -> QgsVectorLayer:
    """A plan layer from a database that predates the final column."""
    return _add_plan_layer(new_project, OLD_PLAN_URI)


def _plan_feature(layer: QgsVectorLayer, plan_id: str, **attributes) -> QgsFeature:
    feature = QgsFeature(layer.fields())
    feature.setGeometry(OUTLINE)
    feature.setAttribute("id", plan_id)
    feature.setAttribute("name", {"fin": "Kaava"})
    for name, value in attributes.items():
        feature.setAttribute(name, value)
    return feature


@pytest.mark.usefixtures("_no_sibling_layers")
def test_a_final_plan_is_read_as_final(plan_layer: QgsVectorLayer):
    feature = _plan_feature(plan_layer, "plan-1", final=True)

    assert PlanLayer.model_from_feature(feature).final is True


@pytest.mark.usefixtures("_no_sibling_layers")
def test_a_plan_that_is_not_final_is_read_as_not_final(plan_layer: QgsVectorLayer):
    feature = _plan_feature(plan_layer, "plan-1", final=False)

    assert PlanLayer.model_from_feature(feature).final is False


@pytest.mark.usefixtures("_no_sibling_layers")
def test_a_plan_without_the_final_field_is_not_final(old_plan_layer: QgsVectorLayer):
    feature = _plan_feature(old_plan_layer, "plan-1")

    assert PlanLayer.model_from_feature(feature).final is False


def test_saving_a_plan_keeps_the_final_flag_of_the_layer(plan_layer: QgsVectorLayer):
    """The model may be stale; the column belongs to the backend."""
    plan_layer.dataProvider().addFeatures([_plan_feature(plan_layer, "plan-1", final=True)])
    stale_model = Plan(id_="plan-1", name="Kaava", geom=OUTLINE, final=False)

    feature = PlanLayer.feature_from_model(stale_model)

    assert feature["final"] is True


def test_a_new_plan_leaves_the_final_field_unset(plan_layer: QgsVectorLayer):  # noqa: ARG001
    feature = PlanLayer.feature_from_model(Plan(name="Kaava", geom=OUTLINE, final=True))

    assert QgsVariantUtils.isNull(feature["final"])
