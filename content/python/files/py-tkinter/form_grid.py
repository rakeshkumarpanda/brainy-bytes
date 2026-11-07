# 6.4 Desktop windows with tkinter
# Window program "form_grid" from the lesson. It opens a window, so run it on your own computer.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import tkinter as tk
from tkinter import messagebox, ttk


def submit():
    name = name_entry.get().strip()
    age = age_entry.get().strip()
    if not name or not age.isdigit():
        messagebox.showerror("Sign up", "Please type a name and an age in numbers.")
        return
    result.config(text=f"Welcome, {name} ({age})!")


root = tk.Tk()
root.title("Sign up")
root.geometry("340x170")
root.columnconfigure(1, weight=1)           # column 1 gets any extra width

ttk.Label(root, text="Name:").grid(row=0, column=0, sticky="e", padx=8, pady=6)
name_entry = ttk.Entry(root)
name_entry.grid(row=0, column=1, sticky="ew", padx=8)

ttk.Label(root, text="Age:").grid(row=1, column=0, sticky="e", padx=8, pady=6)
age_entry = ttk.Entry(root, width=6)
age_entry.grid(row=1, column=1, sticky="w", padx=8)

ttk.Button(root, text="Submit", command=submit).grid(row=2, column=0, columnspan=2, pady=8)
result = ttk.Label(root, text="")
result.grid(row=3, column=0, columnspan=2)

name_entry.focus()
root.bind("<Return>", lambda event: submit())
root.mainloop()
