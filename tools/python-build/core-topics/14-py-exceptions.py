# Core Python 5.1: exceptions. Follows PCEP-30-02 section 4.4 (exceptions: try-except, try-except Exception,
# ordering the except branches, propagating exceptions through function boundaries, delegating responsibility for
# handling exceptions) and PCAP-31-03 section 3 (the hierarchy of exceptions, raise, assert, except as, else, finally,
# exceptions as objects, the args property, defining your own exceptions), checked against the Python 3.14 tutorial
# chapter 8 "Errors and Exceptions" and the library reference "Built-in Exceptions".
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, lc, leet, files, grow, leet_items, term

chapter('py-exceptions')
K = Kit()

K.code('basic', r'''
answers = ["42", "seven", "3.5", " 18 "]

for text in answers:
    try:
        age = int(text)               # may raise ValueError
        print("age is", age)
    except ValueError:
        print(repr(text), "is not a whole number")
print("the program keeps running")
''')

K.code('multi', r'''
def safe_divide(a, b):
    try:
        return a / b
    except ZeroDivisionError:
        return "cannot divide by zero"
    except TypeError as err:          # as err gives you the exception object
        return f"wrong types: {err}"

print(safe_divide(10, 4))
print(safe_divide(10, 0))
print(safe_divide(10, "2"))

prices = {"tea": 10}
for item in ["tea", "cake", 5]:
    try:
        print(item, prices[item] * 2)
    except (KeyError, TypeError) as err:      # one handler, two kinds
        print("problem:", type(err).__name__, err.args)
''')

K.code('order', r'''
def check(value):
    try:
        return 10 / value
    except ZeroDivisionError:                  # the most specific first
        return "zero"
    except ArithmeticError:                    # its parent class
        return "some other arithmetic problem"
    except Exception as err:                   # almost everything
        return "other: " + type(err).__name__

print(check(0))
print(check(10 ** 400))        # too big for a float: OverflowError, a child of ArithmeticError
print(check("x"))
print(issubclass(ZeroDivisionError, ArithmeticError), issubclass(KeyError, LookupError))
print([c.__name__ for c in ZeroDivisionError.__mro__])
''')

K.code('elsefin', r'''
def read_number(text):
    try:
        n = int(text)
    except ValueError:
        print("  except: bad input")
        return None
    else:
        print("  else: only when there was no exception")
        return n
    finally:
        print("  finally: always, even after return")

for t in ["12", "twelve"]:
    print("read_number(" + repr(t) + ")")
    print("  returned", read_number(t))
''')

K.code('propagate', r'''
def average(marks):
    return sum(marks) / len(marks)       # raises for an empty list

def report(marks):
    return "Average: " + str(average(marks))   # does not handle it either

for group in [[70, 80, 90], []]:
    try:
        print(report(group))             # the caller decides what to do
    except ZeroDivisionError:
        print("No marks yet")
''')

K.code('raise', r'''
def set_age(age):
    if not isinstance(age, int):
        raise TypeError("age must be a whole number")
    if age < 0 or age > 150:
        raise ValueError(f"age {age} is not possible")
    return age

for value in [30, -4, "ten"]:
    try:
        print("ok:", set_age(value))
    except (TypeError, ValueError) as err:
        print(type(err).__name__ + ":", err)

def load(text):
    try:
        return int(text)
    except ValueError as err:
        raise RuntimeError("could not load the settings") from err   # keep the cause

try:
    load("abc")
except RuntimeError as err:
    print(err, "| caused by:", repr(err.__cause__))
''')

K.code('reraise', r'''
log = []

def withdraw(balance, amount):
    try:
        if amount > balance:
            raise ValueError("not enough money")
        return balance - amount
    except ValueError:
        log.append(f"failed withdraw of {amount}")
        raise                          # bare raise: log it, then pass the same exception on

try:
    withdraw(100, 500)
except ValueError as err:
    print("caller got:", err)
print(log)
''')

K.code('custom', r'''
class BankError(Exception):
    """Base class for every error of this bank program."""

class InsufficientFunds(BankError):
    def __init__(self, balance, amount):
        super().__init__(f"balance {balance} is less than {amount}")
        self.balance = balance
        self.amount = amount

def withdraw(balance, amount):
    if amount > balance:
        raise InsufficientFunds(balance, amount)
    return balance - amount

try:
    withdraw(300, 1000)
except BankError as err:                 # catches every bank error
    print("Error:", err)
    print("short by", err.amount - err.balance)
print(InsufficientFunds.__mro__[1].__name__)
''')

K.code('assert', r'''
def percent(part, whole):
    assert whole > 0, "whole must be positive"     # a check for programmers
    return 100 * part / whole

print(percent(3, 4))
try:
    percent(1, 0)
except AssertionError as err:
    print("AssertionError:", err)
# python -O turns every assert off, so never use assert to check user input
''')

