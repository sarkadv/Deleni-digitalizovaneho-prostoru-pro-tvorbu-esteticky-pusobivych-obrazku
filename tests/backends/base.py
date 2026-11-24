"""
Backend interface shared by the Python and the C implementation.

Tests talk only to this interface. A backend converts the plain data types below
to whatever its implementation uses, calls the real code and converts the result back.
Backends contain no checking logic.

Plain data types used across the interface:
    point   -> tuple (x, y)
    color   -> tuple (r, g, b) of floats 0-1
    image   -> RGBImage (row-major RGB bytes)
    region  -> Region
Names of tessellations / distributions / effects are the enum member names
(e.g. "VORONOI", "UNIFORM", "GRID_ONE_COLOR").
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional

Point = tuple
Color = tuple

TESSELLATIONS = ["VORONOI", "DELAUNAY_FAST", "DELAUNAY_BETTER_COLORS", "QUADTREE"]
DISTRIBUTIONS = ["UNIFORM", "LAPLACE_AREA", "LAPLACE_LENGTH", "LAPLACE_GRADIENT",
                 "QUADTREE", "ERROR", "NORMAL_THIRDS", "MITCHELL"]
EFFECTS = ["BASIC", "GRID_ONE_COLOR", "GRID_COLORFUL", "MULTIPLE_SHAPES",
           "RECTANGLE_WITH_OVAL", "GRADIENTS", "PAPER"]

# region kind produced by each tessellation
REGION_KIND = {"VORONOI": "voronoi", "DELAUNAY_FAST": "delaunay",
               "DELAUNAY_BETTER_COLORS": "delaunay", "QUADTREE": "quadtree"}


@dataclass(frozen=True)
class RGBImage:
    width: int
    height: int
    data: bytes  # width * height * 3 bytes, row-major

    def pixel(self, x: int, y: int) -> tuple:
        i = (y * self.width + x) * 3
        return self.data[i], self.data[i + 1], self.data[i + 2]


@dataclass(frozen=True)
class RGBAImage:
    width: int
    height: int
    data: bytes  # width * height * 4 bytes, row-major, in the byte order the program saves to PNG

    def pixel(self, x: int, y: int) -> tuple:
        i = (y * self.width + x) * 4
        return tuple(self.data[i:i + 4])


@dataclass
class Region:
    kind: str                      # "voronoi" | "delaunay" | "quadtree"
    vertices: list                 # list of points
    color: Color                   # base colour
    generator: Optional[Point] = None   # voronoi regions only

    def to_json(self) -> dict:
        d = {"kind": self.kind, "vertices": [list(v) for v in self.vertices], "color": list(self.color)}
        if self.generator is not None:
            d["generator"] = list(self.generator)
        return d

    @staticmethod
    def from_json(d: dict) -> "Region":
        return Region(d["kind"], [tuple(v) for v in d["vertices"]], tuple(d["color"]),
                      tuple(d["generator"]) if "generator" in d else None)


class Backend(ABC):
    """Every method mirrors one function / class method of the original program."""

    name: str = "abstract"

    # ---- program-level -------------------------------------------------------------
    @abstractmethod
    def seed(self, value: int) -> None:
        """Seed every random generator the implementation uses."""

    @abstractmethod
    def tessellation_labels(self) -> dict:
        """{member name: GUI label} in declaration order (TessellationType)."""

    @abstractmethod
    def distribution_labels(self) -> dict:
        """{member name: GUI label} in declaration order (DistributionType)."""

    @abstractmethod
    def effect_labels(self) -> dict:
        """{member name: GUI label} in declaration order (EffectType)."""

    @abstractmethod
    def load_image(self, path: str) -> RGBImage:
        """Open an input image the way the GUI does (EXIF orientation applied, converted to RGB)."""

    @abstractmethod
    def save_png(self, image: RGBAImage, path: str) -> None:
        """Save a generated image the way the result window does."""

    # ---- util/convolution ------------------------------------------------------------
    @abstractmethod
    def convolute(self, matrix: list, kernel: list) -> list: ...

    @abstractmethod
    def create_convolution_padding(self, matrix: list) -> list: ...

    @abstractmethod
    def separate_color_channels(self, image: RGBImage) -> tuple: ...

    @abstractmethod
    def convolution_kernels(self) -> dict:
        """{"LAPLACE": matrix, "GAUSSIAN": matrix}"""

    # ---- util/color_utils ------------------------------------------------------------
    @abstractmethod
    def color_int_to_float(self, color: tuple) -> Color: ...

    @abstractmethod
    def find_complementary_color(self, color: Color) -> Color: ...

    @abstractmethod
    def get_point_color(self, image: RGBImage, point: Point) -> Color: ...

    @abstractmethod
    def find_image_mode_color(self, image: RGBImage) -> Color: ...

    @abstractmethod
    def find_points_average_color(self, image: RGBImage, points: list) -> Color: ...

    @abstractmethod
    def find_points_most_common_colors(self, image: RGBImage, points: list, count: int = 1) -> list: ...

    @abstractmethod
    def get_rectangle_average_color(self, vertices: list, image: RGBImage) -> Color: ...

    @abstractmethod
    def get_rectangle_color_standard_deviation(self, vertices: list, image: RGBImage,
                                               average_color: Color) -> float: ...

    @abstractmethod
    def get_colors_difference(self, color1: Color, color2: Color) -> float: ...

    @abstractmethod
    def get_colors_ratio(self, image: RGBImage, points: list, color1: Color, color2: Color) -> float: ...

    # ---- util/geometry_utils + geometry/point_2d ----------------------------------------
    @abstractmethod
    def is_point_in_image(self, image: RGBImage, point: Point) -> bool: ...

    @abstractmethod
    def find_rectangle_points(self, vertices: list) -> tuple: ...

    @abstractmethod
    def find_points_in_polygon(self, vertices: list, limit: int, image: RGBImage) -> list: ...

    @abstractmethod
    def crop_polygon_by_bounds(self, bounds: list, vertices: list) -> list: ...

    @abstractmethod
    def polygon_area(self, points: list) -> float:
        """Area of the polygon built from the points (get_polygon_from_points(...).area)."""

    @abstractmethod
    def random_point_in_polygon(self, vertices: list, excluded: Point = None) -> Optional[Point]:
        """Random integer point strictly inside, different from `excluded`; None if there is none."""

    @abstractmethod
    def find_polygon_centroid(self, vertices: list) -> Point: ...

    @abstractmethod
    def find_polygon_longest_side(self, vertices: list) -> tuple: ...

    @abstractmethod
    def split_polygon(self, vertices: list) -> list: ...

    @abstractmethod
    def remove_similar_points(self, points: list, min_distance: int) -> list: ...

    @abstractmethod
    def euclidean_distance(self, p: Point, q: Point) -> float: ...

    @abstractmethod
    def line_center(self, p: Point, q: Point) -> Point: ...

    # ---- point_generator / tessellation_generator / visualizer -------------------------
    @abstractmethod
    def generate_points(self, image: RGBImage, distribution: str,
                        x_min: int, x_max: int, y_min: int, y_max: int) -> list:
        """PointGenerator(image, distribution, x_min, x_max, y_min, y_max).generate_points()"""

    @abstractmethod
    def generate_regions(self, points: list, image: RGBImage, tessellation: str) -> list:
        """TesellationGenerator(points, image, tessellation).generate_regions()"""

    @abstractmethod
    def create_image(self, image: RGBImage, regions: list, effect: str) -> RGBAImage:
        """Visualizer(image, regions, effect).create_image()"""

    @abstractmethod
    def write_points_to_file(self, points: list, workdir: str) -> str:
        """util.file_writer.write_points_to_file run with `workdir` as the current directory.
        Returns the path the program reports (relative to workdir)."""

    # ---- whole pipeline, as Controller.generate() runs it ---------------------------------
    def stylize(self, image: RGBImage, tessellation: str, distribution: str, effect: str) -> RGBAImage:
        points = self.generate_points(image, distribution, 1, image.width, 1, image.height)
        regions = self.generate_regions(points, image, tessellation)
        return self.create_image(image, regions, effect)
