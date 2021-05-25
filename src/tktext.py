"""A modded version of tkinter.Text"""

from src.modules import font, styles, tk, ttk, EditorErr
from src.settings import Settings
from src.functions import darken_color, is_dark_color, lighten_color
from src.constants import MAIN_KEY, logger
from src.highlighter import create_tags, recolorize


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
        style = styles.get_style_by_name(settings_class.get_settings("pygments"))
        bgcolor = style.background_color
        fgcolor = style.highlight_color
        if is_dark_color(bgcolor):
            bg = lighten_color(bgcolor, 30, 30, 30)
            fg = lighten_color(fgcolor, 40, 40, 40)
        else:
            bg = darken_color(bgcolor, 30, 30, 30)
            fg = darken_color(fgcolor, 40, 40, 40)
        self.text = EnhancedText(
            self,
            bg=bgcolor,
            fg=fgcolor,
            selectforeground=bg,
            selectbackground=fgcolor,
            insertbackground=fg,
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


class TextOpts:
    def __init__(self, textwidget: tk.Text, bindkey: bool = False, keyaction: callable = None):
        if bindkey and keyaction:
            raise EditorErr('`bindkey` and `keyaction` cannot be specified at the same time.')
        self.keyaction = keyaction
        self.bindkey = bindkey
        self.text = textwidget
        self.settings_class = Settings()
        self.tabwidth = self.settings_class.get_settings("tab")
        self.text.bind("<<Key>>", self.key)
        self.text.event_add("<<Key>>", "<KeyRelease>")
        for char in ['"', "'", "(", "[", "{"]:
            self.text.bind(char, self.autoinsert)
        for char in [")", "]", "}"]:
            self.text.bind(char, self.close_brackets)
        self.text.bind("<BackSpace>", self.backspace)
        self.text.bind("<Return>", self.autoindent)
        self.text.bind("<Tab>", self.tab)
        self.text.bind(f"<{MAIN_KEY}-i>", lambda _=None: self.indent("indent"))
        self.text.bind(f"<{MAIN_KEY}-u>", lambda _=None: self.indent("unindent"))
        self.text.bind(f"<{MAIN_KEY}-Z>", self.redo)
        self.text.bind(f"<{MAIN_KEY}-z>", self.undo)
        self.text.bind(f"{MAIN_KEY}-d", self.duplicate_line)
        create_tags(self.text)
        recolorize(self.text)

    def tab(self, event=None):
        # Convert tabs to spaces
        event.widget.insert("insert", " " * self.tabwidth)
        self.key()
        # Quit quickly, before a char is being inserted.
        return "break"

    def key(self, _=None) -> None:
        """Event when a key is pressed."""
        if self.bindkey:
            currtext = self.text
            recolorize(currtext)
            currtext.edit_separator()
            currtext.see("insert")
            logger.exception("Error when handling keyboard event:")
        else:
            self.keyaction()

    def duplicate_line(self) -> None:
        currtext = self.text
        sel = currtext.get("sel.first", "sel.last")
        if currtext.tag_ranges("sel"):
            currtext.tag_remove("sel", "1.0", "end")
            currtext.insert("insert", sel)
        else:
            text = currtext.get("insert linestart", "insert lineend")
            currtext.insert("insert", "\n" + text)
        self.key()

    def backspace(self, _=None) -> None:
        currtext = self.text
        # Backchar
        if currtext.get("insert -1c", "insert +1c") in ["''", '""', "[]", "{}", "()"]:
            currtext.delete("insert", "insert +1c")
        # Backtab
        if currtext.get(f"insert -{self.tabwidth}c", "insert") == " " * self.tabwidth:
            currtext.delete(f"insert -{self.tabwidth - 1}c", "insert")
        self.key()

    def close_brackets(self, event: tk.EventType = None) -> str:
        currtext = self.text
        if (event.char in [")", "]", "}", "'", '"'] and
                currtext.get('insert -1c', 'insert') in [")", "]", "}", "'", '"']):
            currtext.mark_set("insert", "insert +1c")
            self.key()
            return "break"
        currtext.delete("insert", 'insert +1c')
        self.key()

    def autoinsert(self, event=None) -> str:
        """Auto-inserts a symbol
        * ' -> ''
        * " -> ""
        * ( -> ()
        * [ -> []
        * { -> {}"""
        currtext = self.text
        char = event.char
        if currtext.tag_ranges("sel"):
            selected = currtext.get("sel.first", "sel.last")
            if char == "'":
                currtext.delete("sel.first", "sel.last")
                currtext.insert("insert", f"'{selected}'")
                return "break"
            if char == '"':
                currtext.delete("sel.first", "sel.last")
                currtext.insert("insert", f'"{selected}"')
                return "break"
            if char == "(":
                currtext.delete("sel.first", "sel.last")
                currtext.insert("insert", f"({selected})")
                return "break"
            if char == "[":
                currtext.delete("sel.first", "sel.last")
                currtext.insert("insert", f"[{selected}]")
                return "break"
            if char == "{":
                currtext.delete("sel.first", "sel.last")
                currtext.insert(
                    "insert", "{" + selected + "}"
                )  # Can't use f-string for this!
                return "break"

        if char == "'":
            if currtext.get("insert", "insert +1c") == "'":
                currtext.mark_set("insert", "insert +1c")
                return "break"
            currtext.insert("insert", "''")
            currtext.mark_set("insert", "insert -1c")
            return "break"
        if char == '"':
            if currtext.get("insert", "insert +1c") == '"':
                currtext.mark_set("insert", "insert +1c")
                return "break"
            currtext.insert("insert", '""')
            currtext.mark_set("insert", "insert -1c")
            return "break"
        if char == "(":
            currtext.insert("insert", "()")
            currtext.mark_set("insert", "insert -1c")
            return "break"
        if char == "[":
            currtext.insert("insert", "[]")
            currtext.mark_set("insert", "insert -1c")
            return "break"
        if char == "{":
            currtext.insert("insert", r"{}")
            currtext.mark_set("insert", "insert -1c")
            return "break"
        currtext.mark_set("insert", "insert -1c")
        self.key()

    def autoindent(self, _=None) -> str:
        """Auto-indents the next line"""
        currtext = self.text
        indentation = ""
        lineindex = currtext.index("insert").split(".")[0]
        linetext = currtext.get(lineindex + ".0", lineindex + ".end")
        for character in linetext:
            if character in [" ", "\t"]:
                indentation += character
            else:
                break

        if linetext.endswith(":"):
            indentation += " " * self.tabwidth
        if linetext.endswith("\\"):
            indentation += " " * self.tabwidth
        if "return" in linetext or "break" in linetext:
            indentation = indentation[4:]
        if linetext.endswith("(") or linetext.endswith(", ") or linetext.endswith(","):
            indentation += " " * self.tabwidth

        currtext.insert(currtext.index("insert"), "\n" + indentation)
        self.key()
        return "break"

    def undo(self, _=None) -> None:
        try:
            self.text.edit_undo()
            self.key()
        except Exception:
            return

    def redo(self, _=None) -> None:
        try:
            self.text.edit_redo()
            self.key()
        except Exception:
            return
