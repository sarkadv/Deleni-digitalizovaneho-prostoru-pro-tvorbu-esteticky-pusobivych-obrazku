"""
Generates the reference data in tests/golden/ from the ORIGINAL PYTHON implementation.
The files are committed; both implementations are tested against them.

    python tests/tools/make_golden.py          (run from the Python project root)

Only deterministic results are stored exactly. Where the Python program itself is random,
the generator checks that the stored result does not depend on the seed.
"""

import hashlib
import json
import os
import random
import sys

TESTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(TESTS_DIR)
sys.path.insert(0, TESTS_DIR)

from backends import load_backend, Region                       # noqa: E402
from helpers import load_png_rgb, rgba_to_pil, mean_abs_diff_rgb, opaque_fraction   # noqa: E402
from test_image_io import SAMPLES                                # noqa: E402

GOLDEN = os.path.join(TESTS_DIR, "golden")
DATA = os.path.join(TESTS_DIR, "data")
b = load_backend("python", python_root=PROJECT_ROOT)


def img(name):
    return load_png_rgb(os.path.join(DATA, name + ".png"))


def dump(name, obj):
    with open(os.path.join(GOLDEN, name + ".json"), "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, separators=(",", ":"))
    print("  ", name + ".json")


def save_render(name, rgba):
    rgba_to_pil(rgba).save(os.path.join(GOLDEN, name + ".png"))
    print("  ", name + ".png")


# ---- exact predicates for choosing points in general position ---------------------------------------
def incircle(a, b_, c, d):
    """> 0 if d inside circle (a, b, c) for counter-clockwise a, b, c (exact integer arithmetic)."""
    rows = [(p[0] - d[0], p[1] - d[1]) for p in (a, b_, c)]
    m = [(x, y, x * x + y * y) for x, y in rows]
    return (m[0][0] * (m[1][1] * m[2][2] - m[2][1] * m[1][2])
            - m[0][1] * (m[1][0] * m[2][2] - m[2][0] * m[1][2])
            + m[0][2] * (m[1][0] * m[2][1] - m[2][0] * m[1][1]))


def general_position(points):
    """True if the Delaunay triangulation of the points is unique (no 4 points on an empty circle
    and no 3 collinear points on a triangle)."""
    from scipy.spatial import Delaunay
    tri = Delaunay(points)
    for s, nbrs in zip(tri.simplices, tri.neighbors):
        a, b_, c = (tuple(points[i]) for i in s)
        orient = (b_[0] - a[0]) * (c[1] - a[1]) - (b_[1] - a[1]) * (c[0] - a[0])
        if orient == 0:
            return False
        if orient < 0:
            b_, c = c, b_
        for n in nbrs:
            if n == -1:
                continue
            for i in tri.simplices[n]:
                d = tuple(points[i])
                if d not in (a, b_, c) and incircle(a, b_, c, d) == 0:
                    return False
    return True


def fixed_points(width, height, count, seed, extra):
    """Deterministic points away from the border, such that points + `extra` are in general position."""
    rnd = random.Random(seed)
    while True:
        pts = set()
        while len(pts) < count:
            pts.add((rnd.randint(2, width - 3), rnd.randint(2, height - 3)))
        pts = sorted(pts)
        if general_position(pts + extra):
            return pts


def seed_independent(fn, seeds=(1, 2, 3, 4, 5)):
    results = []
    for s in seeds:
        b.seed(s)
        results.append(fn())
    return all(r == results[0] for r in results), results[0]


def main():
    os.makedirs(GOLDEN, exist_ok=True)

    print("image decoding")
    dec = {}
    for name in SAMPLES:
        im = b.load_image(os.path.join(PROJECT_ROOT, "img_input", name))
        dec[name] = {"size": [im.width, im.height], "sha256": hashlib.sha256(im.data).hexdigest()}
    im = b.load_image(os.path.join(DATA, "photo.jpg"))
    dec["tests/data/photo.jpg"] = {"size": [im.width, im.height], "sha256": hashlib.sha256(im.data).hexdigest()}
    dump("image_decoding", dec)

    print("quadtree")
    quad = {}
    for name in ["blocks", "blocks_large", "photo", "gradient"]:
        im = img(name)
        pts = b.generate_points(im, "QUADTREE", 1, im.width, 1, im.height)
        quad[name] = [r.to_json() for r in b.generate_regions(pts, im, "QUADTREE")]
    dump("quadtree_regions", quad)

    print("voronoi")
    vor = {}
    for name, count, seed in [("photo", 60, 1), ("blocks_large", 80, 2)]:
        im = img(name)
        L = max(im.width, im.height) * 4
        far = [(-L, -L), (L, -L), (L, L), (-L, L)]
        pts = fixed_points(im.width, im.height, count, seed, far)
        regions = b.generate_regions(pts, im, "VORONOI")
        vor[name] = {"points": pts, "regions": [r.to_json() for r in regions]}
    dump("voronoi_regions", vor)

    print("delaunay")
    dela = {}
    for name, count, seed in [("blocks", 30, 3), ("blocks_large", 80, 4), ("photo", 60, 5)]:
        im = img(name)
        corners = [(0, 0), (im.width - 1, im.height - 1), (0, im.height - 1), (im.width - 1, 0)]
        s = seed
        while True:
            pts = fixed_points(im.width, im.height, count, s, corners)
            same, regions = seed_independent(
                lambda: [r.to_json() for r in b.generate_regions(pts, im, "DELAUNAY_BETTER_COLORS")])
            if same or name == "photo":
                break
            s += 100
        # photo colours depend on random tie-breaking -> only the triangles are exact
        dela[name] = {"points": pts, "regions": regions, "colors_exact": same}
    dump("delaunay_regions", dela)

    print("laplace distributions")
    lap = {}
    im = img("photo")
    for dist in ["LAPLACE_AREA", "LAPLACE_LENGTH", "LAPLACE_GRADIENT"]:
        lap[dist] = b.generate_points(im, dist, 1, im.width, 1, im.height)
    dump("laplace_points", lap)

    print("renders")
    for name in ["blocks", "blocks_large", "photo"]:
        im = img(name)
        regions = [Region.from_json(r) for r in quad[name]]
        for effect in ["BASIC", "GRID_ONE_COLOR", "GRID_COLORFUL", "RECTANGLE_WITH_OVAL"]:
            save_render(f"render_quadtree_{name}_{effect}", b.create_image(im, regions, effect))
    for name in ["blocks", "blocks_large"]:
        im = img(name)
        regions = [Region.from_json(r) for r in dela[name]["regions"]]
        for effect in ["BASIC", "GRID_ONE_COLOR", "GRID_COLORFUL"]:
            save_render(f"render_delaunay_{name}_{effect}", b.create_image(im, regions, effect))
    for name in ["photo", "blocks_large"]:
        im = img(name)
        regions = [Region.from_json(r) for r in vor[name]["regions"]]
        for effect in ["BASIC", "GRID_ONE_COLOR", "GRID_COLORFUL"]:
            save_render(f"render_voronoi_{name}_{effect}", b.create_image(im, regions, effect))
    # gradients: random tie-breaking inside Python -> stored for a tolerance comparison
    for kind, name in [("quadtree", "blocks_large"), ("delaunay", "blocks_large")]:
        im = img(name)
        src = quad[name] if kind == "quadtree" else dela[name]["regions"]
        regions = [Region.from_json(r) for r in src]
        same, render = seed_independent(lambda: b.create_image(im, regions, "GRADIENTS"))
        print("   gradients", kind, name, "seed independent:", same)
        save_render(f"render_{kind}_{name}_GRADIENTS", render)

    print("pipeline reference values")
    combos = {
        "VORONOI": (["UNIFORM", "NORMAL_THIRDS", "ERROR", "MITCHELL"],
                    ["BASIC", "GRID_ONE_COLOR", "GRID_COLORFUL", "GRADIENTS", "PAPER"]),
        "DELAUNAY_FAST": (["UNIFORM", "NORMAL_THIRDS", "LAPLACE_AREA", "LAPLACE_LENGTH", "LAPLACE_GRADIENT",
                           "MITCHELL"],
                          ["BASIC", "GRID_ONE_COLOR", "GRID_COLORFUL", "GRADIENTS", "PAPER"]),
        "DELAUNAY_BETTER_COLORS": (["UNIFORM", "NORMAL_THIRDS", "LAPLACE_AREA", "LAPLACE_LENGTH",
                                    "LAPLACE_GRADIENT", "MITCHELL"],
                                   ["BASIC", "GRID_ONE_COLOR", "GRID_COLORFUL", "GRADIENTS", "PAPER"]),
        "QUADTREE": (["QUADTREE"], ["BASIC", "GRID_ONE_COLOR", "GRID_COLORFUL", "GRADIENTS", "MULTIPLE_SHAPES",
                                    "RECTANGLE_WITH_OVAL"]),
    }
    im = img("photo")
    ref = {}
    points = {}     # same order of seeding as tests/test_pipeline.py: points once per distribution
    for tess, (dists, effects) in combos.items():
        for dist in dists:
            if dist not in points:
                b.seed(1)
                points[dist] = b.generate_points(im, dist, 1, im.width, 1, im.height)
            b.seed(1)
            regions = b.generate_regions(list(points[dist]), im, tess)
            for effect in effects:
                b.seed(1)
                out = b.create_image(im, regions, effect)
                key = f"{tess}/{dist}/{effect}"
                ref[key] = {"mean_abs_diff": round(mean_abs_diff_rgb(out, im), 3),
                            "opaque_fraction": round(opaque_fraction(out), 4), "regions": len(regions)}
                print("  ", key, ref[key])
    dump("pipeline_reference", ref)


if __name__ == "__main__":
    main()
