import random
import sys
from typing import Tuple

from PIL import Image
from scipy.spatial import KDTree

from shapely import Polygon, LineString, make_valid
from shapely.geometry import Point, MultiPoint

from geometry.point_2d import Point2D


def is_point_in_image(image, point: Point2D) -> bool:
    """
    :param image: obrázek
    :param point: 2D bod
    :return: nachází se souřadnice bodu uvnitř obrázku?
    """
    return not (point.get_x() < 0 or point.get_x() >= image.width or point.get_y() < 0 or point.get_y() >= image.height)


def find_rectangle_points(vertices: list[Point2D]) -> Tuple[list[int], list[int]]:
    """
    :param vertices: vrcholy obdélníku
    :return: celočíselné body v obdélníku
    """

    min_x = min([point.get_x() for point in vertices])
    max_x = max([point.get_x() for point in vertices])

    min_y = min([point.get_y() for point in vertices])
    max_y = max([point.get_y() for point in vertices])

    x_points = list(range(min_x, max_x))
    y_points = list(range(min_y, max_y))

    return x_points, y_points


def find_points_in_polygon(vertices: list[Point2D], point_count_limit: int, image: Image) -> list[Point2D]:
    """
    :param vertices: vrcholy polygonu
    :param point_count_limit: limit vygenerovaných bodů, po jehož dosažení je hledání ukončeno (-1 žádný limit)
    :param image: obrázek
    :return: body nacházející se v polygonu
    """

    no_vertices_in_image = True

    for vertex in vertices:
        if is_point_in_image(image, vertex):
            no_vertices_in_image = False
            break

    if no_vertices_in_image:
        return []

    x_points, y_points = find_rectangle_points(vertices)

    x_indices = list(range(len(x_points)))
    y_indices = list(range(len(y_points)))

    random.shuffle(x_indices)
    random.shuffle(y_indices)

    multipoint = MultiPoint([(vertex.get_x(), vertex.get_y()) for vertex in vertices])
    convex_hull = multipoint.convex_hull

    points = []
    points.extend(vertices)

    for i in range(len(x_indices)):
        for j in range(len(y_indices)):
            x = x_points[x_indices[i]]
            y = y_points[y_indices[j]]
            point = Point2D(x, y)

            if not is_point_in_image(image, point):
                continue

            if point in vertices:
                # bod už byl přidán před cyklem
                continue

            if convex_hull.contains(Point(point.get_x(), point.get_y())):
                points.append(point)

            if point_count_limit != -1 and len(points) >= point_count_limit:
                return points

    return points


def crop_polygon_by_bounds(bounds: list[Tuple[float, float]],
                           vertices: list[Tuple[float, float]]) -> list[Tuple[float, float]]:
    """
    :param bounds: ořezové hranice dané 2D vrcholy polygonu
    :param vertices: ořezávaný polygon daný 2D vrcholy
    :return: oříznutý polygon daný 2D vrcholy
    """

    intersecting_polygon = Polygon(vertices)
    bounding_polygon = Polygon(bounds)

    if not bounding_polygon.is_valid:
        # hranice nejsou validní polygon
        return vertices

    if not intersecting_polygon.is_valid:
        # zaokrouhlením vrcholů může vzniknout polygon, který protíná sám sebe -> oprava polygonu
        intersecting_polygon = make_valid(intersecting_polygon)

    # průnik může kromě plochy obsahovat i úsečky a body (dotyk na hranici) -> ponechány jen plošné části
    parts = []

    for part in _polygon_parts(intersecting_polygon):
        parts.extend(_polygon_parts(part.intersection(bounding_polygon)))

    if len(parts) == 0:
        # polygon leží mimo hranice nebo se jich jen dotýká
        return []

    # oříznutý polygon je největší plošná část průniku
    cropped_polygon = max(parts, key=lambda polygon: polygon.area)

    x_coords, y_coords = cropped_polygon.exterior.xy
    new_vertices = []

    for i in range(len(x_coords)):
        new_vertices.append((x_coords[i], y_coords[i]))

    return new_vertices


def _polygon_parts(geometry) -> list[Polygon]:
    """
    :param geometry: geometrie knihovny Shapely (např. Polygon, MultiPolygon, GeometryCollection)
    :return: polygony s nenulovým obsahem, ze kterých se geometrie skládá
    """

    if isinstance(geometry, Polygon):
        return [geometry] if geometry.area > 0 else []

    if hasattr(geometry, "geoms"):
        # složená geometrie
        parts = []

        for part in geometry.geoms:
            parts.extend(_polygon_parts(part))

        return parts

    # úsečka nebo bod
    return []


def get_polygon_from_points(points: list[Point2D]) -> Polygon:
    """
    :param points: seznam 2D bodů
    :return: instance třídy Polygon vytvořená z daných bodů
    """

    return Polygon([(point.get_x(), point.get_y()) for point in points])


