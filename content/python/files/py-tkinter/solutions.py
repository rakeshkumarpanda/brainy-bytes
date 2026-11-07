# 6.4 Desktop windows with tkinter
# Model solutions. Try practice.py first.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>


# ------------------------------------------------------------------ the checker
# check(tests) runs each test and says PASS or FAIL. A test is a pair: the call to make and the answer we expect.
import json


def check(name, tests):
    passed = 0
    for call, expected in tests:
        try:
            got = eval(call)
        except Exception as error:
            got = "error: " + type(error).__name__ + ": " + str(error)
        if json.dumps(got, sort_keys=True, default=repr) == json.dumps(expected, sort_keys=True, default=repr):
            passed = passed + 1
            print("  PASS", call)
        else:
            print("  FAIL", call, "expected", repr(expected), "but got", repr(got))
    print(name + ":", passed, "of", len(tests), "tests pass")
    return passed == len(tests)


# ================================================================== task 1: Place keypad buttons in a grid
# Write keypad_layout(labels, columns). A window puts buttons in a grid in reading order: left to
# right, then the next row. Return a list of [label, row, column] for every label. With 3 columns,
# the 4th button goes to row 1, column 0. Hint: divmod.
# Why it works: In the window you would then write: for label, row, column in keypad_layout(...):
# ttk.Button(root, text=label).grid(row=row, column=column).

def keypad_layout(labels, columns):
    layout = []
    for index, label in enumerate(labels):
        row, column = divmod(index, columns)
        layout.append([label, row, column])
    return layout


# ================================================================== task 2: Read and centre window geometry strings
# Tk describes a window with a geometry string such as "300x200+810+440": width x height, then +x +y
# (the offsets may also start with -). Write parse_geometry(text) that returns a dict with width,
# height, x and y as ints, with x and y None when the text is only "300x200". Raise ValueError for
# anything else. Also write center(width, height, screen_width, screen_height) that returns the
# geometry string that centres the window, using whole numbers.
# Why it works: int("-0") is 0 and int("+20") is 20, so the sign can stay in the group. In Tk a
# minus offset counts from the right or bottom edge of the screen.

import re

GEOMETRY = re.compile(r"(\d+)x(\d+)(?:([+-]\d+)([+-]\d+))?")


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


# ================================================================== task 3: Write a to do list model with undo
# Write the class TodoModel, the logic behind a to do window. add(text) strips the text and ignores
# it when it is empty or already in the list (ignoring upper and lower case). remove(index) removes
# one task and raises IndexError unless 0 <= index < number of tasks (so -1 is not allowed). undo()
# undoes the last add or remove that really happened, and a removed task goes back to its old place.
# undo() with nothing to undo does nothing. items() returns a copy of the list. The helper
# play(commands) runs commands such as ("add", "Milk") and returns [items, number of IndexErrors].
# Why it works: Because the model knows nothing about tkinter, all of this is tested without a
# window. The window only calls add, remove and undo and then redraws the list box from items().

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


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Place keypad buttons in a grid", [('keypad_layout(["7", "8", "9", "4"], 3)', [['7', 0, 0], ['8', 0, 1], ['9', 0, 2], ['4', 1, 0]]), ('keypad_layout([], 3)', []), ('keypad_layout(["a", "b", "c"], 1)', [['a', 0, 0], ['b', 1, 0], ['c', 2, 0]])]))
    results.append(check("Task 2: Read and centre window geometry strings", [('parse_geometry("300x200+810+440")', {'width': 300, 'height': 200, 'x': 810, 'y': 440}), ('parse_geometry("640x480")', {'width': 640, 'height': 480, 'x': None, 'y': None}), ('parse_geometry("200x100-0+20")', {'width': 200, 'height': 100, 'x': 0, 'y': 20}), ('center(300, 200, 1920, 1080)', '300x200+810+440'), ('center(301, 201, 1366, 768)', '301x201+532+283'), ('error_of("big")', 'ValueError'), ('error_of("300x200+10")', 'ValueError')]))
    results.append(check("Task 3: Write a to do list model with undo", [('play([("add", "Milk"), ("add", " Bread "), ("add", "")])', [['Milk', 'Bread'], 0]), ('play([("add", "Milk"), ("add", "milk")])', [['Milk'], 0]), ('play([("add", "A"), ("add", "B"), ("add", "C"), ("remove", 1), ("undo",)])', [['A', 'B', 'C'], 0]), ('play([("remove", 0), ("undo",), ("add", "A"), ("undo",), ("undo",)])', [[], 1]), ('play([("add", "A"), ("remove", -1)])', [['A'], 1]), ('play([("add", "A"), ("add", "B"), ("remove", 0), ("add", "C"), ("undo",), ("undo",)])', [['A', 'B'], 0])]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
