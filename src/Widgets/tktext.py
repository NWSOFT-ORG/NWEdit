"""A modded version of tkinter.Text"""

from src.modules import font, styles, tk, ttk, ttkthemes, lexers
from src.settings import Settings
from src.functions import darken_color, is_dark_color, lighten_color
from src.constants import MAIN_KEY, logger
from src.highlighter import create_tags, recolorize, recolorize_line


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
        super().__init__(*args, **kwargs)
        self.comment_marker = ""
        self.opts = None
        self.searchable = False
        self.navigate = False
        self.lexer = lexers.get_lexer_by_name('text')

        # create a proxy for the underlying widget
        self._orig = self._w + "_orig"
        self.tk.call("rename", self._w, self._orig)
        self.tk.createcommand(self._w, self._proxy)

    def set_lexer(self, lexer: str) -> None:
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
        except tk.TclError:
            pass


class EnhancedTextFrame(ttk.Frame):
    """An enhanced text frame to put the
    text widget with linenumbers in."""

    def __init__(self, *args: any, **kwargs: any) -> None:
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

    def on_change(self, _: tk.Event = None) -> None:
        currline = self.text.index("insert")
        self.linenumbers.advancedredraw(first=self.first_line, line=currline)

    def _on_resize(self, _: tk.Event = None) -> None:
        self.linenumbers.redraw(first=self.first_line)

    def set_first_line(self, line: int) -> None:
        self.first_line = line


