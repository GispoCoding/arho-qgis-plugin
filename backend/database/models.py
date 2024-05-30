import uuid
from datetime import datetime
from typing import List, Literal, Optional

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
    organisation: Mapped["Organisation"] = relationship(
        "Organisation", backref="plans", lazy="joined"
    )
    plan_regulation_group_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey(
            "hame.plan_regulation_group.id", name="plan_regulation_group_id_fkey"
        )
    )
    # Let's do lazy loading for all general plan regulations.
    plan_regulation_group = relationship(
        "PlanRegulationGroup", backref="plans", lazy="joined"
    )
    plan_type_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("codes.plan_type.id", name="plan_type_id_fkey")
    )
    # Let's load all the codes for objects joined.
    plan_type = relationship("PlanType", backref="plans", lazy="joined")

    permanent_plan_identifier: Mapped[Optional[str]]
    producers_plan_identifier: Mapped[Optional[str]]
    description: Mapped[language_str]
    scale: Mapped[Optional[int]]
    matter_management_identifier: Mapped[Optional[str]]
    record_number: Mapped[Optional[str]]
    geom: Mapped[MultiPolygon]
    # Only plan should have validated_at field, since validation is only done
    # for complete plan objects. Also validation errors might concern multiple
    # models, not just one field or one table in database.
    validated_at: Mapped[Optional[datetime]]
    validation_errors: Mapped[Optional[dict[str, str]]]
    to_be_exported: Mapped[bool] = mapped_column(server_default="f")


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

    # Let's add backreference to allow lazy loading from this side.
    plan_regulations: Mapped[List["PlanRegulation"]] = relationship(
        "PlanRegulation",
        back_populates="plan_regulation_group",
        lazy="joined",
        order_by="PlanRegulation.ordering",  # list regulations in right order
    )

    # Let's add backreference to allow lazy loading from this side. Unit tests
    # will not detect missing joined loads, because currently fixtures are created
    # and added in the same database session that is passed on to the unit tests
    # for running. Therefore, any related objects returned by the session may be
    # lazy loaded, because they are already added to the existing session.
    # But why don't integration tests catch this missing, they contain propositions too?
    # Maybe has something to do with the lifecycle of pytest session fixture?
    plan_propositions: Mapped[List["PlanProposition"]] = relationship(
        "PlanProposition",
        back_populates="plan_regulation_group",
        lazy="joined",
        order_by="PlanProposition.ordering",  # list propositions in right order
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
    plan_theme_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("codes.plan_theme.id", name="plan_theme_id_fkey")
    )
    plan_regulation_group: Mapped[PlanRegulationGroup] = relationship(
        "PlanRegulationGroup", back_populates="plan_regulations"
    )
    # Let's load all the codes for objects joined.
    type_of_plan_regulation = relationship(
        "TypeOfPlanRegulation", backref="plan_regulations", lazy="joined"
    )
    # Let's load all the codes for objects joined.
    type_of_verbal_plan_regulation = relationship(
        "TypeOfVerbalPlanRegulation", backref="plan_regulations", lazy="joined"
    )
    # Let's load all the codes for objects joined.
    plan_theme = relationship("PlanTheme", backref="plan_regulations", lazy="joined")

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
    # Let's load all the codes for objects joined.
    intended_use = relationship(
        "TypeOfAdditionalInformation",
        foreign_keys=[intended_use_id],
        backref="intended_use_plan_regulations",
        lazy="joined",
    )
    existence = relationship(
        "TypeOfAdditionalInformation",
        foreign_keys=[existence_id],
        backref="existence_plan_regulations",
        lazy="joined",
    )
    regulation_type_additional_information = relationship(
        "TypeOfAdditionalInformation",
        foreign_keys=[regulation_type_additional_information_id],
        backref="type_plan_regulations",
        lazy="joined",
    )
    significance = relationship(
        "TypeOfAdditionalInformation",
        foreign_keys=[significance_id],
        backref="significance_plan_regulations",
        lazy="joined",
    )
    reservation = relationship(
        "TypeOfAdditionalInformation",
        foreign_keys=[reservation_id],
        backref="reservation_plan_regulations",
        lazy="joined",
    )
    development = relationship(
        "TypeOfAdditionalInformation",
        foreign_keys=[development_id],
        backref="development_plan_regulations",
        lazy="joined",
    )
    disturbance_prevention = relationship(
        "TypeOfAdditionalInformation",
        foreign_keys=[disturbance_prevention_id],
        backref="disturbance_prevention_plan_regulations",
        lazy="joined",
    )
    construction_control = relationship(
        "TypeOfAdditionalInformation",
        foreign_keys=[construction_control_id],
        backref="construction_control_plan_regulations",
        lazy="joined",
    )

    numeric_range: Mapped[numeric_range]
    unit: Mapped[str] = mapped_column(nullable=True)
    text_value: Mapped[language_str]
    numeric_value: Mapped[float] = mapped_column(nullable=True)
    ordering: Mapped[Optional[int]] = mapped_column(index=True)


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
    plan_theme_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("codes.plan_theme.id", name="plan_theme_id_fkey")
    )

    plan_regulation_group = relationship(
        "PlanRegulationGroup", back_populates="plan_propositions"
    )
    # Let's load all the codes for objects joined.
    plan_theme = relationship("PlanTheme", backref="plan_propositions", lazy="joined")
    text_value: Mapped[language_str]
    ordering: Mapped[Optional[int]] = mapped_column(index=True)


