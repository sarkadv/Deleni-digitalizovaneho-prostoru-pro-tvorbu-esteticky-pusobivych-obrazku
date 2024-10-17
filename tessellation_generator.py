from enums.tessellation_type import *
from tessellations.delaunay_tessellation import DelaunayTessellation
from tessellations.voronoi_tessellation import *
from geometry.a_region import *


class TesellationGenerator:
    def __init__(self, points: list[Point2D], image: ImageFile, tessellation_type: TessellationType):
        self.__points = points
        self.__image = image

        if tessellation_type == TessellationType.VORONOI:
            self.__tesellation = VoronoiTessellation()
        elif tessellation_type == TessellationType.DELAUNAY:
            self.__tesellation = DelaunayTessellation()
        else:   # placeholder
            self.__tesellation = VoronoiTessellation()

    def generate_regions(self) -> list[ARegion]:
        return self.__tesellation.generate_regions(self.__points, self.__image)
