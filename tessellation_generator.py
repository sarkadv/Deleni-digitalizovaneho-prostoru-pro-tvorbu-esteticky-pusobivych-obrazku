from enums.tessellation_type import *
from tessellations.delaunay_tessellation_better_colors import DelaunayTessellationBetterColors
from tessellations.delaunay_tessellation_fast import DelaunayTessellationFast
from tessellations.quadtree_tessellation import QuadtreeTessellation
from tessellations.voronoi_tessellation import *


class TesellationGenerator:
    def __init__(self, points: list[Point2D], image: Image, tessellation_type: TessellationType):
        self.__points = points
        self.__image = image

        if tessellation_type == TessellationType.VORONOI:
            self.__tesellation = VoronoiTessellation()
        elif tessellation_type == TessellationType.DELAUNAY_FAST:
            self.__tesellation = DelaunayTessellationFast()
        elif tessellation_type == TessellationType.DELAUNAY_BETTER_COLORS:
            self.__tesellation = DelaunayTessellationBetterColors()
        elif tessellation_type == TessellationType.QUADTREE:
            self.__tesellation = QuadtreeTessellation()

    def generate_regions(self) -> list[ARegion]:
        return self.__tesellation.generate_regions(self.__points, self.__image)
