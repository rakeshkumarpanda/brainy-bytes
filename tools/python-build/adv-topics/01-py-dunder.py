# Advanced Python 1.1: special methods and operator overloading. Follows PCPP-32-101 block 1 (advanced object
# oriented programming: special methods, operator overloading, emulating built in types), checked against the Python
# 3.14 data model reference (section 3.3 "Special method names"), the functools.total_ordering and operator module
# documentation, and the fractions module.
import math
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, lc, leet, files, grow, leet_items

chapter('py-dunder')
K = Kit()

K.code('vector', r'''
import math


class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Vector({self.x}, {self.y})"

    def __add__(self, other):                  # v + w
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other):                  # v - w
        return Vector(self.x - other.x, self.y - other.y)

    def __mul__(self, k):                      # v * 3
        return Vector(self.x * k, self.y * k)

    def __rmul__(self, k):                     # 3 * v
        return self * k

    def __neg__(self):                         # -v
        return Vector(-self.x, -self.y)

    def __abs__(self):                         # abs(v)
        return math.hypot(self.x, self.y)

    def __eq__(self, other):                   # v == w
        return isinstance(other, Vector) and (self.x, self.y) == (other.x, other.y)

    def __bool__(self):                        # if v:
        return self.x != 0 or self.y != 0


a = Vector(3, 4)
b = Vector(1, 2)
print(a + b, a - b, a * 2, 2 * a, -a)
print(abs(a), a == Vector(3, 4), bool(Vector(0, 0)))
print(a.__add__(b))                            # what a + b really runs
''')

K.code('compare', r'''
from functools import total_ordering


@total_ordering                                # writes <=, > and >= from == and <
class Version:
    def __init__(self, text):
        self.parts = tuple(int(p) for p in text.split("."))

    def __repr__(self):
        return "Version(" + ".".join(str(p) for p in self.parts) + ")"

    def __eq__(self, other):
        return self.parts == other.parts

    def __lt__(self, other):
        return self.parts < other.parts        # tuples compare item by item


versions = [Version("3.14.0"), Version("3.9.7"), Version("3.10.2")]
print(sorted(versions))
print(max(versions), Version("3.9") <= Version("3.10"), Version("2.7") >= Version("3.0"))
print(sorted(["3.14.0", "3.9.7", "3.10.2"]))   # as plain text the order is wrong
''')

K.code('hashing', r'''
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Point({self.x}, {self.y})"

    def __eq__(self, other):
        return isinstance(other, Point) and (self.x, self.y) == (other.x, other.y)

    def __hash__(self):                        # equal objects MUST have equal hashes
        return hash((self.x, self.y))


points = {Point(1, 2), Point(1, 2), Point(3, 4)}
print(len(points), Point(1, 2) in points)
seen = {Point(0, 0): "origin"}
print(seen[Point(0, 0)])

p = Point(5, 5)
box = {p}
p.x = 6                                        # changing a key after it is in a set
print(p in box, Point(6, 5) in box)            # it can no longer be found
''')

K.code('container', r'''
class Playlist:
    def __init__(self, songs):
        self.songs = list(songs)

    def __len__(self):                         # len(p)
        return len(self.songs)

    def __getitem__(self, index):              # p[0], p[-1], p[1:3]
        if isinstance(index, slice):
            return Playlist(self.songs[index])
        return self.songs[index]

    def __setitem__(self, index, song):        # p[0] = "new"
        self.songs[index] = song

    def __contains__(self, song):              # "x" in p
        return song.lower() in (s.lower() for s in self.songs)

    def __iter__(self):                        # for s in p
        return iter(self.songs)

    def __repr__(self):
        return f"Playlist({self.songs})"


p = Playlist(["Tum Hi Ho", "Kesariya", "Naatu Naatu", "Jai Ho"])
print(len(p), p[0], p[-1])
print(p[1:3])
p[0] = "Chaiyya Chaiyya"
print("kesariya" in p, "Believer" in p)
for song in p:
    print("-", song)
print(list(reversed(p)))                       # reversed works with __len__ and __getitem__
''')

K.code('call', r'''
class Counter:
    def __init__(self):
        self.count = 0

    def __call__(self, step=1):                # lets the object be called like a function
        self.count += step
        return self.count


clicks = Counter()
clicks()
clicks()
print(clicks(5), clicks.count)
print(callable(clicks), callable(5), callable(len))
''')

K.code('format', r'''
class Money:
    def __init__(self, amount):
        self.amount = amount

    def __repr__(self):                        # for developers
        return f"Money({self.amount!r})"

    def __str__(self):                         # for users
        return f"Rs {self.amount:,.2f}"

    def __format__(self, spec):                # f"{m:...}" and format(m, ...)
        if spec == "words":
            return f"{self.amount} rupees"
        return "Rs " + format(self.amount, spec)


m = Money(1234567.5)
print(repr(m))
print(str(m))
print(f"{m:,.0f} | {m:words} | {m:>12.1f}")
print([m])
''')

K.code('inplace', r'''
class Bag:
    def __init__(self):
        self.items = []

    def __iadd__(self, item):                  # bag += item changes the bag itself
        self.items.append(item)
        return self                            # += assigns whatever comes back

    def __repr__(self):
        return f"Bag({self.items})"


bag = Bag()
same = bag
bag += "pen"
bag += "book"
print(bag, same is bag)

nums = [1, 2]
alias = nums
nums += [3]                                    # list has __iadd__: changes in place
print(alias)
tup = (1, 2)
alias = tup
tup += (3,)                                    # tuple has no __iadd__: falls back to __add__, a new tuple
print(alias, tup)
''')

