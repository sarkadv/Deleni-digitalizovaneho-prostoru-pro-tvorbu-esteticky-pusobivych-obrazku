import numpy as np
import scipy.stats as stats
from scipy.stats import randint

from distributions.a_distribution import *
from geometry.point_2d import *


class MitchellDistribution(ADistribution):
    POINT_COUNT_MULTIPLIER = 100_000
    CANDIDATE_COUNT_MULTIPLIER = 2

    def generate_points(self, image: Image, x_min: int, x_max: int, y_min: int, y_max: int) -> list[Point2D]:
        # náhodné proměnné diskrétního rovnoměrného rozdělení
        uniform_discrete_variable_x = stats.randint(low=x_min, high=x_max)
        uniform_discrete_variable_y = stats.randint(low=y_min, high=y_max)

        point_count = round(math.log((image.width * image.height * self.POINT_COUNT_MULTIPLIER) ** 2, 1.05)) * 2

        # vygenerujeme náhodně první bod
        points = self.__generate_candidates(1, uniform_discrete_variable_x, uniform_discrete_variable_y)

        # generujeme nové body, dokud jich není daný počet
        while len(points) < point_count:
            candidate_count = self.CANDIDATE_COUNT_MULTIPLIER * len(points)

            candidates = self.__generate_candidates(candidate_count, uniform_discrete_variable_x,
                                                    uniform_discrete_variable_y)

            # kandidát, který má maximální minimální vzdálenost od již vygenerovaných bodů
            new_point = self.__find_max_distance_point(points, candidates)

            if new_point is not None:  # bod je None, jestliže se shoduje s některým již získaným bodem
                points.append(new_point)

        return points

    def __generate_candidates(self, point_count: int, uniform_discrete_variable_x: randint,
                              uniform_discrete_variable_y: randint) -> list[Point2D]:
        points = []

        coordinates_x = uniform_discrete_variable_x.rvs(size=point_count)
        coordinates_y = uniform_discrete_variable_y.rvs(size=point_count)

        for i in range(0, point_count):
            points.append(Point2D(int(coordinates_x[i]), int(coordinates_y[i])))

        return list(set(points))  # odstranění duplicitních bodů

    def __find_max_distance_point(self, current_points: list[Point2D], candidates: list[Point2D]) -> Point2D | None:
        min_distances = []

        # převedení na np.array
        # příliš se nevyplatí aktuálně vygenerované body udržovat jako np.array dlouhodobě
        # při přidání nového bodu se totiž vždy alokuje paměť pro celé nové pole a prvky se překopírují
        current_points = np.array([[point.get_x(), point.get_y()] for point in current_points])

        # nalezení minimální vzdálenosti každého kandidáta od všech bodů z množiny již vygenerovaných bodů
        for candidate in candidates:
            candidate_np = np.array([candidate.get_x(), candidate.get_y()])

            # euklidovské vzdálenosti kandidáta od každého bodu z množiny hotových bodů
            distances = np.sqrt(np.sum((current_points - candidate_np) ** 2, axis=1))

            min_distances.append(min(distances))

        # nalezení maximální vzdálenosti ze všech minimálních
        max_distance_index = np.argmax(min_distances)
        max_distance = min_distances[max_distance_index]

        if math.isclose(max_distance, 0, abs_tol=0.1):
            # bod se shoduje s již vygenerovaným bodem
            return None

        # vrátit kandidáta s maximální minimální vzdálenosti od množiny již získaných bodů
        return candidates[max_distance_index]
