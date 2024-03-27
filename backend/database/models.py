import uuid
from datetime import datetime
from typing import Literal, Optional

# we have to import CodeBase in codes.py from here to allow two-way relationships
from base import (  # noqa
    CodeBase,
    PlanBase,
    PlanObjectBase,
    VersionedBase,
    language_str,
    numeric_range,
    timestamp,
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

    organisation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("hame.organisation.id", name="organisation_id_fkey")
    )
    organisation = relationship("Organisation", backref="plans")
    plan_regulation_group_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey(
            "hame.plan_regulation_group.id", name="plan_regulation_group_id_fkey"
        )
    )
    plan_regulation_group = relationship("PlanRegulationGroup", backref="plans")
    plan_type_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("codes.plan_type.id", name="plan_type_id_fkey")
    )
    plan_type = relationship("PlanType", backref="plans")

    permanent_plan_identifier: Mapped[Optional[str]]
    producers_plan_identifier: Mapped[Optional[str]]
    description: Mapped[language_str]
    scale: Mapped[Optional[int]]
    matter_management_identifier: Mapped[Optional[str]]
    record_number: Mapped[Optional[str]]
    approved_at: Mapped[Optional[datetime]]
    geom: Mapped[MultiPolygon]


class LandUseArea(PlanObjectBase):
    """
    Osa-alue
    """

    __tablename__ = "land_use_area"

    geom: Mapped[MultiPolygon]


class OtherArea(PlanObjectBase):
    """
    Aluevaraus
    """

    __tablename__ = "other_area"

    geom: Mapped[MultiPolygon]


class Line(PlanObjectBase):
    """
    Viivat
    """

    __tablename__ = "line"

    geom: Mapped[MultiLineString]


class LandUsePoint(PlanObjectBase):
    """
    Maankäytön pisteet
    """

    __tablename__ = "land_use_point"

    geom: Mapped[MultiPoint]


class OtherPoint(PlanObjectBase):
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

    short_name: Mapped[unique_str]
    name: Mapped[language_str]
    # värikoodi?
    type_of_plan_regulation_group_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(
            "codes.type_of_plan_regulation_group.id",
            name="type_of_plan_regulation_group_id_fkey",
        )
    )
    type_of_plan_regulation_group = relationship(
        "TypeOfPlanRegulationGroup", backref="plan_regulation_groups"
    )


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
    plan_regulation_group = relationship(
        "PlanRegulationGroup", backref="plan_regulations"
    )
    type_of_plan_regulation = relationship(
        "TypeOfPlanRegulation", backref="plan_regulations"
    )
    # plan_theme: kaavoitusteema-koodilista
    type_of_verbal_plan_regulation = relationship(
        "TypeOfVerbalPlanRegulation", backref="plan_regulations"
    )

    # Käyttötarkoitus
    intended_use_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(
            "codes.type_of_additional_information.id",
            name="intended_use_id_fkey",
        ),
        nullable=True,
    )
    # Olemassaolo
    existence_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(
            "codes.type_of_additional_information.id",
            name="existence_id_fkey",
        ),
        nullable=True,
    )
    # Tyyppi
    regulation_type_additional_information_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(
            "codes.type_of_additional_information.id",
            name="regulation_type_additional_information_id_fkey",
        ),
        nullable=True,
    )
    # Merkittävyys
    significance_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(
            "codes.type_of_additional_information.id",
            name="significance_id_fkey",
        ),
        nullable=True,
    )
    # Eri tahojen tarpeisiin varaus
    reservation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(
            "codes.type_of_additional_information.id",
            name="reservation_id_fkey",
        ),
        nullable=True,
    )
    # Kehittäminen
    development_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(
            "codes.type_of_additional_information.id",
            name="development_id_fkey",
        ),
        nullable=True,
    )
    # Häiriöntorjuntatarve
    disturbance_prevention_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(
            "codes.type_of_additional_information.id",
            name="disturbance_prevention_id_fkey",
        ),
        nullable=True,
    )
    # Rakentamisen ohjaus
    construction_control_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(
            "codes.type_of_additional_information.id",
            name="construction_control_id_fkey",
        ),
        nullable=True,
    )
    intended_use = relationship(
        "TypeOfAdditionalInformation",
        foreign_keys=[intended_use_id],
        backref="intended_use_plan_regulations",
    )
    existence = relationship(
        "TypeOfAdditionalInformation",
        foreign_keys=[existence_id],
        backref="existence_plan_regulations",
    )
    regulation_type_additional_information = relationship(
        "TypeOfAdditionalInformation",
        foreign_keys=[regulation_type_additional_information_id],
        backref="type_plan_regulations",
    )
    significance = relationship(
        "TypeOfAdditionalInformation",
        foreign_keys=[significance_id],
        backref="significance_plan_regulations",
    )
    reservation = relationship(
        "TypeOfAdditionalInformation",
        foreign_keys=[reservation_id],
        backref="reservation_plan_regulations",
    )
    development = relationship(
        "TypeOfAdditionalInformation",
        foreign_keys=[development_id],
        backref="development_plan_regulations",
    )
    disturbance_prevention = relationship(
        "TypeOfAdditionalInformation",
        foreign_keys=[disturbance_prevention_id],
        backref="disturbance_prevention_plan_regulations",
    )
    construction_control = relationship(
        "TypeOfAdditionalInformation",
        foreign_keys=[construction_control_id],
        backref="construction_control_plan_regulations",
    )

    numeric_range: Mapped[numeric_range]
    unit: Mapped[str] = mapped_column(nullable=True)
    text_value: Mapped[language_str]
    numeric_value: Mapped[float] = mapped_column(nullable=True)
    ordering: Mapped[Optional[int]] = mapped_column(index=True)
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
        "PlanRegulationGroup", backref="plan_propositions"
    )
    text_value: Mapped[language_str]
    ordering: Mapped[Optional[int]] = mapped_column(index=True)
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

    type_of_source_data = relationship("TypeOfSourceData", backref="source_data")
    name: Mapped[language_str]
    additional_information_uri: Mapped[str]
    detachment_date: Mapped[datetime]


class Organisation(VersionedBase):
    """
    Toimija
    """

    __tablename__ = "organisation"

    name: Mapped[language_str]
    business_id: Mapped[str]
    administrative_region_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(
            "codes.administrative_region.id", name="administrative_region_id_fkey"
        )
    )
    administrative_region = relationship(
        "AdministrativeRegion", backref="organisations"
    )


class Document(VersionedBase):
    """
    Asiakirja
    """

    __tablename__ = "document"

    type_of_document_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("codes.type_of_document.id", name="type_of_document_id_fkey")
    )
    plan_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("hame.plan.id", name="plan_id_fkey")
    )

    type_of_document = relationship("TypeOfDocument", backref="documents")
    plan = relationship("Plan", backref="documents")
    permanent_document_identifier: Mapped[Optional[uuid.UUID]]
    name: Mapped[str]
    personal_details: Mapped[str]
    publicity: Mapped[Literal["julkinen", "ei julkinen"]]  # Muita?
    language: Mapped[str]
    decision: Mapped[bool]
    decision_date: Mapped[Optional[timestamp]]
    # file
