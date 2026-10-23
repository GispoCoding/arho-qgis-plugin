"""Plan scale and the pixel size of the plan map GeoTIFF.

The scale is the denominator of the scale ratio (1000 for 1:1000), as in the Ryhti `scale`
field. The scale, the dpi and the pixel size are tied by
pixel size (m/px) = scale * 0.0254 / dpi.
"""

from __future__ import annotations

import math

from qgis.core import QgsRectangle

from arho_feature_template.project.layers.code_layers import PlanType, PlanTypeLayer
from arho_feature_template.utils.misc_utils import get_active_plan_matter_plan_type_id

METRES_PER_INCH = 0.0254

DEFAULT_SCALES = {
    PlanType.REGIONAL: 100000,
    PlanType.GENERAL: 10000,
    PlanType.TOWN: 1000,
}

# Ryhti accepts only pixel sizes that are a power of two from 0.015625 m to 256 m (rule 227)
MIN_PIXEL_SIZE_EXPONENT = -6
MAX_PIXEL_SIZE_EXPONENT = 8
PIXEL_SIZES = [2.0**exponent for exponent in range(MIN_PIXEL_SIZE_EXPONENT, MAX_PIXEL_SIZE_EXPONENT + 1)]

DEFAULT_DPI = 250

PLAN_MAP_MARGIN = 0.1


def default_scale(plan_type: PlanType | None) -> int | None:
    return DEFAULT_SCALES.get(plan_type) if plan_type is not None else None


def default_scale_of_active_plan_matter() -> int | None:
    return default_scale(PlanTypeLayer.get_plan_type(get_active_plan_matter_plan_type_id()))


def pixel_size_for(scale: float, dpi: float) -> float:
    return scale * METRES_PER_INCH / dpi


def dpi_for(scale: float, pixel_size: float) -> float:
    return scale * METRES_PER_INCH / pixel_size


def nearest_allowed_pixel_size(pixel_size: float) -> float:
    """The allowed pixel size nearest to the given one on a logarithmic scale."""
    exponent = round(math.log2(pixel_size))
    return 2.0 ** max(MIN_PIXEL_SIZE_EXPONENT, min(MAX_PIXEL_SIZE_EXPONENT, exponent))


def default_pixel_size(scale: float) -> float:
    return nearest_allowed_pixel_size(pixel_size_for(scale, DEFAULT_DPI))


def plan_map_extent(plan_extent: QgsRectangle, pixel_size: float) -> QgsRectangle:
    """The plan extent with a 10 % margin, snapped outwards to the pixel grid."""
    margin = max(plan_extent.width(), plan_extent.height()) * PLAN_MAP_MARGIN
    return QgsRectangle(
        math.floor((plan_extent.xMinimum() - margin) / pixel_size) * pixel_size,
        math.floor((plan_extent.yMinimum() - margin) / pixel_size) * pixel_size,
        math.ceil((plan_extent.xMaximum() + margin) / pixel_size) * pixel_size,
        math.ceil((plan_extent.yMaximum() + margin) / pixel_size) * pixel_size,
    )


def image_size(extent: QgsRectangle, pixel_size: float) -> tuple[int, int]:
    """Width and height in pixels of an extent snapped to the pixel grid."""
    return round(extent.width() / pixel_size), round(extent.height() / pixel_size)
