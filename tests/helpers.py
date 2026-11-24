"""Helper functions used by tests (independent of the implementation under test)."""

import math

from PIL import Image

from backends.base import RGBImage, RGBAImage


# ---- images --------------------------------------------------------------------------------
def load_png_rgb(path: str) -> RGBImage:
    img = Image.open(path).convert("RGB")
    return RGBImage(img.width, img.height, img.tobytes())


def load_png_rgba(path: str) -> RGBAImage:
    img = Image.open(path)
    assert img.mode == "RGBA", path
    return RGBAImage(img.width, img.height, img.tobytes())


def rgba_to_pil(image: RGBAImage) -> Image.Image:
    return Image.frombytes("RGBA", (image.width, image.height), image.data)


def solid_image(width: int, height: int, color: tuple) -> RGBImage:
    return RGBImage(width, height, bytes(color) * (width * height))


def image_from_rows(rows: list) -> RGBImage:
    """rows: list of rows, each a list of (r, g, b) tuples"""
    height, width = len(rows), len(rows[0])
    return RGBImage(width, height, bytes(c for row in rows for px in row for c in px))


def mean_abs_diff_rgb(a: RGBAImage, b: RGBImage) -> float:
    """Mean absolute difference of RGB channels between a generated image and an input image."""
    assert (a.width, a.height) == (b.width, b.height)
    total = 0
    n = a.width * a.height
    for i in range(n):
        for c in range(3):
            total += abs(a.data[4 * i + c] - b.data[3 * i + c])
    return total / (3 * n)


def opaque_fraction(image: RGBAImage) -> float:
    n = image.width * image.height
    return sum(1 for i in range(n) if image.data[4 * i + 3] == 255) / n


def differing_pixels(a: RGBAImage, b: RGBAImage) -> int:
    assert (a.width, a.height) == (b.width, b.height)
    n = a.width * a.height
    return sum(1 for i in range(n) if a.data[4 * i:4 * i + 4] != b.data[4 * i:4 * i + 4])


# ---- geometry ------------------------------------------------------------------------------
def shoelace_area(vertices: list) -> float:
    s = 0.0
    for i in range(len(vertices)):
        x1, y1 = vertices[i]
        x2, y2 = vertices[(i + 1) % len(vertices)]
        s += x1 * y2 - x2 * y1
    return abs(s) / 2


def normalize_polygon(vertices: list) -> tuple:
    """Canonical form of a polygon ring: closing duplicate and repeated consecutive points removed,
    counter-clockwise order, starting at the smallest vertex. Makes polygons comparable regardless
    of starting vertex and orientation."""
    pts = [tuple(v) for v in vertices]
    dedup = []
    for p in pts:
        if not dedup or dedup[-1] != p:
            dedup.append(p)
    while len(dedup) > 1 and dedup[0] == dedup[-1]:
        dedup.pop()
    if len(dedup) < 3:
        return tuple(sorted(dedup))
    s = sum(dedup[i][0] * dedup[(i + 1) % len(dedup)][1] - dedup[(i + 1) % len(dedup)][0] * dedup[i][1]
            for i in range(len(dedup)))
    if s < 0:
        dedup.reverse()
    k = dedup.index(min(dedup))
    return tuple(dedup[k:] + dedup[:k])


def polygons_close(a: list, b: list, tol: float = 1.0) -> bool:
    """Same polygon up to vertex order/orientation and a coordinate tolerance of `tol`."""
    na, nb = normalize_polygon(a), normalize_polygon(b)
    if len(na) != len(nb):
        return False
    n = len(na)
    for shift in range(n):
        if all(abs(na[i][0] - nb[(i + shift) % n][0]) <= tol and abs(na[i][1] - nb[(i + shift) % n][1]) <= tol
               for i in range(n)):
            return True
    return False


def min_pairwise_distance(points: list) -> float:
    """Exact minimum distance between two points of the list (sweep over x-sorted points)."""
    pts = sorted(points)
    best = math.inf
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            if pts[j][0] - pts[i][0] >= best:
                break
            best = min(best, math.dist(pts[i], pts[j]))
    return best


def point_count_formula(width: int, height: int) -> int:
    """Number of points requested by the uniform, normal and Mitchell distributions (thesis, ch. 5.9)."""
    return round(math.log((width * height * 100_000) ** 2, 1.05)) * 2
