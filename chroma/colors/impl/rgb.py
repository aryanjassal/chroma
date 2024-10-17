from __future__ import annotations

import colorsys
from typing import Type, cast

from chroma.colors.base import Color, T
from chroma.colors.utils import check_types
from chroma.types import Number
from chroma.utils import clamp, never

ColorTypeRGB = tuple[float, float, float] | tuple[int, int, int]


class ColorRGB(Color):
    def __init__(self, r: Number, g: Number, b: Number):
        if not check_types((r, g, b), int) and not check_types((r, g, b), float):
            raise TypeError("The color components have different types.")
        if (type(r) == float and (max(r, g, b) > 1.0 or min(r, g, b) < 0.0)) or (
            type(r) == int and (max(r, g, b) > 255 or min(r, g, b) < 0)
        ):
            raise ValueError("The color components have invalid values.")
        self.__r = r
        self.__g = g
        self.__b = b

    @property
    def r(self) -> Number:
        return self.__r

    @property
    def g(self) -> Number:
        return self.__g

    @property
    def b(self) -> Number:
        return self.__b

    @property
    def color(self) -> ColorTypeRGB:
        return (self.__r, self.__g, self.__b)

    def cast(self, target_type: Type[T]) -> T:
        # Delayed imports to avoid circular imports
        from chroma.colors.impl import ColorHex, ColorHSL

        # We know that the type we are returning is correct, but the linter
        # doesn't. So, we use cast() to tell it that.
        if target_type == ColorHSL:
            h, l, s = colorsys.rgb_to_hls(*self.color)
            return cast(T, ColorHSL(h, s, l))
        elif target_type == ColorHex:
            color = f"{self.r:02x}{self.g:02x}{self.b:02x}"
            return cast(T, ColorHex(color))
        elif target_type == ColorRGB:
            return cast(T, self)
        else:
            raise TypeError(f"Cannot convert to type {target_type}")

    def __update(self, r: Number, g: Number, b: Number):
        if not check_types((r, g, b), int) and not check_types((r, g, b), float):
            raise TypeError("The color components have different types.")
        self.__r = r
        self.__g = g
        self.__b = b
        return self

    def blended(self, color: Color, ratio: float = 0.5) -> ColorRGB:
        r1, g1, b1 = self.color
        r2, g2, b2 = color.cast(ColorRGB).color
        a1 = 1 - ratio
        a2 = ratio
        r3 = a1 * r1 + a2 * r2
        g3 = a1 * g1 + a2 * g2
        b3 = a1 * b1 + a2 * b2
        return ColorRGB(r3, g3, b3)

    def blend(self, color: Color, ratio: float = 0.5) -> ColorRGB:
        self.__update(*self.blended(color, ratio).color)
        return self

    def normalized(self) -> ColorRGB:
        if check_types(self.color, int):
            r = self.r / 255.0
            g = self.g / 255.0
            b = self.b / 255.0
            return ColorRGB(r, g, b)
        elif check_types(self.color, float):
            return ColorRGB(*self.color)
        else:
            raise TypeError(f"The color components have different types {self.color}")

    def normalize(self) -> ColorRGB:
        self.__update(*self.normalized().color)
        return self

    def denormalized(self) -> ColorRGB:
        if check_types(self.color, float):
            r = int(self.r * 255.0)
            g = int(self.g * 255.0)
            b = int(self.b * 255.0)
            return ColorRGB(r, g, b)
        elif check_types(self.color, int):
            return ColorRGB(*self.color)
        else:
            raise TypeError(f"The color components have different types {self.color}")

    def denormalize(self) -> ColorRGB:
        self.__update(*self.denormalized().color)
        return self

    def set_r(self, r: Number) -> ColorRGB:
        is_normal = self.color == self.normalized().color

        if is_normal:
            if type(r) == float:
                self.__r = clamp(r, 0.0, 1.0)
                return self
            elif type(r) == int:
                self.__r = clamp(r / 360.0, 0.0, 1.0)
            never()
        else:
            if type(r) == float:
                self.__r = clamp(r * 360, 0, 360)
                return self
            elif type(r) == int:
                self.__r = clamp(r, 0, 360)
            never()

    def set_g(self, g: Number) -> ColorRGB:
        ig_normal = self.color == self.normalized().color

        if ig_normal:
            if type(g) == float:
                self.__g = clamp(g, 0.0, 1.0)
                return self
            elif type(g) == int:
                self.__g = clamp(g / 360.0, 0.0, 1.0)
            never()
        else:
            if type(g) == float:
                self.__g = clamp(g * 360, 0, 360)
                return self
            elif type(g) == int:
                self.__g = clamp(g, 0, 360)
            never()

    def set_b(self, b: Number) -> ColorRGB:
        is_normal = self.color == self.normalized().color

        if is_normal:
            if type(b) == float:
                self.__b = clamp(b, 0.0, 1.0)
                return self
            elif type(b) == int:
                self.__b = clamp(b / 360.0, 0.0, 1.0)
            never()
        else:
            if type(b) == float:
                self.__b = clamp(b * 360, 0, 360)
                return self
            elif type(b) == int:
                self.__b = clamp(b, 0, 360)
            never()

    # TEST: Do we really need to do it this way? Why can't the user cast to HSL
    # to access these particular functions? I guess I will keep them here for
    # the time being, but usage is discouraged.

    def darkened(self, amount: float) -> ColorRGB:
        """Usage discouraged. Cast to ColorHSL to use these methods."""
        from chroma.colors.impl import ColorHSL

        return self.cast(ColorHSL).darkened(amount).cast(ColorRGB)

    def darken(self, amount: float) -> ColorRGB:
        """Usage discouraged. Cast to ColorHSL to use these methods."""
        from chroma.colors.impl import ColorHSL

        return self.cast(ColorHSL).darken(amount).cast(ColorRGB)

    def lightened(self, amount: float) -> ColorRGB:
        """Usage discouraged. Cast to ColorHSL to use these methods."""
        from chroma.colors.impl import ColorHSL

        return self.cast(ColorHSL).lightened(amount).cast(ColorRGB)

    def lighten(self, amount: float) -> ColorRGB:
        """Usage discouraged. Cast to ColorHSL to use these methods."""
        from chroma.colors.impl import ColorHSL

        return self.cast(ColorHSL).lighten(amount).cast(ColorRGB)

    def saturated(self, amount: float) -> ColorRGB:
        """Usage discouraged. Cast to ColorHSL to use these methods."""
        from chroma.colors.impl import ColorHSL

        return self.cast(ColorHSL).saturated(amount).cast(ColorRGB)

    def saturate(self, amount: float) -> ColorRGB:
        """Usage discouraged. Cast to ColorHSL to use these methods."""
        from chroma.colors.impl import ColorHSL

        return self.cast(ColorHSL).saturate(amount).cast(ColorRGB)

    def desaturated(self, amount: float) -> ColorRGB:
        """Usage discouraged. Cast to ColorHSL to use these methods."""
        from chroma.colors.impl import ColorHSL

        return self.cast(ColorHSL).desaturated(amount).cast(ColorRGB)

    def desaturate(self, amount: float) -> ColorRGB:
        """Usage discouraged. Cast to ColorHSL to use these methods."""
        from chroma.colors.impl import ColorHSL

        return self.cast(ColorHSL).desaturate(amount).cast(ColorRGB)

    def __str__(self):
        return f"hsl({self.r}, {self.g}, {self.b})"
