import sys
from typing import Tuple

import cairo

from abc import ABC, abstractmethod

from PIL import Image

from geometry.point_2d import *
from util.color_utils import find_points_most_common_color
from util.image_drawer import draw_polygon, draw_polygon_with_gradient
from util.geometry_utils import find_points_in_polygon, split_polygon


class ARegion(ABC):

    PAPER_CHANNEL_ADDITION = 0.15

    def __init__(self, vertices: list[Point2D], base_color: Tuple[float, float, float]):
        self.__vertices = vertices
        self.__base_color = base_color

    def draw_basic(self, context: cairo.Context) -> None:
        draw_polygon(context, self.__vertices, self.__base_color, self.__base_color)

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
        polygons = split_polygon(self.__vertices)

        if len(polygons) < 2:
            # nedošlo k rozdělení polygonu (např. polygon moc malý)
            draw_polygon(context, self.__vertices, self.__base_color, self.__base_color)
            return

        polygon1 = polygons[0]
        polygon2 = polygons[1]

        # nalezení všech bodů v polygonech - jinak gradienty vytváří příliš rušivé nepřesnosti (díry)
        points1 = find_points_in_polygon(polygon1, -1, image)
        points2 = find_points_in_polygon(polygon2, -1, image)

        if len(points1) == 0 or len(points2) == 0:
            # nenalezeny žádné body alespoň v jednom z polygonů (např. polygon moc malý)
            draw_polygon(context, self.__vertices, self.__base_color, self.__base_color)
            return

        # nalezení nejčastějších barev v polygonech
        start_color = find_points_most_common_color(image, points1)[0]
        end_color = find_points_most_common_color(image, points2)[0]

        # nalezení nejvzdálenějších vrcholů (každý z jednoho polygonu)
        max_distance = -sys.maxsize
        start_vertex = None
        end_vertex = None

        for vertex1 in polygon1:
            if vertex1 not in self.__vertices:
                # pouze vrcholy původního polygonu
                continue

            for vertex2 in polygon2:
                if vertex2 not in self.__vertices:
                    # pouze vrcholy původního polygonu
                    continue

                distance = vertex1.euclidean_distance(vertex2)

                if distance > max_distance:
                    max_distance = distance
                    start_vertex = vertex1
                    end_vertex = vertex2

        # vykreslení polygonu s gradientem
        draw_polygon_with_gradient(context, self.__vertices, start_vertex, end_vertex, start_color, end_color)

    def draw_paper(self, context: cairo.Context) -> None:
        # zesvětlení barevných kanálů
        color_r = min(self.__base_color[0] + self.PAPER_CHANNEL_ADDITION, 1)
        color_g = min(self.__base_color[1] + self.PAPER_CHANNEL_ADDITION, 1)

        # modrá přidána méně, aby byl obraz žlutější
        color_b = min(self.__base_color[2] + self.PAPER_CHANNEL_ADDITION * 5/6, 1)

        draw_polygon(context, self.__vertices, (color_r, color_g, color_b), (color_r, color_g, color_b))

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
