from typing import Tuple

from scipy.spatial import Delaunay, KDTree

from distributions.a_distribution import *
from geometry.pixel import Pixel
from geometry.point_2d import *
from util.geometry_utils import convolute, create_convolution_padding


class ALaplaceDistribution(ADistribution):
    CONVOLUTION_MATRIX = [[0, 1, 0], [1, -4, 1], [0, 1, 0]]     # konvoluční jádro
    POINT_COUNT_MULTIPLIER = 0.03   # procento bodů s nejvyšší hodnotou gradientu, které budou považovány za hrany

    AREA_DIVISOR = 500
    SIDE_DIVISOR = 20
    DISTANCE_DIVISOR = 100

    MAX_TRIANGLE_AREA = 0    # maximální obsah trojúhelníku
    MAX_SIDE_LENGTH = 0     # maximální délka strany trojúhelníku
    MAX_VERTEX_COLOR_DIFFERENCE = 0.85
    MIN_DISTANCE_BETWEEN_POINTS = 0

    def generate_points(self, image: Image, x_min: int, x_max: int, y_min: int, y_max: int) -> list[Point2D]:
        self.MAX_TRIANGLE_AREA = int((image.width * image.height) / self.AREA_DIVISOR)
        self.MAX_SIDE_LENGTH = int(min(image.width, image.height) / self.SIDE_DIVISOR)
        self.MIN_DISTANCE_BETWEEN_POINTS = int(min(image.width, image.height) / self.DISTANCE_DIVISOR)

        # oddělení barevných kanálů
        r_channel, g_channel, b_channel = self.__separate_color_channels(image)

        # výpočet Laplaceova filtru odděleně pro všechny kanály
        laplace_r = convolute(r_channel, self.CONVOLUTION_MATRIX)
        laplace_g = convolute(g_channel, self.CONVOLUTION_MATRIX)
        laplace_b = convolute(b_channel, self.CONVOLUTION_MATRIX)

        pixels = []

        for i in range(image.height):
            for j in range(image.width):
                pixels.append(Pixel(j, i, int(laplace_r[i][j]), int(laplace_g[i][j]), int(laplace_b[i][j])))

        # ponecháme pouze část pixelů s největšími hodnotami v absolutní hodnotě
        pixels.sort(key=lambda pixel: abs(pixel.get_convolution_gradient()), reverse=True)
        keep_count = int(len(pixels) * self.POINT_COUNT_MULTIPLIER)
        pixels = pixels[:keep_count]

        # ponecháme pouze část pixelů, které jsou od sebe dostatečně daleko (aby nevznikaly moc malé trojúhelníky)
        pixels = self.__remove_similar_pixels(pixels, self.MIN_DISTANCE_BETWEEN_POINTS)

        # body pro DT
        coordinates = [[pixel.get_x(), pixel.get_y()] for pixel in pixels]

        change = True

        # vytvoříme DT a přidáme body, aby nevznikaly příliš velké trojúhelníky
        while change:
            change = False
            delaunay = Delaunay(coordinates)

            for triangle in delaunay.simplices:
                vertices = []

                for index in triangle:
                    vertices.append(delaunay.points[index])

                points = [Point2D(round(vertex[0]), round(vertex[1])) for vertex in vertices]

                # otestování, zda je nutné přidat nový bod + vytvoření nového bodu / bodů
                new_points = self.split_triangle(points, image)

                for new_point in new_points:
                    coordinate = [new_point.get_x(), new_point.get_y()]

                    if coordinate not in coordinates:
                        coordinates.append(coordinate)
                        change = True

        points = [Point2D(coordinate[0], coordinate[1]) for coordinate in coordinates]
        return points

    @abstractmethod
    def split_triangle(self, points: list[Point2D], image: Image) -> list[Point2D]:
        pass

    def __separate_color_channels(self, image: Image) -> Tuple:
        # inicializace 2D pole hodnot barev pro výpočet Laplaceova filtru
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

    def __remove_similar_pixels(self, pixels: list[Pixel], min_distance_between_points: int) -> list[Pixel]:
        # vytvoření datové struktury KD-tree z bodů
        points = [(pixel.get_x(), pixel.get_y()) for pixel in pixels]
        tree = KDTree(points)

        unique_points = []
        visited_indices = set()     # indexy již nepotřebných bodů

        for i in range(len(points)):
            point = points[i]

            if i in visited_indices:
                continue

            unique_points.append(pixels[i])

            # nalezení všech bodů, které jsou blízko aktuálního bodu
            nearby_points_indices = tree.query_ball_point(point, min_distance_between_points)

            for point_index in nearby_points_indices:
                visited_indices.add(point_index)

        return unique_points
