import threading
import tkinter as tk
from enum import Enum, auto
from queue import Queue
from tkinter import ttk

from badger.core.browser import launch_chrome
from badger.core.log import Level, Log, add_log, read_logs
from badger.core.tasks import APP_NAME, TASKS, Task, execute_tasks


class State(Enum):
    IDLE = auto()
    BROWSER_LAUNCHING = auto()
    BROWSER_READY = auto()
    RUNNING = auto()
    COMPLETE = auto()
    BROWSER_ERROR = auto()


class BadgerUI:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.state = State.IDLE
        self.log_queue: Queue[Log] = Queue()

        self._setup_window()
        self._build_ui()
        self._update_ui()
        self.root.after(100, self._process_log_queue)

    def _setup_window(self) -> None:
        self.root.title(APP_NAME)
        self.root.geometry("1000x540")
        self.root.minsize(1000, 540)

    def _build_ui(self) -> None:
        main = ttk.Frame(self.root, padding=8)
        main.pack(fill=tk.BOTH, expand=True)

        self._build_browser_section(main)

        middle = ttk.Frame(main)
        middle.pack(fill=tk.BOTH, expand=True, pady=(8, 0))

        left = ttk.Frame(middle)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 4))
        self._build_task_section(left)

        right = ttk.Frame(middle)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(4, 0))
        self._build_log_section(right)

        self._build_run_section(main)

    def _build_browser_section(self, parent: tk.Widget) -> None:
        frame = ttk.LabelFrame(parent, text="Step 1  -  Open Browser")
        frame.pack(fill=tk.X)

        row = ttk.Frame(frame)
        row.pack(fill=tk.X, padx=6, pady=6)

        self.launch_btn = ttk.Button(row, text="Open Chrome", command=self._on_launch_browser)
        self.launch_btn.pack(side=tk.LEFT, padx=(0, 16))

        self.browser_status_lbl = ttk.Label(row, text="Not running")
        self.browser_status_lbl.pack(side=tk.LEFT)

        self.adv_btn = ttk.Button(row, text="Advanced", command=self._toggle_advanced)
        self.adv_btn.pack(side=tk.RIGHT)

        self._advanced_open = False
        self._advanced_frame = ttk.Frame(frame)

        ttk.Label(self._advanced_frame, text="Debug port:").pack(side=tk.LEFT, padx=(6, 4))
        self.port_var = tk.IntVar(value=9222)
        self.port_entry = ttk.Spinbox(
            self._advanced_frame, from_=1024, to=65535, textvariable=self.port_var, width=7
        )
        self.port_entry.pack(side=tk.LEFT)

        ttk.Separator(self._advanced_frame, orient=tk.VERTICAL).pack(
            side=tk.LEFT, fill=tk.Y, padx=12, pady=2
        )

        self.show_debug_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            self._advanced_frame,
            text="Show debug output",
            variable=self.show_debug_var,
            command=self._on_toggle_debug,
        ).pack(side=tk.LEFT)

    def _toggle_advanced(self) -> None:
        self._advanced_open = not self._advanced_open
        if self._advanced_open:
            self._advanced_frame.pack(fill=tk.X, padx=6, pady=(0, 6))
        else:
            self._advanced_frame.pack_forget()

    def _on_toggle_debug(self) -> None:
        self.log_text.tag_configure(Level.DEBUG.value, elide=not self.show_debug_var.get())

    def _build_task_section(self, parent: tk.Widget) -> None:
        frame = ttk.LabelFrame(parent, text="Step 2  -  Choose Tasks")
        frame.pack(fill=tk.BOTH, expand=True)

        btn_row = ttk.Frame(frame)
        btn_row.pack(fill=tk.X, padx=6, pady=(6, 2))
        self.select_all_btn = ttk.Button(btn_row, text="Select All", command=self._on_select_all)
        self.select_all_btn.pack(side=tk.LEFT, padx=(0, 4))
        self.clear_all_btn = ttk.Button(btn_row, text="Clear All", command=self._on_clear_all)
        self.clear_all_btn.pack(side=tk.LEFT)

        container = ttk.Frame(frame)
        container.pack(fill=tk.BOTH, expand=True, padx=6, pady=(0, 6))

        canvas = tk.Canvas(container, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient=tk.VERTICAL, command=canvas.yview)
        scrollable = ttk.Frame(canvas)

        scrollable.bind("<Configure>", lambda _: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        self.task_vars: list[tk.BooleanVar] = []
        self.task_checkbuttons: list[ttk.Checkbutton] = []
        for task in TASKS:
            var = tk.BooleanVar()
            self.task_vars.append(var)
            cb = ttk.Checkbutton(scrollable, text=task.name, variable=var, command=self._update_ui)
            cb.pack(anchor=tk.W, pady=2)
            self.task_checkbuttons.append(cb)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def _build_run_section(self, parent: tk.Widget) -> None:
        frame = ttk.LabelFrame(parent, text="Step 3  -  Run")
        frame.pack(fill=tk.X, pady=(8, 0))

        row = ttk.Frame(frame)
        row.pack(fill=tk.X, padx=6, pady=6)

        self.run_btn = ttk.Button(row, text="Start", command=self._on_run)
        self.run_btn.pack(side=tk.LEFT, padx=(0, 8))

        self.stop_btn = ttk.Button(row, text="Stop", command=self._on_stop)
        self.stop_btn.pack(side=tk.LEFT)

        self.run_status_lbl = ttk.Label(row, text="")
        self.run_status_lbl.pack(side=tk.RIGHT, padx=8)

    def _build_log_section(self, parent: tk.Widget) -> None:
        frame = ttk.LabelFrame(parent, text="Activity Log")
        frame.pack(fill=tk.BOTH, expand=True)

        container = ttk.Frame(frame)
        container.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        self.log_text = tk.Text(
            container, wrap=tk.WORD, state=tk.DISABLED, bg="#1e1e1e", fg="#cccccc", relief=tk.FLAT
        )
        scrollbar = ttk.Scrollbar(container, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)

        self.log_text.tag_configure("ts", foreground="#555555")
        self.log_text.tag_configure(Level.DEBUG.value, foreground="#888888", elide=True)
        self.log_text.tag_configure(Level.INFO.value, foreground="#9cdcfe")
        self.log_text.tag_configure(Level.WARN.value, foreground="#dcdcaa")
        self.log_text.tag_configure(Level.ERROR.value, foreground="#f44747")

        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def _update_ui(self) -> None:
        is_launching = self.state is State.BROWSER_LAUNCHING
        browser_up = self.state in (State.BROWSER_READY, State.COMPLETE)
        is_running = self.state is State.RUNNING
        any_selected = any(v.get() for v in self.task_vars)

        launch_locked = browser_up or is_launching
        self.launch_btn.configure(state=tk.DISABLED if launch_locked else tk.NORMAL)
        self.port_entry.configure(state=tk.DISABLED if launch_locked else tk.NORMAL)

        if browser_up:
            self.browser_status_lbl.configure(text="Ready", foreground="#4caf50")
        elif is_launching:
            self.browser_status_lbl.configure(text="Launching", foreground="#ff9800")
        elif self.state is State.BROWSER_ERROR:
            self.browser_status_lbl.configure(text="Failed", foreground="#f44747")
        else:
            self.browser_status_lbl.configure(text="Not running", foreground="#9e9e9e")

        task_state = tk.NORMAL if (browser_up and not is_running) else tk.DISABLED
        for cb in self.task_checkbuttons:
            cb.configure(state=task_state)
        self.select_all_btn.configure(state=task_state)
        self.clear_all_btn.configure(state=task_state)

        self.run_btn.configure(
            state=tk.NORMAL if (browser_up and any_selected and not is_running) else tk.DISABLED,
            text="Running" if is_running else "Start",
        )
        self.stop_btn.configure(state=tk.NORMAL if is_running else tk.DISABLED)
        self.run_status_lbl.configure(
            text={State.RUNNING: "Running", State.COMPLETE: "Complete"}.get(self.state, "")
        )

    def _log(self, log: Log) -> None:
        tag = log.level.value
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"[{log.timestamp.isoformat()}] ", ("ts", tag))
        self.log_text.insert(tk.END, f"[{tag:<5}] {log.message}\n", tag)
        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)

    def _queue_log(self, step: str, message: str, level: Level = Level.INFO) -> None:
        log = Log(level=level, message=f"[{step}] {message}")
        add_log(log)
        self.log_queue.put(log)

    def _process_log_queue(self) -> None:
        while not self.log_queue.empty():
            self._log(self.log_queue.get_nowait())
        self.root.after(100, self._process_log_queue)

    def _on_launch_browser(self) -> None:
        self.state = State.BROWSER_LAUNCHING
        self._update_ui()
        port = self.port_var.get()
        self._queue_log("BROWSER", f"Opening Chrome on port {port}")
        threading.Thread(target=self._launch_browser_thread, args=(port,), daemon=True).start()

    def _launch_browser_thread(self, port: int) -> None:
        def log_message(msg: str, level: Level) -> None:
            self._queue_log("BROWSER", msg, level)

        result = launch_chrome(log_message=log_message, port=port)
        success = result.get("running", False)
        self.state = State.BROWSER_READY if success else State.BROWSER_ERROR
        self.root.after(0, self._on_browser_ready, success)

    def _on_browser_ready(self, success: bool = True) -> None:
        if success:
            self._queue_log("BROWSER", "Chrome is ready.")
        else:
            self._queue_log("BROWSER", "Chrome failed to launch.", Level.ERROR)
        self._update_ui()

    def _on_select_all(self) -> None:
        for v in self.task_vars:
            v.set(True)
        self._update_ui()

    def _on_clear_all(self) -> None:
        for v in self.task_vars:
            v.set(False)
        self._update_ui()

    def _on_run(self) -> None:
        selected = [t for t, v in zip(TASKS, self.task_vars, strict=False) if v.get()]
        if not selected or self.state not in (State.BROWSER_READY, State.COMPLETE):
            return
        self.state = State.RUNNING
        self._update_ui()
        self._queue_log("RUN", f"Starting {len(selected)} task(s)")
        threading.Thread(target=self._run_tasks, args=(selected,), daemon=True).start()

    def _run_tasks(self, selected: list[Task]) -> None:
        def progress(msg: str) -> None:
            self._queue_log("RUN", msg)

        try:
            execute_tasks(
                selected, on_progress=progress, is_cancelled=lambda: self.state is not State.RUNNING
            )
            if self.state is State.RUNNING:
                self._queue_log("RUN", "All tasks finished.")
        except Exception as exc:  # noqa: BLE001
            self._queue_log("RUN", f"Unexpected error: {exc}", Level.ERROR)
        finally:
            self.root.after(0, self._on_run_complete)

    def _on_run_complete(self) -> None:
        if self.state is State.RUNNING:
            self.state = State.COMPLETE
        self._update_ui()

    def _on_stop(self) -> None:
        self.state = State.COMPLETE
        self._queue_log("RUN", "Stopped by user.", Level.WARN)
        self._update_ui()


def main() -> None:
    root = tk.Tk()
    ui = BadgerUI(root)
    for log in read_logs():
        ui.log_queue.put(log)
    root.mainloop()


if __name__ == "__main__":
    main()
