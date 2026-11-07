# Advanced Python 1.3: class design. Follows PCPP-32-101 block 1 (class methods, static methods, properties and
# encapsulation, abstract classes, composition), plus dataclasses, __slots__ and descriptors, checked against the
# Python 3.14 documentation of classmethod, staticmethod, property, functools.cached_property, abc, dataclasses,
# the data model sections on __slots__ and descriptors, and the Descriptor HowTo Guide.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, lc, leet, files, grow, leet_items

chapter('py-class-design')
K = Kit()

K.code('kinds', r'''
from datetime import date


class Person:
    count = 0                                  # class attribute

    def __init__(self, name, born):
        self.name = name
        self.born = born
        Person.count += 1

    def age(self, today):                      # instance method: gets self
        return today.year - self.born

    @classmethod
    def from_text(cls, text):                  # class method: gets cls
        name, born = text.split(",")
        return cls(name.strip(), int(born))    # an alternative constructor

    @staticmethod
    def is_adult(age):                         # static method: gets nothing extra
        return age >= 18


class Student(Person):
    pass


asha = Person("Asha", 1996)
ravi = Person.from_text("Ravi, 2010")
meera = Student.from_text("Meera, 2001")       # cls is Student here
today = date(2026, 11, 7)
print(asha.age(today), ravi.age(today), type(meera).__name__)
print(Person.is_adult(ravi.age(today)), Person.count)
print(type(Person.__dict__["from_text"]).__name__, type(Person.__dict__["is_adult"]).__name__)
''')

K.code('property', r'''
class Temperature:
    def __init__(self, celsius):
        self.celsius = celsius                 # goes through the setter below

    @property
    def celsius(self):                         # getter: t.celsius
        return self._celsius

    @celsius.setter
    def celsius(self, value):                  # setter: t.celsius = value
        if value < -273.15:
            raise ValueError("below absolute zero")
        self._celsius = value

    @property
    def fahrenheit(self):                      # read only, computed each time
        return self._celsius * 9 / 5 + 32


t = Temperature(25)
print(t.celsius, t.fahrenheit)
t.celsius = 100
print(t.fahrenheit, vars(t))
for bad in [-300]:
    try:
        t.celsius = bad
    except ValueError as err:
        print("ValueError:", err)
try:
    t.fahrenheit = 0
except AttributeError as err:
    print("AttributeError:", err)
''')

K.code('cached', r'''
from functools import cached_property


class Report:
    def __init__(self, numbers):
        self.numbers = numbers

    @cached_property                           # computed once, then stored on the object
    def total(self):
        print("adding up", len(self.numbers), "numbers")
        return sum(self.numbers)


r = Report(list(range(1, 101)))
print(r.total)
print(r.total)                                 # no second "adding up" line
print("total" in vars(r))                      # the answer now lives in the instance dict
del r.total                                    # forget it, the next read recomputes
print(r.total)
''')

K.code('abstract', r'''
from abc import ABC, abstractmethod
from collections.abc import Sized


class Payment(ABC):                            # cannot be made directly
    @abstractmethod
    def pay(self, amount):
        """Every payment method must say how it pays."""

    @property
    @abstractmethod
    def name(self):
        ...

    def receipt(self, amount):                 # normal methods are shared
        return f"{self.name}: paid {amount} -> {self.pay(amount)}"


class Upi(Payment):
    name = "UPI"

    def pay(self, amount):
        return "ok"


class Card(Payment):
    name = "Card"                              # forgot pay()


print(Upi().receipt(250))
for cls in [Payment, Card]:
    try:
        cls()
    except TypeError as err:
        print("TypeError:", err)


class Box:
    def __len__(self):
        return 3


print(isinstance(Box(), Sized))                # collections.abc checks for __len__
''')

K.code('dataclass', r'''
from dataclasses import dataclass, field, asdict, astuple, replace


@dataclass
class Item:
    name: str
    price: float
    qty: int = 1                               # a default

    @property
    def total(self):
        return self.price * self.qty


@dataclass
class Cart:
    owner: str
    items: list = field(default_factory=list)  # NEVER items: list = []

    def add(self, item):
        self.items.append(item)


pen = Item("pen", 10.0, 3)
print(pen, pen.total)
print(pen == Item("pen", 10.0, 3))             # __eq__ compares the fields
print(asdict(pen), astuple(pen))
print(replace(pen, qty=5))                     # a changed copy

a, b = Cart("Asha"), Cart("Ravi")
a.add(pen)
print(len(a.items), len(b.items))              # separate lists
''')

K.code('dcmore', r'''
from dataclasses import dataclass, field, FrozenInstanceError


@dataclass(frozen=True, order=True)            # read only, and comparable with < >
class Version:
    major: int
    minor: int
    patch: int = 0


print(sorted([Version(3, 14), Version(3, 9, 7), Version(3, 10, 2)]))
print(Version(3, 14) > Version(3, 9, 7), hash(Version(1, 0)) == hash(Version(1, 0)))
v = Version(3, 14)
try:
    v.major = 4
except FrozenInstanceError as err:
    print("FrozenInstanceError:", err)


@dataclass
class Rectangle:
    width: float
    height: float
    area: float = field(init=False)            # not an __init__ argument

    def __post_init__(self):                   # runs after the generated __init__
        if self.width <= 0 or self.height <= 0:
            raise ValueError("sides must be positive")
        self.area = self.width * self.height


print(Rectangle(3, 4))


@dataclass(kw_only=True, slots=True)           # keyword only arguments, and __slots__
class Settings:
    host: str = "localhost"
    port: int = 8000


print(Settings(port=9000), hasattr(Settings(), "__dict__"))
''')

