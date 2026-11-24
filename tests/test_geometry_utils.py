"""Geometry helpers (util/geometry_utils.py, geometry/point_2d.py)."""

import pytest

from helpers import solid_image, shoelace_area, normalize_polygon, polygons_close

IMG10 = solid_image(10, 10, (50, 50, 50))


# GE-01
# ---- Point2D -------------------------------------------------------------------------------
def test_euclidean_distance(backend):
    assert backend.euclidean_distance((0, 0), (3, 4)) == 5.0
    assert backend.euclidean_distance((2, 2), (2, 2)) == 0.0


# GE-02
def test_line_center_truncates_toward_zero(backend):
    assert backend.line_center((1, 1), (4, 4)) == (2, 2)
    assert backend.line_center((-1, 0), (-4, 0)) == (-2, 0)
    assert backend.line_center((0, 0), (10, 6)) == (5, 3)


# GE-03
# ---- image bounds / rectangles ----------------------------------------------------------------
def test_is_point_in_image(backend):
    img = solid_image(4, 3, (0, 0, 0))
    assert backend.is_point_in_image(img, (0, 0))
    assert backend.is_point_in_image(img, (3, 2))
    for p in [(4, 0), (0, 3), (-1, 0), (0, -1)]:
        assert not backend.is_point_in_image(img, p)


# GE-04
def test_find_rectangle_points_excludes_max(backend):
    assert backend.find_rectangle_points([(1, 2), (4, 2), (4, 5), (1, 5)]) == ([1, 2, 3], [2, 3, 4])
    assert backend.find_rectangle_points([(3, 3), (3, 3), (3, 3), (3, 3)]) == ([], [])


# GE-05
# ---- points in polygon ------------------------------------------------------------------------
def test_points_in_square(backend):
    square = [(0, 0), (4, 0), (4, 4), (0, 4)]
    pts = backend.find_points_in_polygon(square, -1, IMG10)
    assert pts[:4] == square                         # vertices always come first
    assert len(pts) == len(set(pts)) == 13           # + strictly interior points x, y in 1..3
    assert set(pts[4:]) == {(x, y) for x in range(1, 4) for y in range(1, 4)}


# GE-06
def test_points_in_triangle(backend):
    tri = [(0, 0), (6, 0), (0, 6)]
    pts = backend.find_points_in_polygon(tri, -1, IMG10)
    assert set(pts[3:]) == {(x, y) for x in range(1, 6) for y in range(1, 6) if x + y < 6}
    assert len(pts) == 3 + 10


# GE-07
def test_points_in_polygon_limit(backend):
    square = [(0, 0), (4, 0), (4, 4), (0, 4)]
    allowed = set(backend.find_points_in_polygon(square, -1, IMG10))
    backend.seed(3)
    pts = backend.find_points_in_polygon(square, 6, IMG10)
    assert len(pts) == 6 and pts[:4] == square and set(pts) <= allowed


# GE-08
def test_points_in_polygon_partially_outside_image(backend):
    poly = [(-2, -2), (3, -2), (3, 3), (-2, 3)]
    pts = backend.find_points_in_polygon(poly, -1, IMG10)
    assert pts[:4] == poly                           # vertices are kept even outside the image
    assert set(pts[4:]) == {(x, y) for x in range(0, 3) for y in range(0, 3)}


# GE-09
def test_points_in_polygon_all_vertices_outside(backend):
    assert backend.find_points_in_polygon([(-5, -5), (-1, -5), (-1, -1)], -1, IMG10) == []
    # even if the polygon covers the image
    assert backend.find_points_in_polygon([(-5, -5), (20, -5), (20, 20), (-5, 20)], -1, IMG10) == []


# GE-10
def test_points_in_polygon_random_order_is_seeded(backend):
    poly = [(0, 0), (9, 0), (9, 9), (0, 9)]
    backend.seed(11)
    a = backend.find_points_in_polygon(poly, -1, IMG10)
    backend.seed(11)
    b = backend.find_points_in_polygon(poly, -1, IMG10)
    assert a == b


# ---- cropping -------------------------------------------------------------------------------
BOUNDS = [(0, 0), (0, 10), (10, 10), (10, 0)]


