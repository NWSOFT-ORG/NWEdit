import tkinter as tk

from src.Components.winframe import \
    WinFrame  # You may import from PyPlus Libraries


class Sample(WinFrame):
    def __init__(self, master):
        super().__init__(master, "SAMPLE")
        master.withdraw()
        self.hello()

    def on_exit(self, _):
        super().on_exit(_)
        self.master.destroy()

    @staticmethod
    def hello():
        print("Hello")


def main():
    Sample(tk.Toplevel())


class Plugin:  # Every Plugin main file should be a class called 'Plugin'
    """A sample plugin"""

    def __init__(self):
        # Defined menu -> New menu
        self.menu = {
            "[Tools]@A -> [Testing]": {
                "Sample": {
                    "icon": "info",
                    "mnemonic": None,
                    "function": "main()",
                    "imports": "src.Plugins.plugin_sample -> main",
                    "disable": False
                }
            }
        }
        self.PLUGIN_DATA = {
            "name"   : "Sample",
            "menu"   : self.menu,
            "onstart": lambda: None,
            "onsave" : lambda: None
        }
