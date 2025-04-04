import tkinter as tk
from tkinter import filedialog, messagebox

from PIL import Image, ImageTk


class ResultWindow(tk.Toplevel):
    """
    Okno pro zobrazení výsledného obrázku.
    """

    DEFAULT_WINDOW_SIZE = "725x725"
    MIN_WINDOW_WIDTH = 725
    MIN_WINDOW_HEIGHT = 725

    CANVAS_WIDTH = 650
    CANVAS_HEIGHT = 650

    IMG_OUTPUT_FOLDER = "img_output/"

    def __init__(self, parent: tk.Frame, controller):
        super().__init__(parent)
        self.__controller = controller
        self.__generated_image = controller.get_generated_image()

        self.title("Vygenerovaný obrázek")
        self.geometry(self.DEFAULT_WINDOW_SIZE)
        self.minsize(self.MIN_WINDOW_WIDTH, self.MIN_WINDOW_HEIGHT)
        self.maxsize(self.MIN_WINDOW_WIDTH, self.MIN_WINDOW_HEIGHT)

        self.protocol("WM_DELETE_WINDOW", lambda: self.__close_window())    # zavolání speciální funkce při zavření okna
        self.grab_set()     # jde kliknout pouze na widgety tohoto okna

        self.__create_canvas()

        self.__save_button = tk.Button(self, text="Uložit obrázek", command=lambda: self.__save_file())
        self.__save_button.pack(pady=10, padx=(250, 10), side=tk.LEFT)

        self.__back_button = tk.Button(self, text="< Zpět", command=lambda: self.__close_window())
        self.__back_button.pack(pady=10, padx=(10, 250), side=tk.RIGHT)

    def __create_canvas(self) -> None:
        """
        Inicializuje a vyplní komponentu Canvas výsledným obrázkem.
        """

        self.__canvas = tk.Canvas(self, width=self.CANVAS_WIDTH, height=self.CANVAS_HEIGHT)

        # škálování a převod obrázku do vhodného formátu pro Canvas
        self.__canvas_image = self.__create_canvas_image(self.__generated_image)

        canvas_image_width = self.__canvas_image.width()
        canvas_image_height = self.__canvas_image.height()

        # výpočet souřadnic x, y tak, aby obrázek byl vycentrovaný uprostřed plátna
        canvas_image_x = int((self.CANVAS_WIDTH - canvas_image_width) / 2)
        canvas_image_y = int((self.CANVAS_HEIGHT - canvas_image_height) / 2)

        self.__canvas.create_image(canvas_image_x, canvas_image_y, anchor="nw", image=self.__canvas_image)
        self.__canvas.pack(pady=10)

    def __create_canvas_image(self, image: Image) -> tk.PhotoImage:
        """
        Provede škálování a převod obrázku na formát vhodný pro komponentu Canvas.
        :param image: vygenerovaný obrázek
        :return: obrázek ve formátu pro komponentu Canvas
        """

        canvas_image_width = self.CANVAS_WIDTH - 20
        canvas_image_height = self.CANVAS_HEIGHT - 20

        if image.width <= canvas_image_width and image.height <= canvas_image_height:
            # obrázek se vejde na plátno

            return ImageTk.PhotoImage(image)

        else:
            # obrázek větší než plátno -> škálování

            if image.width >= image.height:
                height_to_width_ratio = image.height / image.width

                width = canvas_image_width
                height = int(width * height_to_width_ratio)

            else:
                width_to_height_ratio = image.width / image.height

                height = canvas_image_height
                width = int(height * width_to_height_ratio)

            image_resized = image.resize((width, height), Image.LANCZOS)

        return ImageTk.PhotoImage(image_resized)

    def __save_file(self) -> None:
        """
        Zobrazí dialog pro uložení výsledného obrázku do souboru.
        """

        filetypes = (
            ("image files", "*.png"),
        )

        filename = filedialog.asksaveasfilename(
            defaultextension=".png",
            title="Uložit obrázek",
            initialdir=self.IMG_OUTPUT_FOLDER,
            filetypes=filetypes)

        if filename != '':
            try:
                self.__generated_image.save(filename, "PNG")    # uložení do .png souboru

                messagebox.showinfo("Success", "Vygenerovaný obrázek uložen do souboru:\n" + filename)

            except IOError as _:
                messagebox.showerror("Error", "Nepodařilo se uložit obrázek.")

    def __close_window(self) -> None:
        """
        Provede reset GUI pro generování nového obrázku při zavření okna s aktuálním výsledným obrázkem.
        """

        self.__controller.reset()



