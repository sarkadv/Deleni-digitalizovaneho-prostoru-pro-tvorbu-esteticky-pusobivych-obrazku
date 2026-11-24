"""Space partitioning: Voronoi diagram, Delaunay triangulation, quadtree (tessellations/)."""

import pytest

from helpers import solid_image, normalize_polygon, shoelace_area, polygons_close

QUADTREE_IMAGES = ["blocks", "blocks_large", "photo", "gradient"]


def corners(img):
    return [(0, 0), (img.width, 0), (img.width, img.height), (0, img.height)]


def triangle_pixels(tri, img):
    """Colours of the triangle's vertices and of all integer points strictly inside it."""
    (ax, ay), (bx, by), (cx, cy) = tri
    area2 = (bx - ax) * (cy - ay) - (by - ay) * (cx - ax)
    cols = set()
    for x, y in tri:
        if 0 <= x < img.width and 0 <= y < img.height:
            cols.add(img.pixel(x, y))
    for y in range(min(ay, by, cy), max(ay, by, cy) + 1):
        for x in range(min(ax, bx, cx), max(ax, bx, cx) + 1):
            d1 = (bx - ax) * (y - ay) - (by - ay) * (x - ax)
            d2 = (cx - bx) * (y - by) - (cy - by) * (x - bx)
            d3 = (ax - cx) * (y - cy) - (ay - cy) * (x - cx)
            inside = (d1 > 0 and d2 > 0 and d3 > 0) if area2 > 0 else (d1 < 0 and d2 < 0 and d3 < 0)
            if inside and 0 <= x < img.width and 0 <= y < img.height:
                cols.add(img.pixel(x, y))
    return cols


def f(c):
    return tuple(v / 255 for v in c)


# TE-01
# ---- quadtree ------------------------------------------------------------------------------
def test_quadtree_distribution_returns_image_corners(backend, data_image):
    img = data_image("blocks")
    assert backend.generate_points(img, "QUADTREE", 1, img.width, 1, img.height) == corners(img)


# TE-02
@pytest.mark.parametrize("name", QUADTREE_IMAGES)
def test_quadtree_matches_reference(backend, data_image, golden, name):
    img = data_image(name)
    expected = golden("quadtree_regions")[name]
    regions = backend.generate_regions(corners(img), img, "QUADTREE")
    assert len(regions) == len(expected)
    for got, exp in zip(regions, expected):
        assert got.kind == "quadtree"
        assert [list(v) for v in got.vertices] == exp["vertices"]
        assert got.color == pytest.approx(tuple(exp["color"]), abs=1e-12)


# TE-03
@pytest.mark.parametrize("name", QUADTREE_IMAGES)
def test_quadtree_regions_tile_the_image(backend, data_image, name):
    img = data_image(name)
    regions = backend.generate_regions(corners(img), img, "QUADTREE")
    covered = [[0] * img.width for _ in range(img.height)]
    for r in regions:
        nw, ne, se, sw = r.vertices
        assert nw[1] == ne[1] and sw[1] == se[1] and nw[0] == sw[0] and ne[0] == se[0]   # NW, NE, SE, SW
        for y in range(nw[1], sw[1]):
            for x in range(nw[0], ne[0]):
                covered[y][x] += 1
    assert all(c == 1 for row in covered for c in row)


# TE-04
def test_quadtree_region_color_is_average(backend, data_image):
    img = data_image("blocks")
    for r in backend.generate_regions(corners(img), img, "QUADTREE"):
        assert r.color == pytest.approx(backend.get_rectangle_average_color(r.vertices, img), abs=1e-12)


# TE-05
def test_quadtree_uniform_image_is_one_region(backend):
    img = solid_image(50, 30, (10, 20, 30))
    regions = backend.generate_regions(corners(img), img, "QUADTREE")
    assert len(regions) == 1
    assert regions[0].vertices == corners(img)
    assert regions[0].color == pytest.approx(f((10, 20, 30)))


# TE-06
@pytest.mark.parametrize("size", [7, 9])
def test_quadtree_split_uses_round_half_to_even(backend, size):
    # the split is at round(size / 2) with Python's rounding: round(3.5) == 4 and round(4.5) == 4.
    # Black columns x < 4, white columns x >= 4: splitting exactly at x == 4 leaves four
    # single-coloured children, any other split line cuts through the edge and divides further.
    from helpers import image_from_rows
    img = image_from_rows([[(0, 0, 0) if x < 4 else (255, 255, 255) for x in range(size)] for _ in range(size)])
    regions = backend.generate_regions(corners(img), img, "QUADTREE")
    # children are pushed NW, NE, SE, SW and popped from the stack in reverse order
    assert [r.vertices for r in regions] == [
        [(0, 4), (4, 4), (4, size), (0, size)],          # SW
        [(4, 4), (size, 4), (size, size), (4, size)],    # SE
        [(4, 0), (size, 0), (size, 4), (4, 4)],          # NE
        [(0, 0), (4, 0), (4, 4), (0, 4)],                # NW
    ]


