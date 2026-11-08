# 4.2 Django in depth: ORM, migrations, forms, users and tests
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


# ================================================================== task 1: Write a sign up form with Django forms
# Finish SignupForm. The fields and their basic checks are ready. Add clean_username: change the
# name to lower case, raise ValidationError("Use only letters and digits.") when it has anything
# else, and "This name is taken." when it is in TAKEN. Add clean: when both passwords are there but
# differ, add the error "The passwords do not match." to password2. try_signup(data) returns ["ok",
# username] or ["errors", {field: [messages]}].
# Why it works: clean_<field> runs only when the field's own checks passed, so an empty username
# shows "This field is required." and never reaches your method. In a real site you would use
# UserCreationForm, which also checks the password against the validators in
# AUTH_PASSWORD_VALIDATORS.

import django
from django.conf import settings

settings.configure(SECRET_KEY="dev-only")
django.setup()

from django import forms

TAKEN = {"ann", "admin"}


class SignupForm(forms.Form):
    username = forms.CharField(max_length=20)
    email = forms.EmailField()
    password = forms.CharField(min_length=10)
    password2 = forms.CharField()

    def clean_username(self):
        name = self.cleaned_data["username"].lower()
        if not name.isalnum():
            raise forms.ValidationError("Use only letters and digits.")
        if name in TAKEN:
            raise forms.ValidationError("This name is taken.")
        return name

    def clean(self):
        data = super().clean()
        if data.get("password") and data.get("password2") and data["password"] != data["password2"]:
            self.add_error("password2", "The passwords do not match.")
        return data


def try_signup(data):
    form = SignupForm(data)
    if form.is_valid():
        return ["ok", form.cleaned_data["username"]]
    return ["errors", {field: [e["message"] for e in errors] for field, errors in form.errors.get_json_data().items()}]


# ================================================================== task 2: Plan migrations like migrate does
# Each migration lists the migrations it depends on, as in GRAPH. Write apply_plan(dependencies,
# applied): the migrations not applied yet, each one after everything it depends on, and when
# several are free, take them in name order (visit the names sorted, and the parents of each
# sorted). Raise ValueError for a circular dependency. Write rollback_plan(dependencies, applied,
# target): the applied migrations that depend on target, directly or through others, newest first,
# which is what migrate books 0001 undoes.
# Why it works: Django builds the same graph from the dependencies list in every migration file,
# then walks it in this order. That is why two developers who both add a 0002 migration get
# "Conflicting migrations detected" and must run makemigrations --merge.

def apply_plan(dependencies, applied):
    """The migrations still to run, each after the ones it depends on. Ties go in name order."""
    done = set(applied)
    plan = []
    visiting = set()

    def visit(name):
        if name in done:
            return
        if name in visiting:
            raise ValueError(f"circular dependency at {name}")
        visiting.add(name)
        for parent in sorted(dependencies[name]):
            visit(parent)
        visiting.discard(name)
        done.add(name)
        plan.append(name)

    for name in sorted(dependencies):
        visit(name)
    return plan


def rollback_plan(dependencies, applied, target):
    """The applied migrations to undo so that target is the last one left: every migration that needs target, newest first."""
    needs = set()
    changed = True
    while changed:
        changed = False
        for name in applied:
            if name not in needs and (target in dependencies[name] or needs & set(dependencies[name])):
                needs.add(name)
                changed = True
    return [name for name in reversed(applied) if name in needs]


GRAPH = {
    "books.0001": [],
    "books.0002": ["books.0001"],
    "books.0003": ["books.0002", "users.0001"],
    "users.0001": [],
    "users.0002": ["users.0001"],
}


def plan_error(graph):
    try:
        apply_plan(graph, [])
    except ValueError:
        return "ValueError"
    return "no error"


# ================================================================== task 3: Build atomic() with savepoints
# MiniDB keeps balances in a dict. Make atomic() work as a context manager like Django's
# transaction.atomic: when the block ends with an error, every change made inside it is undone and
# the error goes on, and when it ends normally the changes stay. Blocks can be nested: an error in
# an inner block undoes only the inner block, like a savepoint. move() is ready, and it changes the
# receiver before it checks the sender, so a missing atomic leaves money from nowhere.
# bank_story(steps) runs a story and catches the errors of each block.
# Why it works: Databases do this without copying everything: they keep a log of changes and undo
# them on ROLLBACK. Django turns the outer atomic into BEGIN and COMMIT and each inner one into
# SAVEPOINT and RELEASE, exactly the nesting you built here.

