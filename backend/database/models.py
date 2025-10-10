from __future__ import annotations

from datetime import datetime  # Sqlalchemy uses this runtime
from typing import TYPE_CHECKING, Any
from uuid import UUID  # Sqlalchemy uses this runtime

from geoalchemy2 import Geometry, WKBElement
from sqlalchemy import Column, ForeignKey, Index, Table, Uuid
from sqlalchemy.orm import Mapped, declared_attr, mapped_column, relationship
from sqlalchemy.sql import func

from database.base import (
    PROJECT_SRID,
    AttributeValueMixin,
    Base,
    VersionedBase,
    language_str,
)

if TYPE_CHECKING:
    from database.codes import (
        AdministrativeRegion,
        CategoryOfPublicity,
        Language,
        LegalEffectsOfMasterPlan,
        LifeCycleStatus,
        Municipality,
        NameOfPlanCaseDecision,
        PersonalDataContent,
        PlanTheme,
        PlanType,
        RetentionTime,
        TypeOfAdditionalInformation,
        TypeOfDocument,
        TypeOfInteractionEvent,
        TypeOfPlanRegulation,
        TypeOfPlanRegulationGroup,
        TypeOfProcessingEvent,
        TypeOfSourceData,
        TypeOfUnderground,
        TypeOfVerbalPlanRegulation,
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
        ForeignKey("hame.plan.id", name="plan_id_fkey", ondelete="CASCADE"),
        index=True,
        comment="A plan in which the regulation group is a general regulation group",
    ),
    Column(
        "land_use_area_id",
        ForeignKey(
            "hame.land_use_area.id", name="land_use_area_id_fkey", ondelete="CASCADE"
        ),
        index=True,
    ),
    Column(
        "other_area_id",
        ForeignKey("hame.other_area.id", name="other_area_id_fkey", ondelete="CASCADE"),
        index=True,
    ),
    Column(
        "line_id",
        ForeignKey("hame.line.id", name="line_id_fkey", ondelete="CASCADE"),
        index=True,
    ),
    Column(
        "point_id",
        ForeignKey("hame.point.id", name="point_id_fkey", ondelete="CASCADE"),
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


plan_theme_association = Table(
    "plan_theme_association",
    Base.metadata,
    Column("id", Uuid, primary_key=True, server_default=func.gen_random_uuid()),
    Column(
        "plan_regulation_id",
        ForeignKey(
            "hame.plan_regulation.id",
            name="plan_regulation_id_fkey",
            ondelete="CASCADE",
        ),
        index=True,
    ),
    Column(
        "plan_proposition_id",
        ForeignKey(
            "hame.plan_proposition.id",
            name="plan_proposition_id_fkey",
            ondelete="CASCADE",
        ),
        index=True,
    ),
    Column(
        "plan_theme_id",
        ForeignKey(
            "codes.plan_theme.id", name="plan_theme_id_fkey", ondelete="CASCADE"
        ),
        index=True,
        nullable=False,
    ),
    schema="hame",
)


class PlanBase(VersionedBase):
    """All plan data tables should have additional date fields."""

    __abstract__ = True

    # Let's have exported at field for all plan data, because some of them may be
    # exported and others added after the plan has last been exported? This will
    # require finding all the exported objects in the database after export is done,
    # is it worth the trouble?
    exported_at: Mapped[datetime | None]

    lifecycle_status_id: Mapped[UUID] = mapped_column(
        ForeignKey("codes.lifecycle_status.id", name="plan_lifecycle_status_id_fkey"),
        index=True,
    )

    # class reference in abstract base class, with backreference to class name:
    @declared_attr
    @classmethod
    def lifecycle_status(cls) -> Mapped[LifeCycleStatus]:
        return relationship(
            "LifeCycleStatus", back_populates=f"{cls.__tablename__}s", lazy="joined"
        )

    # Let's add backreference to allow lazy loading from this side.
    @declared_attr
    @classmethod
    def lifecycle_dates(cls) -> Mapped[list[LifeCycleDate]]:
        return relationship(
            "LifeCycleDate",
            back_populates=f"{cls.__tablename__}",
            lazy="joined",
            cascade="all, delete-orphan",
            passive_deletes=True,
            order_by="LifeCycleDate.starting_at",
        )


class Plan(PlanBase):
    """Maakuntakaava, compatible with Ryhti 2.0 specification"""

    __tablename__ = "plan"

    organisation_id: Mapped[UUID] = mapped_column(
        ForeignKey("hame.organisation.id", name="organisation_id_fkey")
    )
    organisation: Mapped[Organisation] = relationship(
        back_populates="plans", lazy="joined"
    )

    plan_type_id: Mapped[UUID] = mapped_column(
        ForeignKey("codes.plan_type.id", name="plan_type_id_fkey")
    )
    # Let's load all the codes for objects joined.
    plan_type: Mapped[PlanType] = relationship(back_populates="plans", lazy="joined")
    # Also join plan documents
    documents: Mapped[list[Document]] = relationship(
        back_populates="plan", lazy="joined", cascade="all, delete-orphan"
    )
    # Load plan objects ordered
    land_use_areas: Mapped[list[LandUseArea]] = relationship(
        order_by="LandUseArea.ordering",
        back_populates="plan",
        cascade="all, delete-orphan",
    )
    other_areas: Mapped[list[OtherArea]] = relationship(
        order_by="OtherArea.ordering",
        back_populates="plan",
        cascade="all, delete-orphan",
    )
    lines: Mapped[list[Line]] = relationship(
        order_by="Line.ordering", back_populates="plan", cascade="all, delete-orphan"
    )
    points: Mapped[list[Point]] = relationship(
        order_by="Point.ordering", back_populates="plan", cascade="all, delete-orphan"
    )

    permanent_plan_identifier: Mapped[str | None]
    producers_plan_identifier: Mapped[str | None]
    name: Mapped[language_str]
    description: Mapped[language_str | None]
    scale: Mapped[int | None]
    matter_management_identifier: Mapped[str | None]
    record_number: Mapped[str | None]
    geom: Mapped[WKBElement] = mapped_column(
        type_=Geometry(geometry_type="MULTIPOLYGON", srid=PROJECT_SRID)
    )
    # Only plan should have validated_at field, since validation is only done
    # for complete plan objects. Also validation errors might concern multiple
    # models, not just one field or one table in database.
    validated_at: Mapped[datetime | None]
    validation_errors: Mapped[dict[str, Any] | str | None]

    # Regulation groups belonging to a plan
    regulation_groups: Mapped[list[PlanRegulationGroup]] = relationship(
        back_populates="plan", cascade="all, delete-orphan"
    )

    general_plan_regulation_groups: Mapped[list[PlanRegulationGroup]] = relationship(
        secondary=regulation_group_association,
        lazy="joined",
        overlaps=(
            "general_plan_regulation_groups,land_use_areas,other_areas,"
            "points,lines,plan_regulation_groups"
        ),
    )
    legal_effects_of_master_plan: Mapped[list[LegalEffectsOfMasterPlan]] = relationship(
        "LegalEffectsOfMasterPlan",
        secondary=legal_effects_association,
        lazy="joined",
        back_populates="plans",
    )

    source_data: Mapped[list[SourceData]] = relationship(
        back_populates="plan", cascade="all, delete-orphan"
    )


class PlanObjectBase(PlanBase):
    """All plan object tables have the same fields, apart from geometry."""

    __abstract__ = True

    @declared_attr.directive
    @classmethod
    def __table_args__(cls) -> tuple:
        return (
            Index(
                f"ix_{cls.__tablename__}_plan_id_ordering",
                "plan_id",
                "ordering",
                unique=True,
            ),
            PlanBase.__table_args__,
        )

    name: Mapped[language_str | None]
    description: Mapped[language_str | None]
    source_data_object: Mapped[str | None]
    height_min: Mapped[float | None]
    height_max: Mapped[float | None]
    height_unit: Mapped[str | None]
    height_reference_point: Mapped[str | None]
    ordering: Mapped[int | None]
    type_of_underground_id: Mapped[UUID] = mapped_column(
        ForeignKey("codes.type_of_underground.id", name="type_of_underground_id_fkey"),
        index=True,
    )
    plan_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("hame.plan.id", name="plan_id_fkey"), index=True
    )

    # Annotate the geom here and define columns in subclasses.
    geom: Mapped[WKBElement]

    # class reference in abstract base class, with backreference to class name
    # Let's load all the codes for objects joined.
    @declared_attr
    @classmethod
    def type_of_underground(cls) -> Mapped[TypeOfUnderground]:
        return relationship(
            "TypeOfUnderground", back_populates=f"{cls.__tablename__}s", lazy="joined"
        )

    # class reference in abstract base class, with backreference to class name:
    @declared_attr
    @classmethod
    def plan(cls) -> Mapped[Plan]:
        return relationship("Plan", back_populates=f"{cls.__tablename__}s")

    # class reference in abstract base class, with backreference to class name:
    @declared_attr
    @classmethod
    def plan_regulation_groups(cls) -> Mapped[list[PlanRegulationGroup]]:
        return relationship(
            "PlanRegulationGroup",
            secondary="hame.regulation_group_association",
            back_populates=f"{cls.__tablename__}s",
            overlaps=(
                "general_plan_regulation_groups,land_use_areas,other_areas,"
                "points,lines,plan_regulation_groups"
            ),
            lazy="joined",
        )


