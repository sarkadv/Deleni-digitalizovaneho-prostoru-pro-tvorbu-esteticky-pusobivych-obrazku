import random
from collections import Counter
from typing import Tuple

import cairo
import PIL.Image as Image
import os

import numpy as np
from shapely.geometry import Point, MultiPoint

from geometry.point_2d import Point2D

IMG_OUTPUT_FOLDER = 'img_output/'
IMG_OUTPUT_EXTENSION = '.png'


def cairo_surface_from_pil(image: Image) -> cairo.Surface:
    # podle https://pycairo.readthedocs.io/en/latest/tutorial/pillow.html

    image.putalpha(256)
    arr = bytearray(image.tobytes('raw', 'BGRa'))

    return cairo.ImageSurface.create_for_data(arr, cairo.FORMAT_RGB24, image.width, image.height)


def find_image_mode_color(image: Image) -> Tuple[float, float, float]:
    pixels = list(image.getdata())

    color_counts = Counter(pixels)
    mode_color_int = color_counts.most_common(1)[0][0]

    return color_int_to_float(mode_color_int)


def find_points_mode_color(image: Image, points: list[Point2D]) -> Tuple[float, float, float, float]:
    if len(points) < 1:
        return 0, 0, 0, 0

    color_counts = Counter()

    for point in points:
        if point.get_x() < 0 or point.get_x() >= image.width or point.get_y() < 0 or point.get_y() >= image.height:
            continue

        pixel = image.getpixel((point.get_x(), point.get_y())) + (255,)
        color_counts.update([pixel])

    if len(color_counts) < 1:
        return 0, 0, 0, 0

    mode_color_int = color_counts.most_common(1)[0][0]

    return color_int_to_float(mode_color_int)


def is_point_in_image(image, point: Point2D):
    return not (point.get_x() < 0 or point.get_x() >= image.width or point.get_y() < 0 or point.get_y() >= image.height)


def find_complementary_color(color: Tuple[float, float, float]) -> Tuple[float, float, float]:
    return 1 - color[0], 1 - color[1], 1 - color[2]


def find_output_filename(input_filename: str) -> str:
    basename = os.path.basename(input_filename)
    basename_no_extension = basename.split('.')[0]

    return IMG_OUTPUT_FOLDER + basename_no_extension + IMG_OUTPUT_EXTENSION


def color_int_to_float(color_int: Tuple) -> Tuple:
    return tuple(primary_color / 255 for primary_color in color_int)


def find_points_in_polygon(vertices: list[Point2D], point_count_limit: int, image: Image) -> list[Point2D]:
    """
    :param vertices: vrcholy polygonu
    :param point_count_limit: limit vygenerovaných bodů, po jehož dosažení je hledání ukončeno (-1 žádný limit)
    :param image: celý obraz
    :return: body nacházející se v polygonu
    """

    no_vertices_in_image = True

    for vertex in vertices:
        if is_point_in_image(image, vertex):
            no_vertices_in_image = False
            break

    if no_vertices_in_image:
        return []

    min_x = min([point.get_x() for point in vertices])
    max_x = max([point.get_x() for point in vertices])

    min_y = min([point.get_y() for point in vertices])
    max_y = max([point.get_y() for point in vertices])

    x_points = list(range(min_x, max_x + 1))
    y_points = list(range(min_y, max_y + 1))

    x_indices = list(range(len(x_points)))
    y_indices = list(range(len(y_points)))

    random.shuffle(x_indices)
    random.shuffle(y_indices)

    # vytvoření konvexní obálky
    multipoint = MultiPoint([(vertex.get_x(), vertex.get_y()) for vertex in vertices])
    convex_hull = multipoint.convex_hull

    points = []

    for i in range(len(x_indices)):
        for j in range(len(y_indices)):
            x = x_points[x_indices[i]]
            y = y_points[y_indices[j]]
            point = Point2D(x, y)

            if convex_hull.contains(Point(point.get_x(), point.get_y())) and is_point_in_image(image, point):
                points.append(point)

            if point_count_limit != -1 and len(points) == point_count_limit:
                return points

    return points

def get_rectangle_average_color(vertices: list[Point2D], image: Image) -> Tuple[float, float, float, float]:
    min_x = min([point.get_x() for point in vertices])
    max_x = max([point.get_x() for point in vertices])

    min_y = min([point.get_y() for point in vertices])
    max_y = max([point.get_y() for point in vertices])

    x_points = list(range(min_x, max_x + 1))
    y_points = list(range(min_y, max_y + 1))

    sum_r = 0
    sum_g = 0
    sum_b = 0

    for i in range(len(x_points)):
        r, g, b = image.getpixel((x_points[i], y_points[i]))
        sum_r += r
        sum_g += g
        sum_b += b

    sum_r = int(sum_r / len(x_points))
    sum_g = int(sum_g / len(x_points))
    sum_b = int(sum_b / len(x_points))

    return color_int_to_float((sum_r, sum_g, sum_b, 255))

def get_rectangle_color_standard_deviation(vertices: list[Point2D], image: Image, average_color: Tuple[float, float, float, float]) -> Tuple[float, float, float, float]:
    pass





