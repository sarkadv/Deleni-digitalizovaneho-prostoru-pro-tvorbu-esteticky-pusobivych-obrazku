import os
import tkinter as tk
from tkinter import filedialog

from PIL import ImageTk, Image

from enums.distribution_type import DistributionType
from enums.effect_type import EffectType
from enums.tessellation_type import TessellationType


class OptionsFrame(tk.Frame):
    NAME = "options_frame"
    IMG_INPUT_FOLDER = "img_input/"

    def __init__(self, parent: tk.Frame, controller):
        tk.Frame.__init__(self, parent)
        self.__controller = controller

        self.__logo = ImageTk.PhotoImage(Image.open("logo.png"))
        self.__logo_label = tk.Label(self, padx=15, pady=15, image=self.__logo)
        self.__logo_label.pack(pady=10)

        self.__file_button = tk.Button(self, text="Vybrat obrázek", command=lambda: self.pick_file())
        self.__file_button.pack(pady=(10, 0), fill="x", expand=True)

        self.__file_label = tk.Label(self, text="Vybraný obrázek: X")
        self.__file_label.pack(pady=(0, 10))

        self.__tessellation_string = tk.StringVar(self, value="Vybrat teselaci")
        self.__tessellation_menu = tk.OptionMenu(self, self.__tessellation_string, *TessellationType.values(),
                                                 command=self.__controller.set_tessellation)
        self.__tessellation_menu.pack(pady=10, fill="x", expand=True)

        self.__distribution_string = tk.StringVar(self, value="Vybrat rozdělení bodů")
        self.__distribution_menu = tk.OptionMenu(self, self.__distribution_string, *DistributionType.values(),
                                                 command=self.__controller.set_distribution)
        self.__distribution_menu.pack_forget()

        self.__effect_string = tk.StringVar(self, value="Vybrat efekt")
        self.__effect_menu = tk.OptionMenu(self, self.__effect_string, *EffectType.values(),
                                           command=self.__controller.set_effect)
        self.__effect_menu.pack_forget()

        self.__continue_button = tk.Button(self, text='> Generovat', command=lambda: self.__controller.generate())
        self.__continue_button.pack_forget()

    def pick_file(self) -> None:
        filetypes = (
            ("image files", "*.jpg"),
            ("image files", "*.jpeg"),
        )

        filename = filedialog.askopenfilename(
            title="Vybrat obrázek",
            initialdir=self.IMG_INPUT_FOLDER,
            filetypes=filetypes)

        if filename != "":  # uživatel nevybral žádný obrázek
            self.__controller.set_image_file(filename)

    def configure_file_label(self, filename: str) -> None:
        if filename == "":
            self.__file_label.configure(text="Vybraný obrázek: X")
        else:
            self.__file_label.configure(text="Vybraný obrázek: " + os.path.basename(filename))

    def show_distribution_menu(self, tessellation: TessellationType) -> None:
        self.__distribution_string = tk.StringVar(self, value="Vybrat rozdělení bodů")
        self.__distribution_menu.pack_forget()
        self.__continue_button.pack_forget()

        if tessellation == TessellationType.VORONOI:
            self.__distribution_menu = tk.OptionMenu(self, self.__distribution_string,
                                                     *[DistributionType.UNIFORM.value],
                                                     command=self.__controller.set_distribution)
            self.__distribution_menu.pack(pady=10, fill="x", expand=True)

        elif tessellation == TessellationType.DELAUNAY_FAST or tessellation == TessellationType.DELAUNAY_BETTER_COLORS:
            self.__distribution_menu = tk.OptionMenu(self, self.__distribution_string,
                                                     *[DistributionType.UNIFORM.value, DistributionType.LAPLACE.value],
                                                     command=self.__controller.set_distribution)
            self.__distribution_menu.pack(pady=10, fill="x", expand=True)

        elif tessellation == TessellationType.QUADTREE:     # u quadtree nelze vybrat žádné rozdělení
            self.__controller.set_distribution(DistributionType.QUADTREE)

    def show_effect_menu(self, tessellation: TessellationType) -> None:
        self.__effect_string = tk.StringVar(self, value="Vybrat efekt")
        self.__effect_menu.pack_forget()
        self.__continue_button.pack_forget()

        if tessellation == TessellationType.VORONOI:
            self.__effect_menu = tk.OptionMenu(self, self.__effect_string,
                                               *EffectType.values(),
                                               command=self.__controller.set_effect)
            self.__effect_menu.pack(pady=10, fill="x", expand=True)

        elif tessellation == TessellationType.DELAUNAY_FAST or tessellation == TessellationType.DELAUNAY_BETTER_COLORS:
            self.__effect_menu = tk.OptionMenu(self, self.__effect_string,
                                               *EffectType.values(),
                                               command=self.__controller.set_effect)
            self.__effect_menu.pack(pady=10, fill="x", expand=True)

        elif tessellation == TessellationType.QUADTREE:
            self.__effect_menu = tk.OptionMenu(self, self.__effect_string,
                                               *EffectType.values(),
                                               command=self.__controller.set_effect)
            self.__effect_menu.pack(pady=10, fill="x", expand=True)

    def show_continue_button(self) -> None:
        self.__continue_button.pack(pady=10, fill="x", expand=True)
