# Advanced Python 6.4: desktop windows with tkinter. Checked against the Python 3.14 documentation of tkinter and
# tkinter.ttk (Tk, mainloop, widgets, pack, grid, place, columnconfigure weight, sticky, StringVar, IntVar,
# BooleanVar, trace_add, bind and event strings, Canvas items, after, messagebox, the rule that Tk calls belong in the
# main thread) and the PCPP-32-101 GUI programming section. The window programs were run with Python 3.14 and Tk 9.0
# under Xvfb, and the screenshots in content/python/img/py-tkinter/ are from those runs.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, lc, leet, files, grow, leet_items, gui, gui_files

chapter('py-tkinter')
K = Kit()

HELLO = '''import tkinter as tk

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
'''

FORM = '''import tkinter as tk
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
'''

PIZZA = '''import tkinter as tk
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
'''

BALL = '''import tkinter as tk

WIDTH = 400
HEIGHT = 250
SIZE = 30

root = tk.Tk()
root.title("Bouncing ball")
canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="white")
canvas.pack()

canvas.create_rectangle(10, 10, 130, 40, fill="#dbeafe", outline="#2563eb")
canvas.create_text(70, 25, text="Space: pause")
canvas.create_line(0, HEIGHT - 20, WIDTH, HEIGHT - 20, fill="gray", dash=(4, 2))
ball = canvas.create_oval(50, 50, 50 + SIZE, 50 + SIZE, fill="orange")

dx = 4
dy = 3
running = True


def move():
    global dx, dy
    if running:
        canvas.move(ball, dx, dy)
        x1, y1, x2, y2 = canvas.coords(ball)
        if x1 <= 0 or x2 >= WIDTH:
            dx = -dx
        if y1 <= 0 or y2 >= HEIGHT - 20:
            dy = -dy
    root.after(20, move)                 # call move again in 20 ms, about 50 times a second


def toggle(event):
    global running
    running = not running


def jump(event):
    canvas.coords(ball, event.x, event.y, event.x + SIZE, event.y + SIZE)


root.bind("<space>", toggle)
canvas.bind("<Button-1>", jump)
move()
root.mainloop()
'''

TODO = '''import json
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
'''

FREEZE = '''import queue
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
'''

K.code('event_loop_model', r'''
from collections import deque

# A pretend event queue. A real one is filled by the operating system: clicks, keys, timers, redraws.
events = deque([("click", "button"), ("key", "a"), ("timer", "tick"), ("key", "Return"), ("close", "")])
handlers = {}


def bind(kind, function):
    handlers[kind] = function


def on_click(detail):
    print("clicked the", detail)


def on_key(detail):
    print("key pressed:", detail)


bind("click", on_click)
bind("key", on_key)

while events:                              # this is what mainloop() does, again and again
    kind, detail = events.popleft()
    if kind == "close":
        print("window closed, so mainloop returns")
        break
    handler = handlers.get(kind)
    if handler is None:
        print("no handler for", kind, "so nothing happens")
    else:
        handler(detail)
''')

K.code('converter_logic', r'''
def celsius_to_fahrenheit(text):
    """The logic of a converter window, kept apart from tkinter so it is easy to test."""
    text = text.strip().replace(",", ".")
    try:
        celsius = float(text)
    except ValueError:
        return "Please type a number"
    if celsius < -273.15:
        return "Colder than absolute zero is not possible"
    fahrenheit = celsius * 9 / 5 + 32
    return f"{fahrenheit:.1f} degrees Fahrenheit"


for typed in ["100", "-40", " 36,6 ", "hot", "", "-300"]:
    print(repr(typed), "gives", celsius_to_fahrenheit(typed))

assert celsius_to_fahrenheit("0") == "32.0 degrees Fahrenheit"
assert celsius_to_fahrenheit("abc") == "Please type a number"
print("tests pass")

# In the window, the button only connects the two worlds:
#   def convert():
#       result.config(text=celsius_to_fahrenheit(entry.get()))
''')

K.lesson('idea', 'Windows, buttons and the event loop', f'''
{src('Python 3.14 documentation of tkinter and tkinter.ttk, and the PCPP-32-101 GUI programming section.')}
{wwh('A <b>GUI</b> (graphical user interface) is a program with windows, buttons, text boxes and menus instead of typed commands. <b>tkinter</b> is the GUI toolkit that comes with Python. It wraps <b>Tk</b>, a toolkit that runs on Windows, macOS and Linux.',
     'Many users never open a terminal. A small window lets them pick a file, fill in a form or press a button, and it can show pictures, charts and live data. Office tools, installers and lab instruments often need exactly this.',
     'You build a tree of <b>widgets</b> (the window, frames, labels, buttons), place them with a <b>geometry manager</b> (pack, grid or place), connect events such as clicks to your functions, and hand control to <b>mainloop()</b>. From then on your code runs only when an event calls it.')}
{viz('pytk')}
{versus('Ways to build a user interface in Python', ['', 'tkinter', 'PySide6 or PyQt6', 'Kivy', 'Web app (Flask, Django)', 'Textual'], [
    ['Install', 'Comes with Python', 'pip, about 100 MB', 'pip', 'pip, plus a browser', 'pip'],
    ['Look', 'Simple, native with ttk', 'Modern, very rich', 'Its own touch style', 'Anything HTML and CSS can do', 'Text in the terminal'],
    ['Runs on', 'Desktop', 'Desktop', 'Desktop, Android, iOS', 'Any device with a browser', 'Any terminal, also over SSH'],
    ['Licence', 'Python licence', 'LGPL (PySide6) or GPL / paid (PyQt6)', 'MIT', 'Your choice', 'MIT'],
    ['Best for', 'Small tools, teaching, the PCPP exam', 'Large desktop applications', 'Touch and mobile apps', 'Apps for many users', 'Developer tools']],
    'tkinter to learn how every GUI works and for small tools, Qt for big desktop programs, and a web app when many people must use it.')}
''', kw=['GUI', 'tkinter', 'Tk', 'widget', 'event', 'event loop', 'mainloop', 'event driven', 'PySide6', 'PyQt', 'Kivy', 'Textual'])