class SourceData(VersionedBase):
    """
    Lähtötietoaineistot
    """

    __tablename__ = "source_data"

    type_of_source_data_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("codes.type_of_source_data.id", name="type_of_source_data_id_fkey")
    )
    plan_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("hame.plan.id", name="plan_id_fkey")
    )

    # Let's load all the codes for objects joined.
    type_of_source_data = relationship(
        "TypeOfSourceData", backref="source_data", lazy="joined"
    )
    plan = relationship("Plan", backref="source_data")
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
    # Let's load all the codes for objects joined.
    administrative_region = relationship(
        "AdministrativeRegion", backref="organisations", lazy="joined"
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

    # Let's load all the codes for objects joined.
    type_of_document = relationship(
        "TypeOfDocument", backref="documents", lazy="joined"
    )
    plan = relationship("Plan", backref="documents")
    permanent_document_identifier: Mapped[Optional[uuid.UUID]]
    name: Mapped[str]
    personal_details: Mapped[str]
    publicity: Mapped[Literal["julkinen", "ei julkinen"]]  # Muita?
    language: Mapped[str]
    decision: Mapped[bool]
    decision_date: Mapped[Optional[timestamp]]
    # file


class LifeCycleDate(VersionedBase):
    """
    Elinkaaritilan päivämäärät
    """

    __tablename__ = "lifecycle_date"

    lifecycle_status_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("codes.lifecycle_status.id", name="plan_lifecycle_status_id_fkey"),
        index=True,
    )
    plan_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("hame.plan.id", name="plan_id_fkey")
    )
    land_use_area_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("hame.land_use_area.id", name="land_use_area_id_fkey")
    )
    other_area_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("hame.other_area.id", name="other_area_id_fkey")
    )
    line_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("hame.line.id", name="line_id_fkey")
    )
    land_use_point_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("hame.land_use_point.id", name="land_use_point_id_fkey")
    )
    other_point_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("hame.other_point.id", name="other_point_id_fkey")
    )
    plan_regulation_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("hame.plan_regulation.id", name="plan_regulation_id_fkey")
    )
    plan_proposition_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("hame.plan_proposition.id", name="plan_proposition_id_fkey")
    )

    plan: Mapped[Optional["Plan"]] = relationship(back_populates="lifecycle_dates")
    land_use_area: Mapped[Optional[LandUseArea]] = relationship(
        back_populates="lifecycle_dates"
    )
    other_area: Mapped[Optional[OtherArea]] = relationship(
        back_populates="lifecycle_dates"
    )
    line: Mapped[Optional[Line]] = relationship(back_populates="lifecycle_dates")
    land_use_point: Mapped[Optional[LandUsePoint]] = relationship(
        back_populates="lifecycle_dates"
    )
    other_point: Mapped[Optional[OtherPoint]] = relationship(
        back_populates="lifecycle_dates"
    )
    plan_regulation: Mapped[Optional["PlanRegulation"]] = relationship(
        back_populates="lifecycle_dates"
    )
    plan_proposition: Mapped[Optional["PlanProposition"]] = relationship(
        back_populates="lifecycle_dates"
    )
    # Let's load all the codes for objects joined.
    lifecycle_status = relationship(
        "LifeCycleStatus", backref="lifecycle_dates", lazy="joined"
    )
    starting_at: Mapped[Optional[datetime]]
    ending_at: Mapped[Optional[datetime]]
