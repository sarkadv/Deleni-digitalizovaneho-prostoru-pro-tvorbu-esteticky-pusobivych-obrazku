from scipy.spatial import Delaunay

from distributions.a_distribution import *
from geometry.pixel import Pixel
from geometry.point_2d import *
from util.convolution import convolute, LAPLACE_CONVOLUTION_MATRIX, separate_color_channels
from util.geometry_utils import remove_similar_points


class ALaplaceDistribution(ADistribution):
    """
    Abstraktní třída reprezentující rozdělení bodů dle Laplaceova operátoru.
    """

    POINT_COUNT_MULTIPLIER = 0.05   # procento bodů s nejvyšší hodnotou gradientu, které budou považovány za hrany

    # vhodně zvolené konstanty pro výpočet parametrů
    AREA_DIVISOR = 500
    SIDE_DIVISOR = 20
    DISTANCE_DIVISOR = 65

    MAX_TRIANGLE_AREA = 0    # maximální obsah trojúhelníku - vypočteno za běhu
    MAX_SIDE_LENGTH = 0     # maximální délka strany trojúhelníku - vypočteno za běhu
    MAX_VERTEX_COLOR_DIFFERENCE = 0.85  # maximální rozdíl barev ve vrcholech trojúhelníku

    MIN_DISTANCE_BETWEEN_POINTS = 0     # minimální euklidovská vzdálenost mezi dvěma body - vypočteno za běhu

    def generate_points(self, image: Image, x_min: int, x_max: int, y_min: int, y_max: int) -> list[Point2D]:
        self.MAX_TRIANGLE_AREA = int((image.width * image.height) / self.AREA_DIVISOR)
        self.MAX_SIDE_LENGTH = int(min(image.width, image.height) / self.SIDE_DIVISOR)
        self.MIN_DISTANCE_BETWEEN_POINTS = int(min(image.width, image.height) / self.DISTANCE_DIVISOR)

        # oddělení barevných kanálů
        r_channel, g_channel, b_channel = separate_color_channels(image)

        # výpočet Laplaceova filtru odděleně pro všechny kanály
        laplace_r = convolute(r_channel, LAPLACE_CONVOLUTION_MATRIX)
        laplace_g = convolute(g_channel, LAPLACE_CONVOLUTION_MATRIX)
        laplace_b = convolute(b_channel, LAPLACE_CONVOLUTION_MATRIX)

        pixels = []

        for i in range(image.height):
            for j in range(image.width):
                pixels.append(Pixel(j, i, int(laplace_r[i][j]), int(laplace_g[i][j]), int(laplace_b[i][j])))

        # ponecháme pouze část pixelů s největšími hodnotami v absolutní hodnotě
        pixels.sort(key=lambda pixel: abs(pixel.get_convolution_gradient()), reverse=True)
        keep_count = int(len(pixels) * self.POINT_COUNT_MULTIPLIER)
        pixels = pixels[:keep_count]

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

        # ponecháme pouze část bodů, které jsou od sebe dostatečně daleko (aby nevznikaly moc malé trojúhelníky)
        points = remove_similar_points(points, self.MIN_DISTANCE_BETWEEN_POINTS)
        return points

    @abstractmethod
    def split_triangle(self, points: list[Point2D], image: Image) -> list[Point2D]:
        """
        Metoda zjistí, zda je nutné předaný trojúhelník rozdělit podle kritérií implementující třídy.
        Pokud dojde k rozdělení, jsou nově vytvořené body vráceny.
        :param points: aktuální vrcholy trojúhelníku
        :param image: vstupní obrázek
        :return: nově vytvořené body / prázdný seznam
        """
        pass