K.lesson('first', 'Your first window', f'''
{gui('hello_window', HELLO, {1: 'Import tkinter under the short name tk. This is the usual style.', 6: 'The function the button will call. It changes the global counter, so it needs the global statement.', 12: 'tk.Tk() makes the main window. A program has exactly one Tk object.', 14: 'geometry("WIDTHxHEIGHT") sets the size in pixels.', 16: 'Every widget gets its parent as the first argument. Options such as text and font are keyword arguments.', 17: 'A widget is invisible until a geometry manager places it. pack() stacks widgets from the top.', 19: 'command=say_hello hands over the function itself, without brackets. Tk calls it on every click.', 22: 'mainloop() shows the window and handles events until the window is closed.', 23: 'This line runs only after the window is closed.'}, 'hello.png', 'The window after two clicks on "Say hello".')}
{table(['Step', 'Code', 'What it does'], [
    ['1', 'root = tk.Tk()', 'Make the main window'],
    ['2', 'w = tk.Label(root, text=...)', 'Make a widget inside a parent'],
    ['3', 'w.pack() or w.grid(...)', 'Place it, or it stays invisible'],
    ['4', 'command=function, w.bind(event, function)', 'Connect events to your functions'],
    ['5', 'w.config(text=...) or w["text"] = ...', 'Change a widget later'],
    ['6', 'root.mainloop()', 'Start the event loop']])}
<p>mainloop() is a loop that waits for events and calls the right function for each one. This small model shows the idea without a window, so it runs in the page:</p>
{run('event_loop_model')}
{note('command=say_hello() (with brackets) is the classic beginner bug: it calls the function ONCE while the button is made and stores its result, None, as the command. Then clicks do nothing. To pass arguments, use command=lambda: say(name).', 'exam')}
''', kw=['Tk', 'title', 'geometry', 'Label', 'Button', 'command', 'pack', 'mainloop', 'config', 'event queue', 'callback'])

K.lesson('layout', 'Placing widgets: pack, grid and place', f'''
{gui('form_grid', FORM, {6: 'Entry.get() returns the text the user typed, always as a string.', 8: 'Check the input before you use it. isdigit() is True only for whole numbers made of digits.', 9: 'messagebox shows a small dialog window and waits until the user closes it.', 17: 'weight=1: when the window gets wider, column 1 gets the extra space.', 19: 'grid puts the label in row 0, column 0. sticky="e" pushes it to the right side of its cell.', 21: 'sticky="ew" stretches the entry from the left to the right edge of its cell.', 27: 'columnspan=2 lets the button use both columns.', 31: 'focus() puts the text cursor in the name box, so the user can type at once.', 32: 'bind connects the Enter key to submit. A bound function gets an event object, so the lambda takes one argument.'}, 'form.png', 'The sign up form after typing Ann and 31 and submitting.')}
{versus('Geometry managers', ['', 'pack', 'grid', 'place'], [
    ['Idea', 'Stack widgets from one side (top, left ...)', 'A table of rows and columns', 'Exact x, y position or relative position'],
    ['Good for', 'Toolbars, simple columns of widgets', 'Forms, dialogs, almost every real layout', 'Overlays, games, special cases'],
    ['Grows with the window', 'fill and expand', 'sticky and weight', 'Only with relx, rely, relwidth'],
    ['Main options', 'side, fill, expand, padx, pady, anchor', 'row, column, sticky, columnspan, rowspan, padx, pady', 'x, y, relx, rely, anchor, width, height']],
    'Use grid for forms and most windows, pack for simple stacks. Inside ONE parent use only one of them.')}
{note('Never mix pack and grid for widgets with the same parent: Tk raises TclError ("cannot use geometry manager grid inside . which already has slaves managed by pack"). Put each group in its own Frame instead, and each Frame can use its own manager.', 'warn')}
''', kw=['pack', 'grid', 'place', 'sticky', 'columnspan', 'weight', 'columnconfigure', 'padx', 'pady', 'Entry', 'get', 'messagebox', 'focus', 'Frame'])

K.lesson('vars', 'Widgets and control variables', f'''
{gui('pizza_order', PIZZA, {9: 'A StringVar holds a string. Widgets that share it stay in step with it automatically.', 10: 'BooleanVar for a check box, IntVar for whole numbers. value= sets the start value.', 15: 'A function for trace_add gets three arguments from Tk. *args collects and ignores them.', 23: 'All three radio buttons share variable=size, so choosing one sets size to its value and clears the others.', 26: 'A Scale gives floats. The command rounds the value, so count stays a whole number.', 27: 'textvariable=summary: the label shows whatever summary holds, now and after every change.', 30: 'trace_add("write", f) calls f every time the variable gets a new value.'}, 'pizza.png', 'The pizza window after choosing Large and moving the scale to 3.')}
{table(['Widget', 'Use it for', 'Read or set'], [
    ['ttk.Label, tk.Message', 'Text or an image', 'config(text=...) or textvariable'],
    ['ttk.Button', 'An action', 'command='],
    ['ttk.Entry', 'One line of text', 'get(), insert(0, s), delete(0, "end")'],
    ['tk.Text', 'Many lines of text', 'get("1.0", "end"), insert("end", s)'],
    ['ttk.Checkbutton, ttk.Radiobutton', 'Yes or no, one of several', 'variable= BooleanVar or StringVar'],
    ['ttk.Combobox, tk.Listbox', 'Pick from a list', 'get(), curselection()'],
    ['ttk.Scale, ttk.Spinbox', 'A number in a range', 'variable= or get()'],
    ['tk.Canvas', 'Drawing and animation', 'create_line, create_oval, move, coords'],
    ['ttk.Frame, ttk.LabelFrame', 'Group other widgets', 'a parent for others'],
    ['tk.Menu, filedialog, messagebox', 'Menus and standard dialogs', 'askopenfilename(), showinfo()']])}
{note('ttk widgets (from tkinter import ttk) use the look of the operating system and are styled with themes. The older tk widgets use options such as bg and fg. Prefer ttk where it has the widget. Listbox, Text, Canvas and Menu exist only in tk.', 'tip')}
''', kw=['StringVar', 'IntVar', 'BooleanVar', 'DoubleVar', 'textvariable', 'trace_add', 'Radiobutton', 'Checkbutton', 'Scale', 'Combobox', 'Listbox', 'Text', 'ttk', 'themes'])

