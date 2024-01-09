from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column
from base import language_str, VersionedBase


class Plan(VersionedBase):
    """
    Maakuntakaava, compatible with Ryhti 2.0 specification
    """

    __tablename__ = "plan"

    name: Mapped[language_str]
    approved_at: Mapped[Optional[datetime]]
