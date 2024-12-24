from collections.abc import Iterable
from typing import Type


def check_types(iterable: Iterable, _type: Type) -> bool:
    return all([type(val) is _type for val in iterable])