K.lesson('events', 'Events, the Canvas and animation with after()', f'''
{gui('bouncing_ball', BALL, {9: 'A Canvas is a drawing area. Its point (0, 0) is the TOP left corner, and y grows downwards.', 12: 'Every create_ method draws an item and returns its id, a number you use later to move or change it.', 15: 'Keep the id of the ball so that move() can find it again.', 22: 'move() changes global variables, so it names them in a global statement.', 25: 'canvas.move(item, dx, dy) shifts the item by dx pixels right and dy pixels down.', 26: 'coords(item) gives the corners x1, y1, x2, y2 of the box around the oval.', 27: 'At the left or right wall, turn the horizontal direction round.', 31: 'after(20, move) asks mainloop to call move again in 20 ms. This is how tkinter animates without blocking.', 34: 'Event handlers get an event object with details: event.x, event.y, event.keysym, event.char.', 43: '"<space>" is the space key. "<Button-1>" is a click with the left mouse button.'}, 'ball.png', 'The canvas while the ball is bouncing.')}
{table(['Event string', 'Happens when', 'Useful event fields'], [
    ['&lt;Button-1&gt;, &lt;Button-3&gt;', 'Left or right mouse button pressed', 'event.x, event.y'],
    ['&lt;Double-Button-1&gt;', 'Double click', 'event.x, event.y'],
    ['&lt;B1-Motion&gt;, &lt;Motion&gt;', 'Mouse moved with or without the button down', 'event.x, event.y'],
    ['&lt;Key&gt;, &lt;Return&gt;, &lt;Escape&gt;, a', 'Any key, Enter, Esc, the a key', 'event.keysym, event.char'],
    ['&lt;Control-s&gt;', 'Ctrl and S together', 'event.state'],
    ['&lt;Configure&gt;', 'The widget changed size', 'event.width, event.height'],
    ['&lt;FocusIn&gt;, &lt;FocusOut&gt;', 'The widget got or lost the keyboard', 'event.widget']])}
{note('bind on a widget catches events in that widget. root.bind catches them anywhere in the window, and bind_all in every window of the program. For the close button use root.protocol("WM_DELETE_WINDOW", function).', 'tip')}
''', kw=['bind', 'event', 'Button-1', 'Key', 'keysym', 'Canvas', 'create_oval', 'move', 'coords', 'after', 'animation', 'protocol', 'WM_DELETE_WINDOW'])

K.lesson('app', 'A real app: classes, scrollbars and saving', f'''
{gui('todo_app', TODO, {6: 'The tasks are saved as JSON in your home folder.', 9: 'The app is a class based on ttk.Frame. Each window part is an attribute, so the methods can reach it.', 12: 'sticky="nsew" plus weight=1 on row 0 and column 0 makes the frame fill the whole window.', 20: 'Pressing Enter in the entry calls add with an event object. The button calls add without one, so add has event=None.', 23: 'Listbox is a tk widget. ttk has no list box.', 25: 'A scrollbar and a list box are linked both ways: command= scrolls the list, yscrollcommand moves the bar.', 31: 'Load the saved tasks when the app starts.', 40: 'curselection() gives a tuple with the indexes of the chosen lines, empty when nothing is chosen.', 47: 'get(0, "end") gives every line of the list box as a tuple.'}, 'todo.png', 'The to do list with three tasks, one of them chosen.')}
<p>Keep the logic of an app (rules, calculations, saving) outside the window code. Then you can test it without opening a window, and the window code stays short. This is called <b>separating the model from the view</b>:</p>
{run('converter_logic')}
{versus('Where to put the code', ['', 'Everything in the callbacks', 'Model and view apart'], [
    ['Testing', 'Only by clicking by hand', 'Normal unit tests with pytest'],
    ['Changing the look', 'Touches the rules too', 'Only the view changes'],
    ['Moving to another toolkit or the web', 'Rewrite everything', 'Keep the model, write a new view']],
    'Callbacks should only read the widgets, call the model and show the result.')}
''', kw=['class', 'ttk.Frame', 'Listbox', 'Scrollbar', 'curselection', 'yscrollcommand', 'json', 'model view', 'MVC', 'testing GUI code'])

K.lesson('freeze', 'Long tasks without freezing the window', f'''
{gui('frozen_or_not', FREEZE, {7: 'A thread safe queue carries results from the worker thread to the main thread.', 17: 'bad_click runs inside mainloop. While it sleeps, no event is handled: no redraw, no clicks.', 23: 'The progress bar animates because mainloop keeps running.', 24: 'The slow work moves to another thread. daemon=True lets the program end even if it still runs.', 25: 'Start checking for the result in 100 ms.', 28: 'The worker never touches a widget. tkinter calls belong in the main thread only.', 34: 'get_nowait() returns at once, or raises queue.Empty when there is nothing yet.', 36: 'Not ready: check again later. This keeps every callback short.'}, 'freeze.png', 'The window half way through the good way: the progress bar keeps moving.')}
{table(['Long task', 'What to use'], [
    ['Waiting or a timer', 'root.after(ms, function)'],
    ['Many small steps (a counter, an animation)', 'Do one step, then after(ms, next_step)'],
    ['Slow input and output (download, database)', 'A thread that puts results in a queue.Queue, checked with after()'],
    ['Heavy CPU work', 'A process (concurrent.futures.ProcessPoolExecutor), results checked with after()'],
    ['Never', 'time.sleep() or a long loop inside a callback']])}
{note('Tk is not thread safe. Create and change widgets only in the thread that runs mainloop. Other threads hand their results over through a queue, and the main thread picks them up with after().', 'warn')}
''', kw=['freeze', 'not responding', 'after', 'threading', 'queue', 'Progressbar', 'thread safe', 'main thread', 'ProcessPoolExecutor'])

