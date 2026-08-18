__all__ = ["RunPanel"]

import tkinter as tk
from collections.abc import Callable
from tkinter import ttk

from badger.ui.state import RunState


class RunPanel(ttk.LabelFrame):
    def __init__(
        self, parent: tk.Widget, *, on_run: Callable[[], None], on_stop: Callable[[], None]
    ) -> None:
        super().__init__(parent, text="Step 3  -  Run")

        row = ttk.Frame(self)
        row.pack(fill=tk.X, padx=6, pady=6)

        self.run_btn = ttk.Button(row, text="Start", command=on_run)
        self.run_btn.pack(side=tk.LEFT, padx=(0, 8))

        self.stop_btn = ttk.Button(row, text="Stop", command=on_stop)
        self.stop_btn.pack(side=tk.LEFT)

        self.run_status_lbl = ttk.Label(row, text="")
        self.run_status_lbl.pack(side=tk.RIGHT, padx=8)

    def set_state(self, state: RunState, *, can_start: bool) -> None:
        is_running = state is RunState.RUNNING
        self.run_btn.configure(
            state=tk.NORMAL if can_start else tk.DISABLED, text="Running" if is_running else "Start"
        )
        self.stop_btn.configure(state=tk.NORMAL if is_running else tk.DISABLED)
        self.run_status_lbl.configure(
            text={RunState.RUNNING: "Running", RunState.COMPLETE: "Complete"}.get(state, "")
        )
