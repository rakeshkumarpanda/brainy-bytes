# Core Python 4.2: scope and recursion. Follows PCEP-30-02 section 4.2 (name scopes, name hiding (shadowing), the
# global keyword) and section 4.1's recursion, plus PCAP-31-03 nonlocal and closures, checked against the Python 3.14
# tutorial section 9.2 "Python Scopes and Namespaces", the language reference section 4.2 "Naming and binding" and
# the sys and functools documentation.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, lc, leet, files, grow, leet_items

chapter('py-scope-recursion')
K = Kit()

K.code('scope1', r'''
tax_rate = 0.18                 # global: made at the top level of the file

def price_with_tax(price):
    tax = price * tax_rate      # tax is local: it exists only during this call
    return price + tax

print(price_with_tax(100))
print(tax_rate)                 # the global is visible everywhere
try:
    print(tax)                  # the local is gone after the call
except NameError as err:
    print("NameError:", err)
''')

K.code('shadow', r'''
x = "global x"

def demo():
    x = "local x"     # a new local name that hides (shadows) the global one
    print("inside:", x)

demo()
print("outside:", x)  # the global was never touched

def no_list_change(items):
    items = [0, 0]    # rebinding the local name does not affect the caller
def list_change(items):
    items.append(99)  # changing the object does

nums = [1, 2]
no_list_change(nums)
list_change(nums)
print(nums)
''')

K.code('legb', r'''
x = "global"

def outer():
    x = "enclosing"
    def inner():
        x = "local"
        print("inner sees:", x)
    inner()
    print("outer sees:", x)

outer()
print("module sees:", x)
print("len comes from:", len.__module__)   # the built-in scope
''')

K.code('globalkw', r'''
visits = 0

def visit():
    global visits         # use the module level name, do not make a local one
    visits += 1

visit()
visit()
print("visits:", visits)

# Better: pass values in and return the new value
def next_count(count):
    return count + 1

total = 0
total = next_count(total)
total = next_count(total)
print("total:", total)
''')

K.code('unbound', r'''
count = 10

def broken():
    print(count)      # count is local here because of the line below
    count = 5

try:
    broken()
except UnboundLocalError as err:
    print("UnboundLocalError:", err)
''')

K.code('closure', r'''
def make_counter():
    n = 0
    def step():
        nonlocal n        # change n of make_counter, not a new local
        n += 1
        return n
    return step

a = make_counter()
b = make_counter()        # a second, separate counter
print(a(), a(), a())
print(b())
print(a.__closure__[0].cell_contents)   # where a keeps its n

def multiplier(k):
    def times(x):
        return x * k      # reading k needs no nonlocal
    return times

double = multiplier(2)
triple = multiplier(3)
print(double(10), triple(10))
''')

K.code('fact', r'''
def factorial(n):
    if n <= 1:                    # base case: stops the recursion
        return 1
    return n * factorial(n - 1)   # recursive case: a smaller problem

for n in range(6):
    print(n, factorial(n))

def countdown(n):
    if n == 0:
        print("Lift off!")
        return
    print(n)
    countdown(n - 1)

countdown(3)
''')

K.code('limit', r'''
import sys
print("recursion limit:", sys.getrecursionlimit())

sys.setrecursionlimit(40)     # a small limit, only so this demo stays short

def forever(n):
    return forever(n + 1)     # no base case

try:
    forever(0)
except RecursionError as err:
    print("RecursionError:", err)

sys.setrecursionlimit(1000)   # put the normal limit back

def depth(n):
    return 0 if n == 0 else 1 + depth(n - 1)

print(depth(20))              # fine, well below the limit
''')

K.code('examples', r'''
def total(items):
    if not items:                       # empty list: sum is 0
        return 0
    return items[0] + total(items[1:])  # first item + sum of the rest

def reverse(text):
    if len(text) <= 1:
        return text
    return reverse(text[1:]) + text[0]

def power(base, exp):                   # fast power: halve the exponent
    if exp == 0:
        return 1
    half = power(base, exp // 2)
    if exp % 2 == 0:
        return half * half
    return half * half * base

def hanoi(n, start, spare, goal, moves):
    if n == 0:
        return
    hanoi(n - 1, start, goal, spare, moves)   # move n - 1 discs out of the way
    moves.append((start, goal))               # move the biggest disc
    hanoi(n - 1, spare, start, goal, moves)   # put the n - 1 discs back on top

print(total([4, 8, 15, 16, 23, 42]))
print(reverse("recursion"))
print(power(2, 10), power(3, 5))
moves = []
hanoi(3, "A", "B", "C", moves)
print(len(moves), "moves:", moves)
''')

