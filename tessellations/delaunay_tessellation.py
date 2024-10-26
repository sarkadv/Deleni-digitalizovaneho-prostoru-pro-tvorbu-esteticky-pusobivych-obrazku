import random

import numpy as np
from PIL.ImageFile import ImageFile
from scipy.spatial import Delaunay

from geometry.a_region import ARegion
from geometry.delaunay_region import DelaunayRegion
from tessellations.a_tessellation import ATessellation
from util.image_utils import *


class DelaunayTessellation(ATessellation):

    REGION_CHOSEN_POINTS_COUNT = 100

    def generate_regions(self, points: list[Point2D], image: ImageFile) -> list[ARegion]:
        # přidání okrajových bodů, aby byly vytvořeny trojúhelníky po celém obrazu
        points.append(Point2D(0, 0))
        points.append(Point2D(image.width, image.height))
        points.append(Point2D(0, image.height))
        points.append(Point2D(image.width, 0))

        coordinates = [[point.get_x(), point.get_y()] for point in points]

        delaunay = Delaunay(coordinates)

        regions = []

        for triangle in delaunay.simplices:
            vertices = []

            for index in triangle:
                vertices.append(delaunay.points[index])

            points = [Point2D(round(vertex[0]), round(vertex[1])) for vertex in vertices]

            base_color_float = self.__get_base_color(image, points)

            new_region = DelaunayRegion(points, base_color_float)
            regions.append(new_region)

        return regions

    def __get_base_color(self, image: ImageFile, vertices: list[Point2D]) -> Tuple[float, float, float, float]:
        points = find_points_in_polygon(vertices, self.REGION_CHOSEN_POINTS_COUNT, image)
        return find_points_mode_color(image, points)
