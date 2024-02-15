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


class SourceData(VersionedBase):
    """
    Lähtötietoaineistot
    """

    __tablename__ = "source_data"

    type_of_source_data_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("codes.type_of_source_data.id", name="type_of_source_data_id_fkey")
    )

    type_of_source_data = relationship("TypeOfSourceData", back_populates="source_data")
    name: Mapped[language_str]
    language: Mapped[language_str]
    additional_information_uri: Mapped[str]


class Operator(VersionedBase):
    """
    Toimija
    """

    __tablename__ = "operator"

    name: Mapped[language_str]
    business_id: Mapped[str]
    # administrative_region_id: koodilista
