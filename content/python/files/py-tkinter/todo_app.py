# 6.4 Desktop windows with tkinter
# Window program "todo_app" from the lesson. It opens a window, so run it on your own computer.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import json
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

FILE = Path.home() / "todo.json"


class TodoApp(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=10)
        self.grid(row=0, column=0, sticky="nsew")
        master.columnconfigure(0, weight=1)
        master.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self.entry = ttk.Entry(self)
        self.entry.grid(row=0, column=0, sticky="ew")
        self.entry.bind("<Return>", self.add)
        ttk.Button(self, text="Add", command=self.add).grid(row=0, column=1, padx=(6, 0))

        self.listbox = tk.Listbox(self, height=8)
        self.listbox.grid(row=1, column=0, sticky="nsew", pady=8)
        scroll = ttk.Scrollbar(self, orient="vertical", command=self.listbox.yview)
        scroll.grid(row=1, column=1, sticky="ns", pady=8)
        self.listbox.config(yscrollcommand=scroll.set)

        ttk.Button(self, text="Done", command=self.remove).grid(row=2, column=0, sticky="w")
        ttk.Button(self, text="Save", command=self.save).grid(row=2, column=1)
        self.load()

    def add(self, event=None):
        text = self.entry.get().strip()
        if text:
            self.listbox.insert("end", text)
            self.entry.delete(0, "end")

    def remove(self):
        chosen = self.listbox.curselection()
        if not chosen:
            messagebox.showinfo("To do", "Click a task first.")
            return
        self.listbox.delete(chosen[0])

    def save(self):
        tasks = list(self.listbox.get(0, "end"))
        FILE.write_text(json.dumps(tasks, indent=2), encoding="utf-8")
        messagebox.showinfo("To do", f"Saved {len(tasks)} tasks in {FILE}")

    def load(self):
        if FILE.exists():
            for task in json.loads(FILE.read_text(encoding="utf-8")):
                self.listbox.insert("end", task)


root = tk.Tk()
root.title("To do list")
root.geometry("320x300")
app = TodoApp(root)
root.mainloop()
