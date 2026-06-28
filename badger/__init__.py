__all__ = ["__version__", "get_cache_root", "get_config_root", "get_data_root", "get_state_root"]
__version__ = "2026.1.0"
__project__ = "badger"

import os
import platform
from pathlib import Path


def get_cache_root() -> Path:
    if platform.system() == "Windows":
        folder = Path.home() / f".{__project__}"
    else:
        cache_home = os.getenv("XDG_CACHE_HOME", default=str(Path.home() / ".cache"))
        folder = Path(cache_home).resolve() / __project__
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def get_config_root() -> Path:
    if platform.system() == "Windows":
        folder = Path.home() / f".{__project__}"
    else:
        config_home = os.getenv("XDG_CONFIG_HOME", default=str(Path.home() / ".config"))
        folder = Path(config_home).resolve() / __project__
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def get_data_root() -> Path:
    if platform.system() == "Windows":
        folder = Path.home() / f".{__project__}"
    else:
        data_home = os.getenv("XDG_DATA_HOME", default=str(Path.home() / ".local" / "data"))
        folder = Path(data_home).resolve() / __project__
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def get_state_root() -> Path:
    if platform.system() == "Windows":
        folder = Path.home() / f".{__project__}"
    else:
        state_home = os.getenv("XDG_STATE_HOME", default=str(Path.home() / ".local" / "state"))
        folder = Path(state_home).resolve() / __project__
    folder.mkdir(parents=True, exist_ok=True)
    return folder
