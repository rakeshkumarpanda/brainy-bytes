# Advanced Python 2.3: context managers. Follows PCPP-32-101 block 1 (the with statement, __enter__ and __exit__,
# context managers in the standard library), checked against the Python 3.14 language reference (the with
# statement, including several managers in one with and the bracketed form), the data model section "With
# Statement Context Managers", the contextlib documentation (contextmanager, suppress, redirect_stdout, chdir,
# closing, nullcontext, ExitStack, ContextDecorator) and PEP 343.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, lc, leet, files, grow, leet_items

chapter('py-context')
K = Kit()

K.code('files', r'''
import os
import tempfile

path = os.path.join(tempfile.mkdtemp(), "notes.txt")

with open(path, "w") as f:                     # the file is closed when the block ends
    f.write("line one\n")
print("closed after with?", f.closed)

try:
    with open(path) as f:
        print(f.readline().strip())
        raise ValueError("something went wrong")
except ValueError as err:
    print("error:", err, "| closed anyway?", f.closed)

# what with saves you from writing by hand
f = open(path)
try:
    print(len(f.read()), "characters")
finally:
    f.close()
print(f.closed)
''')

K.code('protocol', r'''
class Door:
    def __enter__(self):
        print("open")
        return "room"                          # this value goes into "as"

    def __exit__(self, kind, err, tb):
        print("close, got:", kind.__name__ if kind else None, err)
        return False                           # do not hide errors


with Door() as place:
    print("inside the", place)

try:
    with Door():
        print(1 / 0)
        print("never printed")
except ZeroDivisionError:
    print("the error still reached us")
''')

K.code('suppress', r'''
from contextlib import suppress


class IgnoreMissing:
    def __enter__(self):
        return self

    def __exit__(self, kind, err, tb):
        return kind is not None and issubclass(kind, KeyError)   # True hides the error


prices = {"tea": 10}
with IgnoreMissing():
    print(prices["coffee"])
print("carried on after a KeyError")

with suppress(FileNotFoundError):              # the ready made version
    open("no-such-file.txt")
print("carried on after FileNotFoundError")

try:
    with suppress(KeyError):
        print(1 / 0)                           # a different error is NOT hidden
except ZeroDivisionError as err:
    print("not suppressed:", err)
''')

K.code('generator', r'''
from contextlib import contextmanager


@contextmanager
def temporary(settings, key, value):
    old = settings.get(key)
    settings[key] = value                      # set up: like __enter__
    try:
        yield settings                         # the with body runs here
    finally:
        settings[key] = old                    # clean up: like __exit__, even after an error


config = {"mode": "live"}
with temporary(config, "mode", "test") as c:
    print("inside:", c["mode"])
print("after:", config["mode"])

try:
    with temporary(config, "mode", "debug"):
        raise RuntimeError("crash")
except RuntimeError:
    print("after a crash:", config["mode"])


@temporary(config, "mode", "audit")            # works as a decorator too
def report():
    return "report made in " + config["mode"] + " mode"


print(report(), "|", config["mode"])
''')

K.code('stdlib', r'''
import io
import os
import tempfile
import threading
from contextlib import redirect_stdout, chdir, closing, nullcontext
from decimal import Decimal, localcontext

buffer = io.StringIO()
with redirect_stdout(buffer):                  # capture print output
    print("this goes into the buffer")
print("captured:", repr(buffer.getvalue()))

start = os.getcwd()
with tempfile.TemporaryDirectory() as folder:  # deleted when the block ends
    with chdir(folder):                        # Python 3.11 and later
        print("inside a temp folder:", os.getcwd() != start)
    print("back home:", os.getcwd() == start)
print("folder deleted:", not os.path.exists(folder))

with localcontext() as ctx:
    ctx.prec = 4
    print(Decimal(1) / Decimal(7))
print(Decimal(1) / Decimal(7))

lock = threading.Lock()
with lock:                                     # acquire, then always release
    print("locked:", lock.locked())
print("locked:", lock.locked())


class Connection:
    def close(self):
        print("connection closed")


with closing(Connection()):                    # calls .close() at the end
    print("using the connection")

with nullcontext("no set up needed") as value: # a stand in that does nothing
    print(value)
''')

K.code('many', r'''
class Named:
    def __init__(self, name):
        self.name = name

    def __enter__(self):
        print("enter", self.name)
        return self.name

    def __exit__(self, kind, err, tb):
        print("exit", self.name)
        return False


with Named("A") as a, Named("B") as b:
    print("body with", a, b)

with (
    Named("outer") as x,
    Named("inner") as y,                       # the bracket form (Python 3.10 and later)
):
    print("body with", x, y)
''')

