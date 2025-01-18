from PIL import Image

from distributions.a_laplace_distribution import ALaplaceDistribution
from geometry.point_2d import *
from util.color_utils import find_points_average_color, get_point_color, get_colors_difference
from util.geometry_utils import find_polygon_centroid


class LaplaceDistributionGradient(ALaplaceDistribution):
    def split_triangle(self, points: list[Point2D], image: Image) -> list[Point2D]:
        if len(points) < 3:
            return []

        average_color = find_points_average_color(image, points)

        for point in points:
            point_color = get_point_color(image, point)

            difference = get_colors_difference(point_color, average_color)

            if difference > self.MAX_VERTEX_COLOR_DIFFERENCE:
                return [find_polygon_centroid(points)]

        return []
