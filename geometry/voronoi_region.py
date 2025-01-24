from geometry.a_region import *


class VoronoiRegion(ARegion):
    def __init__(self, vertices: list[Point2D], seed: Point2D, base_color: Tuple[float, float, float]):
        super().__init__(vertices, base_color)
        self.__generator = seed

    def draw_multiple_shapes(self, context: cairo.Context):
        pass

    def draw_rectangle_with_oval(self, context: cairo.Context, image: Image):
        pass

    def get_generator(self) -> Point2D:
        return self.__generator
