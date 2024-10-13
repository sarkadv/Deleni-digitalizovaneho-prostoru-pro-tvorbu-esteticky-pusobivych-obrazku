from collections import Counter
from typing import Tuple

import cairo
import PIL.Image as Image
import os

OUTPUT_FOLDER = 'img_output/'
OUTPUT_EXTENSION = '.png'


def cairo_surface_from_pil(image: Image) -> cairo.Surface:
    # podle https://pycairo.readthedocs.io/en/latest/tutorial/pillow.html

    image.putalpha(256)
    arr = bytearray(image.tobytes('raw', 'BGRa'))

    return cairo.ImageSurface.create_for_data(arr, cairo.FORMAT_RGB24, image.width, image.height)


def find_image_mode_color(image: Image) -> Tuple[float, float, float]:
    pixels = list(image.getdata())

    color_counts = Counter(pixels)
    mode_color_int = color_counts.most_common(1)[0][0]

    mode_color_float = tuple([primary / 255 for primary in mode_color_int])

    return mode_color_float


def find_complementary_color(color: Tuple[float, float, float]) -> Tuple[float, float, float]:
    return 1 - color[0], 1 - color[1], 1 - color[2]


def find_output_filename(input_filename: str) -> str:
    basename = os.path.basename(input_filename)
    basename_no_extension = basename.split('.')[0]

    return OUTPUT_FOLDER + basename_no_extension + OUTPUT_EXTENSION



