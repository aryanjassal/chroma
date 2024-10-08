"""
Creates a color theme for foot as a diff file and writes it to the foot config.
"""

from pathlib import Path
import re

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

    try:
        # Read the existing file contents
        with out_path.open('r') as f:
            lines = f.readlines()
        
        in_colors_section = False
        updated_lines = []
        
        # Regular expression to match color lines (e.g., foreground=...)
        color_line_pattern = re.compile(r'^(foreground|background|regular\d+|bright\d+)\s*=\s*.*$')

        for line in lines:
            # Detect the start of the [colors] section
            if line.strip() == "[colors]":
                in_colors_section = True
                updated_lines.append(line)
                continue

            # Detect the end of the [colors] section
            if in_colors_section and line.startswith("["):
                in_colors_section = False
                updated_lines.append(line)
                continue

            # If we are in the [colors] section, try to replace the color lines
            if in_colors_section:
                match = color_line_pattern.match(line.strip())
                if match:
                    color_key = match.group(1)
                    if color_key in theme:
                        # Replace with the new color
                        col = utils.color_to("hexvalue", theme[color_key])
                        updated_lines.append(f"{color_key}={col}\n")
                    else:
                        # Keep the old line if no new color is provided for this key
                        updated_lines.append(line)
                else:
                    updated_lines.append(line)
            else:
                updated_lines.append(line)
        
        # Write the updated config back to the file
        with out_path.open('w') as f:
            f.writelines(updated_lines)
        
        print("Colors updated successfully without touching other sections.")
    
    except FileNotFoundError as e:
        print(f"Config file not found: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

    logger.info("Successfully applied Foot theme!")
