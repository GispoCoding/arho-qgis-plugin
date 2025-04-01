import uuid
from datetime import datetime
from typing import List, Optional

from shapely.geometry import MultiLineString, MultiPoint, MultiPolygon
from sqlalchemy import Column, ForeignKey, Index, Table, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

# we have to import CodeBase in codes.py from here to allow two-way relationships
from database.base import (  # noqa
    AttributeValueMixin,
    Base,
    CodeBase,
    PlanBase,
    PlanObjectBase,
    VersionedBase,
    language_str,
    timestamp,
)

regulation_group_association = Table(
    "regulation_group_association",
    Base.metadata,
    Column("id", Uuid, primary_key=True, server_default=func.gen_random_uuid()),
    Column(
        "plan_regulation_group_id",
        ForeignKey(
            "hame.plan_regulation_group.id",
            name="plan_regulation_group_id_fkey",
            ondelete="CASCADE",
        ),
        index=True,
    ),
    # General groups cannot actually be n2n but use this approach anyway
    # to make the approach uniform with the plan objects
    Column(
        "plan_id",
        ForeignKey(
            "hame.plan.id",
            name="plan_id_fkey",
            ondelete="CASCADE",
        ),
        index=True,
        comment="A plan in which the regulation group is a general regulation group",
    ),
    Column(
        "land_use_area_id",
        ForeignKey(
            "hame.land_use_area.id",
            name="land_use_area_id_fkey",
            ondelete="CASCADE",
        ),
        index=True,
    ),
    Column(
        "other_area_id",
        ForeignKey(
            "hame.other_area.id",
            name="other_area_id_fkey",
            ondelete="CASCADE",
        ),
        index=True,
    ),
    Column(
        "land_use_point_id",
        ForeignKey(
            "hame.land_use_point.id",
            name="land_use_point_id_fkey",
            ondelete="CASCADE",
        ),
        index=True,
    ),
    Column(
        "line_id",
        ForeignKey(
            "hame.line.id",
            name="line_id_fkey",
            ondelete="CASCADE",
        ),
        index=True,
    ),
    Column(
        "other_point_id",
        ForeignKey(
            "hame.other_point.id",
            name="other_point_id_fkey",
            ondelete="CASCADE",
        ),
        index=True,
    ),
    schema="hame",
)


legal_effects_association = Table(
    "legal_effects_association",
    Base.metadata,
    Column(
        "plan_id",
        ForeignKey("hame.plan.id", name="plan_id_fkey", ondelete="CASCADE"),
        primary_key=True,
        # indexed by the primary key
    ),
    Column(
        "legal_effects_of_master_plan_id",
        ForeignKey(
            "codes.legal_effects_of_master_plan.id",
            name="legal_effects_of_master_plan_id_fkey",
            ondelete="CASCADE",
        ),
        primary_key=True,
        # use separate index because not the leftmost column of the primary key
        index=True,
    ),
    schema="hame",
)


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

    plan_type_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("codes.plan_type.id", name="plan_type_id_fkey")
    )
    # Let's load all the codes for objects joined.
    plan_type = relationship("PlanType", backref="plans", lazy="joined")
    # Also join plan documents
    documents = relationship(
        "Document", back_populates="plan", lazy="joined", cascade="delete"
    )
    # Load plan objects ordered
    land_use_areas = relationship(
        "LandUseArea", order_by="LandUseArea.ordering", back_populates="plan"
    )
    other_areas = relationship(
        "OtherArea", order_by="OtherArea.ordering", back_populates="plan"
    )
    lines = relationship("Line", order_by="Line.ordering", back_populates="plan")
    land_use_points = relationship(
        "LandUsePoint", order_by="LandUsePoint.ordering", back_populates="plan"
    )
    other_points = relationship(
        "OtherPoint", order_by="OtherPoint.ordering", back_populates="plan"
    )

    permanent_plan_identifier: Mapped[Optional[str]]
    producers_plan_identifier: Mapped[Optional[str]]
    name: Mapped[Optional[language_str]]
    description: Mapped[Optional[language_str]]
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

    general_plan_regulation_groups: Mapped[List["PlanRegulationGroup"]] = relationship(
        secondary=regulation_group_association,
        lazy="joined",
        overlaps=(
            "general_plan_regulation_groups,land_use_areas,other_areas,"
            "land_use_points,lines,plan_regulation_groups"
        ),
    )
    legal_effects_of_master_plan = relationship(
        "LegalEffectsOfMasterPlan",
        secondary=legal_effects_association,
        lazy="joined",
        backref="plans",
    )


