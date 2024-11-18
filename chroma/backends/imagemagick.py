import re
import subprocess
from pathlib import Path

from chroma import utils
from chroma.colors import Color, ColorHex, ColorHSL
from chroma.logger import Logger
from chroma.types import HSLMap, HSLMapValue

logger = Logger.get_logger()

HSL_MAP: HSLMap = {
    "accent": (None, (60, 100), (50, 90)),
    "black": (None, None, (5, 20)),
    "white": (None, None, (80, 95)),
    "background": (None, (0, 20), (5, 10)),
    "foreground": (None, (0, 20), (90, 95)),
    "red": ([(0, 35), (325, 360)], (40, 90), (30, 90)),
    "orange": ((35, 75), (30, 90), (40, 80)),
    "brown": ((35, 75), (30, 70), (20, 70)),
    "yellow": ((65, 105), (40, 90), (30, 90)),
    "green": ((100, 160), (40, 90), (30, 90)),
    "blue": ((200, 230), (40, 50), (40, 60)),
    "cyan": ((170, 200), (40, 90), (40, 90)),
    "magenta": ((280, 310), (30, 50), (30, 50)),
}


# NOTE: These generators are used when the corresponding color cannot be inferred
# from the image.


def generator_fg(
    white: Color,
    accent: Color,
    blend_ratio: float,
    light_ratio: float,
    condition: HSLMapValue,
) -> Color:
    white = white.cast(ColorHSL).normalize()
    accent = accent.cast(ColorHSL).normalize()
    l1 = white.color[0]
    l2 = accent.color[0]
    hue = l1 * blend_ratio + l2 * blend_ratio
    white.set_l(utils.clamp(hue, 0.0, 1.0))
    white = white.lighten(light_ratio)
    color = utils.clamp_color_to_hslrules(white, condition)
    return color.cast(ColorHex)  # To stringify as a Hex color


def generator_bg(
    black: Color,
    accent: Color,
    blend_ratio: float,
    dark_ratio: float,
    condition: HSLMapValue,
) -> Color:
    black = black.cast(ColorHSL).normalize()
    accent = accent.cast(ColorHSL).normalize()
    l1 = black.color[0]
    l2 = accent.color[0]
    hue = l1 * blend_ratio + l2 * blend_ratio
    black.set_l(utils.clamp(hue, 0.0, 1.0))
    black = black.darken(dark_ratio)
    color = utils.clamp_color_to_hslrules(black, condition)
    return color.cast(ColorHex)  # To stringify as a Hex color


def generator_norm(
    white: Color,
    accent: Color,
    mix_hex: str,
    condition: HSLMapValue,
) -> Color:
    mix = ColorHex(mix_hex)
    if mix.cast(ColorHSL).l < 0.3:
        mix = mix.cast(ColorHSL).set_l(0.45)
    else:
        mix = mix.darkened(0.25)
    color = white.blended(mix, 0.75)
    color = color.blended(accent, 0.15)
    color = color.saturated(0.2)
    color = color.darkened(0.2)
    color = color.blend(mix, 0.15)
    color = color.lighten(0.25)
    color = utils.clamp_color_to_hslrules(color, condition)
    return color.cast(ColorHex)  # To stringify as a Hex color


def generator_bright(
    white: Color,
    accent: Color,
    mix_hex: str,
    condition: HSLMapValue,
) -> Color:
    return generator_norm(white, accent, mix_hex, condition).lightened(0.15)


def generator_black(prominent: Color, condition: HSLMapValue) -> Color:
    color = (
        prominent.darkened(0.4)
        .blended(prominent, 0.2)
        .lightened(0.4)
        .blended(prominent, 0.1)
    )
    color = utils.clamp_color_to_hslrules(color, condition)
    return color.cast(ColorHex)  # To stringify as a Hex color


def generator_white(prominent: Color, condition: HSLMapValue) -> Color:
    color = (
        prominent.lightened(0.4)
        .blended(prominent, 0.2)
        .darkened(0.4)
        .blended(prominent, 0.1)
    )
    color = utils.clamp_color_to_hslrules(color, condition)
    return color.cast(ColorHex)  # To stringify as a Hex color


def generator_accent(prominent: Color, condition: HSLMapValue) -> Color:
    color = utils.clamp_color_to_hslrules(prominent.saturated(0.1), condition)
    return color.cast(ColorHex)  # To stringify as a Hex color


