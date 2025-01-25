from geometry.quadtree_region import QuadtreeRegion
from tessellations.a_tessellation import *
from geometry.a_region import *
from util.color_utils import get_rectangle_average_color, get_rectangle_color_standard_deviation
from util.geometry_utils import *


class QuadtreeTessellation(ATessellation):
    MAX_STANDARD_DEVIATION = 0.12  # maximální směrodatná odchylka barev regionu
    MIN_AREA = 0  # minimální obsah obdélníku, výpočet při startu dělení
    MIN_AREA_DIVISOR = 10_000

    def generate_regions(self, points: list[Point2D], image: Image) -> list[ARegion]:
        self.MIN_AREA = image.width * image.height / self.MIN_AREA_DIVISOR

        stack = []
        regions = []    # hotové regiony bez potomků

        # pole points musí mít vždy body v pořadí od NW a poté po směru hodinových ručiček
        first_region = QuadtreeRegion(points, (0, 0, 0))  # region obsahující celý obrázek
        stack.append(first_region)

        while len(stack) > 0:
            region = stack.pop()

            point_NW = region.get_vertices()[0]
            point_NE = region.get_vertices()[1]
            point_SE = region.get_vertices()[2]
            point_SW = region.get_vertices()[3]

            average_color = get_rectangle_average_color(region.get_vertices(), image)
            region.set_base_color(average_color)

            # výpočet obsahu obdélníku
            side_length_a = point_NE.get_x() - point_NW.get_x()
            side_length_b = point_SW.get_y() - point_NW.get_y()
            area = side_length_a * side_length_b

            if area < self.MIN_AREA:
                # region hotový
                regions.append(region)
                continue

            standard_deviation = get_rectangle_color_standard_deviation(region.get_vertices(), image, average_color)

            if standard_deviation <= self.MAX_STANDARD_DEVIATION:
                # region hotový
                regions.append(region)
                continue

            # rozdělení na 4 obdélníky

            # rozdělení v polovině v obou osách
            x_division = round((point_NE.get_x() - point_NW.get_x()) / 2) + point_NW.get_x()
            y_division = round((point_SW.get_y() - point_NW.get_y()) / 2) + point_NW.get_y()

            # levý horní obdélník
            corners_NW = [point_NW, Point2D(x_division, point_NW.get_y()),
                          Point2D(x_division, y_division), Point2D(point_NW.get_x(), y_division)]

            # pravý horní obdélník
            corners_NE = [Point2D(x_division, point_NE.get_y()), point_NE,
                          Point2D(point_NE.get_x(), y_division), Point2D(x_division, y_division)]

            # pravý dolní obdélník
            corners_SE = [Point2D(x_division, y_division), Point2D(point_SE.get_x(), y_division),
                          point_SE, Point2D(x_division, point_SE.get_y())]

            # levý dolní obdélník
            corners_SW = [Point2D(point_SW.get_x(), y_division), Point2D(x_division, y_division),
                          Point2D(x_division, point_SW.get_y()), point_SW]

            child_NW = QuadtreeRegion(corners_NW, average_color)
            child_NE = QuadtreeRegion(corners_NE, average_color)
            child_SE = QuadtreeRegion(corners_SE, average_color)
            child_SW = QuadtreeRegion(corners_SW, average_color)

            # uložení potomků na zásobník
            stack.extend([child_NW, child_NE, child_SE, child_SW])

        return regions
