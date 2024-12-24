from chroma.colors import ColorHex, ColorHSL, ColorRGB
from chroma.colors.utils import check_types


def test_check_types():
    assert check_types([True, False, True], bool)
    assert check_types([0, 50, 99], int)
    assert check_types([0.0, 0.5, 10.0], float)
    assert not check_types([0.0, 0, 10.0], float)
    assert not check_types([0.0, 0, 10.0], int)
    assert not check_types(["0", 0, 10.0], int)
    assert not check_types(["0", 0, 10.0], str)


def test_check_hex_casting():
    color = ColorHex("#000000")

    rgb = color.cast(ColorRGB)
    assert type(rgb) is ColorRGB
    assert rgb.color == (0, 0, 0)
    assert rgb.r == 0
    assert rgb.g == 0
    assert rgb.b == 0

    hsl = color.cast(ColorHSL)
    assert type(hsl) is ColorHSL
    assert hsl.color == (0, 0, 0)
    assert hsl.h == 0
    assert hsl.s == 0
    assert hsl.l == 0


def test_check_rgb_casting():
    color = ColorRGB(0, 0, 0)

    hex = color.cast(ColorHex)
    assert type(hex) is ColorHex
    assert hex.color == "#000000"

    hsl = color.cast(ColorHSL)
    assert type(hsl) is ColorHSL
    assert hsl.color == (0, 0, 0)
    assert hsl.h == 0
    assert hsl.s == 0
    assert hsl.l == 0


def test_check_hsl_casting():
    color = ColorHSL(0, 0, 0)

    hex = color.cast(ColorHex)
    assert type(hex) is ColorHex
    assert hex.color == "#000000"

    rgb = color.cast(ColorRGB)
    assert type(rgb) is ColorRGB
    assert rgb.color == (0, 0, 0)
    assert rgb.r == 0
    assert rgb.g == 0
    assert rgb.b == 0