K.code('exitstack', r'''
import os
import tempfile
from contextlib import ExitStack

folder = tempfile.mkdtemp()
names = ["a.txt", "b.txt", "c.txt"]            # how many files is only known at run time

with ExitStack() as stack:
    files = []
    for name in names:
        f = stack.enter_context(open(os.path.join(folder, name), "w"))
        files.append(f)
    stack.callback(print, "callback: every file is about to close")
    for number, f in enumerate(files, start=1):
        f.write("file " + str(number))
    print("open now:", sum(1 for f in files if not f.closed))
print("open after:", sum(1 for f in files if not f.closed))
''')

K.lesson('idea', 'Context managers and the with statement', f'''
{src('Python 3.14 language reference (the with statement), the data model section on context managers, the contextlib documentation, PEP 343 and PCPP-32-101 block 1.')}
{wwh('A <b>context manager</b> is an object that sets something up at the start of a block and cleans it up at the end, whatever happens in between. The <b>with</b> statement uses it: with open(path) as f: opens a file and promises to close it.',
     'Programs borrow things that must be given back: files, network connections, locks, temporary folders, changed settings. If an error happens halfway, or a return leaves early, the clean up line is easy to skip. A leaked file or a lock that is never released can crash a server hours later. Writing try and finally everywhere works but is long and easy to get wrong.',
     'with X as v: calls X.__enter__() and stores its return value in v. The body runs. When the body ends, normally, by return, or by an exception, Python calls X.__exit__(type, error, traceback). If __exit__ returns a true value the exception is suppressed, otherwise it continues.')}
{viz('pywith')}
{run('files')}
{note('A file object is its own context manager: its __exit__ calls close(). Always open files with with. In CPython an unclosed file is usually closed by garbage collection, but other Pythons (PyPy) and long running programs can run out of file handles first.', 'tip')}
''', kw=['context manager', 'with', 'open', 'close', 'clean up', 'try finally', 'resource'])

K.lesson('protocol', 'Writing a context manager class', f'''
{run('protocol')}
{table(['Method', 'Called', 'Gets', 'Returns'], [
    ['__enter__(self)', 'When the with line runs', 'Nothing else', 'The value stored by as (often self, a file, or a connection)'],
    ['__exit__(self, kind, err, tb)', 'When the block ends, for ANY reason', 'None, None, None, or the exception type, object and traceback', 'True to hide the exception, False or None to let it continue']])}
{versus('Making sure clean up runs', ['', 'clean up as the last line', 'try and finally', 'with and a context manager'], [
    ['Runs after an error', 'No', 'Yes', 'Yes'],
    ['Runs after return or break', 'No', 'Yes', 'Yes'],
    ['Code at each use', 'One line, often forgotten', 'Four or more lines', 'One line'],
    ['Set up and clean up kept together', 'No', 'No, they are far apart', 'Yes, in one class or function'],
    ['Reusable', 'No', 'No', 'Yes']],
    'write the set up and clean up once as a context manager, then every user gets safe clean up with one with line.')}
''', kw=['__enter__', '__exit__', 'as', 'exception arguments', 'traceback', 'try finally'])

K.lesson('suppress', 'Suppressing exceptions', f'''
{run('suppress')}
{note('Only return True from __exit__ on purpose and only for the exact errors you expect. Hiding every error makes bugs invisible. contextlib.suppress(SomeError) is the clear, ready made way to say "this error is fine here".', 'warn')}
{versus('Ignoring an expected error', ['', 'try / except / pass', 'with suppress(Error)'], [
    ['Lines', 'Four', 'Two'],
    ['Says what it means', 'Not at a glance', 'Yes'],
    ['Can run code on the error', 'Yes', 'No'],
    ['Other errors', 'Pass through', 'Pass through']],
    'use suppress when you only want to ignore one kind of error. Use try and except when you need to do something about it.')}
''', kw=['suppress', 'return True', 'swallow exception', 'KeyError', 'FileNotFoundError'])

K.lesson('generator', 'contextmanager: a context manager from a generator', f'''
{run('generator')}
{note('Everything before yield is the set up, the yielded value goes into as, and everything after yield is the clean up. The try and finally around the yield is what makes the clean up run after an error: without it, an exception in the body would be raised at the yield and skip the rest.', 'exam')}
{versus('Two ways to write a context manager', ['', 'a class with __enter__ and __exit__', '@contextmanager on a generator'], [
    ['Code', 'Longer', 'Short'],
    ['Keeps state between uses', 'Yes, in attributes', 'Only for one with'],
    ['Can decide to hide errors', 'Return True from __exit__', 'Catch the error around yield and do not re raise'],
    ['Can be used as a decorator', 'With ContextDecorator', 'Yes, automatically'],
    ['Best for', 'Reusable objects like connections', 'Quick set up and clean up pairs']],
    'start with @contextmanager. Write a class when the manager is an object that does more than set up and clean up.')}
''', kw=['contextmanager', 'yield', 'try finally', 'decorator', 'ContextDecorator', 'temporary setting'])