K.lesson('maths', 'The maths: pixels, frames and how fast people click', f'''
{fxs(fx('Screen coordinates', 'x grows to the right, y grows DOWN, (0, 0) is the top left corner', 'A point 50 pixels from the top has y = 50, not y = height &minus; 50.'),
     fx('Centre a window', 'x = (screen width &minus; window width) // 2, y = (screen height &minus; window height) // 2', 'A 300 &times; 200 window on 1920 &times; 1080: x = 810, y = 440, geometry "300x200+810+440".', key=True),
     fx('Frames and speed', 'delay = 1000 / fps ms, speed = pixels per step &times; 1000 / delay', 'after(20, ...) gives 50 frames a second. 4 pixels a step is 200 pixels a second.'),
     fx('Sharing extra space', 'extra for column i = extra &times; weight<sub>i</sub> / sum of weights', '300 extra pixels, weights 1 and 2: 100 and 200 pixels.'),
     fx('Fitts\'s law', 'time = a + b &times; log<sub>2</sub>(D / W + 1)', 'D = distance to the target, W = its width. Big, close buttons are faster to hit.', key=True),
     fx('Hick\'s law', 'time = b &times; log<sub>2</sub>(n + 1)', 'n equal choices. 7 menu items: log<sub>2</sub> 8 = 3 times b.'))}
{steps('Worked example: how long does it take to hit a small button far away?', [
    'Take a = 0.1 s and b = 0.15 s, typical numbers for a mouse.',
    'The button is 20 pixels wide and 300 pixels away: D / W + 1 = 15 + 1 = 16.',
    'log<sub>2</sub> 16 = 4, so the time is 0.1 + 0.15 &times; 4 = 0.7 s.',
    'Make the button 80 pixels wide: D / W + 1 = 4.75, log<sub>2</sub> 4.75 &asymp; 2.25, time &asymp; 0.44 s.',
    eq('A 4 times wider button saves about 0.26 s on every click')])}
''', kw=['coordinates', 'centre window', 'fps', 'frame rate', 'weight', 'Fitts law', 'Hick law', 'usability'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>Make a window with labels, buttons and entries, place them with pack or grid, and call your function with command=.</p>',
    '<p>Use control variables, bind events, draw and animate on a Canvas with after(), and build an app as a class with ttk widgets, menus and dialogs.</p>',
    '<p>Keep the model apart from the view and test it, keep the window alive with after(), threads and queues, and style the app with ttk themes.</p>',
    '<p>Understand how Tk talks to the window system, the single UI thread rule in every toolkit, accessibility, high DPI screens, and human factors such as Fitts\'s and Hick\'s laws. Move to Qt for large apps.</p>')}
{grow('Make a window that reacts to clicks.', 'Build forms, canvases and class based apps.', 'Design responsive, tested and usable interfaces.')}
''', kw=['beginner', 'expert', 'MVC', 'themes', 'accessibility', 'high DPI', 'Qt'])

lc(657, 'Robot Return to Origin', 'robot-return-to-origin', 'e', 'Count the moves in each direction', 'Like moving an item on a canvas: R adds to x, L takes away. Back at the start means x and y are both 0.', r'''
def judge_circle(moves):
    x = 0
    y = 0
    for move in moves:
        if move == "R":
            x += 1
        elif move == "L":
            x -= 1
        elif move == "U":
            y -= 1
        else:
            y += 1
    return x == 0 and y == 0
''', [('judge_circle("UD")', True), ('judge_circle("LL")', False), ('judge_circle("RRDDLLUU")', True)])
lc(733, 'Flood Fill', 'flood-fill', 'e', 'The paint bucket tool: breadth first search', 'Start at the clicked pixel and paint every neighbour (up, down, left, right) that has the old colour. Stop at once if the new colour equals the old one.', r'''
from collections import deque


def flood_fill(image, sr, sc, color):
    old = image[sr][sc]
    if old == color:
        return image
    rows = len(image)
    cols = len(image[0])
    todo = deque([(sr, sc)])
    image[sr][sc] = color
    while todo:
        r, c = todo.popleft()
        for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
            if 0 <= nr < rows and 0 <= nc < cols and image[nr][nc] == old:
                image[nr][nc] = color
                todo.append((nr, nc))
    return image
''', [('flood_fill([[1, 1, 1], [1, 1, 0], [1, 0, 1]], 1, 1, 2)', [[2, 2, 2], [2, 2, 0], [2, 0, 1]]), ('flood_fill([[0, 0, 0], [0, 0, 0]], 0, 0, 0)', [[0, 0, 0], [0, 0, 0]])])
lc(836, 'Rectangle Overlap', 'rectangle-overlap', 'e', 'Overlap on both axes', 'Two boxes overlap when the left edge of each is before the right edge of the other, on x AND on y. Touching edges do not count. Games use this for collisions.', r'''
def is_rectangle_overlap(rec1, rec2):
    overlap_x = min(rec1[2], rec2[2]) > max(rec1[0], rec2[0])
    overlap_y = min(rec1[3], rec2[3]) > max(rec1[1], rec2[1])
    return overlap_x and overlap_y
''', [('is_rectangle_overlap([0, 0, 2, 2], [1, 1, 3, 3])', True), ('is_rectangle_overlap([0, 0, 1, 1], [1, 0, 2, 1])', False), ('is_rectangle_overlap([0, 0, 1, 1], [2, 2, 3, 3])', False)])
lc(1232, 'Check If It Is a Straight Line', 'check-if-it-is-a-straight-line', 'e', 'Compare slopes with a cross product', 'Points are on one line when (y - y0) &times; (x1 - x0) equals (y1 - y0) &times; (x - x0) for every point. Multiplying avoids dividing by zero for vertical lines.', r'''
def check_straight_line(coordinates):
    x0, y0 = coordinates[0]
    x1, y1 = coordinates[1]
    for x, y in coordinates[2:]:
        if (y - y0) * (x1 - x0) != (y1 - y0) * (x - x0):
            return False
    return True
