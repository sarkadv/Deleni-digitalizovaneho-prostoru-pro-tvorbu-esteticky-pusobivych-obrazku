from distributions.error_distribution import ErrorDistribution
from distributions.laplace_distribution_area import LaplaceDistributionArea
from distributions.laplace_distribution_gradient import LaplaceDistributionGradient
from distributions.laplace_distribution_length import LaplaceDistributionLength
from distributions.mitchell_distribution import MitchellDistribution
from distributions.normal_distribution_thirds import NormalDistributionThirds
from distributions.quadtree_distribution import QuadtreeDistribution
from distributions.uniform_distribution import *
from enums.distribution_type import *


class PointGenerator:
    def __init__(self, image: Image, distribution_type: DistributionType,
                 x_min: int, x_max: int, y_min: int, y_max: int):

        self.__image = image
        self.__x_min = x_min
        self.__x_max = x_max
        self.__y_min = y_min
        self.__y_max = y_max

        if distribution_type == DistributionType.UNIFORM:
            self.__distribution = UniformDistribution()

        elif distribution_type == DistributionType.NORMAL_THIRDS:
            self.__distribution = NormalDistributionThirds()

        elif distribution_type == DistributionType.LAPLACE_AREA:
            self.__distribution = LaplaceDistributionArea()

        elif distribution_type == DistributionType.LAPLACE_LENGTH:
            self.__distribution = LaplaceDistributionLength()

        elif distribution_type == DistributionType.LAPLACE_GRADIENT:
            self.__distribution = LaplaceDistributionGradient()

        elif distribution_type == DistributionType.QUADTREE:
            self.__distribution = QuadtreeDistribution()

        elif distribution_type == DistributionType.ERROR:
            self.__distribution = ErrorDistribution()

        elif distribution_type == DistributionType.MITCHELL:
            self.__distribution = MitchellDistribution()

    def generate_points(self) -> list[Point2D]:
        return self.__distribution.generate_points(self.__image, self.__x_min, self.__x_max, self.__y_min, self.__y_max)
