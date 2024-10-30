from geometry.quadtree_region import QuadtreeRegion
from tessellations.a_tessellation import *
from geometry.a_region import *
from util.image_utils import *


class QuadtreeTessellation(ATessellation):
    MAX_STANDARD_DEVIATION = 0.15   # maximální směrodatná odchylka regionu
    MIN_AREA_SIZE = 15  # minimální obsah obdélníku

    def generate_regions(self, points: list[Point2D], image: ImageFile) -> list[ARegion]:
        stack = []

        # pole points musí mít vždy body v pořadí od levého horního a poté po směru hodinových ručiček
        first_region = QuadtreeRegion(points, (0, 0, 0, 0))     # region obsahující celý obrázek
        stack.append(first_region)

        while len(stack) > 0:
            region = stack.pop()

            # rohy regionu v pořadí levý horní, pravý horní, levý dolní, pravý dolní
            corners = [[region.get_vertices()[0], region.get_vertices()[1]],
                       [region.get_vertices()[3], region.get_vertices()[2]]]

            average_color = get_rectangle_average_color(region.get_vertices(), image)
            region.set_base_color(average_color)

            # výpočet obsahu obdélníku
            side_length_a = corners[0][1].get_x() - corners[0][0].get_x()
            side_length_b = corners[1][0].get_y() - corners[0][0].get_y()
            area = side_length_a * side_length_b

            if area < self.MIN_AREA_SIZE:
                continue

            standard_deviation = get_rectangle_color_standard_deviation(region.get_vertices(), image, average_color)

            if standard_deviation > self.MAX_STANDARD_DEVIATION:
                # rozdělení na 4 obdélníky
                children = [[None, None],
                            [None, None]]

                # rozdělení v polovině v obou osách
                x_division = int((corners[0][1].get_x() - corners[0][0].get_x()) / 2) + corners[0][0].get_x()
                y_division = int((corners[1][1].get_y() - corners[0][0].get_y()) / 2) + corners[0][0].get_y()

                # levý horní obdélník
                corners_upper_left = [corners[0][0], Point2D(x_division, corners[0][0].get_y()),
                                      Point2D(x_division, y_division), Point2D(corners[0][0].get_x(), y_division)]

                # pravý horní obdélník
                corners_upper_right = [Point2D(x_division, corners[0][1].get_y()), corners[0][1],
                                       Point2D(corners[0][1].get_x(), y_division), Point2D(x_division, y_division)]

                # levý dolní obdélník
                corners_bottom_right = [Point2D(x_division, y_division), Point2D(corners[1][1].get_x(), y_division),
                                        corners[1][1], Point2D(x_division, corners[1][1].get_y())]

                # pravý dolní obdélník
                corners_bottom_left = [Point2D(corners[1][0].get_x(), y_division), Point2D(x_division, y_division),
                                       Point2D(x_division, corners[1][0].get_y()), corners[1][0]]

                children[0][0] = QuadtreeRegion(corners_upper_left, average_color)
                children[0][1] = QuadtreeRegion(corners_upper_right, average_color)
                children[1][1] = QuadtreeRegion(corners_bottom_right, average_color)
                children[1][0] = QuadtreeRegion(corners_bottom_left, average_color)

                region.set_children(children)

                # uložení potomků na zásobník
                stack.extend([children[0][0], children[0][1], children[1][1], children[1][0]])

        # vracíme pouze region obsahující celý obrázek, ostatní regiony jsou v něm rekurzivně uložené
        return [first_region]
