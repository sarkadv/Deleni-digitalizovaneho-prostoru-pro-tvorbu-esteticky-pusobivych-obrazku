from enums.extended_enum import *


class EffectType(ExtendedEnum):
    """
    Výčtový typ pro různé druhy efektů.
    """

    BASIC = 'Žádný'
    GRID_ONE_COLOR = 'Mřížka - Jednobarevná'
    GRID_COLORFUL = 'Mřížka - Vícebarevná'
    MULTIPLE_SHAPES = 'Různé tvary oblastí'
    RECTANGLE_WITH_OVAL = 'Obdélníkové oblasti s ovály'
    GRADIENTS = 'Gradienty'
    PAPER = 'Papír'
