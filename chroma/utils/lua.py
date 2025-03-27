from lupa import LuaRuntime

from chroma.colors.methods import blend, darken, desaturate, lighten, saturate
from chroma.logger import Logger

from .paths import cache_dir, chroma_dir
from .tools import to_dict

DEFAULT_STATE: dict = {
    "use_generated": True,
    "__darken": darken,
    "__lighten": lighten,
    "__saturate": saturate,
    "__desaturate": desaturate,
    "__blend": blend,
}

logger = Logger.get_logger()


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
                runtime.globals()[key] = value  # pyright: ignore
            else:
                logger.debug(f"Setting state '{key}' = '{value}'")
                runtime.execute(f"{key} = {value}")

    if state is not None:
        register_state(sanitize_python(state))

    return runtime


def parse_lua(runtime, lua) -> dict:
    return to_dict(runtime.execute(lua))
