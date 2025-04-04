from distributions.a_distribution import *
from geometry.point_2d import *


class QuadtreeDistribution(ADistribution):
    """
    Třída představující rozdělení bodů dle kvadrantového stromu.
    Vygenerované body jsou pouze rohy obrázku definující prostor, který má kvadrantový strom rozdělit.
    """

    def generate_points(self, image: Image, x_min: int, x_max: int, y_min: int, y_max: int) -> list[Point2D]:
        # vrácení rohů obrázku
        return [Point2D(0, 0), Point2D(image.width, 0), Point2D(image.width, image.height), Point2D(0, image.height)]