K.code('memo', long=True, src=r'''
from functools import lru_cache

calls = 0
def fib(n):
    global calls
    calls += 1
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)

print("fib(25) =", fib(25), "after", calls, "calls")

@lru_cache(maxsize=None)        # remember every answer (a decorator, Advanced 1.2)
def fast_fib(n):
    if n < 2:
        return n
    return fast_fib(n - 1) + fast_fib(n - 2)

print("fast_fib(25) =", fast_fib(25), fast_fib.cache_info())
print("fast_fib(300) =", fast_fib(300))

def loop_fib(n):                # the same answer with a loop and two names
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a

print(loop_fib(25), loop_fib(300) == fast_fib(300))
''')

K.lesson('idea', 'Where names live, and functions that call themselves', f'''
{src('Python 3.14 tutorial section 9.2, language reference section 4.2, PCEP-30-02 sections 4.1 and 4.2.')}
{wwh('The <b>scope</b> of a name is the part of the program where you can use it. A name made inside a function is <b>local</b> to that function. A name made at the top of a file is <b>global</b>. <b>Recursion</b> is when a function calls itself to solve a smaller copy of the same problem.',
     'Scopes keep functions independent: a helper can use the name i or total without breaking the same name somewhere else. Recursion makes problems that are made of smaller copies of themselves (folders inside folders, family trees, maths like n!) short and clear.',
     'Each call gets a fresh set of local names (a frame). Python looks names up in the order Local, Enclosing, Global, Built-in. A recursive function has a <b>base case</b> that answers directly and a <b>recursive case</b> that calls itself on a smaller input, so it always reaches the base case.')}
{scene('Russian nesting dolls', '<p>To count the dolls in a matryoshka set, open the outer doll. If it is empty, the answer is 1 (the base case). Otherwise the answer is 1 plus the number of dolls inside, and you count those the same way (the recursive case). Each opened doll waits on the table until the inner count comes back. Those waiting dolls are the call stack.</p>')}
{run('scope1')}
''', kw=['scope', 'local', 'global', 'recursion', 'base case', 'frame'])

K.lesson('shadow', 'Local names hide global names', f'''
{run('shadow')}
{note('Assigning to a name inside a function makes a new local name, even if a global with the same name exists. This is called <b>shadowing</b>. Changing an object (items.append) is different from rebinding a name (items = [...]): the first is seen by the caller, the second is not.', 'exam')}
''', kw=['shadowing', 'name hiding', 'rebinding vs mutating', 'pass by object reference'])

K.lesson('legb', 'The LEGB rule', f'''
{viz('pylegb')}
{run('legb')}
{table(['Letter', 'Scope', 'Made by'], [
    ['L', 'Local', 'Assignments and parameters inside the current function call'],
    ['E', 'Enclosing', 'The local names of any outer function, for a function inside a function'],
    ['G', 'Global', 'Assignments at the top level of the module (the .py file)'],
    ['B', 'Built-in', 'Names Python gives you: print, len, range, int, ValueError ...']])}
{note('Python decides which names are local when it compiles the function, not while it runs. If a name is assigned anywhere in the function, it is local in the whole function.', 'exam')}
''', kw=['LEGB', 'local', 'enclosing', 'global', 'built-in', 'name lookup'])

K.lesson('globalkw', 'The global statement', f'''
{run('globalkw')}
{versus('Sharing a changing value between functions', ['', 'global variable', 'pass in and return'], [
    ['Code', 'global visits then visits += 1', 'total = next_count(total)'],
    ['Who can change it', 'Any function, from anywhere', 'Only code that gets the returned value'],
    ['Testing', 'Hard: the result depends on hidden state', 'Easy: same input, same output'],
    ['Good for', 'Settings read in many places, small scripts', 'Almost everything else']],
    'pass values in and return results. Keep global for constants and the rare value that the whole program really shares.')}
''', kw=['global keyword', 'global state', 'side effects', 'constants'])

