import uuid
from datetime import datetime
from typing import Optional
from typing_extensions import Annotated
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
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
    code_list_uri = ""

    id: Mapped[autoincrement_pk]
    value: Mapped[unique_str]
    name: Mapped[language_str]

    @property
    def uri(self):
        return f"{self.code_list_uri}/code/{self.value}"


class LifeCycleStatus(CodeBase):
    """
    This code table is common to all versioned data tables.
    """
    __tablename__ = "lifecycle_status"
    code_list_uri = "http://uri.suomi.fi/codelist/rytj/kaavaelinkaari"


class VersionedBase(Base):
    """
    Versioned data tables should have some uniform fields.
    """
    __abstract__ = True

    id: Mapped[uuid_pk]
    created_at: Mapped[timestamp]
    # TODO: postgresql has no default onupdate. Will implement this with trigger.
    modified_at: Mapped[timestamp]
    exported_at: Mapped[Optional[datetime]]
    valid_from: Mapped[Optional[datetime]]
    valid_to: Mapped[Optional[datetime]]
    lifecycle_status_id: Mapped[int] = mapped_column(ForeignKey("lifecycle_status.id"))

    @declared_attr
    def lifecycle_status(cls) -> Mapped["LifeCycleStatus"]:
        return relationship("LifeCycleStatus")
