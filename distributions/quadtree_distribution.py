from distributions.a_distribution import *
from geometry.point_2d import *


class QuadtreeDistribution(ADistribution):
    def generate_points(self, image: ImageFile, x_min: int, x_max: int, y_min: int, y_max: int) -> list[Point2D]:
        return [Point2D(0, 0), Point2D(image.width, 0), Point2D(image.width, image.height), Point2D(0, image.height)]
