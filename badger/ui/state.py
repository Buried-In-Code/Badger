__all__ = ["POLL_INTERVAL_SECS", "BrowserState", "RunState"]

from enum import Enum, auto


class BrowserState(Enum):
    CLOSED = auto()
    LAUNCHING = auto()
    OPEN = auto()
    FAILED = auto()


class RunState(Enum):
    IDLE = auto()
    RUNNING = auto()
    COMPLETE = auto()


POLL_INTERVAL_SECS = 2.0
