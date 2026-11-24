"""Drawing regions with the chosen effect (visualizer.py, geometry/*_region.py, util/image_drawer.py)."""

import pytest

from backends import Region
from helpers import differing_pixels, solid_image, mean_abs_diff_rgb

EXACT = ([("quadtree", name, eff) for name in ["blocks", "blocks_large", "photo"]
          for eff in ["BASIC", "GRID_ONE_COLOR", "GRID_COLORFUL", "RECTANGLE_WITH_OVAL"]]
         + [("delaunay", name, eff) for name in ["blocks", "blocks_large"]
            for eff in ["BASIC", "GRID_ONE_COLOR", "GRID_COLORFUL"]]
         + [("voronoi", name, eff) for name in ["photo", "blocks_large"]
            for eff in ["BASIC", "GRID_ONE_COLOR", "GRID_COLORFUL"]])


def reference_regions(golden, kind, name):
    if kind == "quadtree":
        src = golden("quadtree_regions")[name]
    elif kind == "delaunay":
        src = golden("delaunay_regions")[name]["regions"]
    else:
        src = golden("voronoi_regions")[name]["regions"]
    return [Region.from_json(r) for r in src]


# RE-01
@pytest.mark.parametrize("kind,name,effect", EXACT)
def test_render_matches_reference_exactly(backend, data_image, golden, golden_png, kind, name, effect):
    img = data_image(name)
    out = backend.create_image(img, reference_regions(golden, kind, name), effect)
    expected = golden_png(f"render_{kind}_{name}_{effect}")
    assert (out.width, out.height) == (expected.width, expected.height)
    assert differing_pixels(out, expected) == 0


# RE-02
@pytest.mark.parametrize("kind", ["quadtree", "delaunay"])
def test_gradients_match_reference(backend, data_image, golden, golden_png, kind):
    img = data_image("blocks_large")
    backend.seed(1)
    out = backend.create_image(img, reference_regions(golden, kind, "blocks_large"), "GRADIENTS")
    expected = golden_png(f"render_{kind}_blocks_large_GRADIENTS")
    # the split of each region may differ by a pixel between geometry libraries
    assert differing_pixels(out, expected) <= 0.02 * img.width * img.height


# RE-03
def test_output_has_image_size_and_is_transparent_without_regions(backend, data_image):
    img = data_image("photo")
    out = backend.create_image(img, [], "BASIC")
    assert (out.width, out.height) == (img.width, img.height)
    assert out.data == bytes(4 * img.width * img.height)


# RE-04
def test_basic_fills_region_with_base_color(backend):
    img = solid_image(20, 10, (0, 0, 0))
    region = Region("quadtree", [(0, 0), (20, 0), (20, 10), (0, 10)], (1.0, 0.5, 0.0))
    out = backend.create_image(img, [region], "BASIC")
    assert out.pixel(10, 5) == (255, 128, 0, 255)
    assert out.pixel(0, 0) == (255, 128, 0, 255)


# RE-05
def test_regions_with_fewer_than_three_vertices_are_not_drawn(backend, data_image):
    img = data_image("blocks")
    tri = Region("delaunay", [(5, 5), (40, 8), (20, 40)], (0.2, 0.4, 0.6))
    degenerate = [Region("delaunay", [(1, 1), (60, 40)], (1.0, 0.0, 0.0)),
                  Region("voronoi", [], (1.0, 0.0, 0.0), (3, 3))]
    for effect in ["BASIC", "GRID_ONE_COLOR", "GRID_COLORFUL", "PAPER"]:
        backend.seed(4)
        alone = backend.create_image(img, [tri], effect)
        backend.seed(4)
        mixed = backend.create_image(img, degenerate + [tri], effect)
        assert mixed.data == alone.data, effect


# RE-06
def test_paper_lightens_regions_and_adds_dark_noise(backend, data_image, golden):
    img = data_image("blocks_large")
    regions = reference_regions(golden, "quadtree", "blocks_large")
    lightened = [Region(r.kind, r.vertices,
                        (min(r.color[0] + 0.15, 1), min(r.color[1] + 0.15, 1), min(r.color[2] + 0.15 * 5 / 6, 1)))
                 for r in regions]
    backend.seed(3)
    paper = backend.create_image(img, regions, "PAPER")
    plain = backend.create_image(img, lightened, "BASIC")
    ratios = []
    for i in range(0, img.width * img.height * 4, 4):
        assert paper.data[i + 3] == plain.data[i + 3]
        for c in range(3):
            if plain.data[i + c] >= 40:
                ratios.append(paper.data[i + c] / plain.data[i + c])
    # noise is black with alpha between 0.1 and 0.2 -> every channel darkened to 80-90 %
    assert min(ratios) >= 0.78 and max(ratios) <= 1.0
    assert sum(1 for r in ratios if 0.78 <= r <= 0.92) >= 0.95 * len(ratios)


