# 6.4 Desktop windows with tkinter
# Window program "frozen_or_not" from the lesson. It opens a window, so run it on your own computer.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import queue
import threading
import time
import tkinter as tk
from tkinter import ttk

results = queue.Queue()


def slow_work():
    time.sleep(3)                          # pretend to download a big file
    return "file downloaded"


def bad_click():
    status.config(text="Working... the window is frozen")
    slow_work()                            # mainloop cannot run for 3 seconds
    status.config(text="Done the bad way")


def good_click():
    status.config(text="Working in the background...")
    progress.start(10)
    threading.Thread(target=worker, daemon=True).start()
    root.after(100, check_result)


def worker():                              # runs in another thread: no tkinter calls here
    results.put(slow_work())


def check_result():                        # runs in the main thread, called by mainloop
    try:
        message = results.get_nowait()
    except queue.Empty:
        root.after(100, check_result)      # not ready yet: look again in 100 ms
        return
    progress.stop()
    status.config(text=f"Done the good way: {message}")


root = tk.Tk()
root.title("Frozen or not")
ttk.Button(root, text="Slow task, bad way", command=bad_click).pack(padx=20, pady=(15, 5), fill="x")
ttk.Button(root, text="Slow task, good way", command=good_click).pack(padx=20, pady=5, fill="x")
progress = ttk.Progressbar(root, mode="indeterminate", length=280)
progress.pack(padx=20, pady=5)
status = ttk.Label(root, text="Press a button")
status.pack(pady=(5, 15))
root.mainloop()
