import math
from typing import Tuple

from geometry.a_region import *


class VoronoiRegion(ARegion):
    def __init__(self, vertices: list[Point], seed: Point, base_color: Tuple[float, float, float, float]):
        super().__init__(vertices)
        self.__generator = seed
        self.__base_color = base_color

    def draw_basic(self, context: cairo.Context) -> None:
        points = [(vertex.get_x(), vertex.get_y()) for vertex in self.get_vertices()]

        # nakreslení výplně
        context.set_source_rgba(*self.__base_color)
        context.move_to(*points[0])  # přesunutí na první bod

        for point in points[1:]:    # nakreslení úseček mezi ostatními body
            context.line_to(*point)
        context.close_path()    # uzavření polygonu

        context.fill_preserve()

        context.set_line_width(1)
        context.stroke()

    def draw_grid(self, context: cairo.Context, border_width: float,
                  border_color_rgb: Tuple[float, float, float]) -> None:

        points = [(vertex.get_x(), vertex.get_y()) for vertex in self.get_vertices()]

        context.move_to(*points[0])  # přesunutí na první bod

        for point in points[1:]:    # nakreslení úseček mezi ostatními body
            context.line_to(*point)
        context.close_path()    # uzavření polygonu

        # nakreslení obrysu
        context.set_source_rgb(*border_color_rgb)
        context.set_line_width(border_width)
        context.stroke()

        # nakreslení generátoru
        context.arc(self.__generator.get_x(), self.__generator.get_y(), border_width * 1.5, 0, 2 * math.pi)
        context.fill()

    def get_generator(self) -> Point:
        return self.__generator
