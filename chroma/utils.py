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


def default_theme() -> Path:
    return chroma_themes_dir() / "default.lua"


def runtime():
    runtime = LuaRuntime(unpack_returned_tuples=True)
    runtime.execute(f"package.path = package.path .. ';{cache_dir().parent}/?.lua'")
    runtime.execute(f"package.path = package.path .. ';{chroma_themes_dir()}/?.lua'")
    return runtime


def backup(path: Path) -> bool:
    backup_name = f"{path.name}.bak"
    backup_path = path.parent / backup_name

    if backup_path.is_file():
        return False
    else:
        shutil.move(path, backup_path)
        return True


def validate_header(path: Path, header: str) -> bool:
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
        if backup(path):
            return True
        else:
            logger.warn(
                f"Could not automatically back up {path} because a backup "
                "already exists. Manual intervention is required."
            )
            return False
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


def inspect_dict(iterable) -> None:
    def inspect(d, pre=str()):
        for k, v in d.items():
            if isinstance(v, dict) or lua_type(v) == "table":
                inspect(v, f"{pre}{k}.")
            else:
                print(f"{pre}{k} = {v}")

    inspect(iterable)