# TE-07
def test_quadtree_finer_where_image_is_detailed(backend, data_image):
    img = data_image("halves")     # left half flat, right half noise
    regions = backend.generate_regions(corners(img), img, "QUADTREE")
    left = sum(1 for r in regions if r.vertices[1][0] <= img.width // 2)
    right = len(regions) - left
    assert left <= 8 and right > 100 * left


# TE-08
# ---- Voronoi ---------------------------------------------------------------------------------
@pytest.mark.parametrize("name", ["photo", "blocks_large"])
def test_voronoi_matches_reference(backend, data_image, golden, name):
    img = data_image(name)
    ref = golden("voronoi_regions")[name]
    points = [tuple(p) for p in ref["points"]]
    regions = backend.generate_regions(points, img, "VORONOI")
    assert len(regions) == len(ref["regions"]) == len(points)
    for got, exp in zip(regions, ref["regions"]):
        assert got.kind == "voronoi"
        assert list(got.generator) == exp["generator"]
        assert got.color == pytest.approx(tuple(exp["color"]), abs=1e-12)
        assert polygons_close(got.vertices, exp["vertices"], tol=1), (got.generator, got.vertices, exp["vertices"])


# TE-09
@pytest.mark.parametrize("name", ["photo", "blocks_large"])
def test_voronoi_regions_follow_input_order_and_cover_image(backend, data_image, golden, name):
    img = data_image(name)
    points = [tuple(p) for p in golden("voronoi_regions")[name]["points"]]
    regions = backend.generate_regions(points, img, "VORONOI")
    assert [r.generator for r in regions] == points          # one region per point, same order
    for r in regions:
        assert r.color == backend.get_point_color(img, r.generator)
        assert all(0 <= x <= img.width and 0 <= y <= img.height for x, y in r.vertices)
    total = sum(shoelace_area(normalize_polygon(r.vertices)) for r in regions)
    assert total == pytest.approx(img.width * img.height, rel=0.01)


# TE-10
def test_voronoi_region_contains_its_generator(backend, data_image, golden):
    img = data_image("photo")
    points = [tuple(p) for p in golden("voronoi_regions")["photo"]["points"]]
    for r in backend.generate_regions(points, img, "VORONOI"):
        poly = normalize_polygon(r.vertices)
        gx, gy = r.generator
        for i in range(len(poly)):
            (x1, y1), (x2, y2) = poly[i], poly[(i + 1) % len(poly)]
            assert (x2 - x1) * (gy - y1) - (y2 - y1) * (gx - x1) >= -1.5 * max(abs(x2 - x1), abs(y2 - y1))


# ---- Delaunay --------------------------------------------------------------------------------
def triangle_set(regions):
    return {tuple(sorted(tuple(v) for v in r.vertices)) for r in regions}


# TE-11
@pytest.mark.parametrize("tess", ["DELAUNAY_FAST", "DELAUNAY_BETTER_COLORS"])
@pytest.mark.parametrize("name", ["blocks", "blocks_large", "photo"])
def test_delaunay_triangles_match_reference(backend, data_image, golden, tess, name):
    img = data_image(name)
    ref = golden("delaunay_regions")[name]
    regions = backend.generate_regions([tuple(p) for p in ref["points"]], img, tess)
    assert all(r.kind == "delaunay" and len(r.vertices) == 3 for r in regions)
    assert len(regions) == len(ref["regions"])
    assert triangle_set(regions) == {tuple(sorted(tuple(v) for v in r["vertices"])) for r in ref["regions"]}


# TE-12
@pytest.mark.parametrize("name", ["blocks", "blocks_large"])
def test_delaunay_better_colors_match_reference(backend, data_image, golden, name):
    img = data_image(name)
    ref = golden("delaunay_regions")[name]
    assert ref["colors_exact"]
    regions = backend.generate_regions([tuple(p) for p in ref["points"]], img, "DELAUNAY_BETTER_COLORS")
    expected = {tuple(sorted(tuple(v) for v in r["vertices"])): tuple(r["color"]) for r in ref["regions"]}
    for r in regions:
        assert r.color == pytest.approx(expected[tuple(sorted(r.vertices))], abs=1e-12)


# TE-13
@pytest.mark.parametrize("tess", ["DELAUNAY_FAST", "DELAUNAY_BETTER_COLORS"])
def test_delaunay_colors_come_from_the_triangle(backend, data_image, golden, tess):
    img = data_image("photo")
    ref = golden("delaunay_regions")["photo"]
    backend.seed(2)
    for r in backend.generate_regions([tuple(p) for p in ref["points"]], img, tess):
        assert tuple(round(c * 255) for c in r.color) in triangle_pixels(r.vertices, img)


# TE-14
def test_delaunay_covers_image_including_corners(backend, data_image, golden):
    img = data_image("blocks_large")
    pts = [tuple(p) for p in golden("delaunay_regions")["blocks_large"]["points"]]
    regions = backend.generate_regions(pts, img, "DELAUNAY_BETTER_COLORS")
    vertices = {tuple(v) for r in regions for v in r.vertices}
    assert vertices == set(pts) | {(0, 0), (img.width - 1, 0), (0, img.height - 1), (img.width - 1, img.height - 1)}
    total = sum(shoelace_area(r.vertices) for r in regions)
    assert total == pytest.approx((img.width - 1) * (img.height - 1))


# TE-15
def test_delaunay_fast_is_seeded(backend, data_image, golden):
    img = data_image("photo")
    pts = [tuple(p) for p in golden("delaunay_regions")["photo"]["points"]]
    backend.seed(9)
    a = backend.generate_regions(pts, img, "DELAUNAY_FAST")
    backend.seed(9)
    b = backend.generate_regions(pts, img, "DELAUNAY_FAST")
    assert [(r.vertices, r.color) for r in a] == [(r.vertices, r.color) for r in b]


# TE-16
def test_delaunay_handles_duplicate_and_collinear_points(backend, data_image):
    img = data_image("blocks")
    pts = [(10, 10), (10, 10), (20, 10), (30, 10), (40, 10), (25, 30)]
    regions = backend.generate_regions(pts, img, "DELAUNAY_BETTER_COLORS")
    for r in regions:
        assert shoelace_area(r.vertices) > 0
    assert sum(shoelace_area(r.vertices) for r in regions) == pytest.approx((img.width - 1) * (img.height - 1))
