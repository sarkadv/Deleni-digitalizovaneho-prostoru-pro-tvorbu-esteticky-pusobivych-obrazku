import scipy.stats as stats
from distributions.a_distribution import *
from geometry.point import *


class UniformDistribution(ADistribution):

    POINT_DIVISOR = 100_000

    def generate_points(self, image: ImageFile) -> list[Point]:
        uniform_discrete_variable_x = stats.randint(low=0, high=image.width + 1)
        uniform_discrete_variable_y = stats.randint(low=0, high=image.height + 1)

        point_count = round(image.width * image.height / self.POINT_DIVISOR)
        points = []

        coordinates_x = uniform_discrete_variable_x.rvs(size=point_count)
        coordinates_y = uniform_discrete_variable_y.rvs(size=point_count)

        for i in range(0, point_count):
            points.append(Point(int(coordinates_x[i]), int(coordinates_y[i])))

        return list(set(points))    # odstranění duplicitních bodů
