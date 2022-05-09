from typing import *

from src.modules import os, tk
from src.Utils.photoimage import IconImage, PhotoImage

images: Dict[Text, Tuple[IconImage, PhotoImage]] = {}


def init_images() -> None:
    for file in os.listdir("Images/"):
        file = os.path.join("Images", file)
        if os.path.isfile(file) and file.endswith(".png"):
            name = file.removeprefix("Images/").replace(".png", "")
            images[name] = (IconImage(file=file), PhotoImage(file=file))


def get_image(
    image: Text, img_type: Literal["image", "icon"] = "icon"
) -> tk.PhotoImage:
    if img_type == "image":
        return images[image][1]
    return images[image][0]
