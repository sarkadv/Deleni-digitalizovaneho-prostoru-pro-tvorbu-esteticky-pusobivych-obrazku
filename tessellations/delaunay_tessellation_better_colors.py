from tessellations.a_delaunay_tessellation import ADelaunayTessellation
from util.color_utils import find_points_most_common_colors
from util.geometry_utils import *


class DelaunayTessellationBetterColors(ADelaunayTessellation):
    """
    Třída reprezentuje dělení prostoru Delaunayho triangulací.
    Základní barva oblastí je určena podle všech celočíselných bodů uvnitř oblasti.
    """

    def get_base_color(self, image: Image, vertices: list[Point2D]) -> Tuple[float, float, float]:
        # v každém polygonu se naleznou všechny celočíselné body
        points = find_points_in_polygon(vertices, -1, image)
        return find_points_most_common_colors(image, points)[0]