class LandUseArea(PlanObjectBase):
    """Aluevaraus"""

    __tablename__ = "land_use_area"

    geom: Mapped[WKBElement] = mapped_column(
        type_=Geometry(geometry_type="MULTIPOLYGON", srid=PROJECT_SRID)
    )


class OtherArea(PlanObjectBase):
    """Osa-alue"""

    __tablename__ = "other_area"

    geom: Mapped[WKBElement] = mapped_column(
        type_=Geometry(geometry_type="MULTIPOLYGON", srid=PROJECT_SRID)
    )


class Line(PlanObjectBase):
    """Viivat"""

    __tablename__ = "line"

    geom: Mapped[WKBElement] = mapped_column(
        type_=Geometry(geometry_type="MULTILINESTRING", srid=PROJECT_SRID)
    )


class Point(PlanObjectBase):
    """Pisteet"""

    __tablename__ = "point"

    geom: Mapped[WKBElement] = mapped_column(
        type_=Geometry(geometry_type="MULTIPOINT", srid=PROJECT_SRID)
    )


class PlanRegulationGroup(VersionedBase):
    """Kaavamääräysryhmä"""

    __tablename__ = "plan_regulation_group"
    __table_args__ = (
        Index("ix_plan_regulation_group_plan_id_ordering", "plan_id", "ordering"),
        Index("ix_plan_regulation_group_plan_id_short_name", "plan_id", "short_name"),
        VersionedBase.__table_args__,
    )

    short_name: Mapped[str | None]
    name: Mapped[language_str | None]

    plan_id: Mapped[UUID] = mapped_column(
        ForeignKey("hame.plan.id", name="plan_id_fkey", ondelete="CASCADE"),
        nullable=False,
        comment="Plan to which this regulation group belongs",
        index=True,
    )
    plan: Mapped[Plan] = relationship(back_populates="regulation_groups")

    ordering: Mapped[int | None]

    # värikoodi?
    type_of_plan_regulation_group_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "codes.type_of_plan_regulation_group.id",
            name="type_of_plan_regulation_group_id_fkey",
        )
    )
    type_of_plan_regulation_group: Mapped[TypeOfPlanRegulationGroup] = relationship(
        back_populates="plan_regulation_groups", lazy="joined"
    )

    # Let's add backreference to allow lazy loading from this side.
    plan_regulations: Mapped[list[PlanRegulation]] = relationship(
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
    plan_propositions: Mapped[list[PlanProposition]] = relationship(
        back_populates="plan_regulation_group",
        lazy="joined",
        order_by="PlanProposition.ordering",  # list propositions in right order
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    land_use_areas: Mapped[list[LandUseArea]] = relationship(
        secondary="hame.regulation_group_association",
        back_populates="plan_regulation_groups",
        overlaps=(
            "general_plan_regulation_groups,land_use_areas,other_areas,"
            "points,lines,plan_regulation_groups"
        ),
    )
    other_areas: Mapped[list[OtherArea]] = relationship(
        secondary="hame.regulation_group_association",
        back_populates="plan_regulation_groups",
        overlaps=(
            "general_plan_regulation_groups,land_use_areas,other_areas,"
            "points,lines,plan_regulation_groups"
        ),
    )
    lines: Mapped[list[Line]] = relationship(
        secondary="hame.regulation_group_association",
        back_populates="plan_regulation_groups",
        overlaps=(
            "general_plan_regulation_groups,land_use_areas,other_areas,"
            "points,lines,plan_regulation_groups"
        ),
    )
    points: Mapped[list[Point]] = relationship(
        secondary="hame.regulation_group_association",
        back_populates="plan_regulation_groups",
        overlaps=(
            "general_plan_regulation_groups,land_use_areas,other_areas,"
            "points,lines,plan_regulation_groups"
        ),
    )


class AdditionalInformation(VersionedBase, AttributeValueMixin):
    """Kaavamääräyksen lisätieto"""

    __tablename__ = "additional_information"

    plan_regulation_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "hame.plan_regulation.id",
            name="plan_regulation_id_fkey",
            ondelete="CASCADE",
        ),
        index=True,
    )
    type_additional_information_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "codes.type_of_additional_information.id",
            name="type_additional_information_id_fkey",
        ),
        index=True,
    )

    plan_regulation: Mapped[PlanRegulation] = relationship(
        back_populates="additional_information"
    )
    type_of_additional_information: Mapped[TypeOfAdditionalInformation] = relationship(
        lazy="joined"
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
    """Kaavamääräys"""

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

    plan_regulation_group_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "hame.plan_regulation_group.id",
            name="plan_regulation_group_id_fkey",
            ondelete="CASCADE",
        ),
        index=True,
    )

    type_of_plan_regulation_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "codes.type_of_plan_regulation.id", name="type_of_plan_regulation_id_fkey"
        )
    )

    plan_regulation_group: Mapped[PlanRegulationGroup] = relationship(
        back_populates="plan_regulations"
    )
    # Let's load all the codes for objects joined.
    type_of_plan_regulation: Mapped[TypeOfPlanRegulation] = relationship(
        back_populates="plan_regulations", lazy="joined"
    )
    # Let's load all the codes for objects joined.
    types_of_verbal_plan_regulations: Mapped[list[TypeOfVerbalPlanRegulation]] = (
        relationship(
            "TypeOfVerbalPlanRegulation",
            secondary=type_of_verbal_regulation_association,
            back_populates="plan_regulations",
            lazy="joined",
        )
    )
    plan_themes: Mapped[list[PlanTheme]] = relationship(
        secondary=plan_theme_association,
        overlaps="plan_propositions,plan_themes",
        back_populates="plan_regulations",
        lazy="joined",
    )

    additional_information: Mapped[list[AdditionalInformation]] = relationship(
        back_populates="plan_regulation",
        lazy="joined",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    ordering: Mapped[int | None]
    subject_identifiers: Mapped[list[str] | None]


class PlanProposition(PlanBase):
    """Kaavasuositus"""

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

    plan_regulation_group_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "hame.plan_regulation_group.id",
            name="plan_regulation_group_id_fkey",
            ondelete="CASCADE",
        ),
        index=True,
    )

    plan_regulation_group: Mapped[PlanRegulationGroup] = relationship(
        back_populates="plan_propositions"
    )
    # Let's load all the codes for objects joined.
    plan_themes: Mapped[list[PlanTheme]] = relationship(
        secondary=plan_theme_association,
        overlaps="plan_regulations,plan_themes",
        back_populates="plan_propositions",
        lazy="joined",
    )
    text_value: Mapped[language_str | None]
    ordering: Mapped[int | None]


