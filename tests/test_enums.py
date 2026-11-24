"""GUI labels of tessellations, point distributions and effects (enums/)."""


# EN-01
def test_tessellation_labels(backend):
    assert list(backend.tessellation_labels().items()) == [
        ("VORONOI", "Voroného diagram"),
        ("DELAUNAY_FAST", "Delaunayho triangulace - Rychlejší"),
        ("DELAUNAY_BETTER_COLORS", "Delaunayho triangulace - Lepší barvy"),
        ("QUADTREE", "Kvadrantový strom"),
    ]


# EN-02
def test_distribution_labels(backend):
    assert list(backend.distribution_labels().items()) == [
        ("UNIFORM", "Rovnoměrné rozdělení"),
        ("LAPLACE_AREA", "Laplaceův operátor - Obsah trojúhelníku"),
        ("LAPLACE_LENGTH", "Laplaceův operátor - Délka strany"),
        ("LAPLACE_GRADIENT", "Laplaceův operátor - Rozdíl barev vrcholů"),
        ("QUADTREE", "Kvadrantový strom"),
        ("ERROR", "Dělení oblastí podle chyby"),
        ("NORMAL_THIRDS", "Normální rozdělení - Pravidlo třetin"),
        ("MITCHELL", "Mitchellův algoritmus"),
    ]


# EN-03
def test_effect_labels(backend):
    assert list(backend.effect_labels().items()) == [
        ("BASIC", "Žádný"),
        ("GRID_ONE_COLOR", "Mřížka - Jednobarevná"),
        ("GRID_COLORFUL", "Mřížka - Vícebarevná"),
        ("MULTIPLE_SHAPES", "Různé tvary oblastí"),
        ("RECTANGLE_WITH_OVAL", "Obdélníkové oblasti s ovály"),
        ("GRADIENTS", "Gradienty"),
        ("PAPER", "Papír"),
    ]
