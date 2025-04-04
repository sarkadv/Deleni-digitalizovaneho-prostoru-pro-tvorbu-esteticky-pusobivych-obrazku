import datetime

from geometry.point_2d import Point2D

POINTS_OUTPUT_FOLDER = 'points_output/'
POINTS_OUTPUT_EXTENSION = '.txt'


def write_points_to_file(points: list[Point2D]) -> str:
    """
    Zapíše seznam 2D bodů do textového souboru.
    :param points: seznam 2D bodů
    :return: cesta k textovému souboru
    """

    filepath = POINTS_OUTPUT_FOLDER + datetime.datetime.now().strftime("%d-%m-%Y_%H-%M-%S") + POINTS_OUTPUT_EXTENSION

    with open(filepath, 'w') as file:
        file.write('# počet bodů\n')
        file.write(str(len(points)) + '\n')

        file.write('# souřadnice x;souřadnice y\n')
        for point in points:
            file.write(str(point.get_x()) + ';' + str(point.get_y()) + '\n')

    return filepath
