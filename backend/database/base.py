import uuid
from datetime import datetime
from typing import Optional
from typing_extensions import Annotated
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    """
    Here we link any postgres specific data types to type annotations.
    """
    type_annotation_map = {
        uuid.UUID: UUID(as_uuid=True),
        dict[str, str]: JSONB,
    }


"""
Here we define any custom type annotations we want to use for columns
"""
autoincrement_pk = Annotated[int, mapped_column(primary_key=True, autoincrement=True)]
uuid_pk = Annotated[uuid.UUID, mapped_column(primary_key=True, server_default=func.gen_random_uuid())]
unique_str = Annotated[str, mapped_column(unique=True)]
language_str = Annotated[dict[str, str], mapped_column(server_default='{\"fin\": \"\", \"swe\": \"\"}')]
timestamp = Annotated[datetime, mapped_column(server_default=func.now())]

metadata = Base.metadata


class CodeBase(Base):
    """
    Code tables in Ryhti should refer to national Ryhti code table URIs.
    """
    __abstract__ = True
    __table_args__ = {"schema": "codes"}
    code_list_uri = ""

    id: Mapped[autoincrement_pk]
    value: Mapped[unique_str]
    name: Mapped[language_str]

    @property
    def uri(self):
        return f"{self.code_list_uri}/code/{self.value}"


class VersionedBase(Base):
    """
    Versioned data tables should have some uniform fields.
    """
    __abstract__ = True
    __table_args__ = {"schema": "hame"}

    id: Mapped[uuid_pk]
    created_at: Mapped[timestamp]
    # TODO: postgresql has no default onupdate. Will implement this with trigger.
    modified_at: Mapped[timestamp]
    exported_at: Mapped[Optional[datetime]]
    valid_from: Mapped[Optional[datetime]]
    valid_to: Mapped[Optional[datetime]]
