from enums.extended_enum import *


class DistributionType(ExtendedEnum):
    """
    Výčtový typ pro různé druhy rozdělení bodů.
    """

    UNIFORM = 'Rovnoměrné rozdělení'
    LAPLACE_AREA = 'Laplaceův operátor - Obsah trojúhelníku'
    LAPLACE_LENGTH = 'Laplaceův operátor - Délka strany'
    LAPLACE_GRADIENT = 'Laplaceův operátor - Rozdíl barev vrcholů'
    QUADTREE = 'Kvadrantový strom'
    ERROR = 'Dělení oblastí podle chyby'
    NORMAL_THIRDS = 'Normální rozdělení - Pravidlo třetin'
    MITCHELL = 'Mitchellův algoritmus'
