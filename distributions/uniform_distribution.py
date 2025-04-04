import scipy.stats as stats
from distributions.a_distribution import *
from geometry.point_2d import *
from util.geometry_utils import remove_similar_points


class UniformDistribution(ADistribution):
    """
    Třída reprezentující rozdělení bodů dle rovnoměrného rozložení.
    """

    # vhodně zvolené konstanty pro výpočet parametrů
    POINT_COUNT_MULTIPLIER = 100_000
    MIN_DISTANCE_BETWEEN_POINTS = 0
    DISTANCE_DIVISOR = 100

    def generate_points(self, image: Image, x_min: int, x_max: int, y_min: int, y_max: int) -> list[Point2D]:
        self.MIN_DISTANCE_BETWEEN_POINTS = int(min(image.width, image.height) / self.DISTANCE_DIVISOR)
        point_count = round(math.log((image.width * image.height * self.POINT_COUNT_MULTIPLIER) ** 2, 1.05)) * 2
        points = []

        # náhodné proměnné diskrétního rovnoměrného rozdělení
        uniform_discrete_variable_x = stats.randint(low=x_min, high=x_max)
        uniform_discrete_variable_y = stats.randint(low=y_min, high=y_max)

        coordinates_x = uniform_discrete_variable_x.rvs(size=point_count)
        coordinates_y = uniform_discrete_variable_y.rvs(size=point_count)

        for i in range(0, point_count):
            points.append(Point2D(int(coordinates_x[i]), int(coordinates_y[i])))

        # odstranění příliš blízkých bodů
        points = remove_similar_points(points, self.MIN_DISTANCE_BETWEEN_POINTS)
        return points