''', [('check_straight_line([[1, 2], [2, 3], [3, 4], [4, 5], [5, 6], [6, 7]])', True), ('check_straight_line([[1, 1], [2, 2], [3, 4], [4, 5], [5, 6], [7, 7]])', False), ('check_straight_line([[0, 0], [0, 1], [0, -1]])', True)])
lc(223, 'Rectangle Area', 'rectangle-area', 'm', 'Both areas minus the overlap', 'Add the two areas and take away the overlap. The overlap width is max(0, min of right edges minus max of left edges), the same for the height.', r'''
def compute_area(ax1, ay1, ax2, ay2, bx1, by1, bx2, by2):
    area_a = (ax2 - ax1) * (ay2 - ay1)
    area_b = (bx2 - bx1) * (by2 - by1)
    width = max(0, min(ax2, bx2) - max(ax1, bx1))
    height = max(0, min(ay2, by2) - max(ay1, by1))
    return area_a + area_b - width * height
''', [('compute_area(-3, 0, 3, 4, 0, -1, 9, 2)', 45), ('compute_area(-2, -2, 2, 2, -2, -2, 2, 2)', 16)])
lc(593, 'Valid Square', 'valid-square', 'm', 'Six distances between four points', 'A square has 4 equal sides and 2 equal, longer diagonals. Use squared distances to stay with whole numbers, and reject a length of 0.', r'''
def valid_square(p1, p2, p3, p4):
    points = [p1, p2, p3, p4]
    distances = []
    for i in range(4):
        for j in range(i + 1, 4):
            dx = points[i][0] - points[j][0]
            dy = points[i][1] - points[j][1]
            distances.append(dx * dx + dy * dy)
    distances.sort()
    return distances[0] > 0 and distances[0] == distances[3] and distances[4] == distances[5] and distances[4] == 2 * distances[0]
''', [('valid_square([0, 0], [1, 1], [1, 0], [0, 1])', True), ('valid_square([0, 0], [1, 1], [1, 0], [0, 12])', False), ('valid_square([1, 0], [-1, 0], [0, 1], [0, -1])', True)])
lc(874, 'Walking Robot Simulation', 'walking-robot-simulation', 'm', 'Directions as a list, obstacles as a set', 'Keep the four directions in a list and turn by moving the index. Store obstacles as a set of tuples so each step is checked in O(1).', r'''
def robot_sim(commands, obstacles):
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    blocked = {(x, y) for x, y in obstacles}
    x = 0
    y = 0
    facing = 0
    best = 0
    for command in commands:
        if command == -2:
            facing = (facing + 3) % 4
        elif command == -1:
            facing = (facing + 1) % 4
        else:
            dx, dy = directions[facing]
            for step in range(command):
                if (x + dx, y + dy) in blocked:
                    break
                x += dx
                y += dy
                best = max(best, x * x + y * y)
    return best
''', [('robot_sim([4, -1, 3], [])', 25), ('robot_sim([4, -1, 4, -2, 4], [[2, 4]])', 65), ('robot_sim([6, -1, -1, 6], [[0, 0]])', 36)])
lc(1041, 'Robot Bounded In Circle', 'robot-bounded-in-circle', 'm', 'Run the instructions once and look at the result', 'After one run the robot is either back at the start or facing a new direction. In both cases it stays in a circle. Only "away and still facing north" escapes.', r'''
def is_robot_bounded(instructions):
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    x = 0
    y = 0
    facing = 0
    for letter in instructions:
        if letter == "G":
            x += directions[facing][0]
            y += directions[facing][1]
        elif letter == "R":
            facing = (facing + 1) % 4
        else:
            facing = (facing + 3) % 4
    return (x == 0 and y == 0) or facing != 0
''', [('is_robot_bounded("GGLLGG")', True), ('is_robot_bounded("GG")', False), ('is_robot_bounded("GL")', True)])
lc(391, 'Perfect Rectangle', 'perfect-rectangle', 'h', 'Areas add up and only four corners stay', 'The small areas must add up to the big box. Toggle every corner in a set: inner corners appear an even number of times and cancel out, so exactly the four outer corners must be left.', r'''
def is_rectangle_cover(rectangles):
    area = 0
    corners = set()
    for x1, y1, x2, y2 in rectangles:
        area += (x2 - x1) * (y2 - y1)
        for corner in ((x1, y1), (x1, y2), (x2, y1), (x2, y2)):
            if corner in corners:
                corners.remove(corner)
            else:
                corners.add(corner)
    left = min(r[0] for r in rectangles)
    bottom = min(r[1] for r in rectangles)
    right = max(r[2] for r in rectangles)
    top = max(r[3] for r in rectangles)
    outer = {(left, bottom), (left, top), (right, bottom), (right, top)}
    return corners == outer and area == (right - left) * (top - bottom)
''', [('is_rectangle_cover([[1, 1, 3, 3], [3, 1, 4, 2], [3, 2, 4, 4], [1, 3, 2, 4], [2, 3, 3, 4]])', True), ('is_rectangle_cover([[1, 1, 2, 3], [1, 3, 2, 4], [3, 1, 4, 2], [3, 2, 4, 4]])', False), ('is_rectangle_cover([[1, 1, 3, 3], [3, 1, 4, 2], [1, 3, 2, 4], [2, 2, 4, 4]])', False)])
lc(850, 'Rectangle Area II', 'rectangle-area-ii', 'h', 'Coordinate compression on a grid', 'Collect every x and y edge, sort them and mark which small cells between them are covered. Add up the covered cells and take the result modulo 10<sup>9</sup> + 7.', r'''
def rectangle_area(rectangles):
    xs = sorted({x for r in rectangles for x in (r[0], r[2])})
    ys = sorted({y for r in rectangles for y in (r[1], r[3])})
    x_index = {x: i for i, x in enumerate(xs)}
    y_index = {y: i for i, y in enumerate(ys)}
    covered = [[False] * len(ys) for _ in xs]
    for x1, y1, x2, y2 in rectangles:
        for i in range(x_index[x1], x_index[x2]):
            for j in range(y_index[y1], y_index[y2]):
                covered[i][j] = True
    total = 0
    for i in range(len(xs) - 1):
        for j in range(len(ys) - 1):
            if covered[i][j]:
                total += (xs[i + 1] - xs[i]) * (ys[j + 1] - ys[j])
    return total % (10 ** 9 + 7)
