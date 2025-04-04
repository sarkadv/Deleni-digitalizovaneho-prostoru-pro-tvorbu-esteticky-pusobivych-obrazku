import cairo

from geometry.a_region import ARegion
from enums.effect_type import *
from util.color_utils import find_complementary_color, find_image_mode_color
from util.image_drawer import draw_paper_texture
from util.geometry_utils import *


class Visualizer:
    """
    Třída zodpovědná za vykreslení oblastí teselace na grafický kontext.
    """

    BORDER_DIVISOR = 500    # vhodně zvolená konstanta pro získání šířky obrysu

    def __init__(self, image: Image, regions: list[ARegion], effect: EffectType):
        self.__image = image
        self.__regions = regions
        self.__effect = effect

    def create_image(self) -> Image:
        """
        Podle atributů vykreslí na grafický kontext oblasti teselace s vybraným efektem.
        Grafický kontext je poté převeden na instanci Image z knihovny Pillow a obrázek je vrácen.
        :return: instance třídy Image
        """

        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.__image.width, self.__image.height)
        context = cairo.Context(surface)

        if self.__effect == EffectType.BASIC:
            for region in self.__regions:
                region.draw_basic(context)

        elif self.__effect == EffectType.GRID_ONE_COLOR:
            border_width = self.__image.width / self.BORDER_DIVISOR
            border_color_rgb = find_complementary_color(find_image_mode_color(self.__image))

            for region in self.__regions:
                region.draw_grid(context, border_width, border_color_rgb, False)

        elif self.__effect == EffectType.GRID_COLORFUL:
            border_width = round(self.__image.width / self.BORDER_DIVISOR)

            for region in self.__regions:
                # barva je vybrána samostatně pro každý region
                region.draw_grid(context, border_width, (0.0, 0.0, 0.0), True)

        elif self.__effect == EffectType.MULTIPLE_SHAPES:
            for region in self.__regions:
                # metoda implementována pouze pro Quadtree, pro ostatní teselace nemá smysl
                region.draw_multiple_shapes(context)

        elif self.__effect == EffectType.RECTANGLE_WITH_OVAL:
            for region in self.__regions:
                region.draw_rectangle_with_oval(context, self.__image)

        elif self.__effect == EffectType.GRADIENTS:
            for region in self.__regions:
                region.draw_gradients(context, self.__image)

        elif self.__effect == EffectType.PAPER:
            for region in self.__regions:
                region.draw_paper(context)

            draw_paper_texture(context, self.__image.width, self.__image.height)

        data = surface.get_data()
        image = Image.frombuffer("RGBA", (self.__image.width, self.__image.height), data, "raw", "BGRA", 0, 1)
        return image
