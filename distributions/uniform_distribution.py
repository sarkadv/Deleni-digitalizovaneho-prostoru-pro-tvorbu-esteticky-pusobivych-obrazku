import math

import scipy.stats as stats
from distributions.a_distribution import *
from geometry.point_2d import *


class UniformDistribution(ADistribution):

    POINT_COUNT_MULTIPLIER = 100_000

    def generate_points(self, image: ImageFile, x_min: int, x_max: int, y_min: int, y_max: int) -> list[Point2D]:
        uniform_discrete_variable_x = stats.randint(low=x_min, high=x_max)
        uniform_discrete_variable_y = stats.randint(low=y_min, high=y_max)

        point_count = round(math.log((image.width * image.height * self.POINT_COUNT_MULTIPLIER) ** 2, 1.05))
        points = []

        coordinates_x = uniform_discrete_variable_x.rvs(size=point_count)
        coordinates_y = uniform_discrete_variable_y.rvs(size=point_count)

        for i in range(0, point_count):
            points.append(Point2D(int(coordinates_x[i]), int(coordinates_y[i])))

        return list(set(points))    # odstranění duplicitních bodů
