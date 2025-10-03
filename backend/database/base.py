from __future__ import annotations

import uuid
from datetime import datetime
from typing import Annotated, Any, ClassVar

from sqlalchemy import FetchedValue
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func
from sqlalchemy.types import ARRAY, TEXT, TIMESTAMP, Enum as SQLAlchemyEnum

from database.enums import AttributeValueDataType

PROJECT_SRID = 3067


class Base(DeclarativeBase):
    """Here we link any postgres specific data types to type annotations."""

    type_annotation_map: ClassVar[dict[Any, Any]] = {
        uuid.UUID: postgresql.UUID(as_uuid=False),
        dict[str, str]: postgresql.JSONB,  # Used for multi language text fields
        dict[str, Any] | str: postgresql.JSONB,  # Used for validation errors
        list[str]: ARRAY(TEXT),
        datetime: TIMESTAMP(timezone=True),
    }


"""
Here we define any custom type annotations we want to use for columns
"""

unique_str = Annotated[str, mapped_column(unique=True, index=True)]
language_str = dict[str, str]

metadata = Base.metadata


class VersionedBase(Base):
    """Versioned data tables should have some uniform fields."""

    __abstract__ = True
    __table_args__: Any = {"schema": "hame"}  # noqa: RUF012  # No can do, sqlalchemy has Any annotation for this

    # Go figure. We have to *explicitly state* id is a mapped column, because id will
    # have to be defined inside all the subclasses for relationship remote_side
    # definition to work. So even if there is an id field in all the classes,
    # self-relationships will later break if id is only defined by type annotation.
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, server_default=func.gen_random_uuid()
    )
    created_at: Mapped[datetime | None] = mapped_column(
        server_default=FetchedValue()
    )  # Set always in before insert trigger. Must be nullable for clients
    modified_at: Mapped[datetime | None] = mapped_column(
        server_default=FetchedValue(), server_onupdate=FetchedValue()
    )  # Set always in before insert/update trigger. Must be nullable for clients


class AttributeValueMixin:
    """Common attributes for property values."""

    value_data_type: Mapped[AttributeValueDataType | None] = mapped_column(
        SQLAlchemyEnum(
            AttributeValueDataType, values_callable=lambda e: [x.value for x in e]
        )
    )

    numeric_value: Mapped[float | None]
    numeric_range_min: Mapped[float | None]
    numeric_range_max: Mapped[float | None]

    unit: Mapped[str | None]

    text_value: Mapped[language_str | None]
    text_syntax: Mapped[str | None]

    code_list: Mapped[str | None]
    code_value: Mapped[str | None]
    code_title: Mapped[language_str | None]

    height_reference_point: Mapped[str | None]