K.code('slots', long=True, src=r'''
import tracemalloc


class Plain:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Slotted:
    __slots__ = ("x", "y")                     # only these attributes, no __dict__

    def __init__(self, x, y):
        self.x = x
        self.y = y


def bytes_per_object(cls, n=10_000):
    tracemalloc.start()
    objects = [cls(i, i) for i in range(n)]
    used = tracemalloc.get_traced_memory()[0]
    tracemalloc.stop()
    return used // n


print("Plain:  ", bytes_per_object(Plain), "bytes per object")
print("Slotted:", bytes_per_object(Slotted), "bytes per object")

s = Slotted(1, 2)
try:
    s.z = 3
except AttributeError as err:
    print("AttributeError:", err)
''')

K.code('descriptor', r'''
class Positive:
    """A reusable rule: the attribute must be a number above 0."""

    def __set_name__(self, owner, name):       # told the attribute name when the class is made
        self.private = "_" + name

    def __get__(self, obj, owner):
        if obj is None:
            return self
        return getattr(obj, self.private)

    def __set__(self, obj, value):
        if value <= 0:
            raise ValueError(self.private[1:] + " must be positive")
        setattr(obj, self.private, value)


class Product:
    price = Positive()                         # one rule object per attribute
    stock = Positive()

    def __init__(self, price, stock):
        self.price = price
        self.stock = stock


p = Product(99.5, 10)
print(p.price, p.stock, vars(p))
for field_name, bad in [("price", 0), ("stock", -5)]:
    try:
        setattr(p, field_name, bad)
    except ValueError as err:
        print("ValueError:", err)
''')

K.lesson('idea', 'Designing classes well', f'''
{src('Python 3.14 documentation of classmethod, staticmethod, property, functools.cached_property, abc and dataclasses, the data model sections on __slots__ and descriptors, the Descriptor HowTo Guide, and PCPP-32-101 block 1.')}
{wwh('Python gives you tools to say exactly what each part of a class is: methods that work on an object, on the class, or on neither, attributes that check their values (<b>properties</b>), classes that only describe a shape (<b>abstract classes</b>), and classes that are mostly data (<b>dataclasses</b>).',
     'A class written with only plain methods and attributes lets callers store bad values, repeats boilerplate like __init__ and __repr__, and gives no clear contract for child classes. These tools fix each of those problems with one decorator.',
     '@classmethod passes the class, @staticmethod passes nothing, @property turns attribute access into method calls, @abstractmethod blocks objects until children fill the gaps, and @dataclass writes __init__, __repr__ and __eq__ from type annotated fields.')}
{viz('pymethods')}
{run('kinds')}
''', kw=['class design', 'classmethod', 'staticmethod', 'property', 'abstract class', 'dataclass'])

K.lesson('kinds', 'Instance, class and static methods', f'''
{versus('Three kinds of method', ['', 'instance method', '@classmethod', '@staticmethod'], [
    ['First argument', 'self (the object)', 'cls (the class)', 'none'],
    ['Can read or change', 'The object and its class', 'The class only', 'Only its arguments'],
    ['Called as', 'obj.m()', 'Cls.m() or obj.m()', 'Cls.m() or obj.m()'],
    ['Typical use', 'Almost everything', 'Alternative constructors like from_text, dict.fromkeys, datetime.now', 'A helper that belongs to the topic, like is_adult'],
    ['With inheritance', 'self is the child object', 'cls is the child class', 'Nothing changes']],
    'use a class method when you need the class (above all to build objects), a static method for a helper that needs neither, and an instance method otherwise.')}
{note('Student.from_text returned a Student because the method calls cls(...), not Person(...). That is why alternative constructors should be class methods.', 'exam')}
''', kw=['instance method', 'class method', 'static method', 'alternative constructor', 'cls', 'from_text'])

K.lesson('property', 'Properties: attributes with rules', f'''
{run('property')}
{run('cached')}
{versus('Three ways to give access to data', ['', 'a public attribute', 'get_x() and set_x() methods', '@property'], [
    ['Caller writes', 't.celsius = 5', 't.set_celsius(5)', 't.celsius = 5'],
    ['Checks values', 'No', 'Yes', 'Yes'],
    ['Can add checks later without changing callers', 'No', 'No', 'Yes'],
    ['Feels like Python', 'Yes', 'No (Java style)', 'Yes']],
    'start with plain attributes. When a rule appears, turn the attribute into a property: no calling code has to change.')}
{note('Store the real value under another name (self._celsius). If the setter wrote self.celsius = value it would call itself forever and raise RecursionError.', 'warn')}
''', kw=['property', 'getter', 'setter', 'read only', 'computed attribute', 'cached_property', 'encapsulation'])

