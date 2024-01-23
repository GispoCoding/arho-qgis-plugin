from datetime import datetime
from typing import Optional

from base import VersionedBase, language_str
from codes import LifeCycleStatus
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Plan(VersionedBase):
    """
    Maakuntakaava, compatible with Ryhti 2.0 specification
    """

    __tablename__ = "plan"

    name: Mapped[language_str]
    approved_at: Mapped[Optional[datetime]]
    lifecycle_status_id: Mapped[int] = mapped_column(
        ForeignKey("codes.lifecycle_status.id")
    )
    lifecycle_status: Mapped[LifeCycleStatus] = relationship(back_populates="plans")
