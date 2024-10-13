from typing import Tuple

import cairo

from abc import ABC, abstractmethod

from geometry.point import *


class ARegion(ABC):
    def __init__(self, vertices: list[Point]):
        self.__vertices = vertices

    def get_vertices(self) -> list[Point]:
        return self.__vertices

    @abstractmethod
    def draw_basic(self, context: cairo.Context) -> None:
        pass

    @abstractmethod
    def draw_grid(self, context: cairo.Context, border_width: float,
                  border_color_rgb: Tuple[float, float, float]) -> None:

        pass

