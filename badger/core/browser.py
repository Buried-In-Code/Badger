__all__ = ["launch_chrome"]

import platform
import subprocess
from collections.abc import Callable
from pathlib import Path, WindowsPath

from badger.severity import Severity


def launch_chrome(display: Callable[[str, Severity], None], port: int = 9222) -> dict:
    if platform.system() == "Windows":
        chrome_path = (
            WindowsPath("c:/")
            / "Program Files"
            / "Google"
            / "Chrome"
            / "Application"
            / "chrome.exe"
        )
        data_path = r"%LOCALAPPDATA%\Google\Chrome\RemoteDebugProfile"
        cmd = [chrome_path, f"--remote-debugging-port={port}", f"--user-data-dir={data_path}"]
    elif platform.system() == "Linux":
        chrome_path = "google-chrome-stable"
        data_path = Path.home() / ".cache" / "google-chrome" / "remote-debug-profile"
        data_path.parent.mkdir(exist_ok=True, parents=True)
        cmd = [chrome_path, f"--remote-debugging-port={port}", f"--user-data-dir={data_path}"]
    else:
        return {"running": False, "message": f"Unsupported platform: {platform.system()}"}

    try:
        display("Starting Chrome with CDP...", Severity.DEBUG)
        subprocess.Popen(cmd)  # noqa: S603
        return {"running": True, "message": "Chrome launched successfully"}
    except FileNotFoundError as err:
        return {"running": False, "message": str(err)}
