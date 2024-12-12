import sys
from typing import Tuple

import cairo

from abc import ABC, abstractmethod

from PIL import Image
from shapely import Polygon

from geometry.point_2d import *
from util.color_utils import find_points_most_common_color, get_point_color, get_colors_difference, \
    make_colors_more_different, get_colors_ratio
from util.image_drawer import draw_polygon, draw_polygon_with_gradient
from util.geometry_utils import find_points_in_polygon


class ARegion(ABC):

    COLORS_DIFFERENCE_MULTIPLIER = 1.5
    MIN_COLORS_RATIO = 0.2
    MAX_COLORS_RATIO = 0.8

    def __init__(self, vertices: list[Point2D], base_color: Tuple[float, float, float]):
        self.__vertices = vertices
        self.__base_color = base_color

    def draw_basic(self, context: cairo.Context) -> None:
        draw_polygon(context, self.__vertices, self.__base_color, False)

    @abstractmethod
    def draw_grid(self, context: cairo.Context, border_width: float,
                  border_color_rgb: Tuple[float, float, float], colorful: bool) -> None:

        pass

    @abstractmethod
    def draw_multiple_shapes(self, context: cairo.Context) -> None:
        pass

    @abstractmethod
    def draw_rectangle_with_oval(self, context: cairo.Context, image: Image) -> None:
        pass

    def draw_gradients(self, context: cairo.Context, image: Image) -> None:
        # nalezení bodů v polygonu
        vertices_polygon_format = [[vertex.get_x(), vertex.get_y()] for vertex in self.__vertices]
        region_chosen_points_count = Polygon(vertices_polygon_format).area / 2
        points = find_points_in_polygon(self.__vertices, region_chosen_points_count, image)

        # nalezení 2 nejčastějších barev v polygonu
        most_common_colors = find_points_most_common_color(image, points, 2)
        start_color = most_common_colors[0]

        # jestliže polygon obsahuje jen 1 barvu, druhá barva bude stejná
        if len(most_common_colors) < 2:
            end_color = start_color
        else:
            end_color = most_common_colors[1]

        # nalezení vrcholu polygonu, který má nejbližší barvu k té první
        start_color_difference = sys.maxsize
        start_vertex = None

        for vertex in self.__vertices:
            vertex_color = get_point_color(image, vertex)
            difference = get_colors_difference(vertex_color, start_color)

            if difference < start_color_difference:
                start_color_difference = difference
                start_vertex = vertex

        # nalezení vrcholu polygonu, který má nejbližší barvu k té druhé (nesmí být stejný vrchol jako první)
        end_color_difference = sys.maxsize
        end_vertex = None

        for vertex in self.__vertices:
            if vertex is start_vertex:
                continue

            vertex_color = get_point_color(image, vertex)
            difference = get_colors_difference(vertex_color, end_color)

            if difference < end_color_difference:
                end_color_difference = difference
                end_vertex = vertex

        # druhá barva mírně pozměněná
        end_color = make_colors_more_different(start_color, end_color, self.COLORS_DIFFERENCE_MULTIPLIER)

        # poměr druhé barvy k první
        colors_ratio = get_colors_ratio(image, points, start_color, end_color)
        colors_ratio = colors_ratio / (colors_ratio + 1)    # normalizace na interval 0-1
        colors_ratio = max(colors_ratio, self.MIN_COLORS_RATIO)
        colors_ratio = min(colors_ratio, self.MAX_COLORS_RATIO)

        # vykreslení polygonu s gradientem
        draw_polygon_with_gradient(context, self.__vertices, start_vertex, end_vertex, start_color,
                                   end_color, 1 - colors_ratio)

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
