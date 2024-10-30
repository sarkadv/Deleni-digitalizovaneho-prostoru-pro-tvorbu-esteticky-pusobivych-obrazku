from typing import Tuple

from scipy.spatial import Delaunay, KDTree

from distributions.a_distribution import *
from geometry.pixel import Pixel
from geometry.point_2d import *


class LaplaceDistribution(ADistribution):
    CONVOLUTION_MATRIX = [[0, 1, 0], [1, -4, 1], [0, 1, 0]]     # konvoluční jádro
    POINT_COUNT_MULTIPLIER = 0.02   # procento bodů s nejvyšší hodnotou gradientu, které budou považovány za hrany
    AREA_DIVISOR = 1000
    MIN_DISTANCE_BETWEEN_POINTS = 8

    def generate_points(self, image: ImageFile, x_min: int, x_max: int, y_min: int, y_max: int) -> list[Point2D]:
        # oddělení barevných kanálů
        r_channel, g_channel, b_channel = self.__create_color_channels(image)

        # výpočet Laplaceova filtru odděleně pro všechny kanály
        laplace_r = self.__compute_laplace(r_channel)
        laplace_g = self.__compute_laplace(g_channel)
        laplace_b = self.__compute_laplace(b_channel)

        pixels = []

        for i in range(image.height):
            for j in range(image.width):
                pixels.append(Pixel(j, i, laplace_r[i][j], laplace_g[i][j], laplace_b[i][j]))

        # ponecháme pouze část pixelů s největšími hodnotami v absolutní hodnotě
        pixels.sort(key=lambda pixel: abs(pixel.get_r() + pixel.get_g() + pixel.get_b()), reverse=True)
        keep_count = int(len(pixels) * self.POINT_COUNT_MULTIPLIER)
        pixels = pixels[:keep_count]

        # ponecháme pouze část pixelů, které jsou od sebe dostatečně daleko (aby nevznikaly moc malé trojúhelníky)
        pixels = self.__remove_similar_pixels(pixels, self.MIN_DISTANCE_BETWEEN_POINTS)

        # body pro DT
        coordinates = [[pixel.get_x(), pixel.get_y()] for pixel in pixels]

        change = True
        max_area = int((image.width * image.height) / self.AREA_DIVISOR)    # maximální obsah trojúhelníku

        # vytvoříme DT a přidáme body, aby nevznikaly příliš velké trojúhelníky
        while change:
            change = False
            delaunay = Delaunay(coordinates)

            for triangle in delaunay.simplices:
                vertices = []

                for index in triangle:
                    vertices.append(delaunay.points[index])

                points = [Point2D(round(vertex[0]), round(vertex[1])) for vertex in vertices]
                p1 = points[0]
                p2 = points[1]
                p3 = points[2]

                # obsah trojúhelníku
                area = abs(p1.get_x() * (p2.get_y() - p3.get_y())
                           + p2.get_x() * (p3.get_y() - p1.get_y())
                           + p3.get_x() * (p1.get_y() - p2.get_y())) / 2

                if area > max_area:
                    # nalezení středu trojúhelníku
                    centroid_x = int((p1.get_x() + p2.get_x() + p3.get_x()) / 3)
                    centroid_y = int((p1.get_y() + p2.get_y() + p3.get_y()) / 3)

                    coordinates.append([centroid_x, centroid_y])
                    change = True

        points = [Point2D(coordinate[0], coordinate[1]) for coordinate in coordinates]
        return list(set(points))    # odstranění duplicit

    def __create_color_channels(self, image: ImageFile) -> Tuple:
        # inicializace 2D pole hodnot barev pro výpočet Laplaceova filtru
        # navíc 2 řádky nahoře a dole + 2 sloupce vlevo a vpravo kvůli použití konvolučního jádra
        r_channel = [[0 for j in range(image.width + 2)] for i in range(image.height + 2)]
        g_channel = [[0 for j in range(image.width + 2)] for i in range(image.height + 2)]
        b_channel = [[0 for j in range(image.width + 2)] for i in range(image.height + 2)]

        # i = řádek, j = sloupec
        for i in range(image.height):
            for j in range(image.width):
                r, g, b = image.getpixel((j, i))
                r_channel[i + 1][j + 1] = r
                g_channel[i + 1][j + 1] = g
                b_channel[i + 1][j + 1] = b

                if j == 0:  # pixel úplně vlevo
                    r_channel[i + 1][j] = r
                    g_channel[i + 1][j] = g
                    b_channel[i + 1][j] = b

                elif j == image.width - 1:  # pixel úplně vpravo
                    r_channel[i + 1][j + 2] = r
                    g_channel[i + 1][j + 2] = g
                    b_channel[i + 1][j + 2] = b

        # 1. řádek vložen znovu úplně nahoru kvůli výpočtu s konvolučním jádrem
        for j in range(image.width + 2):
            r_channel[0][j] = r_channel[1][j]
            g_channel[0][j] = g_channel[1][j]
            b_channel[0][j] = b_channel[1][j]

        # poslední řádek vložen znovu úplně dolů kvůli výpočtu s konvolučním jádrem
        for j in range(image.width + 2):
            r_channel[image.height + 1][j] = r_channel[image.height][j]
            g_channel[image.height + 1][j] = g_channel[image.height][j]
            b_channel[image.height + 1][j] = b_channel[image.height][j]

        return r_channel, g_channel, b_channel

    def __compute_laplace(self, color_matrix: list[list[int]]):
        # výsledná matice má o 2 řádky a sloupce méně
        result_height = len(color_matrix) - 2
        result_width = len(color_matrix[0]) - 2

        result = [[0 for j in range(result_width)] for i in range(result_height)]

        for i in range(1, result_height + 1):
            for j in range(1, result_width + 1):
                laplace_sum = 0

                # výpočet diskrétní konvoluce
                for i_conv in range(-1, 2):
                    for j_conv in range(-1, 2):
                        convolution_matrix_value = self.CONVOLUTION_MATRIX[i_conv + 1][j_conv + 1]
                        color_matrix_value = color_matrix[i + i_conv][j + j_conv]
                        laplace_sum += convolution_matrix_value * color_matrix_value

                # umístění výsledku konvoluce do matice
                result[i - 1][j - 1] = laplace_sum

        return result

    def __remove_similar_pixels(self, pixels: list[Pixel], min_distance_between_points: int):
        # vytvoření datové struktury KD-tree z bodů
        points = [(pixel.get_x(), pixel.get_y()) for pixel in pixels]
        tree = KDTree(points)

        unique_points = []
        visited = set()     # indexy již nepotřebných bodů

        for i in range(len(points)):
            point = points[i]

            if i in visited:
                continue

            unique_points.append(pixels[i])

            # nalezení všech bodů, které jsou blízko aktuálního bodu
            nearby_points = tree.query_ball_point(point, min_distance_between_points)

            for j in nearby_points:
                visited.add(j)

        return unique_points
