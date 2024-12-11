from enums.extended_enum import *


# typy efektů
class EffectType(ExtendedEnum):
    BASIC = 'Žádný'
    GRID_ONE_COLOR = 'Grid - Jednobarevný'
    GRID_COLORFUL = 'Grid - Vícebarevný'
    MULTIPLE_SHAPES = 'Různé tvary oblastí'
    RECTANGLE_WITH_OVAL = 'Obdélníkové oblasti s ovály'
