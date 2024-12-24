"""
Creates a color theme for GTK, and writes that to `~/.config/gtk-4.0/gtk.css`
and `~/.config/gtk-3.0/gtk.css`. Note that currently theming GTK 3 and 4
separately isn't supported. Instead, only the supported options are applied
to GTK 3, and all options are applied to GTk 4. The custom css is applied to
both GTK 3 and 4.
"""

from pathlib import Path

import chroma
from chroma.exceptions import ParentDirectoryException
from chroma.integration import Integration
from chroma.logger import Logger
from chroma.utils.theme import validate_header

logger = Logger.get_logger()

GTK_HEADER = f"/* {chroma.CHROMA_GENERATED_HEADER} */"
GTK_PALETTE_VALID_COLORS = [
    "blue",
    "green",
    "yellow",
    "orange",
    "red",
    "purple",
    "brown",
    "light",
    "dark",
]


def validate_palette(palette: dict, index: int) -> dict | None:
    """Validates the entries in a GTK color palette.

    If the entries are invalid, `None` is returned.

    If all entries are valid, then a palette is constructed in a way where the
    key is the palette index and color, and the value is the provided color.
    This constructed palette is returned as a `dict`. For example:
    ```
    { "blue_1": "#00ff00" }
    ```
    """

    # GTK only supports 5 separate palettes
    assert index in [1, 2, 3, 4, 5]

    # The palette would be a Lua object. We need to convert it to a python one.
    palette_keys = [k for k in palette]
    if sorted(palette_keys) == sorted(GTK_PALETTE_VALID_COLORS):
        return {
            f"blue_{index}": palette["blue"],
            f"green_{index}": palette["green"],
            f"yellow_{index}": palette["yellow"],
            f"orange_{index}": palette["orange"],
            f"red_{index}": palette["red"],
            f"purple_{index}": palette["purple"],
            f"brown_{index}": palette["brown"],
            f"light_{index}": palette["light"],
            f"dark_{index}": palette["dark"],
        }


class GTKIntegration(Integration):
    def apply(self):
        if self.group.get("colors") is None:
            logger.info("Colors for GTK group is unset. Skipping integration.")
            return
        palettes = []

        theme_palettes = self.group.get("palettes")
        if theme_palettes is not None:
            theme_palettes = dict(theme_palettes)
            for i in range(1, 6):
                palette = theme_palettes.get(f"palette{i}")
                if palette is None:
                    logger.warn(f"Palette {i} is unset. Skipping.")
                    continue

                if not isinstance(palette, dict):
                    palette = dict(palette)

                validated_palette = validate_palette(palette, i)
                if validated_palette is None:
                    logger.warn(f"Palette {i} contains invalid keys. Skipping.")
                    logger.debug(f"Got: {validated_palette}")
                    continue

                palettes.append(validated_palette)
        else:
            logger.warn(
                "No palettes present. Please have at least one palette for the theme."
            )

        gtk3_valid = validate_header(Path(self.group["out"]["gtk3"]), GTK_HEADER)
        gtk4_valid = validate_header(Path(self.group["out"]["gtk4"]), GTK_HEADER)
        if not gtk3_valid or not gtk4_valid:
            logger.error("Cannot write configuration for GTK. Skipping integration.")
            return

        generated_file = []
        generated_file.append(GTK_HEADER)

        for name, color in self.group["colors"].items():
            generated_file.append(f"@define-color {name} {color};")
        for palette in palettes:
            for name, color in palette.items():
                generated_file.append(f"@define-color {name} {color};")

        generated_file.append(self.group["sidebar_patch"])

        # If the group has a field for extra GTK CSS, then add that to the
        # output file too.
        if self.group.get("extra_css") is not None:
            generated_file.append(self.group["extra_css"])

        # Manually insert newlines to make it play well with file.writelines()
        generated_file = [line + "\n" for line in generated_file]

        try:
            with open(Path(self.group["out"]["gtk3"]).expanduser(), "w") as f:
                f.writelines(generated_file)
            with open(Path(self.group["out"]["gtk4"]).expanduser(), "w") as f:
                f.writelines(generated_file)
        except FileNotFoundError as e:
            ParentDirectoryException(
                f"{e.__str__()}\n"
                "Failed to open file. Does the parent directory exist?"
            )

        logger.info("Successfully applied GTK theme!")


def register():
    return {"gtk": GTKIntegration}
