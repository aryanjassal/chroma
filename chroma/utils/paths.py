from pathlib import Path

import chroma
from chroma.logger import Logger

logger = Logger.get_logger()


def find_theme_from_name(name: str) -> Path | None:
    """
    If a theme with the given name exists in the expected themes directory, then
    return the path to the theme. Otherwise, return None.

    The name can either include or omit file extension. As such, both cases for
    with and without extensions will be tested. If both file exists, then the
    closest match (i.e. without extension if the name didn't have an extension)
    will be returned.

    The themes present in the user's config directory will be prioritised over
    default themes.
    """

    # Make a list of directories to search in
    theme_dirs = [config_dir() / "themes", chroma_dir() / "themes"]

    # Set variables to names with and without the extension
    ext_exists = name[-4:0] == ".lua"
    name_with_ext = name if ext_exists else f"{name}.lua"
    name_without_ext = name[:-4] if ext_exists else name

    for dir in theme_dirs:
        # Check if the files exist (but don't return yet)
        exists_with_ext = (dir / name_with_ext).exists()
        exists_without_ext = (dir / name_without_ext).exists()

        logger.debug(f"Checking for '{name}' in {dir}")
        logger.debug(
            f"File with extension {'exists' if exists_with_ext else 'does not exist'}"
        )
        logger.debug(
            f"File without extension {'exists' if exists_without_ext else 'does not exist'}"
        )

        # If the extension existed in the original file, then we check the file
        # with extension first. Otherwise, we check the file without extension
        # first.
        if ext_exists:
            if exists_with_ext:
                return dir / name_with_ext
            elif exists_without_ext:
                return dir / name_without_ext
        else:
            if exists_without_ext:
                return dir / name_without_ext
            elif exists_with_ext:
                return dir / name_with_ext

    # If the file couldn't be found, then we return None as the file couldn't
    # be found. Note that omitting this line will also work as python will
    # return None by default, but it's better to be explicit.
    return None


def cache_dir() -> Path:
    path = Path("~/.cache/chroma").expanduser()
    path.mkdir(parents=True, exist_ok=True)
    return path


def config_dir() -> Path:
    path = Path("~/.config/chroma").expanduser()
    return path


def chroma_dir() -> Path:
    return Path(chroma.__file__).parent


def chroma_builtins_dir() -> Path:
    path = chroma_dir() / "builtins"
    return path


def themes_dir() -> Path:
    path = cache_dir() / "themes"
    path.mkdir(parents=True, exist_ok=True)
    return path


def override_theme() -> Path:
    return config_dir() / "overrides.lua"