K.lesson('stdlib', 'Context managers in the standard library', f'''
{run('stdlib')}
{table(['Context manager', 'Set up', 'Clean up'], [
    ['open(...)', 'Open a file', 'Close it'],
    ['threading.Lock()', 'Acquire the lock', 'Release it'],
    ['tempfile.TemporaryDirectory()', 'Make a folder', 'Delete it with everything inside'],
    ['contextlib.chdir(path)', 'Change the working folder', 'Change back'],
    ['contextlib.redirect_stdout(f)', 'Send print to f', 'Send it back to the screen'],
    ['decimal.localcontext()', 'A private copy of the decimal settings', 'Restore the old settings'],
    ['contextlib.closing(obj)', 'Nothing', 'Call obj.close()'],
    ['contextlib.nullcontext(v)', 'Nothing, gives v', 'Nothing'],
    ['sqlite3 connection', 'Start a transaction', 'Commit, or roll back on error (it does not close)'],
    ['unittest.mock.patch(...)', 'Replace an object for a test', 'Put the original back']])}
{note('nullcontext is handy when a with is sometimes needed and sometimes not: lock if threaded else nullcontext().', 'tip')}
''', kw=['threading.Lock', 'TemporaryDirectory', 'chdir', 'redirect_stdout', 'localcontext', 'closing', 'nullcontext', 'sqlite3', 'mock.patch'])

K.lesson('many', 'Several managers and ExitStack', f'''
{run('many')}
{note('Managers are entered left to right and exited in the reverse order, like a stack: the last one opened is the first one closed. That is what you want: an inner resource that depends on an outer one is cleaned up first.', 'exam')}
{run('exitstack')}
{note('ExitStack is for when the number of managers is only known while the program runs. enter_context adds a manager, callback adds any function to call at the end, and everything is cleaned up in reverse order, even if opening the third file fails.', 'tip')}
{deep('async with', '<p>Async code uses async with and the methods __aenter__ and __aexit__ (or @contextlib.asynccontextmanager), so the set up and clean up can await network calls. Advanced 5.2 uses it with asyncio.</p>')}
''', kw=['multiple managers', 'exit order', 'LIFO', 'ExitStack', 'enter_context', 'callback', 'async with', '__aenter__'])

K.lesson('maths', 'The maths: leaks, failures and exit order', f'''
{fxs(fx('Exit order of n nested managers', 'the k-th one entered is the (n &minus; k + 1)-th one exited', 'with A, B, C: A is entered 1st and exited 3rd.', key=True),
     fx('Chance that at least one of n steps fails', '1 &minus; (1 &minus; p)<sup>n</sup>', 'Each of 10 steps fails with p = 0.01: 1 &minus; 0.99<sup>10</sup> &asymp; 9.6 %. Errors are common, so clean up must not depend on success.', key=True),
     fx('Expected leaks without with', 'leaks = calls &times; p (chance a path forgets to close)', '1000 calls with p = 0.02 leak about 20 files. With with: 0.'),
     fx('Time until a leaking server runs out of file handles', 'requests = free handles / leaks per request', '1024 handles and 2 leaks per request: 512 requests.'),
     fx('Elapsed time with a timer context manager', 'elapsed = t<sub>exit</sub> &minus; t<sub>enter</sub>', 'Entered at 1.50 s, exited at 2.75 s: 1.25 s.'))}
{steps('Worked example: a server that leaks file handles', [
    '2000 requests per minute, and 5 % of them forget to close a file: 2000 &times; 0.05 = 100 leaks per minute.',
    'The limit is 1024 open handles and 24 are in use: 1000 are free.',
    'Minutes until the limit: 1000 / 100.',
    eq('10 minutes, then every open() fails. A with statement makes the leak rate 0.')])}
''', kw=['exit order', 'failure probability', 'resource leak', 'file descriptor limit', 'elapsed time'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>Open files with with and know the file is closed afterwards, even after an error.</p>',
    '<p>Write context manager classes with __enter__ and __exit__, and generator based ones with @contextmanager and try and finally.</p>',
    '<p>Suppress exact errors on purpose, use several managers in one with, ExitStack for a dynamic number, and the standard ones: locks, temporary folders, chdir, redirect_stdout, localcontext.</p>',
    '<p>with is defined by PEP 343: Python looks up __enter__ and __exit__ on the TYPE (not the object), calls __exit__ with the exception triple, and treats a true result as suppression. @contextmanager wraps the generator and throws the body exception in at the yield. ExitStack unwinds callbacks in LIFO order and chains exceptions raised during clean up.</p>')}
{grow('Use with for files.', 'Write context managers both ways.', 'Combine managers and explain the protocol exactly.')}
''', kw=['beginner', 'expert', 'PEP 343', 'exception triple'])

lc(636, 'Exclusive Time of Functions', 'exclusive-time-of-functions', 'm', 'A stack of running functions', 'Logs open and close like nested with blocks. Keep a stack of running ids. When something starts or ends, give the time since the last event to the function on top.', r'''
def exclusive_time(n, logs):
    result = [0] * n
    stack = []
    previous = 0
    for entry in logs:
        func_id, kind, time = entry.split(":")
        func_id = int(func_id)
        time = int(time)
        if kind == "start":
            if stack:
                result[stack[-1]] += time - previous
            stack.append(func_id)
            previous = time
        else:
            result[stack.pop()] += time - previous + 1
            previous = time + 1
    return result
