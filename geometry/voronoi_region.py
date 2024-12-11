from geometry.a_region import *
from util.image_drawer import draw_circle
from util.image_utils import find_complementary_color


class VoronoiRegion(ARegion):
    def __init__(self, vertices: list[Point2D], seed: Point2D, base_color: Tuple[float, float, float]):
        super().__init__(vertices, base_color)
        self.__generator = seed

    def draw_grid(self, context: cairo.Context, border_width: float,
                  border_color_rgb: Tuple[float, float, float], colorful: bool) -> None:

        if len(self.get_vertices()) == 0:
            return

        # nakreslení obrysu
        if not colorful:
            # všechny obrysy stejná barva
            border_color = border_color_rgb

        else:
            # obrys každé oblasti může být jiný
            r, g, b = self.get_base_color()
            border_color = find_complementary_color((r, g, b))

        draw_polygon(context, self.get_vertices(), border_color, True)

        # nakreslení generátoru
        draw_circle(context, self.__generator, border_width * 1.5, border_color)

    def draw_multiple_shapes(self, context: cairo.Context):
        pass

    def draw_rectangle_with_oval(self, context: cairo.Context, image: Image):
        pass

    def get_generator(self) -> Point2D:
        return self.__generator
