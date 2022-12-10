import io
import os
import tkinter as tk
from typing import Dict, Literal, Tuple, Union

import pyvips
from PIL import Image, ImageTk

from src.Utils.photoimage import IconImage, PhotoImage

images: Dict[str, Tuple[IconImage, PhotoImage]] = {}
orig_images: Dict[str, io.BytesIO] = {}


def init_images() -> None:
    for file_path in os.listdir("Images/"):
        file_path = os.path.join("Images", file_path)
        if os.path.isfile(file_path) and file_path.endswith(".svg"):
            name = file_path.replace("Images/", "").replace(".svg", "")
            out = io.BytesIO()

            image = pyvips.Image.new_from_file(file_path, access="sequential", scale=5)
            out.write(image.write_to_buffer(".png"))

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
