from tkinter import ttk
from typing import Callable

from pygments import lexers

from src.Components.tktext import EnhancedText, EnhancedTextFrame, TextOpts
from src.Components.winframe import WinFrame
from src.types import Tk_Widget
from src.Utils.images import get_image


class CodeInputDialog(WinFrame):
    def __init__(
        self, parent: Tk_Widget, title: str, onsave: Callable
    ) -> None:
        super().__init__(parent, title, closable=False, icon=get_image("question"))

        self.save = self.add_destroy_action(onsave)
        self.textframe = EnhancedTextFrame(self)
        self.textframe.pack(fill="both", expand=1)

        self.text: EnhancedText = self.textframe.text
        self.text.lexer = lexers.get_lexer_by_name("Python")
        TextOpts(self, bindkey=True).set_text(self.text)
        self.text.focus_set()

        self.create_button_box()

    def create_button_box(self) -> None:
        button_frame = ttk.Frame(self)
        okbtn = ttk.Button(button_frame, text="OK", command=self.save)
        okbtn.pack(side="left")
        cancelbtn = ttk.Button(button_frame, text="Cancel", command=self.destroy)
        cancelbtn.pack(side="left")
        button_frame.pack(fill="x")

    def insert(self, pos: str, text: str) -> None:
        self.text.insert(pos, text)

    def get(self, pos1: str, pos2: str) -> str:
        return self.text.get(pos1, pos2)

    def add_destroy_action(self, function: Callable) -> callable:
        def new():
            function()
            self.destroy()

        return new