# GE-11
def test_crop_partially_outside(backend):
    res = backend.crop_polygon_by_bounds(BOUNDS, [(-5, -5), (5, -5), (5, 5), (-5, 5)])
    assert polygons_close(res, [(0, 0), (5, 0), (5, 5), (0, 5)], tol=1e-9)


# GE-12
def test_crop_triangle(backend):
    res = backend.crop_polygon_by_bounds(BOUNDS, [(5, 5), (15, 5), (5, 15)])
    assert polygons_close(res, [(5, 5), (10, 5), (10, 10), (5, 10)], tol=1e-9)


# GE-13
def test_crop_fully_inside(backend):
    poly = [(1, 1), (8, 2), (4, 7)]
    assert polygons_close(backend.crop_polygon_by_bounds(BOUNDS, poly), poly, tol=1e-9)


# GE-14
def test_crop_disjoint_gives_empty(backend):
    assert backend.crop_polygon_by_bounds(BOUNDS, [(20, 20), (30, 20), (30, 30)]) == []


# GE-15
def test_crop_touching_edge_gives_empty(backend):
    # the intersection is only a line segment, it has no area
    assert backend.crop_polygon_by_bounds(BOUNDS, [(10, 0), (20, 0), (20, 10), (10, 10)]) == []


# GE-16
def test_crop_self_intersecting_polygon_is_repaired(backend):
    # a bow-tie is split into its two triangles; the larger part inside the bounds is returned
    bowtie = [(-5, -5), (15, 15), (15, -5), (-5, 15)]
    res = backend.crop_polygon_by_bounds(BOUNDS, bowtie)
    assert all(0 <= x <= 10 and 0 <= y <= 10 for x, y in res)
    assert shoelace_area(normalize_polygon(res)) == pytest.approx(25)


# GE-17
def test_crop_rounded_voronoi_region_with_line_part(backend):
    # region from a real run: its intersection with the image is a polygon plus a line segment
    bounds = [(0, 0), (0, 63), (95, 63), (95, 0)]
    region = [(2, 47), (2, 46), (-339, 46), (-337, 49), (0, 49), (0, 48)]
    res = backend.crop_polygon_by_bounds(bounds, region)
    assert polygons_close(res, [(0, 46), (2, 46), (2, 47), (0, 48)], tol=1e-9)


# GE-18
def test_crop_degenerate_self_touching_region(backend):
    bounds = [(0, 0), (0, 63), (95, 63), (95, 0)]
    region = [(82, 2), (82, 3), (82, 2), (82, -310), (83, -309), (83, 2)]
    res = backend.crop_polygon_by_bounds(bounds, region)
    assert polygons_close(res, [(82, 0), (83, 0), (83, 2), (82, 2)], tol=1e-9)


# GE-19
# ---- area / random point / centroid / longest side -----------------------------------------------
def test_polygon_area(backend):
    assert backend.polygon_area([(0, 0), (4, 0), (4, 3), (0, 3)]) == 12.0
    assert backend.polygon_area([(0, 0), (4, 0), (0, 3)]) == 6.0
    assert backend.polygon_area([(0, 0), (0, 3), (4, 0)]) == 6.0


# GE-20
def test_random_point_in_polygon_is_strictly_inside(backend):
    backend.seed(5)
    tri = [(0, 0), (10, 0), (0, 10)]
    for _ in range(200):
        x, y = backend.random_point_in_polygon(tri)
        assert isinstance(x, int) and isinstance(y, int)
        assert x > 0 and y > 0 and x + y < 10


# GE-21
def test_random_point_in_polygon_without_inner_point(backend):
    backend.seed(7)
    sliver = [(94, 41), (94, 42), (95, 43.5), (95, 41)]     # no integer point strictly inside
    assert backend.random_point_in_polygon(sliver) is None
    square = [(0, 0), (2, 0), (2, 2), (0, 2)]               # only (1, 1) is inside
    assert backend.random_point_in_polygon(square) == (1, 1)
    assert backend.random_point_in_polygon(square, excluded=(1, 1)) is None


