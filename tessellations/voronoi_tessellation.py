from scipy.spatial import Voronoi

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

        # hranice obrázku
        bounds = [(0, 0), (0, image.height - 1), (image.width - 1, image.height - 1), (image.width - 1, 0)]

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

                    if not intersects_bounds and \
                            (x_coord < 0 or x_coord >= image.width or y_coord < 0 or y_coord >= image.height):
                        intersects_bounds = True

                    vertices.append((x_coord, y_coord))

            if infinite:
                continue  # region zahodíme, pokračujeme dalším

            if intersects_bounds:
                vertices = crop_polygon_by_bounds(bounds, vertices)

            points = [Point2D(round(vertex[0]), round(vertex[1])) for vertex in vertices]
            generator = Point2D(round(vor_point[0]), round(vor_point[1]))

            base_color_float = get_point_color(image, generator)

            new_region = VoronoiRegion(points, generator, base_color_float)
            regions.append(new_region)

        return regions
