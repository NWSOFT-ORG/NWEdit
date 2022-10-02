from tkinter import font, ttk

from PIL import Image, ImageTk

from src.Utils.color_utils import (darken_color, hex2dec, is_dark_color,
                                   lighten_color)

ICON_REPLACE_COLOR = (193, 193, 193, 255)


class PhotoImage(ImageTk.PhotoImage):
    def __init__(self, file) -> None:
        self.image = Image.open(file)
        self.image.convert("RGBA")

        w = self.image.width
        h = self.image.height
        self.image = self.image.resize((w // 5, h // 5), 1)

        super().__init__(self.image)


class IconImage(ImageTk.PhotoImage):
    def __init__(self, file) -> None:
        self.image = Image.open(file)
        self.image.convert("RGBA")

        w = self.image.width
        h = self.image.height
        self.image = self.image.resize((w // 5, h // 5), 1)

        self.resize_image()

        super().__init__(image=self.image)

    @property
    def bg(self):
        style = ttk.Style()
        bg = style.lookup("TLabel", "background")
        if is_dark_color(bg):
            bg = lighten_color(bg, 10)
        else:
            bg = darken_color(bg, 10)
        bg = hex2dec(bg)
        return bg

    def resize_image(self):
        font_height = font.Font().metrics("linespace")
        self.image = self.image.resize((font_height, font_height), Image.ANTIALIAS)
