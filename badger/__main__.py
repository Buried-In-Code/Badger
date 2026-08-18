import tkinter as tk

from badger.core.log import read_logs
from badger.ui import BadgerUI


def gui() -> None:
    root = tk.Tk()
    ui = BadgerUI(root)
    for log in read_logs():
        ui.log_queue.put(log)
    root.mainloop()


if __name__ == "__main__":
    gui()
