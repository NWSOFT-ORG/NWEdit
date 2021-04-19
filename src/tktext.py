"""A modded version of tkinter.Text"""

from src.modules import font, get_style_by_name, tk, ttk
from src.settings import Settings


class TextLineNumbers(tk.Canvas):
    """Line numbers class for tkinter text widgets. From stackoverflow."""

    def __init__(self, *args: any, **kwargs: any) -> None:
        tk.Canvas.__init__(self, *args, **kwargs)
        self.textwidget = None

    def attach(self, text_widget: tk.Text) -> None:
        self.textwidget = text_widget

    def advancedredraw(self, line: str, first: int) -> None:
        """redraw line numbers"""
        self.delete("all")

        i = self.textwidget.index("@0,0")
        w = len(self.textwidget.index("end-1c linestart"))
        self.config(width=w * 10)
        while True:
            dline = self.textwidget.dlineinfo(i)
            if dline is None:
                break
            y = dline[1]
            linenum = str(int(str(i).split(".")[0]) + first - 1)

            if int(linenum) == int(float(line)):
                bold = font.Font(family=self.textwidget["font"], weight="bold")
                self.create_text(
                    2,
                    y,
                    anchor="nw",
                    text=linenum,
                    fill=self.textwidget["fg"],
                    font=bold,
                )
            else:
                self.create_text(
                    2,
                    y,
                    anchor="nw",
                    text=linenum,
                    fill=self.textwidget["fg"],
                    font=self.textwidget["font"],
                )
            i = self.textwidget.index("%s+1line" % i)

    def redraw(self, first: int) -> None:
        """redraw line numbers"""
        self.delete("all")

        i = self.textwidget.index("@0,0")
        w = len(self.textwidget.index("end-1c linestart"))
        self.config(width=w * 10)
        while True:
            dline = self.textwidget.dlineinfo(i)
            if dline is None:
                break
            y = dline[1]
            linenum = str(int(str(i).split(".")[0]) + first - 1)
            self.create_text(
                2,
                y,
                anchor="nw",
                text=linenum,
                fill=self.textwidget["fg"],
                font=self.textwidget["font"],
            )
            i = self.textwidget.index("%s+1line" % i)


class EnhancedText(tk.Text):
    """Text widget, but 'records' your key actions
    If you hit a key, or the text widget's content has changed,
    it generats an event, to redraw the line numbers."""

    def __init__(self, *args: any, **kwargs: any) -> None:
        tk.Text.__init__(self, *args, **kwargs)
        self.searchable = False
        self.navigate = False

        # create a proxy for the underlying widget
        self._orig = self._w + "_orig"
        self.tk.call("rename", self._w, self._orig)
        self.tk.createcommand(self._w, self._proxy)

    def set_lexer(self, lexer):
        self.lexer = lexer

    def _proxy(self, *args: list) -> object:
        try:
            # The text widget might throw an error while pasting text!
            # let the actual widget perform the requested action
            cmd = (self._orig,) + args
            result = self.tk.call(cmd)

            # generate an event if something was added or deleted,
            # or the cursor position changed
            if (
                args[0] in ("insert", "replace", "delete")
                or args[0:3] == ("mark", "set", "insert")
                or args[0:2] == ("xview", "moveto")
                or args[0:2] == ("xview", "scroll")
                or args[0:2] == ("yview", "moveto")
                or args[0:2] == ("yview", "scroll")
            ):
                self.event_generate("<<Change>>", when="tail")

            # return what the actual widget returned

            return result
        except Exception:
            pass


class EnhancedTextFrame(ttk.Frame):
    """An enhanced text frame to put the
    text widget with linenumbers in."""

    def __init__(self, *args, **kwargs) -> None:
        ttk.Frame.__init__(self, *args, **kwargs)
        settings_class = Settings()
        self.font = settings_class.get_settings("font")
        self.first_line = 1
        style = get_style_by_name(settings_class.get_settings("pygments"))
        bgcolor = style.background_color
        fgcolor = style.highlight_color
        self.text = EnhancedText(
            self,
            bg=bgcolor,
            fg=fgcolor,
            selectforeground=bgcolor,
            selectbackground=fgcolor,
            insertbackground=fgcolor,
            highlightthickness=0,
            font=self.font,
            wrap="none",
            insertwidth=3,
            maxundo=-1,
            autoseparators=1,
            undo=True,
        )
        self.linenumbers = TextLineNumbers(
            self, width=30, bg=bgcolor, bd=0, highlightthickness=0
        )
        self.linenumbers.attach(self.text)

        self.linenumbers.pack(side="left", fill="y")
        xscroll = ttk.Scrollbar(self, command=self.text.xview, orient="horizontal")
        xscroll.pack(side="bottom", fill="x", anchor="nw")
        yscroll = ttk.Scrollbar(self, command=self.text.yview)
        self.text["yscrollcommand"] = yscroll.set
        yscroll.pack(side="right", fill="y")
        self.text.pack(side="right", fill="both", expand=True)

        self.text["xscrollcommand"] = xscroll.set

        self.text.bind("<<Change>>", self.on_change)
        self.text.bind("<Configure>", self._on_resize)

    def on_change(self, _=None) -> None:
        currline = self.text.index("insert")
        self.linenumbers.advancedredraw(first=self.first_line, line=currline)

    def _on_resize(self, _=None) -> None:
        self.linenumbers.redraw(first=self.first_line)

    def set_first_line(self, line: int) -> None:
        self.first_line = line
