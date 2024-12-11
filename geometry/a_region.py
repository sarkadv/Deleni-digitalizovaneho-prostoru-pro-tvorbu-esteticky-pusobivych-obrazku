from typing import Tuple

import cairo

from abc import ABC, abstractmethod

from PIL import Image

from geometry.point_2d import *
from util.image_drawer import draw_polygon


class ARegion(ABC):
    def __init__(self, vertices: list[Point2D], base_color: Tuple[float, float, float]):
        self.__vertices = vertices
        self.__base_color = base_color

    def draw_basic(self, context: cairo.Context) -> None:
        if len(self.get_vertices()) == 0:
            return

        draw_polygon(context, self.__vertices, self.__base_color, False)

    @abstractmethod
    def draw_grid(self, context: cairo.Context, border_width: float,
                  border_color_rgb: Tuple[float, float, float], colorful: bool) -> None:

        pass

    @abstractmethod
    def draw_multiple_shapes(self, context: cairo.Context):
        pass

    @abstractmethod
    def draw_rectangle_with_oval(self, context: cairo.Context, image: Image):
        pass

    def get_vertices(self) -> list[Point2D]:
        return self.__vertices

    def get_base_color(self) -> Tuple[float, float, float]:
        return self.__base_color

    def get_x_axis_length(self) -> int:
        min_x = min([point.get_x() for point in self.__vertices])
        max_x = max([point.get_x() for point in self.__vertices])

        return max_x - min_x

    def get_y_axis_length(self) -> int:
        min_y = min([point.get_y() for point in self.__vertices])
        max_y = max([point.get_y() for point in self.__vertices])

        return max_y - min_y

    def set_base_color(self, base_color: Tuple[float, float, float]) -> None:
        if 0.0 <= all(base_color) <= 1.0:
            self.__base_color = base_color
