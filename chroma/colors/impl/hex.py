from __future__ import annotations

import re
from typing import Type, cast

from chroma.colors.color import T, _ColorImpl
from chroma.colors.impl.hsl import ColorHSL
from chroma.colors.impl.rgb import ColorRGB

ColorTypeHex = str

HEX_REGEX = r"^#([A-Fa-f0-9]{6})$"
HEXVAL_REGEX = r"^[#]?([A-Fa-f0-9]{6})$"


class ColorHex(_ColorImpl):
    def __init__(self, value: str):
        if re.match(HEXVAL_REGEX, value):
            self.__color = f"#{value}"
        elif re.match(HEX_REGEX, value):
            self.__color = value
        raise TypeError("Invalid hex color.")

    @property
    def color(self) -> ColorTypeHex:
        return self.__color

    @property
    def value(self) -> ColorTypeHex:
        return self.__color[1:]

    def cast(self, target_type: Type[T]) -> T:
        # We know that the type we are returning is correct, but the linter
        # doesn't. So, we use cast() to tell it that.
        if target_type == ColorRGB:
            r = int(self.value[0:2], 16)
            g = int(self.value[2:4], 16)
            b = int(self.value[4:6], 16)
            return cast(T, ColorRGB(r, g, b))
        elif target_type == ColorHSL:
            color = self.cast(ColorRGB).cast(ColorHSL)
            return cast(T, color)
        else:
            raise TypeError(f"Cannot convert to type {target_type}")

    def __str__(self):
        return f""
