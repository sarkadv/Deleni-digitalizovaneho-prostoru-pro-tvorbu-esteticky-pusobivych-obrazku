from typing import Tuple, Any

import cairo

from geometry.a_region import ARegion
from geometry.point_2d import Point2D


class QuadtreeRegion(ARegion):
    def __init__(self, vertices: list[Point2D], base_color: Tuple[float, float, float, float]):
        super().__init__(vertices, base_color)
        self.__children = [[None, None],
                           [None, None]]

    def draw_basic(self, context: cairo.Context) -> None:
        stack = [self]

        while len(stack) > 0:
            region = stack.pop()
            points = [(vertex.get_x(), vertex.get_y()) for vertex in region.get_vertices()]

            # nakreslení výplně
            context.set_source_rgba(*region.get_base_color())
            context.move_to(*points[0])  # přesunutí na první bod

            for point in points[1:]:  # nakreslení úseček mezi ostatními body
                context.line_to(*point)
            context.close_path()  # uzavření polygonu

            context.fill_preserve()

            context.set_line_width(1)   # nakreslení obrysu
            context.stroke()

            # pokud má region potomky, vložit je do zásobníku
            if region.__children[0][0] is not None:
                for i in range(len(region.__children)):
                    for j in range(len(region.__children[0])):
                        child = region.__children[i][j]
                        stack.append(child)

    def draw_grid(self, context: cairo.Context, border_width: float,
                  border_color_rgb: Tuple[float, float, float]) -> None:
        stack = [self]

        while len(stack) > 0:
            region = stack.pop()
            points = [(vertex.get_x(), vertex.get_y()) for vertex in region.get_vertices()]

            context.move_to(*points[0])  # přesunutí na první bod

            for point in points[1:]:  # nakreslení úseček mezi ostatními body
                context.line_to(*point)
            context.close_path()  # uzavření polygonu

            # nakreslení obrysu
            context.set_source_rgb(*border_color_rgb)
            context.set_line_width(border_width)
            context.stroke()

            # pokud má region potomky, vložit je do zásobníku
            if region.__children[0][0] is not None:
                for i in range(len(region.__children)):
                    for j in range(len(region.__children[0])):
                        child = region.__children[i][j]
                        stack.append(child)

    def get_children(self) -> list[list[Any]]:
        return self.__children

    def set_children(self, children: list[list['QuadtreeRegion']]) -> None:
        self.__children = children
