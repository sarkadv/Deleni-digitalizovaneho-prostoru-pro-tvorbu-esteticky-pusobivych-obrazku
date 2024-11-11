from PIL.ImageFile import ImageFile

from geometry.a_region import ARegion
from enums.effect_type import *
from util.image_utils import *


class Visualizer:

    BORDER_DIVISOR = 500

    def __init__(self, image: Image, regions: list[ARegion], effect: EffectType):
        self.__image = image
        self.__regions = regions
        self.__effect = effect

        self.__output_filename = find_output_filename(self.__image.filename)

    def create_image(self) -> Image:
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.__image.width, self.__image.height)
        context = cairo.Context(surface)

        if self.__effect == EffectType.BASIC:
            for region in self.__regions:
                region.draw_basic(context)

        elif self.__effect == EffectType.GRID_ONE_COLOR:
            border_width = self.__image.width / self.BORDER_DIVISOR
            border_color_rgb = find_complementary_color(find_image_mode_color(self.__image))

            surface = cairo_surface_from_pil(self.__image)
            context = cairo.Context(surface)

            for region in self.__regions:
                region.draw_grid(context, border_width, border_color_rgb)

        elif self.__effect == EffectType.GRID_COLORFUL:
            border_width = self.__image.width / self.BORDER_DIVISOR

            surface = cairo_surface_from_pil(self.__image)
            context = cairo.Context(surface)

            for region in self.__regions:
                r, g, b, a = region.get_base_color()
                border_color_rgb = find_complementary_color((r, g, b))
                region.draw_grid(context, border_width, border_color_rgb)

        data = surface.get_data()
        image = Image.frombuffer("RGBA", (self.__image.width, self.__image.height), data, "raw", "BGRA", 0, 1)
        return image

