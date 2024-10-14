import importlib
import importlib.util
import shutil
import subprocess
from pathlib import Path
from typing import Literal, NoReturn, Optional

from lupa import LuaRuntime, lua_type

import chroma
from chroma.logger import Logger

logger = Logger.get_logger()


Number = int | float


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


# TODO: limit functionality to validation and not backup
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


def to_dict(table):
    """Recursively converts lua tables to python dicts"""

    def convert(t):
        result = dict()
        for k, v in t.items():
            if lua_type(v) == "table" or type(v) == dict:
                v = convert(v)
            result[k] = v
        return result

    return convert(table)


def merge(*dicts) -> dict:
    def merge_recursive(dict1, dict2):
        result = dict1.copy()
        for k, v in dict2.items():
            if k in result and isinstance(result[k], dict) and isinstance(v, dict):
                result[k] = merge_recursive(result[k], v)
            else:
                result[k] = v
        return result

    result = {}
    for d in dicts:
        result = merge_recursive(result, d)

    return result


def set_exception_hook(func):
    import sys

    sys.excepthook = func


def never(message: Optional[str] = None) -> NoReturn:
    if message:
        raise RuntimeError(message)
    raise RuntimeError


def inspect_dict(iterable) -> None:
    def inspect(d, pre=str()):
        for k, v in d.items():
            if isinstance(v, dict):
                inspect(v, f"{pre}{k}.")
            else:
                print(f"{pre}{k} = {v}")

    inspect(iterable)


def parse_file(runtime, filename) -> dict:
    with open(filename, mode="r") as f:
        theme = f.read()
    return to_dict(runtime.execute(theme))


def load_module(path: str | Path):
    """Dynamically load a handler from a file path."""

    module_name = Path(path).stem
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is not None:
        module = importlib.util.module_from_spec(spec)
        if spec.loader is not None:
            spec.loader.exec_module(module)
            return module
        else:
            logger.fatal(f"Could not load module {module_name}")
    else:
        logger.fatal(f"Could not load module {module_name}")


def discover_modules(path: str | Path):
    """Discover and load all handlers from a directory."""

    config_dir = Path(path).expanduser()
    modules = []

    if Path(config_dir).is_dir():
        for filename in Path(config_dir).iterdir():
            if filename.suffix == ".py":
                module_path = Path(config_dir) / filename
                module = load_module(module_path)
                modules.append(module)
    return modules


def check_program(
    program: str,
    action: Literal["WARN"] | Literal["NOOP"] | Literal["EXIT"] = "WARN",
) -> bool:
    result = subprocess.run(
        ["command", "-v", program],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        text=True,
        shell=False,
    )
    if result.returncode != 0:
        if action == "WARN":
            logger.warn(
                f"{program} was not found on your system. You can disable "
                "the handler by assigning the table to nil in the overrides."
            )
            return False
        if action == "EXIT":
            logger.fatal(
                f"{program} was not found on your system. You must disable "
                "the handler by assigning the table to nil in the overrides."
            )
    return True


def write_lua_colors(path: Path, colors: dict, indent: int = 2):
    contents = []
    contents.append("return {\n")
    for name, color in colors.items():
        contents.append(f"{' ' * indent}{name} = \"{color}\",\n")
    contents.append("}")
    path.write_text("".join(contents))


def clamp(x: Number, _min: Number, _max: Number):
    return max(_min, min(x, _max))