class TextEditingPlugin:
    def __init__(self, bindkey: bool = False, keyaction: callable = None):
        self.keyaction = keyaction
        self.bindkey = bindkey
        self.settings_class = Settings()
        self.tabwidth = self.settings_class.get_settings("tab")
        self.theme = self.settings_class.get_settings("theme")
        self.style = ttkthemes.ThemedStyle()
        self.style.set_theme(self.theme)
        self.bg = self.style.lookup("TLabel", "background")
        self.fg = self.style.lookup("TLabel", "foreground")
        if is_dark_color(self.bg):
            self.copy_icon = tk.PhotoImage(file="Images/copy-light.gif")
            self.delete_icon = tk.PhotoImage(file="Images/delete-light.gif")
            self.indent_icon = tk.PhotoImage(file="Images/indent-light.gif")
            self.paste_icon = tk.PhotoImage(file="Images/paste-light.gif")
            self.unindent_icon = tk.PhotoImage(file="Images/unindent-light.gif")
            self.sel_all_icon = tk.PhotoImage(file="Images/sel-all-light.gif")
        else:
            self.copy_icon = tk.PhotoImage(file="Images/copy.gif")
            self.delete_icon = tk.PhotoImage(file="Images/delete.gif")
            self.indent_icon = tk.PhotoImage(file="Images/indent.gif")
            self.paste_icon = tk.PhotoImage(file="Images/paste.gif")
            self.unindent_icon = tk.PhotoImage(file="Images/unindent.gif")
            self.sel_all_icon = tk.PhotoImage(file="Images/sel-all.gif")
        self.cut_icon = tk.PhotoImage(file="Images/cut.gif")
        self.redo_icon = tk.PhotoImage(file="Images/redo.gif")
        self.undo_icon = tk.PhotoImage(file="Images/undo.gif")

    def set_text(self, text: [EnhancedText, tk.Text]) -> None:
        self.text = text
        self.bind_events()

    def create_menu(self, master: tk.Tk):
        """Creates the menu for the master"""
        menu = tk.Menu(master)
        menu.add_command(
            label="Undo",
            command=self.undo,
            image=self.undo_icon,
            compound='left'
        )
        menu.add_command(
            label="Redo",
            command=self.redo,
            image=self.redo_icon,
            compound='left'
        )
        menu.add_command(
            label="Cut",
            command=self.cut,
            image=self.cut_icon,
            compound='left'
        )
        menu.add_command(
            label="Copy",
            command=self.copy,
            image=self.copy_icon,
            compound='left'
        )
        menu.add_command(
            label="Paste",
            command=self.paste,
            image=self.paste_icon,
            compound='left'
        )
        menu.add_command(
            label="Duplicate Line or Selected", command=self.duplicate_line
        )
        indent_cascade = tk.Menu(menu)
        indent_cascade.add_command(
            label="Indent",
            command=lambda: self.indent(True),
            image=self.indent_icon,
            compound='left'
        )
        indent_cascade.add_command(
            label="Unident",
            command=lambda: self.indent(False),
            image=self.unindent_icon,
            compound='left'
        )
        menu.add_cascade(label='Indent...', menu=indent_cascade)
        menu.add_command(
            label="Comment/Uncomment Line or Selected", command=self.comment_lines
        )
        menu.add_command(label="Join lines", command=self.join_lines)
        case_cascade = tk.Menu(menu)
        case_cascade.add_command(label="Swap case", command=self.swap_case)
        case_cascade.add_command(label="Upper case", command=self.upper_case)
        case_cascade.add_command(label="Lower case", command=self.lower_case)
        menu.add_cascade(label='Case...', menu=case_cascade)
        select_cascade = tk.Menu(menu)
        select_cascade.add_command(
            label="Select All",
            command=self.select_all,
            image=self.sel_all_icon,
            compound='left'
        )
        select_cascade.add_command(label="Select Line", command=self.sel_line)
        select_cascade.add_command(label="Select Word", command=self.sel_word)
        select_cascade.add_command(label="Select Prev Word", command=self.sel_word_left)
        select_cascade.add_command(label="Select Next Word", command=self.sel_word_right)
        menu.add_cascade(label='Select...', menu=select_cascade)
        delete_cascade = tk.Menu(menu)
        delete_cascade.add_command(
            label="Delete Selected",
            image=self.delete_icon,
            command=self.delete,
            compound='left'
        )
        delete_cascade.add_command(label="Delete Word", command=self.del_word)
        delete_cascade.add_command(label="Delete Prev Word", command=self.del_word_left)
        delete_cascade.add_command(label="Delete Next Word", command=self.del_word_right)
        menu.add_command(label="-1 char", command=self.nav_1cb)
        menu.add_command(label="+1 char", command=self.nav_1cf)
        menu.add_command(label="Word end", command=self.nav_wordend)
        menu.add_command(label="Word start", command=self.nav_wordstart)
        menu.add_command(label="Move line up", command=self.mv_line_up)
        menu.add_command(label="Move line down", command=self.mv_line_dn)

        right_click_menu = tk.Menu(master)
        right_click_menu.add_command(label="Undo", command=self.undo)
        right_click_menu.add_command(label="Redo", command=self.redo)
        right_click_menu.add_command(label="Cut", command=self.cut)
        right_click_menu.add_command(label="Copy", command=self.copy)
        right_click_menu.add_command(label="Paste", command=self.paste)
        right_click_menu.add_command(label="Delete", command=self.delete)
        right_click_menu.add_command(
            label="Select All", command=self.select_all
        )
        logger.debug("Right-click menu created")
        return [menu, right_click_menu]

    def bind_events(self):
        text = self.text
        text.bind("<KeyRelease>", self.key)
        for char in ['"', "'", "(", "[", "{"]:
            text.bind(char, self.autoinsert)
        for char in [")", "]", "}"]:
            text.bind(char, self.close_brackets)
        text.bind("<BackSpace>", self.backspace)
        text.bind("<Return>", self.autoindent)
        text.bind("<Tab>", self.tab)
        text.bind(f"<{MAIN_KEY}-i>", lambda _=None: self.indent(True))
        text.bind(f"<{MAIN_KEY}-u>", lambda _=None: self.indent(False))
        text.bind(f"<{MAIN_KEY}-Z>", self.redo)
        text.bind(f"<{MAIN_KEY}-z>", self.undo)
        text.bind(f"{MAIN_KEY}-d", self.duplicate_line)
        create_tags(text)
        recolorize(text)

    def tab(self, _: tk.Event = None):
        # Convert tabs to spaces
        self.text.insert("insert", " " * self.tabwidth)
        self.key()
        # Quit quickly, before a char is being inserted.
        return "break"

    def key(self, _: tk.Event = None) -> None:
        """Event when a key is pressed."""
        if self.bindkey:
            currtext = self.text
            recolorize_line(currtext)
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

    def indent(self, indent: bool = True) -> None:
        """Indent/unindent feature."""
        currtext = self.text
        if currtext.tag_ranges("sel"):
            sel_start = currtext.index("sel.first linestart")
            sel_end = currtext.index("sel.last lineend")
        else:
            sel_start = currtext.index("insert linestart")
            sel_end = currtext.index("insert lineend")
        if indent:
            selected_text = currtext.get(sel_start, sel_end)
            indented = []
            for line in selected_text.splitlines():
                indented.append(" " * self.tabwidth + line)
            currtext.delete(sel_start, sel_end)
            currtext.insert(sel_start, "\n".join(indented))
            currtext.tag_remove("sel", "1.0", "end")
            currtext.tag_add("sel", sel_start, f"{sel_end} +4c")
            self.key()
        else:
            selected_text = currtext.get(sel_start, sel_end)
            unindented = []
            for line in selected_text.splitlines():
                if line.startswith(" " * self.tabwidth):
                    unindented.append(line[4:])
                else:
                    return
            currtext.delete(sel_start, sel_end)
            currtext.insert(sel_start, "\n".join(unindented))
            currtext.tag_remove("sel", "1.0", "end")
            currtext.tag_add("sel", sel_start, sel_end)
            self.key()

    def comment_lines(self, _: tk.Event = None):
        """Comments the selection or line"""
        try:
            currtext = self.text
            if not currtext.comment_marker:
                return
            comment_markers = currtext.comment_marker.split(" ")
            block = len(comment_markers) == 2
            if block and comment_markers[1] != "":
                comment_start = comment_markers[0]
                comment_end = comment_markers[1]
            else:
                comment_start = currtext.comment_marker
                comment_end = ""
            if currtext.tag_ranges("sel"):
                start_index, end_index = "sel.first linestart", "sel.last lineend"
                text = currtext.get(start_index, end_index)
                currtext.delete(start_index, end_index)
                if block:
                    if text.startswith(comment_start):
                        currtext.insert(
                            "insert", text[len(comment_start): -len(comment_end)]
                        )
                        self.key()
                        return
                    currtext.insert("insert", f"{comment_start} {text} {comment_end}")
                    self.key()
                    return
                for line in currtext.get(start_index, end_index).splitlines():
                    if line.startswith(comment_start) and line.endswith(comment_end):
                        currtext.insert(
                            "insert",
                            f"{line[len(comment_start) + 1:len(comment_end) + 1]}\n",
                        )
                    else:
                        currtext.insert(
                            "insert", f"{comment_start}{line}{comment_end}\n"
                        )
            else:
                start_index, end_index = "insert linestart", "insert lineend"
                line = currtext.get(start_index, end_index)
                currtext.delete(start_index, end_index)
                if line.startswith(comment_start) and line.endswith(comment_end):
                    currtext.insert(
                        "insert", f"{line[len(comment_start):len(comment_end)]}\n"
                    )
                else:
                    currtext.insert("insert", f"{comment_start}{line}{comment_end}\n")
            self.key()
        except (KeyError, AttributeError):
            return

    def backspace(self, _: tk.Event = None) -> None:
        currtext = self.text
        # Backchar
        if currtext.get("insert -1c", "insert +1c") in ["''", '""', "[]", "{}", "()"]:
            currtext.delete("insert", "insert +1c")
        # Backtab
        if currtext.get(f"insert -{self.tabwidth}c", "insert") == " " * self.tabwidth:
            currtext.delete(f"insert -{self.tabwidth - 1}c", "insert")
        self.key()

    def close_brackets(self, event: tk.Event = None) -> str:
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
            indentation = indentation[self.tabwidth:]
        if linetext.endswith("(") or linetext.endswith(", ") or linetext.endswith(","):
            indentation += " " * self.tabwidth

        currtext.insert(currtext.index("insert"), "\n" + indentation)
        self.key()
        return "break"

    def undo(self, _=None) -> None:
        try:
            self.text.edit_undo()
            self.key()
        except tk.TclError:  # No action needed
            return

    def redo(self, _=None) -> None:
        try:
            self.text.edit_redo()
            self.key()
        except tk.TclError:  # No action needed
            return
    
    def copy(self) -> None:
        try:
            sel = self.text.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.text.clipboard_clear()
            self.text.clipboard_append(sel)
        except tk.TclError:
            pass

    def delete(self) -> None:
        self.text.delete(tk.SEL_FIRST, tk.SEL_LAST)
        self.key()

    def cut(self) -> None:
        try:
            self.copy()
            self.delete()
            self.key()
        except tk.TclError:
            pass

    def paste(self) -> None:
        try:
            clipboard = self.text.clipboard_get()
            if clipboard:
                self.text.insert(
                    "insert", clipboard.replace("\t", " " * self.tabwidth)
                )
            self.key()
        except tk.TclError:  # No clipboard
            pass

    def select_all(self) -> None:
        try:
            self.text.tag_add('sel', "1.0", 'end')
            self.text.mark_set("insert", "end")
            self.text.see("insert")
        except tk.TclError:
            pass
    
    def nav_1cf(self) -> None:
        currtext = self.text
        currtext.mark_set("insert", "insert +1c")

    def nav_1cb(self) -> None:
        currtext = self.text
        currtext.mark_set("insert", "insert -1c")

    def nav_wordstart(self) -> None:
        currtext = self.text
        currtext.mark_set("insert", "insert -1c wordstart")

    def nav_wordend(self) -> None:
        currtext = self.text
        currtext.mark_set("insert", "insert wordend")

    def sel_word(self) -> None:
        currtext = self.text
        currtext.tag_remove("sel", "1.0", "end")
        currtext.tag_add("sel", "insert -1c wordstart", "insert wordend")

    def sel_word_left(self) -> None:
        currtext = self.text
        currtext.mark_set("insert", "insert wordstart -2c")
        self.sel_word()

    def sel_word_right(self) -> None:
        currtext = self.text
        currtext.mark_set("insert", "insert wordend +2c")
        self.sel_word()

    def sel_line(self) -> None:
        currtext = self.text
        currtext.tag_add("sel", "insert linestart", "insert +1l linestart")

    def del_word(self) -> None:
        currtext = self.text
        currtext.delete("insert -1c wordstart", "insert wordend")
        self.key()

    def del_word_left(self) -> None:
        currtext = self.text
        currtext.mark_set("insert", "insert wordstart -2c")
        self.del_word()

    def del_word_right(self) -> None:
        currtext = self.text
        currtext.mark_set("insert", "insert wordend +2c")
        self.del_word()

    def join_lines(self) -> None:
        currtext = self.text
        if not currtext.tag_ranges("sel"):
            return
        sel = currtext.get("sel.first", "sel.last").splitlines()
        if len(sel) < 2:
            return
        sel = "".join(sel)
        currtext.delete("sel.first", "sel.last")
        currtext.insert("insert", sel)
        self.key()

    def mv_line_up(self) -> None:
        currtext = self.text
        text = currtext.get("insert -1l lineend", "insert lineend")
        currtext.delete("insert -1l lineend", "insert lineend")
        currtext.mark_set("insert", "insert -1l")
        currtext.insert("insert", text)

    def mv_line_dn(self) -> None:
        currtext = self.text
        text = currtext.get("insert -1l lineend", "insert lineend")
        currtext.delete("insert -1l lineend", "insert lineend")
        currtext.mark_set("insert", "insert +1l")
        currtext.insert("insert", text)

    def swap_case(self) -> None:
        currtext = self.text
        if not currtext.tag_ranges("sel"):
            return
        text = currtext.get("sel.first", "sel.last")
        currtext.delete("sel.first", "sel.last")
        text = text.swapcase()
        currtext.insert("insert", text)
        self.key()

    def upper_case(self) -> None:
        currtext = self.text
        if not currtext.tag_ranges("sel"):
            return
        text = currtext.get("sel.first", "sel.last")
        currtext.delete("sel.first", "sel.last")
        text = text.upper()
        currtext.insert("insert", text)
        self.key()

    def lower_case(self) -> None:
        currtext = self.text
        if not currtext.tag_ranges("sel"):
            return
        text = currtext.get("sel.first", "sel.last")
        currtext.delete("sel.first", "sel.last")
        text = text.lower()
        currtext.insert("insert", text)
        self.key()
