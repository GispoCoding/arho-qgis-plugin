import uuid
from datetime import datetime
from typing import Optional, Tuple

# we have to import CodeBase in codes.py from here to allow two-way relationships
from base import (  # noqa
    CodeBase,
    PlanBase,
    PlanFeatureBase,
    VersionedBase,
    autoincrement_int,
    language_str,
    unique_str,
)
from shapely.geometry import MultiLineString, MultiPoint, MultiPolygon
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Plan(PlanBase):
    """
    Maakuntakaava, compatible with Ryhti 2.0 specification
    """

    __tablename__ = "plan"

    name: Mapped[language_str]
    approved_at: Mapped[Optional[datetime]]
    geom: Mapped[MultiPolygon]


class LandUseArea(PlanFeatureBase):
    """
    Osa-alue
    """

    __tablename__ = "land_use_area"

    geom: Mapped[MultiPolygon]


class OtherArea(PlanFeatureBase):
    """
    Aluevaraus
    """

    __tablename__ = "other_area"

    geom: Mapped[MultiPolygon]


class Line(PlanFeatureBase):
    """
    Viivat
    """

    __tablename__ = "line"

    geom: Mapped[MultiLineString]


class LandUsePoint(PlanFeatureBase):
    """
    Maankäytön pisteet
    """

    __tablename__ = "land_use_point"

    geom: Mapped[MultiPoint]


class OtherPoint(PlanFeatureBase):
    """
    Muut pisteet
    """

    __tablename__ = "other_point"

    geom: Mapped[MultiPoint]


class PlanRegulationGroup(VersionedBase):
    """
    Kaavamääräysryhmä
    """

    __tablename__ = "plan_regulation_group"

    plan_regulations = relationship(
        "PlanRegulation", back_populates="plan_regulation_group"
    )
    plan_propositions = relationship(
        "PlanProposition", back_populates="plan_regulation_group"
    )
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


class PlanProposition(PlanBase):
    """
    Kaavasuositus
    """

    __tablename__ = "plan_proposition"

    plan_regulation_group_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(
            "hame.plan_regulation_group.id", name="plan_regulation_group_id_fkey"
        )
    )

    plan_regulation_group = relationship(
        "PlanRegulationGroup", back_populates="plan_propositions"
    )
    text_value: Mapped[language_str]
    ordering: Mapped[autoincrement_int]
    # plan_theme: kaavoitusteema-koodilista
    # ElinkaaritilaX_pvm
