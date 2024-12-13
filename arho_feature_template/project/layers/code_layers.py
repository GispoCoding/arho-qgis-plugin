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


code_layers = AbstractCodeLayer.__subclasses__()
