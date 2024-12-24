from __future__ import annotations

import colorsys
from typing import Type, cast

from chroma.colors.base import Color, T
from chroma.colors.utils import check_types
from chroma.logger import Logger
from chroma.types import Number
from chroma.utils import clamp, never

ColorTypeHSL = tuple[float, float, float] | tuple[int, int, int]

logger = Logger.get_logger()


class ColorHSL(Color):
    def __init__(self, h: Number, s: Number, l: Number):
        if not check_types((h, s, l), int) and not check_types((h, s, l), float):
            raise TypeError("The color components have different types.")
        if (type(h) is float and (max(h, s, l) > 1.0 or min(h, s, l) < 0.0)) or (
            type(h) is int and (h > 360 or max(s, l) > 100 or min(h, s, l) < 0)
        ):
            print(h, s, l)
            raise ValueError("The color components have invalid values.")
        self.__h = h
        self.__s = s
        self.__l = l

    @property
    def h(self) -> Number:
        return self.__h

    @property
    def s(self) -> Number:
        return self.__s

    @property
    def l(self) -> Number:
        return self.__l

    @property
    def color(self) -> ColorTypeHSL:
        return (self.__h, self.__s, self.__l)

    def cast(self, _type: Type[T]) -> T:
        # Delayed imports to avoid circular imports
        from chroma.colors.impl import ColorHex, ColorRGB

        # We know that the type we are returning is correct, but the linter
        # doesn't. So, we use cast() to tell it that.
        if _type is ColorRGB:
            h, s, l = self.normalized().color
            color = ColorRGB(*colorsys.hls_to_rgb(h, l, s))
            return cast(T, color)
        elif _type is ColorHex:
            return cast(T, self.cast(ColorRGB).cast(ColorHex))
        elif _type is ColorHSL:
            return cast(T, ColorHSL(*self.color))
        else:
            raise TypeError(f"Cannot convert to type {_type}")

    def normalized(self) -> ColorHSL:
        if check_types(self.color, int):
            h = self.h / 360.0
            s = self.s / 100.0
            l = self.l / 100.0
            return ColorHSL(h, s, l)
        elif check_types(self.color, float):
            return ColorHSL(*self.color)
        else:
            raise TypeError("The color components have different types.")

    def normalize(self) -> ColorHSL:
        return self.normalized()

    def denormalized(self) -> ColorHSL:
        if check_types(self.color, float):
            h = int(self.h * 360)
            s = int(self.s * 100)
            l = int(self.l * 100)
            return ColorHSL(h, s, l)
        elif check_types(self.color, int):
            return ColorHSL(*self.color)
        else:
            raise TypeError("The color components have different types.")

    def denormalize(self) -> ColorHSL:
        return self.denormalized()

    def darkened(self, amount: float) -> ColorHSL:
        h, s, l = self.normalized().color
        l = clamp(l - amount, 0.0, 1.0)
        return ColorHSL(h, s, l)

    def darken(self, amount: float) -> ColorHSL:
        return self.darkened(amount)

    def lightened(self, amount: float) -> ColorHSL:
        h, s, l = self.normalized().color
        l = clamp(l + amount, 0.0, 1.0)
        return ColorHSL(h, s, l)

    def lighten(self, amount: float) -> ColorHSL:
        return self.lightened(amount)

    def saturated(self, amount: float) -> ColorHSL:
        h, s, l = self.normalized().color
        s = clamp(s + amount, 0.0, 1.0)
        return ColorHSL(h, s, l)

    def saturate(self, amount: float) -> ColorHSL:
        return self.saturated(amount)

    def desaturated(self, amount: float) -> ColorHSL:
        h, s, l = self.normalized().color
        s = clamp(s - amount, 0.0, 1.0)
        return ColorHSL(h, s, l)

    def desaturate(self, amount: float) -> ColorHSL:
        return self.desaturated(amount)

    def blended(self, color: Color, ratio: float = 0.5) -> ColorHSL:
        from chroma.colors.impl import ColorRGB

        return self.cast(ColorRGB).blend(color, ratio).cast(ColorHSL)

    def blend(self, color: Color, ratio: float = 0.5) -> ColorHSL:
        return self.blended(color, ratio)

    def set_h(self, h: Number) -> ColorHSL:
        is_normal = self.color == self.normalized().color

        if is_normal:
            if type(h) is float:
                self.__h = clamp(h, 0.0, 1.0)
                return self
            elif type(h) is int:
                self.__h = clamp(h / 360.0, 0.0, 1.0)
            never()
        else:
            if type(h) is float:
                self.__h = clamp(h * 360, 0, 360)
                return self
            elif type(h) is int:
                self.__h = clamp(h, 0, 360)
            never()

    def set_s(self, s: Number) -> ColorHSL:
        is_normal = self.color == self.normalized().color

        if is_normal:
            if type(s) is float:
                self.__s = clamp(s, 0.0, 1.0)
                return self
            elif type(s) is int:
                self.__s = clamp(s / 360.0, 0.0, 1.0)
            never()
        else:
            if type(s) is float:
                self.__s = clamp(s * 360, 0, 360)
                return self
            elif type(s) is int:
                self.__s = clamp(s, 0, 360)
            never()

    def set_l(self, l: Number) -> ColorHSL:
        is_normal = self.color == self.normalized().color

        if is_normal:
            if type(l) is float:
                self.__l = clamp(l, 0.0, 1.0)
                return self
            elif type(l) is int:
                self.__l = clamp(l / 360.0, 0.0, 1.0)
            never()
        else:
            if type(l) is float:
                self.__l = clamp(l * 360, 0, 360)
                return self
            elif type(l) is int:
                self.__l = clamp(l, 0, 360)
            never()

    def __str__(self):
        from chroma.colors.impl import ColorHex

        logger.warn(f"{self.__class__.__name__}: __str__ is only supported by ColorHex.")
        logger.warn("Defaulting to __str__ of ColorHex")
        return self.cast(ColorHex).__str__()
