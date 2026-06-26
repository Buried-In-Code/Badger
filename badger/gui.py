import queue
import threading
import tkinter as tk
from datetime import datetime
from tkinter import ttk

from badger.core.browser import launch_chrome
from badger.core.tasks import APP_NAME, TASKS, execute_tasks


class TaskAutomationGUI:
    def __init__(self, root) -> None:
        self.root = root
        self.state = "IDLE"
        self.browser_running = False
        self.executing = False
        self.log_queue = queue.Queue()

        self.task_vars = []
        self.task_checkbuttons = []

        self._setup_window()
        self._build_header()
        self._build_browser_control()
        self._build_separator()
        self._build_task_selection()
        self._build_execution_control()
        self._build_output_log()
        self._build_status_bar()
        self._update_ui()

        self.root.after(100, self._process_log_queue)

    def _setup_window(self) -> None:
        self.root.title(APP_NAME)
        self.root.geometry("900x700")
        self.root.minsize(600, 500)

    def _build_header(self) -> None:
        header = tk.Frame(self.root, height=60)
        header.pack(fill=tk.X, padx=5, pady=(5, 0))
        header.pack_propagate(False)
        lbl = tk.Label(header, text=APP_NAME, font=("TkDefaultFont", 14, "bold"))
        lbl.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

    def _build_browser_control(self) -> None:
        frame = tk.LabelFrame(self.root, text="Browser Control", padx=5, pady=5)
        frame.pack(fill=tk.X, padx=5, pady=(5, 0))

        btn_frame = tk.Frame(frame)
        btn_frame.pack(fill=tk.X)

        self.launch_btn = tk.Button(
            btn_frame, text="Open Browser (Chrome)", command=self._on_launch_browser
        )
        self.launch_btn.pack(side=tk.LEFT, padx=5, pady=5)

        self.browser_status = tk.Label(btn_frame, text="Chrome status: Not running")
        self.browser_status.pack(side=tk.LEFT, padx=15, pady=5)

    def _build_separator(self) -> None:
        sep = ttk.Separator(self.root, orient=tk.HORIZONTAL)
        sep.pack(fill=tk.X, padx=5, pady=(10, 5))

    def _build_task_selection(self) -> None:
        frame = tk.LabelFrame(self.root, text="Select Tasks to Execute", padx=5, pady=5)
        frame.pack(fill=tk.X, padx=5, pady=(0, 5))

        btn_frame = tk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=(0, 5))

        tk.Button(btn_frame, text="Select All", command=self._on_select_all).pack(
            side=tk.RIGHT, padx=2
        )
        tk.Button(btn_frame, text="Clear All", command=self._on_clear_all).pack(
            side=tk.RIGHT, padx=2
        )

        canvas = tk.Canvas(frame, height=120, highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable = tk.Frame(canvas)

        scrollable.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        self.task_vars = []
        self.task_checkbuttons = []
        for t in TASKS:
            var = tk.BooleanVar(value=False)
            self.task_vars.append(var)
            cb = ttk.Checkbutton(scrollable, text=t.name, variable=var, command=self._update_ui)
            cb.pack(anchor=tk.W, padx=5, pady=2)
            self.task_checkbuttons.append(cb)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self._bind_mousewheel(canvas)

    def _bind_mousewheel(self, canvas) -> None:
        def _on_mousewheel(event) -> None:
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)

    def _build_execution_control(self) -> None:
        frame = tk.Frame(self.root, bd=1, relief=tk.SUNKEN, padx=5, pady=5)
        frame.pack(fill=tk.X, padx=5, pady=(0, 5))

        self.execute_btn = tk.Button(frame, text="Execute Selected Tasks", command=self._on_execute)
        self.execute_btn.pack(side=tk.LEFT, padx=5, pady=5)

        self.stop_btn = tk.Button(frame, text="Stop Execution", command=self._on_stop)
        self.stop_btn.pack(side=tk.LEFT, padx=5, pady=5)

        self.exec_status = tk.Label(frame, text="Ready")
        self.exec_status.pack(side=tk.RIGHT, padx=15, pady=5)

    def _build_output_log(self) -> None:
        frame = tk.LabelFrame(self.root, text="Execution Log", padx=5, pady=5)
        frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))

        text_frame = tk.Frame(frame)
        text_frame.pack(fill=tk.BOTH, expand=True)

        self.output_text = tk.Text(text_frame, wrap=tk.WORD, state=tk.DISABLED, height=10)
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.output_text.yview)
        self.output_text.configure(yscrollcommand=scrollbar.set)

        self.output_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        tk.Button(frame, text="Clear Output", command=self._on_clear_output).pack(pady=(5, 0))

    def _build_status_bar(self) -> None:
        frame = tk.Frame(self.root, bd=1, relief=tk.SUNKEN)
        frame.pack(fill=tk.X, side=tk.BOTTOM)

        self.state_label = tk.Label(frame, text="Ready", anchor=tk.W)
        self.state_label.pack(side=tk.LEFT, padx=5)

        self.ts_label = tk.Label(frame, text="", anchor=tk.E)
        self.ts_label.pack(side=tk.RIGHT, padx=5)

    def _log(self, step, message, severity="INFO") -> None:
        ts = datetime.now().strftime("%H:%M:%S")
        line = f"[{ts}] [{step}] {message}\n"
        self.output_text.configure(state=tk.NORMAL)
        self.output_text.insert(tk.END, line)
        self.output_text.see(tk.END)
        self.output_text.configure(state=tk.DISABLED)

    def _process_log_queue(self) -> None:
        while not self.log_queue.empty():
            msg = self.log_queue.get_nowait()
            self._log(*msg)
        self.root.after(100, self._process_log_queue)

    def _update_ui(self) -> None:
        any_selected = any(v.get() for v in self.task_vars)

        if self.state == "IDLE":
            self.launch_btn.configure(state=tk.NORMAL)
            for cb in self.task_checkbuttons:
                cb.configure(state=tk.NORMAL)
            self.execute_btn.configure(
                state=tk.DISABLED if not (self.browser_running and any_selected) else tk.NORMAL
            )
            self.execute_btn.configure(text="Execute Selected Tasks")
            self.stop_btn.pack_forget()
            self.exec_status.configure(text="Ready")
            self.state_label.configure(text="Ready")

        elif self.state == "BROWSER_LAUNCHING":
            self.launch_btn.configure(state=tk.DISABLED)
            for cb in self.task_checkbuttons:
                cb.configure(state=tk.NORMAL)
            self.execute_btn.configure(state=tk.DISABLED)
            self.browser_status.configure(text="Chrome status: Launching...")

        elif self.state == "BROWSER_READY":
            self.launch_btn.configure(state=tk.DISABLED)
            for cb in self.task_checkbuttons:
                cb.configure(state=tk.NORMAL)
            self.execute_btn.configure(
                state=tk.DISABLED if not (self.browser_running and any_selected) else tk.NORMAL
            )
            self.execute_btn.configure(text="Execute Selected Tasks")
            self.browser_status.configure(text="Chrome status: Ready for debugging")

        elif self.state == "EXECUTING":
            self.launch_btn.configure(state=tk.DISABLED)
            for cb in self.task_checkbuttons:
                cb.configure(state=tk.DISABLED)
            self.execute_btn.configure(state=tk.DISABLED, text="Executing...")
            self.stop_btn.pack(side=tk.LEFT, padx=5, pady=5, before=self.exec_status)
            self.exec_status.configure(text="Executing...")
            self.state_label.configure(text="Executing...")

        elif self.state == "EXECUTION_COMPLETE":
            self.launch_btn.configure(state=tk.DISABLED if self.browser_running else tk.NORMAL)
            for cb in self.task_checkbuttons:
                cb.configure(state=tk.NORMAL)
            self.execute_btn.configure(
                state=tk.NORMAL if (self.browser_running and any_selected) else tk.DISABLED
            )
            self.execute_btn.configure(text="Execute Selected Tasks")
            self.stop_btn.pack_forget()
            self.state_label.configure(text="Completed")

        self._update_timestamp()

    def _update_timestamp(self) -> None:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.ts_label.configure(text=now)

    def _on_launch_browser(self) -> None:
        self.state = "BROWSER_LAUNCHING"
        self.browser_status.configure(text="Chrome status: Launching...")
        self.launch_btn.configure(state=tk.DISABLED)
        self._update_ui()
        self._log("BROWSER", "Launching Chrome with remote debugging...", "INFO")
        threading.Thread(target=self._launch_chrome, daemon=True).start()

    def _launch_chrome(self) -> None:
        result = launch_chrome()
        self.browser_running = result["running"]
        self.state = "BROWSER_READY"
        self.root.after(0, self._on_browser_ready)

    def _on_browser_ready(self) -> None:
        self.browser_status.configure(text="Chrome status: Ready for debugging")
        self._log(
            "BROWSER", "Chrome launched successfully with remote debugging enabled.", "SUCCESS"
        )
        self._update_ui()

    def _on_select_all(self) -> None:
        for v in self.task_vars:
            v.set(True)
        self._update_ui()

    def _on_clear_all(self) -> None:
        for v in self.task_vars:
            v.set(False)
        self._update_ui()

    def _on_execute(self) -> None:
        selected = [t for t, v in zip(TASKS, self.task_vars, strict=False) if v.get()]
        if not selected or not self.browser_running:
            return
        self.state = "EXECUTING"
        self.executing = True
        self._update_ui()
        self._log("EXECUTION", f"Starting execution of {len(selected)} task(s)...", "INFO")
        threading.Thread(target=self._execute_tasks, args=(selected,), daemon=True).start()

    def _execute_tasks(self, selected) -> None:
        def progress(msg) -> None:
            self.log_queue.put(("EXECUTION", msg, "INFO"))

        execute_tasks(selected, on_progress=progress, is_cancelled=lambda: not self.executing)
        if self.executing:
            self.log_queue.put(("EXECUTION", "All selected tasks completed.", "SUCCESS"))
        self.executing = False
        self.root.after(0, self._on_execution_complete)

    def _on_execution_complete(self) -> None:
        self.state = "EXECUTION_COMPLETE"
        self._update_ui()

    def _on_stop(self) -> None:
        self.executing = False
        self._log("EXECUTION", "Execution stopped by user.", "WARNING")
        self.state = "EXECUTION_COMPLETE"
        self._update_ui()

    def _on_clear_output(self) -> None:
        self.output_text.configure(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.configure(state=tk.DISABLED)


def main() -> None:
    root = tk.Tk()
    TaskAutomationGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
