import math
from collections import Counter
from typing import Tuple

from PIL import Image

from geometry.point_2d import Point2D
from util.geometry_utils import is_point_in_image, find_rectangle_points


def color_int_to_float(color_int: Tuple) -> Tuple:
    return tuple(channel / 255 for channel in color_int)


def find_complementary_color(color: Tuple[float, float, float]) -> Tuple[float, float, float]:
    return 1 - color[0], 1 - color[1], 1 - color[2]


def get_point_color(image: Image, point: Point2D) -> Tuple[float, float, float]:
    if is_point_in_image(image, point):
        r, g, b = image.getpixel((point.get_x(), point.get_y()))
        return color_int_to_float((r, g, b))
    else:
        return 0, 0, 0


def find_image_mode_color(image: Image) -> Tuple[float, float, float]:
    pixels = list(image.getdata())

    color_counts = Counter(pixels)
    mode_color_int = color_counts.most_common(1)[0][0]

    return color_int_to_float(mode_color_int)


def find_points_average_color(image: Image, points: list[Point2D]) -> Tuple[float, float, float]:
    if len(points) < 1:
        return 0, 0, 0

    sum_r = 0
    sum_g = 0
    sum_b = 0

    for point in points:
        if not is_point_in_image(image, point):
            continue

        r, g, b = get_point_color(image, point)
        sum_r += r
        sum_g += g
        sum_b += b

    sum_r = sum_r / len(points)
    sum_g = sum_g / len(points)
    sum_b = sum_b / len(points)

    return sum_r, sum_g, sum_b


def find_points_most_common_colors(image: Image, points: list[Point2D], most_common_count: int = 1) \
        -> list[Tuple[float, float, float]]:

    if len(points) < 1:
        return [(0, 0, 0)]

    color_counts = Counter()

    for point in points:
        if not is_point_in_image(image, point):
            continue

        pixel = get_point_color(image, point)
        color_counts.update([pixel])

    if len(color_counts) < 1:
        return [(0, 0, 0)]

    most_common_colors = color_counts.most_common(most_common_count)
    result = []

    for color in most_common_colors:
        result.append(color[0])

    return result


def get_rectangle_average_color(vertices: list[Point2D], image: Image) -> Tuple[float, float, float]:
    x_points, y_points = find_rectangle_points(vertices, False)

    # obdélník je moc malý
    if len(x_points) == 0 or len(y_points) == 0:
        point = Point2D(vertices[0].get_x(), vertices[0].get_y())
        r, g, b = get_point_color(image, point)
        return r, g, b

    sum_r = 0
    sum_g = 0
    sum_b = 0

    for i in range(len(x_points)):
        for j in range(len(y_points)):
            point = Point2D(x_points[i], y_points[j])
            r, g, b = get_point_color(image, point)
            sum_r += r
            sum_g += g
            sum_b += b

    sum_r = sum_r / (len(x_points) * len(y_points))
    sum_g = sum_g / (len(x_points) * len(y_points))
    sum_b = sum_b / (len(x_points) * len(y_points))

    return sum_r, sum_g, sum_b


def get_rectangle_color_standard_deviation(vertices: list[Point2D], image: Image,
                                           average_color: Tuple[float, float, float]) -> float:
    x_points, y_points = find_rectangle_points(vertices, False)

    # obdélník je moc malý
    if len(x_points) * len(y_points) <= 1:
        return 0

    sd_r = 0
    sd_g = 0
    sd_b = 0

    for i in range(len(x_points)):
        for j in range(len(y_points)):
            point = Point2D(x_points[i], y_points[j])
            r, g, b = get_point_color(image, point)
            sd_r += (r - average_color[0]) ** 2
            sd_g += (g - average_color[1]) ** 2
            sd_b += (b - average_color[2]) ** 2

    sd_r = sd_r * (1.0 / (len(x_points) * len(y_points) - 1))
    sd_g = sd_g * (1.0 / (len(x_points) * len(y_points) - 1))
    sd_b = sd_b * (1.0 / (len(x_points) * len(y_points) - 1))

    return math.sqrt(sd_r) + math.sqrt(sd_g) + math.sqrt(sd_b)


def get_colors_difference(color1: Tuple[float, float, float],
                          color2: Tuple[float, float, float]) -> float:
    difference = 0
    length = min(len(color1), len(color2))

    for i in range(length):
        difference += abs(color1[i] - color2[i])

    return difference


def get_colors_ratio(image: Image, points: list[Point2D], color1: Tuple[float, float, float],
                     color2: Tuple[float, float, float]) -> float:

    color1_count = 1
    color2_count = 1

    for point in points:
        color = get_point_color(image, point)

        color1_difference = get_colors_difference(color1, color)
        color2_difference = get_colors_difference(color2, color)

        # zvýšení výskytu barvy, ke které je zkoumaný pixel blíže
        if color1_difference < color2_difference:
            color1_count += 1
        else:
            color2_count += 1

    # vrácení poměru pixelů bližších k druhé barvě než k té první
    return color2_count / color1_count
