import tkinter as tk

from src.Components.customenotebook import ClosableNotebook


class CustomTabs(ClosableNotebook):
    def __init__(self, master):
        super().__init__(master, self.close_handle)

    def close_handle(self, event):
        # From editor.py
        selected_tab = None
        # noinspection DuplicatedCode
        if self.index("end"):
            # Close the current tab if close is selected from file menu, or
            # keyboard shortcut.
            if event is None or event.type == str(2):
                selected_tab = self.get_tab
            # Otherwise close the tab based on coordinates of center-click.
            else:
                try:
                    index = event.widget.index(f"@{event.x},{event.y}")
                    selected_tab = self.nametowidget(self.tabs()[index])
                except tk.TclError:
                    return

        self.forget(selected_tab)
