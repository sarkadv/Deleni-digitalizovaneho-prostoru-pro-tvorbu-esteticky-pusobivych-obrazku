"""Whole pipeline as Controller.generate runs it: points -> regions -> image, for every combination
of tessellation, point distribution and effect offered by the GUI."""

import pytest

from helpers import mean_abs_diff_rgb, opaque_fraction

VORONOI_DISTS = ["UNIFORM", "NORMAL_THIRDS", "ERROR", "MITCHELL"]
DELAUNAY_DISTS = ["UNIFORM", "NORMAL_THIRDS", "LAPLACE_AREA", "LAPLACE_LENGTH", "LAPLACE_GRADIENT", "MITCHELL"]
COMMON_EFFECTS = ["BASIC", "GRID_ONE_COLOR", "GRID_COLORFUL", "GRADIENTS", "PAPER"]
QUADTREE_EFFECTS = ["BASIC", "GRID_ONE_COLOR", "GRID_COLORFUL", "GRADIENTS", "MULTIPLE_SHAPES",
                    "RECTANGLE_WITH_OVAL"]

COMBOS = ([("VORONOI", d, e) for d in VORONOI_DISTS for e in COMMON_EFFECTS]
          + [(t, d, e) for t in ["DELAUNAY_FAST", "DELAUNAY_BETTER_COLORS"] for d in DELAUNAY_DISTS
             for e in COMMON_EFFECTS]
          + [("QUADTREE", "QUADTREE", e) for e in QUADTREE_EFFECTS])


def combo_param(t, d, e):
    return pytest.param(t, d, e, id=f"{t}-{d}-{e}")


_cache = {}


def regions_for(backend, img, tess, dist):
    """Points are generated once per distribution and regions once per tessellation (seed 1)."""
    pkey = (id(backend), dist)
    if pkey not in _cache:
        backend.seed(1)
        _cache[pkey] = backend.generate_points(img, dist, 1, img.width, 1, img.height)
    rkey = (id(backend), tess, dist)
    if rkey not in _cache:
        backend.seed(1)
        _cache[rkey] = backend.generate_regions(list(_cache[pkey]), img, tess)
    return _cache[rkey]


# PI-01
@pytest.mark.parametrize("tess,dist,effect", [combo_param(*c) for c in COMBOS])
def test_pipeline(backend, data_image, golden, tess, dist, effect):
    img = data_image("photo")
    regions = regions_for(backend, img, tess, dist)
    backend.seed(1)
    out = backend.create_image(img, regions, effect)

    assert (out.width, out.height) == (img.width, img.height)
    assert len(out.data) == 4 * img.width * img.height

    mad = mean_abs_diff_rgb(out, img)
    opaque = opaque_fraction(out)
    ref = golden("pipeline_reference")[f"{tess}/{dist}/{effect}"]
    # the result must stylise the picture about as faithfully as the reference program
    assert 0.5 * ref["mean_abs_diff"] - 1 <= mad <= 1.3 * ref["mean_abs_diff"] + 3, (mad, ref)
    assert abs(opaque - ref["opaque_fraction"]) <= 0.1, (opaque, ref)
    tolerance = 0.25 if dist.startswith("LAPLACE") or dist == "ERROR" else 0.15
    assert abs(len(regions) - ref["regions"]) <= tolerance * ref["regions"], (len(regions), ref)


# PI-02
def test_stylize_runs_whole_pipeline(backend, data_image):
    img = data_image("blocks_large")
    backend.seed(3)
    out = backend.stylize(img, "QUADTREE", "QUADTREE", "BASIC")
    assert (out.width, out.height) == (img.width, img.height)
    assert opaque_fraction(out) == 1.0
    assert mean_abs_diff_rgb(out, img) < 5
