"""Choosing the initial set of points (point_generator.py, distributions/).

Most distributions are random, so the tests check properties every correct result must have."""

import pytest

from helpers import solid_image, point_count_formula, min_pairwise_distance

W, H = 300, 200
PLAIN = solid_image(W, H, (0, 0, 0))
RANDOM_DISTRIBUTIONS = ["UNIFORM", "NORMAL_THIRDS", "ERROR"]


def gen(backend, img, dist, seed=1):
    backend.seed(seed)
    return backend.generate_points(img, dist, 1, img.width, 1, img.height)


def far_points(img):
    L = max(img.width, img.height) * 4
    return [(-L, -L), (L, -L), (L, L), (-L, L)]


# DI-01
def test_point_count_formula():
    # values used below; round() is Python's round-half-to-even
    assert point_count_formula(300, 200) == 1846
    assert point_count_formula(100, 80) == 1680
    assert point_count_formula(1000, 700) == 2048


# DI-02
@pytest.mark.parametrize("dist", RANDOM_DISTRIBUTIONS)
def test_random_distributions_are_seeded(backend, data_image, dist):
    img = data_image("blocks_large")
    assert gen(backend, img, dist, 7) == gen(backend, img, dist, 7)
    assert gen(backend, img, dist, 7) != gen(backend, img, dist, 8)


# DI-03
@pytest.mark.parametrize("dist", ["UNIFORM", "NORMAL_THIRDS", "LAPLACE_AREA", "LAPLACE_LENGTH",
                                  "LAPLACE_GRADIENT", "ERROR"])
def test_points_are_unique_integers(backend, data_image, dist):
    pts = gen(backend, data_image("blocks_large"), dist)
    assert all(isinstance(x, int) and isinstance(y, int) for x, y in pts)
    assert len(set(pts)) == len(pts)


# DI-04
# ---- uniform ----------------------------------------------------------------------------------
def test_uniform_bounds_and_count(backend):
    pts = gen(backend, PLAIN, "UNIFORM")
    assert all(1 <= x <= W - 1 and 1 <= y <= H - 1 for x, y in pts)   # upper bound exclusive
    n = point_count_formula(W, H)
    assert 0.7 * n <= len(pts) <= n


# DI-05
def test_uniform_respects_given_range(backend):
    backend.seed(2)
    pts = backend.generate_points(PLAIN, "UNIFORM", 10, 20, 5, 8)
    assert pts and all(10 <= x <= 19 and 5 <= y <= 7 for x, y in pts)


# DI-06
def test_uniform_removes_close_points(backend):
    # minimum distance int(min(w, h) / 100) = 2 -> points at distance <= 2 are removed
    assert min_pairwise_distance(gen(backend, PLAIN, "UNIFORM")) > 2


# DI-07
def test_uniform_is_spread_evenly(backend):
    pts = gen(backend, PLAIN, "UNIFORM", 3)
    for qx in (0, 1):
        for qy in (0, 1):
            q = sum(1 for x, y in pts if (x >= W / 2) == qx and (y >= H / 2) == qy) / len(pts)
            assert 0.21 <= q <= 0.29


# DI-08
# ---- normal distribution + rule of thirds ------------------------------------------------------
def test_normal_bounds_count_and_distance(backend):
    pts = gen(backend, PLAIN, "NORMAL_THIRDS")
    assert all(0 <= x < W and 0 <= y < H for x, y in pts)
    assert 0.5 * point_count_formula(W, H) <= len(pts) <= point_count_formula(W, H)
    assert min_pairwise_distance(pts) > 2


# DI-09
def test_normal_points_concentrate_around_thirds(backend):
    pts = gen(backend, PLAIN, "NORMAL_THIRDS", 4)
    frame = sum(1 for x, y in pts if x < 0.1 * W or x >= 0.9 * W or y < 0.1 * H or y >= 0.9 * H) / len(pts)
    center = sum(1 for x, y in pts if W / 3 <= x < 2 * W / 3 and H / 3 <= y < 2 * H / 3) / len(pts)
    # uniform points: frame ~0.35, center ~0.11
    assert frame < 0.2
    assert center > 0.17
    assert abs(sum(x for x, _ in pts) / len(pts) - W / 2) < 0.04 * W
    assert abs(sum(y for _, y in pts) / len(pts) - H / 2) < 0.04 * H


