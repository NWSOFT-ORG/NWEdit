from src.modules import Image, ImageTk, font, ttk
from src.Utils.color_utils import (darken_color, hex2dec, is_dark_color,
                                   lighten_color)

ICON_REPLACE_COLOR = (148, 148, 148, 255)


class PhotoImage(ImageTk.PhotoImage):
    def __init__(self, file) -> None:
        self.image = Image.open(file)
        self.image.convert("RGBA")
        super().__init__(self.image)


class IconImage(ImageTk.PhotoImage):
    def __init__(self, file) -> None:
        self.image = Image.open(file)
        self.image.convert("RGBA")

        self.resize_image()
        self.replace_colors()

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

    def replace_colors(self):
        pixdata = self.image.load()

        for y in range(self.image.size[1]):
            for x in range(self.image.size[0]):
                if pixdata[x, y] == ICON_REPLACE_COLOR:
                    self.image.putpixel((x, y), (self.bg, self.bg, self.bg, 255))

    def resize_image(self):
        font_height = font.Font().metrics("linespace")
        self.image = self.image.resize([font_height, font_height])
