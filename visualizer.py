import cairo
from PIL.ImageFile import ImageFile

from geometry.a_region import ARegion
from enums.effect_type import *


class Visualizer:
    def __init__(self, image: ImageFile, regions: list[ARegion], effect: EffectType):
        self.__image = image
        self.__regions = regions
        self.__effect = effect

    def 

