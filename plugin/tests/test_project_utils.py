"""Layer lookups are scoped to a layer tree group, because layer names are not unique."""

from __future__ import annotations

import pytest
from qgis.core import QgsProject, QgsVectorLayer

from arho_feature_template.exceptions import LayerGroupNotFoundError, LayerNotFoundError
from arho_feature_template.project.layers import AbstractLayer
from arho_feature_template.utils.project_utils import (
    find_vector_layers,
    get_layer_group,
    get_vector_layer_from_project,
)

PLAN_GROUP = "Kaavasuunnitelma"
VALID_GROUP = "Ajantasakaava"


def _add_layer(project: QgsProject, group_name: str, layer_name: str, source: str) -> QgsVectorLayer:
    """Add a memory layer named `layer_name` into `group_name`, creating the group if needed."""
    root = project.layerTreeRoot()
    group = root.findGroup(group_name) or root.addGroup(group_name)
    layer = QgsVectorLayer(f"Point?crs=EPSG:3067&field=id:string&field=src:string({source})", layer_name, "memory")
    assert layer.isValid()
    project.addMapLayer(layer, addToLegend=False)
    group.addLayer(layer)
    return layer


@pytest.fixture
def project_with_groups(new_project: QgsProject) -> QgsProject:
    """Two groups holding same-named layers, like the real ARHO project."""
    plan_points = _add_layer(new_project, PLAN_GROUP, "Pisteet", "plan")
    valid_points = _add_layer(new_project, VALID_GROUP, "Pisteet", "valid")
    # A layer in a sub-group, like "Kaavasuunnitelma / Taustatiedot"
    root = new_project.layerTreeRoot()
    sub = root.findGroup(PLAN_GROUP).addGroup("Taustatiedot")
    documents = QgsVectorLayer("None?field=id:string", "Asiakirjat", "memory")
    new_project.addMapLayer(documents, addToLegend=False)
    sub.addLayer(documents)

    new_project.plan_points = plan_points  # type: ignore[attr-defined]
    new_project.valid_points = valid_points  # type: ignore[attr-defined]
    new_project.documents = documents  # type: ignore[attr-defined]
    return new_project


def test_lookup_picks_the_layer_from_the_given_group(project_with_groups: QgsProject):
    assert get_vector_layer_from_project("Pisteet", PLAN_GROUP).id() == project_with_groups.plan_points.id()
    assert get_vector_layer_from_project("Pisteet", VALID_GROUP).id() == project_with_groups.valid_points.id()


def test_lookup_searches_sub_groups(project_with_groups: QgsProject):
    assert get_vector_layer_from_project("Asiakirjat", PLAN_GROUP).id() == project_with_groups.documents.id()


def test_lookup_ignores_layers_of_other_groups(project_with_groups: QgsProject):  # noqa: ARG001
    assert find_vector_layers("Asiakirjat", VALID_GROUP) == []
    with pytest.raises(LayerNotFoundError):
        get_vector_layer_from_project("Asiakirjat", VALID_GROUP)


def test_missing_group_raises(project_with_groups: QgsProject):  # noqa: ARG001
    with pytest.raises(LayerGroupNotFoundError):
        get_layer_group("Ei ole")
    with pytest.raises(LayerGroupNotFoundError):
        get_vector_layer_from_project("Pisteet", "Ei ole")


def test_abstract_layer_uses_its_group(project_with_groups: QgsProject):
    class PlanPointLayer(AbstractLayer):
        name = "Pisteet"
        group = PLAN_GROUP

    class ValidPointLayer(AbstractLayer):
        name = "Pisteet"
        group = VALID_GROUP

    class MissingGroupLayer(AbstractLayer):
        name = "Pisteet"
        group = "Ei ole"

    assert PlanPointLayer.exists()
    assert ValidPointLayer.exists()
    assert not MissingGroupLayer.exists()

    assert PlanPointLayer.get_from_project().id() == project_with_groups.plan_points.id()
    assert ValidPointLayer.get_from_project().id() == project_with_groups.valid_points.id()
    with pytest.raises(LayerGroupNotFoundError):
        MissingGroupLayer.get_from_project()
