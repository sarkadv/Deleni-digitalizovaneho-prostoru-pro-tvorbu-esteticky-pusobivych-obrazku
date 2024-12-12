from typing import Tuple

import cairo
from PIL import Image

from geometry.a_region import ARegion
from geometry.point_2d import Point2D
from util.color_utils import find_complementary_color
from util.image_drawer import draw_polygon


class DelaunayRegion(ARegion):
    def __init__(self, vertices: list[Point2D], base_color: Tuple[float, float, float]):
        super().__init__(vertices, base_color)

    def draw_grid(self, context: cairo.Context, border_width: float,
                  border_color_rgb: Tuple[float, float, float], colorful: bool) -> None:

        if len(self.get_vertices()) == 0:
            return

        # nakreslení obrysu
        if not colorful:
            # všechny obrysy stejná barva
            border_color = border_color_rgb
        else:
            # obrys každé oblasti může být jiný
            border_color = find_complementary_color(self.get_base_color())

        draw_polygon(context, self.get_vertices(), border_color, True)

    def draw_multiple_shapes(self, context: cairo.Context):
        pass

    def draw_rectangle_with_oval(self, context: cairo.Context, image: Image):
        pass
