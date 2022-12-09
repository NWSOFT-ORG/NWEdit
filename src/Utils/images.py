import io
import os
import tkinter as tk
from typing import Dict, Literal, Tuple, Union

from src.constants import WINDOWS

if not WINDOWS:
    import cairosvg
else:
    pass

from src.Utils.photoimage import IconImage, PhotoImage
from PIL import Image, ImageTk

images: Dict[str, Tuple[IconImage, PhotoImage]] = {}
orig_images: Dict[str, Image.Image] = {}


def _init_images_win():
    pass


def init_images() -> None:
    if WINDOWS:
        _init_images_win()
    for file_path in os.listdir("Images/"):
        file_path = os.path.join("Images", file_path)
        if os.path.isfile(file_path) and file_path.endswith(".svg"):
            name = file_path.replace("Images/", "").replace(".svg", "")
            out = io.BytesIO()
            cairosvg.svg2png(url=file_path, write_to=out, unsafe=True, scale=5)
            # Scale up and down to create sort of antialiasing
            # SVG created using Illustrator might trigger a false <ENTITY> problem
            images[name] = (IconImage(file=out), PhotoImage(file=out))
            orig_images[name] = out


def get_image(
    image: str,
    img_type: Literal["image", "icon", "custom"] = "icon",
    width: int = None,
    height: int = None
) -> Union[None, PhotoImage, IconImage, tk.Image]:
    if not image:
        return None
    if img_type == "image":
        return images[image][1]
    elif img_type == "custom":
        if width is None or height is None:
            raise ValueError("Height or width must be specified to use the 'custom' size")
        orig_img = orig_images[image]
        orig_img = Image.open(orig_img)
        orig_img.convert("RGBA")
        orig_img = orig_img.resize((width, height), 1)
        return ImageTk.PhotoImage(image=orig_img)
    return images[image][0]
