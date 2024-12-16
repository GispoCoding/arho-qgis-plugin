from __future__ import annotations

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

    @classmethod
    def get_id_of_regulation_type(cls, regulation_type: str) -> str | None:
        for feature in cls.get_from_project().getFeatures():
            if feature["value"] == regulation_type:
                return feature["id"]

        return None


code_layers = AbstractCodeLayer.__subclasses__()
