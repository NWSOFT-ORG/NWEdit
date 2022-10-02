#!/usr/bin/python3
import tkinter as tk

from src.Components.startdialog import StartDialog
from src.constants import OSX

if __name__ == "__main__":
    if OSX:
        # noinspection PyUnresolvedReferences
        from Foundation import NSBundle

        bundle = NSBundle.mainBundle()
        if bundle:
            info = bundle.localizedInfoDictionary() or bundle.infoDictionary()
            if info:
                info["CFBundleName"] = "PyPlus"  # Change name on the titlebar
                info["CFBundleDisplayName"] = "PyPlus"  # Change name on the Dock
    root = tk.Tk()
    root.option_add('*tearOff', "false")

    StartDialog(master=root)  # Starts the Editor
    root.mainloop()

