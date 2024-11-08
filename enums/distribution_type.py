from enums.extended_enum import *


# typy rozdělení bodů
class DistributionType(ExtendedEnum):
    UNIFORM = 'Rovnoměrné rozdělení'
    LAPLACE_AREA = 'Laplaceův operátor - obsah trojúhelníku'
    LAPLACE_LENGTH = 'Laplaceův operátor - délka strany'
    LAPLACE_GRADIENT = 'Laplaceův operátor - rozdíl barev vrcholů'
    QUADTREE = 'Kvadrantový strom'
    DEVIATION = 'Dělení oblastí podle odchylky'
