from typing import *
from src.modules import tk, os

images: Dict[Text, tk.PhotoImage] = {}


def init_images():
    for file in os.listdir("Images/"):
        file = os.path.join("Images", file)
        if os.path.isfile(file) and file.endswith(".gif"):
            name = file.removeprefix("Images/").replace("-dark", "").replace(".gif", "")
            print(name)
            images[name] = tk.PhotoImage(file=file)

def get_image(image) -> tk.PhotoImage:
    return images[image]