K.lesson('abc', 'Abstract base classes', f'''
{run('abstract')}
{note('An abstract base class is a contract: "every Payment can pay and has a name". Python refuses to create an object until every abstract method is filled in, so a forgotten method fails at once instead of in front of a customer. collections.abc gives ready made contracts like Sized, Iterable, Sequence and Mapping.', 'tip')}
{deep('Virtual subclasses', '<p>Payment.register(SomeClass) makes isinstance(SomeClass(), Payment) True without inheritance and without any checks. collections.abc uses __subclasshook__ instead, which is why Box counts as Sized just because it has __len__.</p>')}
''', kw=['abc', 'ABC', 'abstractmethod', 'abstract property', 'contract', 'collections.abc', 'register', 'virtual subclass'])

K.lesson('dataclass', 'Dataclasses: classes for data', f'''
{run('dataclass')}
{run('dcmore')}
{table(['Option', 'What it adds'], [
    ['@dataclass', '__init__, __repr__ and __eq__ from the annotated fields'],
    ['field(default_factory=list)', 'A new default object for every instance (a plain [] default is refused)'],
    ['frozen=True', 'Assignment raises FrozenInstanceError, and __hash__ is generated'],
    ['order=True', '&lt;, &lt;=, &gt;, &gt;= comparing the fields as a tuple, in order'],
    ['field(init=False) and __post_init__', 'Computed fields and checks after __init__'],
    ['kw_only=True', 'Every field must be passed by name'],
    ['slots=True', 'Generates __slots__ for less memory and faster access'],
    ['asdict, astuple, replace', 'Convert to a dict or tuple, or copy with changes']])}
{versus('Ways to bundle data', ['', 'tuple', 'namedtuple', 'dict', '@dataclass'], [
    ['Fields by name', 'No', 'Yes', 'Yes (keys)', 'Yes'],
    ['Can change', 'No', 'No', 'Yes', 'Yes (or frozen)'],
    ['Methods and properties', 'No', 'Some', 'No', 'Yes'],
    ['Type hints and defaults', 'No', 'Defaults only', 'No', 'Yes'],
    ['Best for', 'Small fixed groups', 'Light records', 'JSON style data', 'Most records in an app']],
    'reach for @dataclass first when a class is mostly data.')}
''', kw=['dataclass', 'field', 'default_factory', 'frozen', 'order', '__post_init__', 'asdict', 'replace', 'kw_only', 'namedtuple'])

K.lesson('slots', '__slots__ and descriptors', f'''
{run('slots')}
{note('__slots__ removes the per object __dict__, so objects are smaller and adding a misspelt attribute fails at once. In Python 3.14 a normal object already keeps its attributes compactly until you touch __dict__, so the saving is smaller than older guides say: about a third in this run. Use slots for classes with very many objects.', 'tip')}
{run('descriptor')}
{note('A <b>descriptor</b> is an object with __get__, __set__ or __delete__, stored as a class attribute. property, classmethod, staticmethod and every normal method are descriptors. Write your own when the same rule (like "must be positive") applies to many attributes in many classes.', 'exam')}
''', kw=['__slots__', 'memory', 'descriptor', '__get__', '__set__', '__set_name__', 'tracemalloc'])

K.lesson('maths', 'The maths: conversions, ordering and memory', f'''
{fxs(fx('Celsius to Fahrenheit (a computed property)', 'F = C &times; 9 / 5 + 32', '25 &deg;C is 25 &times; 1.8 + 32 = 77 &deg;F.', key=True),
     fx('The other way', 'C = (F &minus; 32) &times; 5 / 9', '212 &deg;F is 180 &times; 5 / 9 = 100 &deg;C.'),
     fx('Absolute zero', 'C &ge; &minus;273.15, so F &ge; &minus;459.67', 'The setter rejects anything colder.'),
     fx('order=True compares as tuples', '(a<sub>1</sub>, a<sub>2</sub>, ...) &lt; (b<sub>1</sub>, b<sub>2</sub>, ...) at the first position where they differ', 'Version(3, 9, 7) &lt; Version(3, 14, 0) because 9 &lt; 14, even though "9" &gt; "14" as text.', key=True),
     fx('Memory for n objects', 'total &asymp; n &times; bytes per object', '1,000,000 objects at 40 bytes less each save about 40 MB.'),
     fx('Age from a birth year (ignoring the birthday)', 'age = current year &minus; birth year', '2026 &minus; 1996 = 30.'))}
{steps('Worked example: sorting Version(3, 14), Version(3, 9, 7), Version(3, 10, 2)', [
    'As tuples: (3, 14, 0), (3, 9, 7), (3, 10, 2).',
    'All start with 3, so compare the second numbers: 14, 9, 10.',
    eq('9 &lt; 10 &lt; 14, so the order is 3.9.7, 3.10.2, 3.14.0')])}
''', kw=['Fahrenheit', 'Celsius', 'tuple ordering', 'lexicographic', 'memory estimate'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>Use @classmethod for alternative constructors, @staticmethod for helpers, and @property for computed or checked attributes.</p>',
    '<p>Write setters and read only properties, abstract base classes with @abstractmethod, and dataclasses with defaults, default_factory, frozen and order.</p>',
    '<p>Use cached_property, __post_init__, kw_only and slots, collections.abc contracts, and write descriptors with __set_name__ for rules shared by many attributes.</p>',
    '<p>Attribute lookup: data descriptors on the class (property, slots) beat the instance __dict__, which beats non data descriptors (functions, cached_property) and plain class attributes. That order explains why a property cannot be hidden by vars(obj) while cached_property can store its answer in the instance dict. dataclass builds its methods with exec at class creation.</p>')}
{grow('Use class methods, static methods and properties.',
      'Design with abstract classes and dataclasses.',
      'Explain the descriptor protocol and the attribute lookup order.')}
