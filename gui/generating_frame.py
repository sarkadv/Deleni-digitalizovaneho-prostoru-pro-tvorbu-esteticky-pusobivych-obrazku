import tkinter as tk
from tkinter import ttk

from PIL import ImageTk, Image

from gui.result_window import ResultWindow


class GeneratingFrame(tk.Frame):
    """
    Okno GUI pro zobrazení průběhu generování obrázku.
    """

    NAME = "generating_frame"

    def __init__(self, parent: tk.Frame, controller):
        tk.Frame.__init__(self, parent)
        self.__controller = controller
        self.__generated_image = None

        self.__logo = ImageTk.PhotoImage(Image.open("logo.png"))
        self.__logo_label = tk.Label(self, padx=15, pady=15, image=self.__logo)
        self.__logo_label.pack(pady=10)

        self.__progress_label = tk.Label(self, text="Generování obrázku...")
        self.__progress_label.pack(pady=10)

        self.__separator = ttk.Separator(self, orient='horizontal')
        self.__separator.pack(pady=10, fill="x")

        self.__points_label = tk.Label(self, text="")
        self.__points_label.pack_forget()

        self.__image_label = tk.Label(self, text="Obrázek byl vygenerován!")
        self.__image_label.pack_forget()

        self.__continue_button = tk.Button(self, text='> Zobrazit',
                                           command=lambda: self.__show_result_window())
        self.__continue_button.pack_forget()

    def set_points_file(self, filepath: str) -> None:
        """
        Nastaví text o zápisu vygenerovaných bodů do souboru.
        :param filepath: cesta k souboru s body
        """

        self.__points_label = tk.Label(self, text="Vygenerované body uloženy do souboru:\n" + filepath)
        self.__points_label.pack(pady=10)

    def set_points_generated(self) -> None:
        """
        Nastaví text o dokončení generování bodů.
        """

        self.__points_label = tk.Label(self, text="Body byly vygenerovány.")
        self.__points_label.pack(pady=10)

    def set_image_generated(self) -> None:
        """
        Nastaví text o dokončení generování obrázku.
        """

        self.__image_label.pack(pady=10)

    def show_continue_button(self) -> None:
        """
        Zviditelní tlačítko pro pokračování do dalšího okna.
        """

        self.__continue_button.pack(pady=10)

    def __show_result_window(self) -> None:
        """
        Zobrazí okno s výsledným obrázkem.
        """

        ResultWindow(self, self.__controller)
