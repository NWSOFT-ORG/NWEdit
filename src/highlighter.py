import tkinter as tk
from tkinter import font

import pygments
from pygments import styles

from src.SettingsParser.general_settings import GeneralSettings


def create_tags(textbox: tk.Text) -> None:
    """
    The method creates the tags associated with each distinct style element of the
    source code 'dressing'"""
    currtext = textbox
    settings = GeneralSettings()
    bold_font = font.Font(currtext, settings.get_font())
    bold_font.configure(weight=font.BOLD)
    italic_font = font.Font(currtext, settings.get_font())
    italic_font.configure(slant=font.ITALIC)
    bold_italic_font = font.Font(currtext, settings.get_font())
    bold_italic_font.configure(weight=font.BOLD, slant=font.ITALIC)
    style = styles.get_style_by_name(settings.get_settings("pygments_theme"))

    for ttype, ndef in style:
        tag_font = ''

        if ndef["bold"] and ndef["italic"]:
            tag_font = bold_italic_font
        elif ndef["bold"]:
            tag_font = bold_font
        elif ndef["italic"]:
            tag_font = italic_font

        if ndef["color"]:
            foreground = f"#{ndef['color']}"
        else:
            foreground = ''

        currtext.tag_configure(str(ttype), foreground=foreground, font=tag_font)


def recolorize(textbox: tk.Text, lexer) -> None:
    """
    This method colors and styles the prepared tags"""
    currtext = textbox
    start_index = currtext.index("1.0")
    end_index = currtext.index("end")

    for tag in currtext.tag_names():
        if tag in ["sel", "found"]:
            continue
        currtext.tag_remove(tag, start_index, end_index)

    _code = currtext.get(start_index, end_index)

    for index, line in enumerate(_code):
        if index == 0 and line != "\n":
            break
        elif line == "\n":
            start_index = currtext.index(f"{start_index}+1line")
        else:
            break

    currtext.mark_set("range_start", start_index)
    for token, content in pygments.lex(_code, lexer):
        currtext.mark_set("range_end", f"range_start + {len(content)}c")
        currtext.tag_add(str(token), "range_start", "range_end")
        currtext.mark_set("range_start", "range_end")


# noinspection DuplicatedCode
def recolorize_line(textbox: tk.Text, lexer) -> None:
    """
    This method colors and styles the prepared tags"""
    currtext = textbox
    start_index = currtext.index("insert -1c linestart")
    end_index = currtext.index("insert lineend")

    tri_str_start = []
    tri_str_end = []
    tri_str = []
    cursor_pos = float(currtext.index("insert"))
    for index, linenum in enumerate(currtext.tag_ranges("Token.Literal.String.Doc")):
        if index % 2 == 1:
            tri_str_end.append(float(str(linenum)))
        else:
            tri_str_start.append(float(str(linenum)))

    for index, value in enumerate(tri_str_start):
        tri_str.append((value, tri_str_end[index]))

    for x in tri_str:
        if x[0] <= cursor_pos <= x[1]:
            start_index = str(x[0])
            end_index = str(x[1])

    for tag in currtext.tag_names():
        if tag in ["sel", "found"]:
            continue
        currtext.tag_remove(tag, start_index, end_index)

    _code = currtext.get(start_index, end_index)

    currtext.mark_set("range_start", start_index)
    for token, content in pygments.lex(_code, lexer):
        currtext.mark_set("range_end", f"range_start + {len(content)}c")
        currtext.tag_add(str(token), "range_start", "range_end")
        currtext.mark_set("range_start", "range_end")
