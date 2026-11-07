# Advanced Python 1.2: extended arguments, closures and decorators. Follows PCPP-32-101 block 1 (extended function
# argument syntax, closures, decorators: function and class decorators, decorators with arguments, stacking), checked
# against the Python 3.14 reference (function definitions, section 8.7), PEP 318 (decorators), PEP 570
# (positional only parameters), PEP 3102 (keyword only arguments) and the functools documentation.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, lc, leet, files, grow, leet_items

chapter('py-decorators')
K = Kit()

K.code('args', r'''
def describe(name, /, age, *hobbies, city="Pune", **extra):
    #        ^ positional only  ^ any number   ^ keyword only   ^ any other keywords
    return f"{name} {age} {hobbies} {city} {extra}"


print(describe("Asha", 30))
print(describe("Asha", age=30, city="Delhi"))
print(describe("Ravi", 25, "chess", "music", lang="hi"))

try:
    describe(name="Asha", age=30)
except TypeError as err:
    print("TypeError:", err)

values = ["Meera", 41, "yoga"]
options = {"city": "Goa", "pet": "cat"}
print(describe(*values, **options))      # * and ** unpack at the call


def forward(*args, **kwargs):            # pass everything on, unchanged
    return describe(*args, **kwargs)


print(forward("Ali", 19, city="Agra"))
''')

K.code('first', r'''
def shout(text):
    return text.upper() + "!"


def whisper(text):
    return text.lower() + "..."


say = shout                              # a function is an object: give it another name
print(say("hi"), say.__name__)

actions = {"loud": shout, "soft": whisper}
print(actions["soft"]("HELLO"))          # store functions in a dict


def apply_twice(func, value):            # pass a function as an argument
    return func(func(value))


print(apply_twice(shout, "go"))


def make_greeter(greeting):              # return a new function
    def greet(name):
        return greeting + ", " + name
    return greet


hello = make_greeter("Hello")
namaste = make_greeter("Namaste")
print(hello("Asha"), "|", namaste("Ravi"))
print(namaste.__closure__[0].cell_contents)   # the value the closure remembers
''')

K.code('simple', r'''
def shout(func):
    def wrapper(*args, **kwargs):
        print("calling", func.__name__)
        result = func(*args, **kwargs)
        return result
    return wrapper


@shout                                   # the same as add = shout(add)
def add(a, b):
    return a + b


print(add(2, 3))
print(add.__name__)                      # the name is now wrapper: see the next program
''')

K.code('wraps', r'''
from functools import wraps


def plain(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


def careful(func):
    @wraps(func)                         # copy name, docstring and more from func
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


@plain
def area(w, h):
    """Return the area of a rectangle."""
    return w * h


@careful
def volume(w, h, d):
    """Return the volume of a box."""
    return w * h * d


print(area.__name__, area.__doc__)
print(volume.__name__, volume.__doc__)
print(volume.__wrapped__(1, 2, 3))       # wraps also keeps the original
''')

K.code('count', r'''
from functools import wraps


def count_calls(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        wrapper.calls += 1               # a function can have its own attributes
        return func(*args, **kwargs)
    wrapper.calls = 0
    return wrapper


@count_calls
def greet(name):
    return "hi " + name


greet("Asha")
greet("Ravi")
print(greet("Meera"), greet.calls)
''')

K.code('factory', r'''
from functools import wraps


def repeat(times):                       # 1. the factory takes the settings
    def decorate(func):                  # 2. the real decorator takes the function
        @wraps(func)
        def wrapper(*args, **kwargs):    # 3. the wrapper takes the call's arguments
            results = []
            for i in range(times):
                results.append(func(*args, **kwargs))
            return results
        return wrapper
    return decorate


@repeat(3)                               # wave = repeat(3)(wave)
def wave(name):
    return "hi " + name


print(wave("Asha"))


def retry(attempts):
    def decorate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, attempts + 1):
                try:
                    return func(*args, **kwargs)
                except ConnectionError as err:
                    print("attempt", attempt, "failed:", err)
            raise ConnectionError("gave up after " + str(attempts) + " attempts")
        return wrapper
    return decorate


tries = {"n": 0}


@retry(3)
def fetch():
    tries["n"] += 1
    if tries["n"] < 3:                   # fails twice, then works
        raise ConnectionError("timeout")
    return "data"


print(fetch())
''')

