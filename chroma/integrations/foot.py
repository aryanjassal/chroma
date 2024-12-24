"""
Creates an includable theme file for foot terminal.

To use this theme, add the following line into your foot config, where
`<path>` should be replaced by the output file provided to Chroma.

```ini
[main]
include=<path>
```

This will make sure to import the theme dynamically, so the entire config file
doesn't have to be modified to change the theme. If other includes exist, then
they might interfere with the themes generated by Chroma.
"""

from pathlib import Path

import chroma
from chroma.colors import ColorHex
from chroma.exceptions import ParentDirectoryException
from chroma.integration import Integration
from chroma.logger import Logger
from chroma.utils.theme import validate_header

logger = Logger.get_logger()

FOOT_HEADER = f"# {chroma.CHROMA_GENERATED_HEADER}"


class FootIntegration(Integration):
    def apply(self):
        colors = self.group.get("colors")
        if colors is None:
            logger.info("Colors for Foot group is unset. Skipping integration.")
            return

        # TODO: actually support all the themable options in foot like this:
        # https://man.archlinux.org/man/foot.ini.5.en
        theme = {
            "foreground": colors.get("foreground"),
            "background": colors.get("background"),
            "selection-foreground": colors.get("selection_foreground"),
            "selection-background": colors.get("selection_background"),
            "regular0": colors.get("black"),
            "regular1": colors.get("red"),
            "regular2": colors.get("green"),
            "regular3": colors.get("yellow"),
            "regular4": colors.get("blue"),
            "regular5": colors.get("magenta"),
            "regular6": colors.get("cyan"),
            "regular7": colors.get("white"),
            "bright0": colors.get("bright_black"),
            "bright1": colors.get("bright_red"),
            "bright2": colors.get("bright_green"),
            "bright3": colors.get("bright_yellow"),
            "bright4": colors.get("bright_blue"),
            "bright5": colors.get("bright_magenta"),
            "bright6": colors.get("bright_cyan"),
            "bright7": colors.get("bright_white"),
        }

        if not validate_header(Path(self.group["out"]), FOOT_HEADER):
            logger.error("Cannot write configuration for Foot. Skipping integration.")
            return

        generated_theme = []
        generated_theme.append(FOOT_HEADER)
        generated_theme.append("[colors]")

        for k, v in theme.items():
            if v is None:
                logger.info(f"Key {k} is unset.")
                continue
            col = ColorHex(v).value
            generated_theme.append(f"{k}={col}")

        # Manually insert newlines to make it play well with file.writelines()
        generated_theme = [line + "\n" for line in generated_theme]

        try:
            with open(Path(self.group["out"]).expanduser(), "w") as f:
                f.writelines(generated_theme)
        except FileNotFoundError as e:
            ParentDirectoryException(
                f"{e.__str__()}\n"
                "Failed to open file. Does the parent directory exist?"
            )
        logger.info("Successfully applied Foot theme!")


def register():
    return {"foot": FootIntegration}