import copy


class MiniDB:
    def __init__(self, data):
        self.data = dict(data)
        self.saved = []                      # a stack of copies, one for each open atomic block

    def __enter__(self):
        self.saved.append(copy.deepcopy(self.data))
        return self

    def __exit__(self, kind, error, trace):
        snapshot = self.saved.pop()
        if kind is not None:
            self.data = snapshot             # an error inside the block: undo everything it changed
        return False                         # never hide the error

    def atomic(self):
        return self

    def move(self, sender, receiver, amount):
        if amount <= 0:
            raise ValueError("amount must be positive")
        self.data[receiver] += amount
        if self.data[sender] < amount:
            raise ValueError(f"{sender} has only {self.data[sender]}")
        self.data[sender] -= amount


def bank_story(steps):
    """steps: a list of ("move", sender, receiver, amount) or ("block", [inner steps]). Returns the balances and the errors."""
    db = MiniDB({"ann": 100, "bob": 20, "cat": 0})
    errors = []

    def run(step_list):
        for step in step_list:
            if step[0] == "move":
                db.move(*step[1:])
            else:
                try:
                    with db.atomic():
                        run(step[1])
                except ValueError as e:
                    errors.append(str(e))

    run(steps)
    return [db.data, errors]


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Write a sign up form with Django forms", [('try_signup({"username": "Zed42", "email": "zed@example.com", "password": "long enough 1", "password2": "long enough 1"})', ['ok', 'zed42']), ('try_signup({"username": "ANN", "email": "a@example.com", "password": "long enough 1", "password2": "long enough 1"})', ['errors', {'username': ['This name is taken.']}]), ('try_signup({"username": "zed 42", "email": "zed@example.com", "password": "long enough 1", "password2": "long enough 1"})', ['errors', {'username': ['Use only letters and digits.']}]), ('try_signup({"username": "zed", "email": "zed@example.com", "password": "long enough 1", "password2": "long enough 2"})', ['errors', {'password2': ['The passwords do not match.']}]), ('try_signup({"username": "zed", "email": "nope", "password": "short", "password2": "short"})', ['errors', {'email': ['Enter a valid email address.'], 'password': ['Ensure this value has at least 10 characters (it has 5).']}]), ('try_signup({"username": "", "email": "zed@example.com", "password": "long enough 1", "password2": "long enough 1"})', ['errors', {'username': ['This field is required.']}])]))
    results.append(check("Task 2: Plan migrations like migrate does", [('apply_plan(GRAPH, [])', ['books.0001', 'books.0002', 'users.0001', 'books.0003', 'users.0002']), ('apply_plan(GRAPH, ["books.0001", "users.0001"])', ['books.0002', 'books.0003', 'users.0002']), ('apply_plan(GRAPH, list(GRAPH))', []), ('rollback_plan(GRAPH, ["books.0001", "books.0002", "users.0001", "books.0003", "users.0002"], "books.0001")', ['books.0003', 'books.0002']), ('rollback_plan(GRAPH, ["books.0001", "books.0002", "users.0001", "books.0003", "users.0002"], "users.0001")', ['users.0002', 'books.0003']), ('rollback_plan(GRAPH, ["books.0001"], "books.0001")', []), ('plan_error({"a.0001": ["a.0002"], "a.0002": ["a.0001"]})', 'ValueError')]))
    results.append(check("Task 3: Build atomic() with savepoints", [('bank_story([("move", "ann", "bob", 30)])', [{'ann': 70, 'bob': 50, 'cat': 0}, []]), ('bank_story([("block", [("move", "bob", "cat", 50)])])', [{'ann': 100, 'bob': 20, 'cat': 0}, ['bob has only 20']]), ('bank_story([("block", [("move", "ann", "cat", 10), ("move", "bob", "cat", 99)])])', [{'ann': 100, 'bob': 20, 'cat': 0}, ['bob has only 20']]), ('bank_story([("block", [("move", "ann", "cat", 10), ("block", [("move", "bob", "cat", 99)]), ("move", "ann", "bob", 5)])])', [{'ann': 85, 'bob': 25, 'cat': 10}, ['bob has only 20']]), ('bank_story([("block", [("move", "ann", "bob", 0)]), ("move", "bob", "ann", 20)])', [{'ann': 120, 'bob': 0, 'cat': 0}, ['amount must be positive']])]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