K.lesson('unbound', 'UnboundLocalError', f'''
{run('unbound')}
{note('The fix is either to rename the local variable, to pass count in as a parameter, or, if you really mean the global, to add global count at the top of the function.', 'tip')}
''', kw=['UnboundLocalError', 'local before assignment', 'compile time scope'])

K.lesson('closure', 'nonlocal and closures', f'''
{run('closure')}
{wwh('A <b>closure</b> is an inner function that remembers names from the function around it, even after that outer function has finished.',
     'It lets you make functions with their own private memory: counters, multipliers, settings, without a global variable or a class.',
     'Python stores each remembered name in a cell attached to the inner function (func.__closure__). Reading an enclosing name needs nothing special. Assigning to it needs <b>nonlocal</b>, or Python would make a new local name.')}
{note('global reaches the module scope. nonlocal reaches the nearest enclosing function scope and is a SyntaxError at the top level. Decorators (Advanced 1.2) are built from closures.', 'exam')}
''', kw=['closure', 'nonlocal', 'cell', '__closure__', 'factory function', 'private state'])

K.lesson('fact', 'Recursion: base case and recursive case', f'''
{viz('pystack')}
{run('fact')}
{table(['Part', 'factorial', 'Question to ask'], [
    ['Base case', 'if n &lt;= 1: return 1', 'What is the smallest input I can answer at once?'],
    ['Recursive case', 'return n * factorial(n - 1)', 'How does the answer use the answer for a smaller input?'],
    ['Progress', 'n &minus; 1 is smaller than n', 'Does every call get closer to the base case?']])}
''', kw=['recursion', 'base case', 'recursive case', 'factorial', 'call stack', 'stack frame'])

K.lesson('limit', 'The recursion limit', f'''
{run('limit')}
{note('Each call uses a frame on the call stack. To protect the program, CPython stops at about 1,000 frames deep with RecursionError. sys.setrecursionlimit can raise the limit, but a recursion that deep is usually better written as a loop.', 'warn')}
''', kw=['RecursionError', 'recursion limit', 'sys.getrecursionlimit', 'stack overflow'])

K.lesson('examples', 'Classic recursive functions', f'''
{run('examples')}
{note('total(items[1:]) is clear but copies the list each time, which makes it O(n<sup>2</sup>). Real code uses sum(). Fast power is the opposite: halving the exponent makes it O(log n), which is how pow(a, b, m) handles huge numbers in cryptography.', 'tip')}
''', kw=['sum recursion', 'reverse string', 'fast power', 'exponentiation by squaring', 'Tower of Hanoi'])

K.lesson('memo', 'Memoisation: remember answers', f'''
{run('memo')}
{wwh('<b>Memoisation</b> means storing the answer of each call so the same call never has to be worked out twice.',
     'Naive fib(n) calls fib(n &minus; 2) twice, fib(n &minus; 3) three times, and so on: the number of calls grows like 1.6<sup>n</sup>. fib(25) needs 242,785 calls.',
     'functools.lru_cache keeps a dict from arguments to results. With it each fib(k) is computed once, so fib(n) takes n + 1 calls. A plain loop with two names does the same in O(n) time and O(1) memory.')}
''', kw=['memoization', 'memoisation', 'lru_cache', 'functools', 'dynamic programming', 'Fibonacci'])

K.lesson('versus', 'Recursion or a loop', f'''
{versus('Recursion compared with iteration', ['', 'Recursion', 'Loop'], [
    ['Fits best', 'Nested data: trees, folders, JSON, divide and conquer', 'Walking a list, counting, simple repeats'],
    ['Memory', 'One frame per pending call: O(depth)', 'Usually O(1)'],
    ['Depth limit in Python', 'About 1,000', 'None'],
    ['Speed in CPython', 'Slower (each call has a cost)', 'Faster'],
    ['Readability', 'Very clear when the problem is recursive', 'Very clear when it is a sequence']],
    'use recursion when the data or the problem is naturally nested, and a loop for everything else. Python does not remove tail calls, so a deep "tail recursive" function still hits the limit.')}
''', kw=['recursion vs iteration', 'tail call', 'stack depth', 'divide and conquer'])

