"""
Creates a color theme for GTK 4, and writes that to `~/.config/gtk-4.0/gtk.css`.
"""

from pathlib import Path

import chroma
from chroma import utils
from chroma.logger import Logger

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


def apply(group, _):
    if group.get("colors") is None:
        logger.info("Colors for GTK group is unset. Skipping handler.")
        return
    palettes = []

    theme_palettes = dict(group.get("palettes"))
    if theme_palettes is not None:
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

    gtk3_valid = utils.validate_header(Path(group["out"]["gtk3"]), GTK_HEADER)
    gtk4_valid = utils.validate_header(Path(group["out"]["gtk4"]), GTK_HEADER)
    if not gtk3_valid or not gtk4_valid:
        logger.error("Cannot write configuration for GTK. Skipping handler.")
        return

    generated_file = []
    generated_file.append(GTK_HEADER)

    for name, color in group["colors"].items():
        generated_file.append(f"@define-color {name} {color};")
    for palette in palettes:
        for name, color in palette.items():
            generated_file.append(f"@define-color {name} {color};")

    generated_file.append(group["sidebar_patch"])

    # If the group has a field for extra GTK CSS, then add that to the
    # output file too.
    if group.get("extra_css") is not None:
        generated_file.append(group["extra_css"])

    # Manually insert newlines to make it play well with file.writelines()
    generated_file = [line + "\n" for line in generated_file]

    try:
        with open(Path(group["out"]["gtk3"]).expanduser(), "w") as f:
            f.writelines(generated_file)
        with open(Path(group["out"]["gtk4"]).expanduser(), "w") as f:
            f.writelines(generated_file)
    except FileNotFoundError as e:
        logger.error(e)
        logger.fatal("Failed to open file. Does the parent directory exist?")

    logger.info("Successfully applied GTK theme!")
