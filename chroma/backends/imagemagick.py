import re
import subprocess
from pathlib import Path

from chroma.colors import Color
from chroma.logger import Logger

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

# fmt: off
REQUIRED_COLORS = {
    "accent": None,
    "black": None,
    "white": None,
    "bright_black": lambda x: x["black"].lighten(0.1),
    "bright_white": lambda x: x["white"].lighten(0.25),
    "accent_bg": lambda x: x["accent"].saturate(-0.1).darken(0.1),
    "accent_fg": lambda x: x["white"].lighten(0.2),
    "foreground": lambda x: x["white"].lighten(0.85, True) if x["white"].as_hsl().color[2] < 0.9 else x["white"],
    "foreground_alt": lambda x: x["white"].lighten(0.7, True) if x["white"].as_hsl().color[2] < 0.9 else x["white"].lighten(0.1),
    "foreground_unfocus": lambda x: x["white"].lighten(0.75, True) if x["white"].as_hsl().color[2] < 0.9 else x["white"].lighten(0.15),
    "background": lambda x: x["black"].saturate(0.5, True).darken(0.1, True) if x["black"].as_hsl().color[2] > 0.15 or x["black"].as_hsl().color[1] > 0.5 else x["black"],
    "background_alt": lambda x: x["black"].saturate(0.35, True).darken(0.15, True) if x["black"].as_hsl().color[2] > 0.15 or x["black"].as_hsl().color[1] > 0.5 else x["black"].darken(0.1), 
    "background_unfocus": lambda x: x["black"].saturate(0.2, True).darken(0.2, True) if x["black"].as_hsl().color[2] > 0.2 or x["black"].as_hsl().color[1] > 0.5 else x["black"].darken(0.15),
    "red": lambda x: x["white"].blend(Color("#ff0000", "hex").darken(0.1)).blend(x["accent"], 0.1).saturate(0.6, True), 
    "orange": lambda x: x["white"].blend(Color("#ff8800", "hex").darken(0.1)).blend(x["accent"], 0.1).saturate(0.6, True),
    "brown": lambda x: x["white"].blend(Color("#884400", "hex").darken(0.1)).blend(x["accent"], 0.1).saturate(0.6, True),
    "yellow": lambda x: x["white"].blend(Color("#ffff00", "hex").darken(0.1)).blend(x["accent"], 0.1).saturate(0.6, True),
    "green": lambda x: x["white"].blend(Color("#00ff00", "hex").darken(0.1)).blend(x["accent"], 0.1).saturate(0.6, True),
    "blue": lambda x: x["white"].blend(Color("#0000ff", "hex").darken(0.1)).blend(x["accent"], 0.1).saturate(0.6, True),
    "cyan": lambda x: x["white"].blend(Color("#00ffff", "hex").darken(0.1)).blend(x["accent"], 0.1).saturate(0.6, True),
    "magenta": lambda x: x["white"].blend(Color("#00ff00", "hex").darken(0.1)).blend(x["accent"], 0.1).saturate(0.6, True),
    "bright_red": lambda x: x["white"].blend(Color("#ff0000", "hex")).lighten(0.15).blend(x["accent"], 0.1), 
    "bright_orange": lambda x: x["white"].blend(Color("#ff8800", "hex")).lighten(0.15).blend(x["accent"], 0.1),
    "bright_brown": lambda x: x["white"].blend(Color("#884400", "hex")).lighten(0.15).blend(x["accent"], 0.1),
    "bright_yellow": lambda x: x["white"].blend(Color("#ffff00", "hex")).lighten(0.15).blend(x["accent"], 0.1),
    "bright_green": lambda x: x["white"].blend(Color("#00ff00", "hex")).lighten(0.15).blend(x["accent"], 0.1),
    "bright_blue": lambda x: x["white"].blend(Color("#0000ff", "hex")).lighten(0.15).blend(x["accent"], 0.1),
    "bright_cyan": lambda x: x["white"].blend(Color("#00ffff", "hex")).lighten(0.15).blend(x["accent"], 0.1),
    "bright_magenta": lambda x: x["white"].blend(Color("#00ff00", "hex")).lighten(0.15).blend(x["accent"], 0.1),
}

REQUIRED_ESTIMATIONS = {
    "accent": lambda x: x.saturate(0.1),
    "black": lambda x: x.darken(0.4).blend(x, 0.4).lighten(0.4).blend(x, 0.1).darken(0.3 if x.as_hsl().color[2] > 25 else 0.1),
    "white": lambda x: x.lighten(0.4).blend(x, 0.4).darken(0.4).blend(x, 0.1).lighten(0.3 if x.as_hsl().color[2] < 75 else 0.1),
}
# fmt: on


def hsl_match(color: Color, map: dict = HSL_MAP, omit=[]):
    def hsl_denormal(h, s, l):
        h = int(h * 360)
        s = int(s * 100)
        l = int(l * 100)
        return (h, s, l)

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

    h, s, l = hsl_denormal(*color.as_hsl().color)
    for name, requirement in map.items():
        if (
            check_part(h, requirement[0])
            and check_part(s, requirement[1])
            and check_part(l, requirement[2])
        ):
            if name in omit:
                continue

            color_regular = color.as_hex()
            color_bright = color.lighten(0.1).as_hex()

            logger.debug(f"Found color {name} to be {color_regular}")
            logger.debug(f"Calculated color bright_{name} to be {color_bright}")

            return {
                name: color_regular.color,
                f"bright_{name}": color_bright.color,
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
            color = Color(color, "hex").as_hsl()
            if color.color[1] > 0.4 and color.color[2] > 0.25:
                prominent_color = color.as_hex()
                logger.debug(f"Detected prominent color {prominent_color}")
                break

        if prominent_color is None:
            prominent_color = Color(colors[0], "hex")
            logger.debug(
                f"Could not detect a suitable prominent color. Using {prominent_color.as_hex()}"
            )

        mapped_colors = {}
        for color in colors:
            color = Color(color, "hex")
            mapped = hsl_match(color, hsl_map, mapped_colors.keys())
            if mapped:
                mapped_colors = {**mapped, **mapped_colors}

        if estimate_missing:
            for name, generator in required_estimations.items():
                if mapped_colors.get(name) is None:
                    mapped_colors[name] = generator(prominent_color)
                    logger.debug(f"Estimating {name} to be {mapped_colors[name]}")

        colors = {
            k: Color(v, "hex") if type(v) != Color else v
            for k, v, in mapped_colors.items()
        }

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

        mapped_colors = {
            k: v.color if type(v) == Color else v for k, v, in mapped_colors.items()
        }

        return mapped_colors
    logger.fatal("Could not generate a suitable color palette.")


def register():
    return {"magick": generate, "imagemagick": generate}
