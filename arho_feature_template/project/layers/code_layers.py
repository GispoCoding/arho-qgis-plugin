from __future__ import annotations

from typing import ClassVar

from qgis.core import QgsFeatureRequest

from arho_feature_template.project.layers import AbstractLayer


class AbstractCodeLayer(AbstractLayer): ...


class PlanTypeLayer(AbstractCodeLayer):
    name = "Kaavalaji"


class LifeCycleStatusLayer(AbstractCodeLayer):
    name = "Elinkaaren tila"


class OrganisationLayer(AbstractCodeLayer):
    name = "Toimija"


class UndergroundTypeLayer(AbstractCodeLayer):
    name = "Maanalaisuuden tyyppi"


class PlanRegulationGroupTypeLayer(AbstractCodeLayer):
    name = "Kaavamääräysryhmän tyyppi"

    LAYER_NAME_TO_REGULATION_GROUP_TYPE_MAP: ClassVar[dict[str, str]] = {
        "Kaava": "generalRegulations",
        "Aluevaraus": "landUseRegulations",
        "Osa-alue": "otherAreaRegulations",
        "Viiva": "lineRegulations",
        "Muu piste": "otherPointRegulations",
        "Maankäytön kohteet": "landUseRegulations",
    }

    @classmethod
    def get_id_by_feature_layer_name(cls, layer_name: str) -> str | None:
        regulation_group_type = cls.LAYER_NAME_TO_REGULATION_GROUP_TYPE_MAP.get(layer_name)

        request = QgsFeatureRequest().setFilterExpression(f"\"value\"='{regulation_group_type}'")
        feature = next(cls.get_from_project().getFeatures(request), None)
        if feature:
            return feature["id"]

        return None


class PlanRegulationTypeLayer(AbstractCodeLayer):
    name = "Kaavamääräyslaji"

    @classmethod
    def get_regulation_type_by_id(cls, _id: str) -> str | None:
        for feature in cls.get_from_project().getFeatures():
            if feature["id"] == _id:
                return feature["value"]

        return None


code_layers = AbstractCodeLayer.__subclasses__()
