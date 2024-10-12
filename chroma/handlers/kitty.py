"""
Creates a color theme for Kitty.
"""

from pathlib import Path

import chroma
from chroma import utils
from chroma.colors import Color
from chroma.handler import Handler
from chroma.logger import Logger

logger = Logger.get_logger()

KITTY_HEADER = f"# {chroma.CHROMA_GENERATED_HEADER}"


class KittyHandler(Handler):
    def apply(self):
        colors = self.group.get("colors")
        if colors is None:
            logger.info("Colors for Kitty group is unset. Skipping handler.")
            return

        # TODO: actually support all the themable options in kitty like this:
        # https://github.com/kovidgoyal/kitty-themes/blob/master/template.conf
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

        metadata = {
            "name": self.meta.get("name"),
            "author": self.meta.get("author"),
            "blurb": self.meta.get("description"),
        }

        if not utils.validate_header(Path(self.group["out"]), KITTY_HEADER):
            logger.error("Cannot write configuration for Kitty. Skipping handler.")
            return

        generated_file = []
        generated_file.append(KITTY_HEADER)

        # Only write the metadata if the option is set to allow it.
        if self.group.get("write_meta"):
            generated_file.append("# vim:ft=kitty")
            for k, v in metadata.items():
                if v is not None:
                    generated_file.append(f"## {k}: {v}")

        for k, v in theme.items():
            col = Color(v, "hex").as_format("hex")
            generated_file.append(f"{k} {col}")

        # Manually insert newlines to make it play well with file.writelines()
        generated_file = [line + "\n" for line in generated_file]

        try:
            with open(Path(self.group["out"]).expanduser(), "w") as f:
                f.writelines(generated_file)
        except FileNotFoundError as e:
            logger.error(e)
            logger.fatal("Failed to open file. Does the parent directory exist?")

        logger.info("Successfully applied Kitty theme!")


def register():
    return {"kitty": KittyHandler}
