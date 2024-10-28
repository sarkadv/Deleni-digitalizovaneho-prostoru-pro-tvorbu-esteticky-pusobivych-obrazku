import tkinter as tk
from tkinter import filedialog, messagebox

from PIL import Image, ImageTk


class ResultWindow(tk.Toplevel):

    DEFAULT_WINDOW_SIZE = "725x725"
    MIN_WINDOW_WIDTH = 725
    MIN_WINDOW_HEIGHT = 725

    CANVAS_WIDTH = 650
    CANVAS_HEIGHT = 650

    IMG_OUTPUT_FOLDER = "img_output/"

    def __init__(self, parent: tk.Frame, controller, generated_image: Image):
        super().__init__(parent)
        self.__controller = controller
        self.__generated_image = generated_image

        self.title("Vygenerovaný obrázek")
        self.geometry(self.DEFAULT_WINDOW_SIZE)
        self.minsize(self.MIN_WINDOW_WIDTH, self.MIN_WINDOW_HEIGHT)
        self.maxsize(self.MIN_WINDOW_WIDTH, self.MIN_WINDOW_HEIGHT)

        self.protocol("WM_DELETE_WINDOW", lambda: self.__close_window())    # zavolání speciální funkce při zavření okna
        self.grab_set()     # jde kliknout pouze na widgety tohoto okna

        self.__create_canvas()

        self.__save_button = tk.Button(self, text="Uložit obrázek", command=lambda: self.__save_file())
        self.__save_button.pack(pady=10, side=tk.BOTTOM)

    def __create_canvas(self) -> None:
        self.__canvas = tk.Canvas(self, width=self.CANVAS_WIDTH, height=self.CANVAS_HEIGHT)
        self.__canvas_image = self.__create_canvas_image(self.__generated_image)

        canvas_image_width = self.__canvas_image.width()
        canvas_image_height = self.__canvas_image.height()

        # výpočet souřadnic x, y tak, aby obrázek byl vycentrovaný uprostřed plátna
        canvas_image_x = int((self.CANVAS_WIDTH - canvas_image_width) / 2)
        canvas_image_y = int((self.CANVAS_HEIGHT - canvas_image_height) / 2)

        self.__canvas.create_image(canvas_image_x, canvas_image_y, anchor="nw", image=self.__canvas_image)
        self.__canvas.pack(pady=10)

    def __create_canvas_image(self, image: Image) -> tk.PhotoImage:
        if image.width <= self.CANVAS_WIDTH and image.height <= self.CANVAS_HEIGHT:
            return ImageTk.PhotoImage(image)

        # obrázek větší než plátno
        else:
            if image.width >= image.height:
                height_to_width_ratio = image.height / image.width

                width = self.CANVAS_WIDTH
                height = int(width * height_to_width_ratio)

            else:
                width_to_height_ratio = image.width / image.height

                height = self.CANVAS_HEIGHT
                width = int(height * width_to_height_ratio)

            image_resized = image.resize((width, height), Image.LANCZOS)

        return ImageTk.PhotoImage(image_resized)

    def __save_file(self) -> None:
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

                print("Vygenerovaný obrázek uložen do souboru: " + filename)
                messagebox.showinfo("Success", "Vygenerovaný obrázek uložen do souboru:\n" + filename)

            except IOError as e:
                messagebox.showerror("Error", "Nepodařilo se uložit obrázek.")

    def __close_window(self) -> None:
        # při zavření okna se resetuje celá aplikace
        self.__controller.reset()



