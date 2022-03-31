"""Provides convenient color utilities"""

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
    if hex_code.startswith("#"):
        hex_code = hex_code[1:]
    if (
            hex2dec(hex_code[:2]) <= DARK_COLOR
            and hex2dec(hex_code[2:4]) <= DARK_COLOR
            and hex2dec(hex_code[4:]) <= DARK_COLOR
    ):
        return True
    return False


def darken_color(hex_code, decrement) -> str:
    hex_code = hex_code[1:]
    rgb = (
        hex2dec(hex_code[:2]) - decrement,
        hex2dec(hex_code[2:4]) - decrement,
        hex2dec(hex_code[4:]) - decrement,
    )
    value = "#"
    for x in rgb:
        value += dec2hex(x)[2:]
    return value


def lighten_color(hex_code, increment) -> str:
    hex_code = hex_code[1:]
    rgb = (
        hex2dec(hex_code[:2]) + increment,
        hex2dec(hex_code[2:4]) + increment,
        hex2dec(hex_code[4:]) + increment,
    )
    value = "#"
    for x in rgb:
        value += dec2hex(x)[2:]
    return value
