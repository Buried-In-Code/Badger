import json
from datetime import datetime
from pathlib import Path

from badger.core.log import Level, Log, add_log, read_logs


def test_level_values() -> None:
    assert Level.DEBUG.value == "DEBUG"
    assert Level.INFO.value == "INFO"
    assert Level.WARN.value == "WARN"
    assert Level.ERROR.value == "ERROR"


def test_log_default_timestamp() -> None:
    log = Log(message="test")
    assert isinstance(log.timestamp, datetime)
    assert log.level == Level.INFO
    assert log.message == "test"


def test_log_custom_level() -> None:
    log = Log(level=Level.ERROR, message="error")
    assert log.level == Level.ERROR


def test_log_is_frozen() -> None:
    log = Log(message="frozen")
    try:
        log.message = "changed"
        raise AssertionError("should have raised")  # noqa: TRY301
    except Exception:  # noqa: S110, BLE001
        pass


def test_add_log_and_read_logs() -> None:
    log1 = Log(level=Level.INFO, message="first log")
    log2 = Log(level=Level.WARN, message="second log")
    add_log(log1)
    add_log(log2)

    logs = read_logs()
    assert len(logs) == 2
    assert logs[0].level == Level.INFO
    assert logs[0].message == "first log"
    assert logs[1].level == Level.WARN
    assert logs[1].message == "second log"


def test_read_logs_empty() -> None:
    assert read_logs() == []


def test_read_logs_ignores_empty_lines(monkeypatch, tmp_path: Path) -> None:  # noqa: ANN001
    logfile = tmp_path / "logs.jsonl"
    logfile.write_text(
        json.dumps({"timestamp": "2024-01-01T00:00:00", "level": "INFO", "message": "m"})
        + "\n\n\n"
        + json.dumps({"timestamp": "2024-01-01T00:00:01", "level": "DEBUG", "message": "n"})
        + "\n"
    )
    monkeypatch.setattr("badger.core.log.logfile", logfile)
    logs = read_logs()
    assert len(logs) == 2


def test_add_log_appends() -> None:
    log1 = Log(message="a")
    log2 = Log(message="b")
    add_log(log1)
    add_log(log2)
    assert len(read_logs()) == 2
