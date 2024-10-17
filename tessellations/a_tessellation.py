from abc import ABC, abstractmethod

from PIL.ImageFile import ImageFile

from geometry.point_2d import Point2D
from geometry.a_region import ARegion


class ATessellation(ABC):

    @abstractmethod
    def generate_regions(self, points: list[Point2D], image: ImageFile) -> list[ARegion]:
        pass
