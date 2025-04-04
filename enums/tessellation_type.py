from enums.extended_enum import *


class TessellationType(ExtendedEnum):
    """
    Výčtový typ pro různé druhy dělení prostoru.
    """

    VORONOI = 'Voroného diagram'
    DELAUNAY_FAST = 'Delaunayho triangulace - Rychlejší'
    DELAUNAY_BETTER_COLORS = 'Delaunayho triangulace - Lepší barvy'
    QUADTREE = 'Kvadrantový strom'