K.code('eafp', r'''
stock = {"pen": 12, "ink": 0}

# LBYL: look before you leap
if "cap" in stock:
    print(stock["cap"])
else:
    print("no cap (checked first)")

# EAFP: easier to ask forgiveness than permission
try:
    print(stock["cap"])
except KeyError:
    print("no cap (caught the error)")

# For this simple case the dict already has a tool
print(stock.get("cap", 0))
''')

K.code('with', r'''
import os, tempfile
path = os.path.join(tempfile.gettempdir(), "demo_exceptions.txt")

f = open(path, "w")
try:
    f.write("first line\n")
    1 / 0                       # something goes wrong in the middle
except ZeroDivisionError:
    print("handled the error")
finally:
    f.close()                   # the file is closed whatever happened
print("closed:", f.closed)

with open(path, "w") as g:      # with does the same try and finally for you
    g.write("safe\n")
print("closed:", g.closed)
os.remove(path)
''')

K.code('group', r'''
errors = ExceptionGroup("two checks failed", [ValueError("bad age"), KeyError("name")])

try:
    raise errors
except* ValueError as group:       # except* (Python 3.11+) handles part of a group
    print("value problems:", [str(e) for e in group.exceptions])
except* KeyError as group:
    print("missing keys:", [str(e) for e in group.exceptions])
''')

K.lesson('idea', 'When things go wrong: exceptions', f'''
{src('Python 3.14 tutorial chapter 8, library reference Built-in Exceptions, PCEP-30-02 section 4.4 and PCAP-31-03 section 3.')}
{wwh('An <b>exception</b> is an object Python raises when something goes wrong while the program runs: text that is not a number, a missing key, a file that is not there, dividing by zero. If nobody handles it, the program stops and prints a <b>traceback</b>.',
     'Real programs meet bad input, broken networks and missing files every day. A program that crashes on the first typo is useless. Exceptions separate the normal path from the error path, so you can say "try this, and if this kind of problem happens, do that instead", and keep running.',
     'You put risky code in a <b>try</b> block. When an exception is raised, Python stops that block at once and looks for an <b>except</b> clause whose class matches. If it finds one, that handler runs and the program carries on after the try statement. If not, the exception travels up to the caller, then its caller, until something handles it or the program ends.')}
{scene('a payment that fails', '<p>You pay for a train ticket and your bank declines the card. A good app does not freeze or close. It catches the "payment declined" error, shows "Please try another card", keeps your booking details, and lets you try again. That is an except clause. Closing the payment window in every case, success or failure, is the finally clause.</p>')}
{term(['$ python3 crash.py', 'Traceback (most recent call last):', '  File "/tmp/crash.py", line 3, in <module>', '    print(total / len(marks))', '          ~~~~~~^~~~~~~~~~~~', 'ZeroDivisionError: division by zero'], 'An unhandled exception (real Python 3.14 output)')}
{note('Read a traceback from the bottom up. The last line names the exception and the reason. The lines above show where it happened, with the newest call last. Python 3.11 and later mark the exact part of the line with ^ and ~ characters.', 'tip')}
''', kw=['exception', 'error', 'traceback', 'try', 'except', 'crash'])

K.lesson('basic', 'try and except', f'''
{run('basic')}
{versus('Syntax errors and exceptions', ['', 'SyntaxError', 'Exception at run time'], [
    ['When', 'Before the program starts, while Python reads the file', 'While the program runs'],
    ['Example', 'print("hi" (a missing bracket)', 'int("seven"), 10 / 0, {}["x"]'],
    ['Can try and except catch it', 'Not in the same file, which never starts', 'Yes'],
    ['Fix', 'Correct the code', 'Handle it, or prevent the cause']],
    'syntax errors are mistakes in writing. Exceptions are problems that happen while running, often caused by data you cannot control.')}
''', kw=['try except', 'ValueError', 'SyntaxError vs exception', 'handle error'])

K.lesson('multi', 'Several handlers, and the exception object', f'''
{run('multi')}
{table(['Exception', 'Typical cause'], [
    ['ValueError', 'Right type, wrong value: int("seven")'],
    ['TypeError', 'Wrong type: "2" + 3, len(5)'],
    ['ZeroDivisionError', 'Dividing by zero with / // or %'],
    ['IndexError', 'List index out of range: [1, 2][5]'],
    ['KeyError', 'Missing dict key'],
    ['NameError', 'A name that was never defined (UnboundLocalError is its child)'],
    ['AttributeError', 'A missing attribute or method: (5).append(1)'],
    ['FileNotFoundError', 'Opening a file that does not exist (a child of OSError)'],
    ['ImportError and ModuleNotFoundError', 'A module that cannot be found or loaded'],
    ['RecursionError', 'Too deep recursion (a child of RuntimeError)'],
    ['KeyboardInterrupt', 'Ctrl+C. A child of BaseException, not of Exception']])}
''', kw=['except as', 'exception object', 'args', 'multiple except', 'tuple of exceptions', 'common exceptions'])

