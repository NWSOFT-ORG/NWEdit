from typing import *

from src.modules import lexers, tk, ttk
from src.Utils.images import get_image
from src.Widgets.tktext import EnhancedTextFrame, TextOpts
from src.Widgets.winframe import WinFrame


class CodeInputDialog(WinFrame):
    def __init__(
        self, parent: Union[tk.Misc, tk.Tk, tk.Toplevel], title: Text, onsave: Callable
    ) -> None:
        super().__init__(parent, title, closable=False, icon=get_image("question"))

        self.save = self.add_destroy_action(onsave)
        self.textframe = EnhancedTextFrame(self)
        self.textframe.pack(fill="both", expand=1)

        self.text: tk.Text = self.textframe.text
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

    def insert(self, pos: Text, text: Text) -> None:
        self.text.insert(pos, text)

    def get(self, pos1: Text, pos2: Text) -> str:
        return self.text.get(pos1, pos2)

    def add_destroy_action(self, function: Callable) -> callable:
        def new():
            function()
            self.destroy()

        return new