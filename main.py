#!/usr/bin/python3
import logging
from tkinter import Tk

from src.Components.startdialog import StartDialog
from src.constants import OSX

if __name__ == "__main__":
    if OSX:
        # noinspection PyUnresolvedReferences,PyPackageRequirements
        # This really should be renamed! PyCharm always complains about it!
        from Foundation import NSBundle

        bundle = NSBundle.mainBundle()
        if bundle:
            info = bundle.localizedInfoDictionary() or bundle.infoDictionary()
            if info:
                info["CFBundleName"] = "NWEdit"  # Change name on the titlebar
                info["CFBundleDisplayName"] = "NWEdit"  # Change name on the Dock
    root = Tk()
    root.option_add('*tearOff', "false")

    StartDialog(master=root)  # Starts the Editor
    root.mainloop()

    # Stop log
    logging.shutdown()
