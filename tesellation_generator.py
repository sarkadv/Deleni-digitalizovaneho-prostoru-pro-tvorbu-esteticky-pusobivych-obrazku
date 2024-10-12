from enums.tesellation_type import *
from tesellations.voronoi_tesellation import *
from geometry.a_region import *


class TesellationGenerator:
    def __init__(self, points: list[Point], image: ImageFile, tesellation_type: TesellationType):
        self.__points = points
        self.__image = image

        if tesellation_type == TesellationType.VORONOI:
            self.__tesellation = VoronoiTesellation()
        else:   # placeholder
            self.__tesellation = VoronoiTesellation()

    def generate_regions(self) -> list[ARegion]:
        return self.__tesellation.generate_regions(self.__points, self.__image)