''', [('rectangle_area([[0, 0, 2, 2], [1, 0, 2, 3], [1, 0, 3, 1]])', 6), ('rectangle_area([[0, 0, 1000000000, 1000000000]])', 49)])

K.lesson('leetcode', 'LeetCode practice', leet('<p>Window programs are full of screen geometry. These problems practise it: moving a robot like an item on a canvas, the paint bucket tool (flood fill), boxes that overlap like widgets or game objects, points on a line, squares, and the area covered by many rectangles.</p>'), kw=['LeetCode', 'geometry', 'flood fill', 'BFS', 'rectangles', 'overlap', 'simulation', 'coordinate compression'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'tkinter comes with Python. Make root = tk.Tk(), add widgets with their parent, place them, then call root.mainloop().',
    'mainloop waits for events and calls your functions. command=function, without brackets. bind(event, function) for keys and mouse.',
    'grid with sticky and weight for forms, pack for simple stacks, never both in one parent.',
    'StringVar, IntVar and BooleanVar keep widgets in step. The Canvas draws items you move with move and coords, animated with after().',
    'Callbacks must return fast: after() for timers and steps, threads with a queue for slow work. Keep the model apart from the view so you can test it.'],
    'Next: how Python itself runs your code, from source to bytecode.')}
{files('Three tasks: place keypad buttons in a grid, read and centre window geometry strings, and write a to do list model with undo.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'Which call shows the window and starts handling events?', ['root.show()', 'root.mainloop()', 'root.run()', 'root.pack()'], 1, 'The event loop.', 'The program stays in mainloop until the window is closed.')
K.quiz('e', 'Which geometry manager places widgets in rows and columns?', ['pack', 'grid', 'place', 'table'], 1, 'Rows and columns.', 'grid(row=..., column=...).')
K.quiz('e', 'Which widget is made for one line of text that the user types?', ['Label', 'Entry', 'Canvas', 'Frame'], 1, 'Input.', 'Read it with entry.get(). Text is for many lines.')
K.quiz('m', 'What happens with tk.Button(root, text="Go", command=go())?', ['go runs on every click', 'go runs once while the button is made, and clicks then do nothing', 'An error at once', 'go runs when the window closes'], 1, 'Brackets call the function.', 'Write command=go, or command=lambda: go(arg) to pass arguments.')
K.quiz('m', 'A callback calls time.sleep(5). What does the user see?', ['A progress bar', 'The window freezes for 5 seconds', 'Nothing changes', 'The window closes'], 1, 'mainloop is blocked.', 'Use after() or a thread with a queue instead.')
K.quiz('m', 'What does sticky="ew" do in grid?', ['Hides the widget', 'Stretches the widget from the left to the right edge of its cell', 'Moves it to the top', 'Makes the column wider'], 1, 'East and west.', 'n, s, e and w are the compass sides of the cell.')
K.quiz('m', 'How do you make a label show the value of a StringVar named msg and update by itself?', ['Label(root, text=msg)', 'Label(root, textvariable=msg)', 'Label(root, var=msg)', 'msg.pack()'], 1, 'textvariable.', 'Every msg.set(...) changes the label.')
K.quiz('m', 'Where is the point (0, 0) on a Canvas?', ['Bottom left', 'Top left', 'The centre', 'Bottom right'], 1, 'Screens count from the top.', 'y grows downwards.')
K.quiz('h', 'You use pack for one widget and grid for another, both with root as parent. What happens?', ['Both work', 'Tk raises TclError because the managers would fight', 'grid wins', 'pack wins'], 1, 'One manager per parent.', 'Put the groups in separate Frames.')
K.quiz('h', 'A worker thread has finished a download. How should it show the result in a label?', ['label.config(...) from the thread', 'Put the result in a queue.Queue and let an after() callback in the main thread show it', 'Call root.mainloop() again', 'Use time.sleep in the main thread'], 1, 'Tk is not thread safe.', 'Only the main thread touches widgets.')
K.quiz('h', 'Why does a bound handler need a parameter, as in def on_key(event)?', ['It does not', 'Tk passes an event object with details such as keysym, x and y', 'For self', 'To return a value'], 1, 'Event details.', 'command= functions get no argument, bind functions get one.')
K.quiz('x', 'In the style of a CMU human computer interaction exam: by Fitts\'s law, why are menus at the top edge of the screen (as on macOS) fast to hit?', ['They are bigger', 'The pointer stops at the edge, so the target is in effect infinitely deep and you cannot overshoot', 'They are closer', 'They use bigger fonts'], 1, 'Edges stop the mouse.', 'W becomes very large in the direction of the movement, so log<sub>2</sub>(D / W + 1) is close to 0.')
K.quiz('x', 'In the style of a Stanford systems exam: why do almost all GUI toolkits use ONE UI thread with an event queue instead of locking every widget?', ['Threads are slow', 'Events flow down from the app and up from the system at the same time, so per widget locks easily deadlock. One thread handles events in order.', 'Python has a GIL', 'Widgets cannot be locked'], 1, 'Two directions of calls.', 'Qt, Android, iOS, browsers and Tk all follow the single UI thread rule.')

K.calc('e', 'after(20, move) calls move again every 20 ms. How many times a second is that?', '50', '1000 / 20.', ['1 second = 1000 ms.', '1000 / 20.', eq('50 frames a second')], check=1000 // 20)
K.calc('e', 'Centre a 300 pixel wide window on a 1920 pixel wide screen. What is x?', '810', '(1920 &minus; 300) // 2.', ['1920 &minus; 300 = 1620.', '1620 // 2.', eq('810')], check=(1920 - 300) // 2)
K.calc('e', '12 keypad buttons go in a grid with 3 columns. How many rows are there?', '4', '12 / 3.', ['Each row holds 3 buttons.', '12 / 3.', eq('4 rows')], check=12 // 3)
K.calc('m', 'A ball moves 4 pixels every 20 ms. How many pixels does it move in one second?', '200', '4 &times; 50.', ['50 steps a second.', '4 pixels each.', eq('200 pixels a second')], check=4 * (1000 // 20))
K.calc('m', 'For 60 frames a second, what whole number of milliseconds do you pass to after(), rounded down?', '16', '1000 / 60.', ['1000 / 60 = 16.67.', 'after needs a whole number.', eq('16 ms')], check=1000 // 60)
K.calc('m', 'The window gets 300 pixels wider. Column 0 has weight 1 and column 1 has weight 2. How many extra pixels does column 1 get?', '200', '300 &times; 2 / 3.', ['The weights add up to 3.', '300 &times; 2 / 3.', eq('200 pixels')], check=300 * 2 // 3)
K.calc('m', 'The colour "#ff8000" has which green value from 0 to 255?', '128', 'The middle two hex digits.', ['#rrggbb: green is 80.', '8 &times; 16 + 0.', eq('128')], check=int('80', 16))
K.calc('h', 'Fitts\'s law with a = 0.1 s and b = 0.15 s. A 20 pixel button is 300 pixels away. How many seconds does the click take?', '0.7', 'log<sub>2</sub>(300 / 20 + 1) = 4.', ['D / W + 1 = 16.', '0.1 + 0.15 &times; 4.', eq('0.7 s')], check=round(0.1 + 0.15 * 4, 2))
K.calc('h', 'Hick\'s law with b = 0.2 s. How many seconds does it take to choose from a menu of 7 equal items?', '0.6', 'b &times; log<sub>2</sub>(7 + 1).', ['log<sub>2</sub> 8 = 3.', '0.2 &times; 3.', eq('0.6 s')], check=round(0.2 * 3, 2))
K.calc('x', 'In the style of a CMU human computer interaction exam: with b = 0.1 s, how many seconds faster is a 80 pixel target at 560 pixels than a 20 pixel target at 620 pixels?', '0.2', 'Compare log<sub>2</sub>(D / W + 1).', ['620 / 20 + 1 = 32, log<sub>2</sub> = 5.', '560 / 80 + 1 = 8, log<sub>2</sub> = 3. 0.1 &times; (5 &minus; 3).', eq('0.2 s')], check=round(0.1 * (5 - 3), 2))

K.assign('keypad', 'e', 'Place keypad buttons in a grid',
         '<p>Write <code>keypad_layout(labels, columns)</code>. A window puts buttons in a grid in reading order: left to right, then the next row. Return a list of [label, row, column] for every label. With 3 columns, the 4th button goes to row 1, column 0. Hint: divmod.</p>',
         '''