''', [('exclusive_time(2, ["0:start:0", "1:start:2", "1:end:5", "0:end:6"])', [3, 4]), ('exclusive_time(1, ["0:start:0", "0:start:2", "0:end:5", "0:start:6", "0:end:6", "0:end:7"])', [8])])
lc(946, 'Validate Stack Sequences', 'validate-stack-sequences', 'm', 'Replay the pushes and pops on a real stack', 'Push each value. After every push, pop while the top is the next value that should come out. It works if the stack ends empty, just as every with block must close in reverse order.', r"""
def validate_stack_sequences(pushed, popped):
    stack = []
    i = 0
    for value in pushed:
        stack.append(value)
        while stack and stack[-1] == popped[i]:
            stack.pop()
            i += 1
    return not stack
""", [('validate_stack_sequences([1, 2, 3, 4, 5], [4, 5, 3, 2, 1])', True), ('validate_stack_sequences([1, 2, 3, 4, 5], [4, 3, 5, 1, 2])', False), ('validate_stack_sequences([], [])', True)])
lc(921, 'Minimum Add to Make Parentheses Valid', 'minimum-add-to-make-parentheses-valid', 'm', 'Count open brackets', 'Track how many "(" are still open. A ")" with nothing open needs an added "(". At the end every open one needs a ")".', r'''
def min_add_to_make_valid(s):
    open_count = 0
    added = 0
    for ch in s:
        if ch == "(":
            open_count += 1
        elif open_count > 0:
            open_count -= 1
        else:
            added += 1
    return added + open_count
''', [('min_add_to_make_valid("())")', 1), ('min_add_to_make_valid("(((")', 3), ('min_add_to_make_valid("()))((")', 4)])
lc(1249, 'Minimum Remove to Make Valid Parentheses', 'minimum-remove-to-make-valid-parentheses', 'm', 'A stack of open positions', 'Push the index of each "(". A ")" with an empty stack is removed. Any "(" left on the stack at the end is removed too.', r'''
def min_remove_to_make_valid(s):
    chars = list(s)
    stack = []
    for i in range(len(chars)):
        if chars[i] == "(":
            stack.append(i)
        elif chars[i] == ")":
            if stack:
                stack.pop()
            else:
                chars[i] = ""
    for i in stack:
        chars[i] = ""
    return "".join(chars)
''', [('min_remove_to_make_valid("lee(t(c)o)de)")', 'lee(t(c)o)de'), ('min_remove_to_make_valid("a)b(c)d")', 'ab(c)d'), ('min_remove_to_make_valid("))((")', '')])
lc(856, 'Score of Parentheses', 'score-of-parentheses', 'm', 'A stack of scores per level', 'Opening starts a new level with score 0. Closing turns the level into 1 if it was empty, or double its score otherwise, and adds it to the level outside.', r'''
def score_of_parentheses(s):
    stack = [0]
    for ch in s:
        if ch == "(":
            stack.append(0)
        else:
            inner = stack.pop()
            stack[-1] += max(2 * inner, 1)
    return stack[0]
''', [('score_of_parentheses("()")', 1), ('score_of_parentheses("(())")', 2), ('score_of_parentheses("()()")', 2), ('score_of_parentheses("(()(()))")', 6)])
lc(1190, 'Reverse Substrings Between Each Pair of Parentheses', 'reverse-substrings-between-each-pair-of-parentheses', 'm', 'A stack of unfinished text', 'On "(" save the text so far and start fresh. On ")" reverse the inner text and glue it to the saved text.', r'''
def reverse_parentheses(s):
    stack = []
    text = ""
    for ch in s:
        if ch == "(":
            stack.append(text)
            text = ""
        elif ch == ")":
            text = stack.pop() + text[::-1]
        else:
            text += ch
    return text
