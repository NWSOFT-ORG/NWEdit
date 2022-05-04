from typing import *

from src.modules import os, tk

images: Dict[Text, tk.PhotoImage] = {}

def init_images() -> None:
    for file in os.listdir("Images/"):
        file = os.path.join("Images", file)
        if os.path.isfile(file) and file.endswith(".png"):
            name = file.removeprefix("Images/").replace(".png", "")
            images[name] = tk.PhotoImage(file=file)


def get_image(image: Text) -> tk.PhotoImage:
    return images[image]