# RE-07
def test_paper_noise_is_random_but_seeded(backend, data_image, golden):
    img = data_image("blocks")
    regions = reference_regions(golden, "quadtree", "blocks")
    backend.seed(1)
    a = backend.create_image(img, regions, "PAPER")
    backend.seed(1)
    b = backend.create_image(img, regions, "PAPER")
    backend.seed(2)
    c = backend.create_image(img, regions, "PAPER")
    assert a.data == b.data
    assert a.data != c.data


# RE-08
def test_paper_on_tiny_image(backend):
    # images under 100 pixels: the noise particles are 1 pixel large
    img = solid_image(9, 9, (100, 150, 200))
    region = Region("quadtree", [(0, 0), (9, 0), (9, 9), (0, 9)], (0.4, 0.6, 0.8))
    lightened = Region("quadtree", region.vertices, (0.55, 0.75, 0.8 + 0.125))
    backend.seed(2)
    paper = backend.create_image(img, [region], "PAPER")
    plain = backend.create_image(img, [lightened], "BASIC")
    assert (paper.width, paper.height) == (9, 9)
    # 9 // 1 = 9 particle columns and rows -> every pixel is darkened by the noise
    for i in range(0, 9 * 9 * 4, 4):
        for c in range(3):
            assert 0.78 * plain.data[i + c] <= paper.data[i + c] <= 0.92 * plain.data[i + c] + 1


# RE-09
@pytest.mark.parametrize("w,h", [(1, 1), (10000, 1), (1, 10000)])
def test_paper_on_images_thinner_than_a_noise_particle(backend, w, h):
    img = solid_image(w, h, (100, 150, 200))
    region = Region("quadtree", [(0, 0), (w, 0), (w, h), (0, h)], (0.4, 0.6, 0.8))
    backend.seed(3)
    out = backend.create_image(img, [region], "PAPER")
    assert (out.width, out.height) == (w, h)


# RE-10
def test_multiple_shapes(backend, data_image, golden):
    img = data_image("blocks_large")
    regions = reference_regions(golden, "quadtree", "blocks_large")
    backend.seed(5)
    a = backend.create_image(img, regions, "MULTIPLE_SHAPES")
    backend.seed(5)
    assert backend.create_image(img, regions, "MULTIPLE_SHAPES").data == a.data
    backend.seed(6)
    assert backend.create_image(img, regions, "MULTIPLE_SHAPES").data != a.data

    n = img.width * img.height
    transparent = sum(1 for i in range(n) if a.data[4 * i + 3] == 0)
    # rectangles cover their region fully, ovals ~79 %, triangles and rhombi 50 %
    assert 0.15 * n <= transparent <= 0.45 * n
    colors = {tuple(round(v * 255) for v in r.color) for r in regions}
    opaque = [tuple(a.data[4 * i:4 * i + 3]) for i in range(n) if a.data[4 * i + 3] == 255]
    assert sum(1 for p in opaque if p in colors) >= 0.9 * len(opaque)


# RE-11
def test_multiple_shapes_small_image_does_not_fail(backend, data_image, golden):
    # small images produce quadtree regions with zero width or height
    img = data_image("photo")
    regions = reference_regions(golden, "quadtree", "photo")
    assert any(r.vertices[0][0] == r.vertices[1][0] or r.vertices[0][1] == r.vertices[3][1] for r in regions)
    for s in range(3):
        backend.seed(s)
        out = backend.create_image(img, regions, "MULTIPLE_SHAPES")
        assert (out.width, out.height) == (img.width, img.height)


# RE-12
def test_gradients_on_photo_are_closer_to_input_than_flat_colors(backend, data_image, golden):
    # each region gets two colours of its own halves -> follows the picture better than one colour
    img = data_image("photo")
    regions = reference_regions(golden, "voronoi", "photo")
    backend.seed(1)
    grad = mean_abs_diff_rgb(backend.create_image(img, regions, "GRADIENTS"), img)
    basic = mean_abs_diff_rgb(backend.create_image(img, regions, "BASIC"), img)
    assert grad < basic < 35
