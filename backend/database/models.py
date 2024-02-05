from datetime import datetime
from typing import Optional

from base import PlanBase, language_str
from shapely.geometry import Polygon
from sqlalchemy.orm import Mapped


class Plan(PlanBase):
    """
    Maakuntakaava, compatible with Ryhti 2.0 specification
    """

    __tablename__ = "plan"

    name: Mapped[language_str]
    approved_at: Mapped[Optional[datetime]]
    geom: Mapped[Polygon]
