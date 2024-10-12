from typing import Tuple

from geometry.a_region import *


class VoronoiRegion(ARegion):
    def __init__(self, vertices: list[Point], seed: Point):
        super().__init__(vertices)
        self.__seed = seed

    def draw(self) -> None:
        pass

    def get_seed(self) -> Point:
        return self.__seed
