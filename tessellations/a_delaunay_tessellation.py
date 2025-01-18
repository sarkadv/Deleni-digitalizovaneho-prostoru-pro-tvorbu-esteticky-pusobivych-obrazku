from abc import abstractmethod

from scipy.spatial import Delaunay

from geometry.a_region import ARegion
from geometry.delaunay_region import DelaunayRegion
from tessellations.a_tessellation import ATessellation
from util.geometry_utils import *


class ADelaunayTessellation(ATessellation):
    def generate_regions(self, points: list[Point2D], image: Image) -> list[ARegion]:
        # přidání okrajových bodů, aby byly vytvořeny trojúhelníky po celém obrazu
        top_left = Point2D(0, 0)
        top_right = Point2D(image.width - 1, image.height - 1)
        bottom_left = Point2D(0, image.height - 1)
        bottom_right = Point2D(image.width - 1, 0)

        if top_left not in points:
            points.append(top_left)
        if top_right not in points:
            points.append(top_right)
        if bottom_left not in points:
            points.append(bottom_left)
        if bottom_right not in points:
            points.append(bottom_right)

        coordinates = [[point.get_x(), point.get_y()] for point in points]

        delaunay = Delaunay(coordinates)

        regions = []

        for triangle in delaunay.simplices:
            vertices = []

            for index in triangle:
                vertices.append(delaunay.points[index])

            points = [Point2D(round(vertex[0]), round(vertex[1])) for vertex in vertices]

            base_color_float = self.get_base_color(image, points)

            new_region = DelaunayRegion(points, base_color_float)
            regions.append(new_region)

        return regions

    @abstractmethod
    def get_base_color(self, image: Image, vertices: list[Point2D]) -> Tuple[float, float, float]:
        pass