K.lesson('maths', 'The maths of recursion', f'''
{fxs(fx('Recurrence for a simple recursion', 'T(n) = T(n &minus; 1) + c gives T(n) = O(n)', 'factorial and countdown do constant work and then one smaller call.', key=True),
     fx('Calls made by naive fib(n)', 'C(n) = C(n &minus; 1) + C(n &minus; 2) + 1 = 2F(n + 1) &minus; 1', 'fib(5) makes 2 &times; 8 &minus; 1 = 15 calls, as the animation counts.', key=True),
     fx('Golden ratio growth', 'F(n) &asymp; &phi;<sup>n</sup> / &radic;5, &phi; = (1 + &radic;5)/2 &asymp; 1.618', 'So naive fib is exponential: about 1.6<sup>n</sup> calls.'),
     fx('Tower of Hanoi moves', 'M(n) = 2M(n &minus; 1) + 1 = 2<sup>n</sup> &minus; 1', '3 discs need 7 moves, 64 discs need about 1.8 &times; 10<sup>19</sup>.', key=True),
     fx('Fast power', 'T(n) = T(n/2) + c gives T(n) = O(log n)', 'power(2, 1000) needs only about 10 levels of calls.'),
     fx('Master theorem (divide and conquer)', 'T(n) = a&middot;T(n/b) + O(n<sup>d</sup>)', 'If d &gt; log<sub>b</sub> a: O(n<sup>d</sup>). If equal: O(n<sup>d</sup> log n). If less: O(n<sup>log<sub>b</sub> a</sup>). Merge sort: a = 2, b = 2, d = 1 gives O(n log n).'))}
{steps('Worked example: prove factorial is correct by induction', [
    'Claim: factorial(n) returns n! for every n &ge; 0.',
    'Base: for n = 0 and n = 1 it returns 1, which is 0! and 1!.',
    'Step: assume factorial(n &minus; 1) returns (n &minus; 1)!. Then factorial(n) returns n &times; (n &minus; 1)! = n!.',
    eq('By induction the claim holds for every n &ge; 0'),
    'This is why a correct base case and a smaller recursive call are all you need.'])}
''', kw=['recurrence relation', 'induction', 'Fibonacci calls', 'golden ratio', 'Tower of Hanoi', 'master theorem'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>Names made in a function are local and vanish after the call. A function can call itself if it has a base case.</p>',
    '<p>Python finds names with LEGB. global and nonlocal let a function assign to an outer name. Assigning anywhere makes a name local. Recursion needs a base case and a smaller step, and stops near 1,000 frames.</p>',
    '<p>Closures keep enclosing names alive in cells. Memoise repeated calls with lru_cache. Write recurrences to find the cost of a recursive function, and prove it correct with induction.</p>',
    '<p>The compiler classifies every name as local, cell, free or global and emits different bytecodes (LOAD_FAST, LOAD_DEREF, LOAD_GLOBAL). Since Python 3.11 pure Python calls do not use the C stack, but the recursion limit still guards against runaway recursion. Recursion with memoisation is top down dynamic programming, the loop version is bottom up.</p>')}
{grow('Tell local from global names and write a factorial with a base case.',
      'Use LEGB, global and nonlocal correctly, trace the call stack, and avoid UnboundLocalError.',
      'Write closures, memoise with lru_cache, analyse recursion with recurrences and prove it correct by induction.')}
''', kw=['beginner', 'expert', 'LOAD_FAST', 'LOAD_DEREF', 'dynamic programming'])

lc(509, 'Fibonacci Number', 'fibonacci-number', 'e', 'Recursion with memo or a loop', 'F(0) = 0, F(1) = 1. Use two names a and b and move them forward n times.', r'''
def fib(n):
    a = 0
    b = 1
    for _ in range(n):
        a, b = b, a + b
    return a
''', [('fib(2)', 1), ('fib(3)', 2), ('fib(4)', 3), ('fib(30)', 832040)])
lc(70, 'Climbing Stairs', 'climbing-stairs', 'e', 'Recurrence ways(n) = ways(n &minus; 1) + ways(n &minus; 2)', 'The last step was 1 or 2 stairs. It is Fibonacci shifted by one.', r'''
def climb_stairs(n):
    one_before = 1
    two_before = 1
    for _ in range(n - 1):
        one_before, two_before = one_before + two_before, one_before
    return one_before
