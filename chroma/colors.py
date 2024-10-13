from __future__ import annotations

import colorsys
from typing import Literal

from chroma import utils
from chroma.logger import Logger

logger = Logger.get_logger()

ColorFormat = Literal["hex"] | Literal["hexval"] | Literal["rgb"] | Literal["hsl"]


class Color:
    def __init__(self, color, format: ColorFormat):
        # if format in ["hex", "hexval"]:
        #     assert type(color) == str, f"Expected type str, got {type(color)}"
        # elif format in ["rgb", "hsl"]:
        #     assert type(color) == tuple, f"Expected type tuple, got {type(color)}"
        #     assert len(color) == 3, f"Expected len 3, got {type(color)}"
        #     assert type(color[0]) == float | int, f"Expected type float or int, got {type(color)}"
        #     assert type(color[1]) == float | int, f"Expected type float or int, got {type(color)}"
        #     assert type(color[2]) == float | int, f"Expected type float or int, got {type(color)}"
        # else:
        #     logger.error("Unsupported type")

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
            rgb = self.denormalized().color
            return Color(rgb_to_hexval(*rgb), "hex")
        elif self.format == "hsl":
            h, s, l = self.color
            rgb = colorsys.hls_to_rgb(h, l, s)
            rgb = Color(rgb, "rgb").denormalized()
            return Color(rgb_to_hexval(*rgb.color), "hex")
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
            rgb = self.denormalized().color
            return Color(rgb_to_hexval(*rgb), "hexval")
        elif self.format == "hsl":
            h, s, l = self.color
            rgb = colorsys.hls_to_rgb(h, l, s)
            rgb = Color(rgb, "rgb").denormalized()
            return Color(rgb_to_hexval(*rgb.color), "hexval")
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
            h, l, s = colorsys.rgb_to_hls(*rgb)
            return Color((h, s, l), "hsl")
        elif self.format == "hexval":
            rgb = self.as_rgb().color
            h, l, s = colorsys.rgb_to_hls(*rgb)
            return Color((h, s, l), "hsl")
        elif self.format == "rgb":
            h, l, s = colorsys.rgb_to_hls(*self.color)
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
            converted = tuple([col / 255.0 for col in self.color])
            return Color(converted, self.format)
        elif all([type(x) == float for x in self.color]):
            return self
        else:
            color = self.color
            logger.error("Colors are malformed and don't have the same type.")
            logger.fatal(f"{type(color[0])}, {type(color[1])}, {type(color[2])}")

    def normalize(self) -> Color:
        return self.normalized()

    def denormalized(self) -> Color:
        assert self.format in ["rgb"]
        if all([type(x) == float for x in self.color]):
            converted = tuple([int(col * 255.0) for col in self.color])
            return Color(converted, self.format)
        elif all([type(x) == int for x in self.color]):
            return self
        else:
            color = self.color
            logger.error("Colors are malformed and don't have the same type.")
            logger.fatal(f"{type(color[0])}, {type(color[1])}, {type(color[2])}")

    def denormalize(self) -> Color:
        return self.denormalized()

    def darkened(self, amount: float) -> Color:
        h, s, l = self.as_hsl().color
        l = max(0, l - amount)
        return Color((h, s, l), "hsl").as_format(self.format)

    def darken(self, amount: float) -> Color:
        return self.darkened(amount)

    def lightened(self, amount: float) -> Color:
        h, s, l = self.as_hsl().color
        l = min(1, l + amount)
        return Color((h, s, l), "hsl").as_format(self.format)

    def lighten(self, amount: float) -> Color:
        return self.lightened(amount)

    def blended(self, color: Color, ratio: float = 0.5) -> Color:
        rgb1 = self.as_rgb().color
        rgb2 = color.as_rgb().color
        r1, g1, b1 = rgb1
        r2, g2, b2 = rgb2
        a1 = 1 - ratio
        a2 = ratio
        r3 = a1 * r1 + a2 * r2
        g3 = a1 * g1 + a2 * g2
        b3 = a1 * b1 + a2 * b2
        return Color((r3, g3, b3), "rgb").as_format(color.format)

    def blend(self, color: Color, ratio: float = 0.5):
        return self.blended(color, ratio)

    def saturated(self, amount: float) -> Color:
        h, s, l = self.as_hsl().color
        s = min(1, s + amount)
        return Color((h, s, l), "hsl").as_format(self.format)

    def saturate(self, amount: float) -> Color:
        return self.saturated(amount)

    def __str__(self):
        if self.format in ["hex", "hexval"]:
            return self.color
        else:
            logger.fatal(
                f"The color format {self.format} isn't supported for "
                "stringification yet."
            )