K.lesson('order', 'The exception hierarchy and the order of handlers', f'''
{viz('pyexc')}
{run('order')}
{wwh('Exceptions are classes arranged in a family tree. ZeroDivisionError is a child of ArithmeticError, which is a child of Exception, which is a child of BaseException.',
     'Sometimes you want to handle one exact problem, sometimes a whole family of related problems. The tree lets one except clause do either.',
     'except SomeClass catches that class <b>and all its children</b>. Python tries the handlers from top to bottom and runs the first match only. So put the most specific classes first. A handler for a parent placed first would catch everything and the specific handlers below it would never run.')}
{note('Avoid a bare except: or except BaseException:. They also catch KeyboardInterrupt and SystemExit, so Ctrl+C stops working. Catch Exception at most, and only where you log or report the error.', 'warn')}
''', kw=['exception hierarchy', 'BaseException', 'Exception', 'ArithmeticError', 'LookupError', 'handler order', 'bare except'])

K.lesson('elsefin', 'else and finally', f'''
{run('elsefin')}
{table(['Clause', 'Runs when'], [
    ['try', 'Always first'],
    ['except X', 'An exception of class X (or a child) was raised in try'],
    ['else', 'try finished with no exception'],
    ['finally', 'Always last: after try, except or else, even after return, break or an unhandled exception']])}
{note('The order is fixed: try, then except clauses, then else, then finally. You need at least one except or a finally. else keeps code out of the try block, so you do not accidentally catch errors from it.', 'exam')}
''', kw=['else clause', 'finally clause', 'cleanup', 'return in finally', 'try except else finally'])

K.lesson('propagate', 'Exceptions travel up through function calls', f'''
{run('propagate')}
{term(['$ python3 crash2.py', 'Traceback (most recent call last):', '  File "/tmp/crash2.py", line 7, in <module>', '    print(report([]))', '          ~~~~~~^^^^', '  File "/tmp/crash2.py", line 5, in report', '    return "Average: " + str(average(marks))', '                             ~~~~~~~^^^^^^^', '  File "/tmp/crash2.py", line 2, in average', '    return sum(marks) / len(marks)', '           ~~~~~~~~~~~^~~~~~~~~~~~', 'ZeroDivisionError: division by zero'], 'The same call without a handler: every level is listed')}
{note('A low level function often cannot know what the right reaction is. average should not print "No marks yet" because it may be used in a web page or a report. Let it raise, and handle the exception at the level that knows what to tell the user. This is called delegating responsibility.', 'tip')}
''', kw=['propagation', 'call stack', 'traceback levels', 'delegate handling'])

K.lesson('raise', 'Raising exceptions yourself', f'''
{run('raise')}
{run('reraise')}
{table(['Form', 'Meaning'], [
    ['raise ValueError("message")', 'Raise a new exception with a message'],
    ['raise ValueError', 'Python makes the object for you, with no message'],
    ['raise (alone, inside except)', 'Raise the same exception again, after logging or cleaning up'],
    ['raise NewError(...) from err', 'Raise a new exception and record err as its cause (__cause__)'],
    ['raise NewError(...) from None', 'Hide the original exception from the traceback']])}
''', kw=['raise', 're-raise', 'raise from', '__cause__', 'exception chaining', 'validation'])

K.lesson('custom', 'Your own exception classes', f'''
{run('custom')}
{note('Make your own exceptions by subclassing Exception (never BaseException). Give your program one base class, such as BankError, and make specific errors its children. Callers can then catch one exact problem or every problem of your program. Classes are explained in Core 6.1.', 'tip')}
''', kw=['custom exception', 'subclass Exception', 'exception attributes', 'super().__init__'])

K.lesson('assert', 'assert: checks for programmers', f'''
{run('assert')}
{versus('assert or raise', ['', 'assert condition, message', 'if not condition: raise ...'], [
    ['Meant for', 'Things that can only fail if the code itself has a bug', 'Bad input, missing files, anything the outside world causes'],
    ['Turned off by python -O', 'Yes', 'No'],
    ['Exception', 'AssertionError', 'Any class you choose']],
    'use assert to document and check your own assumptions while developing, and raise for every check that must always happen.')}
''', kw=['assert', 'AssertionError', 'python -O', 'assert vs raise'])

K.lesson('eafp', 'Two styles: EAFP and LBYL', f'''
{run('eafp')}
{versus('Checking first or catching the error', ['', 'LBYL (look before you leap)', 'EAFP (ask forgiveness)'], [
    ['Code', 'if key in d: use d[key]', 'try: use d[key] then except KeyError'],
    ['Fast when', 'Errors are common', 'Errors are rare (no extra check on the normal path)'],
    ['Race conditions', 'Possible: a file can disappear between the check and the open', 'None: the action itself is the check'],
    ['Python style', 'Fine for simple checks', 'Preferred by most Python code']],
    'use EAFP for files, network calls and conversions, and simple if checks or get() when they read more clearly.')}
''', kw=['EAFP', 'LBYL', 'race condition', 'pythonic error handling'])

