from __future__ import annotations

import logging
from string import Template
from textwrap import dedent
from typing import ClassVar

from qgis.utils import iface

from arho_feature_template.project.layers import AbstractLayer

logger = logging.getLogger(__name__)


class AbstractPlanLayer(AbstractLayer):
    filter_template: ClassVar[Template]

    @classmethod
    def apply_filter(cls, plan_id: str | None) -> None:
        """Apply a filter to the layer based on the plan_id."""
        filter_expression = cls.filter_template.substitute(plan_id=plan_id) if plan_id else ""
        layer = cls.get_from_project()
        if not layer:
            logger.warning("Layer %s not found", cls.name)
            return None
        result = layer.setSubsetString(filter_expression)
        if result is False:
            iface.messageBar().pushMessage(
                "Error",
                f"Failed to filter layer {cls.name} with query {filter_expression}",
                level=3,
            )


class PlanLayer(AbstractPlanLayer):
    name = "Kaava"
    filter_template = Template("id = '$plan_id'")


class LandUsePointLayer(AbstractPlanLayer):
    name = "Maankäytön kohteet"
    filter_template = Template("plan_id = '$plan_id'")


class OtherPointLayer(AbstractPlanLayer):
    name = "Muut pisteet"
    filter_template = Template("plan_id = '$plan_id'")


class LineLayer(AbstractPlanLayer):
    name = "Viivat"
    filter_template = Template("plan_id = '$plan_id'")


class LandUseAreaLayer(AbstractPlanLayer):
    name = "Aluevaraus"
    filter_template = Template("plan_id = '$plan_id'")


class OtherAreaLayer(AbstractPlanLayer):
    name = "Osa-alue"
    filter_template = Template("plan_id = '$plan_id'")


class PlanRegulationGroupLayer(AbstractPlanLayer):
    name = "Kaavamääräysryhmät"
    filter_template = Template("plan_id = '$plan_id'")


class RegulationGroupAssociationLayer(AbstractPlanLayer):
    name = "Kaavamääräysryhmien assosiaatiot"
    filter_template = Template(
        dedent(
            """\
            EXISTS (
                SELECT 1
                FROM hame.plan_regulation_group prg
                WHERE
                    hame.regulation_group_association.plan_regulation_group_id = prg.id
                    AND prg.plan_id = '$plan_id'
            )"""
        )
    )


class PlanRegulationLayer(AbstractPlanLayer):
    name = "Kaavamääräys"
    filter_template = Template(
        dedent(
            """\
            EXISTS (
                SELECT 1
                FROM hame.plan_regulation_group prg
                WHERE
                    hame.plan_regulation.plan_regulation_group_id = prg.id
                    AND prg.plan_id = '$plan_id'
            )"""
        )
    )


class PlanPropositionLayer(AbstractPlanLayer):
    name = "Kaavasuositus"
    filter_template = Template(
        dedent(
            """\
            EXISTS (
                SELECT 1
                FROM hame.plan_regulation_group rg
                WHERE
                    hame.plan_proposition.plan_regulation_group_id = rg.id
                    AND rg.plan_id = '$plan_id'
            )"""
        )
    )


class DocumentLayer(AbstractPlanLayer):
    name = "Asiakirjat"
    filter_template = Template("plan_id = '$plan_id'")


class SourceDataLayer(AbstractPlanLayer):
    name = "Lähtötietoaineistot"
    filter_template = Template("plan_id = '$plan_id'")


plan_layers = AbstractPlanLayer.__subclasses__()
