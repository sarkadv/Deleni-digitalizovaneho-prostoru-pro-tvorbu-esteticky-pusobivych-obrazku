from typing import Tuple

from PIL.Image import Image

# konvoluční jádro pro Gaussovské rozostření
GAUSSIAN_CONVOLUTION_MATRIX = [[1 / 16, 1 / 8, 1 / 16],
                               [1 / 8, 1 / 4, 1 / 8],
                               [1 / 16, 1 / 8, 1 / 16]]

# konvoluční jádro pro Laplaceův operátor
LAPLACE_CONVOLUTION_MATRIX = [[0, 1, 0],
                              [1, -4, 1],
                              [0, 1, 0]]


def convolute(original_matrix: list[list[float]], convolution_matrix: list[list[float]]) -> list[list[float]]:
    """
    Provede diskrétní konvoluci nad danou maticí s daným konvolučním jádrem.
    :param original_matrix: vstupní matice ke konvoluci
    :param convolution_matrix: konvoluční jádro
    :return: výsledek konvoluce nad vstupní maticí
    """

    # výsledná matice má o 2 řádky a sloupce méně
    result_height = len(original_matrix) - 2
    result_width = len(original_matrix[0]) - 2

    result = [[0 for j in range(result_width)] for i in range(result_height)]

    for i in range(1, result_height + 1):
        for j in range(1, result_width + 1):
            convolution_sum = 0

            # výpočet diskrétní konvoluce
            for i_conv in range(-1, 2):
                for j_conv in range(-1, 2):
                    convolution_matrix_value = convolution_matrix[i_conv + 1][j_conv + 1]
                    original_matrix_value = original_matrix[i + i_conv][j + j_conv]
                    convolution_sum += convolution_matrix_value * original_matrix_value

            # umístění výsledku konvoluce do matice
            result[i - 1][j - 1] = convolution_sum

    return result


def separate_color_channels(image: Image) -> Tuple[list[list[float]], list[list[float]], list[list[float]]]:
    """
    :param image: obrázek
    :return: tři matice s barevnou hodnotou obrázku v červené, zelené a modré složce
    """

    # inicializace 2D pole hodnot barev pro konvoluci
    r_channel = [[0 for j in range(image.width)] for i in range(image.height)]
    g_channel = [[0 for j in range(image.width)] for i in range(image.height)]
    b_channel = [[0 for j in range(image.width)] for i in range(image.height)]

    # i = řádek, j = sloupec
    for i in range(image.height):
        for j in range(image.width):
            r, g, b = image.getpixel((j, i))
            r_channel[i][j] = r
            g_channel[i][j] = g
            b_channel[i][j] = b

    # padding matic po stranách
    r_channel = create_convolution_padding(r_channel)
    g_channel = create_convolution_padding(g_channel)
    b_channel = create_convolution_padding(b_channel)

    return r_channel, g_channel, b_channel


def create_convolution_padding(original_matrix: list[list[float]]) -> list[list[float]]:
    """
    :param original_matrix: vstupní matice
    :return: vstupní matice rozšířená o horní + dolní řádek, levý + pravý sloupec kvůli konvoluci
    """

    width = len(original_matrix[0])
    height = len(original_matrix)

    # navíc 2 řádky nahoře a dole + 2 sloupce vlevo a vpravo kvůli použití konvolučního jádra
    padded_matrix = [[0 for j in range(width + 2)] for i in range(height + 2)]

    # i = řádek, j = sloupec
    for i in range(height):
        for j in range(width):
            padded_matrix[i + 1][j + 1] = original_matrix[i][j]

            if j == 0:  # pixel úplně vlevo
                padded_matrix[i + 1][j] = original_matrix[i][j]

            elif j == width - 1:  # pixel úplně vpravo
                padded_matrix[i + 1][j + 2] = original_matrix[i][j]

    # 1. řádek vložen znovu úplně nahoru kvůli výpočtu s konvolučním jádrem
    for j in range(width + 2):
        padded_matrix[0][j] = padded_matrix[1][j]

    # poslední řádek vložen znovu úplně dolů kvůli výpočtu s konvolučním jádrem
    for j in range(width + 2):
        padded_matrix[height + 1][j] = padded_matrix[height][j]

    return padded_matrix