K.lesson('with', 'Cleaning up: finally and with', f'''
{run('with')}
{note('A with statement uses a context manager that closes the file (or releases a lock, or ends a database transaction) even when an exception happens. It is the short, safe form of try and finally. Advanced 2.2 shows how to write your own.', 'tip')}
{run('group')}
{deep('Exception groups', '<p>Since Python 3.11 a program can raise several unrelated exceptions at once in an ExceptionGroup, for example when ten network tasks run together and three fail (Advanced 5.1). except* picks out the parts of the group it can handle and lets the rest travel on.</p>')}
''', kw=['with statement', 'context manager', 'cleanup', 'ExceptionGroup', 'except star'])

K.lesson('maths', 'Counting and reasoning about failures', f'''
{fxs(fx('Handlers checked before a match', 'position of the first matching except clause', 'Python stops at the first match, so order decides the cost and the meaning.', key=True),
     fx('Chance that at least one of n independent steps fails', '1 &minus; (1 &minus; p)<sup>n</sup>', 'With p = 1 percent per network call, 50 calls fail at least once with chance 1 &minus; 0.99<sup>50</sup> &asymp; 39 percent. Errors are normal at scale, so handle them.', key=True),
     fx('Expected tries until success (retry loop)', '1 / q', 'If each try succeeds with chance q = 0.8, you need 1.25 tries on average (a geometric distribution).'),
     fx('Exponential back off before retry k', 'wait = base &times; 2<sup>k</sup>', '1, 2, 4, 8 seconds. Used by web clients so a busy server is not flooded (Web 2.2).'))}
{steps('Worked example: a 3 step booking with failure chances 2, 5 and 1 percent', [
    'Chance that every step works: 0.98 &times; 0.95 &times; 0.99.',
    '0.98 &times; 0.95 = 0.931, and 0.931 &times; 0.99 = 0.92169.',
    eq('Chance of at least one failure: 1 &minus; 0.92169 &asymp; 7.8 percent'),
    'About 1 booking in 13 meets an error, so every step needs a clear except path.'])}
''', kw=['probability of failure', 'retry', 'geometric distribution', 'exponential backoff'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>An exception is an error while the program runs. try runs risky code, except handles a problem, and the program goes on.</p>',
    '<p>Catch specific classes, most specific first. Use as err to read the message. else runs when nothing failed, finally always runs. Exceptions travel up through function calls until something handles them.</p>',
    '<p>Raise your own errors with raise, re-raise with a bare raise, chain causes with from, write custom exception classes, use assert only for programmer checks, prefer EAFP, and close resources with with.</p>',
    '<p>CPython 3.11 made try blocks zero cost: entering a try does nothing at run time, and only raising looks up an exception table. Tracebacks are linked frame objects (__traceback__), which can keep large objects alive if you store an exception. Exception groups and except* support structured concurrency in asyncio TaskGroup.</p>')}
{grow('Wrap a risky line in try and except ValueError and keep the program running.',
      'Order several handlers, use else and finally, and let errors propagate to the right level.',
      'Design an exception hierarchy for a program, chain causes, and choose between EAFP and LBYL.')}
''', kw=['beginner', 'expert', 'zero cost exceptions', 'traceback object', 'TaskGroup'])

lc(20, 'Valid Parentheses', 'valid-parentheses', 'e', 'Stack', 'Push every opening bracket. A closing bracket must match the top of the stack. At the end the stack must be empty.', r'''
def is_valid(s):
    pairs = {")": "(", "]": "[", "}": "{"}
    stack = []
    for ch in s:
        if ch in "([{":
            stack.append(ch)
        else:
            if not stack or stack[-1] != pairs[ch]:
                return False
            stack.pop()
    return not stack
''', [('is_valid("()[]{}")', True), ('is_valid("(]")', False), ('is_valid("([)]")', False), ('is_valid("{[]}")', True), ('is_valid("(")', False)])
lc(1614, 'Maximum Nesting Depth of the Parentheses', 'maximum-nesting-depth-of-the-parentheses', 'e', 'Counter', 'Add 1 for "(" and take 1 for ")". The answer is the largest value the counter reaches.', r'''
def max_depth(s):
    depth = 0
    best = 0
    for ch in s:
        if ch == "(":
            depth = depth + 1
            if depth > best:
                best = depth
        elif ch == ")":
            depth = depth - 1
    return best
''', [('max_depth("(1+(2*3)+((8)/4))+1")', 3), ('max_depth("(1)+((2))+(((3)))")', 3), ('max_depth("1")', 0)])
lc(1021, 'Remove Outermost Parentheses', 'remove-outermost-parentheses', 'e', 'Depth counter', 'Keep a bracket only when it is not at depth 0 before an opening or after a closing.', r'''
def remove_outer_parentheses(s):
    result = []
    depth = 0
    for ch in s:
        if ch == "(":
            if depth > 0:
                result.append(ch)
            depth = depth + 1
        else:
            depth = depth - 1
            if depth > 0:
                result.append(ch)
    return "".join(result)
