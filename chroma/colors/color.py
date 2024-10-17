from typing import Generic, Type, TypeVar

from chroma.colors.impl.hex import ColorHex, ColorTypeHex
from chroma.colors.impl.hsl import ColorHSL, ColorTypeHSL
from chroma.colors.impl.rgb import ColorRGB, ColorTypeRGB

T = TypeVar("T", ColorTypeHex, ColorTypeHSL, ColorTypeRGB)
# VT = TypeVar("VT", )


class Color(Generic[T]):
    def __init__(self, color: Type[T]):
        if type(color) == ColorTypeHex:
            self.color = ColorHex(color)

    @property
    def color(self):
        return self.__color
