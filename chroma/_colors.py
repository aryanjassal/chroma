from __future__ import annotations

import colorsys
import re
from typing import Literal, Optional, cast, overload

from chroma import utils
from chroma.logger import Logger
from chroma.types import ColorFormat, ColorTuple, ColorType, Number

logger = Logger.get_logger()

HEX_REGEX = r"^#([A-Fa-f0-9]{6})$"
HEXVAL_REGEX = r"^([A-Fa-f0-9]{6})$"


class Color:
    def __init__(self, color: ColorType, format: Optional[ColorFormat]):
        def _infer_type(col: ColorType) -> ColorFormat:
            if type(col) == str:
                if re.match(HEX_REGEX, col):
                    return "hex"
                if re.match(HEXVAL_REGEX, col):
                    return "hexval"
            logger.fatal(f"Could not infer type of color {col}")

        if format is None:
            self.__format = _infer_type(color)
        else:
            if format in ["hex", "hexval"]:
                assert type(color) == str, f"Expected type str, got {type(color)}"
                assert (
                    re.match(HEX_REGEX, color) is not None
                    and re.match(HEXVAL_REGEX, color) is not None
                ), f"Color is not in the correct format"

            elif format in ["rgb", "hsl"]:
                assert type(color) == tuple, f"Expected type tuple, got {type(color)}"
                assert len(color) == 3, f"Expected len 3, got {type(color)}"
                for c in color:
                    assert type(c) == Number, f"Expected type number, got {type(c)}"

            else:
                logger.fatal(f"Invalid format {format}")

            self.__format: ColorFormat = format

        self.__color = color

    @property
    def color(self) -> ColorType:
        return self.__color

    @property
    def format(self) -> ColorFormat:
        return self.__format

    def as_hex(self) -> Color:
        def rgb_to_hexval(r, g, b):
            return f"#{r:02x}{g:02x}{b:02x}"

        # Nice to be explicit with types in the actual library code
        if self.format == "hex":
            return self
        elif self.format == "hexval":
            return Color(f"#{self.color}", "hex")
        elif self.format == "rgb":
            rgb = self.denormalized().color
            return Color(rgb_to_hexval(*rgb), "hex")
        elif self.format == "hsl":
            h, s, l = cast(ColorTuple, self.color)
            rgb = colorsys.hls_to_rgb(h, l, s)
            rgb = Color(rgb, "rgb").denormalized().color
            return Color(rgb_to_hexval(*rgb), "hex")
        else:
            utils.never()

    def as_hexval(self) -> Color:
        def rgb_to_hexval(r, g, b):
            return f"{r:02x}{g:02x}{b:02x}"

        if self.format == "hex":
            return Color(cast(str, self.color[1:]), "hexval")
        elif self.format == "hexval":
            return self
        elif self.format == "rgb":
            rgb = self.denormalized().color
            return Color(rgb_to_hexval(*rgb), "hexval")
        elif self.format == "hsl":
            h, s, l = cast(ColorTuple, self.color)
            rgb = colorsys.hls_to_rgb(h, l, s)
            rgb = Color(rgb, "rgb").denormalized()
            return Color(rgb_to_hexval(*rgb.color), "hexval")
        else:
            utils.never()

    def as_rgb(self) -> Color:
        def hexval_to_rgb(hexval):
            vals = [int(hexval[i : i + 2], 16) / 255.0 for i in (0, 2, 4)]
            return (vals[0], vals[1], vals[2])

        if self.format == "hex":
            return Color(hexval_to_rgb(self.color[1:]), "rgb")
        elif self.format == "hexval":
            return Color(hexval_to_rgb(self.color), "rgb")
        elif self.format == "rgb":
            return self
        elif self.format == "hsl":
            h, l, s = cast(ColorTuple, self.color)
            return Color(colorsys.hls_to_rgb(h, l, s), "rgb")
        else:
            utils.never()

    def as_hsl(self) -> Color:
        if self.format == "hex":
            rgb = cast(ColorTuple, self.as_rgb().color)
            h, l, s = colorsys.rgb_to_hls(*rgb)
            return Color((h, s, l), "hsl")
        elif self.format == "hexval":
            rgb = cast(ColorTuple, self.as_rgb().color)
            h, l, s = colorsys.rgb_to_hls(*rgb)
            return Color((h, s, l), "hsl")
        elif self.format == "rgb":
            h, l, s = colorsys.rgb_to_hls(*cast(ColorTuple, self.color))
            return Color((h, s, l), "hsl")
        elif self.format == "hsl":
            return self
        else:
            utils.never()

    def as_format(self, format: ColorFormat) -> Color:
        if format == "hex":
            return self.as_hex()
        elif format == "hexval":
            return self.as_hexval()
        elif format == "rgb":
            return self.as_rgb()
        elif format == "hsl":
            return self.as_hsl()

    def normalized(self) -> Color:
        assert self.format in ["rgb"]
        if all([type(x) == int for x in self.color]):
            converted = tuple([col / 255.0 for col in cast(ColorTuple, self.color)])
            return Color(cast(ColorTuple, converted), self.format)
        elif all([type(x) == float for x in self.color]):
            return self
        else:
            color = self.color
            raise ValueError(
                "Colors are malformed and don't have the same type. "
                f"{type(color[0])}, {type(color[1])}, {type(color[2])}"
            )

    def normalize(self) -> None:
        self.__color = self.denormalized().color

    def denormalized(self) -> Color:
        assert self.format in ["rgb"]
        if all([type(x) == float for x in self.color]):
            converted = tuple([int(col * 255.0) for col in cast(ColorTuple, self.color)])
            return Color(cast(ColorTuple, converted), self.format)
        elif all([type(x) == int for x in self.color]):
            return self
        else:
            color = self.color
            raise ValueError(
                "Colors are malformed and don't have the same type. "
                f"{type(color[0])}, {type(color[1])}, {type(color[2])}"
            )

    def denormalize(self) -> None:
        self.__color = self.denormalized().color

    def darkened(self, amount: float, absolute: bool = False) -> Color:
        h, s, l = cast(ColorTuple, self.as_hsl().color)
        if absolute:
            l = amount
        else:
            l -= amount
        l = utils.clamp(l, 0, 1)
        return Color((h, s, l), "hsl").as_format(self.format)

    def darken(self, amount: float, absolute: bool = False) -> None:
        self.__color = self.darkened(amount, absolute).color

    def lightened(self, amount: float, absolute: bool = False) -> Color:
        h, s, l = cast(ColorTuple, self.as_hsl().color)
        if absolute:
            l = amount
        else:
            l += amount
        l = utils.clamp(l, 0, 1)
        return Color((h, s, l), "hsl").as_format(self.format)

    def lighten(self, amount: float, absolute: bool = False) -> None:
        self.__color = self.lightened(amount, absolute).color

    def blended(self, color: Color, ratio: float = 0.5) -> Color:
        rgb1 = cast(ColorTuple, self.as_rgb().color)
        rgb2 = cast(ColorTuple, color.as_rgb().color)
        r1, g1, b1 = rgb1
        r2, g2, b2 = rgb2
        a1 = 1 - ratio
        a2 = ratio
        r3 = a1 * r1 + a2 * r2
        g3 = a1 * g1 + a2 * g2
        b3 = a1 * b1 + a2 * b2
        return Color((r3, g3, b3), "rgb").as_format(color.format)

    def blend(self, color: Color, ratio: float = 0.5) -> None:
        self.__color = self.blended(color, ratio).color

    def saturated(self, amount: float, absolute: bool = False) -> Color:
        h, s, l = cast(ColorTuple, self.as_hsl().color)
        if absolute:
            s = amount
        else:
            s += amount
        s = utils.clamp(s, 0, 1)
        return Color((h, s, l), "hsl").as_format(self.format)

    def saturate(self, amount: float, absolute: bool = False) -> None:
        self.__color = self.saturated(amount, absolute).color

    def __str__(self):
        if self.format in ["hex", "hexval"]:
            return cast(str, self.color).lower()
        elif self.format == "rgb":
            r, g, b = self.denormalized().color
            return f"rgb({r}, {g}, {b})"
        elif self.format == "hsl":
            h, s, l = self.color
            return f"hsl({h}, {s}, {l})"
        utils.never()
