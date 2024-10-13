import sys

from point_generator import *
from tesellation_generator import *
from visualizer import *
from util.image_utils import *


def parse_arguments(parameters: list) -> Tuple[ImageFile, TesellationType, DistributionType, EffectType]:
    filename = parameters[1]

    try:
        image_file = Image.open(filename)
    except IOError:
        raise ValueError('Soubor ' + filename + 'není validní obrázek.')

    tesellation_string = parameters[2]

    if tesellation_string in TesellationType.values():
        tesselation_type = TesellationType(tesellation_string)
    else:
        raise ValueError(tesellation_string + ' není typ validního dělení obrazu.')

    distribution_string = parameters[3]

    if distribution_string in DistributionType.values():
        distribution_type = DistributionType(distribution_string)
    else:
        raise ValueError(distribution_string + ' není typ validního rozdělení bodů.')

    effect_string = parameters[4]

    if effect_string in EffectType.values():
        effect_type = EffectType(effect_string)
    else:
        raise ValueError(effect_string + ' není validní efekt.')

    return image_file, tesselation_type, distribution_type, effect_type


def print_help() -> None:
    print('Použití: main.py <cesta_k_obrázku> <typ_dělení_prostoru> <rozdělení_bodů> <typ_efektu>')

    print('Typy dělení prostoru: ')

    tesselations_dict = TesellationType.dict()

    for key, value in tesselations_dict.items():
        print('\t' + key + ' ... ' + value)

    print('Typy rozdělení bodů: ')

    distributions_dict = DistributionType.dict()

    for key, value in distributions_dict.items():
        print('\t' + key + ' ... ' + value)

    print('Typy efektů: ')

    effects_dict = EffectType.dict()

    for key, value in effects_dict.items():
        print('\t' + key + ' ... ' + value)


if __name__ == '__main__':
    try:
        image, tesellation, distribution, effect = parse_arguments(sys.argv)
    except ValueError:
        print_help()
        exit(1)

    point_generator = PointGenerator(image, distribution)
    points = point_generator.generate_points()

    tesellation_generator = TesellationGenerator(points, image, tesellation)
    regions = tesellation_generator.generate_regions()

    visualizer = Visualizer(image, regions, effect)
    visualizer.create_image()



