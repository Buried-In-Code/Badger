__all__ = ["Level", "Log", "add_log", "read_logs"]

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from badger import get_state_root

logfile = get_state_root() / "log.jsonl"


class Level(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"


@dataclass(kw_only=True, frozen=True)
class Log:
    timestamp: datetime = field(default_factory=datetime.now)
    level: Level = Level.INFO
    message: str


def add_log(log: Log) -> None:
    entry = {
        "timestamp": log.timestamp.isoformat(),
        "level": log.level.value,
        "message": log.message,
    }
    with logfile.open("a") as stream:
        stream.write(json.dumps(entry) + "\n")


def read_logs() -> list[Log]:
    if not logfile.exists():
        return []
    with logfile.open() as stream:
        logs = []
        for line in stream:
            line = line.strip()
            if line:
                data = json.loads(line)
                logs.append(
                    Log(
                        timestamp=datetime.fromisoformat(data["timestamp"]),
                        level=Level(data["level"]),
                        message=data["message"],
                    )
                )
        return logs