''', [('remove_outer_parentheses("(()())(())")', '()()()'), ('remove_outer_parentheses("()()")', '')])
lc(682, 'Baseball Game', 'baseball-game', 'e', 'Stack of scores', '"+" adds the last two, "D" doubles the last, "C" removes the last, anything else is a number.', r'''
def cal_points(operations):
    scores = []
    for op in operations:
        if op == "+":
            scores.append(scores[-1] + scores[-2])
        elif op == "D":
            scores.append(scores[-1] * 2)
        elif op == "C":
            scores.pop()
        else:
            scores.append(int(op))
    return sum(scores)
''', [('cal_points(["5", "2", "C", "D", "+"])', 30), ('cal_points(["5", "-2", "4", "C", "D", "9", "+", "+"])', 27)])
lc(8, 'String to Integer (atoi)', 'string-to-integer-atoi', 'm', 'Careful parsing', 'Skip leading spaces, read one optional sign, read digits until something else, then clamp to the 32 bit range.', r'''
def my_atoi(s):
    i = 0
    n = len(s)
    while i < n and s[i] == " ":
        i = i + 1
    sign = 1
    if i < n and s[i] in "+-":
        if s[i] == "-":
            sign = -1
        i = i + 1
    value = 0
    while i < n and "0" <= s[i] <= "9":
        value = value * 10 + int(s[i])
        i = i + 1
    value = value * sign
    low = -(2 ** 31)
    high = 2 ** 31 - 1
    if value < low:
        return low
    if value > high:
        return high
    return value
''', [('my_atoi("42")', 42), ('my_atoi("   -042")', -42), ('my_atoi("1337c0d3")', 1337), ('my_atoi("words 987")', 0), ('my_atoi("-91283472332")', -2147483648)])
lc(150, 'Evaluate Reverse Polish Notation', 'evaluate-reverse-polish-notation', 'm', 'Stack', 'Numbers go on a stack. An operator pops two numbers, applies itself and pushes the result. Division truncates toward zero.', r'''
def eval_rpn(tokens):
    stack = []
    for t in tokens:
        if t in ("+", "-", "*", "/"):
            b = stack.pop()
            a = stack.pop()
            if t == "+":
                stack.append(a + b)
            elif t == "-":
                stack.append(a - b)
            elif t == "*":
                stack.append(a * b)
            else:
                stack.append(int(a / b))
        else:
            stack.append(int(t))
    return stack[0]
''', [('eval_rpn(["2", "1", "+", "3", "*"])', 9), ('eval_rpn(["4", "13", "5", "/", "+"])', 6), ('eval_rpn(["10", "6", "9", "3", "+", "-11", "*", "/", "*", "17", "+", "5", "+"])', 22)])
lc(468, 'Validate IP Address', 'validate-ip-address', 'm', 'Validate every part', 'IPv4: 4 parts of digits, 0 to 255, no leading zero. IPv6: 8 parts of 1 to 4 hex digits. Check characters yourself, because int() also accepts signs and spaces.', r'''
def valid_ipv4_part(part):
    if len(part) == 0 or len(part) > 3:
        return False
    for ch in part:
        if not ("0" <= ch <= "9"):
            return False
    if len(part) > 1 and part[0] == "0":
        return False
    return int(part) <= 255


def valid_ipv6_part(part):
    if len(part) == 0 or len(part) > 4:
        return False
    for ch in part:
        if ch not in "0123456789abcdefABCDEF":
            return False
    return True


def valid_ip_address(query_ip):
    if query_ip.count(".") == 3:
        parts = query_ip.split(".")
        if all(valid_ipv4_part(p) for p in parts):
            return "IPv4"
    if query_ip.count(":") == 7:
        parts = query_ip.split(":")
        if all(valid_ipv6_part(p) for p in parts):
            return "IPv6"
    return "Neither"
''', [('valid_ip_address("172.16.254.1")', 'IPv4'), ('valid_ip_address("2001:0db8:85a3:0:0:8A2E:0370:7334")', 'IPv6'), ('valid_ip_address("256.256.256.256")', 'Neither'), ('valid_ip_address("01.1.1.1")', 'Neither')])
lc(71, 'Simplify Path', 'simplify-path', 'm', 'Stack of folder names', 'Split on "/". Skip "" and ".", pop for "..", push anything else. Join with "/".', r'''
def simplify_path(path):
    stack = []
    for part in path.split("/"):
        if part == "" or part == ".":
            continue
        if part == "..":
            if stack:
                stack.pop()
        else:
            stack.append(part)
    return "/" + "/".join(stack)
