import tkinter as tk
from tkinter import ttk

from mistune import escape, HTMLRenderer, Markdown
from mistune.plugins.table import plugin_table
from pygments import highlight
from pygments.formatters import html
from pygments.lexers import get_lexer_by_name
from tkhtmlview import HTMLText

from src.Components.scrollbar import Scrollbar
from src.Components.winframe import WinFrame
from src.SettingsParser.general_settings import GeneralSettings
from src.SettingsParser.helpfiles import HelpFiles
from src.tktypes import Tk_Win
from src.Utils.color_utils import lighten_color
from src.Utils.images import get_image


class HighlightRenderer(HTMLRenderer):
    def block_code(self, code, info=None) -> str:
        if info:
            if info == "jsonc":
                info = "json"  # JSONC causes problems
            lexer = get_lexer_by_name(info, stripall=True)
            pygments_style = GeneralSettings().get_settings("pygments_theme")
            formatter = html.HtmlFormatter(noclasses=True, style=pygments_style)
            return highlight(code, lexer, formatter)
        bg = ttk.Style().lookup("TFrame", "background")
        fg = ttk.Style().lookup("TFrame", "foreground")
        return f'<pre style="font-family: \'TkFixedFont\',sans-serif; color: {fg}; background-color: ' \
               f'{lighten_color(bg, 15)}">\
                <code>' \
            + escape(code) \
            + '</code></pre>'

    def codespan(self, text) -> str:
        fg = ttk.Style().lookup("TFrame", "foreground")
        bg = ttk.Style().lookup("TFrame", "background")
        return f'<pre style="font-family: \'TkFixedFont\',sans-serif; color: {fg}; background-color: ' \
               f'{lighten_color(bg, 15)}">' \
            + escape(text) + '</pre>'

    def text(self, text) -> str:
        fg = ttk.Style().lookup("TFrame", "foreground")
        return f'<span style="color: {fg}">' + text + '</span>'

    def list_item(self, *text, **_) -> str:
        fg = ttk.Style().lookup("TFrame", "foreground")
        return f'<span style="color: {fg}"><li>' + text[0] + '</li></span>'


class HelpView(WinFrame):
    def __init__(self, master: Tk_Win) -> None:
        super().__init__(master, "Help", False, True, get_image("question"))
        self.settings = HelpFiles()

        self.panedwin = tk.PanedWindow(self, orient="horizontal")

        self.tree = ttk.Treeview(self.panedwin, show="tree")
        self.tree.bind("<Double-1>", self.on_double_click)
        self.panedwin.add(self.tree)
        self.create_tree()

        self.html_frame = ttk.Frame(self.panedwin)
        self.html = HTMLText(self.html_frame)

        yscroll = Scrollbar(self.html_frame, command=self.html.yview, orient="vertical")
        xscroll = Scrollbar(self.html_frame, command=self.html.xview, orient="horizontal")

        yscroll.pack(side="right", fill="y")
        xscroll.pack(side="bottom", fill="x")
        self.html.pack(fill="both", expand=True, padx=5, pady=5)

        self.html.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)
        self.panedwin.add(self.html_frame)
        self.panedwin.pack(fill="both", expand=True)

        self.show_help(self.settings.get_default)

    def create_tree(self) -> None:
        self.tree.delete(*self.tree.get_children())
        for name in self.settings.get_name():
            self.tree.insert("", "end", text=name)

    def on_double_click(self, event) -> None:
        item = self.tree.identify("item", event.x, event.y)
        text = self.tree.item(item, "text")
        self.show_help(self.settings.get_file(text))

    def apply_custom_style(self, text) -> None:
        bg = ttk.Style(self.master).lookup("TFrame", "background")
        self.html.configure(highlightthickness=0, borderwidth=0, bg=bg, state="normal")

        self.html.set_html(text)
        self.html.configure(state="disabled")

    def show_help(self, file: str) -> None:
        with open(file, "r") as f:
            markdown = Markdown(renderer=HighlightRenderer(), plugins=[plugin_table])
            contents = markdown(f.read())
            self.apply_custom_style(contents)
