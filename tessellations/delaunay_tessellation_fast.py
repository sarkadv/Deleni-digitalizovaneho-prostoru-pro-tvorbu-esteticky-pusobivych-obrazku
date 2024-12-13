from PIL.ImageFile import ImageFile

from tessellations.a_delaunay_tessellation import ADelaunayTessellation
from util.color_utils import find_points_most_common_color
from util.geometry_utils import *


class DelaunayTessellationFast(ADelaunayTessellation):

    def get_base_color(self, image: ImageFile, vertices: list[Point2D]) -> Tuple[float, float, float]:
        # počet nalezených bodů pro daný polygon
        vertices_polygon_format = [[vertex.get_x(), vertex.get_y()] for vertex in vertices]
        region_chosen_points_count = int(Polygon(vertices_polygon_format).area / 2)

        # v každém polygonu se nalezne pouze daný počet bodů
        points = find_points_in_polygon(vertices, region_chosen_points_count, image)
        return find_points_most_common_color(image, points)[0]
