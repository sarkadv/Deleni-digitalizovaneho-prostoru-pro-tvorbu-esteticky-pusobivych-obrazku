import copy
import random
from typing import Tuple, Any

import cairo
from PIL import Image

from geometry.a_region import ARegion
from geometry.point_2d import Point2D
from util.color_utils import find_complementary_color, find_points_most_common_color, get_colors_ratio, \
    make_colors_more_different
from util.image_drawer import draw_polygon, draw_oval
from util.geometry_utils import find_polygon_centroid, find_rectangle_points


class QuadtreeRegion(ARegion):

    MIN_COLORS_RATIO = 0.25
    MAX_COLORS_RATIO = 2
    COLORS_DIFFERENCE_MULTIPLIER = 1.5

    def __init__(self, vertices: list[Point2D], base_color: Tuple[float, float, float]):
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

            draw_polygon(context, region.get_vertices(), region.get_base_color(), region.get_base_color())

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
                border_color = border_color_rgb
            else:
                # obrys každé oblasti může být jiný
                border_color = find_complementary_color(region.get_base_color())

            draw_polygon(context, region.get_vertices(), region.get_base_color(), border_color)

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
                draw_polygon(context, region.get_vertices(), region.get_base_color(), region.get_base_color())

            elif random_number <= 50:
                # ovál
                center = find_polygon_centroid(region.get_vertices())
                radius_x = region.get_x_axis_length() / 2
                radius_y = region.get_y_axis_length() / 2

                draw_oval(context, center, radius_x, radius_y, region.get_base_color())

            elif random_number <= 75:
                # trojúhelník
                vertices = copy.deepcopy(region.get_vertices())

                # odstranění náhodného bodu ze čtyř -> vznikne trojúhelník
                random_index = random.randint(1, len(vertices) - 1)
                del vertices[random_index]

                draw_polygon(context, vertices, region.get_base_color(), region.get_base_color())

            else:
                # kosodélník
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

                draw_polygon(context, vertices, region.get_base_color(), region.get_base_color())

    def draw_rectangle_with_oval(self, context: cairo.Context, image: Image):
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

            points_x, points_y = find_rectangle_points(region.get_vertices(), False)
            points_2D = [Point2D(x, y) for x, y in zip(points_x, points_y)]

            most_common_colors = find_points_most_common_color(image, points_2D, 2)
            rectangle_color = most_common_colors[0]

            if len(most_common_colors) < 2:
                # celá oblast má 1 barvu
                oval_color = rectangle_color
            else:
                oval_color = most_common_colors[1]

            # poměr pixelů bližších k druhé barvě než k té první
            colors_ratio = get_colors_ratio(image, points_2D, rectangle_color, oval_color)

            # změna druhé barvy, aby byla více odlišná od první
            oval_color = make_colors_more_different(rectangle_color, oval_color, self.COLORS_DIFFERENCE_MULTIPLIER)

            # poměr mezi čísly 0.25 až 2, aby nebyl ovál příliš malý, ani velký (přesahující oblast)
            colors_ratio = max(colors_ratio, self.MIN_COLORS_RATIO)
            colors_ratio = min(colors_ratio, self.MAX_COLORS_RATIO)

            # nakreslení obdélníku
            draw_polygon(context, region.get_vertices(), rectangle_color, rectangle_color)

            center = find_polygon_centroid(region.get_vertices())

            # defaultní průměr je polovina oblasti -> dále vynásobeno poměrem barev pro zmenšení / zvětšení
            radius_x = (region.get_x_axis_length() / 4) * colors_ratio
            radius_y = (region.get_y_axis_length() / 4) * colors_ratio

            # vykreslení oválu nad obdélníkem
            draw_oval(context, center, radius_x, radius_y, oval_color)

    def get_children(self) -> list[list[Any]]:
        return self.__children

    def set_children(self, children: list[list['QuadtreeRegion']]) -> None:
        self.__children = children
        self.__split = True