''', kw=['beginner', 'expert', 'data descriptor', 'non data descriptor', 'lookup order'])

lc(1146, 'Snapshot Array', 'snapshot-array', 'm', 'Per index history plus binary search', 'For each index keep a list of (snap id, value) changes. get looks for the last change at or before the snap id with bisect.', r'''
import bisect


class SnapshotArray:
    def __init__(self, length):
        self.history = [[(-1, 0)] for i in range(length)]
        self.snap_id = 0

    def set(self, index, val):
        changes = self.history[index]
        if changes[-1][0] == self.snap_id:
            changes[-1] = (self.snap_id, val)
        else:
            changes.append((self.snap_id, val))

    def snap(self):
        self.snap_id += 1
        return self.snap_id - 1

    def get(self, index, snap_id):
        changes = self.history[index]
        pos = bisect.bisect_right(changes, (snap_id, float("inf"))) - 1
        return changes[pos][1]
''', [('(lambda a: [a.set(0, 5), a.snap(), a.set(0, 6), a.get(0, 0)])(SnapshotArray(3))', [None, 0, None, 5])])
lc(981, 'Time Based Key-Value Store', 'time-based-key-value-store', 'm', 'Lists of times per key, bisect', 'Timestamps arrive in increasing order, so each key keeps a sorted list. get finds the last time not after the asked time.', r'''
import bisect


class TimeMap:
    def __init__(self):
        self.times = {}
        self.values = {}

    def set(self, key, value, timestamp):
        self.times.setdefault(key, []).append(timestamp)
        self.values.setdefault(key, []).append(value)

    def get(self, key, timestamp):
        times = self.times.get(key, [])
        pos = bisect.bisect_right(times, timestamp) - 1
        return self.values[key][pos] if pos >= 0 else ""
''', [('(lambda t: [t.set("foo", "bar", 1), t.get("foo", 1), t.get("foo", 3), t.set("foo", "bar2", 4), t.get("foo", 4), t.get("foo", 5), t.get("foo", 0)])(TimeMap())', [None, 'bar', 'bar', None, 'bar2', 'bar2', ''])])
lc(1797, 'Design Authentication Manager', 'design-authentication-manager', 'm', 'A dict of expiry times', 'Store when each token expires. renew only works while the token is alive. Count the tokens that expire after the current time.', r'''
class AuthenticationManager:
    def __init__(self, timeToLive):
        self.ttl = timeToLive
        self.expires = {}

    def generate(self, tokenId, currentTime):
        self.expires[tokenId] = currentTime + self.ttl

    def renew(self, tokenId, currentTime):
        if self.expires.get(tokenId, 0) > currentTime:
            self.expires[tokenId] = currentTime + self.ttl

    def countUnexpiredTokens(self, currentTime):
        return sum(1 for t in self.expires.values() if t > currentTime)
''', [('(lambda a: [a.renew("aaa", 1), a.generate("aaa", 2), a.countUnexpiredTokens(6), a.generate("bbb", 7), a.renew("aaa", 8), a.renew("bbb", 10), a.countUnexpiredTokens(15)])(AuthenticationManager(5))', [None, None, 1, None, None, None, 0])])
lc(1500, 'Design a File Sharing System', 'design-a-file-sharing-system', 'm', 'Reuse the smallest free id with a heap', 'Hand out ids from a heap of freed ids first, then new ids. Each user has a set of chunks.', r'''
import heapq


class FileSharing:
    def __init__(self, m):
        self.free_ids = []
        self.next_id = 1
        self.owned = {}                        # user id: set of chunks

    def join(self, ownedChunks):
        if self.free_ids:
            user = heapq.heappop(self.free_ids)
        else:
            user = self.next_id
            self.next_id += 1
        self.owned[user] = set(ownedChunks)
        return user

    def leave(self, userID):
        del self.owned[userID]
        heapq.heappush(self.free_ids, userID)

    def request(self, userID, chunkID):
        holders = sorted(u for u, chunks in self.owned.items() if chunkID in chunks)
        if holders:
            self.owned[userID].add(chunkID)
        return holders
''', [('(lambda f: [f.join([1, 2]), f.join([2, 3]), f.join([4]), f.request(1, 3), f.request(2, 2), f.leave(1), f.request(2, 1), f.leave(2), f.join([])])(FileSharing(4))', [1, 2, 3, [2], [1, 2], None, [], None, 1])])
lc(1244, 'Design A Leaderboard', 'design-a-leaderboard', 'm', 'A dict of scores', 'addScore adds to a player, top sorts the scores and adds the K biggest, reset sets a player back to 0.', r'''
class Leaderboard:
    def __init__(self):
        self.scores = {}

    def addScore(self, playerId, score):
        self.scores[playerId] = self.scores.get(playerId, 0) + score

    def top(self, K):
        return sum(sorted(self.scores.values(), reverse=True)[:K])

    def reset(self, playerId):
        self.scores[playerId] = 0
