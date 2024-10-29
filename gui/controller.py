import tkinter as tk
from tkinter import messagebox

from PIL import Image

from enums.distribution_type import DistributionType
from enums.effect_type import EffectType
from enums.tessellation_type import TessellationType
from gui.generating_frame import GeneratingFrame
from gui.options_frame import OptionsFrame
from point_generator import PointGenerator
from tessellation_generator import TesellationGenerator
from util.file_writer import write_points_to_file
from visualizer import Visualizer

DELAUNAY_OUTSIDE_POINTS_FRACTION = 10


class Controller(tk.Tk):

    DEFAULT_WINDOW_SIZE = "300x500"
    MIN_WINDOW_WIDTH = 300
    MIN_WINDOW_HEIGHT = 500

    def __init__(self):
        tk.Tk.__init__(self)
        self.title("ddpptepo")
        self.geometry(self.DEFAULT_WINDOW_SIZE)
        self.minsize(self.MIN_WINDOW_WIDTH, self.MIN_WINDOW_HEIGHT)
        self.maxsize(self.MIN_WINDOW_WIDTH, self.MIN_WINDOW_HEIGHT)
        self.focus_force()

        self.__image = None  # původní obrázek
        self.__tessellation = None
        self.__distribution = None
        self.__effect = None
        self.__generated_image = None  # vygenerovaný obrázek

        container = tk.Frame(self)
        container.pack()

        self.__frames = {}
        self.__current_frame = None

        self.__frames[OptionsFrame.NAME] = OptionsFrame(container, self)
        self.__frames[OptionsFrame.NAME].grid(row=0, column=0, sticky="nsew")

        self.__frames[GeneratingFrame.NAME] = GeneratingFrame(container, self)
        self.__frames[GeneratingFrame.NAME].grid(row=0, column=0, sticky="nsew")

        self.__show_frame(OptionsFrame.NAME)

    def __show_frame(self, page_name: str) -> None:
        self.current_frame = self.__frames[page_name]
        frame = self.__frames[page_name]
        frame.tkraise()     # aktuální rámec do popředí

    def set_image_file(self, filename: str) -> None:
        try:
            image_file = Image.open(filename)
            self.__image = image_file
            self.__frames[OptionsFrame.NAME].configure_file_label(filename)

        except IOError:
            messagebox.showerror("Chyba", "Soubor " + filename + "není validní obrázek.")
            self.__image = None
            self.__frames[OptionsFrame.NAME].configure_file_label("")

    def set_tessellation(self, tessellation_string: str) -> None:
        self.__tessellation = TessellationType(tessellation_string)

        self.__frames[OptionsFrame.NAME].show_distribution_menu(self.__tessellation)
        self.__frames[OptionsFrame.NAME].show_effect_menu(self.__tessellation)
        self.__frames[OptionsFrame.NAME].show_continue_button()

    def set_distribution(self, distribution_string: str) -> None:
        self.__distribution = DistributionType(distribution_string)

    def set_effect(self, effect_string: str) -> None:
        self.__effect = EffectType(effect_string)

    def generate(self) -> None:
        if self.__image is None:
            messagebox.showerror("Chyba", "Nebyl vybrán obrázek.")
            return

        if self.__tessellation is None:
            messagebox.showerror("Chyba", "Nebyla vybrána teselace.")
            return

        if self.__distribution is None:
            messagebox.showerror("Chyba", "Nebylo vybráno rozdělení bodů.")
            return

        if self.__effect is None:
            messagebox.showerror("Chyba", "Nebyl vybrán efekt.")
            return

        self.__show_frame(GeneratingFrame.NAME)
        self.update()   # vykreslení nového rámce

        if self.__tessellation == TessellationType.VORONOI:
            point_generator = PointGenerator(self.__image, self.__distribution, 1, self.__image.width, 1, self.__image.height)

        elif self.__tessellation == TessellationType.DELAUNAY_FAST or self.__tessellation == TessellationType.DELAUNAY_BETTER_COLORS:
            # body i trochu mimo obrázek
            x_min = int((-1 / DELAUNAY_OUTSIDE_POINTS_FRACTION) * self.__image.width)
            x_max = int(((DELAUNAY_OUTSIDE_POINTS_FRACTION + 1) / DELAUNAY_OUTSIDE_POINTS_FRACTION) * self.__image.width)
            y_min = int((-1 / DELAUNAY_OUTSIDE_POINTS_FRACTION) * self.__image.height)
            y_max = int(((DELAUNAY_OUTSIDE_POINTS_FRACTION + 1) / DELAUNAY_OUTSIDE_POINTS_FRACTION) * self.__image.height)

            point_generator = PointGenerator(self.__image, self.__distribution, x_min, x_max, y_min, y_max)

        elif self.__tessellation == TessellationType.QUADTREE:
            point_generator = PointGenerator(self.__image, self.__distribution, 1, self.__image.width, 1, self.__image.height)

        points = point_generator.generate_points()
        filename = write_points_to_file(points)

        self.__frames[GeneratingFrame.NAME].set_points_file(filename)
        self.update()

        tesellation_generator = TesellationGenerator(points, self.__image, self.__tessellation)
        regions = tesellation_generator.generate_regions()

        visualizer = Visualizer(self.__image, regions, self.__effect)
        self.__generated_image = visualizer.create_image()

        self.__frames[GeneratingFrame.NAME].set_image_generated(self.__generated_image)
        self.__frames[GeneratingFrame.NAME].show_continue_button()

    def reset(self) -> None:
        # celé okno se zruší a znovu inicializuje
        self.destroy()
        self.__init__()