K.code('stack', r'''
def tag(name):
    def decorate(func):
        def wrapper():
            print("enter", name)
            result = "<" + name + ">" + func() + "</" + name + ">"
            print("leave", name)
            return result
        return wrapper
    return decorate


@tag("b")                                # applied second, runs first
@tag("i")                                # applied first, runs second
def hello():
    return "hello"


print(hello())
''')

K.code('cache', long=True, src=r'''
from functools import cache, lru_cache

calls = 0


def slow_fib(n):
    global calls
    calls += 1
    return n if n < 2 else slow_fib(n - 1) + slow_fib(n - 2)


print(slow_fib(25), calls, "calls without a cache")


@cache                                   # remember every answer
def fib(n):
    return n if n < 2 else fib(n - 1) + fib(n - 2)


print(fib(25), fib.cache_info())
print(fib(200))


@lru_cache(maxsize=2)                    # keep only the 2 most recently used answers
def square(n):
    return n * n


for n in [1, 2, 1, 3, 2]:
    square(n)
print(square.cache_info())
''')

K.code('classdeco', r'''
PLUGINS = {}


def register(cls):                       # a decorator can take a class too
    PLUGINS[cls.__name__.lower()] = cls
    return cls                           # give the class back unchanged


@register
class Csv:
    pass


@register
class Json:
    pass


print(sorted(PLUGINS), PLUGINS["json"] is Json)


class CountCalls:                        # a class can BE a decorator, through __call__
    def __init__(self, func):
        self.func = func
        self.calls = 0

    def __call__(self, *args, **kwargs):
        self.calls += 1
        return self.func(*args, **kwargs)


@CountCalls                              # square = CountCalls(square)
def square(n):
    return n * n


print(square(3), square(4), square.calls, type(square).__name__)
''')

K.lesson('idea', 'Decorators: add behaviour without changing the code', f'''
{src('Python 3.14 reference section 8.7 (function definitions), PEP 318, PEP 570, PEP 3102, the functools documentation and PCPP-32-101 block 1.')}
{wwh('A <b>decorator</b> is a function that takes a function (or a class) and returns a replacement for it, usually a <b>wrapper</b> that does something extra before or after calling the original. Writing @decorator above a def applies it.',
     'Many functions need the same extra jobs: logging, timing, checking arguments, retrying, caching, checking a login. Copying that code into every function is repetitive and easy to get wrong. A decorator writes the job once and adds it to any function with one line.',
     'Functions are objects, so they can be passed to other functions and returned from them. @shout above def add runs add = shout(add) right after the def. shout returns a wrapper, a closure that remembers the original function and calls it inside.')}
{scene('gift wrapping', '<p>A gift wrapped in paper is still the same gift, but now it comes with a ribbon and a card. Anyone who receives it opens the paper first, then reaches the gift. A decorator wraps a function the same way: callers reach the wrapper first, and the wrapper hands them on to the original.</p>')}
{viz('pydeco')}
{run('simple')}
''', kw=['decorator', 'wrapper', '@ syntax', 'higher order function', 'PEP 318', 'add behaviour'])

K.lesson('args', 'Extended argument syntax', f'''
{run('args')}
{table(['Part of def', 'Meaning', 'Example call'], [
    ['name, /', 'Positional only: cannot be passed by keyword (PEP 570)', 'describe("Asha", ...)'],
    ['age', 'Positional or keyword', 'describe("Asha", 30) or age=30'],
    ['*hobbies', 'Collects extra positional values into a tuple', '"chess", "music"'],
    ['city="Pune" after *', 'Keyword only: must be passed by name (PEP 3102)', 'city="Delhi"'],
    ['**extra', 'Collects extra keyword values into a dict', 'lang="hi"'],
    ['f(*seq, **mapping)', 'At a CALL, * and ** unpack instead of collecting', 'describe(*values, **options)']])}
{note('The order in a def is always: positional only, /, normal, *args (or a bare *), keyword only, **kwargs. *args, **kwargs in a wrapper accept any call and pass it on unchanged, which is why every general decorator uses them. Notice the fourth line of output: name="Asha" did not fill name. Because describe has **extra, it went into extra, so Python reports name as missing.', 'exam')}
''', kw=['*args', '**kwargs', 'positional only', 'keyword only', 'PEP 570', 'PEP 3102', 'unpacking', 'forwarding'])

K.lesson('first', 'Functions are objects, closures remember', f'''
{run('first')}
{note('A <b>closure</b> is a function that remembers the variables of the function it was made in, even after that function has returned. greet remembers greeting. That memory, stored in __closure__, is what lets a wrapper keep hold of the original function.', 'tip')}
''', kw=['first class functions', 'closure', '__closure__', 'cell', 'function factory', 'higher order'])