''', [('(lambda b: [b.addScore(1, 73), b.addScore(2, 56), b.addScore(3, 39), b.addScore(4, 51), b.addScore(5, 4), b.top(1), b.reset(1), b.reset(2), b.addScore(2, 51), b.top(3)])(Leaderboard())', [None, None, None, None, None, 73, None, None, None, 141])])
lc(2526, 'Find Consecutive Integers from a Data Stream', 'find-consecutive-integers-from-a-data-stream', 'm', 'Count the current run', 'Keep how many values in a row have equalled value. consec returns whether that run has reached k.', r'''
class DataStream:
    def __init__(self, value, k):
        self.value = value
        self.k = k
        self.run = 0

    def consec(self, num):
        if num == self.value:
            self.run += 1
        else:
            self.run = 0
        return self.run >= self.k
''', [('(lambda d: [d.consec(4), d.consec(4), d.consec(4), d.consec(3)])(DataStream(4, 3))', [False, False, True, False])])
lc(2296, 'Design a Text Editor', 'design-a-text-editor', 'h', 'Two stacks around the cursor', 'Keep the text left of the cursor and the text right of it (reversed) as two lists. Every operation moves characters between them.', r'''
class TextEditor:
    def __init__(self):
        self.left = []
        self.right = []                        # reversed: right[-1] is just after the cursor

    def addText(self, text):
        self.left.extend(text)

    def deleteText(self, k):
        count = min(k, len(self.left))
        for i in range(count):
            self.left.pop()
        return count

    def cursorLeft(self, k):
        for i in range(min(k, len(self.left))):
            self.right.append(self.left.pop())
        return "".join(self.left[-10:])

    def cursorRight(self, k):
        for i in range(min(k, len(self.right))):
            self.left.append(self.right.pop())
        return "".join(self.left[-10:])
''', [('(lambda e: [e.addText("leetcode"), e.deleteText(4), e.addText("practice"), e.cursorRight(3), e.cursorLeft(8), e.deleteText(10), e.cursorLeft(2), e.cursorRight(6)])(TextEditor())', [None, 4, None, 'etpractice', 'leet', 4, '', 'practi'])])
lc(1825, 'Finding MK Average', 'finding-mk-average', 'h', 'Keep the last m values, sort when asked', 'A deque keeps the last m values. To answer, sort them, drop k from each end and average the middle. Simple, and fine for small m.', r'''
from collections import deque


class MKAverage:
    def __init__(self, m, k):
        self.m = m
        self.k = k
        self.last = deque()

    def addElement(self, num):
        self.last.append(num)
        if len(self.last) > self.m:
            self.last.popleft()

    def calculateMKAverage(self):
        if len(self.last) < self.m:
            return -1
        middle = sorted(self.last)[self.k:self.m - self.k]
        return sum(middle) // len(middle)
''', [('(lambda a: [a.addElement(3), a.addElement(1), a.calculateMKAverage(), a.addElement(10), a.calculateMKAverage(), a.addElement(5), a.addElement(5), a.addElement(5), a.calculateMKAverage()])(MKAverage(3, 1))', [None, None, -1, None, 3, None, None, None, 5])])
lc(2034, 'Stock Price Fluctuation', 'stock-price-fluctuation', 'm', 'Dict plus two lazy heaps', 'Store the price at each time. Push into a max heap and a min heap, and skip heap tops whose price was later corrected.', r'''
import heapq


class StockPrice:
    def __init__(self):
        self.price_at = {}
        self.latest = 0
        self.low = []
        self.high = []

    def update(self, timestamp, price):
        self.price_at[timestamp] = price
        self.latest = max(self.latest, timestamp)
        heapq.heappush(self.low, (price, timestamp))
        heapq.heappush(self.high, (-price, timestamp))

    def current(self):
        return self.price_at[self.latest]

    def maximum(self):
        while -self.high[0][0] != self.price_at[self.high[0][1]]:
            heapq.heappop(self.high)
        return -self.high[0][0]

    def minimum(self):
        while self.low[0][0] != self.price_at[self.low[0][1]]:
            heapq.heappop(self.low)
        return self.low[0][0]
''', [('(lambda s: [s.update(1, 10), s.update(2, 5), s.current(), s.maximum(), s.update(1, 3), s.maximum(), s.update(4, 2), s.minimum()])(StockPrice())', [None, None, 5, 10, None, 5, None, 2])])
lc(1600, 'Throne Inheritance', 'throne-inheritance', 'm', 'A family tree and a preorder walk', 'Keep each person\'s children in birth order and a set of the dead. The order of succession is a preorder walk that skips the dead.', r'''
class ThroneInheritance:
    def __init__(self, kingName):
        self.king = kingName
        self.children = {kingName: []}
        self.dead = set()

    def birth(self, parentName, childName):
        self.children[parentName].append(childName)
        self.children[childName] = []

    def death(self, name):
        self.dead.add(name)

    def getInheritanceOrder(self):
        order = []
        stack = [self.king]
        while stack:
            person = stack.pop()
            if person not in self.dead:
                order.append(person)
            stack.extend(reversed(self.children[person]))
        return order
