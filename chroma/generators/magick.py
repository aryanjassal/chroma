import re
import subprocess
from pathlib import Path
from typing import Callable

from chroma.colors import Color, ColorHex, ColorHSL
from chroma.logger import Logger
from chroma.types import HSLMap, HSLMapValue
from chroma.utils.generator import clamp_color_to_hslrules, match_color_from_hslmap
from chroma.utils.tools import check_program, clamp

logger = Logger.get_logger()


def generator_from(
    source: ColorHex, transform: Callable[[ColorHex], ColorHex], condition: HSLMapValue
) -> ColorHex:
    color = transform(source)
    color = clamp_color_to_hslrules(color, condition)
    return color.cast(ColorHex)


def generator_norm(
    base: str,
    colors: dict[str, Color],
    condition: HSLMapValue,
) -> ColorHex:
    mix = ColorHex(base)
    if mix.cast(ColorHSL).l < 0.3:
        mix = mix.cast(ColorHSL).set_l(0.45)
    else:
        mix = mix.darkened(0.25)
    color = colors["white"].blended(mix, 0.75)
    color = color.blended(colors["accent"], 0.15)
    color = color.saturated(0.2)
    color = color.darkened(0.2)
    color = color.blend(mix, 0.15)
    color = color.lighten(0.25)
    color = clamp_color_to_hslrules(color, condition)
    return color.cast(ColorHex)


def generator_bright(
    base: str,
    colors: dict[str, Color],
    condition: HSLMapValue,
) -> ColorHex:
    return generator_norm(base, colors, condition).lightened(0.15)


def generator_fg(
    lightness: float,
    colors: dict[str, Color],
    condition: HSLMapValue,
) -> ColorHex:
    white = colors["white"].cast(ColorHSL).normalize()
    accent = colors["accent"].cast(ColorHSL).normalize()
    l1 = white.color[0]
    l2 = accent.color[0]
    lum = (l1 + l2) / 2
    white.set_l(clamp(lum, 0.75, 1.0))
    white = white.lighten(lightness)
    color = clamp_color_to_hslrules(white, condition)
    return color.cast(ColorHex)


def generator_bg(
    darkness: float,
    colors: dict[str, Color],
    condition: HSLMapValue,
) -> ColorHex:
    black = colors["black"].cast(ColorHSL).normalize()
    accent = colors["accent"].cast(ColorHSL).normalize()
    l1 = black.color[0]
    l2 = accent.color[0]
    lum = (l1 + l2) / 2
    black.set_l(clamp(lum, 0.0, 0.15))
    black = black.darken(darkness)
    color = clamp_color_to_hslrules(black, condition)
    return color.cast(ColorHex)


# These generators are used when the corresponding color cannot be inferred from
# the image. Each generator must return a ColorHex object.
GENERATOR_REGISTRY = {
    "from_color": generator_from,
    "foreground": generator_fg,
    "background": generator_bg,
    "norm": generator_norm,
    "bright": generator_bright,
}


def generate(
    image_path: Path,
    hsl_map: HSLMap,
    colors_map: dict[str, dict],
    depth: int = 8,
    image_size: int = 256,
    max_colors: int = 1024,
):
    check_program("magick")
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
    proc_io = subprocess.run(command, capture_output=True)

    if proc_io.returncode != 0:
        raise ValueError(
            f"Failed to parse image. Program returned with code {proc_io.returncode}"
        )

    # If anything went wrong, inform the user.
    if proc_io.stderr:
        logger.error(proc_io.stderr)

    stdout = proc_io.stdout.decode("utf-8").splitlines()
    stdout = [line.strip() for line in stdout]
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
        color = ColorHex(color).cast(ColorHSL).denormalize()
        is_promiment = match_color_from_hslmap(
            color=color,
            condition_map={"prominent": (None, (40, 100), (25, 100))},
        )
        if is_promiment:
            prominent_color = color.cast(ColorHex)
            logger.debug(f"Detected prominent color {prominent_color}")
            break

    if prominent_color is None:
        prominent_color = ColorHex(raw_colors[0])
        logger.debug(
            f"Could not detect a suitable prominent color. "
            f"Using {prominent_color.cast(ColorHex)}"
        )

    colors = {}
    for color in raw_colors:
        color = ColorHex(color)
        name = match_color_from_hslmap(color, hsl_map, list(colors.keys()))

        if name is not None:
            color = color.cast(ColorHex)
            colors[name] = color
            logger.debug(f"Found color {name} to be {color}")

    def pass_key(item):
        _, spec = item
        return spec.get("pass", float("inf"))

    # If any colors don't exist, then synthesize them
    for name, args in sorted(colors_map.items(), key=pass_key):
        if colors.get(name) is None:
            # Condition can be None, so no enforcing.
            # TODO: Properly enforce hsl condition
            condition = hsl_map.get(name)
            generator_name = args["generator"]
            generator_args = args["args"]
            generator = GENERATOR_REGISTRY[generator_name]
            calculated_colors = {"prominent": prominent_color, **colors}

            if generator_name == "from_color":
                colors[name] = generator(
                    calculated_colors[generator_args["base"]],
                    generator_args["transform"],
                    condition,
                )
            elif generator_name == "foreground":
                colors[name] = generator(
                    generator_args["lightness"],
                    calculated_colors,
                    condition,
                )
            elif generator_name == "background":
                colors[name] = generator(
                    generator_args["darkness"],
                    calculated_colors,
                    condition,
                )
            elif generator_name == "norm":
                colors[name] = generator(
                    generator_args["base"],
                    calculated_colors,
                    condition,
                )
            elif generator_name == "bright":
                colors[name] = generator(
                    generator_args["base"],
                    calculated_colors,
                    condition,
                )
            else:
                logger.error(f"Generator name {generator_name} is invalid")
            logger.debug(f"Color {name} doesn't exist. Generated to {colors[name]}")
    return colors


def register():
    return {
        "magick": generate,
    }