def keypad_layout(labels, columns):
    layout = []
    for index, label in enumerate(labels):
        row = index % columns
        column = index // columns
        layout.append([label, row, column])
    return layout
''', [('keypad_layout(["7", "8", "9", "4"], 3)', [['7', 0, 0], ['8', 0, 1], ['9', 0, 2], ['4', 1, 0]]), ('keypad_layout([], 3)', []), ('keypad_layout(["a", "b", "c"], 1)', [['a', 0, 0], ['b', 1, 0], ['c', 2, 0]])],
         '''
def keypad_layout(labels, columns):
    layout = []
    for index, label in enumerate(labels):
        row, column = divmod(index, columns)
        layout.append([label, row, column])
    return layout
''', 'The row is index // columns and the column is index % columns. The starter swapped them. divmod(index, columns) gives both at once.', '<p>In the window you would then write: for label, row, column in keypad_layout(...): ttk.Button(root, text=label).grid(row=row, column=column).</p>')
K.assign('geometry', 'm', 'Read and centre window geometry strings',
         '<p>Tk describes a window with a geometry string such as "300x200+810+440": width x height, then +x +y (the offsets may also start with -). Write <code>parse_geometry(text)</code> that returns a dict with width, height, x and y as ints, with x and y None when the text is only "300x200". Raise ValueError for anything else. Also write <code>center(width, height, screen_width, screen_height)</code> that returns the geometry string that centres the window, using whole numbers.</p>',
         '''
def parse_geometry(text):
    size, x, y = text.split("+")
    width, height = size.split("x")
    return {"width": int(width), "height": int(height), "x": int(x), "y": int(y)}


def center(width, height, screen_width, screen_height):
    x = (screen_width - width) / 2
    y = (screen_height - height) / 2
    return f"{width}x{height}+{x}+{y}"


def error_of(text):
    try:
        parse_geometry(text)
    except ValueError:
        return "ValueError"
    return "no error"
''', [('parse_geometry("300x200+810+440")', {'width': 300, 'height': 200, 'x': 810, 'y': 440}), ('parse_geometry("640x480")', {'width': 640, 'height': 480, 'x': None, 'y': None}), ('parse_geometry("200x100-0+20")', {'width': 200, 'height': 100, 'x': 0, 'y': 20}), ('center(300, 200, 1920, 1080)', '300x200+810+440'), ('center(301, 201, 1366, 768)', '301x201+532+283'), ('error_of("big")', 'ValueError'), ('error_of("300x200+10")', 'ValueError')],
         '''
import re

GEOMETRY = re.compile(r"(\\d+)x(\\d+)(?:([+-]\\d+)([+-]\\d+))?")


def parse_geometry(text):
    match = GEOMETRY.fullmatch(text.strip())
    if match is None:
        raise ValueError(f"not a geometry string: {text!r}")
    width, height, x, y = match.groups()
    return {"width": int(width), "height": int(height),
            "x": int(x) if x is not None else None, "y": int(y) if y is not None else None}


def center(width, height, screen_width, screen_height):
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    return f"{width}x{height}+{x}+{y}"


def error_of(text):
    try:
        parse_geometry(text)
    except ValueError:
        return "ValueError"
    return "no error"