RANDOM_POINT_ATTEMPTS = 1000   # počet náhodných pokusů, než se projdou všechny celočíselné body polygonu


def random_point_in_polygon(polygon: Polygon, excluded_point: Point2D | None = None) -> Point2D | None:
    """
    :param polygon: instance třídy Polygon
    :param excluded_point: bod, který nesmí být vrácen (žádný, pokud None)
    :return: náhodný celočíselný 2D bod uvnitř polygonu různý od excluded_point
            / None, pokud takový bod neexistuje
    """

    if polygon.is_empty:
        return None

    min_x, min_y, max_x, max_y = polygon.bounds
    min_x = round(min_x)
    max_x = round(max_x)
    min_y = round(min_y)
    max_y = round(max_y)

    for _ in range(RANDOM_POINT_ATTEMPTS):
        random_point = Point(random.randint(min_x, max_x), random.randint(min_y, max_y))

        if polygon.contains(random_point):
            point = Point2D(int(random_point.x), int(random_point.y))

            if point != excluded_point:
                return point

    # náhodné hledání neuspělo (např. velmi úzký polygon) -> projdou se všechny celočíselné body polygonu
    points = [Point2D(x, y) for x in range(min_x, max_x + 1) for y in range(min_y, max_y + 1)
              if Point2D(x, y) != excluded_point and polygon.contains(Point(x, y))]

    if len(points) == 0:
        # uvnitř polygonu není žádný vhodný celočíselný bod
        return None

    return random.choice(points)


def find_polygon_centroid(vertices: list[Point2D]) -> Point2D:
    """
    :param vertices: vrcholy polygonu
    :return: centroid (geometrický střed) polygonu jako 2D bod
    """

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
    """
    :param vertices: vrcholy polygonu
    :return: dva vrcholy tvořící nejdelší stranu polygonu
    """

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
    """
    Rozdělí polygon na dva polygony. Dělicí úsečka vede od středu nejdelší strany polygonu do středu
    jiné strany, který je nejdále od prvního středu.
    :param vertices: vrcholy polygonu
    :return: seznam obsahující dva seznamy vrcholů polygonů
            / seznam obsahující jeden seznam vrcholů polygonů
            (původní vrcholy, nepodařilo se polygon rozdělit)
    """

    # nalezení středu nejdelší strany polygonu
    longest_side = find_polygon_longest_side(vertices)

    if longest_side[0] is None or longest_side[1] is None:
        return [vertices]  # vrácení původního polygonu

    center1 = longest_side[0].line_center(longest_side[1])

    # nalezení středu strany, který je nejdále od prvního středu
    center_max_distance = -sys.maxsize
    center2 = None

    for i in range(len(vertices)):
        vertex1 = vertices[i]
        vertex2 = vertices[(i + 1) % len(vertices)]

        center = vertex1.line_center(vertex2)  # střed aktuální strany
        distance = center.euclidean_distance(center1)  # vzdálenost aktuálního středu od prvního středu

        if distance > center_max_distance:
            center_max_distance = distance
            center2 = center

    polygon = Polygon([[vertex.get_x(), vertex.get_y()] for vertex in vertices])
    line = LineString([[center1.get_x(), center1.get_y()], [center2.get_x(), center2.get_y()]])  # dělicí úsečka

    # rozdělení polygonu dělicí úsečkou
    split_polygons = []

    try:
        parts = polygon.difference(line.buffer(1))
    except Exception:
        return [vertices]  # vrácení původního polygonu

    if parts.geom_type == "MultiPolygon":
        # úspěšné rozdělení na 2 polygony
        for geom in parts.geoms:
            split_polygons.append(list(geom.exterior.coords)[:-1])
    else:
        # úsečka nerozdělila polygon (např. polygon příliš malý)
        return [vertices]  # vrácení původního polygonu

    result = []
    for polygon in split_polygons:
        # rozdělené polygony do správného formátu
        result.append([Point2D(round(vertex[0]), round(vertex[1])) for vertex in polygon])

    return result


def remove_similar_points(points: list[Point2D], min_distance_between_points: int) -> list[Point2D]:
    """
    :param points: vstupní body
    :param min_distance_between_points: minimální vzdálenost mezi body
    :return: seznam vstupních bodů, ze kterého byly odebrány příliš blízké body
    """

    # vytvoření datové struktury KD-tree z bodů
    point_tuples = [(point.get_x(), point.get_y()) for point in points]
    tree = KDTree(point_tuples)

    unique_points = []
    visited_indices = set()  # indexy již nepotřebných bodů

    for i in range(len(point_tuples)):
        point = point_tuples[i]

        if i in visited_indices:
            continue

        unique_points.append(points[i])

        # nalezení všech bodů, které jsou blízko aktuálního bodu
        nearby_points_indices = tree.query_ball_point(point, min_distance_between_points)

        for point_index in nearby_points_indices:
            visited_indices.add(point_index)

    return unique_points
