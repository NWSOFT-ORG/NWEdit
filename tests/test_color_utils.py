from src.Utils.color_utils import (darken_color, dec2hex, get_hex, hex2dec,
                                   is_dark_color, lighten_color)


def test_hex2dec():
    color = "#FF"
    rgb_color = hex2dec(color)

    assert rgb_color
    assert rgb_color == 255


def test_dec2hex():
    color = 255

    hex_color = dec2hex(color, True)[1:]
    hex_color_no_code = dec2hex(color)

    assert len(hex_color) == 2
    assert len(hex_color_no_code) == 4


def test_is_dark_color():
    assert is_dark_color("black")
    assert not is_dark_color("white")

    assert is_dark_color("#000000")
    assert not is_dark_color("#FFFFFF")


def test_darken_color():
    color = "white"
    black = darken_color(color, 255)

    white_hex = get_hex(color)
    white = ""
    for item in white_hex:
        white += item[2:]

    white = int(white, 16)
    assert black
    assert white
    black = hex2dec(black)
    assert black < white


def test_lighten_color():
    color = "black"
    white = lighten_color(color, 255)

    black_hex = get_hex(color)
    black = ""
    for item in black_hex:
        black += item[2:]

    black = int(black, 16)
    assert white
    assert black == 0
    white = hex2dec(white)
    assert black < white
