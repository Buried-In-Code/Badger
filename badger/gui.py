import threading
import tkinter as tk
from datetime import datetime
from enum import Enum, auto
from queue import Queue
from tkinter import ttk

from badger.core.browser import launch_chrome
from badger.core.tasks import APP_NAME, TASKS, Task, execute_tasks
from badger.severity import Severity


class State(Enum):
    IDLE = auto()
    BROWSER_LAUNCHING = auto()
    BROWSER_READY = auto()
    RUNNING = auto()
    COMPLETE = auto()

    def __str__(self) -> str:
        return self.name


class BadgerUI:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.state = State.IDLE
        self.browser_running = False
        self.running = False
        self.log_queue: Queue = Queue()

        self._setup_window()

        self._build_browser_control(self.root)

        middle = ttk.Frame(self.root)
        middle.pack(fill=tk.BOTH, expand=True, padx=5, pady=(5, 0))
        middle.pack_propagate(False)

        left = ttk.Frame(middle)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 2))
        self._build_task_selection(left)

        right = ttk.Frame(middle)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(2, 0))
        self._build_output_log(right)

        self._build_run_control(self.root)

        self._update_ui()

        self.root.after(100, self._process_log_queue)

    def _setup_window(self) -> None:
        self.root.title(APP_NAME)
        self.root.geometry("1000x500")
        self.root.minsize(1000, 500)

    def _build_browser_control(self, parent: tk.Widget) -> None:
        frame = tk.LabelFrame(parent, text="Browser Control", padx=5, pady=5)
        frame.pack(fill=tk.X, padx=5, pady=(5, 0))

        self.launch_btn = tk.Button(
            frame, text="Open Browser (Chrome)", command=self._on_launch_browser
        )
        self.launch_btn.pack(side=tk.LEFT, padx=5, pady=5)

        tk.Label(frame, text="Port:").pack(side=tk.LEFT, padx=(10, 2))
        self.port_var = tk.IntVar(value=9222)
        self.port_entry = ttk.Spinbox(
            frame, from_=1024, to=65535, textvariable=self.port_var, width=7
        )
        self.port_entry.pack(side=tk.LEFT, padx=(0, 15))

        self.browser_status = tk.Label(frame, text="Chrome: Not running")
        self.browser_status.pack(side=tk.LEFT, padx=15, pady=5)

    def _build_task_selection(self, parent: tk.Widget) -> None:
        frame = tk.LabelFrame(parent, text="Select Tasks to Run", padx=5, pady=5)
        frame.pack(fill=tk.BOTH, expand=True)

        btn_row = tk.Frame(frame)
        btn_row.pack(fill=tk.X, pady=(0, 5))
        self.select_all_btn = tk.Button(btn_row, text="Select All", command=self._on_select_all)
        self.select_all_btn.pack(side=tk.RIGHT, padx=2)
        self.clear_all_btn = tk.Button(btn_row, text="Clear All", command=self._on_clear_all)
        self.clear_all_btn.pack(side=tk.RIGHT, padx=2)

        canvas = tk.Canvas(frame, height=200, highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable = tk.Frame(canvas)

        scrollable.bind("<Configure>", lambda _: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        self.task_vars: list[tk.BooleanVar] = []
        self.task_checkbuttons: list[ttk.Checkbutton] = []
        for task in TASKS:
            var = tk.BooleanVar()
            self.task_vars.append(var)
            cb = ttk.Checkbutton(scrollable, text=task.name, variable=var, command=self._update_ui)
            cb.pack(anchor=tk.W, padx=5, pady=2)
            self.task_checkbuttons.append(cb)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def _build_run_control(self, parent: tk.Widget) -> None:
        frame = tk.Frame(parent, bd=1, relief=tk.SUNKEN, padx=5, pady=5)
        frame.pack(fill=tk.X, padx=5, pady=(0, 5))

        center = tk.Frame(frame)
        center.pack(side=tk.LEFT, expand=True)

        self.run_btn = tk.Button(center, text="Start", command=self._on_run)
        self.run_btn.pack(side=tk.LEFT, padx=5, pady=5)

        self.stop_btn = tk.Button(center, text="Stop", command=self._on_stop)
        self.stop_btn.pack(side=tk.LEFT, padx=5, pady=5)

        self.run_status = tk.Label(frame, text="Ready")
        self.run_status.pack(side=tk.RIGHT, padx=15, pady=5)

    def _build_output_log(self, parent: tk.Widget) -> None:
        frame = tk.LabelFrame(parent, text="Activity Log", padx=5, pady=5)
        frame.pack(fill=tk.BOTH, expand=True)

        self.output_text = tk.Text(frame, wrap=tk.WORD, state=tk.DISABLED, height=10)
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.output_text.yview)
        self.output_text.configure(yscrollcommand=scrollbar.set)
        self.output_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def _update_ui(self) -> None:
        is_running = self.state is State.RUNNING
        is_launching = self.state is State.BROWSER_LAUNCHING
        any_selected = any(v.get() for v in self.task_vars)
        can_run = self.browser_running and any_selected and not is_running

        launch_disabled = self.browser_running or is_launching
        self.launch_btn.configure(state=tk.DISABLED if launch_disabled else tk.NORMAL)
        self.port_entry.configure(state=tk.DISABLED if launch_disabled else tk.NORMAL)

        task_sel_enabled = self.browser_running and not is_launching and not is_running
        cb_state = tk.NORMAL if task_sel_enabled else tk.DISABLED
        for cb in self.task_checkbuttons:
            cb.configure(state=cb_state)
        self.select_all_btn.configure(state=cb_state)
        self.clear_all_btn.configure(state=cb_state)

        self.run_btn.configure(
            state=tk.NORMAL if can_run else tk.DISABLED,
            text="Start" if not is_running else "Running...",
        )

        self.stop_btn.configure(state=tk.NORMAL if is_running else tk.DISABLED)

        if self.browser_running:
            browser_text = "Chrome: Ready"
        elif is_launching:
            browser_text = "Chrome: Launching..."
        else:
            browser_text = "Chrome: Not running"
        self.browser_status.configure(text=browser_text)

        run_text = {State.RUNNING: "Running...", State.COMPLETE: "Complete"}.get(self.state, "")
        self.run_status.configure(text=run_text)

    def _log(self, step: str, message: str, severity: Severity = Severity.INFO) -> None:
        ts = datetime.now().strftime("%H:%M:%S")
        line = f"[{ts}] [{severity:<5}] [{step}] {message}\n"
        self.output_text.configure(state=tk.NORMAL)
        self.output_text.insert(tk.END, line)
        self.output_text.see(tk.END)
        self.output_text.configure(state=tk.DISABLED)

    def _process_log_queue(self) -> None:
        while not self.log_queue.empty():
            self._log(*self.log_queue.get_nowait())
        self.root.after(100, self._process_log_queue)

    def _on_launch_browser(self) -> None:
        self.state = State.BROWSER_LAUNCHING
        self._update_ui()
        port = self.port_var.get()
        self._log("BROWSER", f"Launching Chrome with remote debugging on port {port}...")
        threading.Thread(target=self._launch_browser_thread, args=(port,), daemon=True).start()

    def _launch_browser_thread(self, port: int) -> None:
        def display(msg: str, severity: Severity) -> None:
            self.log_queue.put(("BROWSER", msg, severity))

        result = launch_chrome(display=display, port=port)
        self.browser_running = result["running"]
        self.state = State.BROWSER_READY
        self.root.after(0, self._on_browser_ready)

    def _on_browser_ready(self) -> None:
        self._log("BROWSER", "Chrome launched successfully with remote debugging enabled.")
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
        if not selected or not self.browser_running:
            return
        self.state = State.RUNNING
        self.running = True
        self._update_ui()
        self._log("RUN", f"Starting {len(selected)} task(s)...")
        threading.Thread(target=self._run_tasks, args=(selected,), daemon=True).start()

    def _run_tasks(self, selected: list[Task]) -> None:
        def progress(msg: str) -> None:
            self.log_queue.put(("RUN", msg))

        execute_tasks(selected, on_progress=progress, is_cancelled=lambda: not self.running)
        if self.running:
            self.log_queue.put(("RUN", "All tasks finished."))
        self.running = False
        self.root.after(0, self._on_run_complete)

    def _on_run_complete(self) -> None:
        self.state = State.COMPLETE
        self._update_ui()

    def _on_stop(self) -> None:
        self.running = False
        self._log("RUN", "Stopped by user.", Severity.WARN)
        self.state = State.COMPLETE
        self._update_ui()


def main() -> None:
    root = tk.Tk()
    BadgerUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
