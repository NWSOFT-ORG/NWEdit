#!/usr/bin/python3
import logging
import tkinter as tk

from src.Components.startdialog import StartDialog
from src.constants import logger, OSX
from src.window import create_window, main_loop

if __name__ == "__main__":
    logger.info(f"Tkinter version: {tk.TkVersion}")
    logger.debug("All modules imported")

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

    root = create_window()
    root.option_add('*tearOff', "false")

    StartDialog(master=root)  # Starts the Editor
    main_loop()

    # Stop log
    logging.shutdown()
