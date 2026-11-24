"""Colour helpers (util/color_utils.py)."""

import math

import pytest

from helpers import image_from_rows, solid_image

R, G, B, W, K = (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 255), (0, 0, 0)


def f(c):
    return tuple(v / 255 for v in c)


# CO-01
def test_color_int_to_float(backend):
    assert backend.color_int_to_float((255, 0, 51)) == pytest.approx((1.0, 0.0, 0.2))


# CO-02
def test_complementary_color(backend):
    assert backend.find_complementary_color((0.2, 0.5, 1.0)) == pytest.approx((0.8, 0.5, 0.0))


# CO-03
def test_get_point_color_inside_and_outside(backend):
    img = image_from_rows([[R, G], [B, (10, 20, 30)]])
    assert backend.get_point_color(img, (1, 1)) == pytest.approx(f((10, 20, 30)))
    assert backend.get_point_color(img, (1, 0)) == f(G)
    for outside in [(-1, 0), (0, -1), (2, 0), (0, 2), (100, 100)]:
        assert backend.get_point_color(img, outside) == (0.0, 0.0, 0.0)


# CO-04
def test_image_mode_color(backend):
    img = image_from_rows([[R, G, G], [B, G, R]])
    assert backend.find_image_mode_color(img) == f(G)


# CO-05
def test_image_mode_color_tie_prefers_first_seen(backend):
    # R and B both appear twice; R comes first in row-major order
    assert backend.find_image_mode_color(image_from_rows([[R, B], [B, R]])) == f(R)
    assert backend.find_image_mode_color(image_from_rows([[B, R], [R, B]])) == f(B)


# CO-06
def test_points_average_color(backend):
    img = image_from_rows([[R, G], [B, W]])
    assert backend.find_points_average_color(img, [(0, 0), (1, 0)]) == pytest.approx((0.5, 0.5, 0.0))
    assert backend.find_points_average_color(img, []) == (0.0, 0.0, 0.0)


# CO-07
def test_points_average_color_counts_points_outside_image(backend):
    # the point outside contributes nothing but still divides the sum
    img = image_from_rows([[R, G], [B, W]])
    assert backend.find_points_average_color(img, [(0, 0), (5, 5)]) == pytest.approx((0.5, 0.0, 0.0))


# CO-08
def test_most_common_colors(backend):
    img = image_from_rows([[R, G, G, B], [B, G, R, W]])
    pts = [(x, y) for y in range(2) for x in range(4)]
    assert backend.find_points_most_common_colors(img, pts) == [f(G)]
    assert backend.find_points_most_common_colors(img, pts, 2) == [f(G), f(R)]   # R before B (first seen)
    assert backend.find_points_most_common_colors(img, pts, 10) == [f(G), f(R), f(B), f(W)]


# CO-09
def test_most_common_colors_ties_follow_point_order(backend):
    img = image_from_rows([[R, G, B]])
    assert backend.find_points_most_common_colors(img, [(2, 0), (0, 0), (1, 0)], 3) == [f(B), f(R), f(G)]


# CO-10
def test_most_common_colors_ignores_points_outside(backend):
    img = image_from_rows([[R, G]])
    assert backend.find_points_most_common_colors(img, [(5, 5), (1, 0), (-1, 0)]) == [f(G)]
    assert backend.find_points_most_common_colors(img, [(5, 5)]) == [(0.0, 0.0, 0.0)]
    assert backend.find_points_most_common_colors(img, []) == [(0.0, 0.0, 0.0)]


# CO-11
def test_rectangle_average_color_excludes_max_edges(backend):
    img = image_from_rows([[R, G, W], [B, K, W], [W, W, W]])
    square = [(0, 0), (2, 0), (2, 2), (0, 2)]   # pixels x 0..1, y 0..1
    assert backend.get_rectangle_average_color(square, img) == pytest.approx((0.25, 0.25, 0.25))


# CO-12
def test_rectangle_average_color_degenerate_uses_first_vertex(backend):
    img = image_from_rows([[R, G], [B, W]])
    line = [(1, 0), (1, 0), (1, 2), (1, 2)]
    assert backend.get_rectangle_average_color(line, img) == f(G)


# CO-13
def test_rectangle_standard_deviation(backend):
    img = image_from_rows([[K, W]])
    rect = [(0, 0), (2, 0), (2, 1), (0, 1)]
    avg = backend.get_rectangle_average_color(rect, img)
    assert avg == pytest.approx((0.5, 0.5, 0.5))
    # sample standard deviation per channel sqrt(0.5), summed over 3 channels
    assert backend.get_rectangle_color_standard_deviation(rect, img, avg) == pytest.approx(3 * math.sqrt(0.5))


# CO-14
def test_rectangle_standard_deviation_trivial_cases(backend):
    img = solid_image(4, 4, (10, 200, 30))
    rect = [(0, 0), (4, 0), (4, 4), (0, 4)]
    avg = backend.get_rectangle_average_color(rect, img)
    assert backend.get_rectangle_color_standard_deviation(rect, img, avg) == pytest.approx(0.0)
    one_pixel = [(1, 1), (2, 1), (2, 2), (1, 2)]
    assert backend.get_rectangle_color_standard_deviation(one_pixel, img, (0, 0, 0)) == 0


# CO-15
def test_colors_difference(backend):
    assert backend.get_colors_difference((0.1, 0.5, 1.0), (0.3, 0.5, 0.0)) == pytest.approx(1.2)
    assert backend.get_colors_difference((0.2, 0.2, 0.2), (0.2, 0.2, 0.2)) == 0


# CO-16
def test_colors_ratio(backend):
    img = image_from_rows([[R, R, B]])
    pts = [(0, 0), (1, 0), (2, 0)]
    # counts start at 1: red 1+2, blue 1+1
    assert backend.get_colors_ratio(img, pts, f(R), f(B)) == pytest.approx(2 / 3)
    assert backend.get_colors_ratio(img, pts, f(B), f(R)) == pytest.approx(3 / 2)


# CO-17
def test_colors_ratio_tie_counts_for_second_color(backend):
    img = image_from_rows([[K]])
    # black is equally far from red and green -> counted for the second colour
    assert backend.get_colors_ratio(img, [(0, 0)], f(R), f(G)) == pytest.approx(2.0)
    assert backend.get_colors_ratio(img, [], f(R), f(G)) == pytest.approx(1.0)