''', [('reverse_parentheses("(abcd)")', 'dcba'), ('reverse_parentheses("(u(love)i)")', 'iloveu'), ('reverse_parentheses("(ed(et(oc))el)")', 'leetcode')])
lc(32, 'Longest Valid Parentheses', 'longest-valid-parentheses', 'h', 'A stack of indexes with a base', 'Keep the index of the last unmatched position at the bottom of the stack. After each match, the length is the current index minus the index on top.', r'''
def longest_valid_parentheses(s):
    stack = [-1]
    best = 0
    for i in range(len(s)):
        if s[i] == "(":
            stack.append(i)
        else:
            stack.pop()
            if not stack:
                stack.append(i)                # a new base
            else:
                best = max(best, i - stack[-1])
    return best
''', [('longest_valid_parentheses("(()")', 2), ('longest_valid_parentheses(")()())")', 4), ('longest_valid_parentheses("")', 0)])
lc(735, 'Asteroid Collision', 'asteroid-collision', 'm', 'A stack of survivors', 'Only a left moving asteroid can hit the right moving ones on the stack. Pop the smaller ones, stop if it is destroyed.', r'''
def asteroid_collision(asteroids):
    stack = []
    for rock in asteroids:
        alive = True
        while alive and rock < 0 and stack and stack[-1] > 0:
            if stack[-1] < -rock:
                stack.pop()
            elif stack[-1] == -rock:
                stack.pop()
                alive = False
            else:
                alive = False
        if alive:
            stack.append(rock)
    return stack
''', [('asteroid_collision([5, 10, -5])', [5, 10]), ('asteroid_collision([8, -8])', []), ('asteroid_collision([10, 2, -5])', [10]), ('asteroid_collision([-2, -1, 1, 2])', [-2, -1, 1, 2])])
lc(844, 'Backspace String Compare', 'backspace-string-compare', 'e', 'Build each text with a stack', 'Push letters, pop on "#". Compare the two results.', r'''
def typed(text):
    stack = []
    for ch in text:
        if ch == "#":
            if stack:
                stack.pop()
        else:
            stack.append(ch)
    return stack


def backspace_compare(s, t):
    return typed(s) == typed(t)
''', [('backspace_compare("ab#c", "ad#c")', True), ('backspace_compare("ab##", "c#d#")', True), ('backspace_compare("a#c", "b")', False)])
lc(2390, 'Removing Stars From a String', 'removing-stars-from-a-string', 'm', 'A stack again', 'Each star removes the closest letter on its left: push letters and pop on "*".', r'''
def remove_stars(s):
    stack = []
    for ch in s:
        if ch == "*":
            stack.pop()
        else:
            stack.append(ch)
    return "".join(stack)
