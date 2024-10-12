from scipy.spatial import Voronoi

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

            if -1 in vor_region:
                vor_region.remove(-1)

            vertices = [voronoi.vertices[index] for index in vor_region]
            points = [Point(round(vertex[0]), round(vertex[1])) for vertex in vertices]
            seed = Point(round(vor_point[0]), round(vor_point[1]))

            new_region = VoronoiRegion(points, seed)
            regions.append(new_region)

        return regions
