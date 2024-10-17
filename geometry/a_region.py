from typing import Tuple

import cairo

from abc import ABC, abstractmethod

from geometry.point_2d import *


class ARegion(ABC):
    def __init__(self, vertices: list[Point2D], base_color: Tuple[float, float, float, float]):
        self.__vertices = vertices
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

    @abstractmethod
    def draw_grid(self, context: cairo.Context, border_width: float,
                  border_color_rgb: Tuple[float, float, float]) -> None:

        pass

    def get_vertices(self) -> list[Point2D]:
        return self.__vertices

    def get_base_color(self) -> Tuple[float, float, float, float]:
        return self.__base_color

