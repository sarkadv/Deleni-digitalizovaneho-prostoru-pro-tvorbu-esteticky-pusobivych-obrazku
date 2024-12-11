import math
from typing import Tuple

import cairo

from geometry.point_2d import Point2D


def draw_polygon(context: cairo.Context, vertices: list[Point2D], color: Tuple[float, float, float],
                 border_only: bool) -> None:
    points = [(vertex.get_x(), vertex.get_y()) for vertex in vertices]

    # nakreslení výplně
    context.set_source_rgb(*color)
    context.move_to(*points[0])  # přesunutí na první bod

    for point in points[1:]:  # nakreslení úseček mezi ostatními body
        context.line_to(*point)
    context.close_path()  # uzavření polygonu

    if not border_only:
        context.fill_preserve()

    context.set_line_width(1)  # nakreslení obrysu
    context.stroke()


def draw_circle(context: cairo.Context, center: Point2D, radius: float,
                color: Tuple[float, float, float]) -> None:
    context.set_source_rgb(*color)
    context.arc(center.get_x(), center.get_y(), radius, 0, 2 * math.pi)
    context.fill()


def draw_oval(context: cairo.Context, center: Point2D, radius_x: float, radius_y: float,
              color: Tuple[float, float, float]) -> None:
    context.save()

    context.translate(center.get_x(), center.get_y())
    context.scale(1, radius_y / radius_x)  # změna měřítka pro nakreslení oválu
    context.arc(0, 0, radius_x, 0, 2 * math.pi)
    context.restore()

    # nakreslení výplně
    context.set_source_rgb(*color)
    context.fill_preserve()

    context.set_line_width(1)  # nakreslení obrysu
    context.stroke()


def draw_background(context: cairo.Context, width: int, height: int, color: Tuple[float, float, float]) -> None:
    draw_polygon(context, [Point2D(0, 0), Point2D(width, 0), Point2D(width, height), Point2D(0, height)], color, False)
