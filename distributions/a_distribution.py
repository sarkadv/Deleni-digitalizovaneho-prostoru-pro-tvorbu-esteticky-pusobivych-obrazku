from abc import ABC, abstractmethod

from PIL import Image

from geometry.point_2d import Point2D


class ADistribution(ABC):

    @abstractmethod
    def generate_points(self, image: Image, x_min: int, x_max: int, y_min: int, y_max: int) -> list[Point2D]:
        pass
