"""
Creates a color theme for Kitty.
"""

import os

from chroma.logger import Logger

logger = Logger.get_logger()


def apply(group):
    logger.warn("The Kitty handler is currently borked. Skipping.")
    return

    colors = group.colors

    theme = {
        "foreground": colors["foreground"],
        "background": colors["background"],
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

    kitty_config = []
    with open(os.path.expanduser("~/config/kitty/kitty.conf"), "r") as f:
        kitty_config = f.readlines()

    new_config = []

    for line in kitty_config:
        if any(col in line for col in theme.keys()):
            color_key = line.split()[0]
            if color_key in theme:
                new_line = f"{color_key} {colors[color_key]}"
                new_config.append(new_line)
            else:
                print(" WARN  Line does not have a valid color:")
                print(line)
                new_config.append(line)
        else:
            # Non-color lines are unaffected
            new_config.append(line)

    with open(os.path.expanduser("~/config/kitty/kitty.conf"), "w") as f:
        f.writelines(new_config)

    logger.info("Successfully applied Kitty theme!")
