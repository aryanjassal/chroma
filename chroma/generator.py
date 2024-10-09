import re
import shutil
import subprocess
from pathlib import Path

import chroma
from chroma import utils
from chroma.logger import Logger

logger = Logger.get_logger()


def check_magick():
    if shutil.which("magick"):
        return True
    return False


# TODO: break out magick into a backend like pywal
def magick_generate(image_path: Path, palette_size: int, image_resize: str = "25%"):
    command = [
        "magick",
        str(image_path),
        "-resize",
        image_resize,
        "-colors",
        str(palette_size),
        "-unique-colors",
        "txt:-",
    ]
    proc_io = subprocess.run(command, capture_output=True, check=True)

    # If anything went wrong, inform the user.
    if proc_io.stderr:
        logger.error(proc_io.stderr)

    # First line is irrelevant to colors
    raw_output = proc_io.stdout.splitlines()[1:]

    colors = []
    for line in raw_output:
        match = re.search("#.{6}", str(line))
        if match:
            colors.append(match.group(0))
        else:
            logger.error(f"Color extraction with regex failed for line {line}")

    return colors


def generate(image_path: Path) -> list:
    # Ensure imagemagick exists on the system
    if not check_magick():
        logger.error("Imagemagick was not found on the system.")
        logger.fatal("Please install it and try again.")

    colors = []
    for i in range(0, 20):
        colors = magick_generate(image_path, 16 + i)

        # If this is our last iteration, then the palette couldn't be generated.
        if i == 19:
            logger.fatal("Imagemagick failed to generate a suitable palette.")

        # If we don't have sufficient number of colors, then keep trying.
        if len(colors) < 16:
            logger.info("Imagemagick could not generate a palette.")
            logger.info(f"Trying new palette size {17 + i}.")
            continue

        # If we have enough colors, then break the loop
        logger.info("Imagemagick generated a palette successfully.")
        break

    # First color is background. Colors after index 8 are repeated once.
    raw_colors = colors[:1] + colors[8:16] + colors[8:-1]

    if raw_colors[0][1] != "0":
        raw_colors[0] = utils.darken_color(raw_colors[0], 0.40)

    raw_colors[7] = utils.blend_color(raw_colors[7], "#eeeeee")
    raw_colors[8] = utils.darken_color(raw_colors[7], 0.30)
    raw_colors[15] = utils.blend_color(raw_colors[15], "#eeeeee")

    return raw_colors


def write_lua_colors(colors: list[str], out_path: Path, indent: int = 2):
    generated_theme = []
    generated_theme.append("local colors = {")

    for i, color in enumerate(colors):
        generated_theme.append(f"{' ' * indent}color{i} = \"{color.lower()}\",")

    generated_theme.append("}")
    generated_theme.append("return colors")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        f.writelines([f"{l}\n" for l in generated_theme])


def write_lua_theme(out_path: Path, enabled_modules: list, indent: int = 2):
    generated_theme = []
    generated_theme.append("local colors = require \"chroma.palettes.generated\"")
    generated_theme.append("local theme = require \"chroma.builtins.default\"")

    generated_theme.append(f"theme.options.chroma_version = \"{chroma.__version__}\"")

    if "gtk" in enabled_modules:
        gtk_colors_map = {
            "accent_color": "colors.color4",
            "accent_fg_color": "\"#ffffff\"",
            "accent_bg_color": "colors.color4",
            "window_fg_color": "colors.color7",
            "window_bg_color": "colors.color0",
            "view_fg_color": "colors.color7",
            "view_bg_color": "colors.color0",
            "headerbar_fg_color": "colors.color7",
            "headerbar_bg_color": "colors.color0",
            "card_fg_color": "colors.color7",
            "card_bg_color": "colors.color0",
            "dialog_fg_color": "colors.color7",
            "dialog_bg_color": "colors.color0",
            "popover_fg_color": "\"#ffffff\"",
            "popover_bg_color": "colors.color0",
            "sidebar_fg_color": "colors.color7",
            "sidebar_bg_color": "colors.color0",
            "backdrop_fg_color": "colors.color7",
            "backdrop_bg_color": "colors.color0",
        }
        generated_theme.append("theme.gtk.colors = {")
        for k, v in gtk_colors_map.items():
            generated_theme.append(f"{' ' * indent}{k} = {v},")
        generated_theme.append("}")

    if "kitty" in enabled_modules:
        kitty_colors_map = {
            "background": "colors.color0",
            "foreground": "colors.color7",
            "black": "colors.color0",
            "red": "colors.color1",
            "green": "colors.color2",
            "yellow": "colors.color3",
            "blue": "colors.color4",
            "magenta": "colors.color5",
            "cyan": "colors.color6",
            "white": "colors.color7",
            "bright_black": "colors.color0",
            "bright_red": "colors.color1",
            "bright_green": "colors.color2",
            "bright_yellow": "colors.color3",
            "bright_blue": "colors.color4",
            "bright_magenta": "colors.color5",
            "bright_cyan": "colors.color6",
            "bright_white": "colors.color7",
        }
        generated_theme.append("theme.kitty.colors = {")
        for k, v in kitty_colors_map.items():
            generated_theme.append(f"{' ' * indent}{k} = {v},")
        generated_theme.append("}")

    if "foot" in enabled_modules:
        foot_colors_map = {
            "background": "colors.color0",
            "foreground": "colors.color7",
            "black": "colors.color0",
            "red": "colors.color1",
            "green": "colors.color2",
            "yellow": "colors.color3",
            "blue": "colors.color4",
            "magenta": "colors.color5",
            "cyan": "colors.color6",
            "white": "colors.color7",
            "bright_black": "colors.color0",
            "bright_red": "colors.color1",
            "bright_green": "colors.color2",
            "bright_yellow": "colors.color3",
            "bright_blue": "colors.color4",
            "bright_magenta": "colors.color5",
            "bright_cyan": "colors.color6",
            "bright_white": "colors.color7",
        }
        generated_theme.append("theme.foot.colors = {")
        for k, v in foot_colors_map.items():
            generated_theme.append(f"{' ' * indent}{k} = {v},")
        generated_theme.append("}")

    generated_theme.append("return theme")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        f.writelines([f"{l}\n" for l in generated_theme])


