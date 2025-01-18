from PIL import Image

from distributions.a_laplace_distribution import ALaplaceDistribution
from geometry.point_2d import *


class LaplaceDistributionLength(ALaplaceDistribution):
    def split_triangle(self, points: list[Point2D], image: Image) -> list[Point2D]:
        if len(points) < 3:
            return []

        new_points = []

        for i in range(len(points)):
            point = points[i]

            if i == len(points) - 1:
                # i je poslední index
                other = points[0]
            else:
                other = points[i + 1]

            if point.euclidean_distance(other) > self.MAX_SIDE_LENGTH:
                new_points.append(point.line_center(other))

        return new_points
