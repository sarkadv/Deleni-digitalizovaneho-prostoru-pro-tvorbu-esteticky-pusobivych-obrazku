import math


class Vector2D:
    def __init__(self, x: float, y: float):
        self.__x = x
        self.__y = y

    def get_size(self) -> float:
        return math.sqrt((self.__x ** 2) + (self.__y ** 2))

    def create_normalized(self) -> 'Vector2D':
        size = self.get_size()
        return Vector2D(self.__x / size, self.__y / size)

    def create_orthogonal(self) -> 'Vector2D':
        return Vector2D(-self.__y, self.__x)

    def create_opposite(self) -> 'Vector2D':
        return Vector2D(-self.__x, -self.__y)

    def get_x(self) -> float:
        return self.__x

    def get_y(self) -> float:
        return self.__y
