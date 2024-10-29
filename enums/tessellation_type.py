from enums.extended_enum import *


# typy dělení digitalizovaného prostoru
class TessellationType(ExtendedEnum):
    VORONOI = 'Voroného diagram'
    DELAUNAY_FAST = 'Delaunayho triangulace - Rychlejší'
    DELAUNAY_BETTER_COLORS = 'Delaunayho triangulace - Lepší barvy'
    QUADTREE = 'Kvadrantový strom'