''', [('climb_stairs(2)', 2), ('climb_stairs(3)', 3), ('climb_stairs(10)', 89)])
lc(326, 'Power of Three', 'power-of-three', 'e', 'Divide while you can', 'Keep dividing by 3 while n % 3 == 0. A power of three ends at 1.', r'''
def is_power_of_three(n):
    if n <= 0:
        return False
    while n % 3 == 0:
        n = n // 3
    return n == 1
''', [('is_power_of_three(27)', True), ('is_power_of_three(0)', False), ('is_power_of_three(45)', False), ('is_power_of_three(1)', True)])
lc(342, 'Power of Four', 'power-of-four', 'e', 'Recursive halving', 'Base cases 1 (True) and anything not divisible by 4 (False). Otherwise ask the same question for n // 4.', r'''
def is_power_of_four(n):
    if n == 1:
        return True
    if n <= 0 or n % 4 != 0:
        return False
    return is_power_of_four(n // 4)
''', [('is_power_of_four(16)', True), ('is_power_of_four(5)', False), ('is_power_of_four(1)', True), ('is_power_of_four(8)', False)])
lc(1688, 'Count of Matches in Tournament', 'count-of-matches-in-tournament', 'e', 'Recursion, then a maths shortcut', 'Each round plays n // 2 matches and n &minus; n // 2 teams go on. In the end every team but one loses once: n &minus; 1 matches.', r'''
def number_of_matches(n):
    if n == 1:
        return 0
    return n // 2 + number_of_matches(n - n // 2)
''', [('number_of_matches(7)', 6), ('number_of_matches(14)', 13), ('number_of_matches(1)', 0)])
lc(50, 'Pow(x, n)', 'powx-n', 'm', 'Fast power by halving', 'x<sup>n</sup> = (x<sup>n/2</sup>)<sup>2</sup>, times x when n is odd. For negative n use 1 / x<sup>&minus;n</sup>.', r'''
def my_pow(x, n):
    if n < 0:
        return 1 / my_pow(x, -n)
    if n == 0:
        return 1.0
    half = my_pow(x, n // 2)
    if n % 2 == 0:
        return half * half
    return half * half * x
''', [('round(my_pow(2.0, 10), 5)', 1024.0), ('round(my_pow(2.1, 3), 5)', 9.261), ('round(my_pow(2.0, -2), 5)', 0.25)])
lc(22, 'Generate Parentheses', 'generate-parentheses', 'm', 'Backtracking', 'Build the text one bracket at a time. Add "(" while you have some left, and ")" only when it closes an open one.', r'''
def generate_parenthesis(n):
    result = []

    def build(text, opened, closed):
        if len(text) == 2 * n:
            result.append(text)
            return
        if opened < n:
            build(text + "(", opened + 1, closed)
        if closed < opened:
            build(text + ")", opened, closed + 1)

    build("", 0, 0)
    return result
''', [('generate_parenthesis(3)', ['((()))', '(()())', '(())()', '()(())', '()()()']), ('generate_parenthesis(1)', ['()'])])
lc(46, 'Permutations', 'permutations', 'm', 'Backtracking', 'Pick each unused number for the next place, recurse, then undo the choice.', r'''
def permute(nums):
    result = []

    def build(current, unused):
        if not unused:
            result.append(current)
            return
        for i in range(len(unused)):
            build(current + [unused[i]], unused[:i] + unused[i + 1:])

    build([], nums)
    return result
''', [('permute([1, 2, 3])', [[1, 2, 3], [1, 3, 2], [2, 1, 3], [2, 3, 1], [3, 1, 2], [3, 2, 1]]), ('permute([0, 1])', [[0, 1], [1, 0]])])
lc(78, 'Subsets', 'subsets', 'm', 'Take it or leave it', 'For each number, make two recursive calls: one that takes it and one that skips it.', r'''
def subsets(nums):
    result = []

    def build(i, current):
        if i == len(nums):
            result.append(current)
            return
        build(i + 1, current)
        build(i + 1, current + [nums[i]])

    build(0, [])
    return result
''', [('sorted(subsets([1, 2, 3]))', [[], [1], [1, 2], [1, 2, 3], [1, 3], [2], [2, 3], [3]]), ('subsets([0])', [[], [0]])])
lc(779, 'K-th Symbol in Grammar', 'k-th-symbol-in-grammar', 'm', 'Recursion on the parent', 'Symbol k of row n comes from symbol (k + 1) // 2 of row n &minus; 1. An odd k copies the parent, an even k flips it.', r'''
def kth_grammar(n, k):
    if n == 1:
        return 0
    parent = kth_grammar(n - 1, (k + 1) // 2)
    if k % 2 == 1:
        return parent
    return 1 - parent
''', [('kth_grammar(1, 1)', 0), ('kth_grammar(2, 1)', 0), ('kth_grammar(2, 2)', 1), ('kth_grammar(4, 5)', 1)])

K.lesson('leetcode', 'LeetCode practice', leet(), kw=['LeetCode', 'Fibonacci', 'climbing stairs', 'pow', 'backtracking', 'permutations', 'subsets', 'generate parentheses'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'Names assigned in a function are <b>local</b>. Names at the top of a file are <b>global</b>. A local name hides a global one with the same name.',
    'Python looks names up in the order <b>L</b>ocal, <b>E</b>nclosing, <b>G</b>lobal, <b>B</b>uilt-in.',
    'If a name is assigned anywhere in a function, it is local in the whole function. Reading it first gives UnboundLocalError.',
    '<b>global</b> name lets a function assign to a module name. <b>nonlocal</b> name does the same for an enclosing function.',
    'A <b>closure</b> is an inner function that remembers enclosing names after the outer function returns.',
    '<b>Recursion</b> needs a base case and a recursive case that gets smaller. Each pending call is a frame on the call stack.',
    'CPython stops at about 1,000 frames with RecursionError. Memoise repeated calls with lru_cache, or use a loop.',
    'Naive fib makes 2F(n + 1) &minus; 1 calls. Hanoi needs 2<sup>n</sup> &minus; 1 moves. Fast power needs O(log n) calls.'],
    'Core 4.3 covers lambda, map, filter, sorted with key, and list, dict and set comprehensions.')}
{files('Three tasks: a running total closure, a recursive digit sum, and a recursive flatten for nested lists of any depth.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'A variable made inside a function is called', ['global', 'local', 'built-in', 'static'], 1, 'It lives in the function.', 'Names assigned in a function are local to it.')
K.quiz('e', 'What stops a recursive function from calling itself for ever?', ['A loop', 'The base case', 'return None', 'global'], 1, 'The smallest case.', 'The base case answers without another call.')
K.quiz('e', 'In LEGB, what does B stand for?', ['Block', 'Built-in', 'Base', 'Binary'], 1, 'print and len live there.', 'B is the built-in scope.')
K.quiz('m', 'x = 5, then def f(): x = 10, then f() then print(x). What is printed?', ['10', '5', 'Error', 'None'], 1, 'Shadowing.', 'f made a local x. The global x is still 5.')
K.quiz('m', 'x = 5, then def f(): print(x) then x = 1 inside f. What does f() raise?', ['NameError', 'UnboundLocalError', 'SyntaxError', 'Nothing, prints 5'], 1, 'x is local in all of f.', 'The later assignment makes x local, so reading it first fails.')
K.quiz('m', 'Which keyword lets an inner function assign to a variable of the outer function?', ['global', 'nonlocal', 'outer', 'static'], 1, 'Not the module.', 'nonlocal reaches the nearest enclosing function scope.')
K.quiz('m', 'def f(n): return 1 if n == 0 else n * f(n - 1). What is f(4)?', ['4', '10', '24', '16'], 2, '4!.', '4 &times; 3 &times; 2 &times; 1 = 24.')
K.quiz('m', 'What error does infinite recursion raise in Python?', ['StackOverflowError', 'RecursionError', 'MemoryError', 'LoopError'], 1, 'Python name.', 'RecursionError: maximum recursion depth exceeded.')
K.quiz('h', 'How many calls does naive fib(6) make (fib(n) = fib(n &minus; 1) + fib(n &minus; 2), base n &lt; 2)?', ['13', '25', '15', '21'], 1, '2F(7) &minus; 1.', 'F(7) = 13, so 2 &times; 13 &minus; 1 = 25.')
K.quiz('h', 'What does make_counter() return in the closure example?', ['A number', 'The function step', 'n', 'None'], 1, 'return step.', 'It returns the inner function, which remembers n.')
K.quiz('h', 'How many moves does the Tower of Hanoi need for 5 discs?', ['25', '31', '32', '15'], 1, '2<sup>n</sup> &minus; 1.', '2<sup>5</sup> &minus; 1 = 31.')
K.quiz('x', 'In the style of an MIT 6.006 problem: T(n) = 2T(n/2) + n with T(1) = 1. What is T(n) in big O?', ['O(n)', 'O(n log n)', 'O(n<sup>2</sup>)', 'O(log n)'], 1, 'Master theorem, a = b = 2, d = 1.', 'd = log<sub>2</sub> 2 = 1, so O(n log n), like merge sort.')
K.quiz('x', 'In the style of a Cambridge Part IA question: fs = [lambda: i for i in range(3)]. What is [f() for f in fs]?', ['[0, 1, 2]', '[2, 2, 2]', '[0, 0, 0]', 'Error'], 1, 'Closures capture names, not values.', 'All three lambdas look up i when called, and by then i is 2. Use lambda i=i: i to capture the value.')

K.calc('e', 'factorial(5)?', '120', '5 &times; 4 &times; 3 &times; 2 &times; 1.', ['5 &times; 4 = 20.', '20 &times; 3 &times; 2 = 120.', eq('120')], check=120)
K.calc('e', 'Hanoi moves for 3 discs.', '7', '2<sup>3</sup> &minus; 1.', ['M(n) = 2<sup>n</sup> &minus; 1.', '8 &minus; 1.', eq('7')], check=7)
K.calc('e', 'The default recursion limit of CPython.', '1000', 'sys.getrecursionlimit().', ['The program above printed it.', 'It can be changed with sys.setrecursionlimit.', eq('1000')], check=1000)
K.calc('m', 'Calls made by naive fib(5).', '15', '2F(6) &minus; 1.', ['F(6) = 8.', '2 &times; 8 &minus; 1.', eq('15')], check=15)
K.calc('m', 'Calls made by fib(30) with lru_cache, from empty.', '31', 'n + 1.', ['Each fib(k) for k from 0 to 30 is computed once.', 'That is 31 different arguments.', eq('31')], check=31)
K.calc('m', 'climb_stairs(6): ways to climb 6 stairs with steps of 1 or 2.', '13', 'Fibonacci shifted.', ['ways: 1, 2, 3, 5, 8, 13 for n = 1 to 6.', 'Each is the sum of the two before.', eq('13')], check=13)
K.calc('m', 'How many levels of calls does fast power(2, 64) make, counting power(2, 0)?', '8', 'Exponent halves each level.', ['64, 32, 16, 8, 4, 2, 1, 0.', 'Count them.', eq('8')], check=len([64, 32, 16, 8, 4, 2, 1, 0]))
K.calc('h', 'Calls made by naive fib(10).', '177', '2F(11) &minus; 1.', ['F(11) = 89.', '2 &times; 89 &minus; 1.', eq('177')], check=177)
K.calc('h', 'Matches in a knockout tournament with 100 teams.', '99', 'Every team but the winner loses once.', ['Each match knocks out exactly one team.', '99 teams must be knocked out.', eq('99')], check=99)
K.calc('x', 'In the style of a Stanford CS161 problem: T(n) = 3T(n/2) + n. Using the master theorem, T(n) = O(n<sup>p</sup>). Give p to 3 decimal places.', '1.585', 'log<sub>2</sub> 3.', ['a = 3, b = 2, d = 1.', 'log<sub>2</sub> 3 = 1.585 is bigger than d.', eq('p = log<sub>2</sub> 3 &asymp; 1.585 (Karatsuba multiplication)')], check=1.585)

K.assign('runtotal', 'e', 'Running total closure',
         '<p>Write <code>make_adder()</code> that returns a function add(x). Each call add(x) adds x to a running total kept inside the closure and returns the new total. Two adders must not share a total.</p>',
         '''
def make_adder():
    # your code here
    pass
''', [('(lambda a: (a(5), a(10), a(1)))(make_adder())', (5, 15, 16)), ('(lambda a, b: (a(1), b(1), a(1)))(make_adder(), make_adder())', (1, 1, 2))],
         '''
def make_adder():
    total = 0

    def add(x):
        nonlocal total
        total = total + x
        return total

    return add
''', 'Keep total in make_adder. The inner function needs nonlocal total before it assigns to it.', '<p>Each call to make_adder makes a new total, so the two adders are independent. This is the same idea as an object with one attribute.</p>')
K.assign('rdigits', 'm', 'Recursive digit sum',
         '<p>Write <code>digit_sum(n)</code> for n &ge; 0 using recursion, not loops or str(). The sum of the digits of n is the last digit plus the digit sum of n // 10.</p>',
         '''
def digit_sum(n):
    # your code here
    pass
''', [('digit_sum(0)', 0), ('digit_sum(7)', 7), ('digit_sum(90731)', 20), ('digit_sum(999999)', 54)],
         '''
def digit_sum(n):
    if n < 10:
        return n
    return n % 10 + digit_sum(n // 10)
''', 'Base case: a one digit number is its own sum. Recursive case: n % 10 + digit_sum(n // 10).', '<p>Each call removes one digit, so the depth is the number of digits, far below the recursion limit.</p>')
K.assign('deepflat', 'h', 'Flatten a list of any depth',
         '<p>Write <code>deep_flatten(items)</code> that returns a flat list of every non list value in items, in order, however deeply the lists are nested. [1, [2, [3, [4]]], 5] gives [1, 2, 3, 4, 5].</p>',
         '''
def deep_flatten(items):
    # your code here
    pass
''', [('deep_flatten([1, [2, [3, [4]]], 5])', [1, 2, 3, 4, 5]), ('deep_flatten([])', []), ('deep_flatten([[[]], ["a"]])', ['a'])],
         '''
def deep_flatten(items):
    result = []
    for item in items:
        if isinstance(item, list):
            result.extend(deep_flatten(item))
        else:
            result.append(item)
    return result
''', 'Loop over the items. A list item is flattened by a recursive call, any other item is appended.', '<p>Nested data such as JSON and folder trees is exactly where recursion beats loops. The depth of the recursion equals the depth of the nesting.</p>')

K.must('Scopes', 'Local (inside a call), Enclosing, Global (module), Built-in: LEGB. Assigning makes a name local in the whole function.')
K.must('global and nonlocal', 'global x assigns the module x. nonlocal x assigns the enclosing function x. Reading needs neither.')
K.must('Closures', 'An inner function that remembers enclosing names (cells). Used for counters, factories and decorators.')
K.must('Recursion', 'Base case + smaller recursive case. Each call is a frame. Limit about 1000, RecursionError.')
K.must('Costs', 'T(n) = T(n-1) + c is O(n). Naive fib 2F(n+1) - 1 calls, lru_cache makes it n + 1. Hanoi 2^n - 1. Fast power O(log n).')

T = K.topic(
    slug='py-scope-recursion', topic='py-scope-recursion', step=(4, 'Functions', 'py-c4', 'Write reusable code with def, every kind of argument, scope, recursion, lambda and comprehensions.', 'Intermediate'),
    title='Scope and recursion: LEGB, closures and the call stack', short='Scope and recursion', badge='4.2', minutes=65,
    lead='Find out where every name lives and how functions call themselves. Learn local and global names, shadowing, the LEGB rule, global and nonlocal, UnboundLocalError, closures, recursion with base cases, the call stack and its limit, classic recursive functions, memoisation and the maths of recurrences.',
    desc='local and global scope, shadowing, rebinding vs mutating arguments, LEGB lookup, the global statement, UnboundLocalError, nonlocal and closures, cells, recursion, base and recursive cases, the call stack, RecursionError and the recursion limit, recursive sum, reverse, fast power and Tower of Hanoi, memoisation with lru_cache, recursion vs iteration, recurrences, induction and the master theorem.',
    summary='scope, LEGB, global, nonlocal, closures, recursion, call stack, recursion limit, memoisation, recurrences.',
    keywords=['scope', 'LEGB', 'global', 'nonlocal', 'closure', 'recursion', 'base case', 'call stack', 'RecursionError', 'lru_cache', 'memoization', 'PCEP', 'PCAP'],
    recap='<p>Names are found by LEGB, and global and nonlocal let you assign outer names. Recursion solves a problem through smaller copies of itself, one stack frame at a time, and memoisation stops repeated work.</p>',
    added='2026-11-07', leet=leet_items())
