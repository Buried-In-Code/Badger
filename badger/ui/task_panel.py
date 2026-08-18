__all__ = ["TaskPanel"]

import tkinter as tk
from collections.abc import Callable
from tkinter import ttk

from badger.core.tasks import Task


class TaskPanel(ttk.LabelFrame):
    def __init__(
        self, parent: tk.Widget, *, tasks: list[Task], on_selection_change: Callable[[], None]
    ) -> None:
        super().__init__(parent, text="Step 2  -  Choose Tasks")
        self._tasks = tasks
        self._on_selection_change = on_selection_change

        btn_row = ttk.Frame(self)
        btn_row.pack(fill=tk.X, padx=6, pady=(6, 2))
        self.select_all_btn = ttk.Button(btn_row, text="Select All", command=self._select_all)
        self.select_all_btn.pack(side=tk.LEFT, padx=(0, 4))
        self.clear_all_btn = ttk.Button(btn_row, text="Clear All", command=self._clear_all)
        self.clear_all_btn.pack(side=tk.LEFT)

        container = ttk.Frame(self)
        container.pack(fill=tk.BOTH, expand=True, padx=6, pady=(0, 6))

        canvas = tk.Canvas(container, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient=tk.VERTICAL, command=canvas.yview)
        scrollable = ttk.Frame(canvas)

        scrollable.bind("<Configure>", lambda _: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        self.task_vars: list[tk.BooleanVar] = []
        self.task_checkbuttons: list[ttk.Checkbutton] = []
        for task in tasks:
            var = tk.BooleanVar()
            self.task_vars.append(var)
            checkbutton = ttk.Checkbutton(
                scrollable, text=task.name, variable=var, command=on_selection_change
            )
            checkbutton.pack(anchor=tk.W, pady=2)
            self.task_checkbuttons.append(checkbutton)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    @property
    def has_selection(self) -> bool:
        return any(var.get() for var in self.task_vars)

    def selected_tasks(self) -> list[Task]:
        return [task for task, var in zip(self._tasks, self.task_vars, strict=False) if var.get()]

    def set_enabled(self, *, enabled: bool) -> None:
        state = tk.NORMAL if enabled else tk.DISABLED
        for checkbutton in self.task_checkbuttons:
            checkbutton.configure(state=state)
        self.select_all_btn.configure(state=state)
        self.clear_all_btn.configure(state=state)

    def _select_all(self) -> None:
        for var in self.task_vars:
            var.set(True)
        self._on_selection_change()

    def _clear_all(self) -> None:
        for var in self.task_vars:
            var.set(False)
        self._on_selection_change()
