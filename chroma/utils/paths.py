from pathlib import Path

import chroma


def cache_dir() -> Path:
    path = Path("~/.cache/chroma").expanduser()
    path.mkdir(parents=True, exist_ok=True)
    return path


def config_dir() -> Path:
    path = Path("~/.config/chroma").expanduser()
    return path


def chroma_dir() -> Path:
    return Path(chroma.__file__).parent


def chroma_themes_dir() -> Path:
    path = chroma_dir() / "builtins"
    return path


def themes_dir() -> Path:
    path = cache_dir() / "themes"
    path.mkdir(parents=True, exist_ok=True)
    return path


def override_theme() -> Path:
    return config_dir() / "overrides.lua"
