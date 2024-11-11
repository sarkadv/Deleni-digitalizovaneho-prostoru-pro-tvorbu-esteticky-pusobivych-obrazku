from typing import Tuple

import cairo

from geometry.a_region import ARegion
from geometry.point_2d import Point2D
from util.image_utils import find_complementary_color


class DelaunayRegion(ARegion):
    def __init__(self, vertices: list[Point2D], base_color: Tuple[float, float, float, float]):
        super().__init__(vertices, base_color)

    def draw_grid(self, context: cairo.Context, border_width: float,
                  border_color_rgb: Tuple[float, float, float], colorful: bool) -> None:

        if len(self.get_vertices()) == 0:
            return

        points = [(vertex.get_x(), vertex.get_y()) for vertex in self.get_vertices()]

        context.move_to(*points[0])  # přesunutí na první bod

        for point in points[1:]:    # nakreslení úseček mezi ostatními body
            context.line_to(*point)
        context.close_path()    # uzavření trojúhelníku

        # nakreslení obrysu
        if not colorful:
            context.set_source_rgb(*border_color_rgb)
        else:
            r, g, b, a = self.get_base_color()
            context.set_source_rgb(*find_complementary_color((r, g, b)))

        context.set_line_width(border_width)
        context.stroke()
