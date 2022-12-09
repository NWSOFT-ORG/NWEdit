"""A modded version of tkinter.Text"""

import tkinter as tk
from tkinter import font, ttk
from typing import Union

from pygments import lexers, styles

from src.Components.scrollbar import TextScrollbar
from src.constants import logger, OSX
from src.errors import EditorErr
from src.highlighter import create_tags, recolorize, recolorize_line
from src.SettingsParser.general_settings import GeneralSettings
from src.Utils.color_utils import darken_color, lighten_color
from src.Utils.functions import apply_style


def font_height(font_name, size) -> int:
    f = font.Font(font=font_name, size=size)
    return f.metrics("linespace")


class TextLineNumbers(tk.Canvas):
    """Line numbers class for Tkinter text widgets. From stackoverflow."""

    def __init__(self, *args: any, **kwargs: any) -> None:
        super().__init__(*args, **kwargs)
        self.textwidget = None

    def attach(self, text_widget: tk.Text) -> None:
        self.textwidget = text_widget

    def advancedredraw(self, line: str, first: int) -> None:
        """redraw line numbers"""
        if not self.textwidget:
            return

        self.delete("all")

        i = self.textwidget.index("@0,0")
        w = len(self.textwidget.index("end-1c linestart"))
        while True:
            dline = self.textwidget.dlineinfo(i)
            if dline is None:
                break
            y = dline[1]
            linenum = str(int(str(i).split(".")[0]) + first - 1)

            light_fg = lighten_color(self.textwidget["fg"], 40)
            dark_fg = darken_color(self.textwidget["fg"], 5)

            test_font = font.Font(font=self.textwidget["font"], weight="bold")
            width = test_font.measure("0" * (w + 4))
            self.config(width=width)

            if int(linenum) == int(float(line)):
                bold = font.Font(font=self.textwidget["font"], weight="bold")
                self.create_text(
                    2,
                    y,
                    anchor="nw",
                    text=linenum,
                    fill=light_fg,
                    font=bold,
                )
            else:
                self.create_text(
                    2,
                    y,
                    anchor="nw",
                    text=linenum,
                    fill=dark_fg,
                    font=self.textwidget["font"],
                )
            i = self.textwidget.index(f"{i}+1line")

    def redraw(self, first: int) -> None:
        """redraw line numbers"""
        if not self.textwidget:
            return

        self.delete("all")

        i = self.textwidget.index("@0,0")
        w = len(self.textwidget.index("end-1c linestart"))
        test_font = font.Font(family=self.textwidget["font"], weight="bold")
        width = test_font.measure("0" * (w + 4))
        self.config(width=width)
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
            i = self.textwidget.index(f"{i}+1line")


class EnhancedText(tk.Text):
    """Text widget, but 'records' your key actions
    If you hit a key, or the text widget's content has changed,
    it generats an event, to redraw the line numbers."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.settings = GeneralSettings(self.master)
        self.config(blockcursor=self.settings.get_settings("block_cursor"))
        self.frame = self.master
        self.controller = None
        self.search = False
        self.navigate = False
        self.lexer = lexers.get_lexer_by_name("text")

        # create a proxy for the underlying widget
        self._rename_orig()

    # noinspection PyUnresolvedReferences
    def _rename_orig(self):
        self._orig = self._w + "_orig"
        self.tk.call("rename", self._w, self._orig)
        self.tk.createcommand(self._w, self._proxy)

    def set_spacing(self, _):
        self.update_idletasks()
        space = int(
            font_height(self.settings.get_font(), self.settings.get_settings("font_size")) * (
                    self.settings.get_settings("line_height") - 1)
        ) / 2
        self.config(spacing1=space, spacing3=space)

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
        except tk.TclError:
            pass


class EnhancedTextFrame(ttk.Frame):
    """An enhanced text frame to put the
    text widget with linenumbers in."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        settings_class = GeneralSettings()
        self.first_line = 1
        style = styles.get_style_by_name(settings_class.get_settings("pygments_theme"))
        bgcolor = style.background_color

        self.text = EnhancedText(self)
        apply_style(self.text)
        self.bind("<Configure>", self.text.set_spacing)
        self.linenumbers = TextLineNumbers(
            self, width=30, bg=bgcolor, bd=0, highlightthickness=0
        )
        self.linenumbers.attach(self.text)

        self.linenumbers.pack(side="left", fill="y")
        xscroll = TextScrollbar(
            self, command=self.text.xview, orient="horizontal", widget=self.text
        )
        xscroll.pack(side="bottom", fill="x", anchor="nw")
        yscroll = TextScrollbar(self, command=self.text.yview, widget=self.text)
        self.text["yscrollcommand"] = yscroll.set
        yscroll.pack(side="right", fill="y")
        self.text.pack(side="right", fill="both", expand=True)

        self.text["xscrollcommand"] = xscroll.set

        self.text.bind("<<Change>>", self.on_change)
        self.text.bind("<Configure>", self._on_resize)

    def on_change(self, _=None) -> None:
        currline = self.text.index("insert")
        self.linenumbers.advancedredraw(first=self.first_line, line=currline)

        self.text.tag_remove("current_line", "1.0", "end")
        self.text.tag_add("current_line", "insert linestart", "insert lineend +1c")
        self.text.tag_config("current_line", background=lighten_color(self.text.cget("background"), 20))

    def _on_resize(self, _=None) -> None:
        self.linenumbers.redraw(first=self.first_line)

    def set_first_line(self, line: int) -> None:
        self.first_line = line


