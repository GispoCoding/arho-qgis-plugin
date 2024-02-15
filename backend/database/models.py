import uuid
from datetime import datetime
from typing import Optional, Tuple

from base import PlanBase, VersionedBase, autoincrement_int, language_str, unique_str
from shapely.geometry import Polygon
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Plan(PlanBase):
    """
    Maakuntakaava, compatible with Ryhti 2.0 specification
    """

    __tablename__ = "plan"

    name: Mapped[language_str]
    approved_at: Mapped[Optional[datetime]]
    geom: Mapped[Polygon]


class PlanRegulationGroup(VersionedBase):
    """
    Kaavamääräysryhmä
    """

    __tablename__ = "plan_regulation_group"

    short_name: Mapped[unique_str]
    name: Mapped[language_str]
    # värikoodi?
    # group_type: oma koodilista


class PlanRegulation(PlanBase):
    """
    Kaavamääräys
    """

    __tablename__ = "plan_regulation"

    plan_regulation_group_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(
            "hame.plan_regulation_group.id", name="plan_regulation_group_id_fkey"
        )
    )

    type_of_plan_regulation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(
            "codes.type_of_plan_regulation.id", name="type_of_plan_regulation_id_fkey"
        )
    )
    type_of_verbal_plan_regulation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(
            "codes.type_of_verbal_plan_regulation.id",
            name="type_of_verbal_plan_regulation_id_fkey",
        ),
        nullable=True,
    )
    # type_of_additional_information_id: Mapped[uuid.UUID] = mapped_column(
    #     ForeignKey(
    #         "codes.type_of_additional_information.id",
    #         name="type_of_additional_information_id_fkey",
    #     )
    # )

    plan_regulation_group = relationship(
        "PlanRegulationGroup", back_populates="plan_regulations"
    )
    type_of_plan_regulation = relationship(
        "TypeOfPlanRegulation", back_populates="plan_regulations"
    )
    # plan_theme: kaavoitusteema-koodilista
    type_of_verbal_plan_regulation = relationship(
        "TypeOfVerbalPlanRegulation", back_populates="plan_regulations"
    )
    numeric_range: Mapped[Tuple[float, float]] = mapped_column(nullable=True)
    unit: Mapped[str] = mapped_column(nullable=True)
    text_value: Mapped[language_str]
    numeric_value: Mapped[float] = mapped_column(nullable=True)
    ordering: Mapped[autoincrement_int]
    # ElinkaaritilaX_pvm?
