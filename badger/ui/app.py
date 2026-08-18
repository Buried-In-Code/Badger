__all__ = ["BadgerUI"]

import threading
import time
import tkinter as tk
from queue import Queue
from tkinter import ttk

from badger import __project__, __version__
from badger.core.browser import (
    connect_browser,
    is_browser_running,
    launch_edge,
    record_session,
    wait_for_browser,
)
from badger.core.log import Level, Log, add_log
from badger.core.tasks import TASKS, Task, execute_tasks
from badger.ui.browser_panel import BrowserPanel
from badger.ui.log_panel import LogPanel
from badger.ui.run_panel import RunPanel
from badger.ui.state import POLL_INTERVAL_SECS, BrowserState, RunState
from badger.ui.task_panel import TaskPanel


class BadgerUI:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.browser_state = BrowserState.CLOSED
        self.run_state = RunState.IDLE
        self.log_queue: Queue[Log] = Queue()
        self._poll_port = 9222

        self._setup_window()
        self._build_ui()
        self._update_ui()
        self.root.after(100, self._process_log_queue)
        threading.Thread(target=self._poll_browser, daemon=True).start()

    def _setup_window(self) -> None:
        self.root.title(f"{__project__} v{__version__}")
        self.root.geometry("1000x540")
        self.root.minsize(1000, 540)

    def _build_ui(self) -> None:
        main = ttk.Frame(self.root, padding=8)
        main.pack(fill=tk.BOTH, expand=True)

        self.browser_panel = BrowserPanel(
            main,
            on_launch=self._on_launch_browser,
            on_port_change=self._on_port_change,
            on_debug_visibility_change=self._on_toggle_debug,
        )
        self.browser_panel.pack(fill=tk.X)

        middle = ttk.Frame(main)
        middle.pack(fill=tk.BOTH, expand=True, pady=(8, 0))

        left = ttk.Frame(middle)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 4))
        self.task_panel = TaskPanel(left, tasks=TASKS, on_selection_change=self._update_ui)
        self.task_panel.pack(fill=tk.BOTH, expand=True)

        right = ttk.Frame(middle)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(4, 0))
        self.log_panel = LogPanel(right)
        self.log_panel.pack(fill=tk.BOTH, expand=True)

        self.run_panel = RunPanel(main, on_run=self._on_run, on_stop=self._on_stop)
        self.run_panel.pack(fill=tk.X, pady=(8, 0))

    def _on_port_change(self, port: int) -> None:
        self._poll_port = port

    def _on_toggle_debug(self, visible: bool) -> None:
        self.log_panel.set_debug_visible(visible=visible)

    def _update_ui(self) -> None:
        browser_open = self.browser_state is BrowserState.OPEN
        is_running = self.run_state is RunState.RUNNING

        self.browser_panel.set_state(self.browser_state)
        self.task_panel.set_enabled(enabled=browser_open and not is_running)
        self.run_panel.set_state(
            self.run_state,
            can_start=browser_open and self.task_panel.has_selection and not is_running,
        )

    def _queue_log(self, step: str, message: str, level: Level = Level.INFO) -> None:
        log = Log(level=level, message=f"[{step}] {message}")
        add_log(log)
        self.log_queue.put(log)

    def _process_log_queue(self) -> None:
        while not self.log_queue.empty():
            self.log_panel.append(self.log_queue.get_nowait())
        self.root.after(100, self._process_log_queue)

    def _on_launch_browser(self) -> None:
        self.browser_state = BrowserState.LAUNCHING
        self._update_ui()
        port = self.browser_panel.port
        browser_path = self.browser_panel.browser_path
        self._queue_log("BROWSER", f"Opening Edge on port {port}")
        threading.Thread(
            target=self._launch_browser_thread, args=(port, browser_path), daemon=True
        ).start()

    def _launch_browser_thread(self, port: int, browser_path: str) -> None:
        def log_message(msg: str, level: Level) -> None:
            self._queue_log("BROWSER", msg, level)

        result = launch_edge(log_message=log_message, port=port, browser_path=browser_path)
        if not result.get("running", False):
            reason = result.get("message", "unknown error")
        elif wait_for_browser(port):
            self.root.after(0, lambda: self._on_launch_finished(success=True, reason=""))
            return
        else:
            reason = f"no CDP response on port {port} after 30s"
        self.root.after(0, lambda: self._on_launch_finished(success=False, reason=reason))

    def _on_launch_finished(self, success: bool, reason: str) -> None:
        if success:
            self.browser_state = BrowserState.OPEN
            self._queue_log("BROWSER", "Edge is ready.")
        else:
            self.browser_state = BrowserState.FAILED
            self._queue_log("BROWSER", f"Edge failed to launch: {reason}", Level.ERROR)
        self._update_ui()

    def _poll_browser(self) -> None:
        while True:
            running = is_browser_running(self._poll_port)
            self.root.after(0, self._on_browser_poll, running)
            time.sleep(POLL_INTERVAL_SECS)

    def _on_browser_poll(self, running: bool) -> None:
        if self.browser_state is BrowserState.LAUNCHING:
            return
        if running and self.browser_state is not BrowserState.OPEN:
            self.browser_state = BrowserState.OPEN
            self._queue_log("BROWSER", f"Browser detected on port {self._poll_port}.")
        elif not running and self.browser_state is BrowserState.OPEN:
            self.browser_state = BrowserState.CLOSED
            self._queue_log("BROWSER", "Browser closed.", Level.WARN)
            if self.run_state is RunState.RUNNING:
                self.run_state = RunState.COMPLETE
                self._queue_log(
                    "RUN",
                    "Browser closed mid-run; cancelling remaining entries. "
                    "Re-open Edge, navigate back to the list and start again.",
                    Level.ERROR,
                )
        else:
            return
        self._update_ui()

    def _on_run(self) -> None:
        selected = self.task_panel.selected_tasks()
        if not selected or self.browser_state is not BrowserState.OPEN:
            return
        if self.run_state is RunState.RUNNING:
            return
        self.run_state = RunState.RUNNING
        self._update_ui()
        port = self.browser_panel.port
        self._queue_log("RUN", f"Starting {len(selected)} task(s)")
        threading.Thread(target=self._run_tasks, args=(selected, port), daemon=True).start()

    def _run_tasks(self, selected: list[Task], port: int) -> None:
        def progress(msg: str) -> None:
            self._queue_log("RUN", msg)

        try:
            with connect_browser(port) as list_page:
                self._queue_log("RUN", f"Attached to {list_page.url}", Level.DEBUG)
                with record_session(list_page):
                    results = execute_tasks(
                        list_page,
                        selected,
                        log=progress,
                        is_cancelled=lambda: self.run_state is not RunState.RUNNING,
                    )
            failed = sum(1 for result in results if not result.success)
            self._queue_log(
                "RUN",
                f"Finished: {len(results) - failed} succeeded, {failed} failed.",
                Level.WARN if failed else Level.INFO,
            )
        except Exception as exc:  # noqa: BLE001
            self._queue_log("RUN", f"Unexpected error: {exc}", Level.ERROR)
        finally:
            self.root.after(0, self._on_run_complete)

    def _on_run_complete(self) -> None:
        if self.run_state is RunState.RUNNING:
            self.run_state = RunState.COMPLETE
        self._update_ui()

    def _on_stop(self) -> None:
        self.run_state = RunState.COMPLETE
        self._queue_log("RUN", "Stopped by user.", Level.WARN)
        self._update_ui()