K.lesson('wraps', 'functools.wraps: keep the name and docstring', f'''
{run('wraps')}
{note('Without @wraps every decorated function is called "wrapper" and loses its docstring, which breaks help(), debuggers, logging and frameworks that look up functions by name (Flask uses the name for its routes). Always put @wraps(func) on the wrapper.', 'warn')}
''', kw=['functools.wraps', '__name__', '__doc__', '__wrapped__', 'metadata'])

K.lesson('count', 'Decorators that keep state', f'''
{run('count')}
{run('classdeco')}
{versus('Where a decorator keeps its state', ['', 'attribute on the wrapper function', 'a class with __call__', 'a closure variable with nonlocal'], [
    ['Example', 'wrapper.calls', 'self.calls', 'nonlocal calls'],
    ['Readable from outside', 'Yes: greet.calls', 'Yes: square.calls', 'No'],
    ['Works on methods', 'Yes', 'Needs extra work (__get__)', 'Yes'],
    ['Best for', 'Simple counters and flags', 'Complex state', 'Private state']],
    'a function decorator with wraps is the usual choice. A class decorator object shines when the state is big.')}
''', kw=['stateful decorator', 'function attribute', 'class as decorator', '__call__', 'class decorator', 'registry'])

K.lesson('factory', 'Decorators with arguments', f'''
{run('factory')}
{steps('Reading @repeat(3)', [
    'repeat(3) runs first and returns decorate, which remembers times = 3.',
    'decorate(wave) runs and returns wrapper, which remembers times and func.',
    'The name wave now points to wrapper.',
    'Every call wave(...) runs wrapper(...), which calls the original three times.'])}
{note('A decorator with arguments has three nested functions: the factory (settings), the decorator (the function) and the wrapper (the call). Forgetting the brackets, @retry instead of @retry(3), passes the function as attempts and fails in a confusing way.', 'warn')}
''', kw=['decorator factory', 'decorator with arguments', 'retry', 'repeat', 'three levels'])

K.lesson('stack', 'Stacking decorators', f'''
{run('stack')}
{note('Decorators are applied from the bottom up (nearest the def first) and run from the top down at call time. @a then @b above def f means f = a(b(f)).', 'exam')}
''', kw=['stacked decorators', 'order of decorators', 'a(b(f))'])

K.lesson('cache', 'Built in decorators and caching', f'''
{run('cache')}
{table(['Decorator', 'Module', 'What it does', 'Chapter'], [
    ['@functools.cache, @lru_cache(maxsize)', 'functools', 'Remembers results for arguments seen before', '1.2'],
    ['@functools.wraps(func)', 'functools', 'Copies name and docstring onto a wrapper', '1.2'],
    ['@functools.total_ordering', 'functools', 'Fills in comparison methods', '1.1'],
    ['@property, @x.setter', 'built in', 'Methods that look like attributes', '1.3'],
    ['@classmethod, @staticmethod', 'built in', 'Methods that get the class, or nothing', '1.3'],
    ['@abc.abstractmethod', 'abc', 'Methods every child must write', '1.3'],
    ['@dataclasses.dataclass', 'dataclasses', 'Writes __init__, __repr__ and __eq__ for you', '1.3'],
    ['@contextlib.contextmanager', 'contextlib', 'Turns a generator into a with statement helper', '2.3'],
    ['@app.route("/")', 'Flask', 'Registers a function as a web page', 'Web 3.1']])}
{note('Only cache <b>pure</b> functions, whose result depends only on the arguments. Arguments must be hashable. @cache never forgets, so for many different arguments use lru_cache with a maxsize.', 'warn')}
''', kw=['functools.cache', 'lru_cache', 'memoization', 'built in decorators', 'cache_info', 'pure function'])