class TextOpts:
    def __init__(self, master, bindkey: bool = False, keyaction: callable = None):
        self.keyaction = keyaction
        self.bindkey = bindkey
        self.master = master

        self.settings_class = GeneralSettings()
        self.tabwidth = self.settings_class.get_settings("tab_width")
        self.style = ttk.Style()
        self.bg = self.style.lookup("TLabel", "background")
        self.fg = self.style.lookup("TLabel", "foreground")

    def set_text(self, text: EnhancedText):
        self.text = text
        self.bind_events()
        return self

    @property
    def right_click_menu(self):
        right_click_menu = tk.Menu(self.text)
        right_click_menu.add_command(label="Undo", command=self.undo)
        right_click_menu.add_command(label="Redo", command=self.redo)
        right_click_menu.add_command(label="Cut", command=self.cut)
        right_click_menu.add_command(label="Copy", command=self.copy)
        right_click_menu.add_command(label="Paste", command=self.paste)
        right_click_menu.add_command(label="Delete", command=self.delete)
        right_click_menu.add_command(label="Select All", command=self.select_all)
        logger.debug("Right-click menu created")
        return right_click_menu

    def bind_events(self):
        text = self.text
        text.bind("<<Key>>", self.key)
        text.event_add("<<Key>>", "<KeyRelease>")
        for char in ['"', "'", "(", "[", "{"]:
            text.bind(char, self.autoinsert)
        for char in [")", "]", "}"]:
            text.bind(char, self.close_brackets)
        text.bind("<<BackSpace>>", self.backspace)
        text.event_add("<<BackSpace>>", "<BackSpace>")
        text.bind("<Return>", self.autoindent)
        text.bind("<Tab>", self.tab)
        text.bind(
            ("<Button-2>" if OSX else "<Button-3>"),
            lambda e: self.right_click_menu.post(e.x_root, e.y_root)
        )
        create_tags(text)
        recolorize(text, text.lexer)

    def tab(self, _=None):
        # Convert tabs to spaces
        self.text.insert("insert", " " * self.tabwidth)
        recolorize(self.text, self.text.lexer)
        self.key()
        # Quit quickly, before a char is being inserted.
        return "break"

    def key(self, event: tk.Event = None) -> None:
        """Event when a key is pressed."""
        if self.bindkey:
            currtext = self.text
            recolorize_line(currtext, currtext.lexer)
            currtext.edit_separator()
            currtext.see("insert")
            logger.exception("Error when handling keyboard event:")
        else:
            self.keyaction(event)

    def duplicate_line(self) -> None:
        currtext = self.text
        sel = currtext.get("sel.first", "sel.last")
        if currtext.tag_ranges("sel"):
            currtext.tag_remove("sel", "1.0", "end")
            currtext.insert("insert", sel)
        else:
            text = currtext.get("insert linestart", "insert lineend")
            currtext.insert("insert", "\n" + text)
        recolorize(currtext, currtext.lexer)
        self.key()

    def indent(self, action="indent") -> None:
        """Indent/unindent feature."""
        currtext = self.text
        if currtext.tag_ranges("sel"):
            sel_start = currtext.index("sel.first linestart")
            sel_end = currtext.index("sel.last lineend")
        else:
            sel_start = currtext.index("insert linestart")
            sel_end = currtext.index("insert lineend")
        if action == "indent":
            selected_text = currtext.get(sel_start, sel_end)
            indented = []
            for line in selected_text.splitlines():
                indented.append(" " * self.tabwidth + line)
            currtext.delete(sel_start, sel_end)
            currtext.insert(sel_start, "\n".join(indented))
            currtext.tag_remove("sel", "1.0", "end")
            currtext.tag_add("sel", sel_start, f"{sel_end} +{self.tabwidth}c")
        elif action == "unindent":
            selected_text = currtext.get(sel_start, sel_end)
            unindented = []
            for line in selected_text.splitlines():
                if line.startswith(" " * self.tabwidth):
                    unindented.append(line[self.tabwidth:])
                else:
                    return
            currtext.delete(sel_start, sel_end)
            currtext.insert(sel_start, "\n".join(unindented))
            currtext.tag_remove("sel", "1.0", "end")
            currtext.tag_add("sel", sel_start, sel_end)
        else:
            raise EditorErr("Action undefined.")
        recolorize(currtext, currtext.lexer)
        self.key()

    def comment_lines(self, _=None):
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
            recolorize(currtext, currtext.lexer)
            self.key()
        except (KeyError, AttributeError):
            return

    def backspace(self, _=None) -> str:
        currtext = self.text
        if currtext.tag_ranges("sel"):  # If text selected
            currtext.delete("sel.first", "sel.last")
            return "break"
        # Backspace a char
        if currtext.get("insert -1c", "insert +1c") in ["''", '""', "[]", "{}", "()", "<>"]:
            currtext.delete("insert", "insert +1c")
            self.key()
            return "break"
        # Backspace a tab
        if currtext.get(f"insert -{self.tabwidth}c", "insert") == " " * self.tabwidth:
            currtext.delete(f"insert -{self.tabwidth - 1}c", "insert")
            self.key()
            return "break"
        currtext.delete("insert -1c", "insert")
        self.key()
        return "break"

    def close_brackets(self, event: Union[tk.Event, None] = None) -> str:
        currtext = self.text
        if event:
            if event.char in [")", "]", "}", "'", '"'] and currtext.get(
                    "insert -1c", "insert"
            ) in [")", "]", "}", "'", '"']:
                currtext.mark_set("insert", "insert +1c")
                self.key()
                return "break"
        currtext.delete("insert", "insert +1c")
        self.key()

    def autoinsert(self, event: tk.Event = None) -> str:
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
            recolorize(self.text, self.text.lexer)
            self.key()
        except tk.TclError:
            return

    def redo(self, _=None) -> None:
        try:
            self.text.edit_redo()
            recolorize(self.text, self.text.lexer)
            self.key()
        except tk.TclError:
            return

    def copy(self) -> None:
        try:
            sel = self.text.get("sel.first", "sel.last")
            self.text.clipboard_clear()
            self.text.clipboard_append(sel)
        except tk.TclError:
            pass

    def delete(self) -> None:
        self.text.delete("sel.first", "sel.last")
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
                    "insert", clipboard
                )
            recolorize(self.text, self.text.lexer)
            self.key()
        except tk.TclError:
            pass
        finally:
            return "break"

    def select_all(self) -> None:
        try:
            self.text.tag_add("sel", "1.0", "end")
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
        recolorize(currtext, currtext.lexer)
        self.key()

    def mv_line_up(self) -> None:
        currtext = self.text
        text = currtext.get("insert -1l lineend", "insert lineend")
        currtext.delete("insert -1l lineend", "insert lineend")
        currtext.mark_set("insert", "insert -1l")
        currtext.insert("insert", text)
        recolorize(currtext, currtext.lexer)
        self.key()

    def mv_line_dn(self) -> None:
        currtext = self.text
        text = currtext.get("insert -1l lineend", "insert lineend")
        currtext.delete("insert -1l lineend", "insert lineend")
        currtext.mark_set("insert", "insert +1l")
        currtext.insert("insert", text)
        recolorize(currtext, currtext.lexer)
        self.key()

    def swap_case(self):
        currtext = self.text
        if not currtext.tag_ranges("sel"):
            return
        text = currtext.get("sel.first", "sel.last")
        currtext.delete("sel.first", "sel.last")
        text = text.swapcase()
        currtext.insert("insert", text)
        recolorize(currtext, currtext.lexer)
        self.key()

    def upper_case(self):
        currtext = self.text
        if not currtext.tag_ranges("sel"):
            return
        text = currtext.get("sel.first", "sel.last")
        currtext.delete("sel.first", "sel.last")
        text = text.upper()
        currtext.insert("insert", text)
        recolorize(currtext, currtext.lexer)
        self.key()

    def lower_case(self):
        currtext = self.text
        if not currtext.tag_ranges("sel"):
            return
        text = currtext.get("sel.first", "sel.last")
        currtext.delete("sel.first", "sel.last")
        text = text.lower()
        currtext.insert("insert", text)
        recolorize(currtext, currtext.lexer)
        self.key()
