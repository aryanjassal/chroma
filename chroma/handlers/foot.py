"""
Creates a color theme for foot as a diff file and writes it to the foot config.
"""

import difflib
from pathlib import Path
import subprocess

from chroma import utils
from chroma.logger import Logger

logger = Logger.get_logger()


def apply(group, _):
    colors = group.get("colors")
    if colors is None:
        logger.info("Colors for Foot group is unset. Skipping handler.")
        return

    theme = {
        "foreground": colors["foreground"],
        "background": colors["background"],
        "selection_foreground": colors["selection_foreground"],
        "selection_background": colors["selection_background"],
        "cursor": colors["cursor"],
        "cursor_text": colors["cursor_text"],
        "color0": colors["black"],
        "color1": colors["red"],
        "color2": colors["green"],
        "color3": colors["yellow"],
        "color4": colors["blue"],
        "color5": colors["magenta"],
        "color6": colors["cyan"],
        "color7": colors["white"],
        "color8": colors["bright_black"],
        "color9": colors["bright_red"],
        "color10": colors["bright_green"],
        "color11": colors["bright_yellow"],
        "color12": colors["bright_blue"],
        "color13": colors["bright_magenta"],
        "color14": colors["bright_cyan"],
        "color15": colors["bright_white"],
    }

    generated_theme = []

    for k, v in theme.items():
        col = utils.color_to("hexvalue", v)
        generated_theme.append(f"{k} {col};")

    out_path = Path(group["out"]).expanduser()

    # The output file doesn't exist. Create a new file with only colors.
    if not out_path.exists():
        generated_theme = [line + "\n" for line in generated_theme]

        try:
            with open(out_path, "w") as f:
                f.writelines(generated_theme)
        except FileNotFoundError as e:
            logger.error(e)
            logger.fatal("Failed to open file. Does the parent directory exist?")
        return

    # Otherwise, a config file exists. Create a diff and apply it.
    with open(out_path) as f:
        current_theme = f.read().splitlines()

    diff = list(difflib.unified_diff(current_theme, generated_theme, lineterm=""))
    diff = "\n".join(diff)

    if diff:
        diff_path = out_path.with_suffix(".diff")
        with open(diff_path, "w") as f:
            f.write(diff)
    else:
        logger.info("No changes detected. Skipping diff generation.")
        return

    subprocess.run(["patch", str(out_path), str(diff_path)])

    logger.info("Successfully applied Foot theme!")
