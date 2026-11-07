# 6.4 Desktop windows with tkinter
# Window program "pizza_order" from the lesson. It opens a window, so run it on your own computer.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import tkinter as tk
from tkinter import ttk

PRICES = {"small": 6, "medium": 8, "large": 10}

root = tk.Tk()
root.title("Pizza order")

size = tk.StringVar(value="medium")
cheese = tk.BooleanVar(value=True)
count = tk.IntVar(value=1)
summary = tk.StringVar()


def update_summary(*args):
    price = PRICES[size.get()]
    if cheese.get():
        price = price + 1
    extra = " with extra cheese" if cheese.get() else ""
    summary.set(f"{count.get()} x {size.get()}{extra} = {price * count.get()} euros")


for value in ("small", "medium", "large"):
    ttk.Radiobutton(root, text=value.title(), value=value, variable=size).pack(anchor="w", padx=12)
ttk.Checkbutton(root, text="Extra cheese (+1)", variable=cheese).pack(anchor="w", padx=12, pady=4)
ttk.Scale(root, from_=1, to=10, variable=count, command=lambda value: count.set(round(float(value)))).pack(fill="x", padx=12)
ttk.Label(root, textvariable=summary, font=("Arial", 12, "bold")).pack(padx=12, pady=10)

for variable in (size, cheese, count):
    variable.trace_add("write", update_summary)    # run update_summary whenever the value changes
update_summary()
root.mainloop()