K.code('attrs', r'''
class Config:
    def __init__(self, **values):
        self.__dict__["values"] = values       # avoid our own __setattr__ here

    def __getattr__(self, name):               # only called when normal lookup FAILS
        if name in self.values:
            return self.values[name]
        raise AttributeError(f"no setting called {name!r}")

    def __setattr__(self, name, value):        # called for EVERY attribute assignment
        if name == "port" and not 0 < value < 65536:
            raise ValueError("port must be 1 to 65535")
        self.values[name] = value


cfg = Config(host="localhost", port=8000)
print(cfg.host, cfg.port)
cfg.port = 8080
print(cfg.values)
try:
    cfg.port = 99999
except ValueError as err:
    print("ValueError:", err)
try:
    cfg.timeout
except AttributeError as err:
    print("AttributeError:", err)
''')

K.code('fraction', r'''
import math
from fractions import Fraction


class Frac:
    def __init__(self, top, bottom):
        if bottom == 0:
            raise ZeroDivisionError("bottom cannot be 0")
        g = math.gcd(top, bottom)              # keep it in lowest terms
        if bottom < 0:
            g = -g
        self.top = top // g
        self.bottom = bottom // g

    def __add__(self, other):                  # a/b + c/d = (ad + cb) / bd
        return Frac(self.top * other.bottom + other.top * self.bottom, self.bottom * other.bottom)

    def __mul__(self, other):                  # a/b * c/d = ac / bd
        return Frac(self.top * other.top, self.bottom * other.bottom)

    def __eq__(self, other):
        return (self.top, self.bottom) == (other.top, other.bottom)

    def __float__(self):
        return self.top / self.bottom

    def __repr__(self):
        return f"{self.top}/{self.bottom}"


print(Frac(1, 2) + Frac(1, 3), Frac(2, 4), Frac(3, -6))
print(Frac(2, 3) * Frac(9, 4), float(Frac(1, 8)))
print(Frac(1, 2) + Frac(1, 3) == Frac(5, 6))
print(Fraction(1, 2) + Fraction(1, 3))         # the standard library version
print(0.1 + 0.2, Fraction(1, 10) + Fraction(2, 10))
''')

K.lesson('idea', 'Special methods: make your class feel built in', f'''
{src('Python 3.14 data model reference section 3.3 "Special method names", the functools and fractions documentation, and PCPP-32-101 block 1.')}
{wwh('<b>Special methods</b> (also called magic methods or dunder methods, for "double underscore") are methods with names like __add__ or __len__ that Python calls for you when you use an operator or a built in function on your object.',
     'Built in types work with +, ==, len, in, for and print. Your own classes do not, unless you tell Python how. Without special methods you would write v.add(w) and v.equals(w), which is harder to read and does not work with sorted, sum, sets or dicts.',
     'Python turns every operator into a method call on the type of the object: a + b becomes type(a).__add__(a, b), len(x) becomes type(x).__len__(x). Write those methods and your objects join in with every part of Python that uses them. Changing the meaning of an operator for your class is called <b>operator overloading</b>.')}
{scene('a universal socket', '<p>A phone charger works in any socket because it has the standard plug shape. Python operators are the sockets. A special method is your class giving itself the standard plug, so + and len and for can use it like any built in type.</p>')}
{viz('pydunder')}
{run('vector')}
''', kw=['special methods', 'magic methods', 'dunder', 'operator overloading', '__add__', 'data model'])

K.lesson('table', 'The main special methods', f'''
{table(['You write', 'Python calls', 'Group'], [
    ['repr(x), str(x), format(x, s)', '__repr__, __str__, __format__', 'Text'],
    ['x + y, x - y, x * y, x / y, x // y, x % y, x ** y, x @ y', '__add__, __sub__, __mul__, __truediv__, __floordiv__, __mod__, __pow__, __matmul__', 'Arithmetic'],
    ['y + x when y does not know x', '__radd__ and the other r methods on x', 'Reflected'],
    ['x += y', '__iadd__ (or __add__ then assign)', 'In place'],
    ['-x, +x, abs(x), ~x', '__neg__, __pos__, __abs__, __invert__', 'Unary'],
    ['x == y, x != y, x &lt; y, x &lt;= y, x &gt; y, x &gt;= y', '__eq__, __ne__, __lt__, __le__, __gt__, __ge__', 'Comparison'],
    ['hash(x), set and dict keys', '__hash__', 'Hashing'],
    ['bool(x), if x', '__bool__, else __len__', 'Truth'],
    ['len(x), x[i], x[i] = v, del x[i], v in x', '__len__, __getitem__, __setitem__, __delitem__, __contains__', 'Container'],
    ['for v in x, iter(x), next(it)', '__iter__, __next__', 'Iteration (2.1)'],
    ['x(...)', '__call__', 'Callable'],
    ['with x:', '__enter__, __exit__', 'Context manager (2.3)'],
    ['x.name when it is missing, x.name = v', '__getattr__, __setattr__', 'Attributes'],
    ['int(x), float(x), round(x)', '__int__, __float__, __round__', 'Conversion']])}
{note('Special methods are looked up on the <b>class</b>, not on the object. Setting obj.__len__ = ... on one object does nothing for len(obj). Also, never invent your own __names__: they are reserved for Python.', 'exam')}
''', kw=['special method table', '__getitem__', '__len__', '__call__', '__iter__', '__matmul__', 'class lookup'])