''', [('(lambda t: [t.birth("king", "andy"), t.birth("king", "bob"), t.birth("andy", "matthew"), t.death("bob"), t.getInheritanceOrder()])(ThroneInheritance("king"))', [None, None, None, None, ['king', 'andy', 'matthew']])])

K.lesson('leetcode', 'LeetCode practice', leet('<p>Each problem is a small class design exercise: choose the attributes in __init__ so that every method stays simple and fast. Several of them pair a dict with a heap or with bisect, a pattern you will meet again in Advanced 4.2.</p>'), kw=['LeetCode', 'class design', 'bisect', 'heap', 'snapshot', 'text editor'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'Instance methods get self, @classmethod gets cls (use it for alternative constructors), @staticmethod gets nothing.',
    '@property turns reads and writes into method calls: computed values, checks in a setter, read only attributes. Store the real value under _name.',
    '@cached_property computes once and stores the answer in the instance dict.',
    'Abstract base classes (ABC with @abstractmethod) are contracts: objects cannot be made until every abstract method exists.',
    '@dataclass writes __init__, __repr__ and __eq__. Use field(default_factory=list), frozen, order, __post_init__, kw_only and slots as needed.',
    '__slots__ removes the instance dict to save memory and stop new attributes.',
    'Descriptors (__get__, __set__, __set_name__) are the machinery behind property and methods, and let one rule serve many attributes.'],
    '1.4 covers exceptions in depth, copying objects, and saving objects with pickle and shelve.')}
{files('Three tasks: a BankAccount with a checked balance property and a from_text class method, a Shape abstract class with two children, and an Order dataclass.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'What is the first argument of a @classmethod?', ['self', 'cls, the class', 'nothing', 'the module'], 1, 'Class method.', 'Python passes the class, by convention named cls.')
K.quiz('e', 'What does @property let you write?', ['obj.x() instead of obj.x', 'obj.x instead of obj.get_x()', 'Only private attributes', 'Static attributes'], 1, 'Attribute syntax.', 'A property runs a method when you read obj.x.')
K.quiz('e', 'Which methods does @dataclass write by default?', ['__init__, __repr__, __eq__', 'Only __init__', '__hash__ and __lt__', 'None'], 0, 'The usual three.', 'order=True and frozen=True add more.')
K.quiz('m', 'Student inherits from Person. Student.from_text(...) is a class method that returns cls(...). What type is the result?', ['Person', 'Student', 'type', 'object'], 1, 'cls is the class it was called on.', 'cls is Student, so cls(...) makes a Student.')
K.quiz('m', 'A property has a getter but no setter. What does obj.x = 5 do?', ['Stores 5', 'Raises AttributeError', 'Calls the getter', 'Nothing'], 1, 'Read only.', 'Python says the property has no setter.')
K.quiz('m', 'Why is items: list = [] refused in a dataclass?', ['Lists are not allowed', 'It would share one list between all objects, so dataclass raises ValueError', 'It is a syntax error', 'It works fine'], 1, 'Mutable default.', 'Use field(default_factory=list).')
K.quiz('m', 'An ABC has one @abstractmethod. A child class does not write it. What happens when you call Child()?', ['It works', 'TypeError: Can\'t instantiate abstract class', 'The method returns None', 'NotImplementedError when called'], 1, 'Blocked at creation.', 'Abstract classes refuse to create objects with missing methods.')
K.quiz('m', 'What does frozen=True do to a dataclass?', ['Makes it faster', 'Assigning a field raises FrozenInstanceError, and the class becomes hashable', 'Removes __init__', 'Stores it on disk'], 1, 'Read only.', 'Frozen dataclasses are immutable and hashable.')
K.quiz('h', 'In a setter for celsius, the code writes self.celsius = value. What happens?', ['It stores value', 'The setter calls itself forever: RecursionError', 'AttributeError', 'Nothing'], 1, 'Same name.', 'Assigning to celsius calls the setter again. Store under _celsius.')
K.quiz('h', 'What does __slots__ = ("x", "y") do?', ['Makes x and y class attributes', 'Removes the instance __dict__, so only x and y can be set', 'Makes them private', 'Freezes the object'], 1, 'Fixed attributes.', 'Setting any other attribute raises AttributeError.')
K.quiz('h', 'Why can cached_property store its answer in the instance dict while property cannot be hidden that way?', ['cached_property is faster', 'property is a data descriptor, which wins over the instance dict, while cached_property is a non data descriptor', 'property has no __get__', 'They are the same'], 1, 'Lookup order.', 'Data descriptors (with __set__) beat the instance dict. Non data descriptors lose to it.')
K.quiz('x', 'In the style of a CMU 17-214 exam: a class needs objects built from a JSON string, and child classes must build child objects. Which design is best?', ['A module level function make_from_json', 'A @staticmethod from_json that calls the parent class name', 'A @classmethod from_json that returns cls(...)', 'Parse inside __init__'], 2, 'Inheritance aware constructor.', 'Only cls follows the class the method was called on.')
K.quiz('x', 'In the style of an MIT 6.031 exam: @dataclass(order=True) class V with fields major, minor. Which is True?', ['V(3, 9) > V(3, 10)', 'V(3, 10) > V(3, 9)', 'V(2, 99) > V(3, 0)', 'They cannot be compared'], 1, 'Tuple order.', 'Fields are compared as tuples: (3, 10) &gt; (3, 9).')

K.calc('e', 'Temperature(25).fahrenheit with F = C &times; 9 / 5 + 32.', '77', '25 &times; 1.8 + 32.', ['25 &times; 9 = 225.', '225 / 5 = 45.', eq('45 + 32 = 77')], check=25 * 9 / 5 + 32)
K.calc('e', '212 &deg;F in Celsius with C = (F &minus; 32) &times; 5 / 9.', '100', 'Subtract 32 first.', ['212 &minus; 32 = 180.', '180 &times; 5 = 900.', eq('900 / 9 = 100')], check=(212 - 32) * 5 / 9)
K.calc('e', 'Person.count starts at 0. Three people are made, one with from_text. What is Person.count?', '3', 'from_text calls cls(...), which runs __init__.', ['Each __init__ adds 1.', 'from_text still runs __init__.', eq('3')], check=3)
K.calc('m', 'Item("pen", 10.0, 3).total, where total is price &times; qty.', '30', '10 &times; 3.', ['price = 10.0.', 'qty = 3.', eq('30')], check=30)
K.calc('m', 'Rectangle(3, 4) with area computed in __post_init__.', '12', 'width &times; height.', ['__init__ sets width and height.', '__post_init__ sets area = 3 &times; 4.', eq('12')], check=12)
K.calc('m', 'Absolute zero, &minus;273.15 &deg;C, in Fahrenheit (2 decimal places).', '-459.67', 'Use the formula.', ['&minus;273.15 &times; 1.8 = &minus;491.67.', 'Add 32.', eq('&minus;459.67')], check=round(-273.15 * 9 / 5 + 32, 2))
K.calc('m', 'Report(list(range(1, 101))).total is read 3 times with cached_property. How many times is the sum computed?', '1', 'Cached in the instance dict.', ['The first read computes 5050 and stores it.', 'Later reads find it in vars(r).', eq('1')], check=1)
K.calc('h', 'Slots save about 40 bytes per object. How many MB (10<sup>6</sup> bytes) do 2,500,000 objects save?', '100', 'n &times; bytes.', ['2,500,000 &times; 40 = 100,000,000 bytes.', 'Divide by 10<sup>6</sup>.', eq('100 MB')], check=2_500_000 * 40 // 10 ** 6)
K.calc('h', 'With order=True, how many of these are True: V(1, 2) &lt; V(1, 3), V(2, 0) &lt; V(1, 9), V(1, 2) &lt;= V(1, 2)?', '2', 'Tuple order.', ['(1, 2) &lt; (1, 3): True.', '(2, 0) &lt; (1, 9): False. (1, 2) &lt;= (1, 2): True.', eq('2')], check=sum([(1, 2) < (1, 3), (2, 0) < (1, 9), (1, 2) <= (1, 2)]))
K.calc('x', 'In the style of an Imperial College exam: at which temperature are the Celsius and Fahrenheit numbers equal? Solve C = 9C / 5 + 32.', '-40', 'Collect the C terms.', ['C &minus; 9C / 5 = 32, so &minus;4C / 5 = 32.', 'C = 32 &times; (&minus;5 / 4).', eq('&minus;40')], check=-40)

K.assign('account', 'm', 'A bank account with a checked balance',
         '<p>Write <code>Account(owner, balance=0)</code>. Make <code>balance</code> a property whose setter raises <code>ValueError</code> for a negative value. Add a class method <code>from_text("Asha:250")</code> that returns an account, and a static method <code>valid_owner(name)</code> that returns True when name is not empty and only letters.</p>',
         '''