class SourceData(VersionedBase):
    """Lähtötietoaineistot"""

    __tablename__ = "source_data"

    type_of_source_data_id: Mapped[UUID] = mapped_column(
        ForeignKey("codes.type_of_source_data.id", name="type_of_source_data_id_fkey")
    )
    plan_id: Mapped[UUID] = mapped_column(
        ForeignKey("hame.plan.id", name="plan_id_fkey"), index=True
    )

    # Let's load all the codes for objects joined.
    type_of_source_data: Mapped[TypeOfSourceData] = relationship(
        back_populates="source_data", lazy="joined"
    )
    plan: Mapped[Plan] = relationship(back_populates="source_data")
    name: Mapped[language_str | None]
    additional_information_uri: Mapped[str]
    detachment_date: Mapped[datetime]


class Organisation(VersionedBase):
    """Toimija"""

    __tablename__ = "organisation"

    name: Mapped[language_str | None]
    business_id: Mapped[str]
    municipality_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("codes.municipality.id", name="municipality_id_fkey")
    )
    administrative_region_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "codes.administrative_region.id", name="administrative_region_id_fkey"
        )
    )
    # Let's load all the codes for objects joined.
    municipality: Mapped[Municipality] = relationship(
        back_populates="organisations", lazy="joined"
    )
    administrative_region: Mapped[AdministrativeRegion] = relationship(
        back_populates="organisations", lazy="joined"
    )

    plans: Mapped[list[Plan]] = relationship(back_populates="organisation")


