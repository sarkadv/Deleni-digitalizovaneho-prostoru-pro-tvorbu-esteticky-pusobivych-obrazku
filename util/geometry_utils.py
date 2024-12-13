import copy
import random
import sys
from typing import Tuple

import PIL.Image as Image
import numpy as np
from scipy.spatial._qhull import ConvexHull

from shapely import Polygon, LineString
from shapely.geometry import Point, MultiPoint

from geometry.point_2d import Point2D


def is_point_in_image(image, point: Point2D):
    return not (point.get_x() < 0 or point.get_x() >= image.width or point.get_y() < 0 or point.get_y() >= image.height)


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


def find_polygon_longest_side(vertices: list[Point2D]) -> Tuple[Point2D, Point2D]:
    max_distance = -sys.maxsize
    max_distance_vertices = (None, None)

    for i in range(len(vertices)):
        vertex1 = vertices[i]
        vertex2 = vertices[(i + 1) % len(vertices)]

        distance = vertex1.euclidean_distance(vertex2)

        if distance > max_distance:
            max_distance = distance
            max_distance_vertices = (vertex1, vertex2)

    return max_distance_vertices


def split_polygon(vertices: list[Point2D]) -> list[list[Point2D]]:
    # nalezení středu nejdelší strany polygonu
    longest_side = find_polygon_longest_side(vertices)
    center1 = longest_side[0].line_center(longest_side[1])

    # nalezení středu strany, který je nejdále od prvního středu
    center_max_distance = -sys.maxsize
    center2 = None

    for i in range(len(vertices)):
        vertex1 = vertices[i]
        vertex2 = vertices[(i + 1) % len(vertices)]

        center = vertex1.line_center(vertex2)   # střed aktuální strany
        distance = center.euclidean_distance(center1)   # vzdálenost aktuálního středu od prvního středu

        if distance > center_max_distance:
            center_max_distance = distance
            center2 = center

    polygon = Polygon([[vertex.get_x(), vertex.get_y()] for vertex in vertices])
    line = LineString([[center1.get_x(), center1.get_y()], [center2.get_x(), center2.get_y()]]) # dělicí přímka

    # rozdělení polygonu dělicí přímkou
    split_polygons = []
    parts = polygon.difference(line.buffer(1))

    if parts.geom_type == "MultiPolygon":
        # úspěšné rozdělení na 2 polygony
        for geom in parts.geoms:
            split_polygons.append(list(geom.exterior.coords)[:-1])
    else:
        # přímka nerozdělila polygon (např. polygon příliš malý)
        return [vertices]   # vrácení původního polygonu

    result = []
    for polygon in split_polygons:
        # rozdělené polygony do správného formátu
        result.append([Point2D(round(vertex[0]), round(vertex[1])) for vertex in polygon])

    return result
