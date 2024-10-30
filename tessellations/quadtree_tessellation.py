from geometry.quadtree_region import QuadtreeRegion
from tessellations.a_tessellation import *
from geometry.a_region import *
from util.image_utils import *


class QuadtreeTessellation(ATessellation):
    REGION_CHOSEN_POINTS_COUNT = 100

    def generate_regions(self, points: list[Point2D], image: ImageFile) -> list[ARegion]:
        average_color = get_rectangle_average_color(points, image)
        region = QuadtreeRegion(points, average_color)