''', [('remove_stars("leet**cod*e")', 'lecoe'), ('remove_stars("erase*****")', '')])

K.lesson('leetcode', 'LeetCode practice', leet('<p>with blocks nest like brackets: the last one opened is the first one closed. Every problem here uses a stack for that same reason, from timing nested function calls to matching brackets and replaying pushes and pops.</p>'), kw=['LeetCode', 'stack', 'parentheses', 'nested', 'exclusive time', 'stack sequences'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'with X as v: runs X.__enter__() (its return value goes into v), then the body, then X.__exit__(type, error, traceback), whatever happens.',
    'Clean up in __exit__ runs after errors, return and break, so resources are never leaked.',
    '__exit__ returning True hides the exception. Use contextlib.suppress for the exact errors you expect.',
    '@contextmanager: code before yield is set up, after yield is clean up. Wrap the yield in try and finally.',
    'Standard managers: open, locks, TemporaryDirectory, chdir, redirect_stdout, localcontext, closing, nullcontext, mock.patch.',
    'Several managers enter left to right and exit right to left. ExitStack handles a number known only at run time.'],
    'Step 3 is about writing professional code: style, type hints, tests, logging and debugging.')}
{files('Three tasks: a Setting manager that always restores a value, a log_block generator manager, and a Transaction that rolls back and hides only ValueError.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'What does with open("a.txt") as f: guarantee?', ['The file is read faster', 'The file is closed when the block ends, even after an error', 'The file is created', 'Nothing'], 1, 'Clean up.', "The file's __exit__ closes it.")
K.quiz('e', 'Which two methods make an object a context manager?', ['__init__ and __del__', '__enter__ and __exit__', '__open__ and __close__', '__iter__ and __next__'], 1, 'The protocol.', 'with calls __enter__ at the start and __exit__ at the end.')
K.quiz('e', 'In with Door() as place:, what is stored in place?', ['The Door object always', 'What __enter__ returns', 'What __exit__ returns', 'None'], 1, 'as takes the enter value.', 'Often __enter__ returns self, but it can return anything.')
K.quiz('m', 'What arguments does __exit__ get when the body finished without an error?', ['Nothing', 'None, None, None', 'True', 'The return value of the body'], 1, 'No exception.', 'Type, value and traceback are all None.')
K.quiz('m', '__exit__ returns True after a ZeroDivisionError in the body. What happens?', ['The error continues', 'The error is suppressed and the program goes on after the block', 'The body runs again', 'Python crashes'], 1, 'A true result.', 'True means "handled", so the exception is not raised further.')
K.quiz('m', 'In a @contextmanager function, why put yield inside try and finally?', ['For speed', 'So the clean up after yield runs even if the body raises', 'Because yield needs it', 'To return a value'], 1, 'The error arrives at the yield.', 'An exception in the body is thrown in at the yield, so code after it would be skipped without finally.')
K.quiz('m', 'with A() as a, B() as b: in which order do the managers exit?', ['A then B', 'B then A', 'At the same time', 'It depends on the errors'], 1, 'Like a stack.', 'Last entered, first exited.')
K.quiz('m', 'What does contextlib.suppress(KeyError) do with a ZeroDivisionError in the body?', ['Hides it too', 'Lets it pass through', 'Turns it into a KeyError', 'Logs it'], 1, 'Only the named errors.', 'suppress only hides the exception types you list.')
K.quiz('h', 'What does a sqlite3 connection used in a with block do at the end?', ['Closes the connection', 'Commits, or rolls back if there was an error, but stays open', 'Nothing', 'Deletes the database'], 1, 'A transaction manager.', 'It manages the transaction, not the connection. Close it separately or use closing().')
K.quiz('h', 'You need to open a list of files whose length is known only at run time, all in one with. What do you use?', ['A loop of with statements', 'contextlib.ExitStack', 'nullcontext', 'threading.Lock'], 1, 'A dynamic number.', 'ExitStack.enter_context adds managers one by one and closes them all in reverse.')
K.quiz('h', 'Where does Python look for __enter__ and __exit__?', ['On the object first', 'On the type of the object', 'In globals', 'In the module'], 1, 'Special method lookup.', 'Like other special methods, they are looked up on the class, so adding them to an instance does not work.')
K.quiz('x', 'In the style of a CMU 15-213 exam: why is with lock: safer than lock.acquire() ... lock.release()?', ['It is faster', 'release still runs if the code in between raises or returns, so the lock cannot stay held for ever', 'It uses less memory', 'It allows two threads in'], 1, 'Deadlock.', 'A lock left held after an error blocks every other thread for ever.')
K.quiz('x', 'In the style of a Stanford CS 110 exam: __exit__ itself raises a new error while handling one from the body. What does the caller see?', ['Only the original error', 'The new error, with the original one as its __context__', 'Both are lost', 'Nothing'], 1, 'Chaining.', 'An error raised during handling replaces the first one, which is kept as __context__.')

K.calc('e', 'with A() as a, B() as b, C() as c: In which position (1, 2 or 3) does A exit?', '3', 'Reverse order.', ['Entered: A, B, C.', 'Exited: C, B, A.', eq('A exits 3rd')], check=3)
K.calc('e', 'A timer manager is entered at 1.50 s and exited at 2.75 s. How many seconds passed?', '1.25', 'Exit minus enter.', ['t exit = 2.75.', 't enter = 1.50.', eq('2.75 &minus; 1.50 = 1.25')], check=2.75 - 1.50)
K.calc('e', '1000 calls each forget to close a file with chance 0.02. How many leaked files do you expect?', '20', 'Calls times chance.', ['1000 calls.', 'Chance 0.02 each.', eq('1000 &times; 0.02 = 20')], check=1000 * 0.02)
K.calc('m', 'A server has 1024 free file handles and leaks 2 per request. After how many requests does open() start failing?', '512', 'Free divided by leak.', ['1024 handles.', '2 leaked per request.', eq('1024 / 2 = 512')], check=1024 // 2)
K.calc('m', 'Each of 10 steps fails with chance 0.01. What is the chance in percent that at least one fails (1 decimal place)?', '9.6', '1 &minus; (1 &minus; p)<sup>n</sup>.', ['0.99<sup>10</sup> &asymp; 0.904.', '1 &minus; 0.904 = 0.096.', eq('9.6 %')], check=round((1 - 0.99 ** 10) * 100, 1))
K.calc('m', 'What is score_of_parentheses("(()(()))")?', '6', 'Inside out.', ['() inside counts 1, (()) inside counts 2.', 'Inside the outer pair: 1 + 2 = 3.', eq('The outer pair doubles it: 6')], check=6)
K.calc('m', 'What is min_add_to_make_valid("()))((")?', '4', 'Unmatched on both sides.', ['"()" matches.', 'Two ")" have nothing open: add 2. Two "(" stay open: add 2.', eq('2 + 2 = 4')], check=4)
K.calc('h', 'Logs: "0:start:0", "1:start:2", "1:end:5", "0:end:6". What is the exclusive time of function 1?', '4', 'From 2 to 5 inclusive.', ['Function 1 runs at times 2, 3, 4 and 5.', 'End times count as included.', eq('5 &minus; 2 + 1 = 4')], check=5 - 2 + 1)
K.calc('h', 'Five managers are nested. The 2nd one entered is which one to exit?', '4', 'n &minus; k + 1.', ['n = 5, k = 2.', '5 &minus; 2 + 1.', eq('4th')], check=5 - 2 + 1)
K.calc('x', 'In the style of a CMU 15-213 exam: 2000 requests per minute, 5 % leak one file handle, the limit is 1024 and 24 are in use. After how many minutes is the limit reached?', '10', 'Free handles over leaks per minute.', ['Leaks per minute: 2000 &times; 0.05 = 100.', 'Free handles: 1024 &minus; 24 = 1000.', eq('1000 / 100 = 10 minutes')], check=(1024 - 24) / (2000 * 0.05))

K.assign('setting', 'e', 'A Setting manager that always restores',
         '<p>Write a class <code>Setting(config, key, value)</code>. On enter it puts value into config[key]. On exit it puts back the old value, or removes the key if it was not there before. This must also happen after an error, and errors must not be hidden. use and use_error are helpers that run it.</p>',
         '''
