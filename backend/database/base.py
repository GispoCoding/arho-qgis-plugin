import uuid
from datetime import datetime
from typing import Optional

from geoalchemy2 import Geometry
from shapely.geometry import Polygon
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
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
        Polygon: Geometry(geometry_type="POLYGON", srid=PROJECT_SRID),
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
timestamp = Annotated[datetime, mapped_column(server_default=func.now())]

metadata = Base.metadata


class VersionedBase(Base):
    """
    Versioned data tables should have some uniform fields.
    """

    __abstract__ = True

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
    name: Mapped[language_str]

    @property
    def uri(self):
        return f"{self.code_list_uri}/code/{self.value}"


class PlanBase(VersionedBase):
    """
    All plan data tables should have additional date fields.
    """

    __abstract__ = True
    __table_args__ = {"schema": "hame"}

    exported_at: Mapped[Optional[datetime]]
    valid_from: Mapped[Optional[datetime]]
    valid_to: Mapped[Optional[datetime]]