''', [('simplify_path("/home/")', '/home'), ('simplify_path("/home//foo/")', '/home/foo'), ('simplify_path("/home/user/Documents/../Pictures")', '/home/user/Pictures'), ('simplify_path("/../")', '/')])
lc(227, 'Basic Calculator II', 'basic-calculator-ii', 'm', 'Stack with the previous operator', 'Read a number, then apply the operator before it: + and &minus; push, * and / combine with the top of the stack. Sum the stack.', r'''
def calculate(s):
    stack = []
    number = 0
    op = "+"
    s = s + "+"
    for ch in s:
        if ch == " ":
            continue
        if "0" <= ch <= "9":
            number = number * 10 + int(ch)
            continue
        if op == "+":
            stack.append(number)
        elif op == "-":
            stack.append(-number)
        elif op == "*":
            stack.append(stack.pop() * number)
        else:
            stack.append(int(stack.pop() / number))
        op = ch
        number = 0
    return sum(stack)
''', [('calculate("3+2*2")', 7), ('calculate(" 3/2 ")', 1), ('calculate(" 3+5 / 2 ")', 5), ('calculate("14-3/2")', 13)])
lc(65, 'Valid Number', 'valid-number', 'h', 'Scan with a few flags', 'Track whether you saw a digit, a dot and an exponent. A sign is allowed only at the start or right after e. A dot is not allowed after e.', r'''
def is_number(s):
    seen_digit = False
    seen_dot = False
    seen_exp = False
    for i in range(len(s)):
        ch = s[i]
        if "0" <= ch <= "9":
            seen_digit = True
        elif ch in "+-":
            if i > 0 and s[i - 1] not in "eE":
                return False
        elif ch == ".":
            if seen_dot or seen_exp:
                return False
            seen_dot = True
        elif ch in "eE":
            if seen_exp or not seen_digit:
                return False
            seen_exp = True
            seen_digit = False
        else:
            return False
    return seen_digit
