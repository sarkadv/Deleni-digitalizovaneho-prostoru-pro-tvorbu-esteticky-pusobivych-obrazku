from abc import ABC, abstractmethod

from PIL import Image

from geometry.point_2d import Point2D
from geometry.a_region import ARegion


class ATessellation(ABC):

    @abstractmethod
    def generate_regions(self, points: list[Point2D], image: Image) -> list[ARegion]:
        pass
