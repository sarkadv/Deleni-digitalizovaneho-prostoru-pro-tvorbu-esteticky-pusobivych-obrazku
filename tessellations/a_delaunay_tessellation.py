from abc import abstractmethod

from scipy.spatial import Delaunay

from geometry.a_region import ARegion
from geometry.delaunay_region import DelaunayRegion
from tessellations.a_tessellation import ATessellation
from util.geometry_utils import *


class ADelaunayTessellation(ATessellation):
    """
    Abstraktní třída reprezentující dělení prostoru Delaunayho triangulací.
    """

    def generate_regions(self, points: list[Point2D], image: Image) -> list[ARegion]:
        # přidání okrajových bodů, aby byly vytvořeny trojúhelníky po celém obrazu
        bounds = [Point2D(0, 0), Point2D(image.width - 1, image.height - 1),
                  Point2D(0, image.height - 1), Point2D(image.width - 1, 0)]

        points.extend(bounds)

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
        """
        Metoda určí základní barvu Delaunayho oblasti podle pravidel implementující třídy.
        :param image: vstupní obrázek
        :param vertices: vrcholy Delaunayho oblasti (trojúhelníku)
        :return: základní barva oblasti
        """
        pass