K.lesson('maths', 'The maths: memoisation and backoff', f'''
{fxs(fx('Calls of plain recursive Fibonacci', 'C(n) = 1 + C(n &minus; 1) + C(n &minus; 2), C(0) = C(1) = 1, so C(n) = 2F(n + 1) &minus; 1', 'fib(25): 2 &times; 121,393 &minus; 1 = 242,785 calls, as the program counted.', key=True),
     fx('Calls with @cache', 'each n from 0 to N is computed once: N + 1 misses', 'fib(25): 26 misses and 23 hits.', key=True),
     fx('Growth', 'F(n) &asymp; &phi;<sup>n</sup> / &radic;5, &phi; = (1 + &radic;5) / 2 &asymp; 1.618', 'Plain recursion is exponential, O(&phi;<sup>n</sup>). The cached version is linear, O(n).'),
     fx('Exponential backoff', 'wait before retry k = base &times; 2<sup>k</sup>, total for n retries = base(2<sup>n</sup> &minus; 1)', 'base 1 s, 4 retries: 1 + 2 + 4 + 8 = 15 s.'),
     fx('LRU hit rate', 'hit rate = hits / (hits + misses)', 'square with maxsize 2 on 1, 2, 1, 3, 2: 1 hit, 4 misses, 20 %.'))}
{steps('Worked example: why fib(25) with @cache has 23 hits', [
    'fib(25) misses and calls fib(24), which misses and calls fib(23), and so on down to fib(1): 25 misses on the way down.',
    'Back in fib(2), the second call fib(0) has never been seen: one more miss, 26 in total.',
    'Back in fib(3) up to fib(25), each second call fib(n &minus; 2) finds its answer already cached: 23 hits.',
    eq('cache_info() reports hits=23, misses=26')])}
''', kw=['memoization', 'Fibonacci calls', 'golden ratio', 'exponential backoff', 'hit rate', 'complexity'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>Know that @decorator above a def means f = decorator(f), and use built in decorators such as @cache.</p>',
    '<p>Write decorators with *args and **kwargs and @wraps, decorators that keep state, decorators with arguments, and know the order of stacked decorators.</p>',
    '<p>Write class decorators and classes used as decorators, decorate methods safely, combine positional only and keyword only parameters, and use caching with a clear idea of when results may go stale.</p>',
    '<p>Decorators are just expressions evaluated at definition time (any expression since PEP 614). To decorate methods with a class based decorator, implement the descriptor protocol (__get__) so it binds self. Type checkers keep the signature of a wrapper with ParamSpec and Concatenate (PEP 612).</p>')}
{grow('Use @decorators and write a simple wrapper with @wraps.',
      'Write decorators with arguments, with state, and stack them correctly.',
      'Write class decorators, descriptor aware decorators and typed decorators with ParamSpec.')}
''', kw=['beginner', 'expert', 'PEP 614', 'ParamSpec', 'PEP 612', 'descriptor decorator'])

lc(746, 'Min Cost Climbing Stairs', 'min-cost-climbing-stairs', 'e', 'Top down with @cache', 'best(i) is the cheapest way to stand past the top from step i: cost[i] + min(best(i + 1), best(i + 2)). Start from step 0 or 1.', r'''
from functools import cache


def min_cost_climbing_stairs(cost):
    @cache
    def best(i):
        if i >= len(cost):
            return 0
        return cost[i] + min(best(i + 1), best(i + 2))
    return min(best(0), best(1))
''', [('min_cost_climbing_stairs([10, 15, 20])', 15), ('min_cost_climbing_stairs([1, 100, 1, 1, 1, 100, 1, 1, 100, 1])', 6)])
lc(62, 'Unique Paths', 'unique-paths', 'm', 'Paths from a cell, cached', 'paths(r, c) = paths(r + 1, c) + paths(r, c + 1), and 1 on the last row or column.', r'''
from functools import cache


def unique_paths(m, n):
    @cache
    def paths(r, c):
        if r == m - 1 or c == n - 1:
            return 1
        return paths(r + 1, c) + paths(r, c + 1)
    return paths(0, 0)
''', [('unique_paths(3, 7)', 28), ('unique_paths(3, 2)', 3)])
lc(64, 'Minimum Path Sum', 'minimum-path-sum', 'm', 'Cheapest from a cell, cached', 'cost(r, c) is the grid value plus the cheaper of moving down or right.', r'''
from functools import cache


def min_path_sum(grid):
    rows, cols = len(grid), len(grid[0])

    @cache
    def cost(r, c):
        if r == rows - 1 and c == cols - 1:
            return grid[r][c]
        options = []
        if r + 1 < rows:
            options.append(cost(r + 1, c))
        if c + 1 < cols:
            options.append(cost(r, c + 1))
        return grid[r][c] + min(options)
    return cost(0, 0)
''', [('min_path_sum([[1, 3, 1], [1, 5, 1], [4, 2, 1]])', 7), ('min_path_sum([[1, 2, 3], [4, 5, 6]])', 12)])
lc(91, 'Decode Ways', 'decode-ways', 'm', 'Ways from a position, cached', 'From position i, take one digit (if not 0) or two digits (if 10 to 26) and add the ways for the rest.', r'''
from functools import cache


