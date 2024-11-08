from PIL import ImageFile

from distributions.a_laplace_distribution import ALaplaceDistribution
from geometry.point_2d import *
from util.image_utils import find_polygon_centroid


class LaplaceDistributionArea(ALaplaceDistribution):
    def split_triangle(self, points: list[Point2D], image: ImageFile) -> list[Point2D]:
        if len(points) < 3:
            return []

        p1 = points[0]
        p2 = points[1]
        p3 = points[2]

        # obsah trojúhelníku
        area = abs(p1.get_x() * (p2.get_y() - p3.get_y())
                   + p2.get_x() * (p3.get_y() - p1.get_y())
                   + p3.get_x() * (p1.get_y() - p2.get_y())) / 2

        if area > self.MAX_TRIANGLE_AREA:
            # trojúhelník má příliš velký obsah
            return [find_polygon_centroid(points)]
        else:
            return []
