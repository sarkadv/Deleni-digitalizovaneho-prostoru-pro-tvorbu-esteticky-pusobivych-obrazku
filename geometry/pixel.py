class Pixel:
    def __init__(self, x: int, y: int, r: int, g: int, b: int):
        self.__x = x
        self.__y = y
        self.__r = r
        self.__g = g
        self.__b = b

    def get_x(self) -> int:
        return self.__x

    def get_y(self) -> int:
        return self.__y

    def get_r(self) -> int:
        return self.__r

    def get_g(self) -> int:
        return self.__g

    def get_b(self) -> int:
        return self.__b
