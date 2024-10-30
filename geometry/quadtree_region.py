from typing import Tuple

import cairo

from geometry.a_region import ARegion
from geometry.point_2d import Point2D


class QuadtreeRegion(ARegion):
    def __init__(self, vertices: list[Point2D], base_color: Tuple[float, float, float, float]):
        super().__init__(vertices, base_color)
        self.__children = [[None, None],
                           [None, None]]

    def draw_grid(self, context: cairo.Context, border_width: float,
                  border_color_rgb: Tuple[float, float, float]) -> None:
        pass

    def get_children(self):
        return self.__children

    def set_children(self, children: list[list['QuadtreeRegion']]):
        self.__children = children
