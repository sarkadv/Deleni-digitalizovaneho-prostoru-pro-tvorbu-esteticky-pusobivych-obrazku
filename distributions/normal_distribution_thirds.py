import numpy as np
from PIL import Image

from distributions.a_distribution import ADistribution
from geometry.point_2d import *
from util.geometry_utils import is_point_in_image


class NormalDistributionThirds(ADistribution):

    POINT_COUNT_MULTIPLIER = 100_000

    def generate_points(self, image: Image, x_min: int, x_max: int, y_min: int, y_max: int) -> list[Point2D]:
        point_count = round(math.log((image.width * image.height * self.POINT_COUNT_MULTIPLIER) ** 2, 1.05)) * 2
        points = []

        centers = [None, None, None, None]    # průsečíky z pravidla třetin, střední hodnoty normálních rozdělení
        # body ve směru hodinových ručiček od levého horního rohu
        centers[0] = Point2D(image.width * (1/3), image.height * (1/3))
        centers[1] = Point2D(image.width * (2/3), image.height * (1/3))
        centers[2] = Point2D(image.width * (1/3), image.height * (2/3))
        centers[3] = Point2D(image.width * (2/3), image.height * (2/3))

        # směrodatná odchylka x je polovina ze vzdálenosti na ose x mezi středními hodnotami
        # většina bodů bude vygenerována do vzdálenosti mezi střední hodnotou
        # a středem na ose x mezi středními hodnotami
        # malé procento bodů bude vygenerováno dále
        st_dev_x = (centers[1].get_x() - centers[0].get_x()) / 2

        # směrodatná odchylka y je polovina ze vzdálenosti na ose y mezi středními hodnotami
        st_dev_y = (centers[2].get_y() - centers[0].get_y()) / 2

        for center in centers:
            # okolo každé střední hodnoty vygenerovat čtvrtinu bodů
            new_points = self.__generate_normal_distribution_points(center, int(point_count / len(centers)),
                                                                    st_dev_x, st_dev_y)
            points.extend(new_points)

        result = set()  # mezi body nesmí být duplicity

        for point in points:
            # hledáme body, které jsou uvnitř obrázku
            if is_point_in_image(image, point):
                result.add(point)

        return list(result)

    def __generate_normal_distribution_points(self, center: Point2D, point_count: int,
                                              st_dev_x: float, st_dev_y: float) -> list[Point2D]:

        # vygenerování normálně rozložených bodů
        normal_data_x = np.random.normal(center.get_x(), st_dev_x, point_count)
        normal_data_y = np.random.normal(center.get_y(), st_dev_y, point_count)

        points = set()  # mezi body nesmí být duplicity

        for i in range(point_count):
            x = round(normal_data_x[i])
            y = round(normal_data_y[i])
            points.add(Point2D(x, y))

        return list(points)
