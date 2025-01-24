from scipy.spatial import Voronoi

from tessellations.a_tessellation import *
from geometry.voronoi_region import *
from geometry.a_region import *
from util.color_utils import get_point_color
from util.geometry_utils import *


class VoronoiTessellation(ATessellation):
    def generate_regions(self, points: list[Point2D], image: Image) -> list[ARegion]:
        # přidání okrajových bodů, aby nebyly uvnitř obrázku vytvářeny nekonvexní regiony
        image_longer_side = max(image.width, image.height)
        far_points = [Point2D(-image_longer_side * 4, -image_longer_side * 4),
                      Point2D(image_longer_side * 4, -image_longer_side * 4),
                      Point2D(image_longer_side * 4, image_longer_side * 4),
                      Point2D(-image_longer_side * 4, image_longer_side * 4)]

        points.extend(far_points)

        coordinates = [[point.get_x(), point.get_y()] for point in points]

        # hranice obrázku
        bounds = [(0, 0), (0, image.height), (image.width, image.height), (image.width, 0)]

        voronoi = Voronoi(coordinates)

        regions = []

        for i in range(len(voronoi.point_region)):
            generator = voronoi.points[i]
            region_index = voronoi.point_region[i]
            region = voronoi.regions[region_index]

            if len(region) < 1:
                continue

            vertices = []
            infinite = False
            intersects_bounds = False

            for index in region:
                if index == -1:
                    infinite = True
                    break
                else:
                    vertex = voronoi.vertices[index]
                    x_coord = round(vertex[0])
                    y_coord = round(vertex[1])

                    if not is_point_in_image(image, Point2D(x_coord, y_coord)):
                        intersects_bounds = True

                    vertices.append((x_coord, y_coord))

            if infinite:
                continue  # nekonvexní region mimo obrázek, zahodime a pokračujeme dalším

            if intersects_bounds:
                vertices = crop_polygon_by_bounds(bounds, vertices)

            points = [Point2D(round(vertex[0]), round(vertex[1])) for vertex in vertices]
            generator = Point2D(round(generator[0]), round(generator[1]))

            base_color_float = get_point_color(image, generator)

            new_region = VoronoiRegion(points, generator, base_color_float)
            regions.append(new_region)

        return regions
