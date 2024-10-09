from __future__ import annotations

import colorsys

from chroma.logger import Logger

logger = Logger.get_logger()

# TODO: instead of Color.to("fmt") just do Color.to_fmt() to give pyright an
# easier time.

class Color:
    def __init__(self, color, format: str):
        assert format in ["hex", "hexval", "rgb", "hls"]

        self.color = color
        self.format: str = format

    def __to_hex(self) -> str:
        if self.format == "hex":
            return self.color
        elif self.format == "hexval":
            return f"#{self.color}"
        elif self.format == "rgb":
            r, g, b = self.color
            return f"#{r:02x}{g:02x}{b:02x}"
        elif self.format == "hls":
            h, l, s = self.color
            r, g, b = colorsys.hls_to_rgb(h, l, s)
            return f"#{r:02x}{g:02x}{b:02x}"
        else:
            logger.fatal("Invalid color format")

    def __to_hexval(self) -> str:
        if self.format == "hex":
            return self.color[1:]
        elif self.format == "hexval":
            return self.color
        elif self.format == "rgb":
            r, g, b = self.color
            return f"{r:02x}{g:02x}{b:02x}"
        elif self.format == "hls":
            h, l, s = self.color
            r, g, b = colorsys.hls_to_rgb(h, l, s)
            return f"{r:02x}{g:02x}{b:02x}"
        else:
            logger.fatal("Invalid color format")

    def __to_rgb(self) -> tuple:
        def hexval_to_rgb(hexval):
            return tuple(int(hexval[i : i + 2], 16) / 255.0 for i in (0, 2, 4))

        if self.format == "hex":
            return hexval_to_rgb(self.color[1:])
        elif self.format == "hexval":
            return hexval_to_rgb(self.color)
        elif self.format == "rgb":
            return self.color
        elif self.format == "hls":
            h, l, s = self.color
            return colorsys.hls_to_rgb(h, l, s)
        else:
            logger.fatal("Invalid color format")

    def __to_hls(self) -> tuple:
        if self.format == "hex":
            r, g, b = self.__to_rgb()
            return colorsys.rgb_to_hls(r, g, b)
        elif self.format == "hexval":
            r, g, b = self.__to_rgb()
            return colorsys.rgb_to_hls(r, g, b)
        elif self.format == "rgb":
            return colorsys.rgb_to_hls(*self.color)
        elif self.format == "hls":
            return self.color
        else:
            logger.fatal("Invalid color format")

    def to(self, format: str) -> str | tuple:
        assert format in ["hex", "hexval", "rgb", "hls", "hsv"]

        if format == "hex":
            return self.__to_hex()
        elif format == "hexval":
            return self.__to_hexval()
        elif format == "rgb":
            return self.__to_rgb()
        elif format == "hls":
            return self.__to_hls()
        else:
            logger.fatal("Should never reach here")

    # NOTE: This could be redundant.
    def convert(self, format: str) -> Color:
        assert format in ["hex", "hexval", "rgb", "hls"]

        if format == "hex":
            return Color(self.__to_hex(), "hex")
        elif format == "hexval":
            return Color(self.__to_hexval(), "hexval")
        elif format == "rgb":
            return Color(self.__to_rgb(), "rgb")
        elif format == "hls":
            return Color(self.__to_hls(), "hls")
        else:
            logger.fatal("Should never reach here")

    def normalize(self) -> tuple:
        assert self.format in ["rgb", "hls"]
        return tuple([col / 255.0 for col in self.color])

    def normalized(self) -> Color:
        return Color(self.normalize(), self.format)

    def denormalize(self) -> tuple:
        assert self.format in ["rgb", "hls"]
        return tuple([int(col * 255.0) for col in self.color])

    def denormalized(self) -> Color:
        return Color(self.denormalize(), self.format)

    def darken(self, amount: float):
        rgb: tuple = self.to("rgb")  # pyright: ignore
        rgb = tuple([int(col * (1 - amount)) for col in rgb])
        return Color(rgb, "rgb").to(self.format)

    def darkened(self, amount: float) -> Color:
        return Color(self.darken(amount), self.format)

    def lighten(self, amount: float):
        rgb: tuple = self.to("rgb")  # pyright: ignore
        rgb = tuple([int(col + (255 - col) * amount) for col in rgb])
        return Color(rgb, "rgb").to(self.format)

    def lightened(self, amount: float) -> Color:
        return Color(self.lighten(amount), self.format)

    def blend(self, color: Color):
        rgb1: tuple = self.to("rgb")  # pyright: ignore
        rgb2: tuple = color.to("rgb")  # pyright: ignore
        r1, g1, b1 = rgb1
        r2, g2, b2 = rgb2
        r3 = int(0.5 * r1 + 0.5 * r2)
        g3 = int(0.5 * g1 + 0.5 * g2)
        b3 = int(0.5 * b1 + 0.5 * b2)
        return Color((r3, g3, b3), "rgb").to("hex")

    def blended(self, color: Color):
        return Color(self.blend(color), self.format)

    def saturate(self, amount: float):
        rgb = self.convert("rgb").normalized()
        h, l, s = rgb.to("hls")
        s = amount
        rgb = Color((h, l, s), "hls").convert("rgb")
        rgb = rgb.denormalized().to(self.format)

    def saturated(self, amount: float) -> Color:
        return Color(self.saturate(amount), self.format)
