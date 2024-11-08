import math
import random
from collections import Counter
from typing import Tuple

import cairo
import PIL.Image as Image
import os

from shapely import Polygon
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
        if not is_point_in_image(image, point):
            continue

        pixel = image.getpixel((point.get_x(), point.get_y())) + (255,)
        color_counts.update([pixel])

    if len(color_counts) < 1:
        return 0, 0, 0, 0

    mode_color_int = color_counts.most_common(1)[0][0]

    return color_int_to_float(mode_color_int)


def find_points_average_color(image: Image, points: list[Point2D]) -> Tuple[float, float, float, float]:
    if len(points) < 1:
        return 0, 0, 0, 0

    sum_r = 0
    sum_g = 0
    sum_b = 0

    for point in points:
        if not is_point_in_image(image, point):
            continue

        r, g, b = image.getpixel((point.get_x(), point.get_y()))
        sum_r += r
        sum_g += g
        sum_b += b

    sum_r = int(sum_r / (len(points)))
    sum_g = int(sum_g / (len(points)))
    sum_b = int(sum_b / (len(points)))

    return color_int_to_float((sum_r, sum_g, sum_b, 255))


def is_point_in_image(image, point: Point2D):
    return not (point.get_x() < 0 or point.get_x() >= image.width or point.get_y() < 0 or point.get_y() >= image.height)


def find_complementary_color(color: Tuple[float, float, float]) -> Tuple[float, float, float]:
    return 1 - color[0], 1 - color[1], 1 - color[2]


def find_output_filename(input_filename: str) -> str:
    basename = os.path.basename(input_filename)
    basename_no_extension = basename.split('.')[0]

    return IMG_OUTPUT_FOLDER + basename_no_extension + IMG_OUTPUT_EXTENSION


def color_int_to_float(color_int: Tuple) -> Tuple:
    return tuple(channel / 255 for channel in color_int)


def find_rectangle_points(vertices: list[Point2D], include_border: bool) -> Tuple[list[int], list[int]]:
    min_x = min([point.get_x() for point in vertices])
    max_x = max([point.get_x() for point in vertices])

    min_y = min([point.get_y() for point in vertices])
    max_y = max([point.get_y() for point in vertices])

    if include_border:
        addition = 1
    else:
        addition = 0

    x_points = list(range(min_x, max_x + addition))
    y_points = list(range(min_y, max_y + addition))

    return x_points, y_points


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

    x_points, y_points = find_rectangle_points(vertices, True)

    x_indices = list(range(len(x_points)))
    y_indices = list(range(len(y_points)))

    random.shuffle(x_indices)
    random.shuffle(y_indices)

    multipoint = MultiPoint([(vertex.get_x(), vertex.get_y()) for vertex in vertices])
    convex_hull = multipoint.convex_hull

    points = []

    for i in range(len(x_indices)):
        for j in range(len(y_indices)):
            x = x_points[x_indices[i]]
            y = y_points[y_indices[j]]
            point = Point2D(x, y)

            if is_point_in_image(image, point) and convex_hull.contains(Point(point.get_x(), point.get_y())):
                points.append(point)

            if point_count_limit != -1 and len(points) == point_count_limit:
                return points

    return points


def get_rectangle_average_color(vertices: list[Point2D], image: Image) -> Tuple[float, float, float, float]:
    x_points, y_points = find_rectangle_points(vertices, False)

    # obdélník je moc malý
    if len(x_points) == 0 or len(y_points) == 0:
        r, g, b = image.getpixel((vertices[0].get_x(), vertices[0].get_y()))
        return color_int_to_float((r, g, b, 255))

    sum_r = 0
    sum_g = 0
    sum_b = 0

    for i in range(len(x_points)):
        for j in range(len(y_points)):
            r, g, b = image.getpixel((x_points[i], y_points[j]))
            sum_r += r
            sum_g += g
            sum_b += b

    sum_r = int(sum_r / (len(x_points) * len(y_points)))
    sum_g = int(sum_g / (len(x_points) * len(y_points)))
    sum_b = int(sum_b / (len(x_points) * len(y_points)))

    return color_int_to_float((sum_r, sum_g, sum_b, 255))


def get_rectangle_color_standard_deviation(vertices: list[Point2D], image: Image,
                                           average_color: Tuple[float, float, float, float]) -> float:
    x_points, y_points = find_rectangle_points(vertices, False)

    # obdélník je moc malý
    if len(x_points) * len(y_points) <= 1:
        return 0

    sd_r = 0
    sd_g = 0
    sd_b = 0

    for i in range(len(x_points)):
        for j in range(len(y_points)):
            r, g, b = image.getpixel((x_points[i], y_points[j]))
            sd_r += (r / 255.0 - average_color[0]) ** 2
            sd_g += (g / 255.0 - average_color[1]) ** 2
            sd_b += (b / 255.0 - average_color[2]) ** 2

    sd_r = sd_r * (1.0 / (len(x_points) * len(y_points) - 1))
    sd_g = sd_g * (1.0 / (len(x_points) * len(y_points) - 1))
    sd_b = sd_b * (1.0 / (len(x_points) * len(y_points) - 1))

    return math.sqrt(sd_r) + math.sqrt(sd_g) + math.sqrt(sd_b)


def get_point_color(image: Image, point: Point2D) -> Tuple[float, float, float, float]:
    if is_point_in_image(image, point):
        r, g, b = image.getpixel((point.get_x(), point.get_y()))
        return color_int_to_float((r, g, b, 255))
    else:
        return color_int_to_float((0, 0, 0, 0))


def crop_polygon_by_bounds(bounds: list[Tuple[float, float]],
                           vertices: list[Tuple[float, float]]) -> list[Tuple[float, float]]:
    intersecting_polygon = Polygon(vertices)
    bounding_polygon = Polygon(bounds)

    if not intersecting_polygon.is_valid or not bounding_polygon.is_valid:
        return vertices

    cropped_polygon = intersecting_polygon.intersection(bounding_polygon)

    if not isinstance(cropped_polygon, Polygon):
        return vertices

    x_coords, y_coords = cropped_polygon.exterior.xy
    new_vertices = []

    for i in range(len(x_coords)):
        new_vertices.append((x_coords[i], y_coords[i]))

    return new_vertices


def get_polygon_from_points(points: list[Point2D]) -> Polygon:
    return Polygon([(point.get_x(), point.get_y()) for point in points])


def random_point_in_polygon(polygon: Polygon) -> Point2D:
    min_x, min_y, max_x, max_y = polygon.bounds
    min_x = round(min_x)
    max_x = round(max_x)
    min_y = round(min_y)
    max_y = round(max_y)

    while True:
        random_point = Point(random.randint(min_x, max_x), random.randint(min_y, max_y))

        if polygon.contains(random_point):
            return Point2D(int(random_point.x), int(random_point.y))


def find_polygon_centroid(vertices: list[Point2D]) -> Point2D:
    if len(vertices) == 0:
        return Point2D(-1, -1)

    centroid_x = 0
    centroid_y = 0

    for point in vertices:
        centroid_x += point.get_x()
        centroid_y += point.get_y()

    centroid_x = int(centroid_x / len(vertices))
    centroid_y = int(centroid_y / len(vertices))

    return Point2D(centroid_x, centroid_y)
