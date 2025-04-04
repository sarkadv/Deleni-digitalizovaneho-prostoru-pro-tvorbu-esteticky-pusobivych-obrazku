from abc import ABC, abstractmethod

from PIL import Image

from geometry.point_2d import Point2D
from geometry.a_region import ARegion


class ATessellation(ABC):
    """
    Abstraktní třída reprezentující určitý typ dělení prostoru.
    """

    @abstractmethod
    def generate_regions(self, points: list[Point2D], image: Image) -> list[ARegion]:
        """
        Každá třída představující dělení prostoru musí tuto metodu implementovat.
        Metoda podle počáteční množiny bodů rozdělí prostor podle principů dané teselace a výsledné
        oblasti vrátí.
        :param points: počáteční množina bodů
        :param image: vstupní obrázek
        :return: seznam oblastí rozděleného prostoru
        """
        pass
