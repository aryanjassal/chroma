from __future__ import annotations

import colorsys
from typing import Type, cast

from chroma.colors.base import Color, T
from chroma.colors.utils import check_types
from chroma.types import Number
from chroma.utils import clamp, never

ColorTypeHSL = tuple[float, float, float] | tuple[int, int, int]


class ColorHSL(Color):
    def __init__(self, h: Number, s: Number, l: Number):
        if not check_types((h, s, l), int) and not check_types((h, s, l), float):
            raise TypeError("The color components have different types.")
        if (type(h) == float and (max(h, s, l) > 1.0 or min(h, s, l) < 0.0)) or (
            type(h) == int and (max(h, s, l) > 255 or min(h, s, l) < 0)
        ):
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
        if _type == ColorRGB:
            h, s, l = self.color
            color = ColorRGB(*colorsys.hls_to_rgb(h, l, s))
            return cast(T, color)
        elif _type == ColorHex:
            return cast(T, self.cast(ColorRGB).cast(ColorHex))
        elif _type == ColorHSL:
            return cast(T, ColorHSL(*self.color))
        else:
            raise TypeError(f"Cannot convert to type {_type}")

    def __update(self, h: Number, s: Number, l: Number):
        if not check_types((h, s, l), int) and not check_types((h, s, l), float):
            raise TypeError("The color components have different types.")
        self.__h = h
        self.__s = s
        self.__l = l
        return self

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
        self.__update(*self.normalized().color)
        return self

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
        self.__update(*self.denormalized().color)
        return self

    def darkened(self, amount: float) -> ColorHSL:
        h, s, l = self.normalized().color
        l = clamp(l - amount, 0.0, 1.0)
        return ColorHSL(h, s, l)

    def darken(self, amount: float) -> ColorHSL:
        self.__update(*self.darkened(amount).color)
        return self

    def lightened(self, amount: float) -> ColorHSL:
        h, s, l = self.normalized().color
        l = clamp(l + amount, 0.0, 1.0)
        return ColorHSL(h, s, l)

    def lighten(self, amount: float) -> ColorHSL:
        self.__update(*self.lightened(amount).color)
        return self

    def saturated(self, amount: float) -> ColorHSL:
        h, s, l = self.normalized().color
        s = clamp(s + amount, 0.0, 1.0)
        return ColorHSL(h, s, l)

    def saturate(self, amount: float) -> ColorHSL:
        self.__update(*self.saturated(amount).color)
        return self

    def desaturated(self, amount: float) -> ColorHSL:
        h, s, l = self.normalized().color
        s = clamp(s - amount, 0.0, 1.0)
        return ColorHSL(h, s, l)

    def desaturate(self, amount: float) -> ColorHSL:
        self.__update(*self.desaturated(amount).color)
        return self

    def blended(self, color: Color, ratio: float = 0.5) -> ColorHSL:
        from chroma.colors.impl import ColorRGB

        return self.cast(ColorRGB).blend(color, ratio).cast(ColorHSL)

    def blend(self, color: Color, ratio: float = 0.5) -> ColorHSL:
        self.__update(*self.blended(color, ratio).color)
        return self

    def set_h(self, h: Number) -> ColorHSL:
        is_normal = self.color == self.normalized().color

        if is_normal:
            if type(h) == float:
                self.__h = clamp(h, 0.0, 1.0)
                return self
            elif type(h) == int:
                self.__h = clamp(h / 360.0, 0.0, 1.0)
            never()
        else:
            if type(h) == float:
                self.__h = clamp(h * 360, 0, 360)
                return self
            elif type(h) == int:
                self.__h = clamp(h, 0, 360)
            never()

    def set_s(self, s: Number) -> ColorHSL:
        is_normal = self.color == self.normalized().color

        if is_normal:
            if type(s) == float:
                self.__s = clamp(s, 0.0, 1.0)
                return self
            elif type(s) == int:
                self.__s = clamp(s / 360.0, 0.0, 1.0)
            never()
        else:
            if type(s) == float:
                self.__s = clamp(s * 360, 0, 360)
                return self
            elif type(s) == int:
                self.__s = clamp(s, 0, 360)
            never()

    def set_l(self, l: Number) -> ColorHSL:
        is_normal = self.color == self.normalized().color

        if is_normal:
            if type(l) == float:
                self.__l = clamp(l, 0.0, 1.0)
                return self
            elif type(l) == int:
                self.__l = clamp(l / 360.0, 0.0, 1.0)
            never()
        else:
            if type(l) == float:
                self.__l = clamp(l * 360, 0, 360)
                return self
            elif type(l) == int:
                self.__l = clamp(l, 0, 360)
            never()

    def __str__(self):
        return f"hsl({self.h}, {self.s}, {self.l})"
