from collections.abc import Generator
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def _isolate_logfile(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Generator[Path]:
    logfile = tmp_path / "logs.jsonl"
    monkeypatch.setattr("badger.core.log.logfile", logfile)
    return logfile
