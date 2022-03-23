"""Useful functions"""

from src.constants import textchars
from src.modules import (iskeyword)

DARK_COLOR = 128


def is_binary_string(byte) -> bool:
    return bool(byte.translate(None, textchars))


def hex2dec(hex_code) -> int:
    hex_code = str(hex_code)
    if hex_code.startswith("#"):
        hex_code = hex_code[1:]
    return int(hex_code, 16)


def dec2hex(dec, color_code: bool = False) -> str:
    dec = hex(dec)
    if color_code:
        dec = "#" + dec[2:]
    return dec


def is_dark_color(hex_code) -> bool:
    if hex_code.startswith("#"):
        hex_code = hex_code[1:]
    if (
            hex2dec(hex_code[:2]) <= DARK_COLOR
            and hex2dec(hex_code[2:4]) <= DARK_COLOR
            and hex2dec(hex_code[4:]) <= DARK_COLOR
    ):
        return True
    return False


def darken_color(hex_code, red, green, blue) -> str:
    hex_code = hex_code[1:]
    rgb = (
        hex2dec(hex_code[:2]) - red,
        hex2dec(hex_code[2:4]) - green,
        hex2dec(hex_code[4:]) - blue,
    )
    value = "#"
    for x in rgb:
        value += dec2hex(x)[2:]
    return value


def lighten_color(hex_code, red, green, blue) -> str:
    hex_code = hex_code[1:]
    rgb = (
        hex2dec(hex_code[:2]) + red,
        hex2dec(hex_code[2:4]) + green,
        hex2dec(hex_code[4:]) + blue,
    )
    value = "#"
    for x in rgb:
        value += dec2hex(x)[2:]
    return value


def is_valid_name(name):
    return name.isidentifier() and not iskeyword(name)


def run_in_terminal(*args, **kwargs):
    # FIXME: Replace with browser embed
    print(args, kwargs)


def open_system_shell(*args, **kwargs):
    # FIXME: Replace with browser embed
    print(args, kwargs)
