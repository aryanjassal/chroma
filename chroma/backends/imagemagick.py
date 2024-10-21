import re
import subprocess
from pathlib import Path

from chroma.colors import Color, ColorHex, ColorHSL
from chroma.logger import Logger
from chroma.types import Number

logger = Logger.get_logger()

HSL_MAP = {
    "accent": (None, (40, 100), (50, 100)),
    "black": (None, None, (10, 30)),
    "white": (None, None, (75, 95)),
    "red": ([(0, 35), (325, 360)], (40, 100), (30, 100)),
    "orange": ((35, 75), (30, 100), (40, 80)),
    "brown": ((35, 75), (10, 70), (20, 70)),
    "yellow": ((65, 105), (40, 100), (30, 100)),
    "green": ((100, 160), (40, 100), (30, 100)),
    "blue": ((180, 240), (40, 100), (40, 100)),
    "cyan": ((165, 195), (40, 100), (40, 100)),
    "magenta": ((280, 320), (70, 100), (40, 60)),
}


def hsl_match(color: Color, map: dict = HSL_MAP, omit=[]):
    def check_part(field, cond):
        if type(cond) == list:
            all_cond = []
            for c in cond:
                all_cond.append(check(field, c))
            return all(all_cond)
        else:
            return check(field, cond)

    def check(f, c):
        if c is None:
            return True
        if f >= c[0] and f <= c[1]:
            return True
        return False

    h, s, l = color.cast(ColorHSL).denormalized().color
    for name, requirement in map.items():
        if (
            check_part(h, requirement[0])
            and check_part(s, requirement[1])
            and check_part(l, requirement[2])
        ):
            if name in omit:
                continue

            color_regular = color.cast(ColorHex)
            color_bright = color.lightened(0.1).cast(ColorHex)

            logger.debug(f"Found color {name} to be {color_regular}")
            logger.debug(f"Calculated color bright_{name} to be {color_bright}")

            return {
                name: color_regular.color,
                f"bright_{name}": color_bright.color,
            }


def generator_fg(white: Color, min_light: Number, change_light: Number) -> Color:
    white = white.cast(ColorHSL)
    if white.l < 0.9:
        return white.set_l(min_light)
    else:
        return white.lightened(change_light)


def generator_bg(
    black: Color,
    thresh: float,
    min_sat: Number,
    min_dark: Number,
    change_dark: Number,
) -> Color:
    black = black.cast(ColorHSL)
    if black.l > thresh or black.s > 0.5:
        return black.set_s(min_sat).set_l(min_dark)
    else:
        return black.darkened(change_dark)


def generator_norm(white: Color, accent: Color, mix_hex: str) -> Color:
    mix = ColorHex(mix_hex)
    if mix.cast(ColorHSL).l < 0.3:
        mix = mix.cast(ColorHSL).set_l(0.45)
    else:
        mix = mix.darkened(0.25)
    color = white.blended(mix, 0.75)
    color = color.blended(accent, 0.05).cast(ColorHSL).set_s(0.5)
    if color.l < 0.4:
        return color.set_l(0.4)
    else:
        return color


def generator_bright(white: Color, accent: Color, mix_hex: str) -> Color:
    norm = generator_norm(white, accent, mix_hex)
    return norm.lightened(0.15)


REQUIRED_COLORS = {
    "accent": None,
    "black": None,
    "white": None,
    "bright_black": lambda x: x["black"].lightened(0.1),
    "bright_white": lambda x: x["white"].lightened(0.25),
    "accent_bg": lambda x: x["accent"].desaturated(0.2).darkened(0.1),
    "accent_fg": lambda x: x["white"].lightened(0.2),
    "foreground": lambda x: generator_fg(x["white"], 0.85, 0.0),
    "foreground_alt": lambda x: generator_fg(x["white"], 0.7, 0.1),
    "foreground_unfocus": lambda x: generator_fg(x["white"], 0.75, 0.15),
    "background": lambda x: generator_bg(x["black"], 0.10, 0.5, 0.08, 0.0),
    "background_alt": lambda x: generator_bg(x["black"], 0.15, 0.15, 0.15, 0.1),
    "background_unfocus": lambda x: generator_bg(x["black"], 0.2, 0.2, 0.2, 0.15),
    "red": lambda x: generator_norm(x["white"], x["accent"], "#ff0000"),
    "orange": lambda x: generator_norm(x["white"], x["accent"], "#ff8800"),
    "brown": lambda x: generator_norm(x["white"], x["accent"], "#884400"),
    "yellow": lambda x: generator_norm(x["white"], x["accent"], "#ffff00"),
    "green": lambda x: generator_norm(x["white"], x["accent"], "#00ff00"),
    "blue": lambda x: generator_norm(x["white"], x["accent"], "#0000ff"),
    "cyan": lambda x: generator_norm(x["white"], x["accent"], "#00ffff"),
    "magenta": lambda x: generator_norm(x["white"], x["accent"], "#ff00ff"),
    "bright_red": lambda x: generator_bright(x["white"], x["accent"], "#ff0000"),
    "bright_orange": lambda x: generator_bright(x["white"], x["accent"], "#ff8800"),
    "bright_brown": lambda x: generator_bright(x["white"], x["accent"], "#884400"),
    "bright_yellow": lambda x: generator_bright(x["white"], x["accent"], "#ffff00"),
    "bright_green": lambda x: generator_bright(x["white"], x["accent"], "#00ff00"),
    "bright_blue": lambda x: generator_bright(x["white"], x["accent"], "#0000ff"),
    "bright_cyan": lambda x: generator_bright(x["white"], x["accent"], "#00ffff"),
    "bright_magenta": lambda x: generator_bright(x["white"], x["accent"], "#ff00ff"),
}

