from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Type, TypeVar

T = TypeVar("T", bound="Color")


class Color(ABC):
    @property
    @abstractmethod
    def color(self) -> Any:
        pass

    @abstractmethod
    def cast(self, _type: Type[T]) -> T:
        pass

    @abstractmethod
    def normalized(self) -> Color:
        pass

    @abstractmethod
    def normalize(self) -> Color:
        pass

    @abstractmethod
    def denormalized(self) -> Color:
        pass

    @abstractmethod
    def denormalize(self) -> Color:
        pass

    @abstractmethod
    def darkened(self, amount: float) -> Color:
        pass

    @abstractmethod
    def darken(self, amount: float) -> Color:
        pass

    @abstractmethod
    def lightened(self, amount: float) -> Color:
        pass

    @abstractmethod
    def lighten(self, amount: float) -> Color:
        pass

    @abstractmethod
    def saturate(self, amount: float) -> Color:
        pass

    @abstractmethod
    def saturated(self, amount: float) -> Color:
        pass

    @abstractmethod
    def desaturate(self, amount: float) -> Color:
        pass

    @abstractmethod
    def desaturated(self, amount: float) -> Color:
        pass

    @abstractmethod
    def blend(self, color: Color, ratio: float = 0.5) -> Color:
        pass

    @abstractmethod
    def blended(self, color: Color, ratio: float = 0.5) -> Color:
        pass

    @abstractmethod
    def __str__(self) -> str:
        pass