class Account:
    def __init__(self, owner, balance=0):
        self.owner = owner
        self.balance = balance

    # your code here


def raises(func, *args):
    try:
        func(*args)
    except Exception as err:
        return type(err).__name__
    return None
''', [('Account.from_text("Asha:250").balance', 250), ('Account.from_text("Asha:250").owner', 'Asha'), ('raises(Account, "Ravi", -5)', 'ValueError'), ('(lambda a: (raises(setattr, a, "balance", -1), a.balance))(Account("Meera", 10))', ['ValueError', 10]), ('(Account.valid_owner("Asha"), Account.valid_owner(""), Account.valid_owner("A1"))', [True, False, False])],
         '''
class Account:
    def __init__(self, owner, balance=0):
        self.owner = owner
        self.balance = balance

    @property
    def balance(self):
        return self._balance

    @balance.setter
    def balance(self, value):
        if value < 0:
            raise ValueError("balance cannot be negative")
        self._balance = value

    @classmethod
    def from_text(cls, text):
        owner, amount = text.split(":")
        return cls(owner, int(amount))

    @staticmethod
    def valid_owner(name):
        return name.isalpha()


def raises(func, *args):
    try:
        func(*args)
    except Exception as err:
        return type(err).__name__
    return None
''', 'Property with @balance.setter storing self._balance. from_text splits on ":" and returns cls(...). valid_owner can use str.isalpha (which is False for "").', '<p>Because __init__ assigns self.balance, the setter checks the starting balance too. One rule, enforced everywhere.</p>')
K.assign('shapes', 'e', 'An abstract Shape',
         '<p>Shape is an abstract class with an abstract method <code>area()</code> and a normal method <code>describe()</code>. Write <code>Circle(r)</code> (use 3.14 for pi) and <code>Square(side)</code> as children. raises() is a test helper.</p>',
         '''
from abc import ABC, abstractmethod


class Shape(ABC):
    @abstractmethod
    def area(self):
        pass

    def describe(self):
        return type(self).__name__ + " " + str(round(self.area(), 2))