K.lesson('arith', 'Arithmetic, reflected and unary operators', f'''
{run('vector')}
{steps('What Python does for a + b', [
    'Call type(a).__add__(a, b).',
    'If that method is missing or returns NotImplemented, call type(b).__radd__(b, a).',
    'If that is missing or returns NotImplemented too, raise TypeError: unsupported operand type(s).',
    'Special case: if b is an instance of a child class of type(a) that overrides __radd__, Python tries b first.'])}
{note('Return the special value NotImplemented (not raise NotImplementedError) when your method cannot handle the other type. That gives the other object a chance to answer. Raising stops Python from trying.', 'exam')}
''', kw=['__radd__', 'reflected operands', 'NotImplemented', '__neg__', '__abs__', 'operator overloading'])

K.lesson('compare', 'Comparisons and total_ordering', f'''
{run('compare')}
{versus('Writing comparisons', ['', 'all six methods by hand', '@total_ordering with __eq__ and __lt__'], [
    ['Lines of code', 'Many, easy to make inconsistent', 'Two methods'],
    ['Speed', 'Fastest', 'Slightly slower for the generated ones'],
    ['Needed for sorted, min, max', '__lt__ is enough', '__lt__ is enough'],
    ['Good for', 'Hot loops', 'Almost everything else']],
    'write __eq__ and __lt__ and let functools.total_ordering write the rest. Or use a dataclass with order=True (1.3).')}
{note('If you write __eq__ but not __ne__, Python gives != for free by inverting __eq__.', 'tip')}
''', kw=['__lt__', '__eq__', 'total_ordering', 'sorting objects', 'comparison operators', 'rich comparison'])

K.lesson('hashing', 'The hash contract', f'''
{run('hashing')}
{steps('The rules for __eq__ and __hash__', [
    'If a == b, then hash(a) must equal hash(b). Otherwise sets and dicts will hold duplicates or lose items.',
    'Writing __eq__ sets __hash__ to None, so the class becomes unhashable until you write __hash__ too.',
    'Build the hash from the same fields that __eq__ compares, for example hash((self.x, self.y)).',
    'Only hash fields that never change. Changing a field after the object is in a set or dict hides it, as the last line shows.'])}
''', kw=['__hash__', 'hash contract', 'hashable', 'set of objects', 'dict key object', 'immutable'])

K.lesson('container', 'Emulating containers', f'''
{run('container')}
{note('A class with only __len__ and __getitem__ already works with for, in, reversed and slicing. That is why Python calls this the <b>sequence protocol</b>. Inheriting from collections.abc.Sequence (or MutableSequence) also gives you index, count and more for free.', 'tip')}
{deep('Slices are objects', '<p>p[1:3] passes a slice object slice(1, 3, None) to __getitem__. Its start, stop and step attributes, and its indices(len) method, let you handle any slice correctly. That is how NumPy supports a[1:3, ::2].</p>')}
''', kw=['__getitem__', '__setitem__', '__contains__', 'sequence protocol', 'slice object', 'collections.abc'])

K.lesson('call', 'Callable objects, text formats and in place operators', f'''
{run('call')}
{run('format')}
{run('inplace')}
{note('x += y first tries x.__iadd__(y) and then ASSIGNS the result to x. That is why __iadd__ must return self. A tuple has no __iadd__, so += makes a new tuple and other names still see the old one.', 'exam')}
''', kw=['__call__', 'callable', '__format__', 'format spec', '__iadd__', 'in place operator'])

K.lesson('attrs', 'Attribute hooks: __getattr__ and __setattr__', f'''
{run('attrs')}
{versus('Three attribute hooks', ['', '__getattr__', '__getattribute__', '__setattr__'], [
    ['Called when', 'Normal lookup failed', 'EVERY attribute read', 'EVERY attribute assignment'],
    ['Typical use', 'Defaults, proxies, lazy loading', 'Rare: logging every access', 'Validation, read only objects'],
    ['Danger', 'Small', 'Infinite recursion if you read self.x inside it', 'Infinite recursion if you write self.x inside it']],
    'prefer properties (1.3) for one or two checked attributes, and keep these hooks for whole groups of names.')}
''', kw=['__getattr__', '__setattr__', '__getattribute__', 'proxy', 'validation', 'recursion'])