# GE-22
def test_random_point_in_polygon_avoids_excluded_point(backend):
    backend.seed(8)
    square = [(0, 0), (3, 0), (3, 2), (0, 2)]               # (1, 1) and (2, 1) are inside
    assert {backend.random_point_in_polygon(square, excluded=(1, 1)) for _ in range(50)} == {(2, 1)}


# GE-23
def test_random_point_in_polygon_uses_whole_polygon(backend):
    backend.seed(6)
    square = [(0, 0), (4, 0), (4, 4), (0, 4)]
    seen = {backend.random_point_in_polygon(square) for _ in range(400)}
    assert seen == {(x, y) for x in range(1, 4) for y in range(1, 4)}


# GE-24
def test_centroid(backend):
    assert backend.find_polygon_centroid([(0, 0), (3, 0), (0, 3)]) == (1, 1)
    assert backend.find_polygon_centroid([(0, 0), (1, 0), (1, 1)]) == (0, 0)     # 2/3 truncated
    assert backend.find_polygon_centroid([(-3, 0), (0, 0), (-2, 0)]) == (-1, 0)  # -5/3 toward zero
    assert backend.find_polygon_centroid([]) == (-1, -1)


# GE-25
def test_longest_side(backend):
    assert backend.find_polygon_longest_side([(0, 0), (3, 0), (3, 4)]) == ((3, 4), (0, 0))
    # ties: the first side wins
    assert backend.find_polygon_longest_side([(0, 0), (1, 0), (1, 1), (0, 1)]) == ((0, 0), (1, 0))
    assert backend.find_polygon_longest_side([]) == (None, None)


# GE-26
# ---- split polygon ----------------------------------------------------------------------------
def test_split_square_in_half(backend):
    square = [(0, 0), (20, 0), (20, 20), (0, 20)]
    parts = backend.split_polygon(square)
    assert len(parts) == 2
    boxes = sorted((min(x for x, _ in p), max(x for x, _ in p), min(y for _, y in p), max(y for _, y in p))
                   for p in parts)
    assert boxes == [(0, 9, 0, 20), (11, 20, 0, 20)]   # cut along x = 10, 2 px wide
    for p in parts:
        assert shoelace_area(normalize_polygon(p)) == pytest.approx(180, abs=1)


# GE-27
def test_split_keeps_original_vertices(backend):
    poly = [(0, 0), (40, 0), (50, 20), (20, 35), (0, 20)]
    parts = backend.split_polygon(poly)
    assert len(parts) == 2
    kept = [v for part in parts for v in part if v in poly]
    assert sorted(set(kept)) == sorted(poly)           # each original vertex lands in one part
    total = sum(shoelace_area(normalize_polygon(p)) for p in parts)
    assert shoelace_area(poly) - 150 < total < shoelace_area(poly)


# GE-28
def test_split_too_small_returns_original(backend):
    tri = [(0, 0), (1, 0), (0, 1)]
    assert backend.split_polygon(tri) == [tri]
    assert backend.split_polygon([]) == [[]]


# GE-29
# ---- removing close points ----------------------------------------------------------------------
def test_remove_similar_points_keeps_order_and_is_inclusive(backend):
    pts = [(0, 0), (1, 0), (5, 5), (0, 1), (5, 6), (1, 1)]
    # distance exactly 1 counts as "too close", sqrt(2) does not
    assert backend.remove_similar_points(pts, 1) == [(0, 0), (5, 5), (1, 1)]


# GE-30
def test_remove_similar_points_no_chaining(backend):
    # (2, 0) is only close to (1, 0), which was already removed -> kept
    assert backend.remove_similar_points([(0, 0), (1, 0), (2, 0)], 1) == [(0, 0), (2, 0)]


# GE-31
def test_remove_similar_points_zero_distance_removes_duplicates(backend):
    assert backend.remove_similar_points([(1, 1), (2, 2), (1, 1), (3, 3)], 0) == [(1, 1), (2, 2), (3, 3)]


# GE-32
def test_remove_similar_points_larger_radius(backend):
    pts = [(0, 0), (3, 4), (6, 8), (2, 1), (10, 10)]
    assert backend.remove_similar_points(pts, 5) == [(0, 0), (6, 8)]
