import math

import scipy.stats as stats
from distributions.a_distribution import *
from geometry.point import *


class UniformDistribution(ADistribution):

    POINT_COUNT_MULTIPLIER = 100_000

    def generate_points(self, image: ImageFile) -> list[Point]:
        uniform_discrete_variable_x = stats.randint(low=1, high=image.width)
        uniform_discrete_variable_y = stats.randint(low=1, high=image.height)

        image_longer_side = max(image.width, image.height)

        point_count = round(math.log((image.width * image.height * self.POINT_COUNT_MULTIPLIER) ** 2, 1.05))
        points = []

        coordinates_x = uniform_discrete_variable_x.rvs(size=point_count)
        coordinates_y = uniform_discrete_variable_y.rvs(size=point_count)

        for i in range(0, point_count):
            points.append(Point(int(coordinates_x[i]), int(coordinates_y[i])))

        # přidání okrajových bodů, aby nebyly uvnitř obrázku vytvářeny nekonvexní regiony

        points.append(Point(-image_longer_side*4, -image_longer_side*4))
        points.append(Point(image_longer_side*4, -image_longer_side*4))
        points.append(Point(image_longer_side*4, image_longer_side*4))
        points.append(Point(-image_longer_side*4, image_longer_side*4))

        return list(set(points))    # odstranění duplicitních bodů
