from __future__ import annotations

import colorsys
from typing import Literal, Optional

from chroma import utils
from chroma.logger import Logger

logger = Logger.get_logger()

ColorFormat = Literal["hex"] | Literal["hexval"] | Literal["rgb"] | Literal["hsl"]


class Color:
    def __init__(self, color, format: ColorFormat):
        self.color = color
        self.format: ColorFormat = format

    def as_hex(self) -> Color:
        def rgb_to_hexval(r, g, b):
            return f"#{r:02x}{g:02x}{b:02x}"

        if self.format == "hex":
            return self
        elif self.format == "hexval":
            return Color(f"#{self.color}", "hex")
        elif self.format == "rgb":
            rgb = self.color
            return Color(rgb_to_hexval(*rgb), "hex")
        elif self.format == "hsl":
            h, s, l = self.color
            rgb = colorsys.hls_to_rgb(h, l, s)
            return Color(rgb_to_hexval(*rgb), "hex")
        else:
            utils.never()

    def as_hexval(self) -> Color:
        def rgb_to_hexval(r, g, b):
            return f"{r:02x}{g:02x}{b:02x}"

        if self.format == "hex":
            return Color(self.color[1:], "hexval")
        elif self.format == "hexval":
            return self
        elif self.format == "rgb":
            rgb = self.color
            return Color(rgb_to_hexval(*rgb), "hexval")
        elif self.format == "hsl":
            h, s, l = self.color
            rgb = colorsys.hls_to_rgb(h, l, s)
            return Color(rgb_to_hexval(*rgb), "hexval")
        else:
            utils.never()

    def as_rgb(self) -> Color:
        def hexval_to_rgb(hexval):
            return tuple(int(hexval[i : i + 2], 16) / 255.0 for i in (0, 2, 4))

        if self.format == "hex":
            return Color(hexval_to_rgb(self.color[1:]), "rgb")
        elif self.format == "hexval":
            return Color(hexval_to_rgb(self.color), "rgb")
        elif self.format == "rgb":
            return self
        elif self.format == "hsl":
            h, l, s = self.color
            return Color(colorsys.hls_to_rgb(h, l, s), "rgb")
        else:
            utils.never()

    def as_hsl(self) -> Color:
        if self.format == "hex":
            rgb = self.as_rgb().color
            return Color(colorsys.rgb_to_hls(*rgb), "hsl")
        elif self.format == "hexval":
            rgb = self.as_rgb().color
            return Color(colorsys.rgb_to_hls(*rgb), "hsl")
        elif self.format == "rgb":
            return Color(colorsys.rgb_to_hls(*self.color), "hsl")
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
        assert self.format in ["rgb", "hsl"]
        assert all([type(x) == int for x in self.color])
        converted = tuple([col / 255.0 for col in self.color])
        return Color(converted, self.format)

    def normalize(self) -> Color:
        return self.normalized()

    def denormalized(self) -> Color:
        assert self.format in ["rgb", "hsl"]
        assert all([type(x) == float for x in self.color])
        converted = tuple([int(col * 255.0) for col in self.color])
        return Color(converted, self.format)

    def denormalize(self) -> Color:
        return self.denormalized()

    def darkened(self, amount: float) -> Color:
        rgb = self.as_rgb().color
        rgb = tuple([int(col * (1 - amount)) for col in rgb])
        return Color(rgb, "rgb").as_format(self.format)

    def darken(self, amount: float) -> Color:
        return self.darkened(amount)

    def lightened(self, amount: float) -> Color:
        rgb = self.as_rgb().color
        rgb = tuple([int(col + (255 - col) * amount) for col in rgb])
        return Color(rgb, "rgb").as_format(self.format)

    def lighten(self, amount: float) -> Color:
        return self.lightened(amount)

    def blended(self, color: Color) -> Color:
        rgb1 = self.as_rgb().color
        rgb2 = color.as_rgb().color
        r1, g1, b1 = rgb1
        r2, g2, b2 = rgb2
        r3 = int(0.5 * r1 + 0.5 * r2)
        g3 = int(0.5 * g1 + 0.5 * g2)
        b3 = int(0.5 * b1 + 0.5 * b2)
        return Color((r3, g3, b3), "rgb").as_format(color.format)

    def blend(self, color: Color):
        return self.blended(color)

    def saturated(self, amount: float) -> Color:
        rgb = self.as_rgb().normalized()
        h, s, l = rgb.as_hsl().color
        s = amount
        return Color((h, s, l), "hsl").denormalized().as_format(self.format)

    def saturate(self, amount: float) -> Color:
        return self.saturated(amount)
