from enums.extended_enum import *


# typy rozdělení bodů
class DistributionType(ExtendedEnum):
    UNIFORM = 'Rovnoměrné rozdělení'
    LAPLACE = 'Laplaceův operátor'
    QUADTREE = 'Kvadrantový strom'
    DEVIATION = 'Dělení oblastí podle odchylky'