''', [('is_number("0")', True), ('is_number("e")', False), ('is_number(".")', False), ('is_number("2e10")', True), ('is_number("-90E3")', True), ('is_number("99e2.5")', False), ('is_number("--6")', False), ('is_number("+.8")', True), ('is_number("4.")', True), ('is_number("1e")', False)])

K.lesson('leetcode', 'LeetCode practice', leet('<p>Error handling is mostly about checking input carefully. These problems are all about validating and parsing text, where a missed case means a wrong answer, exactly like a missed except clause in real code.</p>'), kw=['LeetCode', 'valid parentheses', 'stack', 'atoi', 'reverse polish notation', 'validate IP address', 'valid number'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'An <b>exception</b> is raised when something goes wrong while the program runs. Unhandled, it stops the program with a traceback. Read tracebacks from the bottom.',
    '<b>try</b> holds risky code. <b>except X</b> handles X and its child classes. <b>as err</b> gives the exception object.',
    'Handlers are checked top to bottom and only the first match runs, so put specific classes first.',
    '<b>else</b> runs when try raised nothing. <b>finally</b> always runs, even after return.',
    'Exceptions travel up the call stack until handled. Handle them where you know what to do.',
    '<b>raise</b> X("message") raises, a bare raise re-raises, and raise ... from err records the cause.',
    'Write your own exceptions as subclasses of Exception. Use assert only for programmer checks.',
    'Prefer EAFP for files and conversions, and with for anything that must be closed.'],
    'Core 5.2 shows how Python finds and loads modules and packages, and how pip installs new ones.')}
{files('Three tasks: a safe integer reader, a validator that raises the right exceptions, and a retry helper.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'What does int("abc") raise?', ['TypeError', 'ValueError', 'SyntaxError', 'NameError'], 1, 'Right type, wrong value.', 'The text cannot be read as a whole number.')
K.quiz('e', 'Which block always runs?', ['try', 'except', 'else', 'finally'], 3, 'Always.', 'finally runs in every case.')
K.quiz('e', 'What does [1, 2, 3][5] raise?', ['KeyError', 'IndexError', 'ValueError', 'None'], 1, 'A list position.', 'Index 5 is out of range.')
K.quiz('m', 'When does the else block of a try run?', ['When an exception happened', 'When no exception happened', 'Always', 'Never'], 1, 'No error.', 'else runs only when try finished without an exception.')
K.quiz('m', 'Which except catches ZeroDivisionError?', ['except ValueError', 'except LookupError', 'except ArithmeticError', 'except KeyError'], 2, 'Its parent.', 'ZeroDivisionError is a child of ArithmeticError.')
K.quiz('m', 'Which is the parent class of KeyError and IndexError?', ['ValueError', 'LookupError', 'NameError', 'TypeError'], 1, 'Looking something up.', 'Both are children of LookupError.')
K.quiz('m', 'What does a bare raise inside an except block do?', ['Nothing', 'Raises the same exception again', 'Raises RuntimeError', 'Ends the program quietly'], 1, 'Pass it on.', 'It re-raises the exception being handled.')
K.quiz('m', 'Your own exception class should inherit from', ['BaseException', 'Exception', 'object', 'Error'], 1, 'Not the root.', 'Subclass Exception so Ctrl+C handling is not affected.')
K.quiz('h', 'def f(): try: return 1 finally: return 2. What is f()?', ['1', '2', 'None', 'Error'], 1, 'finally runs last.', 'The return in finally replaces the return in try. (Python 3.14 warns about this, PEP 765.)')
K.quiz('h', 'except Exception first and except ValueError second. What happens with ValueError?', ['The ValueError handler runs', 'The Exception handler runs', 'Both run', 'Error'], 1, 'First match wins.', 'ValueError is a child of Exception, so the first handler catches it.')
K.quiz('h', 'Which is NOT a child of Exception?', ['ValueError', 'KeyboardInterrupt', 'OSError', 'StopIteration'], 1, 'Ctrl+C.', 'KeyboardInterrupt inherits directly from BaseException.')
K.quiz('x', 'In the style of a Stanford CS41 exam: what does python -O do to assert x &gt; 0, "bad"?', ['Makes it faster but still checks', 'Removes it completely', 'Turns it into a warning', 'Raises at import time'], 1, 'Optimise flag.', 'With -O, __debug__ is False and every assert statement is removed.')
K.quiz('x', 'In the style of a CMU 15-112 exam: 50 independent requests each fail with chance 2 percent. Which is closest to the chance that at least one fails?', ['2 percent', '36 percent', '64 percent', '100 percent'], 2, '1 &minus; 0.98<sup>50</sup>.', '0.98<sup>50</sup> &asymp; 0.364, so the chance of at least one failure is about 64 percent.')

K.calc('e', 'How many lines does the basic example print?', '5', 'One per answer and one at the end.', ['Four answers, each prints one line.', 'Then "the program keeps running".', eq('5')], check=5)
K.calc('e', 'int(" 18 ") gives', '18', 'Spaces around are allowed.', ['int() strips spaces at both ends.', 'The digits are 18.', eq('18')], check=int(' 18 '))
K.calc('e', 'Number of except clauses that run when one exception is raised and several match.', '1', 'First match only.', ['Python checks from the top.', 'It runs the first matching handler only.', eq('1')], check=1)
K.calc('m', 'Chance (percent, whole number) that at least one of 50 calls fails, each failing with 1 percent.', '39', '1 &minus; 0.99<sup>50</sup>.', ['0.99<sup>50</sup> &asymp; 0.605.', '1 &minus; 0.605 = 0.395.', eq('about 39 percent')], check=int(100 * (1 - 0.99 ** 50)))
K.calc('m', 'Expected number of tries when each try succeeds with chance 0.25.', '4', '1 / q.', ['Geometric distribution.', '1 / 0.25.', eq('4')], check=4)
K.calc('m', 'Back off waits with base 1 second: total wait before the 5th try (waits 1, 2, 4, 8).', '15', '2<sup>4</sup> &minus; 1.', ['1 + 2 + 4 + 8.', 'A geometric sum.', eq('15 seconds')], check=15)
K.calc('m', 'eval_rpn(["3", "4", "+", "2", "*"])?', '14', '(3 + 4) &times; 2.', ['Push 3, 4. + gives 7.', 'Push 2. * gives 14.', eq('14')], check=14)
K.calc('h', 'Chance (percent, 1 decimal) that a 3 step booking fails at least once with failure chances 2, 5 and 1 percent.', '7.8', '1 &minus; 0.98 &times; 0.95 &times; 0.99.', ['0.98 &times; 0.95 &times; 0.99 = 0.92169.', '1 &minus; 0.92169 = 0.07831.', eq('7.8 percent')], check=round(100 * (1 - 0.98 * 0.95 * 0.99), 1))
K.calc('h', 'How many classes are in ZeroDivisionError.__mro__ (count object too)?', '5', 'Walk up the tree.', ['ZeroDivisionError, ArithmeticError, Exception.', 'BaseException, object.', eq('5')], check=len(ZeroDivisionError.__mro__))
K.calc('x', 'In the style of an MIT 6.031 (Software Construction) question: a service retries a failed call up to 3 extra times. Each call fails with chance 0.1, independently. What is the chance (percent, 2 decimals) that all 4 calls fail?', '0.01', '0.1<sup>4</sup>.', ['All four must fail.', '0.1 &times; 0.1 &times; 0.1 &times; 0.1 = 0.0001.', eq('0.01 percent')], check=round(100 * 0.1 ** 4, 2))

K.assign('readint', 'e', 'Safe integer reader',
         '<p>Write <code>to_int(text, default=0)</code> that returns int(text), or default if the text is not a whole number. Use try and except, not isdigit().</p>',
         '''
def to_int(text, default=0):
    # your code here
    pass
''', [('to_int("42")', 42), ('to_int("abc")', 0), ('to_int("-7")', -7), ('to_int("4.5", -1)', -1), ('to_int(" 9 ")', 9)],
         '''
def to_int(text, default=0):
    try:
        return int(text)
    except ValueError:
        return default