''', 'Use re.fullmatch with an optional group for the offsets, and // for whole pixels. The starter breaks on "640x480", on "-0" and gives 810.0 instead of 810.', '<p>int("-0") is 0 and int("+20") is 20, so the sign can stay in the group. In Tk a minus offset counts from the right or bottom edge of the screen.</p>')
K.assign('todomodel', 'h', 'Write a to do list model with undo',
         '<p>Write the class <code>TodoModel</code>, the logic behind a to do window. add(text) strips the text and ignores it when it is empty or already in the list (ignoring upper and lower case). remove(index) removes one task and raises IndexError unless 0 &lt;= index &lt; number of tasks (so -1 is not allowed). undo() undoes the last add or remove that really happened, and a removed task goes back to its old place. undo() with nothing to undo does nothing. items() returns a copy of the list. The helper play(commands) runs commands such as ("add", "Milk") and returns [items, number of IndexErrors].</p>',
         '''
class TodoModel:
    def __init__(self):
        self.tasks = []
        self.history = []

    def add(self, text):
        text = text.strip()
        if not text:
            return False
        self.tasks.append(text)
        self.history.append(("add", len(self.tasks) - 1, text))
        return True

    def remove(self, index):
        text = self.tasks.pop(index)
        self.history.append(("remove", index, text))

    def undo(self):
        if self.history:
            action, index, text = self.history.pop()
            if action == "add":
                self.tasks.pop(index)

    def items(self):
        return list(self.tasks)


def play(commands):
    model = TodoModel()
    errors = 0
    for command in commands:
        name = command[0]
        try:
            getattr(model, name)(*command[1:])
        except IndexError:
            errors += 1
    return [model.items(), errors]
''', [('play([("add", "Milk"), ("add", " Bread "), ("add", "")])', [['Milk', 'Bread'], 0]), ('play([("add", "Milk"), ("add", "milk")])', [['Milk'], 0]), ('play([("add", "A"), ("add", "B"), ("add", "C"), ("remove", 1), ("undo",)])', [['A', 'B', 'C'], 0]), ('play([("remove", 0), ("undo",), ("add", "A"), ("undo",), ("undo",)])', [[], 1]), ('play([("add", "A"), ("remove", -1)])', [['A'], 1]), ('play([("add", "A"), ("add", "B"), ("remove", 0), ("add", "C"), ("undo",), ("undo",)])', [['A', 'B'], 0])],
         '''
class TodoModel:
    def __init__(self):
        self.tasks = []
        self.history = []

    def add(self, text):
        text = text.strip()
        if not text:
            return False
        for task in self.tasks:
            if task.lower() == text.lower():
                return False
        self.tasks.append(text)
        self.history.append(("add", len(self.tasks) - 1, text))
        return True

    def remove(self, index):
        if not 0 <= index < len(self.tasks):
            raise IndexError(f"no task number {index}")
        text = self.tasks.pop(index)
        self.history.append(("remove", index, text))

    def undo(self):
        if not self.history:
            return
        action, index, text = self.history.pop()
        if action == "add":
            self.tasks.pop(index)
        else:
            self.tasks.insert(index, text)

    def items(self):
        return list(self.tasks)


def play(commands):
    model = TodoModel()
    errors = 0
    for command in commands:
        name = command[0]
        try:
            getattr(model, name)(*command[1:])
        except IndexError:
            errors += 1
    return [model.items(), errors]
''', 'Three gaps in the starter: no duplicate check, Python\'s pop(-1) accepts -1, and undo forgets removes. Save (action, index, text) for each change and insert the text back at index.', '<p>Because the model knows nothing about tkinter, all of this is tested without a window. The window only calls add, remove and undo and then redraws the list box from items().</p>')

K.must('First window', 'root = tk.Tk(), title, geometry("WxH"), Label, Button(command=f), pack, root.mainloop(). command=f without brackets.')
K.must('Layout', 'grid(row, column, sticky="nsew", columnspan, padx, pady), columnconfigure(i, weight=1), pack(side, fill, expand), place(x, y). One manager per parent.')
K.must('Input and variables', 'Entry.get, insert, delete. StringVar, IntVar, BooleanVar, textvariable, variable, trace_add("write", f). messagebox, filedialog.')
K.must('Events and Canvas', 'bind("<Button-1>", f) with event.x, event.y, event.keysym. create_line, create_oval, move, coords. after(ms, f) for animation.')
K.must('Responsive apps', 'Callbacks return fast. after() for timers, threads plus queue.Queue for slow work, widgets only from the main thread. Model apart from the view.')

T = K.topic(
    slug='py-tkinter', topic='py-tkinter', step=(6, 'The standard library toolbox: text, data, databases and GUIs', 'py-a6', 'Find patterns in text, read and write data formats, store data in SQLite, and build desktop windows with tkinter.', 'Advanced'),
    title='Desktop windows with tkinter', short='tkinter GUIs', badge='6.4', minutes=90,
    lead='Build real desktop windows with the toolkit that comes with Python. Learn widgets, layouts with grid and pack, control variables, events, drawing and animation on a Canvas, and how to keep a window alive during long tasks.',
    desc='tkinter Tk, mainloop and the event loop, Label, Button, command, Entry, Text, Checkbutton, Radiobutton, Scale, Listbox, Scrollbar, Canvas, ttk widgets, pack, grid, place, sticky, weight, columnspan, StringVar, IntVar, BooleanVar, trace_add, bind and event strings, after, messagebox, apps as classes, model and view apart, threads with a queue, screen coordinates, Fitts and Hick laws.',
    summary='tkinter widgets, layouts, variables, events, Canvas animation with after() and responsive apps.',
    keywords=['tkinter', 'GUI', 'ttk', 'mainloop', 'grid', 'pack', 'Canvas', 'bind', 'after', 'event loop'],
    recap='<p>Make widgets, place them with grid, connect events to short callbacks, and let mainloop do the waiting.</p>',
    added='2026-11-07', leet=leet_items(), gui=gui_files())