class Document(VersionedBase):
    """Asiakirja"""

    __tablename__ = "document"

    type_of_document_id: Mapped[UUID] = mapped_column(
        ForeignKey("codes.type_of_document.id", name="type_of_document_id_fkey")
    )
    plan_id: Mapped[UUID] = mapped_column(
        ForeignKey("hame.plan.id", name="plan_id_fkey", ondelete="CASCADE"), index=True
    )
    category_of_publicity_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "codes.category_of_publicity.id", name="category_of_publicity_id_fkey"
        )
    )
    personal_data_content_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "codes.personal_data_content.id", name="personal_data_content_id_fkey"
        )
    )
    retention_time_id: Mapped[UUID] = mapped_column(
        ForeignKey("codes.retention_time.id", name="retention_time_id_fkey")
    )
    language_id: Mapped[UUID] = mapped_column(
        ForeignKey("codes.language.id", name="language_id_fkey")
    )

    # Let's load all the codes for objects joined.
    type_of_document: Mapped[TypeOfDocument] = relationship(
        back_populates="documents", lazy="joined"
    )
    plan: Mapped[Plan] = relationship(back_populates="documents")
    category_of_publicity: Mapped[CategoryOfPublicity] = relationship(
        back_populates="documents", lazy="joined"
    )
    personal_data_content: Mapped[PersonalDataContent] = relationship(
        back_populates="documents", lazy="joined"
    )
    retention_time: Mapped[RetentionTime] = relationship(
        back_populates="documents", lazy="joined"
    )
    language: Mapped[Language] = relationship(back_populates="documents", lazy="joined")

    permanent_document_identifier: Mapped[str | None]  # e.g. diaarinumero
    name: Mapped[language_str | None]
    exported_at: Mapped[datetime | None]
    # Ryhti key for the latest file version that was uploaded:
    exported_file_key: Mapped[UUID | None]
    # Entity tag header for the latest file version that was uploaded:
    exported_file_etag: Mapped[str | None]
    arrival_date: Mapped[datetime | None]
    confirmation_date: Mapped[datetime | None]
    accessibility: Mapped[bool] = mapped_column(default=False, server_default="0")
    decision_date: Mapped[datetime | None]
    document_date: Mapped[datetime]
    url: Mapped[str | None]


