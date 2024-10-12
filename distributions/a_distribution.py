from abc import ABC, abstractmethod

from PIL.ImageFile import ImageFile

from geometry.point import Point


class ADistribution(ABC):

    @abstractmethod
    def generate_points(self, image: ImageFile) -> list[Point]:
        pass
