from enums.distribution_type import *
from distributions.uniform_distribution import *


class PointGenerator:
    def __init__(self, image: ImageFile, distribution_type: DistributionType,
                 x_min: int, x_max: int, y_min: int, y_max: int):

        self.__image = image
        self.__x_min = x_min
        self.__x_max = x_max
        self.__y_min = y_min
        self.__y_max = y_max

        if distribution_type == DistributionType.UNIFORM:
            self.__distribution = UniformDistribution()
        else:   # placeholder
            self.__distribution = UniformDistribution()

    def generate_points(self) -> list[Point2D]:
        return self.__distribution.generate_points(self.__image, self.__x_min, self.__x_max, self.__y_min, self.__y_max)
