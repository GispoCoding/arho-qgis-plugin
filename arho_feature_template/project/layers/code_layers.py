from __future__ import annotations

from arho_feature_template.project.layers import AbstractLayer


class AbstractCodeLayer(AbstractLayer): ...


class PlanTypeLayer(AbstractCodeLayer):
    name = "Kaavalaji"


class LifeCycleStatusLayer(AbstractCodeLayer):
    name = "Elinkaaren tila"


code_layers = AbstractCodeLayer.__subclasses__()