def num_decodings(s):
    @cache
    def ways(i):
        if i == len(s):
            return 1
        if s[i] == "0":
            return 0
        total = ways(i + 1)
        if i + 1 < len(s) and 10 <= int(s[i:i + 2]) <= 26:
            total += ways(i + 2)
        return total
    return ways(0)
''', [('num_decodings("12")', 2), ('num_decodings("226")', 3), ('num_decodings("06")', 0)])
lc(139, 'Word Break', 'word-break', 'm', 'Can the rest be split, cached', 'From position i, try every dictionary word that matches there and ask the same question for the rest.', r'''
from functools import cache


def word_break(s, wordDict):
    words = set(wordDict)

    @cache
    def can(i):
        if i == len(s):
            return True
        for j in range(i + 1, len(s) + 1):
            if s[i:j] in words and can(j):
                return True
        return False
    return can(0)
''', [('word_break("leetcode", ["leet", "code"])', True), ('word_break("applepenapple", ["apple", "pen"])', True), ('word_break("catsandog", ["cats", "dog", "sand", "and", "cat"])', False)])
lc(198, 'House Robber', 'house-robber', 'm', 'Rob or skip, cached', 'best(i) = max(rob house i and jump two, or skip to i + 1).', r'''
from functools import cache


def rob(nums):
    @cache
    def best(i):
        if i >= len(nums):
            return 0
        return max(nums[i] + best(i + 2), best(i + 1))
    return best(0)
''', [('rob([1, 2, 3, 1])', 4), ('rob([2, 7, 9, 3, 1])', 12)])
lc(322, 'Coin Change', 'coin-change', 'm', 'Fewest coins for an amount, cached', 'fewest(a) = 1 + the smallest fewest(a - coin). Use infinity for impossible amounts.', r'''
from functools import cache


def coin_change(coins, amount):
    @cache
    def fewest(a):
        if a == 0:
            return 0
        best = float("inf")
        for coin in coins:
            if coin <= a:
                best = min(best, 1 + fewest(a - coin))
        return best
    answer = fewest(amount)
    return -1 if answer == float("inf") else answer
''', [('coin_change([1, 2, 5], 11)', 3), ('coin_change([2], 3)', -1), ('coin_change([1], 0)', 0)])
lc(343, 'Integer Break', 'integer-break', 'm', 'Best split, cached', 'For each first piece k, either keep the rest whole or break it further: max(k * (n - k), k * best(n - k)).', r'''
from functools import cache


def integer_break(n):
    @cache
    def best(m):
        result = 0
        for k in range(1, m):
            result = max(result, k * (m - k), k * best(m - k))
        return result
    return best(n)
''', [('integer_break(2)', 1), ('integer_break(10)', 36)])
lc(96, 'Unique Binary Search Trees', 'unique-binary-search-trees', 'm', 'Catalan numbers, cached', 'Choose each value as the root. The trees on the left and right are independent, so multiply their counts.', r'''
from functools import cache


def num_trees(n):
    @cache
    def count(k):
        if k <= 1:
            return 1
        total = 0
        for root in range(1, k + 1):
            total += count(root - 1) * count(k - root)
        return total
    return count(n)
''', [('num_trees(3)', 5), ('num_trees(1)', 1), ('num_trees(5)', 42)])
lc(494, 'Target Sum', 'target-sum', 'm', 'Ways from (index, total), cached', 'At each number add it or subtract it. Count the ways that land exactly on target.', r'''
from functools import cache


def find_target_sum_ways(nums, target):
    @cache
    def ways(i, total):
        if i == len(nums):
            return 1 if total == target else 0
        return ways(i + 1, total + nums[i]) + ways(i + 1, total - nums[i])
    return ways(0, 0)