class LifeCycleDate(VersionedBase):
    """Elinkaaritilan päivämäärät"""

    __tablename__ = "lifecycle_date"

    lifecycle_status_id: Mapped[UUID] = mapped_column(
        ForeignKey("codes.lifecycle_status.id", name="plan_lifecycle_status_id_fkey"),
        index=True,
    )
    plan_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("hame.plan.id", name="plan_id_fkey", ondelete="CASCADE"), index=True
    )
    land_use_area_id: Mapped[UUID | None] = mapped_column(
        ForeignKey(
            "hame.land_use_area.id", name="land_use_area_id_fkey", ondelete="CASCADE"
        ),
        index=True,
    )
    other_area_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("hame.other_area.id", name="other_area_id_fkey", ondelete="CASCADE"),
        index=True,
    )
    line_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("hame.line.id", name="line_id_fkey", ondelete="CASCADE"), index=True
    )
    point_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("hame.point.id", name="point_id_fkey", ondelete="CASCADE"),
        index=True,
    )
    plan_regulation_id: Mapped[UUID | None] = mapped_column(
        ForeignKey(
            "hame.plan_regulation.id",
            name="plan_regulation_id_fkey",
            ondelete="CASCADE",
        ),
        index=True,
    )
    plan_proposition_id: Mapped[UUID | None] = mapped_column(
        ForeignKey(
            "hame.plan_proposition.id",
            name="plan_proposition_id_fkey",
            ondelete="CASCADE",
        ),
        index=True,
    )

    plan: Mapped[Plan | None] = relationship(back_populates="lifecycle_dates")
    land_use_area: Mapped[LandUseArea | None] = relationship(
        back_populates="lifecycle_dates"
    )
    other_area: Mapped[OtherArea | None] = relationship(
        back_populates="lifecycle_dates"
    )
    line: Mapped[Line | None] = relationship(back_populates="lifecycle_dates")
    point: Mapped[Point | None] = relationship(back_populates="lifecycle_dates")
    plan_regulation: Mapped[PlanRegulation | None] = relationship(
        back_populates="lifecycle_dates"
    )
    plan_proposition: Mapped[PlanProposition | None] = relationship(
        back_populates="lifecycle_dates"
    )
    # Let's load all the codes for objects joined.
    lifecycle_status: Mapped[LifeCycleStatus] = relationship(
        back_populates="lifecycle_dates", lazy="joined"
    )
    # Let's add backreference to allow lazy loading from this side.
    event_dates: Mapped[list[EventDate]] = relationship(
        back_populates="lifecycle_date",
        lazy="joined",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    starting_at: Mapped[datetime]
    ending_at: Mapped[datetime | None]


class EventDate(VersionedBase):
    """Tapahtuman päivämäärät

    Jokaisessa elinkaaritilassa voi olla tiettyjä tapahtumia. Liitetään tapahtuma
    sille sallittuun elinkaaritilaan. Tapahtuman päivämäärien tulee olla aina
    elinkaaritilan päivämäärien välissä.
    """

    __tablename__ = "event_date"

    lifecycle_date_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "hame.lifecycle_date.id", name="lifecycle_date_id_fkey", ondelete="CASCADE"
        ),
        index=True,
    )
    decision_id: Mapped[UUID | None] = mapped_column(
        ForeignKey(
            "codes.name_of_plan_case_decision.id",
            name="name_of_plan_case_decision_id_fkey",
        )
    )
    processing_event_id: Mapped[UUID | None] = mapped_column(
        ForeignKey(
            "codes.type_of_processing_event.id", name="type_of_processing_event_fkey"
        )
    )
    interaction_event_id: Mapped[UUID | None] = mapped_column(
        ForeignKey(
            "codes.type_of_interaction_event.id", name="type_of_interaction_event_fkey"
        )
    )

    # Let's load all the codes for objects joined.
    lifecycle_date: Mapped[LifeCycleDate] = relationship(
        back_populates="event_dates", lazy="joined"
    )
    decision: Mapped[NameOfPlanCaseDecision] = relationship(
        back_populates="event_dates", lazy="joined"
    )
    processing_event: Mapped[TypeOfProcessingEvent] = relationship(
        back_populates="event_dates", lazy="joined"
    )
    interaction_event: Mapped[TypeOfInteractionEvent] = relationship(
        back_populates="event_dates", lazy="joined"
    )

    starting_at: Mapped[datetime]
    ending_at: Mapped[datetime | None]
