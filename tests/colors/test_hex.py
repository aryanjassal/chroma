from chroma.colors import ColorHex
from chroma.colors.base import Color


def test_create_hex_color():
    color = ColorHex("#000000")
    assert type(color) is ColorHex
    assert isinstance(color, Color)