''', [('find_target_sum_ways([1, 1, 1, 1, 1], 3)', 5), ('find_target_sum_ways([1], 1)', 1)])

K.lesson('leetcode', 'LeetCode practice', leet('<p>Every solution here is plain recursion plus one line, @cache. That is memoisation by decorator: the recursion states the idea clearly, and the decorator removes the repeated work. Compare the call counts in the maths lesson.</p>'), kw=['LeetCode', 'memoization', 'dynamic programming', 'functools.cache', 'top down'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'Parameters: positional only before /, keyword only after * or *args, *args is a tuple, **kwargs is a dict. At a call, * and ** unpack.',
    'Functions are objects: name them, store them, pass them, return them. A closure remembers the variables of the function that made it.',
    '@d above def f means f = d(f). A decorator usually returns a wrapper(*args, **kwargs) that calls the original.',
    'Always use @functools.wraps(func) on the wrapper to keep the name, docstring and __wrapped__.',
    'Decorators with arguments have three levels: factory(settings), decorator(func), wrapper(*args).',
    'Stacked decorators are applied bottom up and run top down: @a @b def f is a(b(f)).',
    'Decorators can keep state, take classes, or be classes with __call__. @cache and @lru_cache memoise pure functions.'],
    '1.3 covers class design: class and static methods, properties, abstract classes, dataclasses and __slots__.')}
{files('Three tasks: a call counting decorator, a retry decorator with a number of attempts, and a decorator that checks arguments are positive.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'What does @shout above def add mean?', ['add = add(shout)', 'add = shout(add)', 'shout = add(shout)', 'Nothing until add is called'], 1, 'The decorator gets the function.', '@shout runs add = shout(add) right after the def.')
K.quiz('e', 'In def f(*args), what is args?', ['A list', 'A tuple', 'A dict', 'A set'], 1, 'Collected positional values.', '*args collects extra positional arguments into a tuple.')
K.quiz('e', 'What does functools.wraps do?', ['Makes the function faster', 'Copies the name and docstring of the original onto the wrapper', 'Caches results', 'Catches errors'], 1, 'Metadata.', 'Without it the wrapper keeps its own name, "wrapper".')
K.quiz('m', 'def f(a, /, b): ... Which call fails?', ['f(1, 2)', 'f(1, b=2)', 'f(a=1, b=2)', 'All work'], 2, 'Before / is positional only.', 'a cannot be passed by name.')
K.quiz('m', 'def g(a, *, b): ... What does g(1, 2) do?', ['Works with b = 2', 'TypeError', 'b is None', 'a is (1, 2)'], 1, 'After * is keyword only.', 'b must be passed as b=2.')
K.quiz('m', '@a then @b above def f. What is f?', ['b(a(f))', 'a(b(f))', 'a(f) and b(f)', 'f'], 1, 'Nearest first.', 'b is applied first, then a wraps the result.')
K.quiz('m', 'How many nested functions does a typical decorator with arguments have?', ['1', '2', '3', '4'], 2, 'Settings, function, call.', 'factory(settings) returns decorator(func), which returns wrapper(*args).')
K.quiz('m', 'Which functions are safe to wrap with @cache?', ['Any function', 'Functions whose result depends only on their hashable arguments', 'Functions that print', 'Functions that read the clock'], 1, 'Pure functions.', 'Caching a function that reads changing data would return stale answers.')
K.quiz('h', 'A wrapper is written without return before func(*args). What does the decorated function return?', ['The original result', 'None', 'The wrapper', 'An error'], 1, 'No return.', 'The wrapper computes the result but throws it away and returns None.')
K.quiz('h', 'Someone writes @retry instead of @retry(3), where retry(attempts) is a factory. What happens?', ['It works with a default', 'retry receives the function as attempts and returns decorate, so the name now points to decorate', 'SyntaxError', 'The function runs three times'], 1, 'Missing brackets.', 'The function becomes the attempts value. Calling it later passes your argument as func, a confusing bug.')
K.quiz('h', 'When does the body of a decorator (outside the wrapper) run?', ['At every call', 'Once, when the decorated def runs', 'Never', 'When the program ends'], 1, 'Definition time.', 'The decorator runs at definition time. Only the wrapper runs at each call.')
K.quiz('x', 'In the style of a Stanford CS 41 exam: def log(f): print("deco"), then return f. Then @log above def g(): return 1. The program calls g() twice. How many times is "deco" printed?', ['0', '1', '2', '3'], 1, 'Definition time only.', 'The decorator body runs once when def g runs. Calls go straight to g because log returned it unchanged.')
K.quiz('x', 'In the style of a CMU 15-150 question: plain recursive fib makes C(n) = 2F(n + 1) &minus; 1 calls. With @cache, how many calls does fib(n) make that are cache misses?', ['n', 'n + 1', '2n', 'F(n)'], 1, 'Each argument once.', 'fib(0) to fib(n) are each computed once.')

K.calc('e', 'describe("Ravi", 25, "chess", "music", lang="hi"): how many items are in hobbies?', '2', 'Extra positional values.', ['name = "Ravi", age = 25.', 'The rest are "chess" and "music".', eq('2')], check=2)
K.calc('e', '@repeat(3) on wave. How many times does one call wave("Asha") run the original?', '3', 'The wrapper loops times times.', ['times = 3.', 'The loop calls func each turn.', eq('3')], check=3)
K.calc('e', 'greet is called 3 times with @count_calls. What is greet.calls?', '3', 'One per call.', ['Starts at 0.', 'Each call adds 1.', eq('3')], check=3)
K.calc('m', 'Plain recursive fib(10): how many calls, using C(n) = 2F(n + 1) &minus; 1 with F(11) = 89?', '177', '2 &times; 89 &minus; 1.', ['F(11) = 89.', '2 &times; 89 = 178.', eq('177')], check=2 * 89 - 1)
K.calc('m', 'fib(25) with @cache: how many misses?', '26', 'n + 1.', ['fib(0) to fib(25).', 'Each computed once.', eq('26')], check=26)
K.calc('m', 'Exponential backoff with base 2 s and 3 retries: total waiting in seconds?', '14', 'base(2<sup>n</sup> &minus; 1).', ['Waits 2, 4, 8.', '2 + 4 + 8.', eq('14 = 2 &times; (2<sup>3</sup> &minus; 1)')], check=2 * (2 ** 3 - 1))
K.calc('m', 'lru_cache(maxsize=2) on square, called with 1, 2, 1, 3, 2. How many misses?', '4', 'Track the 2 most recent.', ['1 miss, 2 miss, 1 hit (now 2, 1), 3 miss (drops 2).', '2 is no longer cached: miss.', eq('4 misses, 1 hit')], check=4)
K.calc('h', 'Unique paths in a 3 by 7 grid, which is C(8, 2).', '28', '8 moves, choose the 2 down moves.', ['2 down and 6 right moves: 8 in total.', 'C(8, 2) = 8 &times; 7 / 2.', eq('28')], check=28)
K.calc('h', '@tag("b") above @tag("i") above hello. How many lines does one call print before the result line (enter and leave lines)?', '4', 'Each wrapper prints enter and leave.', ['enter b, enter i.', 'leave i, leave b.', eq('4')], check=4)
K.calc('x', 'In the style of an Oxford problem: the number of BSTs with n keys is the Catalan number C<sub>n</sub> = (2n)! / ((n + 1)! n!). What is C<sub>5</sub>?', '42', '10! / (6! 5!).', ['10! / 5! = 30,240.', '30,240 / 720 = 42.', eq('42')], check=42)

K.assign('countcalls', 'e', 'A call counting decorator',
         '<p>Write a decorator <code>count_calls</code> that counts how many times the decorated function has been called, in an attribute <code>calls</code> on the decorated function. It must return the original result and keep the original <code>__name__</code> (use functools.wraps).</p>',
         '''