''', 'Put return int(text) in try and return default in except ValueError.', '<p>isdigit() would reject "-7" and " 9 ", which int() accepts. Asking int() itself (EAFP) gives exactly its rules.</p>')
HELPER = '''

def raises(func, *args):
    """Test helper: the name of the exception func(*args) raises, or None."""
    try:
        func(*args)
    except Exception as err:
        return type(err).__name__
    return None
'''
K.assign('validate', 'm', 'Validate a username',
         '<p>Write <code>check_username(name)</code>. Raise TypeError if name is not a str. Raise ValueError if it has fewer than 3 or more than 12 characters, or if it contains anything other than letters, digits and _. Otherwise return the name in lower case. The helper raises() is only there for the tests.</p>',
         '''
def check_username(name):
    # your code here
    pass
''' + HELPER, [('check_username("Asha_21")', 'asha_21'), ('raises(check_username, 5)', 'TypeError'), ('raises(check_username, "ab")', 'ValueError'), ('raises(check_username, "no spaces")', 'ValueError'), ('raises(check_username, "abcdefghijklm")', 'ValueError')],
         '''
def check_username(name):
    if not isinstance(name, str):
        raise TypeError("name must be text")
    if len(name) < 3 or len(name) > 12:
        raise ValueError("name must have 3 to 12 characters")
    for ch in name:
        if not (ch.isalnum() or ch == "_"):
            raise ValueError("only letters, digits and _ are allowed")
    return name.lower()
''' + HELPER, 'Check the type first with isinstance, then the length, then each character.', '<p>The order of checks matters: len(5) would raise its own TypeError with a less helpful message.</p>')
FLAKY = '''

def make_flaky(failures):
    """Test helper: an action that raises ConnectionError the first failures times, then returns "ok"."""
    state = {"left": failures}

    def action():
        if state["left"] > 0:
            state["left"] = state["left"] - 1
            raise ConnectionError("try again")
        return "ok"

    return action
''' + HELPER
K.assign('retry', 'm', 'Retry helper',
         '<p>Write <code>retry(action, tries)</code>. Call action() up to tries times. Return its result as soon as one call does not raise. If every call raises, raise the last exception again. make_flaky() and raises() are helpers for the tests.</p>',
         '''
def retry(action, tries):
    # your code here
    pass
''' + FLAKY, [('retry(lambda: 5, 3)', 5), ('retry(make_flaky(2), 3)', 'ok'), ('raises(retry, make_flaky(5), 3)', 'ConnectionError')],
         '''
def retry(action, tries):
    last_error = None
    for attempt in range(tries):
        try:
            return action()
        except Exception as err:
            last_error = err
    raise last_error
''' + FLAKY, 'Loop tries times. Return inside try. In except, remember the exception. After the loop, raise it.', '<p>Real code adds a wait that doubles after each failure (exponential back off), as in the maths lesson.</p>')

K.must('try and except', 'try: risky code. except X as err: handles X and its children. First matching handler only.')
K.must('else and finally', 'else runs if no exception. finally always runs (cleanup). Order: try, except..., else, finally.')
K.must('Hierarchy', 'BaseException > Exception > ArithmeticError > ZeroDivisionError. LookupError > KeyError, IndexError. KeyboardInterrupt is not an Exception.')
K.must('raise', 'raise ValueError("msg"). Bare raise re-raises. raise New() from err sets __cause__. Custom: class MyError(Exception).')
K.must('Style', 'Catch specific classes, never bare except. assert is for programmer checks (-O removes it). EAFP. with closes resources.')

T = K.topic(
    slug='py-exceptions', topic='py-exceptions', step=(5, 'Errors, modules and files', 'py-c5', 'Handle errors with exceptions, organise code in modules and packages, and read and write files.', 'Intermediate'),
    title='Exceptions: try, except, else, finally and raise', short='Exceptions', badge='5.1', minutes=65,
    lead='Keep a program running when something goes wrong. Read tracebacks, catch errors with try and except, order handlers along the exception hierarchy, use else and finally, let errors travel to the right level, raise and re-raise your own errors, write custom exception classes, and know when to use assert, EAFP and with.',
    desc='runtime errors vs syntax errors, tracebacks, try and except, multiple handlers, except as, the args of an exception, the built-in exception hierarchy, handler order, bare except, else and finally, propagation through function calls, raise, re-raise, raise from and __cause__, custom exceptions, assert and python -O, EAFP vs LBYL, finally and with for cleanup, ExceptionGroup and except star, failure probability and retries.',
    summary='try, except, else, finally, exception hierarchy, propagation, raise, custom exceptions, assert, EAFP, with.',
    keywords=['exceptions', 'try', 'except', 'finally', 'else', 'raise', 'traceback', 'ValueError', 'ZeroDivisionError', 'custom exception', 'assert', 'PCEP', 'PCAP'],
    recap='<p>Exceptions separate the normal path from the error path. Catch specific classes in the right order, clean up in finally or with, and raise clear errors of your own.</p>',
    added='2026-11-07', leet=leet_items())
