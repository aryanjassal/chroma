from pathlib import Path

from lupa import LuaRuntime

from chroma.colors.methods import darken, desaturate, lighten, saturate
from chroma.logger import Logger

from .paths import cache_dir, chroma_dir
from .tools import backup, to_dict

logger = Logger.get_logger()

DEFAULT_STATE: dict = {
    "use_generated": True,

    "darken": darken,
    "lighten": lighten,
    "saturate": saturate,
    "desaturate": desaturate,

    # "chroma": {
    #     "colors": {
    #         "methods": {
    #             "darken": darken,
    #             "lighten": lighten,
    #             "saturate": saturate,
    #             "desaturate": desaturate,
    #         }
    #     }
    # },
}


# TODO: add support for lists/arrays
def sanitize_python(state: dict = dict(), **kwargs) -> dict:
    state.update(kwargs)

    def sanitize_value(value):
        if isinstance(value, bool):
            return "true" if value else "false"
        elif isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, str):
            return f'"{value}"'
        elif isinstance(value, dict):
            return sanitize_python(value)
        elif value is None:
            return "nil"
        elif callable(value):
            return value
        else:
            raise ValueError(f"Value of type {type(value)} ({value}) is unsupported")

    sanitized = dict()
    for name, value in state.items():
        sanitized[name] = sanitize_value(value)
    return sanitized


# TODO: add tabled global methods
def runtime(state: dict | None = DEFAULT_STATE):
    runtime = LuaRuntime(unpack_returned_tuples=True)  # pyright: ignore
    runtime.execute(f"package.path = package.path .. ';{chroma_dir().parent}/?.lua'")
    runtime.execute(f"package.path = package.path .. ';{cache_dir().parent}/?.lua'")

    def register_state(d):
        for key, value in d.items():
            if isinstance(value, dict):
                register_state(value)
            elif callable(value):
                logger.debug(f"Setting function '{key}'")
                runtime.globals()[key] = value
            else:
                logger.debug(f"Setting state '{key}' = '{value}'")
                runtime.execute(f"{key} = {value}")

    if state is not None:
        register_state(sanitize_python(state))

    return runtime


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


def parse_file(runtime, filename) -> dict:
    with open(filename, mode="r") as f:
        theme = f.read()
    return to_dict(runtime.execute(theme))


def parse_lua(runtime, lua) -> dict:
    return to_dict(runtime.execute(lua))
