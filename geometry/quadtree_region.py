import copy
import random
from typing import Tuple, Any

import cairo

from geometry.a_region import ARegion
from geometry.point_2d import Point2D
from util.image_drawer import draw_polygon, draw_oval
from util.image_utils import find_complementary_color, find_polygon_centroid


class QuadtreeRegion(ARegion):
    def __init__(self, vertices: list[Point2D], base_color: Tuple[float, float, float, float]):
        super().__init__(vertices, base_color)
        self.__split = False  # má oblast potomky?
        self.__children = [[None, None],
                           [None, None]]

    def draw_basic(self, context: cairo.Context) -> None:
        stack = [self]

        while len(stack) > 0:
            region = stack.pop()

            if len(region.get_vertices()) == 0:
                continue

            # pokud má region potomky, vložit je do zásobníku
            if region.__split:
                for i in range(len(region.__children)):
                    for j in range(len(region.__children[0])):
                        child = region.__children[i][j]
                        stack.append(child)

                # vykreslit pouze koncové regiony bez potomků - region s potomky je stejně překrytý
                continue

            draw_polygon(context, region.get_vertices(), region.get_base_color(), False)

    def draw_grid(self, context: cairo.Context, border_width: float,
                  border_color_rgb: Tuple[float, float, float], colorful: bool) -> None:
        stack = [self]

        while len(stack) > 0:
            region = stack.pop()

            if len(region.get_vertices()) == 0:
                continue

            # pokud má region potomky, vložit je do zásobníku
            if region.__split:
                for i in range(len(region.__children)):
                    for j in range(len(region.__children[0])):
                        child = region.__children[i][j]
                        stack.append(child)

            # nakreslení obrysu
            if not colorful:
                # všechny obrysy stejná barva
                border_color = border_color_rgb + (1,)
            else:
                # obrys každé oblasti může být jiný
                r, g, b, a = region.get_base_color()
                border_color = find_complementary_color((r, g, b)) + (1,)

            draw_polygon(context, region.get_vertices(), border_color, True)

    def draw_multiple_shapes(self, context: cairo.Context) -> None:
        stack = [self]

        while len(stack) > 0:
            region = stack.pop()

            if len(region.get_vertices()) == 0:
                continue

            # pokud má region potomky, vložit je do zásobníku
            if region.__split:
                for i in range(len(region.__children)):
                    for j in range(len(region.__children[0])):
                        child = region.__children[i][j]
                        stack.append(child)

                # vykreslit pouze koncové regiony bez potomků - region s potomky je stejně překrytý
                continue

            random_number = random.randint(1, 100)

            if random_number <= 25:
                # obdélník
                self.__draw_rectangle_shape(context, region)
            elif random_number <= 50:
                # ovál
                self.__draw_oval_shape(context, region)
            elif random_number <= 75:
                # trojúhelník
                self.__draw_triangle_shape(context, region)
            else:
                # kosodélník
                self.__draw_rhomboid_shape(context, region)

    def __draw_rectangle_shape(self, context: cairo.Context, region: 'QuadtreeRegion') -> None:
        draw_polygon(context, region.get_vertices(), region.get_base_color(), False)

    def __draw_oval_shape(self, context: cairo.Context, region: 'QuadtreeRegion') -> None:
        center = find_polygon_centroid(region.get_vertices())
        radius_x = region.get_x_axis_length() / 2
        radius_y = region.get_y_axis_length() / 2

        draw_oval(context, center, radius_x, radius_y, region.get_base_color())

    def __draw_triangle_shape(self, context: cairo.Context, region: 'QuadtreeRegion') -> None:
        vertices = copy.deepcopy(region.get_vertices())

        # odstranění náhodného bodu ze čtyř -> vznikne trojúhelník
        random_index = random.randint(1, len(vertices) - 1)
        del vertices[random_index]

        draw_polygon(context, vertices, region.get_base_color(), False)

    def __draw_rhomboid_shape(self, context: cairo.Context, region: 'QuadtreeRegion') -> None:
        vertices = []

        # nalezení středů všech stran oblasti -> vznikne kosodélník
        for i in range(len(region.get_vertices())):
            vertex = region.get_vertices()[i]

            if i == len(region.get_vertices()) - 1:
                next_vertex = region.get_vertices()[0]
            else:
                next_vertex = region.get_vertices()[i + 1]

            center = vertex.line_center(next_vertex)
            vertices.append(center)

        draw_polygon(context, vertices, region.get_base_color(), False)

    def get_children(self) -> list[list[Any]]:
        return self.__children

    def set_children(self, children: list[list['QuadtreeRegion']]) -> None:
        self.__children = children
        self.__split = True
