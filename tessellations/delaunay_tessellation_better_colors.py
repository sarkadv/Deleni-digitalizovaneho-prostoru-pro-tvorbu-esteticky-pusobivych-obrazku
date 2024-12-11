from PIL.ImageFile import ImageFile

from tessellations.a_delaunay_tessellation import ADelaunayTessellation
from util.image_utils import *


class DelaunayTessellationBetterColors(ADelaunayTessellation):
    def get_base_color(self, image: ImageFile, vertices: list[Point2D]) -> Tuple[float, float, float]:
        # v každém polygonu se naleznou všechny celočíselné body
        points = find_points_in_polygon(vertices, -1, image)
        return find_points_most_common_color(image, points)[0]