K.lesson('maths', 'The maths: fractions and vectors with operators', f'''
{run('fraction')}
{fxs(fx('Adding fractions', 'a/b + c/d = (ad + cb) / bd', '1/2 + 1/3 = (3 + 2) / 6 = 5/6.', key=True),
     fx('Lowest terms', 'divide top and bottom by g = gcd(top, bottom)', '2/4: gcd(2, 4) = 2, so 1/2.', key=True),
     fx('Euclid', 'gcd(a, b) = gcd(b, a mod b), gcd(a, 0) = a', 'gcd(48, 18) = gcd(18, 12) = gcd(12, 6) = gcd(6, 0) = 6.'),
     fx('Vector length', '|v| = &radic;(x<sup>2</sup> + y<sup>2</sup>)', 'abs(Vector(3, 4)) = 5.0, using math.hypot.'),
     fx('Scaling', 'k(x, y) = (kx, ky)', '2 * Vector(3, 4) = Vector(6, 8), through __rmul__.'),
     fx('Dot product with @', 'a @ b = a<sub>x</sub>b<sub>x</sub> + a<sub>y</sub>b<sub>y</sub>', 'Python 3.5 added @ (__matmul__) for exactly this kind of product.'))}
{steps('Worked example: 2/3 &times; 9/4', [
    'Multiply tops and bottoms: 18 / 12.',
    'gcd(18, 12) = 6.',
    eq('18/12 = 3/2, which the program printed')])}
{note('0.1 + 0.2 is 0.30000000000000004 with floats, but Fraction(1, 10) + Fraction(2, 10) is exactly 3/10. Use Fraction or Decimal when exact answers matter, such as money.', 'tip')}
''', kw=['fraction class', 'gcd', 'Euclid algorithm', 'lowest terms', 'vector operators', 'matmul', 'Fraction', 'exact arithmetic'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>Write __repr__, __str__ and __eq__ so objects print nicely and compare by value.</p>',
    '<p>Overload arithmetic and comparison operators, use total_ordering, keep __eq__ and __hash__ consistent, and make containers with __len__, __getitem__ and __contains__.</p>',
    '<p>Return NotImplemented correctly, handle reflected and in place operators, accept slice objects, write __call__ and __format__, and use __getattr__ and __setattr__ without recursion.</p>',
    '<p>Special methods are looked up on the type through slots (tp_as_number, tp_as_sequence in CPython), which is why setting them on an instance has no effect and why they are fast. Implicit lookups skip __getattribute__. The numbers and collections.abc hierarchies define which methods make a type a Number, a Sequence or a Mapping.</p>')}
{grow('Write __repr__, __str__ and __eq__.',
      'Overload operators, comparisons, hashing and the container protocol.',
      'Explain NotImplemented, reflected operands, slot lookup and the abc protocols.')}
''', kw=['beginner', 'expert', 'slots', 'type slots', 'numbers abc', 'collections.abc'])

lc(592, 'Fraction Addition and Subtraction', 'fraction-addition-and-subtraction', 'm', 'Parse, add, reduce with gcd', 'Read each signed fraction, add it to a running a/b with (ad + cb) / bd, then divide by the gcd.', r'''
import math


def fraction_addition(expression):
    top, bottom = 0, 1
    i = 0
    while i < len(expression):
        j = i + 1
        while j < len(expression) and expression[j] not in "+-":
            j += 1
        part = expression[i:j]                 # like "-1/2" or "1/3"
        a, b = part.split("/")
        a, b = int(a), int(b)
        top = top * b + a * bottom
        bottom = bottom * b
        g = math.gcd(top, bottom)
        top, bottom = top // g, bottom // g
        i = j
    return str(top) + "/" + str(bottom)
