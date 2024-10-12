from enums.distribution_type import *
from distributions.uniform_distribution import *


class PointGenerator:
    def __init__(self, image: ImageFile, distribution_type: DistributionType):
        self.__image = image

        if distribution_type == DistributionType.UNIFORM:
            self.__distribution = UniformDistribution()
        else:   # placeholder
            self.__distribution = UniformDistribution()

    def generate_points(self) -> list[Point]:
        return self.__distribution.generate_points(self.__image)
