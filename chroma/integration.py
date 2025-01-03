from abc import ABC, abstractmethod
from typing import Type


class Integration(ABC):
    def __init__(self, group, meta, data):
        super().__init__()
        self.group = group
        self.meta = meta
        self.data = data

    @abstractmethod
    def apply(self) -> None:
        pass


IntegrationT = Type[Integration]