# DI-10
# ---- Mitchell's best candidate ----------------------------------------------------------------------
def test_mitchell(backend):
    img = solid_image(100, 80, (0, 0, 0))
    pts = gen(backend, img, "MITCHELL", 5)
    assert len(pts) == point_count_formula(100, 80)          # exactly the requested number
    assert len(set(pts)) == len(pts)
    assert all(1 <= x <= 99 and 1 <= y <= 79 for x, y in pts)
    # best-candidate sampling spreads points: no two points touch
    assert min_pairwise_distance(pts) >= 1.0
    backend.seed(5)
    uniform_like = backend.generate_points(img, "UNIFORM", 1, 100, 1, 80)
    assert min_pairwise_distance(pts) >= min_pairwise_distance(uniform_like)


# DI-11
@pytest.mark.parametrize("w,h", [(20, 10), (40, 30)])
def test_mitchell_on_tiny_image_fills_every_position(backend, w, h):
    # fewer possible positions than requested points: every position is used once
    img = solid_image(w, h, (0, 0, 0))
    assert point_count_formula(w, h) > (w - 1) * (h - 1)
    pts = gen(backend, img, "MITCHELL", 1)
    assert len(pts) == (w - 1) * (h - 1)
    assert set(pts) == {(x, y) for x in range(1, w) for y in range(1, h)}


# DI-12
# ---- Laplace operator -------------------------------------------------------------------------------
@pytest.mark.parametrize("dist", ["LAPLACE_AREA", "LAPLACE_LENGTH", "LAPLACE_GRADIENT"])
def test_laplace_is_deterministic_and_inside_image(backend, data_image, dist):
    img = data_image("photo")
    a = gen(backend, img, dist, 1)
    assert a == gen(backend, img, dist, 2)
    assert all(0 <= x < img.width and 0 <= y < img.height for x, y in a)


# DI-13
@pytest.mark.parametrize("dist", ["LAPLACE_AREA", "LAPLACE_LENGTH", "LAPLACE_GRADIENT"])
def test_laplace_close_to_reference(backend, data_image, golden, dist):
    """Edge pixels lie on a grid, where the triangulation is often not unique (four points on one
    circle), so points added later may differ. With a different valid triangulation the count stayed
    within 1 % and 93-100 % of the reference points were present."""
    img = data_image("photo")
    ref = {tuple(p) for p in golden("laplace_points")[dist]}
    pts = gen(backend, img, dist)
    assert 0.95 * len(ref) <= len(pts) <= 1.05 * len(ref)
    assert len(ref & set(pts)) >= 0.85 * len(ref)


# DI-14
@pytest.mark.parametrize("dist", ["LAPLACE_AREA", "LAPLACE_LENGTH", "LAPLACE_GRADIENT"])
def test_laplace_points_lie_on_detail(backend, data_image, dist):
    img = data_image("halves")     # left half flat, right half noise
    pts = gen(backend, img, dist)
    # column 47 is flat but next to the noise, so it is an edge too; nothing lies further left
    assert all(x >= 47 for x, _ in pts)


# DI-15
def test_laplace_min_distance(backend, data_image):
    img = data_image("blocks_large")   # min distance int(384 / 65) = 5
    for dist in ["LAPLACE_AREA", "LAPLACE_LENGTH", "LAPLACE_GRADIENT"]:
        assert min_pairwise_distance(gen(backend, img, dist)) > 5


# DI-16
# ---- splitting regions by error -----------------------------------------------------------------------
def test_error_on_plain_image_is_uniform_plus_far_points(backend):
    img = solid_image(200, 150, (90, 90, 90))
    starters = gen(backend, img, "UNIFORM", 6)
    assert gen(backend, img, "ERROR", 6) == starters + far_points(img)


# DI-17
def test_error_adds_points_where_image_varies(backend, data_image):
    img = data_image("halves")
    starters = gen(backend, img, "UNIFORM", 2)
    pts = gen(backend, img, "ERROR", 2)
    assert pts[:len(starters)] == starters
    assert pts[len(starters):len(starters) + 4] == far_points(img)
    added = pts[len(starters) + 4:]
    assert len(added) > 20
    assert sum(1 for x, _ in added if x >= 46) >= 0.9 * len(added)


# DI-18
@pytest.mark.parametrize("seed", range(10))
def test_error_adds_points_only_inside_image(backend, data_image, seed):
    # new points are drawn inside the region clipped to the image, also for regions
    # that became degenerate by rounding their vertices
    img = data_image("halves")
    pts = gen(backend, img, "ERROR", seed)
    far = far_points(img)
    assert all(0 <= x < img.width and 0 <= y < img.height for x, y in pts if (x, y) not in far)