from functools import wraps


def count_calls(func):
    # your code here
    return func


@count_calls
def double(n):
    return n * 2
''', [('(double(2), double(5), double.calls)', [4, 10, 2]), ('double.__name__', 'double')],
         '''
from functools import wraps


def count_calls(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        wrapper.calls = wrapper.calls + 1
        return func(*args, **kwargs)
    wrapper.calls = 0
    return wrapper


@count_calls
def double(n):
    return n * 2
''', 'Inside count_calls define wrapper(*args, **kwargs) with @wraps(func). Set wrapper.calls = 0 before returning wrapper, and add 1 inside it.', '<p>A function is an object, so it can carry its own attributes like calls. The test reads double.calls, which is really wrapper.calls.</p>')
K.assign('retry', 'm', 'A retry decorator',
         '<p>Write <code>retry(attempts)</code>, a decorator with an argument. The wrapper calls the function up to attempts times. If a call succeeds, return its result at once. If every attempt raises an exception, raise the last exception again. make_flaky(n) is a helper that fails n times and then returns "ok".</p>',
         '''
from functools import wraps


def retry(attempts):
    # your code here
    pass


def make_flaky(failures):
    """Helper for the tests: a function that raises ConnectionError failures times, then returns "ok"."""
    state = {"left": failures}
    def flaky():
        if state["left"] > 0:
            state["left"] -= 1
            raise ConnectionError("try again")
        return "ok"
    return flaky


def raises(func, *args):
    try:
        func(*args)
    except Exception as err:
        return type(err).__name__
    return None
''', [('retry(3)(make_flaky(2))()', 'ok'), ('raises(retry(2)(make_flaky(2)))', 'ConnectionError'), ('retry(1)(make_flaky(0))()', 'ok')],
         '''
from functools import wraps


def retry(attempts):
    def decorate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as err:
                    last_error = err
            raise last_error
        return wrapper
    return decorate


def make_flaky(failures):
    """Helper for the tests: a function that raises ConnectionError failures times, then returns "ok"."""
    state = {"left": failures}
    def flaky():
        if state["left"] > 0:
            state["left"] -= 1
            raise ConnectionError("try again")
        return "ok"
    return flaky


def raises(func, *args):
    try:
        func(*args)
    except Exception as err:
        return type(err).__name__
    return None
''', 'Three levels: retry(attempts) returns decorate(func), which returns wrapper. In the wrapper loop attempts times with try and return, remember the error, and raise it after the loop.', '<p>retry(3)(make_flaky(2)) is exactly what @retry(3) does: it fails twice and succeeds on the third attempt. Real code adds a growing wait between attempts (backoff).</p>')
K.assign('positive', 'm', 'Check that arguments are positive',
         '<p>Write a decorator <code>positive_args</code> that raises <code>ValueError</code> if any positional argument is a number that is 0 or less, before calling the function. Otherwise it calls the function and returns its result. Keep the name with wraps.</p>',
         '''
from functools import wraps


def positive_args(func):
    # your code here
    return func


@positive_args
def area(w, h):
    return w * h


def raises(func, *args):
    try:
        func(*args)
    except Exception as err:
        return type(err).__name__
    return None
''', [('area(3, 4)', 12), ('raises(area, 3, -1)', 'ValueError'), ('raises(area, 0, 5)', 'ValueError'), ('area.__name__', 'area')],
         '''
from functools import wraps


def positive_args(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        for value in args:
            if value <= 0:
                raise ValueError("arguments must be positive")
        return func(*args, **kwargs)
    return wrapper


@positive_args
def area(w, h):
    return w * h


def raises(func, *args):
    try:
        func(*args)
    except Exception as err:
        return type(err).__name__
    return None
''', 'Loop over args in the wrapper and raise ValueError for any value that is not above 0. Then return func(*args, **kwargs).', '<p>The check lives in one decorator and protects every function it is put on. This is how validation decorators in web frameworks work.</p>')

K.must('Parameters', 'a, / positional only. *args tuple. after * keyword only. **kwargs dict. f(*seq, **d) unpacks at a call.')
K.must('Closures', 'Functions are objects. An inner function remembers the variables of the outer one (__closure__), even after it returned.')
K.must('Decorator shape', '@d def f is f = d(f). def d(func): @wraps(func) def wrapper(*args, **kwargs): ... return func(*args, **kwargs). return wrapper.')
K.must('Arguments and stacking', '@d(x) is f = d(x)(f): three levels. @a @b def f is a(b(f)): applied bottom up, run top down.')
K.must('Built ins', '@cache, @lru_cache(maxsize), @wraps, @property, @classmethod, @staticmethod, @dataclass, @contextmanager. Cache only pure functions.')

T = K.topic(
    slug='py-decorators', topic='py-decorators', step=(1, 'Advanced object oriented programming', 'py-a1', 'Make classes behave like built in types, then master decorators, class design, exceptions, copying, serialisation and metaclasses.', 'Advanced'),
    title='Extended arguments, closures and decorators', short='Decorators', badge='1.2', minutes=75,
    lead='Add behaviour to functions without touching their code. Learn positional only and keyword only parameters, *args and **kwargs for forwarding, functions as objects and closures, decorators with functools.wraps, decorators that keep state, decorators with arguments, stacking, class decorators and caching with @cache.',
    desc='positional only and keyword only parameters, *args and **kwargs, unpacking at a call, first class functions, closures and __closure__, decorators and the @ syntax, functools.wraps, stateful decorators, decorator factories with arguments, retry, stacking order, class decorators, classes as decorators with __call__, functools.cache and lru_cache, memoisation maths and exponential backoff.',
    summary='parameters, closures, decorators, wraps, decorator factories, stacking, class decorators, cache.',
    keywords=['decorator', 'closure', '*args', '**kwargs', 'positional only', 'keyword only', 'functools.wraps', 'lru_cache', 'cache', 'decorator factory', 'class decorator', 'PCPP'],
    recap='<p>A decorator is a function that returns a better function. Use *args, **kwargs and @wraps in every wrapper, and remember that decorators run once at definition time while wrappers run at every call.</p>',
    added='2026-11-07', leet=leet_items())