# fmt: off
REQUIRED_COLORS = {
    "accent": lambda x: generator_accent(x["prominent"], HSL_MAP["accent"]),
    "black": lambda x: generator_black(x["prominent"], HSL_MAP["black"]),
    "white": lambda x: generator_white(x["prominent"], HSL_MAP["white"]),
    "bright_black": lambda x: x["black"].lightened(0.1),
    "bright_white": lambda x: x["white"].lightened(0.1),
    "accent_bg": lambda x: x["accent"].desaturated(0.2).darkened(0.1),
    "accent_fg": lambda x: x["white"].lightened(0.15),
    "foreground": lambda x: generator_fg(x["white"], x["accent"], 0.5, 0.08, HSL_MAP["foreground"]),
    "foreground_alt": lambda x: generator_fg(x["white"], x["accent"], 0.5, 0.1, HSL_MAP["foreground"]),
    "foreground_unfocus": lambda x: generator_fg(x["white"], x["accent"], 0.5, 0.12, HSL_MAP["foreground"]),
    "background": lambda x: generator_bg(x["black"], x["accent"], 0.5, 0.08, HSL_MAP["background"]),
    "background_alt": lambda x: generator_bg(x["black"], x["accent"], 0.5, 0.1, HSL_MAP["background"]),
    "background_unfocus": lambda x: generator_bg(x["black"], x["accent"], 0.5, 0.12, HSL_MAP["background"]),
    "red": lambda x: generator_norm(x["white"],x["accent"], "#ff0000", HSL_MAP["red"]),
    "orange": lambda x: generator_norm(x["white"], x["accent"], "#ff8800", HSL_MAP["orange"]),
    "brown": lambda x: generator_norm(x["white"], x["accent"], "#884400", HSL_MAP["brown"]),
    "yellow": lambda x: generator_norm(x["white"], x["accent"], "#ffff00", HSL_MAP["yellow"]),
    "green": lambda x: generator_norm(x["white"], x["accent"], "#00ff00", HSL_MAP["green"]),
    "blue": lambda x: generator_norm(x["white"], x["accent"], "#0000ff", HSL_MAP["blue"]),
    "cyan": lambda x: generator_norm(x["white"], x["accent"], "#00ffff", HSL_MAP["cyan"]),
    "magenta": lambda x: generator_norm(x["white"], x["accent"], "#ff00ff", HSL_MAP["magenta"]),
    "bright_red": lambda x: generator_bright(x["white"], x["accent"], "#ff0000", HSL_MAP["red"]),
    "bright_orange": lambda x: generator_bright(x["white"], x["accent"], "#ff8800", HSL_MAP["orange"]),
    "bright_brown": lambda x: generator_bright(x["white"], x["accent"], "#884400", HSL_MAP["brown"]),
    "bright_yellow": lambda x: generator_bright(x["white"], x["accent"], "#ffff00", HSL_MAP["yellow"]),
    "bright_green": lambda x: generator_bright(x["white"], x["accent"], "#00ff00", HSL_MAP["green"]),
    "bright_blue": lambda x: generator_bright(x["white"], x["accent"], "#0000ff", HSL_MAP["blue"]),
    "bright_cyan": lambda x: generator_bright(x["white"], x["accent"], "#00ffff", HSL_MAP["cyan"]),
    "bright_magenta": lambda x: generator_bright(x["white"], x["accent"], "#ff00ff", HSL_MAP["magenta"]),
}
# fmt: on


def generate(
    image_path: Path,
    depth: int = 8,
    image_size: int = 256,
    hsl_map: dict = HSL_MAP,
    max_colors: int = 1024,
    required_colors: dict = REQUIRED_COLORS,
):
    command = [
        "magick",
        str(image_path),
        "-resize",
        f"{image_size}x{image_size}^",
        "-gravity",
        "center",
        "-extent",
        f"{image_size}x{image_size}",
        "-format",
        "%c",
        "-depth",
        str(depth),
        "histogram:info:-",
    ]
    proc_io = subprocess.run(command, capture_output=True, check=True)

    # If anything went wrong, inform the user.
    if proc_io.stderr:
        logger.error(proc_io.stderr)

    stdout = proc_io.stdout.decode("utf-8").splitlines()
    stdout = [l.strip() for l in stdout]
    stdout.sort(key=lambda x: x.split(":", 1)[0], reverse=True)

    raw_colors = []
    for line in stdout[:max_colors]:
        match = re.search("#.{6}", str(line).strip())
        if match:
            raw_colors.append(match.group(0))
        else:
            logger.error(f"Color extraction with regex failed for line {line}")

    prominent_color = None
    for color in raw_colors:
        color = ColorHex(color).cast(ColorHSL)
        if color.color[1] > 0.4 and color.color[2] > 0.25:
            prominent_color = color.cast(ColorHex)
            logger.debug(f"Detected prominent color {prominent_color}")
            break

    if prominent_color is None:
        prominent_color = ColorHex(raw_colors[0])
        logger.debug(
            f"Could not detect a suitable prominent color. Using {prominent_color.cast(ColorHex)}"
        )

    colors = {}
    for color in raw_colors:
        color = ColorHex(color)
        name = utils.match_color_from_hslmap(color, hsl_map, list(colors.keys()))

        if name is not None:
            color_regular = color.cast(ColorHex)

            logger.debug(f"Found color {name} to be {color_regular}")
            colors[name] = color_regular

            if name != "accent":
                color_bright = color.lightened(0.1).cast(ColorHex)
                logger.debug(f"Calculated color bright_{name} to be {color_bright}")
                colors[f"bright_{name}"] = color_bright

    mcolors = {}
    for name, color in colors.items():
        if not isinstance(color, Color):
            mcolors[name] = ColorHex(color)
        elif not isinstance(color, ColorHex):
            mcolors[name] = color.cast(ColorHex)
        else:
            mcolors[name] = color

    colors = mcolors

    for name, generator in required_colors.items():
        if colors.get(name) is None:
            if generator is None:
                logger.error(f"Color {name} doesn't exist when it is expected to.")
                break
            else:
                colors[name] = generator({"prominent": prominent_color, **colors})
                logger.debug(f"Color {name} doesn't exist. Generated to {colors[name]}")

    colors.pop("bright_accent", None)

    # Because generators can return non-hex values, explicitly convert it all to hex
    # I KNOW ITS SHIT, ILL MAKE IT BETTER LATER TRUST ME
    # I MEAN LOOK AT HISTORY OF theme.py
    for name, color in colors.items():
        if not isinstance(color, Color):
            colors[name] = ColorHex(color)
        elif not isinstance(color, ColorHex):
            colors[name] = color.cast(ColorHex)
        else:
            colors[name] = color

    return colors


def register():
    return {
        "magick": generate,
        "imagemagick": generate,
    }
