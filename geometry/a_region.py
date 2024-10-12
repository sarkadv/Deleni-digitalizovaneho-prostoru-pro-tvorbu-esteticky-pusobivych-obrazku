from abc import ABC, abstractmethod

from geometry.point import *


class ARegion(ABC):
    def __init__(self, vertices: list[Point]):
        self.__vertices = vertices

    def get_vertices(self) -> list[Point]:
        return self.__vertices

    @abstractmethod
    def draw(self) -> None:
        pass

