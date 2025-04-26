import math
import random
from typing import Tuple

import cairo

from geometry.point_2d import Point2D
from util.convolution import create_convolution_padding, convolute, GAUSSIAN_CONVOLUTION_MATRIX


def draw_polygon(context: cairo.Context, vertices: list[Point2D], color: Tuple[float, float, float],
                 border_color: Tuple[float, float, float], border_width: int = 1) -> None:
    """
    Vykreslí na grafický kontext polygon.
    :param context: grafický kontext
    :param vertices: vrcholy polygonu
    :param color: RGB barva výplně se složkami 0-1
    :param border_color: RGB barva obrysu se složkami 0-1
    :param border_width: šířka obrysu
    """

    if len(vertices) < 3:
        # není polygon
        return

    points = [(vertex.get_x(), vertex.get_y()) for vertex in vertices]

    # nakreslení výplně
    context.set_source_rgb(*color)
    context.move_to(*points[0])  # přesunutí na první bod

    for point in points[1:]:  # nakreslení úseček mezi ostatními body
        context.line_to(*point)
    context.close_path()  # uzavření polygonu

    context.fill_preserve()  # výplň

    context.set_source_rgb(*border_color)
    context.set_line_width(border_width)  # nakreslení obrysu
    context.stroke()


def draw_circle(context: cairo.Context, center: Point2D, radius: float,
                color: Tuple[float, float, float]) -> None:
    """
    Vykreslí na grafický kontext kruh.
    :param context: grafický kontext
    :param center: střed kruhu
    :param radius: poloměr kruhu
    :param color: RGB barva výplně se složkami 0-1
    """

    context.set_source_rgb(*color)
    context.arc(center.get_x(), center.get_y(), radius, 0, 2 * math.pi)
    context.fill()


def draw_oval(context: cairo.Context, center: Point2D, radius_x: float, radius_y: float,
              color: Tuple[float, float, float]) -> None:
    """
    Vykreslí na grafický kontext ovál.
    :param context: grafický kontext
    :param center: střed oválu
    :param radius_x: poloměr oválu v ose x
    :param radius_y: poloměr oválu v ose y
    :param color: RGB barva výplně se složkami 0-1
    """

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
    """
    Vykreslí na grafický kontext polygon s výplní lineárního gradientu.
    :param context: grafický kontext
    :param vertices: vrcholy polygonu
    :param start_vertex: počáteční bod lineárního gradientu
    :param end_vertex: koncový bod lineárního gradientu
    :param start_color: počáteční barva lineárního gradientu
    :param end_color: koncová barva lineárního gradientu
    """

    if len(vertices) < 3:
        # není polygon
        return

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


def draw_paper_texture(context: cairo.Context, width: int, height: int) -> None:
    """
    Vykreslí na celý grafický kontext šum pro efekt papíru.
    :param context: grafický kontext
    :param width: šířka kontextu
    :param height: výška kontextu
    """

    # velikost jedné částice šumu podle rozměrů obrázku
    noise_particle_size = int(math.log(width * height, 100))

    particles_x = int(width / noise_particle_size)   # počet částic na šířku
    particles_y = int(height / noise_particle_size)  # počet částic na výšku

    # náhodná intenzita částic po celém obrázku
    noise_intensity = [[random.uniform(0.05, 0.1) for _ in range(particles_x)] for _ in range(particles_y)]

    # Gaussovské rozostření intenzity
    noise_intensity_gaussian = create_convolution_padding(noise_intensity)
    noise_intensity_gaussian = convolute(noise_intensity_gaussian, GAUSSIAN_CONVOLUTION_MATRIX)

    for i in range(len(noise_intensity)):
        for j in range(len(noise_intensity[i])):
            # průhlednost částice vypočítána z původni intenzity a rozostřené intenzity
            alpha = noise_intensity[i][j] + noise_intensity_gaussian[i][j]

            context.set_source_rgba(0, 0, 0, alpha)
            context.rectangle(j * noise_particle_size, i * noise_particle_size, noise_particle_size,
                              noise_particle_size)
            context.fill()