class LandUseArea(PlanObjectBase):
    """
    Aluevaraus
    """

    __tablename__ = "land_use_area"

    geom: Mapped[MultiPolygon]


class OtherArea(PlanObjectBase):
    """
    Osa-alue
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
    __table_args__ = (
        Index("ix_plan_regulation_group_plan_id_ordering", "plan_id", "ordering"),
        Index(
            "ix_plan_regulation_group_plan_id_short_name",
            "plan_id",
            "short_name",
            unique=True,
        ),
        VersionedBase.__table_args__,
    )

    short_name: Mapped[Optional[str]]
    name: Mapped[Optional[language_str]]

    plan_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(
            "hame.plan.id",
            name="plan_id_fkey",
            ondelete="CASCADE",
        ),
        nullable=False,
        comment="Plan to which this regulation group belongs",
        index=True,
    )
    plan: Mapped["Plan"] = relationship()

    ordering: Mapped[Optional[int]]

    # värikoodi?
    type_of_plan_regulation_group_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(
            "codes.type_of_plan_regulation_group.id",
            name="type_of_plan_regulation_group_id_fkey",
        )
    )
    type_of_plan_regulation_group = relationship(
        "TypeOfPlanRegulationGroup", backref="plan_regulation_groups", lazy="joined"
    )

    # Let's add backreference to allow lazy loading from this side.
    plan_regulations: Mapped[List["PlanRegulation"]] = relationship(
        "PlanRegulation",
        back_populates="plan_regulation_group",
        lazy="joined",
        order_by="PlanRegulation.ordering",  # list regulations in right order
        cascade="all, delete-orphan",
        passive_deletes=True,
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
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    land_use_areas: Mapped[List["LandUseArea"]] = relationship(
        secondary="hame.regulation_group_association",
        back_populates="plan_regulation_groups",
        overlaps=(
            "general_plan_regulation_groups,land_use_areas,other_areas,"
            "land_use_points,lines,plan_regulation_groups"
        ),
    )
    other_areas: Mapped[List["OtherArea"]] = relationship(
        secondary="hame.regulation_group_association",
        back_populates="plan_regulation_groups",
        overlaps=(
            "general_plan_regulation_groups,land_use_areas,other_areas,"
            "land_use_points,lines,plan_regulation_groups"
        ),
    )
    lines: Mapped[List["Line"]] = relationship(
        secondary="hame.regulation_group_association",
        back_populates="plan_regulation_groups",
        overlaps=(
            "general_plan_regulation_groups,land_use_areas,other_areas,"
            "land_use_points,lines,plan_regulation_groups"
        ),
    )
    land_use_points: Mapped[List["LandUsePoint"]] = relationship(
        secondary="hame.regulation_group_association",
        back_populates="plan_regulation_groups",
        overlaps=(
            "general_plan_regulation_groups,land_use_areas,other_areas,"
            "land_use_points,lines,plan_regulation_groups"
        ),
    )
    other_points: Mapped[List["OtherPoint"]] = relationship(
        secondary="hame.regulation_group_association",
        back_populates="plan_regulation_groups",
        overlaps=(
            "general_plan_regulation_groups,land_use_areas,other_areas,"
            "land_use_points,lines,plan_regulation_groups"
        ),
    )


class AdditionalInformation(VersionedBase, AttributeValueMixin):
    """Kaavamääräyksen lisätieto"""

    __tablename__ = "additional_information"

    plan_regulation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(
            "hame.plan_regulation.id",
            name="plan_regulation_id_fkey",
            ondelete="CASCADE",
        ),
        index=True,
    )
    type_additional_information_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(
            "codes.type_of_additional_information.id",
            name="type_additional_information_id_fkey",
        ),
        index=True,
    )

    plan_regulation: Mapped["PlanRegulation"] = relationship(
        "PlanRegulation", back_populates="additional_information"
    )
    type_of_additional_information = relationship(
        "TypeOfAdditionalInformation", lazy="joined"
    )


type_of_verbal_regulation_association = Table(
    "type_of_verbal_regulation_association",
    Base.metadata,
    Column(
        "plan_regulation_id",
        ForeignKey(
            "hame.plan_regulation.id",
            name="plan_regulation_id_fkey",
            ondelete="CASCADE",
        ),
        primary_key=True,
    ),
    Column(
        "type_of_verbal_plan_regulation_id",
        ForeignKey(
            "codes.type_of_verbal_plan_regulation.id",
            name="type_of_verbal_plan_regulation_id_fkey",
            ondelete="CASCADE",
        ),
        primary_key=True,
        index=True,
    ),
    schema="hame",
)


class PlanRegulation(PlanBase, AttributeValueMixin):
    """
    Kaavamääräys
    """

    __tablename__ = "plan_regulation"
    __table_args__ = (
        Index(
            "ix_plan_regulation_plan_regulation_group_id_ordering",
            "plan_regulation_group_id",
            "ordering",
            unique=True,
        ),
        PlanBase.__table_args__,
    )

    plan_regulation_group_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(
            "hame.plan_regulation_group.id",
            name="plan_regulation_group_id_fkey",
            ondelete="CASCADE",
        )
    )

    type_of_plan_regulation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(
            "codes.type_of_plan_regulation.id", name="type_of_plan_regulation_id_fkey"
        )
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
    types_of_verbal_plan_regulations = relationship(
        "TypeOfVerbalPlanRegulation",
        secondary=type_of_verbal_regulation_association,
        backref="plan_regulations",
        lazy="joined",
    )
    # Let's load all the codes for objects joined.
    plan_theme = relationship("PlanTheme", backref="plan_regulations", lazy="joined")

    additional_information: Mapped[list[AdditionalInformation]] = relationship(
        "AdditionalInformation",
        back_populates="plan_regulation",
        lazy="joined",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    ordering: Mapped[Optional[int]]
    subject_identifiers: Mapped[Optional[List[str]]]


class PlanProposition(PlanBase):
    """
    Kaavasuositus
    """

    __tablename__ = "plan_proposition"
    __table_args__ = (
        Index(
            "ix_plan_proposition_plan_regulation_group_id_ordering",
            "plan_regulation_group_id",
            "ordering",
            unique=True,
        ),
        PlanBase.__table_args__,
    )

    plan_regulation_group_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(
            "hame.plan_regulation_group.id",
            name="plan_regulation_group_id_fkey",
            ondelete="CASCADE",
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
    text_value: Mapped[Optional[language_str]]
    ordering: Mapped[Optional[int]]


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
    name: Mapped[Optional[language_str]]
    additional_information_uri: Mapped[str]
    detachment_date: Mapped[datetime]


class Organisation(VersionedBase):
    """
    Toimija
    """

    __tablename__ = "organisation"

    name: Mapped[Optional[language_str]]
    business_id: Mapped[str]
    municipality_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("codes.municipality.id", name="municipality_id_fkey")
    )
    administrative_region_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(
            "codes.administrative_region.id", name="administrative_region_id_fkey"
        )
    )
    # Let's load all the codes for objects joined.
    municipality = relationship("Municipality", backref="organisations", lazy="joined")
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
        ForeignKey("hame.plan.id", name="plan_id_fkey", ondelete="CASCADE")
    )
    category_of_publicity_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(
            "codes.category_of_publicity.id", name="category_of_publicity_id_fkey"
        )
    )
    personal_data_content_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(
            "codes.personal_data_content.id", name="personal_data_content_id_fkey"
        )
    )
    retention_time_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("codes.retention_time.id", name="retention_time_id_fkey")
    )
    language_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("codes.language.id", name="language_id_fkey")
    )

    # Let's load all the codes for objects joined.
    type_of_document = relationship(
        "TypeOfDocument", backref="documents", lazy="joined"
    )
    plan = relationship("Plan", back_populates="documents")
    category_of_publicity = relationship(
        "CategoryOfPublicity", backref="documents", lazy="joined"
    )
    personal_data_content = relationship(
        "PersonalDataContent", backref="documents", lazy="joined"
    )
    retention_time = relationship("RetentionTime", backref="documents", lazy="joined")
    language = relationship("Language", backref="documents", lazy="joined")

    permanent_document_identifier: Mapped[Optional[str]]  # e.g. diaarinumero
    name: Mapped[Optional[language_str]]
    exported_at: Mapped[Optional[datetime]]
    # Ryhti key for the latest file version that was uploaded:
    exported_file_key: Mapped[Optional[uuid.UUID]]
    arrival_date: Mapped[Optional[datetime]]
    confirmation_date: Mapped[Optional[datetime]]
    accessibility: Mapped[bool] = mapped_column(default=False, server_default="0")
    decision_date: Mapped[Optional[datetime]]
    document_date: Mapped[datetime]
    url: Mapped[Optional[str]]


class LifeCycleDate(VersionedBase):
    """
    Elinkaaritilan päivämäärät
    """

    __tablename__ = "lifecycle_date"

    lifecycle_status_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(
            "codes.lifecycle_status.id",
            name="plan_lifecycle_status_id_fkey",
        ),
        index=True,
    )
    plan_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("hame.plan.id", name="plan_id_fkey", ondelete="CASCADE")
    )
    land_use_area_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey(
            "hame.land_use_area.id", name="land_use_area_id_fkey", ondelete="CASCADE"
        )
    )
    other_area_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("hame.other_area.id", name="other_area_id_fkey", ondelete="CASCADE")
    )
    line_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("hame.line.id", name="line_id_fkey", ondelete="CASCADE")
    )
    land_use_point_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey(
            "hame.land_use_point.id", name="land_use_point_id_fkey", ondelete="CASCADE"
        )
    )
    other_point_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey(
            "hame.other_point.id", name="other_point_id_fkey", ondelete="CASCADE"
        )
    )
    plan_regulation_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey(
            "hame.plan_regulation.id",
            name="plan_regulation_id_fkey",
            ondelete="CASCADE",
        )
    )
    plan_proposition_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey(
            "hame.plan_proposition.id",
            name="plan_proposition_id_fkey",
            ondelete="CASCADE",
        )
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
        "LifeCycleStatus", back_populates="lifecycle_dates", lazy="joined"
    )
    # Let's add backreference to allow lazy loading from this side.
    event_dates = relationship(
        "EventDate",
        back_populates="lifecycle_date",
        lazy="joined",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    starting_at: Mapped[datetime]
    ending_at: Mapped[Optional[datetime]]


class EventDate(VersionedBase):
    """
    Tapahtuman päivämäärät

    Jokaisessa elinkaaritilassa voi olla tiettyjä tapahtumia. Liitetään tapahtuma
    sille sallittuun elinkaaritilaan. Tapahtuman päivämäärien tulee olla aina
    elinkaaritilan päivämäärien välissä.
    """

    __tablename__ = "event_date"

    lifecycle_date_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(
            "hame.lifecycle_date.id",
            name="lifecycle_date_id_fkey",
            ondelete="CASCADE",
        ),
        index=True,
    )
    decision_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey(
            "codes.name_of_plan_case_decision.id",
            name="name_of_plan_case_decision_id_fkey",
        )
    )
    processing_event_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey(
            "codes.type_of_processing_event.id", name="type_of_processing_event_fkey"
        )
    )
    interaction_event_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey(
            "codes.type_of_interaction_event.id", name="type_of_interaction_event_fkey"
        )
    )

    # Let's load all the codes for objects joined.
    lifecycle_date = relationship(
        "LifeCycleDate", back_populates="event_dates", lazy="joined"
    )
    decision = relationship(
        "NameOfPlanCaseDecision", backref="event_dates", lazy="joined"
    )
    processing_event = relationship(
        "TypeOfProcessingEvent", backref="event_dates", lazy="joined"
    )
    interaction_event = relationship(
        "TypeOfInteractionEvent", backref="event_dates", lazy="joined"
    )

    starting_at: Mapped[datetime]
    ending_at: Mapped[Optional[datetime]]
