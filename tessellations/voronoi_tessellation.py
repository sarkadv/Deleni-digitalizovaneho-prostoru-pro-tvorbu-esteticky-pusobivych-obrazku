from scipy.spatial import Voronoi
from shapely import Polygon

from tessellations.a_tessellation import *
from geometry.voronoi_region import *
from geometry.a_region import *
from util.image_utils import *


class VoronoiTessellation(ATessellation):
    def generate_regions(self, points: list[Point2D], image: ImageFile) -> list[ARegion]:
        # přidání okrajových bodů, aby nebyly uvnitř obrázku vytvářeny nekonvexní regiony
        image_longer_side = max(image.width, image.height)

        points.append(Point2D(-image_longer_side * 4, -image_longer_side * 4))
        points.append(Point2D(image_longer_side * 4, -image_longer_side * 4))
        points.append(Point2D(image_longer_side * 4, image_longer_side * 4))
        points.append(Point2D(-image_longer_side * 4, image_longer_side * 4))

        coordinates = [[point.get_x(), point.get_y()] for point in points]

        voronoi = Voronoi(coordinates)

        regions = []

        for i in range(0, len(voronoi.point_region)):
            vor_point = voronoi.points[i]
            vor_region_index = voronoi.point_region[i]
            vor_region = voronoi.regions[vor_region_index]

            if len(vor_region) < 1:
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

                    if x_coord < 0 or x_coord > image.width or y_coord < 0 or y_coord > image.height:
                        intersects_bounds = True

                    vertices.append((x_coord, y_coord))

            if infinite:
                continue  # region zahodíme, pokračujeme dalším

            if intersects_bounds:
                bounds = [(0, 0), (0, image.height), (image.width, image.height), (image.width, 0)]
                vertices = self.__crop_polygon_by_bounds(bounds, vertices)

            points = [Point2D(round(vertex[0]), round(vertex[1])) for vertex in vertices]
            generator = Point2D(round(vor_point[0]), round(vor_point[1]))

            base_color_float = self.__get_base_color(image, generator)

            new_region = VoronoiRegion(points, generator, base_color_float)
            regions.append(new_region)

        return regions

    def __crop_polygon_by_bounds(self, bounds: list[Tuple[float, float]],
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

    def __get_base_color(self, image: ImageFile, generator: Point2D) -> Tuple[float, float, float, float]:
        base_color_int = image.getpixel((generator.get_x(), generator.get_y()))

        base_color_float = color_int_to_float(base_color_int)

        if len(base_color_float) == 3:  # převod RGB na RGBA
            base_color_float = base_color_float + (1.0,)

        return base_color_float

