import colorsys
import re
import shutil
from pathlib import Path

from lupa import LuaRuntime, lua_type

import chroma
from chroma.logger import Logger

logger = Logger.get_logger()


def cache_dir() -> Path:
    path = Path("~/.cache/chroma").expanduser()
    path.mkdir(parents=True, exist_ok=True)
    return path


def config_dir() -> Path:
    path = Path("~/.config/chroma").expanduser()
    return path


def chroma_dir() -> Path:
    return Path(chroma.__file__).parent


# TODO: prune?
def chroma_themes_dir() -> Path:
    path = Path(chroma.__file__).parent
    path = path / "builtins"
    return path


def themes_dir() -> Path:
    path = cache_dir() / "themes"
    path.mkdir(parents=True, exist_ok=True)
    return path


def override_theme() -> Path:
    return config_dir() / "overrides.lua"


# TODO: prune?
def default_theme() -> Path:
    return chroma_themes_dir() / "default.lua"


def runtime():
    runtime = LuaRuntime(unpack_returned_tuples=True)
    runtime.execute(f"package.path = package.path .. ';{chroma_dir().parent}/?.lua'")
    runtime.execute(f"package.path = package.path .. ';{cache_dir().parent}/?.lua'")
    return runtime


def backup(path: Path) -> bool:
    backup_name = f"{path.name}.bak"
    backup_path = path.parent / backup_name

    if backup_path.is_file():
        return False
    else:
        shutil.move(path, backup_path)
        return True


def validate_header(path: Path, header, should_backup: bool = True) -> bool:
    path = path.expanduser()

    # If file does not exist, then we can generate config. Otherwise, try to
    # back the file up.
    if not path.is_file():
        return True

    with open(path) as f:
        file_header = f.readline().rstrip()  # Remove newline from first line

    # If the chroma-generated header doesn't exist, then try to back up the
    # file. If backup is successful, then we can write the theme. Otherwise,
    # raise a warning and mark the file as unable to be written to. If the
    # header exists, then we can write to the file.
    if file_header != header:
        if should_backup:
            if backup(path):
                return True
            else:
                logger.warn(
                    f"Could not automatically back up {path} because a backup "
                    "already exists. Manual intervention is required."
                )
                return False
        else:
            logger.warn(f"Header mismatch detected in {path}. Overwriting.")
    return True


def merge(*dicts) -> dict:
    def merge_recursive(dict1, dict2):
        if lua_type(dict1) == "table":
            dict1 = dict(dict1)

        result = dict1.copy()
        for k, v in dict2.items():
            if (
                k in result
                and (lua_type(result[k]) == "table" or isinstance(result[k], dict))
                and (lua_type(v) == "table" or isinstance(v, dict))
            ):
                result[k] = merge_recursive(result[k], v)
            else:
                result[k] = v
        return result

    result = {}
    for d in dicts:
        result = merge_recursive(result, d)

    return result


# def color_to(format: str, color: str) -> str | None:
#     hexcode_regex = r"^#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$"
#     hexvalue_regex = r"^([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$"
#
#     if format == "hexcode":
#         is_hex = bool(re.match(hexcode_regex, color) or re.match(hexvalue_regex, color))
#         if is_hex:
#             if color[0] == "#":
#                 return color
#             else:
#                 return "#" + color
#         else:
#             logger.error(f"Unsupported color: {color}")
#             return
#     elif format == "hexvalue":
#         is_hex = bool(re.match(hexcode_regex, color) or re.match(hexvalue_regex, color))
#         if is_hex:
#             if color[0] == "#":
#                 return color[1:]
#             else:
#                 return color
#         else:
#             logger.error(f"Unsupported color: {color}")
#             return
#     else:
#         logger.error(f"Unsupported format: {format}.")
#         return


def set_exception_hook(func):
    import sys

    sys.excepthook = func


def inspect_dict(iterable) -> None:
    def inspect(d, pre=str()):
        for k, v in d.items():
            if isinstance(v, dict) or lua_type(v) == "table":
                inspect(v, f"{pre}{k}.")
            else:
                print(f"{pre}{k} = {v}")

    inspect(iterable)


# ## Thanks to Pywal; Need to properly integrate into Chroma
#
#
# def hex_to_rgb(color):
#     """Convert a hex color to rgb."""
#     return tuple(bytes.fromhex(color.strip("#")))
#
#
# def hex_to_xrgba(color):
#     """Convert a hex color to xrdb rgba."""
#     col = color.lower().strip("#")
#     return "%s%s/%s%s/%s%s/ff" % (*col,)
#
#
# def rgb_to_hex(color):
#     """Convert an rgb color to hex."""
#     return "#%02x%02x%02x" % (*color,)
#
#
# def darken_color(color, amount):
#     """Darken a hex color."""
#     color = [int(col * (1 - amount)) for col in hex_to_rgb(color)]
#     return rgb_to_hex(color)
#
#
# def lighten_color(color, amount):
#     """Lighten a hex color."""
#     color = [int(col + (255 - col) * amount) for col in hex_to_rgb(color)]
#     return rgb_to_hex(color)
#
#
# def blend_color(color, color2):
#     """Blend two colors together."""
#     r1, g1, b1 = hex_to_rgb(color)
#     r2, g2, b2 = hex_to_rgb(color2)
#
#     r3 = int(0.5 * r1 + 0.5 * r2)
#     g3 = int(0.5 * g1 + 0.5 * g2)
#     b3 = int(0.5 * b1 + 0.5 * b2)
#
#     return rgb_to_hex((r3, g3, b3))
#
#
# def saturate_color(color, amount):
#     """Saturate a hex color."""
#     r, g, b = hex_to_rgb(color)
#     r, g, b = [x / 255.0 for x in (r, g, b)]
#     h, l, s = colorsys.rgb_to_hls(r, g, b)
#     s = amount
#     r, g, b = colorsys.hls_to_rgb(h, l, s)
#     r, g, b = [x * 255.0 for x in (r, g, b)]
#
#     return rgb_to_hex((int(r), int(g), int(b)))
