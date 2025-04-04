class Pixel:
    """
    Pomocná třída pro provedení diskrétní konvoluce s Laplaceovým operátorem.
    """

    def __init__(self, x: int, y: int, convolution_r: int, convolution_g: int, convolution_b: int):
        self.__x = x
        self.__y = y
        self.__convolution_r = convolution_r
        self.__convolution_g = convolution_g
        self.__convolution_b = convolution_b

    def get_x(self) -> int:
        return self.__x

    def get_y(self) -> int:
        return self.__y

    def get_convolution_r(self) -> int:
        return self.__convolution_r

    def get_convolution_g(self) -> int:
        return self.__convolution_g

    def get_convolution_b(self) -> int:
        return self.__convolution_b

    def get_convolution_gradient(self) -> int:
        return self.__convolution_r + self.__convolution_g + self.__convolution_b
