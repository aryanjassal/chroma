"""
Creates a color theme for foot as a diff file and writes it to the foot config.
"""

import difflib
import subprocess
from pathlib import Path

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
        # "selection_foreground": colors["selection_foreground"],
        # "selection_background": colors["selection_background"],
        # "cursor": colors["cursor"],
        # "cursor_text": colors["cursor_text"],
        "regular0": colors["black"],
        "regular1": colors["red"],
        "regular2": colors["green"],
        "regular3": colors["yellow"],
        "regular4": colors["blue"],
        "regular5": colors["magenta"],
        "regular6": colors["cyan"],
        "regular7": colors["white"],
        "bright0": colors["bright_black"],
        "bright1": colors["bright_red"],
        "bright2": colors["bright_green"],
        "bright3": colors["bright_yellow"],
        "bright4": colors["bright_blue"],
        "bright5": colors["bright_magenta"],
        "bright6": colors["bright_cyan"],
        "bright7": colors["bright_white"],
    }

    generated_theme = []
    generated_theme.append("[colors]")

    for k, v in theme.items():
        col = utils.color_to("hexvalue", v)
        generated_theme.append(f"{k}={col}")

    out_path = Path(group["out"]).expanduser()

    # The output file doesn't exist. Create a new file with only colors.
    if not out_path.exists():
        generated_theme = [line + "\n" for line in generated_theme]
        out_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(out_path, "w") as f:
                f.writelines(generated_theme)
        except FileNotFoundError as e:
            logger.error(e)
            logger.fatal("Failed to open file. Does the parent directory exist?")
        logger.info("Successfully applied Foot theme!")
        return

    # Otherwise, a config file exists. Create a diff and apply it.
    with open(out_path) as f:
        current_theme = f.read().splitlines()

    diff = list(difflib.unified_diff(current_theme, generated_theme, lineterm=""))
    diff = "\n".join(diff) + "\n"

    if diff.strip():
        diff_path = out_path.with_suffix(".diff")
        with open(diff_path, "w") as f:
            f.write(diff)
    else:
        logger.info("No changes detected. Skipping diff generation.")
        return

    capture = subprocess.run(
        ["patch", str(out_path), str(diff_path)],
        capture_output=True,
        text=True,
    )
    if capture.stdout:
        logger.info(capture.stdout.rstrip())
    if capture.stderr:
        logger.error(capture.stderr.rstrip())

    logger.info("Successfully applied Foot theme!")
