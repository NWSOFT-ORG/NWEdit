from src.modules import font, get_style_by_name, tk
from src.settings import Settings


def create_tags(textbox: tk.Text) -> None:
    """
    The method creates the tags associated with each distinct style element of the
    source code 'dressing'"""
    currtext = textbox
    bold_font = font.Font(currtext, currtext.cget("font"))
    bold_font.configure(weight=font.BOLD)
    italic_font = font.Font(currtext, currtext.cget("font"))
    italic_font.configure(slant=font.ITALIC)
    bold_italic_font = font.Font(currtext, currtext.cget("font"))
    bold_italic_font.configure(weight=font.BOLD, slant=font.ITALIC)
    settings = Settings()
    style = get_style_by_name(settings.get_settings("pygments"))

    for ttype, ndef in style:
        tag_font = None

        if ndef["bold"] and ndef["italic"]:
            tag_font = bold_italic_font
        elif ndef["bold"]:
            tag_font = bold_font
        elif ndef["italic"]:
            tag_font = italic_font

        if ndef["color"]:
            foreground = "#%s" % ndef["color"]
        else:
            foreground = None

        currtext.tag_configure(str(ttype), foreground=foreground, font=tag_font)


def recolorize(textbox: tk.Text) -> None:
    """
    This method colors and styles the prepared tags"""
    try:
        currtext = textbox
        _code = currtext.get("1.0", "end-1c")
        tokensource = currtext.lexer.get_tokens(_code)
        start_line = 1
        start_index = 0
        end_line = 1
        end_index = 0

        for ttype, value in tokensource:
            if "\n" in value:
                end_line += value.count("\n")
                end_index = len(value.rsplit("\n", 1)[1])
            else:
                end_index += len(value)

            index1 = f"{start_line}.{start_index}"
            index2 = f"{end_line}.{end_index}"

            for tagname in currtext.tag_names(index1):
                if tagname not in ["sel", "found"]:
                    currtext.tag_remove(tagname, index1, index2)

            currtext.tag_add(str(ttype), index1, index2)

            start_line = end_line
            start_index = end_index

        currtext.update()  # Have to update
    except Exception:
        pass
