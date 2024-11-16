from enums.extended_enum import *


# typy rozdělení bodů
class DistributionType(ExtendedEnum):
    UNIFORM = 'Rovnoměrné rozdělení'
    LAPLACE_AREA = 'Laplaceův operátor - Obsah trojúhelníku'
    LAPLACE_LENGTH = 'Laplaceův operátor - Délka strany'
    LAPLACE_GRADIENT = 'Laplaceův operátor - Rozdíl barev vrcholů'
    QUADTREE = 'Kvadrantový strom'
    DEVIATION = 'Dělení oblastí podle odchylky'
    NORMAL_THIRDS = 'Normální rozdělení - Pravidlo třetin'
