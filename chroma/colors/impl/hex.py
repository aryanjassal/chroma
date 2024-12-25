from __future__ import annotations

import re
from typing import Type, cast

from chroma.colors.base import Color, T

ColorTypeHex = str

HEX_REGEX = r"^#([A-Fa-f0-9]{6})$"
HEXVAL_REGEX = r"([A-Fa-f0-9]{6})$"


class ColorHex(Color):
    def __init__(self, value: str):
        if re.match(HEXVAL_REGEX, value):
            self.__color = f"#{value}"
        elif re.match(HEX_REGEX, value):
            self.__color = value
        else:
            raise TypeError("Invalid hex color.")

    @property
    def color(self) -> ColorTypeHex:
        return self.__color

    @property
    def value(self) -> ColorTypeHex:
        return self.__color[1:]

    def cast(self, _type: Type[T]) -> T:
        # Delayed imports to avoid circular imports
        from chroma.colors.impl import ColorHSL, ColorRGB

        # We know that the type we are returning is correct, but the linter
        # doesn't. So, we use cast() to tell it that.
        if _type is ColorRGB:
            r = int(self.value[0:2], 16)
            g = int(self.value[2:4], 16)
            b = int(self.value[4:6], 16)
            return cast(T, ColorRGB(r, g, b))
        elif _type is ColorHSL:
            color = self.cast(ColorRGB).cast(ColorHSL)
            return cast(T, color)
        elif _type is ColorHex:
            return cast(T, self)
        else:
            raise TypeError(f"Cannot convert to type {_type}")

    def normalize(self):
        raise NotImplementedError("Cannot normalize ColorHex")

    def normalized(self):
        raise NotImplementedError("Cannot normalize ColorHex")

    def denormalize(self):
        raise NotImplementedError("Cannot normalize ColorHex")

    def denormalized(self):
        raise NotImplementedError("Cannot normalize ColorHex")

    # TEST: Do we really need to do it this way? Why can't the user cast to HSL
    # to access these particular functions? I guess I will keep them here for
    # the time being, but usage is discouraged.

    def darkened(self, amount: float) -> ColorHex:
        """Usage discouraged. Cast to ColorHSL to use these methods."""
        from chroma.colors.impl import ColorHSL

        return self.cast(ColorHSL).darkened(amount).cast(ColorHex)

    def darken(self, amount: float) -> ColorHex:
        """Usage discouraged. Cast to ColorHSL to use these methods."""
        from chroma.colors.impl import ColorHSL

        return self.cast(ColorHSL).darken(amount).cast(ColorHex)

    def lightened(self, amount: float) -> ColorHex:
        """Usage discouraged. Cast to ColorHSL to use these methods."""
        from chroma.colors.impl import ColorHSL

        return self.cast(ColorHSL).lightened(amount).cast(ColorHex)

    def lighten(self, amount: float) -> ColorHex:
        """Usage discouraged. Cast to ColorHSL to use these methods."""
        from chroma.colors.impl import ColorHSL

        return self.cast(ColorHSL).lighten(amount).cast(ColorHex)

    def saturated(self, amount: float) -> ColorHex:
        """Usage discouraged. Cast to ColorHSL to use these methods."""
        from chroma.colors.impl import ColorHSL

        return self.cast(ColorHSL).saturated(amount).cast(ColorHex)

    def saturate(self, amount: float) -> ColorHex:
        """Usage discouraged. Cast to ColorHSL to use these methods."""
        from chroma.colors.impl import ColorHSL

        return self.cast(ColorHSL).saturate(amount).cast(ColorHex)

    def desaturated(self, amount: float) -> ColorHex:
        """Usage discouraged. Cast to ColorHSL to use these methods."""
        from chroma.colors.impl import ColorHSL

        return self.cast(ColorHSL).desaturated(amount).cast(ColorHex)

    def desaturate(self, amount: float) -> ColorHex:
        """Usage discouraged. Cast to ColorHSL to use these methods."""
        from chroma.colors.impl import ColorHSL

        return self.cast(ColorHSL).desaturate(amount).cast(ColorHex)

    def blend(self, color: Color, ratio: float = 0.5) -> ColorHex:
        """Usage discouraged. Cast to ColorHSL to use these methods."""
        from chroma.colors.impl import ColorRGB

        return self.cast(ColorRGB).blend(color, ratio).cast(ColorHex)

    def blended(self, color: Color, ratio: float = 0.5) -> ColorHex:
        """Usage discouraged. Cast to ColorHSL to use these methods."""
        from chroma.colors.impl import ColorRGB

        return self.cast(ColorRGB).blended(color, ratio).cast(ColorHex)

    def __str__(self):
        return self.color.lower()