REQUIRED_ESTIMATIONS = {
    "accent": lambda x: x.saturated(0.1),
    "black": lambda x: x.darkened(0.4)
    .blended(x, 0.4)
    .lightened(0.4)
    .blended(x, 0.1)
    .darkened(0.3 if x.cast(ColorHSL).color[2] > 25 else 0.1),
    "white": lambda x: x.lightened(0.4)
    .blended(x, 0.4)
    .darkened(0.4)
    .blended(x, 0.1)
    .lightened(0.3 if x.cast(ColorHSL).color[2] < 75 else 0.1),
}


def generate(
    image_path: Path,
    depth: int = 8,
    image_size: int = 256,
    hsl_map: dict = HSL_MAP,
    max_colors: int = 1024,
    required_colors: dict = REQUIRED_COLORS,
    required_estimations: dict = REQUIRED_ESTIMATIONS,
    max_iterations: int = 5,
    estimate_missing: bool = True,
):
    for _ in range(max_iterations):
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

        colors = []
        for line in stdout[:max_colors]:
            match = re.search("#.{6}", str(line).strip())
            if match:
                colors.append(match.group(0))
            else:
                logger.error(f"Color extraction with regex failed for line {line}")

        prominent_color = None
        for color in colors:
            color = ColorHex(color).cast(ColorHSL)
            if color.color[1] > 0.4 and color.color[2] > 0.25:
                prominent_color = color.cast(ColorHex)
                logger.debug(f"Detected prominent color {prominent_color}")
                break

        if prominent_color is None:
            prominent_color = ColorHex(colors[0])
            logger.debug(
                f"Could not detect a suitable prominent color. Using {prominent_color.cast(ColorHex)}"
            )

        mapped_colors = {}
        for color in colors:
            color = ColorHex(color)
            mapped = hsl_match(color, hsl_map, mapped_colors.keys())
            if mapped:
                mapped_colors = {**mapped, **mapped_colors}

        if estimate_missing:
            for name, generator in required_estimations.items():
                if mapped_colors.get(name) is None:
                    mapped_colors[name] = generator(prominent_color)
                    logger.debug(f"Estimating {name} to be {mapped_colors[name]}")

        colors = {}
        for name, color in mapped_colors.items():
            if not isinstance(color, Color):
                colors[name] = ColorHex(color)
            elif not isinstance(color, ColorHex):
                colors[name] = color.cast(ColorHex)
            else:
                colors[name] = color

        iterate = False
        for name, generator in required_colors.items():
            if mapped_colors.get(name) is None:
                if generator is None:
                    logger.error(f"Color {name} doesn't exist when it is expected to.")
                    iterate = True
                    break
                else:
                    mapped_colors[name] = generator(colors)
                    logger.debug(
                        f"Color {name} doesn't exist. Generated to {mapped_colors[name]}"
                    )

        if iterate:
            image_size = int(image_size * 1.1)
            max_colors = int(max_colors * 1.5)
            logger.error("Could not generate color palette.")
            logger.error(
                f"Trying larger image size {image_size}, extracted colors {max_colors}"
            )
            continue

        mapped_colors.pop("bright_accent", None)

        # Because generators can return non-hex values, explicitly convert it all to hex
        # I KNOW ITS SHIT, ILL MAKE IT BETTER LATER TRUST ME
        # I MEAN LOOK AT HISTORY OF theme.py
        for name, color in mapped_colors.items():
            if not isinstance(color, Color):
                mapped_colors[name] = ColorHex(color)
            elif not isinstance(color, ColorHex):
                mapped_colors[name] = color.cast(ColorHex)
            else:
                mapped_colors[name] = color

        return mapped_colors
    logger.fatal("Could not generate a suitable color palette.")


def register():
    return {"magick": generate, "imagemagick": generate}
