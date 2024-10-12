from abc import ABC, abstractmethod

from PIL.ImageFile import ImageFile

from geometry.point import Point
from geometry.a_region import ARegion


class ATesellation(ABC):

    @abstractmethod
    def generate_regions(self, points: list[Point], image: ImageFile) -> list[ARegion]:
        pass
