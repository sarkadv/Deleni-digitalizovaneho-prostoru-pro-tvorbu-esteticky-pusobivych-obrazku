import tkinter as tk
from tkinter import messagebox

from PIL import Image, ImageOps

from enums.distribution_type import DistributionType
from enums.effect_type import EffectType
from enums.tessellation_type import TessellationType
from gui.generating_frame import GeneratingFrame
from gui.options_frame import OptionsFrame
from point_generator import PointGenerator
from tessellation_generator import TesellationGenerator
from util.file_writer import write_points_to_file
from visualizer import Visualizer


class Controller(tk.Tk):
    """
    Třída pro správu a interakci s GUI.
    """

    DEFAULT_WINDOW_SIZE = "350x550"
    MIN_WINDOW_WIDTH = 350
    MIN_WINDOW_HEIGHT = 550
    TITLE = ""

    def __init__(self):
        tk.Tk.__init__(self)
        self.title(self.TITLE)
        self.geometry(self.DEFAULT_WINDOW_SIZE)
        self.minsize(self.MIN_WINDOW_WIDTH, self.MIN_WINDOW_HEIGHT)
        self.maxsize(self.MIN_WINDOW_WIDTH, self.MIN_WINDOW_HEIGHT)
        self.focus_force()

        self.__image = None  # původní obrázek
        self.__points_output = False    # budou vygenerované body zapsány do souboru ?
        self.__tessellation = None  # vybraná teselace
        self.__distribution = None  # vybrané rozdělení bodů
        self.__effect = None    # vybraný efekt
        self.__generated_image = None  # vygenerovaný obrázek

        container = tk.Frame(self)
        container.pack()

        # inicializace oken GUI
        self.__frames = {}
        self.__current_frame = None

        self.__frames[OptionsFrame.NAME] = OptionsFrame(container, self)
        self.__frames[OptionsFrame.NAME].grid(row=0, column=0, sticky="nsew")

        self.__frames[GeneratingFrame.NAME] = GeneratingFrame(container, self)
        self.__frames[GeneratingFrame.NAME].grid(row=0, column=0, sticky="nsew")

        # výchozí okno pro výběr parametrů je aktivní
        self.__show_frame(OptionsFrame.NAME)

    def __show_frame(self, frame_name: str) -> None:
        """
        Vloží specifikované okno do popředí GUI, aby bylo viditelné a aktivní.
        :param frame_name: jméno okna
        """

        self.current_frame = self.__frames[frame_name]
        frame = self.__frames[frame_name]
        frame.tkraise()

    def set_image_file(self, filepath: str) -> None:
        """
        Nastaví atribut vstupního obrázku, jestliže je soubor validní.
        :param filepath: cesta k obrázku
        """

        try:
            image_file = Image.open(filepath)
            image_file = ImageOps.exif_transpose(image_file)    # správná rotace obrázku
            image_file = image_file.convert("RGB")
            image_file.filename = filepath
            self.__image = image_file
            self.__frames[OptionsFrame.NAME].configure_file_label(filepath)

        except IOError:
            messagebox.showerror("Chyba", "Soubor " + filepath + " není validní obrázek.")
            self.__image = None
            self.__frames[OptionsFrame.NAME].configure_file_label("")

    def set_points_output(self, points_output_int: int) -> None:
        """
        Nastaví příznak zápisu vygenerovaných bodů do souboru.
        :param points_output_int: 0 - nezapisovat do souboru / 1 - zapsat do souboru
        """

        self.__points_output = bool(points_output_int)

    def set_tessellation(self, tessellation_string: str) -> None:
        """
        Nastaví atribut typu teselace a zobrazí menu pro výběr dalších parametrů.
        :param tessellation_string: řetězec se jménem teselace (odpovídá výčtovému typu TessellationType)
        """

        self.__tessellation = TessellationType(tessellation_string)

        # menu rozdělení a efektů se zobrazí znovu bez výběru -> dřívější výběr se zruší
        self.__distribution = None
        self.__effect = None

        self.__frames[OptionsFrame.NAME].show_distribution_menu(self.__tessellation)
        self.__frames[OptionsFrame.NAME].show_effect_menu(self.__tessellation)
        self.__frames[OptionsFrame.NAME].show_continue_button()

    def set_distribution(self, distribution_string: str) -> None:
        """
        Nastaví atribut typu rozdělení bodů.
        :param distribution_string: řetězec se jménem rozdělení (odpovídá výčtovému typu DistributionType)
        """

        self.__distribution = DistributionType(distribution_string)

    def set_effect(self, effect_string: str) -> None:
        """
        Nastaví atribut typu efektu.
        :param effect_string: řetězec se jménem efektu (odpovídá výčtovému typu EffectType)
        """

        self.__effect = EffectType(effect_string)

    def generate(self) -> None:
        """
        Za použití parametrů vybraných uživatelem vygeneruje nejdříve body, poté oblasti teselace
        a výsledek vykreslí do souboru.
        """

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

        point_generator = PointGenerator(self.__image, self.__distribution, 1, self.__image.width, 1,
                                         self.__image.height)

        points = point_generator.generate_points()

        if self.__points_output:
            filepath = write_points_to_file(points)

            self.__frames[GeneratingFrame.NAME].set_points_file(filepath)
            self.update()
        else:
            self.__frames[GeneratingFrame.NAME].set_points_generated()
            self.update()

        tesellation_generator = TesellationGenerator(points, self.__image, self.__tessellation)
        regions = tesellation_generator.generate_regions()

        visualizer = Visualizer(self.__image, regions, self.__effect)
        self.__generated_image = visualizer.create_image()

        self.__frames[GeneratingFrame.NAME].set_image_generated()
        self.__frames[GeneratingFrame.NAME].show_continue_button()

    def reset(self) -> None:
        """
        Resetuje GUI pro generování nového obrázku.
        """

        # celé okno se zruší a znovu inicializuje
        self.destroy()
        self.__init__()

    def get_generated_image(self) -> Image:
        return self.__generated_image