class Circle:
    pass


class Square:
    pass


def raises(func, *args):
    try:
        func(*args)
    except Exception as err:
        return type(err).__name__
    return None
''', [('Circle(1).describe()', 'Circle 3.14'), ('Square(3).area()', 9), ('raises(Shape)', 'TypeError'), ('isinstance(Square(1), Shape)', True)],
         '''
from abc import ABC, abstractmethod


class Shape(ABC):
    @abstractmethod
    def area(self):
        pass

    def describe(self):
        return type(self).__name__ + " " + str(round(self.area(), 2))


class Circle(Shape):
    def __init__(self, r):
        self.r = r

    def area(self):
        return 3.14 * self.r * self.r


class Square(Shape):
    def __init__(self, side):
        self.side = side

    def area(self):
        return self.side * self.side


def raises(func, *args):
    try:
        func(*args)
    except Exception as err:
        return type(err).__name__
    return None
''', 'Inherit from Shape and write __init__ and area in each child.', '<p>Shape() raising TypeError is the contract at work: nobody can use a shape that cannot compute its area.</p>')
K.assign('order', 'm', 'An Order dataclass',
         '<p>Write a dataclass <code>Order</code> with fields <code>customer</code> (str), <code>items</code> (a list, default empty, never shared) and <code>discount</code> (float, default 0.0). Add a method <code>add(name, price)</code> that appends (name, price), and a property <code>total</code> that returns the sum of prices times (1 &minus; discount), rounded to 2 places. In <code>__post_init__</code>, raise <code>ValueError</code> if discount is not between 0 and 1.</p>',
         '''
from dataclasses import dataclass, field


class Order:
    pass


def raises(func, *args):
    try:
        func(*args)
    except Exception as err:
        return type(err).__name__
    return None
''', [('(lambda o: (o.add("pen", 10), o.add("book", 90), o.total))(Order("Asha", discount=0.1))[2]', 90.0), ('(lambda a, b: (a.add("x", 1), len(b.items))[1])(Order("A"), Order("B"))', 0), ('raises(Order, "C", [], 1.5)', 'ValueError'), ('repr(Order("Ravi"))', "Order(customer='Ravi', items=[], discount=0.0)")],
         '''
from dataclasses import dataclass, field


@dataclass
class Order:
    customer: str
    items: list = field(default_factory=list)
    discount: float = 0.0

    def __post_init__(self):
        if not 0 <= self.discount <= 1:
            raise ValueError("discount must be between 0 and 1")

    def add(self, name, price):
        self.items.append((name, price))

    @property
    def total(self):
        subtotal = 0
        for name, price in self.items:
            subtotal = subtotal + price
        return round(subtotal * (1 - self.discount), 2)


def raises(func, *args):
    try:
        func(*args)
    except Exception as err:
        return type(err).__name__
    return None
''', 'Use @dataclass with field(default_factory=list). Check the discount in __post_init__. total loops over the (name, price) pairs.', '<p>The dataclass writes __init__, __repr__ and __eq__, so your code is only the rules: the discount check and the total.</p>')

K.must('Method kinds', 'Instance method gets self. @classmethod gets cls (alternative constructors, returns cls(...)). @staticmethod gets nothing.')
K.must('Properties', '@property getter, @x.setter with checks, no setter means read only. Store the value as self._x. @cached_property computes once.')
K.must('Abstract classes', 'class C(ABC) with @abstractmethod: C() and incomplete children raise TypeError. collections.abc offers ready contracts.')
K.must('Dataclasses', '@dataclass writes __init__, __repr__, __eq__. field(default_factory=list), frozen, order, __post_init__, kw_only, slots, asdict, replace.')
K.must('Slots and descriptors', '__slots__ removes __dict__. Descriptors have __get__ and __set__. Data descriptors beat the instance dict.')

T = K.topic(
    slug='py-class-design', topic='py-class-design', step=(1, 'Advanced object oriented programming', 'py-a1', 'Make classes behave like built in types, then master decorators, class design, exceptions, copying, serialisation and metaclasses.', 'Advanced'),
    title='Class design: methods, properties, abstract classes and dataclasses', short='Class design', badge='1.3', minutes=80,
    lead='Say exactly what each part of a class is. Learn instance, class and static methods, alternative constructors, properties with setters and read only values, cached_property, abstract base classes, dataclasses with all their options, __slots__ and descriptors.',
    desc='instance methods, class methods and alternative constructors, static methods, property getters and setters, read only and computed properties, functools.cached_property, abc.ABC and abstractmethod, abstract properties, collections.abc, dataclasses with field, default_factory, frozen, order, __post_init__, kw_only, slots, asdict and replace, __slots__ and memory, descriptors with __set_name__, the attribute lookup order.',
    summary='class and static methods, properties, cached_property, ABCs, dataclasses, __slots__, descriptors.',
    keywords=['classmethod', 'staticmethod', 'property', 'setter', 'cached_property', 'abc', 'abstractmethod', 'dataclass', 'frozen', '__slots__', 'descriptor', 'PCPP'],
    recap='<p>Pick the method kind by what it needs, guard data with properties, write contracts with ABCs, and let dataclasses write the boilerplate.</p>',
    added='2026-11-07', leet=leet_items())
