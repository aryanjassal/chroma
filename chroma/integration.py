import tempfile
from abc import ABC, abstractmethod
from typing import Type


class Integration(ABC):
    def __init__(self, group, meta, data):
        super().__init__()
        self.group = group
        self.meta = meta
        self.data = data

    def tempdir_create(self) -> str:
        self.__tempdir = tempfile.TemporaryDirectory()
        return self.__tempdir.name

    def tempdir_cleanup(self) -> None:
        self.__tempdir.cleanup()

    @abstractmethod
    def apply(self) -> None:
        pass


IntegrationT = Type[Integration]
