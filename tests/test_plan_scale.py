"""Default plan scales and the GeoTIFF pixel size that follows from the scale and the dpi."""

from __future__ import annotations

import pytest
from qgis.core import QgsRectangle

from arho_feature_template.core.plan_scale import (
    PIXEL_SIZES,
    default_pixel_size,
    default_scale,
    dpi_for,
    image_size,
    nearest_allowed_pixel_size,
    pixel_size_for,
    plan_map_extent,
)
from arho_feature_template.project.layers.code_layers import PlanType


@pytest.mark.parametrize(
    ("plan_type", "scale"),
    [
        (PlanType.REGIONAL, 100000),
        (PlanType.GENERAL, 10000),
        (PlanType.TOWN, 1000),
        (None, None),
    ],
)
def test_default_scale_by_plan_type(plan_type, scale):
    assert default_scale(plan_type) == scale


def test_pixel_sizes_are_the_powers_of_two_ryhti_allows():
    assert PIXEL_SIZES[0] == 0.015625
    assert PIXEL_SIZES[-1] == 256
    assert 0.5 in PIXEL_SIZES


def test_pixel_size_and_dpi_are_inverse():
    assert pixel_size_for(1000, 254) == pytest.approx(0.1)
    assert dpi_for(1000, 0.1) == pytest.approx(254)


@pytest.mark.parametrize(
    ("pixel_size", "nearest"),
    [
        (0.0847, 0.0625),
        (0.1016, 0.125),
        (0.5, 0.5),
        (1.4, 1),
        (1.5, 2),
        (0.001, 0.015625),
        (1000, 256),
    ],
)
def test_nearest_allowed_pixel_size(pixel_size, nearest):
    assert nearest_allowed_pixel_size(pixel_size) == nearest


@pytest.mark.parametrize(("scale", "pixel_size"), [(1000, 0.125), (10000, 1), (100000, 8)])
def test_default_pixel_size_by_scale(scale, pixel_size):
    assert default_pixel_size(scale) == pixel_size


def test_plan_map_extent_covers_the_plan_with_a_margin_on_the_pixel_grid():
    plan_extent = QgsRectangle(1000.3, 2000.7, 1100.1, 2050.2)

    extent = plan_map_extent(plan_extent, 8)

    # The margin is 10 % of the longer side, here 9.98 m
    assert extent.contains(plan_extent.buffered(9.98))
    for coordinate in (extent.xMinimum(), extent.yMinimum(), extent.xMaximum(), extent.yMaximum()):
        assert coordinate % 8 == 0
    assert image_size(extent, 8) == (extent.width() / 8, extent.height() / 8)


def test_image_size_on_a_fine_pixel_grid():
    extent = plan_map_extent(QgsRectangle(0, 0, 1000, 500), 0.125)

    assert (extent.xMinimum(), extent.xMaximum()) == (-100, 1100)
    assert image_size(extent, 0.125) == (9600, 5600)
