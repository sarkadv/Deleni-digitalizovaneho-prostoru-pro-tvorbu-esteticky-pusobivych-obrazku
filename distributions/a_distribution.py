from abc import ABC, abstractmethod

from PIL import Image

from geometry.point_2d import Point2D


class ADistribution(ABC):
    """
    Abstraktní třída představující různé způsoby rozdělení bodů do počáteční množiny teselace.
    """

    @abstractmethod
    def generate_points(self, image: Image, x_min: int, x_max: int, y_min: int, y_max: int) -> list[Point2D]:
        """
        Každá třída představující rozdělení bodů musí tuto metodu implementovat.
        Metoda vygeneruje a vrátí seznam bodů vybraných podle principů daného rozdělení.
        :param image: vstupní obrázek
        :param x_min: minimální souřadnice x bodů
        :param x_max: maximální souřadnice x bodů
        :param y_min: minimální souřadnice y bodů
        :param y_max: maximální souřadnice y bodů
        :return: seznam vygenerovaných bodů
        """
        pass