class Setting:
    def __init__(self, config, key, value):
        self.config = config
        self.key = key
        self.value = value

    def __enter__(self):
        self.config[self.key] = self.value
        return self.config

    def __exit__(self, kind, err, tb):
        pass


def use(config):
    with Setting(config, "mode", "test"):
        inside = config["mode"]
    return inside, config.get("mode"), "mode" in config


def use_error(config):
    try:
        with Setting(config, "mode", "test"):
            raise ValueError("boom")
    except ValueError:
        return "error seen", config.get("mode")
    return "error hidden", config.get("mode")
''', [('use({"mode": "live"})', ['test', 'live', True]), ('use({})', ['test', None, False]), ('use_error({"mode": "live"})', ['error seen', 'live'])],
         '''
class Setting:
    def __init__(self, config, key, value):
        self.config = config
        self.key = key
        self.value = value

    def __enter__(self):
        self.had_key = self.key in self.config
        self.old = self.config.get(self.key)
        self.config[self.key] = self.value
        return self.config

    def __exit__(self, kind, err, tb):
        if self.had_key:
            self.config[self.key] = self.old
        else:
            del self.config[self.key]
        return False


def use(config):
    with Setting(config, "mode", "test"):
        inside = config["mode"]
    return inside, config.get("mode"), "mode" in config


def use_error(config):
    try:
        with Setting(config, "mode", "test"):
            raise ValueError("boom")
    except ValueError:
        return "error seen", config.get("mode")
    return "error hidden", config.get("mode")
''', 'In __enter__ remember whether the key existed and its old value. In __exit__ restore it or delete it, and return False.', '<p>Remembering "was it there" separately from the old value matters: a key whose value is None is not the same as a missing key.</p>')
K.assign('logblock', 'm', 'A log_block manager with @contextmanager',
         '<p>Write <code>log_block(log, name)</code> with @contextmanager. It appends "start name" to the list log, then runs the body. If the body works it appends "end name". If the body raises, it appends "error name: ErrorType" and lets the error continue. ok and bad are helpers.</p>',
         '''
from contextlib import contextmanager


@contextmanager
def log_block(log, name):
    log.append("start " + name)
    yield
    log.append("end " + name)


def ok():
    log = []
    with log_block(log, "load"):
        log.append("working")
    return log


def bad():
    log = []
    try:
        with log_block(log, "save"):
            raise KeyError("x")
    except KeyError:
        return log, "KeyError reached the caller"
    return log, "error hidden"


def nested():
    log = []
    with log_block(log, "outer"):
        with log_block(log, "inner"):
            pass
    return log
''', [('ok()', ['start load', 'working', 'end load']), ('bad()', [['start save', 'error save: KeyError'], 'KeyError reached the caller']), ('nested()', ['start outer', 'start inner', 'end inner', 'end outer'])],
         '''
from contextlib import contextmanager


@contextmanager
def log_block(log, name):
    log.append("start " + name)
    try:
        yield
    except Exception as err:
        log.append("error " + name + ": " + type(err).__name__)
        raise
    log.append("end " + name)


def ok():
    log = []
    with log_block(log, "load"):
        log.append("working")
    return log


def bad():
    log = []
    try:
        with log_block(log, "save"):
            raise KeyError("x")
    except KeyError:
        return log, "KeyError reached the caller"
    return log, "error hidden"


def nested():
    log = []
    with log_block(log, "outer"):
        with log_block(log, "inner"):
            pass
    return log
