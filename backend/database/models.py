from datetime import datetime
from typing import Optional

from base import PlanBase, PlanFeatureBase, VersionedBase, language_str, unique_str
from shapely.geometry import MultiLineString, MultiPoint, MultiPolygon
from sqlalchemy.orm import Mapped


class Plan(PlanBase):
    """
    Maakuntakaava, compatible with Ryhti 2.0 specification
    """

    __tablename__ = "plan"

    name: Mapped[language_str]
    approved_at: Mapped[Optional[datetime]]
    geom: Mapped[MultiPolygon]


class LandUseArea(PlanFeatureBase):
    """
    Osa-alue
    """

    __tablename__ = "land_use_area"

    geom: Mapped[MultiPolygon]


class OtherArea(PlanFeatureBase):
    """
    Aluevaraus
    """

    __tablename__ = "other_area"

    geom: Mapped[MultiPolygon]


class Line(PlanFeatureBase):
    """
    Viivat
    """

    __tablename__ = "line"

    geom: Mapped[MultiLineString]


class LandUsePoint(PlanFeatureBase):
    """
    Maankäytön pisteet
    """

    __tablename__ = "land_use_point"

    geom: Mapped[MultiPoint]


class OtherPoint(PlanFeatureBase):
    """
    Muut pisteet
    """

    __tablename__ = "other_point"

    geom: Mapped[MultiPoint]


class PlanRegulationGroup(VersionedBase):
    """
    Kaavamääräysryhmä
    """

    __tablename__ = "plan_regulation_group"

    short_name: Mapped[unique_str]
    name: Mapped[language_str]
