from scipy.spatial import Voronoi
from shapely import Polygon

from tesellations.a_tesellation import *
from geometry.voronoi_region import *
from geometry.a_region import *


class VoronoiTesellation(ATesellation):
    def generate_regions(self, points: list[Point], image: ImageFile) -> list[ARegion]:
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
                vertices = self.crop_polygon_by_bounds(bounds, vertices)

            points = [Point(round(vertex[0]), round(vertex[1])) for vertex in vertices]
            generator = Point(round(vor_point[0]), round(vor_point[1]))
            base_color_int = image.getpixel((generator.get_x(), generator.get_y()))

            if len(base_color_int) == 3:  # převod RGB na RGBA
                base_color_int = base_color_int + (255,)

            base_color_float = tuple(primary_color / 255 for primary_color in base_color_int)

            new_region = VoronoiRegion(points, generator, base_color_float)
            regions.append(new_region)

        return regions

    def crop_polygon_by_bounds(self, bounds: list[Tuple[float, float]],
                               vertices: list[Tuple[float, float]]) -> list[Tuple[float, float]]:

        intersecting_polygon = Polygon(vertices)
        bounding_polygon = Polygon(bounds)
        cropped_polygon = intersecting_polygon.intersection(bounding_polygon)

        x_coords, y_coords = cropped_polygon.exterior.xy
        new_vertices = []

        for i in range(len(x_coords)):
            new_vertices.append((x_coords[i], y_coords[i]))

        return new_vertices

