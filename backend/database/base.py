import uuid
from datetime import datetime
from typing import Any, List, Optional

from geoalchemy2 import Geometry
from shapely.geometry import MultiLineString, MultiPoint, MultiPolygon
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func
from sqlalchemy.types import ARRAY, TEXT, TIMESTAMP
from sqlalchemy.types import Enum as SQLAlchemyEnum
from typing_extensions import Annotated

from database.enums import AttributeValueDataType

PROJECT_SRID = 3067


class Base(DeclarativeBase):
    """
    Here we link any postgres specific data types to type annotations.
    """

    type_annotation_map = {
        uuid.UUID: UUID(as_uuid=False),
        dict[str, str]: JSONB,
        List[str]: ARRAY(TEXT),
        MultiLineString: Geometry(geometry_type="MULTILINESTRING", srid=PROJECT_SRID),
        MultiPoint: Geometry(geometry_type="MULTIPOINT", srid=PROJECT_SRID),
        MultiPolygon: Geometry(geometry_type="MULTIPOLYGON", srid=PROJECT_SRID),
        datetime: TIMESTAMP(timezone=True),
    }


"""
Here we define any custom type annotations we want to use for columns
"""
uuid_pk = Annotated[
    uuid.UUID, mapped_column(primary_key=True, server_default=func.gen_random_uuid())
]
unique_str = Annotated[str, mapped_column(unique=True, index=True)]
language_str = dict[str, str]
timestamp = Annotated[datetime, mapped_column(server_default=func.now())]

metadata = Base.metadata


class VersionedBase(Base):
    """
    Versioned data tables should have some uniform fields.
    """

    __abstract__ = True
    __table_args__: Any = {"schema": "hame"}

    # Go figure. We have to *explicitly state* id is a mapped column, because id will
    # have to be defined inside all the subclasses for relationship remote_side
    # definition to work. So even if there is an id field in all the classes,
    # self-relationships will later break if id is only defined by type annotation.
    id: Mapped[uuid_pk] = mapped_column()
    created_at: Mapped[timestamp]
    # TODO: postgresql has no default onupdate. Must implement this with trigger.
    modified_at: Mapped[timestamp]


class AttributeValueMixin:
    """Common attributes for property values"""

    value_data_type: Mapped[Optional[AttributeValueDataType]] = mapped_column(
        SQLAlchemyEnum(
            AttributeValueDataType, values_callable=lambda e: [x.value for x in e]
        ),
    )

    numeric_value: Mapped[Optional[float]]
    numeric_range_min: Mapped[Optional[float]]
    numeric_range_max: Mapped[Optional[float]]

    unit: Mapped[Optional[str]]

    text_value: Mapped[Optional[language_str]]
    text_syntax: Mapped[Optional[str]]

    code_list: Mapped[Optional[str]]
    code_value: Mapped[Optional[str]]
    code_title: Mapped[Optional[language_str]]

    height_reference_point: Mapped[Optional[str]]
