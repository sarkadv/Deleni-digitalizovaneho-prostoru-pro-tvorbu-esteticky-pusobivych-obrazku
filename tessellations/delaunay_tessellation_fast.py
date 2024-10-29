from PIL.ImageFile import ImageFile

from tessellations.a_delaunay_tessellation import ADelaunayTessellation
from util.image_utils import *


class DelaunayTessellationFast(ADelaunayTessellation):
    REGION_CHOSEN_POINTS_COUNT = 100

    def get_base_color(self, image: ImageFile, vertices: list[Point2D]) -> Tuple[float, float, float, float]:
        # v každém polygonu se nalezne pouze daný počet bodů
        points = find_points_in_polygon(vertices, self.REGION_CHOSEN_POINTS_COUNT, image)
        return find_points_mode_color(image, points)
