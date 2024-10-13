import math

from PIL.ImageFile import ImageFile

from geometry.a_region import ARegion
from enums.effect_type import *
from util.image_utils import *


class Visualizer:

    BORDER_DIVISOR = 500

    def __init__(self, image: ImageFile, regions: list[ARegion], effect: EffectType):
        self.__image = image
        self.__regions = regions
        self.__effect = effect

        self.__output_filename = find_output_filename(self.__image.filename)

    def create_image(self):
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.__image.width, self.__image.height)
        context = cairo.Context(surface)

        if self.__effect == EffectType.BASIC:
            for region in self.__regions:
                region.draw_basic(context)

        elif self.__effect == EffectType.SHOW_GRID:
            border_width = self.__image.width / self.BORDER_DIVISOR
            border_color_rgb = find_complementary_color(find_image_mode_color(self.__image))

            surface = cairo_surface_from_pil(self.__image)
            context = cairo.Context(surface)

            for region in self.__regions:
                region.draw_grid(context, border_width, border_color_rgb)

        surface.write_to_png(self.__output_filename)


