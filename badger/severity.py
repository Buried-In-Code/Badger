__all__ = ["Severity"]

from enum import Enum, auto


class Severity(Enum):
    DEBUG = auto()
    INFO = auto()
    WARN = auto()
    ERROR = auto()

    def __str__(self) -> str:
        return self.name
