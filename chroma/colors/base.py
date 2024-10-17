from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Type, TypeVar

T = TypeVar("T", bound="_ColorImpl")


class _ColorImpl(ABC):
    @abstractmethod
    def cast(self, target_type: Type[T]) -> T:
        pass

    @abstractmethod
    def __str__(self) -> str:
        pass
