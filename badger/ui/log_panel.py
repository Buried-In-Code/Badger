__all__ = ["LogPanel"]

import tkinter as tk
from tkinter import ttk

from badger.core.log import Level, Log


class LogPanel(ttk.LabelFrame):
    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent, text="Activity Log")

        container = ttk.Frame(self)
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

    def append(self, log: Log) -> None:
        tag = log.level.value
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"[{log.timestamp.isoformat()}] ", ("ts", tag))
        self.log_text.insert(tk.END, f"[{tag:<5}] {log.message}\n", tag)
        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)

    def set_debug_visible(self, *, visible: bool) -> None:
        self.log_text.tag_configure(Level.DEBUG.value, elide=not visible)