''', [('fraction_addition("-1/2+1/2")', '0/1'), ('fraction_addition("-1/2+1/2+1/3")', '1/3'), ('fraction_addition("1/3-1/2")', '-1/6')])
lc(166, 'Fraction to Recurring Decimal', 'fraction-to-recurring-decimal', 'm', 'Long division, remember remainders', 'Do long division. When a remainder comes back, the digits since its first appearance repeat, so wrap them in brackets.', r'''
def fraction_to_decimal(numerator, denominator):
    if numerator == 0:
        return "0"
    sign = "-" if (numerator < 0) != (denominator < 0) else ""
    n, d = abs(numerator), abs(denominator)
    result = sign + str(n // d)
    rest = n % d
    if rest == 0:
        return result
    digits = ""
    seen = {}                                  # remainder: position in digits
    while rest != 0:
        if rest in seen:
            start = seen[rest]
            return result + "." + digits[:start] + "(" + digits[start:] + ")"
        seen[rest] = len(digits)
        rest = rest * 10
        digits = digits + str(rest // d)
        rest = rest % d
    return result + "." + digits
''', [('fraction_to_decimal(1, 2)', '0.5'), ('fraction_to_decimal(2, 1)', '2'), ('fraction_to_decimal(4, 333)', '0.(012)'), ('fraction_to_decimal(-50, 8)', '-6.25'), ('fraction_to_decimal(1, 6)', '0.1(6)')])
lc(1656, 'Design an Ordered Stream', 'design-an-ordered-stream', 'e', 'A list and a pointer', 'Store each value at its id. After each insert, return the run of filled slots starting at the pointer and move the pointer past them.', r'''
class OrderedStream:
    def __init__(self, n):
        self.values = [None] * (n + 1)
        self.ptr = 1

    def insert(self, idKey, value):
        self.values[idKey] = value
        chunk = []
        while self.ptr < len(self.values) and self.values[self.ptr] is not None:
            chunk.append(self.values[self.ptr])
            self.ptr += 1
        return chunk
''', [('(lambda s: [s.insert(3, "ccccc"), s.insert(1, "aaaaa"), s.insert(2, "bbbbb"), s.insert(5, "eeeee"), s.insert(4, "ddddd")])(OrderedStream(5))', [[], ['aaaaa'], ['bbbbb', 'ccccc'], [], ['ddddd', 'eeeee']])])
lc(1845, 'Seat Reservation Manager', 'seat-reservation-manager', 'm', 'A min heap of free seats', 'Keep the free seats in a heap so the smallest one is always on top.', r'''
import heapq


class SeatManager:
    def __init__(self, n):
        self.free = list(range(1, n + 1))      # already a valid heap

    def reserve(self):
        return heapq.heappop(self.free)

    def unreserve(self, seatNumber):
        heapq.heappush(self.free, seatNumber)
''', [('(lambda m: [m.reserve(), m.reserve(), m.unreserve(2), m.reserve(), m.reserve(), m.reserve(), m.reserve(), m.unreserve(5)])(SeatManager(5))', [1, 2, None, 2, 3, 4, 5, None])])
lc(2336, 'Smallest Number in Infinite Set', 'smallest-number-in-infinite-set', 'm', 'A counter plus a set of returned numbers', 'Numbers from next_new upwards are all present. Numbers added back below it go into a heap and a set.', r'''
import heapq


class SmallestInfiniteSet:
    def __init__(self):
        self.next_new = 1
        self.back = []                         # heap of numbers added back
        self.back_set = set()

    def popSmallest(self):
        if self.back:
            n = heapq.heappop(self.back)
            self.back_set.remove(n)
            return n
        self.next_new += 1
        return self.next_new - 1

    def addBack(self, num):
        if num < self.next_new and num not in self.back_set:
            heapq.heappush(self.back, num)
            self.back_set.add(num)
''', [('(lambda s: [s.addBack(2), s.popSmallest(), s.popSmallest(), s.popSmallest(), s.addBack(1), s.popSmallest(), s.popSmallest(), s.popSmallest()])(SmallestInfiniteSet())', [None, 1, 2, 3, None, 1, 4, 5])])
lc(1381, 'Design a Stack With Increment Operation', 'design-a-stack-with-increment-operation', 'm', 'A list with a size limit', 'push only when there is room. increment adds val to the bottom k items.', r'''
class CustomStack:
    def __init__(self, maxSize):
        self.max_size = maxSize
        self.items = []

    def push(self, x):
        if len(self.items) < self.max_size:
            self.items.append(x)

    def pop(self):
        if not self.items:
            return -1
        return self.items.pop()

    def increment(self, k, val):
        for i in range(min(k, len(self.items))):
            self.items[i] += val
''', [('(lambda s: [s.push(1), s.push(2), s.pop(), s.push(2), s.push(3), s.push(4), s.increment(5, 100), s.increment(2, 100), s.pop(), s.pop(), s.pop(), s.pop()])(CustomStack(3))', [None, None, 2, None, None, None, None, None, 103, 202, 201, -1])])
lc(1286, 'Iterator for Combination', 'iterator-for-combination', 'm', 'Make the combinations up front', 'itertools.combinations gives the combinations in order. Store them and walk through them with an index.', r'''
from itertools import combinations


class CombinationIterator:
    def __init__(self, characters, combinationLength):
        self.items = ["".join(c) for c in combinations(characters, combinationLength)]
        self.i = 0

    def next(self):
        self.i += 1
        return self.items[self.i - 1]

    def hasNext(self):
        return self.i < len(self.items)
''', [('(lambda c: [c.next(), c.hasNext(), c.next(), c.hasNext(), c.next(), c.hasNext()])(CombinationIterator("abc", 2))', ['ab', True, 'ac', True, 'bc', False])])
lc(900, 'RLE Iterator', 'rle-iterator', 'm', 'Use up counts', 'Walk the pairs (count, value). Take n from the current count, moving to the next pair when one runs out.', r'''
class RLEIterator:
    def __init__(self, encoding):
        self.encoding = encoding
        self.i = 0

    def next(self, n):
        while self.i < len(self.encoding):
            if n <= self.encoding[self.i]:
                self.encoding[self.i] -= n
                return self.encoding[self.i + 1]
            n -= self.encoding[self.i]
            self.i += 2
        return -1
''', [('(lambda r: [r.next(2), r.next(1), r.next(1), r.next(2)])(RLEIterator([3, 8, 0, 9, 2, 5]))', [8, 8, 5, -1])])
lc(1670, 'Design Front Middle Back Queue', 'design-front-middle-back-queue', 'm', 'A plain list', 'A list with insert and pop at the right index is simple and fast enough for the limits. The middle index is len // 2 for push and (len - 1) // 2 for pop.', r'''
class FrontMiddleBackQueue:
    def __init__(self):
        self.items = []

    def pushFront(self, val):
        self.items.insert(0, val)

    def pushMiddle(self, val):
        self.items.insert(len(self.items) // 2, val)

    def pushBack(self, val):
        self.items.append(val)

    def popFront(self):
        return self.items.pop(0) if self.items else -1

    def popMiddle(self):
        return self.items.pop((len(self.items) - 1) // 2) if self.items else -1

    def popBack(self):
        return self.items.pop() if self.items else -1
''', [('(lambda q: [q.pushFront(1), q.pushBack(2), q.pushMiddle(3), q.pushMiddle(4), q.popFront(), q.popMiddle(), q.popMiddle(), q.popBack(), q.popFront()])(FrontMiddleBackQueue())', [None, None, None, None, 1, 3, 4, 2, -1])])
lc(2349, 'Design a Number Container System', 'design-a-number-container-system', 'm', 'Dict plus a lazy heap per number', 'Remember the number at each index. For each number keep a heap of indexes and drop stale ones when you look at the top.', r'''
import heapq


class NumberContainers:
    def __init__(self):
        self.at = {}                           # index: number
        self.heaps = {}                        # number: heap of indexes

    def change(self, index, number):
        self.at[index] = number
        if number not in self.heaps:
            self.heaps[number] = []
        heapq.heappush(self.heaps[number], index)

    def find(self, number):
        heap = self.heaps.get(number, [])
        while heap and self.at[heap[0]] != number:
            heapq.heappop(heap)                # this index now holds another number
        return heap[0] if heap else -1
''', [('(lambda n: [n.find(10), n.change(2, 10), n.change(1, 10), n.change(3, 10), n.change(5, 10), n.find(10), n.change(1, 20), n.find(10)])(NumberContainers())', [-1, None, None, None, None, 1, None, 2])])

K.lesson('leetcode', 'LeetCode practice', leet('<p>Two problems are pure fraction arithmetic, like the Frac class in this chapter. The others ask for classes that behave like little built in types: streams, iterators, queues and heaps with a clean method interface.</p>'), kw=['LeetCode', 'fraction', 'iterator', 'design', 'heap'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'Operators and built in functions call special methods on the TYPE: a + b is type(a).__add__(a, b), len(x) is type(x).__len__(x).',
    'Return NotImplemented when you cannot handle the other operand. Python then tries the reflected method (__radd__ and friends) and finally raises TypeError.',
    '__repr__ for developers, __str__ for users, __format__ for format specs in f-strings.',
    'Comparisons: __eq__ and __lt__ plus functools.total_ordering. != comes free from __eq__.',
    'If a == b then hash(a) == hash(b). Writing __eq__ removes __hash__. Hash only fields that never change.',
    'Containers: __len__, __getitem__ (which may get a slice), __setitem__, __contains__, __iter__.',
    '__call__ makes objects callable. __iadd__ must return self. __getattr__ runs only when lookup fails, __setattr__ runs on every assignment.'],
    '1.2 moves on to extended function arguments, closures and decorators.')}
{files('Three tasks: a Money class with safe addition and ordering, a 2 by 2 Matrix with @ and ==, and a Sentence container.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'Which special method does len(x) call?', ['__length__', '__len__', '__size__', '__count__'], 1, 'Double underscore len.', 'len(x) calls type(x).__len__(x).')
K.quiz('e', 'Which method makes a + b work for your class?', ['__plus__', '__add__', '__sum__', '__concat__'], 1, 'Add.', 'The + operator calls __add__.')
K.quiz('e', 'Which method is used by print(obj) when both exist?', ['__repr__', '__str__', '__format__', '__print__'], 1, 'For users.', 'print uses str(), which calls __str__.')
K.quiz('m', 'Your __add__ cannot handle the other type. What should it do?', ['raise NotImplementedError', 'return NotImplemented', 'return None', 'return 0'], 1, 'Let the other side try.', 'Returning NotImplemented makes Python try the reflected method of the other operand.')
K.quiz('m', '2 * v works only if the Vector class defines which method?', ['__mul__', '__rmul__', '__imul__', '__lmul__'], 1, 'The int is on the left.', 'int.__mul__ returns NotImplemented, so Python calls v.__rmul__(2).')
K.quiz('m', 'A class has __len__ but no __bool__. When is the object False?', ['Never', 'When len is 0', 'Always', 'When len is 1'], 1, 'The fallback.', 'bool() falls back to __len__, and 0 means False.')
K.quiz('m', 'With @total_ordering, which methods must you write?', ['All six', '__eq__ and one of __lt__, __le__, __gt__, __ge__', 'Only __hash__', '__cmp__'], 1, 'Two are enough.', 'total_ordering fills in the rest from __eq__ and one ordering method.')
K.quiz('m', 'Why must __iadd__ return self?', ['For speed', 'Because x += y assigns the returned value back to x', 'It must not', 'To avoid recursion'], 1, 'Assignment.', 'x += y is x = x.__iadd__(y). Returning None would make x None.')
K.quiz('h', 'p is in a set. Then p.x is changed, and hash uses x. What does p in the_set return?', ['True', 'Usually False', 'TypeError', 'It removes p'], 1, 'Wrong bucket.', 'The set looks in the bucket for the new hash and does not find p there.')
K.quiz('h', 'When is __getattr__ called?', ['On every attribute read', 'Only when normal lookup fails', 'Only for methods', 'On assignment'], 1, 'Fallback.', '__getattribute__ runs on every read. __getattr__ is the fallback after it fails.')
K.quiz('h', 'obj.__len__ = lambda: 5 is set on one instance whose class has no __len__. What does len(obj) do?', ['Returns 5', 'Raises TypeError', 'Returns 0', 'Returns None'], 1, 'Looked up on the type.', 'Implicit special method lookup uses the class, so the instance attribute is ignored.')
K.quiz('x', 'In the style of a Stanford CS 41 exam: class A defines __eq__ returning NotImplemented, and so does class B. What is A() == B()?', ['True', 'False, by falling back to identity', 'TypeError', 'NotImplemented'], 1, 'Both give up.', 'When both sides return NotImplemented for ==, Python compares identity, and two different objects are not identical.')
K.quiz('x', 'In the style of an MIT 6.031 question: why is defining __hash__ on a mutable class that compares by value risky?', ['It is slower', 'Changing a field changes the hash, so the object gets lost inside sets and dicts', 'Python forbids it', 'It breaks __repr__'], 1, 'Hash must stay fixed while stored.', 'A set files an object by its hash at insertion time. A changed hash points to the wrong place.')

K.calc('e', 'Vector(3, 4) + Vector(1, 2): what is the x part of the result?', '4', 'Add the x parts.', ['self.x = 3, other.x = 1.', '__add__ returns Vector(3 + 1, 4 + 2).', eq('4')], check=4)
K.calc('e', 'abs(Vector(6, 8)) with &radic;(x<sup>2</sup> + y<sup>2</sup>).', '10', 'Pythagoras.', ['36 + 64 = 100.', '&radic;100.', eq('10')], check=int(math.hypot(6, 8)))
K.calc('e', 'Frac(1, 2) + Frac(1, 4): what is the bottom after reducing?', '4', '(1 &times; 4 + 1 &times; 2) / 8.', ['6/8.', 'gcd(6, 8) = 2.', eq('3/4, so the bottom is 4')], check=4)
K.calc('m', 'gcd(48, 18) with Euclid.', '6', 'Keep taking remainders.', ['48 mod 18 = 12.', '18 mod 12 = 6, 12 mod 6 = 0.', eq('6')], check=math.gcd(48, 18))
K.calc('m', 'Frac(2, 3) * Frac(9, 4): what is the top after reducing?', '3', '18/12 reduced.', ['2 &times; 9 = 18, 3 &times; 4 = 12.', 'gcd(18, 12) = 6.', eq('3/2, so the top is 3')], check=3)
K.calc('m', 'Vector(1, 2) @ Vector(3, 4) with a dot product __matmul__.', '11', 'Multiply matching parts and add.', ['1 &times; 3 = 3.', '2 &times; 4 = 8.', eq('11')], check=1 * 3 + 2 * 4)
K.calc('m', 'A Playlist has 4 songs. It has __len__ and __getitem__ but no __reversed__. How many times is __getitem__ called by list(reversed(p))?', '4', 'reversed uses __len__ and then each index from the end.', ['len is 4.', 'Indexes 3, 2, 1, 0.', eq('4 calls')], check=4)
K.calc('h', 'With @total_ordering, a class defines __eq__ and __lt__. How many comparison methods does it end up with (==, !=, &lt;, &lt;=, &gt;, &gt;=)?', '6', '2 written, 3 generated, != from object.', ['You write __eq__ and __lt__.', 'total_ordering adds __le__, __gt__ and __ge__. != comes from inverting __eq__.', eq('6')], check=6)
K.calc('h', '1/6 as a decimal is 0.1(6). How many digits come before the repeating part starts, after the point?', '1', 'Long division remainders.', ['10 / 6 = 1, remainder 4.', '40 / 6 = 6, remainder 4 again, so 6 repeats.', eq('1 digit (the 1) before the repeat')], check=1)
K.calc('x', 'In the style of a Cambridge Part IA problem: Frac(1, 2) + Frac(1, 3) + Frac(1, 6). What is the result as a whole number?', '1', 'Common bottom 6.', ['1/2 + 1/3 = 5/6.', '5/6 + 1/6 = 6/6.', eq('gcd reduces 6/6 to 1/1, so 1')], check=1)

K.assign('money', 'm', 'Money with safe addition and ordering',
         '<p>Write a class <code>Money(amount, currency)</code>. <code>a + b</code> returns a new Money when the currencies match and raises <code>ValueError</code> otherwise. <code>a == b</code> is True when amount and currency are equal. <code>a &lt; b</code> compares amounts of the same currency (use functools.total_ordering so &lt;=, &gt; and &gt;= also work). <code>repr</code> gives text like <code>Money(5, \'INR\')</code>. raises() is a test helper.</p>',
         '''
from functools import total_ordering


class Money:
    def __init__(self, amount, currency):
        self.amount = amount
        self.currency = currency

    # your code here


def raises(func, *args):
    """Test helper: the name of the exception func(*args) raises, or None."""
    try:
        func(*args)
    except Exception as err:
        return type(err).__name__
    return None
''', [('repr(Money(5, "INR") + Money(7, "INR"))', "Money(12, 'INR')"), ('raises(lambda: Money(5, "INR") + Money(5, "USD"))', 'ValueError'), ('Money(5, "INR") == Money(5, "INR")', True), ('Money(5, "INR") == Money(5, "USD")', False), ('Money(3, "INR") < Money(5, "INR")', True), ('Money(5, "INR") >= Money(5, "INR")', True), ('sorted([Money(9, "INR"), Money(2, "INR")])[0].amount', 2)],
         '''
from functools import total_ordering


@total_ordering
class Money:
    def __init__(self, amount, currency):
        self.amount = amount
        self.currency = currency

    def __repr__(self):
        return "Money(" + repr(self.amount) + ", " + repr(self.currency) + ")"

    def __add__(self, other):
        if self.currency != other.currency:
            raise ValueError("cannot add different currencies")
        return Money(self.amount + other.amount, self.currency)

    def __eq__(self, other):
        return self.amount == other.amount and self.currency == other.currency

    def __lt__(self, other):
        if self.currency != other.currency:
            raise ValueError("cannot compare different currencies")
        return self.amount < other.amount


def raises(func, *args):
    """Test helper: the name of the exception func(*args) raises, or None."""
    try:
        func(*args)
    except Exception as err:
        return type(err).__name__
    return None
''', 'Write __repr__, __add__, __eq__ and __lt__, and put @total_ordering above the class.', '<p>Refusing to add rupees to dollars is the whole point of a Money class: the rule lives in one place and can never be forgotten.</p>')
K.assign('matrix', 'm', 'A 2 by 2 matrix with @',
         '<p>Write <code>Matrix(a, b, c, d)</code> for the matrix [[a, b], [c, d]]. Support <code>m @ n</code> (matrix product), <code>m == n</code>, <code>m * k</code> and <code>k * m</code> for a number k, and a <code>det()</code> method that returns ad &minus; bc. Store the four numbers as a tuple in <code>self.cells</code>.</p>',
         '''
class Matrix:
    def __init__(self, a, b, c, d):
        self.cells = (a, b, c, d)

    # your code here
''', [('(Matrix(1, 2, 3, 4) @ Matrix(5, 6, 7, 8)).cells', [19, 22, 43, 50]), ('Matrix(1, 2, 3, 4) == Matrix(1, 2, 3, 4)', True), ('(Matrix(1, 2, 3, 4) * 2).cells', [2, 4, 6, 8]), ('(3 * Matrix(1, 0, 0, 1)).cells', [3, 0, 0, 3]), ('Matrix(1, 2, 3, 4).det()', -2)],
         '''
class Matrix:
    def __init__(self, a, b, c, d):
        self.cells = (a, b, c, d)

    def __matmul__(self, other):
        a, b, c, d = self.cells
        e, f, g, h = other.cells
        return Matrix(a * e + b * g, a * f + b * h, c * e + d * g, c * f + d * h)

    def __eq__(self, other):
        return isinstance(other, Matrix) and self.cells == other.cells

    def __mul__(self, k):
        return Matrix(*[x * k for x in self.cells])

    def __rmul__(self, k):
        return self * k

    def det(self):
        a, b, c, d = self.cells
        return a * d - b * c
''', 'Row times column: the top left of the product is a*e + b*g. __rmul__ can return self * k.', '<p>det(m @ n) equals det(m) &times; det(n). Try it: (&minus;2) &times; (&minus;2) = 4 = det of the product.</p>')
K.assign('sentence', 'e', 'A Sentence container',
         '<p>Write <code>Sentence(text)</code> that splits text into words. <code>len(s)</code> is the number of words, <code>s[i]</code> is a word, <code>"word" in s</code> ignores upper and lower case, and <code>for w in s</code> loops over the words.</p>',
         '''
class Sentence:
    def __init__(self, text):
        self.words = text.split()

    # your code here
''', [('len(Sentence("the quick brown fox"))', 4), ('Sentence("the quick brown fox")[1]', 'quick'), ('"QUICK" in Sentence("the quick brown fox")', True), ('[w.upper() for w in Sentence("a b")]', ['A', 'B']), ('"cat" in Sentence("a b")', False)],
         '''
class Sentence:
    def __init__(self, text):
        self.words = text.split()

    def __len__(self):
        return len(self.words)

    def __getitem__(self, i):
        return self.words[i]

    def __contains__(self, word):
        return word.lower() in [w.lower() for w in self.words]

    def __iter__(self):
        return iter(self.words)
''', 'Four short methods: __len__, __getitem__, __contains__ and __iter__, each using self.words.', '<p>With these four methods Sentence works everywhere a list of words would: len, indexing, in, for, list() and sorted().</p>')

K.must('How operators work', 'a + b calls type(a).__add__(a, b). Missing or NotImplemented: try type(b).__radd__(b, a), then TypeError. Lookup is on the class.')
K.must('Text', '__repr__ (developers, lists, REPL), __str__ (print), __format__ (f-string specs).')
K.must('Compare and hash', '__eq__ plus __lt__ with total_ordering. Equal objects need equal hashes. __eq__ alone makes a class unhashable.')
K.must('Containers', '__len__, __getitem__ (ints and slices), __setitem__, __contains__, __iter__. __bool__ falls back to __len__.')
K.must('Other hooks', '__call__ for callable objects, __iadd__ returns self, __getattr__ only on failed lookup, __setattr__ on every assignment.')

T = K.topic(
    slug='py-dunder', topic='py-dunder', step=(1, 'Advanced object oriented programming', 'py-a1', 'Make classes behave like built in types, then master decorators, class design, exceptions, copying, serialisation and metaclasses.', 'Advanced'),
    title='Special methods and operator overloading', short='Special methods', badge='1.1', minutes=75,
    lead='Make your own classes work with +, ==, len, in, for, print and f-strings. Learn how Python turns operators into special method calls, reflected and in place operators, comparisons and total_ordering, the hash contract, the container protocol, callable objects and attribute hooks.',
    desc='special (magic, dunder) methods, operator overloading, __add__ and __radd__, NotImplemented, unary operators, __matmul__, comparisons and functools.total_ordering, __eq__ and __hash__, __bool__, __len__, __getitem__ with slices, __setitem__, __contains__, __iter__, __call__, __repr__, __str__ and __format__, __iadd__, __getattr__ and __setattr__, a Fraction class with gcd.',
    summary='special methods, operator overloading, reflected operators, total_ordering, the hash contract, container protocol, __call__, __format__.',
    keywords=['special methods', 'magic methods', 'dunder', 'operator overloading', '__add__', '__radd__', 'NotImplemented', 'total_ordering', '__hash__', '__getitem__', '__call__', 'PCPP'],
    recap='<p>Write the special methods that match what your object really is, return NotImplemented for types you do not know, and keep __eq__ and __hash__ in step.</p>',
    added='2026-11-07', leet=leet_items())
