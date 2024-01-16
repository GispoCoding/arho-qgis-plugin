from datetime import datetime
from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from base import language_str, VersionedBase
from codes import LifeCycleStatus


class Plan(VersionedBase):
    """
    Maakuntakaava, compatible with Ryhti 2.0 specification
    """

    __tablename__ = "plan"

    name: Mapped[language_str]
    approved_at: Mapped[Optional[datetime]]
    lifecycle_status_id: Mapped[int] = mapped_column(ForeignKey("codes.lifecycle_status.id"))
    lifecycle_status: Mapped[LifeCycleStatus] = relationship(back_populates="plans")
