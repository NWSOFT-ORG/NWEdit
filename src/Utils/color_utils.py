"""Provides convenient color utilities"""
from src.modules import tk

DARK_COLOR = 128


def hex2dec(hex_code: str) -> int:
    hex_code = str(hex_code)
    if hex_code.startswith("#"):
        hex_code = hex_code[1:]
    return int(hex_code, 16)


def dec2hex(dec: int, color_code: bool = False) -> str:
    dec = hex(dec)
    if color_code:
        dec = "#" + dec[2:]
    return dec


def is_dark_color(hex_code: str) -> bool:
    hex_code = check_hex(hex_code)
    if (
            hex2dec(hex_code[0]) <= DARK_COLOR
            and hex2dec(hex_code[1]) <= DARK_COLOR
            and hex2dec(hex_code[2]) <= DARK_COLOR
    ):
        return True
    return False


def check_hex(color):
    """Converts via winfo_rgb()"""
    checking_win = tk.Toplevel()
    rgb = checking_win.winfo_rgb(color)
    checking_win.destroy()

    rgb = [dec2hex(color // 257) for color in rgb]
    return rgb


def darken_color(hex_code: str, decrement: int) -> str:
    hex_code = check_hex(hex_code)
    rgb = (
        hex2dec(hex_code[0]) - decrement,
        hex2dec(hex_code[1]) - decrement,
        hex2dec(hex_code[2]) - decrement,
    )
    value = "#"
    for x in rgb:
        if x < 0:
            value += "00"
            continue
        value += dec2hex(x)[2:]
    return value


def lighten_color(hex_code, increment) -> str:
    hex_code = check_hex(hex_code)
    rgb = (
        hex2dec(hex_code[0]) + increment,
        hex2dec(hex_code[1]) + increment,
        hex2dec(hex_code[2]) + increment,
    )
    value = "#"
    for x in rgb:
        if x > 255:
            value += "ff"
            continue
        value += dec2hex(x)[2:]
    return value


def replace_color(image: tk.PhotoImage, color, replace):
    pass
