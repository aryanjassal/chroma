from chroma.colors import ColorHex
from chroma.colors.base import _ColorImpl


def test_create_hex_color():
    color = ColorHex("#000000")
    assert type(color) == ColorHex
    assert isinstance(color, _ColorImpl)
