from typing import Tuple

import cairo
from PIL import Image

from geometry.a_region import ARegion
from geometry.point_2d import Point2D


class DelaunayRegion(ARegion):
    def __init__(self, vertices: list[Point2D], base_color: Tuple[float, float, float]):
        super().__init__(vertices, base_color)

    def draw_multiple_shapes(self, context: cairo.Context):
        pass

    def draw_rectangle_with_oval(self, context: cairo.Context, image: Image):
        pass
