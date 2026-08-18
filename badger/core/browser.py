__all__ = [
    "connect_browser",
    "default_browser_path",
    "is_browser_running",
    "launch_edge",
    "record_session",
    "wait_for_browser",
]

import platform
import subprocess
import time
import urllib.error
import urllib.request
from collections.abc import Callable, Iterator
from contextlib import contextmanager, suppress
from datetime import datetime
from pathlib import Path, WindowsPath
from zoneinfo import ZoneInfo

from playwright.sync_api import Page, sync_playwright

from badger import __project__, get_cache_home, get_state_home
from badger.core.log import Level


def default_browser_path() -> str:
    if platform.system() == "Windows":
        return str(
            WindowsPath("c:/")
            / "Program Files (x86)"
            / "Microsoft"
            / "Edge"
            / "Application"
            / "msedge.exe"
        )
    if platform.system() == "Linux":
        return "microsoft-edge-stable"
    if platform.system() == "Darwin":
        return str(
            Path("/")
            / "Applications"
            / "Microsoft Edge.app"
            / "Contents"
            / "MacOS"
            / "Microsoft Edge"
        )
    return ""


def launch_edge(
    log_message: Callable[[str, Level], None], port: int = 9222, browser_path: str | None = None
) -> dict:
    data_path = get_cache_home() / "remote-debug-profile"
    edge_path = (browser_path or "").strip() or default_browser_path()
    if not edge_path:
        return {"running": False, "message": f"Unsupported platform: {platform.system()}"}
    cmd = [edge_path, f"--remote-debugging-port={port}", f"--user-data-dir={data_path}"]

    try:
        log_message("Starting Edge with CDP...", Level.DEBUG)
        subprocess.Popen(cmd)  # noqa: S603
        return {"running": True, "message": "Edge launched successfully"}
    except FileNotFoundError as err:
        return {"running": False, "message": str(err)}


def is_browser_running(port: int = 9222) -> bool:
    try:
        with urllib.request.urlopen(f"http://localhost:{port}/json/version", timeout=1):
            return True
    except (urllib.error.URLError, TimeoutError, OSError):
        return False


def wait_for_browser(port: int = 9222, timeout: float = 30.0) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if is_browser_running(port):
            return True
        time.sleep(0.5)
    return False


@contextmanager
def connect_browser(port: int = 9222) -> Iterator[Page]:
    with sync_playwright() as playwright:
        browser = playwright.chromium.connect_over_cdp(f"http://localhost:{port}")
        page = next(iter(page for context in browser.contexts for page in context.pages), None)
        if not page:
            raise RuntimeError("No open pages found; navigate to the list first.")
        yield page


@contextmanager
def record_session(page: Page) -> Iterator[None]:
    context = page.context
    context.tracing.start(screenshots=True, snapshots=True, sources=True)
    try:
        yield
    finally:
        stamp = datetime.now(tz=ZoneInfo("Pacific/Auckland")).strftime("%Y%m%d-%H%M%S")
        with suppress(Exception):
            context.tracing.stop(path=get_state_home() / f"{__project__}_{stamp}.zip")
