import copy
import random
from typing import Tuple

import cairo
from PIL import Image

from geometry.a_region import ARegion
from geometry.point_2d import Point2D
from util.color_utils import find_points_most_common_colors, get_colors_ratio
from util.image_drawer import draw_polygon, draw_oval
from util.geometry_utils import find_polygon_centroid, find_rectangle_points


class QuadtreeRegion(ARegion):
    """
    Třída představující jednu oblast kvadrantového stromu (obdélník).
    """

    # vhodně zvolené konstanty pro efekt obdélníku s oválem uvnitř
    MIN_RATIO = 0.25
    MAX_RATIO = 2

    def __init__(self, vertices: list[Point2D], base_color: Tuple[float, float, float]):
        super().__init__(vertices, base_color)

    def draw_multiple_shapes(self, context: cairo.Context) -> None:
        random_number = random.randint(1, 100)

        if random_number <= 25:
            # obdélník
            draw_polygon(context, self.get_vertices(), self.get_base_color(), self.get_base_color())

        elif random_number <= 50:
            # ovál
            center = find_polygon_centroid(self.get_vertices())
            radius_x = self.get_x_axis_length() / 2
            radius_y = self.get_y_axis_length() / 2

            draw_oval(context, center, radius_x, radius_y, self.get_base_color())

        elif random_number <= 75:
            # trojúhelník
            vertices = copy.deepcopy(self.get_vertices())

            # odstranění náhodného bodu ze čtyř -> vznikne trojúhelník
            random_index = random.randint(1, len(vertices) - 1)
            del vertices[random_index]

            draw_polygon(context, vertices, self.get_base_color(), self.get_base_color())

        else:
            # kosodélník
            vertices = []

            # nalezení středů všech stran oblasti -> vznikne kosodélník
            for i in range(len(self.get_vertices())):
                vertex = self.get_vertices()[i]

                if i == len(self.get_vertices()) - 1:
                    next_vertex = self.get_vertices()[0]
                else:
                    next_vertex = self.get_vertices()[i + 1]

                center = vertex.line_center(next_vertex)
                vertices.append(center)

            draw_polygon(context, vertices, self.get_base_color(), self.get_base_color())

    def draw_rectangle_with_oval(self, context: cairo.Context, image: Image):
        points_x, points_y = find_rectangle_points(self.get_vertices())
        points_2D = [Point2D(x, y) for x, y in zip(points_x, points_y)]

        most_common_colors = find_points_most_common_colors(image, points_2D, 2)
        rectangle_color = most_common_colors[0]

        if len(most_common_colors) < 2:
            # celá oblast má 1 barvu, pouze obdélník bez oválu
            draw_polygon(context, self.get_vertices(), rectangle_color, rectangle_color)
            return

        oval_color = most_common_colors[1]

        # poměr pixelů bližších k druhé barvě než k té první
        colors_ratio = get_colors_ratio(image, points_2D, rectangle_color, oval_color)

        # poměr mezi čísly 0.25 až 2, aby nebyl ovál příliš malý, ani velký (přesahující oblast)
        colors_ratio = max(colors_ratio, self.MIN_RATIO)
        colors_ratio = min(colors_ratio, self.MAX_RATIO)

        # nakreslení obdélníku
        draw_polygon(context, self.get_vertices(), rectangle_color, rectangle_color)

        center = find_polygon_centroid(self.get_vertices())

        # defaultní průměr je polovina oblasti -> dále vynásobeno poměrem barev pro zmenšení / zvětšení
        radius_x = (self.get_x_axis_length() / 4) * colors_ratio
        radius_y = (self.get_y_axis_length() / 4) * colors_ratio

        # vykreslení oválu nad obdélníkem
        draw_oval(context, center, radius_x, radius_y, oval_color)
