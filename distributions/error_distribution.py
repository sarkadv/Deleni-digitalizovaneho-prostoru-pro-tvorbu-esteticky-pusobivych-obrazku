import sys

import numpy as np
from scipy.spatial import Voronoi

from distributions.a_distribution import *
from distributions.uniform_distribution import UniformDistribution
from util.image_utils import *


class ErrorDistribution(ADistribution):
    MAX_STANDARD_DEVIATION = 0.15  # maximální směrodatná odchylka barev regionu
    MIN_AREA_SIZE = 0   # minimální obsah oblasti

    MIN_AREA_SIZE_DIVISOR = 10_000
    POINT_COUNT_MULTIPLIER = 100_000

    def generate_points(self, image: ImageFile, x_min: int, x_max: int, y_min: int, y_max: int) -> list[Point2D]:
        self.MIN_AREA_SIZE = image.width * image.height / self.MIN_AREA_SIZE_DIVISOR

        # počáteční body vygenerovány náhodně rovnoměrným rozdělením
        uniform_distribution = UniformDistribution()
        starter_points = uniform_distribution.generate_points(image, x_min, x_max, y_min, y_max)

        # přidání okrajových bodů, aby nebyly uvnitř obrázku vytvářeny nekonvexní regiony
        image_longer_side = max(image.width, image.height)

        starter_points.append(Point2D(-image_longer_side * 4, -image_longer_side * 4))
        starter_points.append(Point2D(image_longer_side * 4, -image_longer_side * 4))
        starter_points.append(Point2D(image_longer_side * 4, image_longer_side * 4))
        starter_points.append(Point2D(-image_longer_side * 4, image_longer_side * 4))

        coordinates = [[point.get_x(), point.get_y()] for point in starter_points]

        # hranice obrázku
        bounds = [(0, 0), (0, image.height - 1), (image.width - 1, image.height - 1), (image.width - 1, 0)]

        complete_regions_generators = set()     # body generující finální oblast
        change = True

        while change:
            change = False
            voronoi = Voronoi(coordinates)

            for i in range(0, len(voronoi.point_region)):
                vor_point = voronoi.points[i]
                generator = Point2D(int(vor_point[0]), int(vor_point[1]))

                if generator in complete_regions_generators:
                    # oblast finální
                    continue

                vor_region_index = voronoi.point_region[i]
                vor_region = voronoi.regions[vor_region_index]

                if len(vor_region) < 1:
                    complete_regions_generators.add(generator)
                    continue

                vertices = []
                infinite = False
                intersects_bounds = False

                for index in vor_region:
                    if index == -1:
                        infinite = True
                        break
                    else:
                        vertex = voronoi.vertices[index]
                        x_coord = round(vertex[0])
                        y_coord = round(vertex[1])
                        vertices.append((x_coord, y_coord))

                        if not intersects_bounds and \
                                (x_coord < 0 or x_coord >= image.width or y_coord < 0 or y_coord >= image.height):
                            intersects_bounds = True

                if infinite:
                    # oblast je mimo obrázek, není nutné se jí zabývat
                    complete_regions_generators.add(generator)
                    continue

                points = [Point2D(round(vertex[0]), round(vertex[1])) for vertex in vertices]
                polygon = get_polygon_from_points(points)

                if polygon.area < self.MIN_AREA_SIZE:
                    # oblast polygonu menší než minimální povolená, polygon se dále nedělí
                    complete_regions_generators.add(generator)
                    continue

                region_standard_deviation = self.__get_polygon_color_standard_deviation(points, generator,
                                                                                        image, bounds,
                                                                                        intersects_bounds)

                if region_standard_deviation > self.MAX_STANDARD_DEVIATION:
                    change = True

                    if intersects_bounds:
                        # oříznutí polygonu, aby nebyl nový bod vygenerován mimo obrázek
                        cropped_polygon = Polygon(crop_polygon_by_bounds(bounds, vertices))
                    else:
                        cropped_polygon = Polygon(vertices)

                    # nový bod v oblasti
                    new_point = random_point_in_polygon(cropped_polygon)

                    while new_point.__eq__(generator):
                        new_point = random_point_in_polygon(cropped_polygon)

                    coordinates.append([new_point.get_x(), new_point.get_y()])

                else:
                    complete_regions_generators.add(generator)

        return [Point2D(coordinate[0], coordinate[1]) for coordinate in coordinates]

    def __get_polygon_color_standard_deviation(self, vertices: list[Point2D], generator: Point2D,
                                               image: Image, bounds: list[Tuple[float, float]],
                                               intersects_bounds: bool) -> float:

        # některé body polygonu
        points = self.__find_points_around_generator(image, vertices, generator, bounds, intersects_bounds)

        if len(points) <= 1:
            return 0

        average_color = find_points_average_color(image, points)

        sd_r = 0
        sd_g = 0
        sd_b = 0

        for point in points:
            r, g, b = image.getpixel((point.get_x(), point.get_y()))
            sd_r += (r / 255.0 - average_color[0]) ** 2
            sd_g += (g / 255.0 - average_color[1]) ** 2
            sd_b += (b / 255.0 - average_color[2]) ** 2

        sd_r = sd_r * (1.0 / (len(points) - 1))
        sd_g = sd_g * (1.0 / (len(points) - 1))
        sd_b = sd_b * (1.0 / (len(points) - 1))

        return math.sqrt(sd_r) + math.sqrt(sd_g) + math.sqrt(sd_b)

    def __find_points_around_generator(self, image: Image, points: list[Point2D], generator: Point2D,
                                       bounds: list[Tuple[float, float]], intersects_bounds: bool) -> list[Point2D]:

        vertices = [(point.get_x(), point.get_y()) for point in points]

        if intersects_bounds:
            # oříznutí polygonu, aby nebyly body nalezeny mimo obrázek
            cropped_polygon_vertices = crop_polygon_by_bounds(bounds, vertices)
            cropped_polygon = Polygon(cropped_polygon_vertices)
        else:
            cropped_polygon_vertices = vertices
            cropped_polygon = Polygon(vertices)

        cropped_points = [Point2D(int(vertex[0]), int(vertex[1])) for vertex in cropped_polygon_vertices]

        if len(cropped_points) == 0:
            # nebyly nalezeny žádné vrcholy polygonu v obrázku
            return [generator]

        # nalezení maximální vzdálenosti mezi vrcholem polygonu a generátorem
        max_distance_x = -sys.maxsize
        max_distance_y = -sys.maxsize

        for point in cropped_points:
            distance_x = abs(point.get_x() - generator.get_x())
            distance_y = abs(point.get_y() - generator.get_y())

            if distance_x > max_distance_x:
                max_distance_x = distance_x

            if distance_y > max_distance_y:
                max_distance_y = distance_y

        # směrodatná odchylka je třetina z maximální vzdálenosti
        # naprostá většina bodů bude vygenerována v menší vzdálenosti od generátoru než v maximální
        st_dev_x = max_distance_x / 3
        st_dev_y = max_distance_y / 3

        # vygenerování x, y souřadnic normálním rozdělením
        region_chosen_points_count = int(cropped_polygon.area / 2)
        normal_data_x = np.random.normal(generator.get_x(), st_dev_x, region_chosen_points_count)
        normal_data_y = np.random.normal(generator.get_y(), st_dev_y, region_chosen_points_count)

        result = set()

        for i in range(region_chosen_points_count):
            x = round(normal_data_x[i])
            y = round(normal_data_y[i])
            point = Point2D(x, y)

            # hledáme body, které jsou uvnitř obrázku a zároveň uvnitř polygonu
            if is_point_in_image(image, point) and cropped_polygon.contains(Point(x, y)):
                result.add(point)

        return list(result)
