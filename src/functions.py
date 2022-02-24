"""Useful functions"""

from src.constants import textchars
from src.modules import (iskeyword)
import webview

DARK_COLOR: int = 128


def is_binary_string(byte: bytes) -> bool:
    """Check if the byte is binary: No decodable in any encodings (Supported in Python)"""
    return bool(byte.translate(None, textchars))


def hex2dec(hex_code: str) -> int:
    """Returns a decimal integer from a hex integer
       Usage:
       - hex2dec('#c')  => 12
       - hex2dec('c')   => '#c'
    """
    hex_code = str(hex_code)
    if hex_code.startswith("#"):
        hex_code = hex_code[1:]  # Remove the '#', else won't parse properly
    return int(hex_code, 16)  # Return the decimal


def dec2hex(dec, color_code: bool = False) -> str:
    """Converts a decimal to a hex code.
       Usage:
       - dec2hex(12)       => '0xc'
       - dec2hex(12, True) => '#c'
    """
    dec = hex(dec)
    if color_code:
        dec = "#" + dec[2:]  # Convert to color code if needed
    return dec


def is_dark_color(hex_code: str) -> bool:
    """Is this a dark color?
       Note: Hex color structure
       #     00 00 00
       ^     ^  ^  ^
       |     |  |  |
       Hash  R  G  B
       If R, G and B are larger than the 128 index, it should look dark
    """
    if hex_code.startswith("#"):
        hex_code = hex_code[1:]
    return bool(
        hex2dec(hex_code[:2]) <= DARK_COLOR
        and hex2dec(hex_code[2:4]) <= DARK_COLOR
        and hex2dec(hex_code[4:]) <= DARK_COLOR
    )


def darken_color(hex_code: str, red: int, green: int, blue: int) -> str:
    """Makes color darker, by *decreasing* RGB value"""
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


def lighten_color(hex_code: str, red: int, green: int, blue: int) -> str:
    """Makes color darker, by *increasing* RGB value"""
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


def is_valid_name(name: str):
    """Checks if the name is valid (not a keyword)"""
    return name.isidentifier() and not iskeyword(name)


def open_system_shell():
    webview.create_window("Terminal", "http://localhost:1234")
    webview.start()
