from src.Widgets.winframe import WinFrame
from src.modules import tk  # You may import from PyPlus Libraries


class Sample(WinFrame):
    def __init__(self, master):
        super().__init__(master, "SAMPLE")
        self.hello()

    @staticmethod
    def hello():
        print("Hello")


def main(master):
    Sample(master)


class Plugin:  # Every Plugin main file should be a class called 'Plugin'
    """A sample plugin"""

    def __init__(self, master):
        self.menu = tk.Menu(master)
        self.menu.add_command(label="Testing", command=lambda: main(master))
        self.PLUGIN_DATA = {"name": "Sample", "menu": self.menu, "onstart": lambda: None}
        # Should be {"name": "...", "menu": tk.Menu, "onstart": callable, "cascade": bool}
