from geometry.a_region import ARegion
from enums.effect_type import *
from util.image_drawer import draw_background
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
                region.draw_grid(context, border_width, border_color_rgb, False)

        elif self.__effect == EffectType.GRID_COLORFUL:
            border_width = self.__image.width / self.BORDER_DIVISOR

            surface = cairo_surface_from_pil(self.__image)
            context = cairo.Context(surface)

            for region in self.__regions:
                # barva je vybrána samostatně pro každý region
                region.draw_grid(context, border_width, (0.0, 0.0, 0.0), True)

        elif self.__effect == EffectType.MULTIPLE_SHAPES:
            background_color = find_image_mode_color(self.__image)
            draw_background(context, self.__image.width, self.__image.height, background_color)

            for region in self.__regions:
                # metoda implementována pouze pro Quadtree, pro ostatní teselace nemá smysl
                region.draw_multiple_shapes(context)

        elif self.__effect == EffectType.RECTANGLE_WITH_OVAL:
            for region in self.__regions:
                region.draw_rectangle_with_oval(context, self.__image)

        elif self.__effect == EffectType.GRADIENTS:
            for region in self.__regions:
                region.draw_gradients(context, self.__image)

        data = surface.get_data()
        image = Image.frombuffer("RGBA", (self.__image.width, self.__image.height), data, "raw", "BGRA", 0, 1)
        return image

