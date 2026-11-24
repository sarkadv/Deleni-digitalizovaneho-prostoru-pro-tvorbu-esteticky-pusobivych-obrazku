"""
Backend for the original Python implementation. Only converts data and calls the program's code.
"""

import os
import random
import sys

from backends.base import Backend, RGBImage, RGBAImage, Region


class PythonBackend(Backend):
    name = "python"

    def __init__(self, python_root: str):
        self.root = os.path.abspath(python_root)
        if self.root not in sys.path:
            sys.path.insert(0, self.root)

        import numpy
        from PIL import Image, ImageOps
        from shapely import Polygon
        from enums.tessellation_type import TessellationType
        from enums.distribution_type import DistributionType
        from enums.effect_type import EffectType
        from geometry.point_2d import Point2D
        from geometry.voronoi_region import VoronoiRegion
        from geometry.delaunay_region import DelaunayRegion
        from geometry.quadtree_region import QuadtreeRegion
        from point_generator import PointGenerator
        from tessellation_generator import TesellationGenerator
        from visualizer import Visualizer
        from util import color_utils, geometry_utils, convolution, file_writer

        self._np = numpy
        self._Image, self._ImageOps, self._Polygon = Image, ImageOps, Polygon
        self._T, self._D, self._E = TessellationType, DistributionType, EffectType
        self._P = Point2D
        self._region_classes = {"voronoi": VoronoiRegion, "delaunay": DelaunayRegion, "quadtree": QuadtreeRegion}
        self._PointGenerator, self._TesellationGenerator, self._Visualizer = \
            PointGenerator, TesellationGenerator, Visualizer
        self._color, self._geom, self._conv, self._fw = color_utils, geometry_utils, convolution, file_writer
        self._pil_cache = {}

    # ---- conversions -------------------------------------------------------------------
    def _pil(self, image: RGBImage):
        key = id(image)
        cached = self._pil_cache.get(key)
        if cached is None or cached[0] is not image:
            if len(self._pil_cache) > 64:
                self._pil_cache.clear()
            cached = (image, self._Image.frombytes("RGB", (image.width, image.height), image.data))
            self._pil_cache[key] = cached
        return cached[1]

    def _pt(self, p):
        return self._P(p[0], p[1])

    def _pts(self, points):
        return [self._P(p[0], p[1]) for p in points]

    @staticmethod
    def _tup(p):
        return None if p is None else (p.get_x(), p.get_y())

    def _tups(self, points):
        return [(p.get_x(), p.get_y()) for p in points]

    @staticmethod
    def _col(c):
        return tuple(float(v) for v in c)

    def _to_region(self, r) -> Region:
        kind = {"VoronoiRegion": "voronoi", "DelaunayRegion": "delaunay",
                "QuadtreeRegion": "quadtree"}[type(r).__name__]
        gen = self._tup(r.get_generator()) if kind == "voronoi" else None
        return Region(kind, self._tups(r.get_vertices()), self._col(r.get_base_color()), gen)

    def _from_region(self, r: Region):
        cls = self._region_classes[r.kind]
        if r.kind == "voronoi":
            return cls(self._pts(r.vertices), self._pt(r.generator), tuple(r.color))
        return cls(self._pts(r.vertices), tuple(r.color))

    # ---- program-level -----------------------------------------------------------------
    def seed(self, value):
        random.seed(value)
        self._np.random.seed(value)

    def tessellation_labels(self):
        return self._T.dict()

    def distribution_labels(self):
        return self._D.dict()

    def effect_labels(self):
        return self._E.dict()

    def load_image(self, path):
        # same steps as gui.controller.Controller.set_image_file
        img = self._Image.open(path)
        img = self._ImageOps.exif_transpose(img)
        img = img.convert("RGB")
        return RGBImage(img.width, img.height, img.tobytes())

    def save_png(self, image, path):
        # same call as gui.result_window.ResultWindow.__save_file
        self._Image.frombytes("RGBA", (image.width, image.height), image.data).save(path, "PNG")

    # ---- convolution -------------------------------------------------------------------
    def convolute(self, matrix, kernel):
        return self._conv.convolute(matrix, kernel)

    def create_convolution_padding(self, matrix):
        return self._conv.create_convolution_padding(matrix)

    def separate_color_channels(self, image):
        return self._conv.separate_color_channels(self._pil(image))

    def convolution_kernels(self):
        return {"LAPLACE": self._conv.LAPLACE_CONVOLUTION_MATRIX,
                "GAUSSIAN": self._conv.GAUSSIAN_CONVOLUTION_MATRIX}

    # ---- colour ------------------------------------------------------------------------
    def color_int_to_float(self, color):
        return self._col(self._color.color_int_to_float(color))

    def find_complementary_color(self, color):
        return self._col(self._color.find_complementary_color(color))

    def get_point_color(self, image, point):
        return self._col(self._color.get_point_color(self._pil(image), self._pt(point)))

    def find_image_mode_color(self, image):
        return self._col(self._color.find_image_mode_color(self._pil(image)))

    def find_points_average_color(self, image, points):
        return self._col(self._color.find_points_average_color(self._pil(image), self._pts(points)))

    def find_points_most_common_colors(self, image, points, count=1):
        res = self._color.find_points_most_common_colors(self._pil(image), self._pts(points), count)
        return [self._col(c) for c in res]

    def get_rectangle_average_color(self, vertices, image):
        return self._col(self._color.get_rectangle_average_color(self._pts(vertices), self._pil(image)))

    def get_rectangle_color_standard_deviation(self, vertices, image, average_color):
        return float(self._color.get_rectangle_color_standard_deviation(
            self._pts(vertices), self._pil(image), tuple(average_color)))

    def get_colors_difference(self, color1, color2):
        return float(self._color.get_colors_difference(color1, color2))

    def get_colors_ratio(self, image, points, color1, color2):
        return float(self._color.get_colors_ratio(self._pil(image), self._pts(points), color1, color2))

    # ---- geometry ----------------------------------------------------------------------
    def is_point_in_image(self, image, point):
        return bool(self._geom.is_point_in_image(self._pil(image), self._pt(point)))

    def find_rectangle_points(self, vertices):
        xs, ys = self._geom.find_rectangle_points(self._pts(vertices))
        return list(xs), list(ys)

    def find_points_in_polygon(self, vertices, limit, image):
        return self._tups(self._geom.find_points_in_polygon(self._pts(vertices), limit, self._pil(image)))

    def crop_polygon_by_bounds(self, bounds, vertices):
        res = self._geom.crop_polygon_by_bounds([tuple(b) for b in bounds], [tuple(v) for v in vertices])
        return [(float(x), float(y)) for x, y in res]

    def polygon_area(self, points):
        return float(self._geom.get_polygon_from_points(self._pts(points)).area)

    def random_point_in_polygon(self, vertices, excluded=None):
        polygon = self._Polygon([tuple(v) for v in vertices])
        return self._tup(self._geom.random_point_in_polygon(polygon, None if excluded is None else self._pt(excluded)))

    def find_polygon_centroid(self, vertices):
        return self._tup(self._geom.find_polygon_centroid(self._pts(vertices)))

    def find_polygon_longest_side(self, vertices):
        a, b = self._geom.find_polygon_longest_side(self._pts(vertices))
        return self._tup(a), self._tup(b)

    def split_polygon(self, vertices):
        return [self._tups(poly) for poly in self._geom.split_polygon(self._pts(vertices))]

    def remove_similar_points(self, points, min_distance):
        return self._tups(self._geom.remove_similar_points(self._pts(points), min_distance))

    def euclidean_distance(self, p, q):
        return float(self._pt(p).euclidean_distance(self._pt(q)))

    def line_center(self, p, q):
        return self._tup(self._pt(p).line_center(self._pt(q)))

    # ---- pipeline parts ----------------------------------------------------------------
    def generate_points(self, image, distribution, x_min, x_max, y_min, y_max):
        gen = self._PointGenerator(self._pil(image), self._D[distribution], x_min, x_max, y_min, y_max)
        return self._tups(gen.generate_points())

    def generate_regions(self, points, image, tessellation):
        gen = self._TesellationGenerator(self._pts(points), self._pil(image), self._T[tessellation])
        return [self._to_region(r) for r in gen.generate_regions()]

    def create_image(self, image, regions, effect):
        vis = self._Visualizer(self._pil(image), [self._from_region(r) for r in regions], self._E[effect])
        out = vis.create_image()
        return RGBAImage(out.width, out.height, out.tobytes())

    def write_points_to_file(self, points, workdir):
        old = os.getcwd()
        os.chdir(workdir)
        try:
            return self._fw.write_points_to_file(self._pts(points))
        finally:
            os.chdir(old)
