class Point2D:
    def __init__(self, x: int, y: int):
        self.__x = x
        self.__y = y

    def __hash__(self):
        return hash((self.__x, self.__y))

    def __eq__(self, other):
        if not isinstance(other, Point2D):
            return False

        return self.__x == other.get_x() and self.__y == other.get_y()

    def get_x(self) -> int:
        return self.__x

    def get_y(self) -> int:
        return self.__y

