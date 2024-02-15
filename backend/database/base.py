import uuid
from datetime import datetime
from typing import Optional, Tuple

from geoalchemy2 import Geometry
from shapely.geometry import MultiLineString, MultiPoint, MultiPolygon
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import JSONB, NUMRANGE, UUID
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    declared_attr,
    mapped_column,
    relationship,
)
from sqlalchemy.sql import func
from typing_extensions import Annotated

PROJECT_SRID = 3067


class Base(DeclarativeBase):
    """
    Here we link any postgres specific data types to type annotations.
    """

    type_annotation_map = {
        uuid.UUID: UUID(as_uuid=True),
        dict[str, str]: JSONB,
        MultiLineString: Geometry(geometry_type="MULTILINE", srid=PROJECT_SRID),
        MultiPoint: Geometry(geometry_type="MULTILINESTRING", srid=PROJECT_SRID),
        MultiPolygon: Geometry(geometry_type="MULTIPOLYGON", srid=PROJECT_SRID),
        Tuple[float, float]: NUMRANGE,
    }


"""
Here we define any custom type annotations we want to use for columns
"""
uuid_pk = Annotated[
    uuid.UUID, mapped_column(primary_key=True, server_default=func.gen_random_uuid())
]
unique_str = Annotated[str, mapped_column(unique=True, index=True)]
language_str = Annotated[
    dict[str, str], mapped_column(server_default='{"fin": "", "swe": "", "eng": ""}')
]
numeric_range = Annotated[Tuple[float, float], mapped_column(nullable=True)]
timestamp = Annotated[datetime, mapped_column(server_default=func.now())]
autoincrement_int = Annotated[int, mapped_column(autoincrement=True, nullable=True)]

metadata = Base.metadata


class VersionedBase(Base):
    """
    Versioned data tables should have some uniform fields.
    """

    __abstract__ = True
    __table_args__ = {"schema": "hame"}

    id: Mapped[uuid_pk]
    created_at: Mapped[timestamp]
    # TODO: postgresql has no default onupdate. Must implement this with trigger.
    modified_at: Mapped[timestamp]


class CodeBase(VersionedBase):
    """
    Code tables in Ryhti should refer to national Ryhti code table URIs. They may
    have hierarchical structure.
    """

    __abstract__ = True
    __table_args__ = {"schema": "codes"}
    code_list_uri = ""

    value: Mapped[unique_str]
    short_name: Mapped[str] = mapped_column(server_default="", index=True)
    name: Mapped[language_str]
    description: Mapped[language_str]
    # Let's import code status too. This tells our importer if the koodisto is final,
    # or if the code can be deleted and/or moved.
    status: Mapped[str]
    # For now, level can just be imported from RYTJ. Let's assume the level in RYTJ
    # is correct, so we don't have to calculate and recalculate it ourselves.
    level: Mapped[int] = mapped_column(server_default="1", index=True)

    # self-reference in abstract base class:
    # We cannot use @classmethod decorator here. Alembic is buggy and apparently
    # does not recognize declared attributes that are correctly marked as class methods.
    @declared_attr
    def parent_id(cls) -> Mapped[Optional[uuid.UUID]]:  # noqa
        return mapped_column(
            ForeignKey(cls.id, name=f"{cls.__tablename__}_parent_id_fkey"), index=True
        )

    @classmethod
    @declared_attr
    def parent(cls) -> Mapped[VersionedBase]:
        return relationship(cls, back_populates="children")

    @property
    def uri(self):
        return f"{self.code_list_uri}/code/{self.value}"


class PlanBase(VersionedBase):
    """
    All plan data tables should have additional date fields.
    """

    __abstract__ = True

    exported_at: Mapped[Optional[datetime]]
    valid_from: Mapped[Optional[datetime]]
    valid_to: Mapped[Optional[datetime]]
    repealed_at: Mapped[Optional[datetime]]
    lifecycle_status_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("codes.lifecycle_status.id", name="plan_lifecycle_status_id_fkey"),
        index=True,
    )

    # class reference in abstract base class, with backreference to class name:
    @classmethod
    @declared_attr
    def lifecycle_status(cls) -> Mapped[VersionedBase]:
        return relationship("LifeCycleStatus", back_populates=f"{cls.__tablename__}s")


class PlanFeatureBase(PlanBase):
    """
    All plan feature tables have the same fields, apart from geometry.
    """

    __abstract__ = True

    name: Mapped[language_str]
    source_data_object: Mapped[str] = mapped_column(nullable=True)
    height_range: Mapped[numeric_range]
    height_unit: Mapped[str] = mapped_column(nullable=True)
    ordering: Mapped[autoincrement_int]
    type_of_underground_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("codes.type_of_underground.id", name="type_of_underground_id_fkey"),
        index=True,
    )
    plan_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("hame.plan.id", name="plan_id_fkey"), index=True
    )
    plan_regulation_group_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(
            "hame.plan_regulation_group.id", name="plan_regulation_group_id_fkey"
        ),
        index=True,
    )

    # class reference in abstract base class, with backreference to class name:
    @classmethod
    @declared_attr
    def type_of_underground(cls) -> Mapped[VersionedBase]:
        return relationship("TypeOfUnderground", back_populates=f"{cls.__tablename__}s")

    # class reference in abstract base class, with backreference to class name:
    @classmethod
    @declared_attr
    def plan(cls) -> Mapped[VersionedBase]:
        return relationship("Plan", back_populates=f"{cls.__tablename__}s")

    # class reference in abstract base class, with backreference to class name:
    @classmethod
    @declared_attr
    def plan_regulation_group(cls) -> Mapped[VersionedBase]:
        return relationship(
            "PlanRegulationGroup", back_populates=f"{cls.__tablename__}s"
        )
