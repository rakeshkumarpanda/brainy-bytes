# 6.4 Desktop windows with tkinter
# Window program "hello_window" from the lesson. It opens a window, so run it on your own computer.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import tkinter as tk

clicks = 0


def say_hello():
    global clicks
    clicks = clicks + 1
    label.config(text=f"Hello! You clicked {clicks} times.")


root = tk.Tk()
root.title("My first window")
root.geometry("360x140")

label = tk.Label(root, text="Press the button", font=("Arial", 14))
label.pack(pady=15)

button = tk.Button(root, text="Say hello", command=say_hello)
button.pack()

root.mainloop()
print("The window is closed, so mainloop returned.")
