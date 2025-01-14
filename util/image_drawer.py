import math
import random
from typing import Tuple

import cairo

from geometry.point_2d import Point2D
from util.geometry_utils import create_convolution_padding, apply_convolution

GAUSSIAN_CONVOLUTION_MATRIX = [[1 / 16, 1 / 8, 1 / 16],
                               [1 / 8, 1 / 4, 1 / 8],
                               [1 / 16, 1 / 8, 1 / 16]]


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


def draw_polygon_with_gradient(context: cairo.Context, vertices: list[Point2D], start_vertex: Point2D,
                               end_vertex: Point2D, start_color: Tuple[float, float, float],
                               end_color: Tuple[float, float, float]) -> None:
    gradient = cairo.LinearGradient(start_vertex.get_x(), start_vertex.get_y(), end_vertex.get_x(), end_vertex.get_y())

    gradient.add_color_stop_rgb(0, start_color[0], start_color[1], start_color[2])  # počátek gradientu
    gradient.add_color_stop_rgb(1, end_color[0], end_color[1], end_color[2])  # konec gradientu

    points = [(vertex.get_x(), vertex.get_y()) for vertex in vertices]

    # nakreslení polygonu
    context.set_source(gradient)
    context.move_to(*points[0])  # přesunutí na první bod

    for point in points[1:]:  # nakreslení úseček mezi ostatními body
        context.line_to(*point)
    context.close_path()  # uzavření polygonu

    context.fill_preserve()

    context.set_line_width(1)  # nakreslení obrysu
    context.stroke()


def draw_background(context: cairo.Context, width: int, height: int, color: Tuple[float, float, float]) -> None:
    draw_polygon(context, [Point2D(0, 0), Point2D(width, 0), Point2D(width, height), Point2D(0, height)], color, False)


def draw_paper_texture(context: cairo.Context, width: int, height: int) -> None:
    # velikost jedné částice podle rozměrů obrázku
    noise_particle_size = int(math.log(width * height, 100))

    # intenzita náhodných částic po celém obrázku
    noise_intensity = [[random.uniform(0.05, 0.1) for _ in range(int(width / noise_particle_size))]
                       for _ in range(int(height / noise_particle_size))]

    # Gaussovské rozostření intenzity
    noise_intensity_gaussian = create_convolution_padding(noise_intensity)
    noise_intensity_gaussian = apply_convolution(noise_intensity_gaussian, GAUSSIAN_CONVOLUTION_MATRIX)

    for i in range(len(noise_intensity)):
        for j in range(len(noise_intensity[i])):
            # průhlednost částice vypočítána z původni intenzity a rozostřené intenzity
            alpha = noise_intensity[i][j] + noise_intensity_gaussian[i][j]

            context.set_source_rgba(0, 0, 0, alpha)
            context.rectangle(j * noise_particle_size, i * noise_particle_size, noise_particle_size,
                              noise_particle_size)
            context.fill()
