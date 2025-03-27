import shutil
import subprocess
from collections.abc import Iterable
from pathlib import Path
from typing import Literal, NoReturn, Optional

from lupa import lua_type

from chroma.exceptions import ProgramNotFoundException
from chroma.logger import Logger
from chroma.types import Number

logger = Logger.get_logger()


# TODO: fix lint
def to_dict(table) -> dict:
    """Recursively converts lua tables to python dicts"""

    def convert_dict(t):
        result = dict()
        for k, v in t.items():
            if lua_type(v) == "table" or type(v) is dict:
                v = convert_dict(v)
            result[k] = v

        return result

    # If the dictionary is of type { 1: <foo>, 2: <bar> }, then it is an
    # array. It should be converted to [<foo>, <bar>] in python.
    def convert_list(d):
        if all(isinstance(k, int) for k in d.keys()):
            sorted_keys = sorted(d.keys())
            # Make the keys 1-indexed
            if sorted_keys == list(range(1, len(sorted_keys) + 1)):
                result = []
                for i in sorted_keys:
                    value = d[i]
                    if isinstance(value, dict):
                        value = convert_list(value)
                    result.append(value)
                return result
        return {
            k: (convert_list(v) if isinstance(v, dict) else v) for k, v in d.items()
        }

    return convert_list(convert_dict(table))


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


def clamp(x: Number, _min: Number, _max: Number):
    return max(_min, min(x, _max))


def check_program(
    program: str,
    action: Literal["WARN"] | Literal["NOOP"] | Literal["EXIT"] = "WARN",
) -> bool:
    if shutil.which(program) is None:
        if action == "WARN":
            logger.warn(
                f"{program} was not found on your system. You can disable "
                "the integration by assigning the table to nil in the overrides."
            )
            return False
        if action == "EXIT":
            raise ProgramNotFoundException(
                f"{program} was not found on your system. You must disable "
                "the integration by assigning the table to nil in the overrides."
            )
        return False
    return True


def backup(path: Path) -> bool:
    backup_name = f"{path.name}.bak"
    backup_path = path.parent / backup_name

    if backup_path.is_file():
        return False
    else:
        shutil.move(path, backup_path)
        return True


def flatten(values: Iterable, result=[]):
    for v in values:
        if isinstance(v, Iterable):
            flatten(v, result)
        else:
            result.append(v)
    return result


def closest(values: Iterable[int], target: int):
    return min(values, key=lambda x: abs(x - target))
