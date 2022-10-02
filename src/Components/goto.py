import tkinter as tk
from tkinter import ttk

from src.Components.tkentry import Entry
from src.Components.tktext import EnhancedText
from src.Utils.images import get_image


class Navigate:
    def __init__(self, text: EnhancedText):
        self.text = text
        self.goto_frame = ttk.Frame(self.text.frame)
        self._style = ttk.Style()
        self.goto_frame.pack(anchor="nw")
        ttk.Label(self.goto_frame, text="Go to place: [Ln].[Col]").pack(side="left")
        self.location = Entry(self.goto_frame)
        self.location.focus_set()
        self.location.pack(side="left", anchor="nw")
        ttk.Button(self.goto_frame, command=self._goto, text="OK").pack(
            side="left", anchor="nw"
        )
        ttk.Button(self.goto_frame, image=get_image("close"), command=self._exit, width=1).pack(
            side="left", anchor="nw"
        )
        self.statuslabel = ttk.Label(self.goto_frame, foreground="red")
        self.statuslabel.pack(side="left", anchor="nw")

    def check(self) -> bool:
        index = self.location.get().split(".")
        lines = int(float(self.text.index("end")))

        try:
            if len(index) != 2 and int(index[0]) > lines:
                raise ValueError
        except ValueError:  # If not int given
            self.statuslabel.config(text=f'Error: invalid index: {".".join(index)}')
            return False
        return True

    def _goto(self) -> None:
        try:
            if self.check():
                currtext = self.text

                index = self.location.get().split(".")
                if len(index) == 1:
                    currtext.mark_set("insert", f"{index[0]}.0")
                else:
                    currtext.mark_set("insert", f"{index[0]}.{index[1]}")
                currtext.see("insert")
                self._exit()
                return
        except tk.TclError:
            self.check()

    def _exit(self):
        self.goto_frame.pack_forget()
        self.text.focus_set()
        self.text.navigate = False
