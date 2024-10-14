from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Type, TypeVar

T = TypeVar("T", bound="_ColorImpl")


class _ColorImpl(ABC):
    @abstractmethod
    def cast(self, target_type: Type[T]) -> T:
        """Returns this color converted to another color type.

        Args:
            target_type: The target color to convert to.

        Returns:
            The converted color.

        Raises:
            TypeError: If the target type doesn't have a conversion method.
        """
        pass

    @abstractmethod
    def __str__(self) -> str:
        pass
