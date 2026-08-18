__all__ = [
    "__project__",
    "__version__",
    "get_cache_home",
    "get_config_home",
    "get_data_home",
    "get_state_home",
]
__version__ = "2026.1.0"
__project__ = "badger"

from pathlib import Path


def get_cache_home() -> Path:
    folder = Path.home() / f".{__project__}" / "cache"
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def get_config_home() -> Path:
    folder = Path.home() / f".{__project__}" / "config"
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def get_data_home() -> Path:
    folder = Path.home() / f".{__project__}" / "data"
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def get_state_home() -> Path:
    folder = Path.home() / f".{__project__}" / "state"
    folder.mkdir(parents=True, exist_ok=True)
    return folder
