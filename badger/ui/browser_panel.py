__all__ = ["BrowserPanel"]

import contextlib
import tkinter as tk
from collections.abc import Callable
from tkinter import ttk

from badger.core.browser import default_browser_path
from badger.ui.state import BrowserState


class BrowserPanel(ttk.LabelFrame):
    def __init__(
        self,
        parent: tk.Widget,
        *,
        on_launch: Callable[[], None],
        on_port_change: Callable[[int], None],
        on_debug_visibility_change: Callable[[bool], None],
    ) -> None:
        super().__init__(parent, text="Step 1  -  Open Browser")
        self._on_port_changed = on_port_change
        self._on_debug_visibility_changed = on_debug_visibility_change

        row = ttk.Frame(self)
        row.pack(fill=tk.X, padx=6, pady=6)

        self.launch_btn = ttk.Button(row, text="Open Edge", command=on_launch)
        self.launch_btn.pack(side=tk.LEFT, padx=(0, 16))

        self.browser_status_lbl = ttk.Label(row, text="Not running")
        self.browser_status_lbl.pack(side=tk.LEFT)

        self.adv_btn = ttk.Button(row, text="Advanced", command=self._toggle_advanced)
        self.adv_btn.pack(side=tk.RIGHT)

        self._advanced_open = False
        self._advanced_frame = ttk.Frame(self)

        options_row = ttk.Frame(self._advanced_frame)
        options_row.pack(fill=tk.X)

        ttk.Label(options_row, text="Debug port:").pack(side=tk.LEFT, padx=(6, 4))
        self.port_var = tk.IntVar(value=9222)
        self.port_var.trace_add("write", self._handle_port_change)
        self.port_entry = ttk.Spinbox(
            options_row, from_=1024, to=65535, textvariable=self.port_var, width=7
        )
        self.port_entry.pack(side=tk.LEFT)

        ttk.Separator(options_row, orient=tk.VERTICAL).pack(
            side=tk.LEFT, fill=tk.Y, padx=12, pady=2
        )

        self.show_debug_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            options_row,
            text="Show debug output",
            variable=self.show_debug_var,
            command=self._handle_debug_visibility_change,
        ).pack(side=tk.LEFT)

        path_row = ttk.Frame(self._advanced_frame)
        path_row.pack(fill=tk.X, pady=(4, 0))

        ttk.Label(path_row, text="Browser path:").pack(side=tk.LEFT, padx=(6, 4))
        self.browser_path_var = tk.StringVar(value=default_browser_path())
        self.browser_path_entry = ttk.Entry(path_row, textvariable=self.browser_path_var)
        self.browser_path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))

    @property
    def port(self) -> int:
        return self.port_var.get()

    @property
    def browser_path(self) -> str:
        return self.browser_path_var.get()

    def set_state(self, state: BrowserState) -> None:
        launch_locked = state in {BrowserState.OPEN, BrowserState.LAUNCHING}
        widget_state = tk.DISABLED if launch_locked else tk.NORMAL
        self.launch_btn.configure(state=widget_state)
        self.port_entry.configure(state=widget_state)
        self.browser_path_entry.configure(state=widget_state)

        text, colour = {
            BrowserState.OPEN: ("Ready", "#4caf50"),
            BrowserState.LAUNCHING: ("Launching", "#ff9800"),
            BrowserState.FAILED: ("Failed", "#f44747"),
            BrowserState.CLOSED: ("Not running", "#9e9e9e"),
        }[state]
        self.browser_status_lbl.configure(text=text, foreground=colour)

    def _handle_port_change(self, *_: object) -> None:
        with contextlib.suppress(tk.TclError):
            self._on_port_changed(self.port)

    def _handle_debug_visibility_change(self) -> None:
        self._on_debug_visibility_changed(self.show_debug_var.get())

    def _toggle_advanced(self) -> None:
        self._advanced_open = not self._advanced_open
        if self._advanced_open:
            self._advanced_frame.pack(fill=tk.X, padx=6, pady=(0, 6))
        else:
            self._advanced_frame.pack_forget()