''', 'Wrap the yield in try and except Exception as err. Append the error line and use a bare raise to send the same error on.', '<p>A bare raise inside except re raises the error with its original traceback. Forgetting it would silently swallow every error in the body.</p>')
K.assign('transaction', 'h', 'A Transaction that rolls back',
         '<p>Write a class <code>Transaction(account)</code> for a dict like {"balance": 100}. On enter it saves the balance and returns itself. It has <code>deposit(n)</code> and <code>withdraw(n)</code>, and withdraw raises ValueError if the balance would go below 0. On exit after ANY error it restores the saved balance. It hides ValueError (returns True) but lets every other error continue. run is a helper.</p>',
         '''
class Transaction:
    def __init__(self, account):
        self.account = account

    def __enter__(self):
        return self

    def deposit(self, n):
        self.account["balance"] += n

    def withdraw(self, n):
        self.account["balance"] -= n

    def __exit__(self, kind, err, tb):
        return False


def run(steps):
    account = {"balance": 100}
    try:
        with Transaction(account) as t:
            for action, amount in steps:
                if action == "crash":
                    raise RuntimeError("power cut")
                getattr(t, action)(amount)
    except RuntimeError:
        return account["balance"], "RuntimeError passed on"
    return account["balance"], "finished"
''', [('run([("deposit", 50), ("withdraw", 30)])', [120, 'finished']), ('run([("deposit", 50), ("withdraw", 500)])', [100, 'finished']), ('run([("deposit", 50), ("crash", 0)])', [100, 'RuntimeError passed on'])],
         '''
class Transaction:
    def __init__(self, account):
        self.account = account

    def __enter__(self):
        self.saved = self.account["balance"]
        return self

    def deposit(self, n):
        self.account["balance"] += n

    def withdraw(self, n):
        if self.account["balance"] - n < 0:
            raise ValueError("not enough money")
        self.account["balance"] -= n

    def __exit__(self, kind, err, tb):
        if kind is None:
            return False
        self.account["balance"] = self.saved   # roll back after any error
        return issubclass(kind, ValueError)    # hide only ValueError


def run(steps):
    account = {"balance": 100}
    try:
        with Transaction(account) as t:
            for action, amount in steps:
                if action == "crash":
                    raise RuntimeError("power cut")
                getattr(t, action)(amount)
    except RuntimeError:
        return account["balance"], "RuntimeError passed on"
    return account["balance"], "finished"
''', 'Save the balance in __enter__. In __exit__, if kind is not None, restore it, then return issubclass(kind, ValueError).', '<p>This is how database transactions work: all the changes in the block happen, or none of them do. sqlite3 connections behave the same way in a with block.</p>')

K.must('The with protocol', 'with X as v: v = X.__enter__(), body, then X.__exit__(type, err, tb) always. Methods are looked up on the type.')
K.must('Suppressing', '__exit__ returning True hides the exception. contextlib.suppress(Error) hides only the listed types.')
K.must('@contextmanager', 'Set up, then yield the as value inside try, then clean up in finally. Re raise errors you do not handle. Works as a decorator.')
K.must('Standard managers', 'open, Lock, TemporaryDirectory, chdir, redirect_stdout, localcontext, closing, nullcontext, sqlite3 (transaction), mock.patch.')
K.must('Several managers', 'Entered left to right, exited right to left. Bracketed form across lines. ExitStack: enter_context and callback for a dynamic number.')

T = K.topic(
    slug='py-context', topic='py-context', step=(2, 'Iterators, generators and context managers', 'py-a2', 'Work with data one value at a time, use the itertools and functools toolbox, and manage resources safely with with.', 'Advanced'),
    title='Context managers and the with statement', short='Context managers', badge='2.3', minutes=70,
    lead='Never leak a file, lock or setting again. Learn what with really does, how to write context managers as classes and with @contextmanager, how to suppress exactly the right errors, the managers in the standard library, several managers at once and ExitStack.',
    desc='the with statement, __enter__ and __exit__, the as target, exception arguments, suppressing with a true return value, contextlib.suppress, @contextmanager with try and finally, using a manager as a decorator, open, threading.Lock, TemporaryDirectory, chdir, redirect_stdout, decimal.localcontext, closing, nullcontext, sqlite3 transactions, several managers and the bracketed form, exit order, ExitStack with enter_context and callback, async with.',
    summary='with, __enter__ and __exit__, suppressing errors, @contextmanager, standard managers, exit order, ExitStack.',
    keywords=['context manager', 'with', '__enter__', '__exit__', 'contextmanager', 'suppress', 'ExitStack', 'redirect_stdout', 'Lock', 'TemporaryDirectory', 'PCPP'],
    recap='<p>Put set up and clean up together in a context manager, and every with block cleans up, whatever happens inside.</p>',
    added='2026-11-07', leet=leet_items())
