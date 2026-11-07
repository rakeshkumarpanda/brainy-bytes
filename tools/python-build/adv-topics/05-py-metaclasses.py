# Advanced Python 1.5: metaprogramming. Follows PCPP-32-101 block 1 (metaclasses: classes as objects, type() with
# three arguments, the metaclass keyword, __new__ and __call__ in a metaclass, class attributes such as __name__,
# __class__, __bases__ and __dict__), checked against the Python 3.14 data model chapter 3.3.3 "Customizing class
# creation" (__init_subclass__, __set_name__, metaclasses, __prepare__, the order of class creation), the built in
# functions type, getattr, setattr, hasattr, vars and dir, the inspect module, PEP 3115 (metaclasses in Python 3),
# PEP 3129 (class decorators) and PEP 487 (simpler customisation of class creation).
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, lc, leet, files, grow, leet_items

chapter('py-metaclasses')
K = Kit()

K.code('objects', r'''
class Dog:
    sound = "woof"

    def speak(self):
        return self.sound


rex = Dog()
print(type(rex).__name__, type(Dog).__name__, type(type).__name__)
print(isinstance(Dog, type), isinstance(rex, object), isinstance(type, object))

animals = {"dog": Dog}                         # a class can live in a dict
make = animals["dog"]
print(make().speak())


def build(cls, times):                         # and can be passed to a function
    return [cls() for i in range(times)]


print(len(build(Dog, 3)), Dog.__name__, Dog.__bases__)
print(sorted(k for k in vars(Dog) if not k.startswith("__")))
''')

K.code('maketype', r'''
def init(self, name):
    self.name = name


def speak(self):
    return self.name + " says " + self.sound


# type(name, bases, namespace) builds a class without a class statement
Cat = type("Cat", (object,), {"sound": "meow", "__init__": init, "speak": speak})
print(Cat("Tom").speak(), Cat.__name__, Cat.__bases__)

Kitten = type("Kitten", (Cat,), {"sound": "mew"})   # inheritance works as usual
print(Kitten("Kit").speak(), [c.__name__ for c in Kitten.__mro__])


def make_record(name, fields):                 # build classes from data
    def __init__(self, *values):
        for field_name, value in zip(fields, values):
            setattr(self, field_name, value)

    def __repr__(self):
        parts = []
        for field_name in fields:
            parts.append(field_name + "=" + repr(getattr(self, field_name)))
        return name + "(" + ", ".join(parts) + ")"

    return type(name, (), {"__init__": __init__, "__repr__": __repr__, "fields": fields})


Point = make_record("Point", ["x", "y"])
print(Point(3, 4), Point.fields)
''')

K.code('classbody', r'''
print("before the class")


class Shop:
    print("  the class body runs now, only once")
    tax = 0.18
    price = 100
    total = price * (1 + tax)                  # the body is normal code
    snapshot = dict(locals())                  # the namespace filled so far


print("after the class:", Shop.total)
print([k for k in Shop.snapshot if not k.startswith("__")])
print(Shop.__qualname__, Shop.__module__)
''')

K.code('introspect', r'''
import inspect


class Account:
    bank = "City Bank"

    def __init__(self, owner, balance=0):
        self.owner = owner
        self.balance = balance

    def deposit(self, amount, note=""):
        self.balance += amount


acc = Account("Asha", 100)
print(getattr(acc, "owner"), getattr(acc, "pin", "no pin"))
print(hasattr(acc, "deposit"), callable(acc.deposit), callable(acc.owner))
setattr(acc, "branch", "Pune")                 # add an attribute by its name
print(vars(acc))
action = "deposit"                             # a method chosen while the program runs
getattr(acc, action)(50)
print(acc.balance)
print([name for name in dir(acc) if not name.startswith("_")])
print(inspect.signature(Account.deposit))
print(acc.__class__.__name__, Account.__dict__["bank"], [c.__name__ for c in Account.__mro__])
''')

K.code('initsub', r'''
class Plugin:
    registry = {}

    def __init_subclass__(cls, name=None, **kwargs):
        super().__init_subclass__(**kwargs)
        key = name or cls.__name__.lower()
        Plugin.registry[key] = cls             # every child registers itself


class CsvExport(Plugin, name="csv"):
    def run(self, rows):
        lines = []
        for row in rows:
            lines.append(",".join(str(x) for x in row))
        return "\n".join(lines)


class JsonExport(Plugin, name="json"):
    def run(self, rows):
        return str(rows)


class Pdf(Plugin):                             # no name given, so the key is "pdf"
    def run(self, rows):
        return "PDF with " + str(len(rows)) + " rows"


print(sorted(Plugin.registry))
chosen = Plugin.registry["csv"]()              # pick a class by a string
print(chosen.run([[1, 2], [3, 4]]))
print(Plugin.registry["pdf"]().run([[1], [2], [3]]))
''')

K.code('classdeco', r'''
def auto_repr(cls):
    """Add a __repr__ that lists the attributes set in __init__."""
    def __repr__(self):
        parts = []
        for key, value in vars(self).items():
            parts.append(key + "=" + repr(value))
        return cls.__name__ + "(" + ", ".join(parts) + ")"

    cls.__repr__ = __repr__
    return cls                                 # hand the same class back


ROUTES = {}


def route(path):                               # a decorator factory for classes
    def register(cls):
        ROUTES[path] = cls.__name__
        return cls
    return register


@route("/books")
@auto_repr
class Book:
    def __init__(self, title, pages):
        self.title = title
        self.pages = pages


print(Book("Python", 320))
print(ROUTES)
''')

K.code('metaclass', r'''
class CheckMeta(type):
    def __new__(mcs, name, bases, namespace):
        public = sorted(k for k in namespace if not k.startswith("__"))
        print("building class", name, "with", public)
        if bases and "run" not in namespace:   # every child must have run()
            raise TypeError(name + " must define run()")
        namespace["kind"] = name.lower()       # add an attribute to every class
        return super().__new__(mcs, name, bases, namespace)


class Job(metaclass=CheckMeta):
    pass


class Backup(Job):                             # the metaclass is inherited
    def run(self):
        return "backing up"


print(Backup().run(), Backup.kind, type(Backup).__name__)
try:
    class Broken(Job):
        def start(self):
            pass
except TypeError as err:
    print("TypeError:", err)
''')

K.code('singleton', r'''
class Singleton(type):
    instances = {}

    def __call__(cls, *args, **kwargs):        # runs on Config(...)
        if cls not in Singleton.instances:
            print("creating", cls.__name__)
            Singleton.instances[cls] = super().__call__(*args, **kwargs)
        return Singleton.instances[cls]


class Config(metaclass=Singleton):
    def __init__(self, mode="dev"):
        self.mode = mode


a = Config("prod")
b = Config("test")                             # the same object comes back
print(a is b, a.mode, b.mode)
''')

K.code('stdmeta', r'''
from abc import ABC
from enum import Enum


class Shape(ABC):
    pass


class Colour(Enum):
    RED = 1
    GREEN = 2


print(type(Shape).__name__, type(Colour).__name__, type(int).__name__)
print(len(Colour), Colour["RED"], [c.name for c in Colour])   # len, [] and for on the CLASS
print(issubclass(type(Shape), type), type.__bases__)


class MetaA(type):
    pass


class MetaB(type):
    pass


class A(metaclass=MetaA):
    pass


class B(metaclass=MetaB):
    pass


try:
    class C(A, B):                             # two unrelated metaclasses
        pass
except TypeError as err:
    print("TypeError:", str(err).split(":")[0])
''')

K.code('order', r'''
def decorate(cls):
    print("7. the class decorator gets the finished class")
    return cls


class Meta(type):
    @classmethod
    def __prepare__(mcs, name, bases):
        print("1. Meta.__prepare__ makes the namespace dict")
        return {}

    def __new__(mcs, name, bases, ns):
        print("3. Meta.__new__ starts building the class")
        return super().__new__(mcs, name, bases, ns)

    def __init__(cls, name, bases, ns):
        print("6. Meta.__init__ finishes it")
        super().__init__(name, bases, ns)

    def __call__(cls, *args):
        print("8. Meta.__call__ runs when you call the class")
        return super().__call__(*args)


class Base:
    def __init_subclass__(cls):
        print("5. Base.__init_subclass__ hears about the new child")


class Field:
    def __set_name__(self, owner, name):
        print("4. __set_name__ tells a descriptor its name:", name)


@decorate
class Dog(Base, metaclass=Meta):
    print("2. the class body runs")
    size = Field()

    def __init__(self, name):
        print("9. Dog.__init__ fills the new object")
        self.name = name


print("--- now make an object ---")
rex = Dog("Rex")
print(rex.name, type(rex).__name__, type(Dog).__name__)
''')

K.lesson('idea', 'Classes are objects too', f'''
{src('Python 3.14 data model chapter 3.3.3 (customizing class creation), the documentation of type, getattr, setattr, vars, dir and inspect, PEP 3115, PEP 3129, PEP 487, and PCPP-32-101 block 1.')}
{wwh('<b>Metaprogramming</b> means writing code that makes or changes other code, mostly classes, while the program runs. In Python a class is an ordinary object. You can store it in a variable, pass it to a function, make one with <b>type()</b>, look inside it, and run your own code at the moment it is created. A <b>metaclass</b> is the class of a class: the thing that builds class objects.',
     'Some rules apply to many classes at once: "every plugin must register itself", "every model needs a table name", "every command must have a run method". Writing that rule by hand in each class repeats code and is easy to forget. Metaprogramming puts the rule in one place and applies it to every class automatically.',
     'When Python runs a class statement it collects the class body into a dict and then calls the metaclass (normally <b>type</b>) with the name, the base classes and that dict. Hooks let you join in: <b>__init_subclass__</b> on a parent class, a <b>class decorator</b> after the class is built, or a custom metaclass that controls the whole process.')}
{viz('pymeta')}
{run('objects')}
{note('type has two jobs. With one argument, type(x) tells you the class of x. With three arguments, type(name, bases, namespace) builds a new class. And type(type) is type: type is its own class, which is where the chain ends.', 'exam')}
''', kw=['metaprogramming', 'metaclass', 'type', 'class object', 'first class', '__bases__', 'vars'])

K.lesson('dynamic', 'Building classes with type()', f'''
{run('maketype')}
{note('A class statement and a type() call give exactly the same kind of class. Python itself turns every class statement into a call like type("Cat", (object,), namespace). You only need type() directly when the name or the fields are known only while the program runs, for example from a config file.', 'tip')}
{run('classbody')}
{note('The class body runs once, at the moment Python reaches the class statement, not each time you make an object. Names it creates (tax, price, total) end up in the namespace dict, which becomes the class __dict__. That is why a class body can hold any normal code, even print.', 'warn')}
{versus('Ways to make a class', ['', 'class statement', 'type(name, bases, dict)', 'collections.namedtuple or dataclasses.make_dataclass'], [
    ['Readable', 'Best', 'Hard for big classes', 'Good'],
    ['Name and fields known only at run time', 'No', 'Yes', 'Yes'],
    ['Methods', 'Written normally', 'Functions in the dict', 'Generated for you, add more by hand'],
    ['Typical use', 'Almost always', 'Factories, plugins, tests', 'Record types built from data']],
    'write a class statement whenever you can. Use type() or make_dataclass when the shape of the class comes from data.')}
''', kw=['type()', 'three argument type', 'dynamic class', 'class body', 'namespace', 'make_dataclass', 'factory'])

K.lesson('introspect', 'Introspection: looking inside while the program runs', f'''
{run('introspect')}
{table(['Tool', 'What it gives you'], [
    ['getattr(obj, "name", default)', 'The attribute with that name, or the default instead of AttributeError'],
    ['setattr(obj, "name", value), delattr(obj, "name")', 'Set or remove an attribute when the name is in a string'],
    ['hasattr(obj, "name")', 'True if getattr would work'],
    ['callable(x)', 'True if x can be called: functions, methods, classes, objects with __call__'],
    ['vars(obj) or obj.__dict__', 'The attributes stored in the object itself'],
    ['dir(obj)', 'Every name you can reach from obj, including inherited ones, sorted'],
    ['obj.__class__, C.__name__, C.__bases__, C.__mro__', 'The class of an object, its name, its parents and its lookup order'],
    ['C.__subclasses__()', 'The direct children that exist right now'],
    ['inspect.signature(f)', 'The parameters of a function, with defaults']])}
{versus('Choosing a method by its name', ['', 'if and elif chain', 'getattr(obj, name)', 'a dict of name to function'], [
    ['Code to add a new action', 'A new branch every time', 'Only the new method', 'One new dict entry'],
    ['Speed', 'Checks branches one by one', 'One lookup', 'One lookup'],
    ['Safety with user input', 'Safe, only listed names', 'Can reach any attribute, so check the name first', 'Safe, only listed names']],
    'use getattr for names you control (like LeetCode style command lists) and a dict for names that come from users.')}
''', kw=['introspection', 'getattr', 'setattr', 'hasattr', 'delattr', 'callable', 'dir', 'vars', 'inspect.signature', '__subclasses__', '__class__'])

K.lesson('hooks', '__init_subclass__ and class decorators', f'''
{run('initsub')}
{note('__init_subclass__ (PEP 487, Python 3.6) runs on the PARENT every time a child class is created. It is a class method automatically. Keyword arguments in the class line, like name="csv", are passed to it. Always call super().__init_subclass__(**kwargs) so other parents in a multiple inheritance chain get their turn.', 'exam')}
{run('classdeco')}
{note('A class decorator is a function that takes a finished class and returns a class, usually the same one after changing it. @dataclass, @functools.total_ordering and @enum.unique are class decorators from the standard library. Stacked decorators run from the bottom up, so auto_repr ran before route.', 'tip')}
{versus('Three ways to run code when a class is made', ['', 'class decorator', '__init_subclass__', 'metaclass'], [
    ['Applies to', 'Only the decorated class', 'Every child (and grandchild) of the parent', 'Every class it builds, and their children'],
    ['When it runs', 'After the class exists', 'While the class is being built', 'Before, during and after building, and on every call of the class'],
    ['Can change the namespace before the class exists', 'No', 'No', 'Yes, in __new__ or __prepare__'],
    ['Can change how objects are made', 'Only by replacing methods', 'Only by replacing methods', 'Yes, with __call__'],
    ['Mixes with other metaclasses', 'Always', 'Always', 'Can clash (metaclass conflict)'],
    ['How hard to read', 'Easy', 'Easy', 'Hard']],
    'reach for a class decorator or __init_subclass__ first. They cover most real needs. Use a metaclass only when you must control the namespace or object creation.')}
''', kw=['__init_subclass__', 'PEP 487', 'class decorator', 'registry', 'plugin', 'auto_repr', 'route'])

K.lesson('metaclass', 'Metaclasses', f'''
{run('metaclass')}
{note('A metaclass is a subclass of type. Its __new__(mcs, name, bases, namespace) gets everything the class statement collected and must return the new class, normally from super().__new__. Children of Job use CheckMeta too, because Python uses the metaclass of the base class when none is given. The check fires when the class is DEFINED, long before anyone uses it.', 'exam')}
{run('singleton')}
{note('Calling a class, Config(...), really calls type(Config).__call__. The normal type.__call__ runs __new__ and then __init__. Overriding __call__ in a metaclass changes what calling the class does: here it returns the saved object. Notice that the second call did not even run __init__, so mode stayed "prod".', 'warn')}
{run('stdmeta')}
{note('You already use metaclasses: ABC is built by ABCMeta (that is how abstract methods block objects) and every Enum by EnumType (that is why len(Colour) and for c in Colour work on the class itself). A class whose bases have two unrelated metaclasses cannot be made, because Python cannot pick one metaclass that is a child of both.', 'tip')}
{versus('Ways to allow only one object', ['', 'a module level object', 'a metaclass __call__', '__new__ that returns a saved object'], [
    ['Code needed', 'One line: config = Config()', 'A metaclass class', 'A few lines in the class'],
    ['Easy to understand', 'Yes', 'No', 'Medium'],
    ['__init__ runs again on each call', 'Not called again', 'No', 'Yes, a common surprise'],
    ['Easy to test and replace', 'Yes', 'Hard', 'Hard']],
    'in Python a module is already created only once, so a module level object is the usual answer. Know the metaclass version for exams and old code.')}
{deep('Tim Peters on metaclasses', '<p>"Metaclasses are deeper magic than 99% of users should ever worry about. If you wonder whether you need them, you don\'t." Most frameworks that once needed a metaclass (Django models, SQLAlchemy declarative classes) can now be written with __init_subclass__ and __set_name__.</p>')}
''', kw=['metaclass', 'type subclass', '__new__', '__call__', 'singleton', 'ABCMeta', 'EnumType', 'metaclass conflict'])

K.lesson('order', 'The full order of class creation', f'''
{run('order')}
{steps('What Python does for a class statement, in order', [
    'Pick the metaclass: the one given with metaclass=, otherwise the metaclass of the bases (the most derived one), otherwise type.',
    'Call Meta.__prepare__(name, bases) to get the namespace. type gives a plain dict.',
    'Run the class body inside that namespace. It stores __module__, __qualname__ and every name the body defines.',
    'Call Meta(name, bases, namespace). That runs Meta.__new__, which calls type.__new__ to build the class object.',
    'Inside type.__new__: call __set_name__ on every attribute that has it, then __init_subclass__ on the parent.',
    'Run Meta.__init__ on the new class.',
    'Apply class decorators from the bottom up.',
    'Store the result under the class name. Later, calling the class runs Meta.__call__, which runs __new__ and __init__.'])}
{deep('Going further: __prepare__, __mro_entries__ and types.new_class', '<p>__prepare__ may return any mapping, for example one that refuses duplicate names or records the order of definitions. __mro_entries__ lets an object that is not a class appear in a base list (typing.Generic uses it). types.new_class(name, bases, kwds, exec_body) is the safe way to build a class with a metaclass and keywords from code, because it follows every step above exactly like a class statement.</p>')}
''', kw=['class creation order', '__prepare__', '__set_name__', '__init_subclass__', 'Meta.__init__', 'types.new_class', '__mro_entries__'])

K.lesson('maths', 'The maths: counting classes, lookups and steps', f'''
{fxs(fx('Classes made by a factory', 'classes = n<sub>1</sub> &times; n<sub>2</sub> &times; ... &times; n<sub>k</sub>', 'make_record for 3 colours and 4 sizes builds 3 &times; 4 = 12 classes.'),
     fx('Classes in a full hierarchy below one base', 'b + b<sup>2</sup> + ... + b<sup>d</sup> = b(b<sup>d</sup> &minus; 1) / (b &minus; 1)', 'With b = 3 children each and d = 2 levels: 3 + 9 = 12 subclasses, each one seen by __init_subclass__.', key=True),
     fx('Average checks in an if and elif chain', 'average = (n + 1) / 2 for n equally likely names', 'A chain of 9 actions needs 5 checks on average. A dict or getattr needs about 1 lookup.', key=True),
     fx('Worst case attribute lookup', 'dicts checked &le; 1 + len(C.__mro__)', 'The instance dict, then each class in the MRO. For Kitten, Cat, object: at most 1 + 3 = 4.'),
     fx('Objects made by a singleton', 'objects = 1 for any n &ge; 1 calls, against n for a normal class', '50 calls of Config() make 1 object.'),
     fx('Steps from an object up to type', 'type(rex) = Dog, type(Dog) = Meta, type(Meta) = type, type(type) = type', 'Three steps reach type, and then the chain repeats itself.'))}
{steps('Worked example: how many registry entries does Plugin collect?', [
    'Plugin has 3 direct children: b = 3.',
    'Each child has 3 children of its own: d = 2 levels.',
    'Level 1 gives 3 classes and level 2 gives 3 &times; 3 = 9.',
    eq('3 + 9 = 3(3<sup>2</sup> &minus; 1) / (3 &minus; 1) = 12 entries')])}
''', kw=['geometric series', 'hierarchy size', 'average comparisons', 'MRO lookup', 'singleton count'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>Know that classes are objects: type(x), isinstance, store and pass classes, and read __name__, __bases__ and __dict__.</p>',
    '<p>Build classes with type(name, bases, dict), use getattr, setattr, hasattr and vars to work with names in strings, and write class decorators and __init_subclass__ registries.</p>',
    '<p>Write metaclasses with __new__ and __call__, explain inherited metaclasses and metaclass conflicts, and recognise ABCMeta and EnumType in the standard library.</p>',
    '<p>Explain the whole class creation protocol: metaclass selection, __prepare__, the body, __new__, __set_name__, __init_subclass__, __init__, decorators. object is an instance of type and type is a subclass of object, a loop CPython sets up by hand at start up. Know when __mro_entries__ and types.new_class are the right tools, and why most designs should not need a metaclass at all.</p>')}
{grow('Treat classes as objects and look inside them.',
      'Make classes from data and react when classes are created.',
      'Control class creation completely, and choose the lightest tool.')}
''', kw=['beginner', 'expert', 'class creation protocol', 'type and object'])

PLAY = '''

def play(cls, ops, args):
    """Run LeetCode style commands: make the object, then call each method by its name."""
    obj = cls(*args[0])
    results = [None]
    for name, arg in zip(ops[1:], args[1:]):
        results.append(getattr(obj, name)(*arg))
    return results
'''

lc(211, 'Design Add and Search Words Data Structure', 'design-add-and-search-words-data-structure', 'm', 'A trie of dicts, search with recursion', 'Store each word letter by letter in nested dicts. A dot must try every child, so search with a small recursive helper.', r'''
class WordDictionary:
    def __init__(self):
        self.root = {}

    def addWord(self, word):
        node = self.root
        for ch in word:
            node = node.setdefault(ch, {})
        node["$"] = True

    def search(self, word):
        return self.find(self.root, word, 0)

    def find(self, node, word, i):
        if i == len(word):
            return "$" in node
        ch = word[i]
        if ch == ".":
            for key in node:
                if key != "$" and self.find(node[key], word, i + 1):
                    return True
            return False
        return ch in node and self.find(node[ch], word, i + 1)
''' + PLAY, [('play(WordDictionary, ["WordDictionary", "addWord", "addWord", "addWord", "search", "search", "search", "search"], [[], ["bad"], ["dad"], ["mad"], ["pad"], ["bad"], [".ad"], ["b.."]])', [None, None, None, None, False, True, True, True])])
lc(380, 'Insert Delete GetRandom O(1)', 'insert-delete-getrandom-o1', 'm', 'A list plus a dict of positions', 'The list allows a random pick. The dict maps each value to its index. To remove, move the last value into the hole and pop.', r'''
import random


class RandomizedSet:
    def __init__(self):
        self.values = []
        self.where = {}

    def insert(self, val):
        if val in self.where:
            return False
        self.where[val] = len(self.values)
        self.values.append(val)
        return True

    def remove(self, val):
        if val not in self.where:
            return False
        index = self.where.pop(val)
        last = self.values.pop()
        if index < len(self.values):
            self.values[index] = last
            self.where[last] = index
        return True

    def getRandom(self):
        return random.choice(self.values)
''' + PLAY, [('play(RandomizedSet, ["RandomizedSet", "insert", "remove", "insert", "insert", "remove", "insert"], [[], [1], [2], [2], [1], [1], [2]])', [None, True, False, True, False, True, False]), ('(lambda s: (s.insert(5), s.insert(7), s.remove(5), s.getRandom()))(RandomizedSet())[3]', 7)])
lc(2502, 'Design Memory Allocator', 'design-memory-allocator', 'm', 'Scan a list of owners', 'Keep one owner id per memory unit (0 means free). allocate looks for the first run of free units that is long enough.', r'''
class Allocator:
    def __init__(self, n):
        self.memory = [0] * n

    def allocate(self, size, mID):
        run = 0
        for i in range(len(self.memory)):
            if self.memory[i] == 0:
                run += 1
                if run == size:
                    start = i - size + 1
                    for j in range(start, i + 1):
                        self.memory[j] = mID
                    return start
            else:
                run = 0
        return -1

    def freeMemory(self, mID):
        count = 0
        for i in range(len(self.memory)):
            if self.memory[i] == mID:
                self.memory[i] = 0
                count += 1
        return count
''' + PLAY, [('play(Allocator, ["Allocator", "allocate", "allocate", "allocate", "freeMemory", "allocate", "allocate", "allocate", "freeMemory", "allocate", "freeMemory"], [[10], [1, 1], [1, 2], [1, 3], [2], [3, 4], [1, 1], [1, 1], [1], [10, 2], [7]])', [None, 0, 1, 2, 1, 3, 1, 6, 3, -1, 0])])
lc(2353, 'Design a Food Rating System', 'design-a-food-rating-system', 'm', 'A heap per cuisine with lazy deletion', 'Push (-rating, name) into the heap of the cuisine. When asked, pop entries whose rating is out of date before reading the top.', r'''
import heapq


class FoodRatings:
    def __init__(self, foods, cuisines, ratings):
        self.rating = {}
        self.cuisine = {}
        self.heaps = {}
        for food, cuisine, rating in zip(foods, cuisines, ratings):
            self.rating[food] = rating
            self.cuisine[food] = cuisine
            heapq.heappush(self.heaps.setdefault(cuisine, []), (-rating, food))

    def changeRating(self, food, newRating):
        self.rating[food] = newRating
        heapq.heappush(self.heaps[self.cuisine[food]], (-newRating, food))

    def highestRated(self, cuisine):
        heap = self.heaps[cuisine]
        while -heap[0][0] != self.rating[heap[0][1]]:
            heapq.heappop(heap)                # an old rating, throw it away
        return heap[0][1]
''' + PLAY, [('play(FoodRatings, ["FoodRatings", "highestRated", "highestRated", "changeRating", "highestRated", "changeRating", "highestRated"], [[["kimchi", "miso", "sushi", "moussaka", "ramen", "bulgogi"], ["korean", "japanese", "japanese", "greek", "japanese", "korean"], [9, 12, 8, 15, 14, 7]], ["korean"], ["japanese"], ["sushi", 16], ["japanese"], ["ramen", 16], ["japanese"]])', [None, 'kimchi', 'ramen', None, 'sushi', None, 'ramen'])])
lc(2671, 'Frequency Tracker', 'frequency-tracker', 'm', 'Two counters', 'Count each number, and also count how many numbers have each frequency. Then hasFrequency is one dict lookup.', r'''
class FrequencyTracker:
    def __init__(self):
        self.count = {}
        self.freq = {}

    def change(self, number, step):
        old = self.count.get(number, 0)
        new = old + step
        if new < 0:
            return
        self.freq[old] = self.freq.get(old, 0) - 1
        self.freq[new] = self.freq.get(new, 0) + 1
        self.count[number] = new

    def add(self, number):
        self.change(number, 1)

    def deleteOne(self, number):
        self.change(number, -1)

    def hasFrequency(self, frequency):
        return self.freq.get(frequency, 0) > 0
''' + PLAY, [('play(FrequencyTracker, ["FrequencyTracker", "add", "add", "hasFrequency"], [[], [3], [3], [2]])', [None, None, None, True]), ('play(FrequencyTracker, ["FrequencyTracker", "add", "deleteOne", "hasFrequency"], [[], [1], [1], [1]])', [None, None, None, False])])
lc(1993, 'Operations on Tree', 'operations-on-tree', 'm', 'Parents list, children lists, a lock dict', 'lock and unlock check one node. upgrade checks that no ancestor is locked and at least one descendant is, then unlocks every descendant.', r'''
class LockingTree:
    def __init__(self, parent):
        self.parent = parent
        self.children = [[] for i in range(len(parent))]
        for node in range(1, len(parent)):
            self.children[parent[node]].append(node)
        self.locked = {}                       # node: user

    def lock(self, num, user):
        if num in self.locked:
            return False
        self.locked[num] = user
        return True

    def unlock(self, num, user):
        if self.locked.get(num) != user:
            return False
        del self.locked[num]
        return True

    def upgrade(self, num, user):
        node = num
        while node != -1:
            if node in self.locked:
                return False
            node = self.parent[node]
        found = False
        stack = list(self.children[num])
        while stack:
            node = stack.pop()
            if node in self.locked:
                del self.locked[node]
                found = True
            stack.extend(self.children[node])
        if found:
            self.locked[num] = user
        return found
''' + PLAY, [('play(LockingTree, ["LockingTree", "lock", "unlock", "unlock", "lock", "upgrade", "lock"], [[[-1, 0, 0, 1, 1, 2, 2]], [2, 2], [2, 3], [2, 2], [4, 5], [0, 1], [0, 1]])', [None, True, False, True, True, True, False])])
lc(1357, 'Apply Discount Every n Orders', 'apply-discount-every-n-orders', 'm', 'A counter and a price dict', 'Count customers. Every n-th bill is multiplied by (100 &minus; discount) / 100.', r'''
class Cashier:
    def __init__(self, n, discount, products, prices):
        self.n = n
        self.discount = discount
        self.price = dict(zip(products, prices))
        self.customers = 0

    def getBill(self, product, amount):
        self.customers += 1
        total = 0
        for p, a in zip(product, amount):
            total += self.price[p] * a
        if self.customers % self.n == 0:
            total = total * (100 - self.discount) / 100
        return total
''' + PLAY, [('play(Cashier, ["Cashier", "getBill", "getBill", "getBill"], [[3, 50, [1, 2, 3, 4, 5, 6, 7], [100, 200, 300, 400, 300, 200, 100]], [[1, 2], [1, 2]], [[3, 7], [10, 10]], [[1, 2, 3, 4, 5, 6, 7], [1, 1, 1, 1, 1, 1, 1]]])', [None, 500, 4000, 800.0])])
lc(1476, 'Subrectangle Queries', 'subrectangle-queries', 'm', 'Keep a list of updates', 'Instead of painting every cell, remember each update. getValue checks the updates from newest to oldest and falls back to the original grid.', r'''
class SubrectangleQueries:
    def __init__(self, rectangle):
        self.grid = rectangle
        self.updates = []

    def updateSubrectangle(self, row1, col1, row2, col2, newValue):
        self.updates.append((row1, col1, row2, col2, newValue))

    def getValue(self, row, col):
        for r1, c1, r2, c2, value in reversed(self.updates):
            if r1 <= row <= r2 and c1 <= col <= c2:
                return value
        return self.grid[row][col]
''' + PLAY, [('play(SubrectangleQueries, ["SubrectangleQueries", "getValue", "updateSubrectangle", "getValue", "getValue", "updateSubrectangle", "getValue", "getValue"], [[[[1, 2, 1], [4, 3, 4], [3, 2, 1], [1, 1, 1]]], [0, 2], [0, 0, 3, 2, 5], [0, 2], [3, 1], [3, 0, 3, 2, 10], [3, 1], [0, 2]])', [None, 1, None, 5, 5, None, 10, 5])])
lc(2166, 'Design Bitset', 'design-bitset', 'm', 'A list of bits plus a flipped flag', 'flip only toggles a flag, so it is O(1). Keep a count of ones and fix it up when flip happens.', r'''
class Bitset:
    def __init__(self, size):
        self.bits = [0] * size
        self.flipped = False
        self.ones = 0

    def value(self, idx):
        return self.bits[idx] ^ self.flipped

    def fix(self, idx):
        if self.value(idx) == 0:
            self.bits[idx] ^= 1
            self.ones += 1

    def unfix(self, idx):
        if self.value(idx) == 1:
            self.bits[idx] ^= 1
            self.ones -= 1

    def flip(self):
        self.flipped = not self.flipped
        self.ones = len(self.bits) - self.ones

    def all(self):
        return self.ones == len(self.bits)

    def one(self):
        return self.ones > 0

    def count(self):
        return self.ones

    def toString(self):
        text = ""
        for idx in range(len(self.bits)):
            text += str(int(self.value(idx)))
        return text
''' + PLAY, [('play(Bitset, ["Bitset", "fix", "fix", "flip", "all", "unfix", "flip", "one", "unfix", "count", "toString"], [[5], [3], [1], [], [], [0], [], [], [0], [], []])', [None, None, None, None, False, None, None, True, None, 2, '01010'])])
lc(2424, 'Longest Uploaded Prefix', 'longest-uploaded-prefix', 'm', 'A set and a pointer that only moves forward', 'Remember uploaded videos in a set. The prefix pointer moves right while the next video is there. Each video is passed once in total.', r'''
class LUPrefix:
    def __init__(self, n):
        self.uploaded = set()
        self.prefix = 0

    def upload(self, video):
        self.uploaded.add(video)
        while self.prefix + 1 in self.uploaded:
            self.prefix += 1

    def longest(self):
        return self.prefix
''' + PLAY, [('play(LUPrefix, ["LUPrefix", "upload", "longest", "upload", "longest", "upload", "longest"], [[4], [3], [], [1], [], [2], []])', [None, None, 0, None, 1, None, 3])])

K.lesson('leetcode', 'LeetCode practice', leet('<p>Every problem here is a "design" problem, and LeetCode tests them with metaprogramming: it reads a list of method names, makes the object, and calls each method by its name with getattr. The downloadable file includes a small play() helper that does exactly that, so you can run the official examples as they appear on the site.</p>'), kw=['LeetCode', 'design', 'getattr', 'command list', 'trie', 'heap'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'Classes are objects. type(x) gives the class of x, and the class of a class is its metaclass, normally type.',
    'type(name, bases, namespace) builds a class without a class statement. Use it, or make_dataclass, when the class shape comes from data.',
    'A class body runs once and fills a namespace dict that becomes the class __dict__.',
    'getattr, setattr, hasattr, vars, dir and inspect let code look at and change objects by name while it runs.',
    '__init_subclass__ runs on the parent for every new child (great for registries). A class decorator gets the finished class.',
    'A metaclass is a subclass of type. __new__ controls building the class, __call__ controls making objects. Children inherit the metaclass.',
    'Order: pick metaclass, __prepare__, body, Meta.__new__, __set_name__, __init_subclass__, Meta.__init__, decorators, bind the name.'],
    'Step 2 starts with iterators and generators, the protocol behind every for loop.')}
{files('Three tasks: a plugin registry with __init_subclass__, a class factory built with type(), and a metaclass that demands docstrings and lists public methods.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'What is type(int)?', ['int', 'type', 'object', 'class'], 1, 'The class of a class.', 'Built in classes are made by type, the default metaclass.')
K.quiz('e', 'What does type("A", (), {"x": 1}) return?', ['The string "A"', 'A new class named A with a class attribute x', 'An object of class A', 'An error'], 1, 'Three arguments.', 'With three arguments type builds a class.')
K.quiz('e', 'obj has no attribute pin. What does getattr(obj, "pin", 0) return?', ['None', '0', 'It raises AttributeError', '"pin"'], 1, 'The default.', 'The third argument is returned instead of raising AttributeError.')
K.quiz('m', 'When does the body of a class statement run?', ['Every time an object is made', 'Once, when Python reaches the class statement', 'Only when a method is called', 'Never, it is only read'], 1, 'Like normal code.', 'It runs once and fills the namespace that becomes the class __dict__.')
K.quiz('m', 'Which method of a parent class runs automatically every time a child class is created?', ['__init__', '__new__', '__init_subclass__', '__set_name__'], 2, 'PEP 487.', '__init_subclass__ is called on the parent with the new child class as cls.')
K.quiz('m', 'What does a class decorator receive?', ['The class body as text', 'The finished class object', 'Each new instance', 'The metaclass'], 1, 'After building.', 'It gets the class and returns a class, usually the same one.')
K.quiz('m', 'In a metaclass, which method runs when you write Config()?', ['Meta.__new__', 'Meta.__prepare__', 'Meta.__call__', 'Meta.__init_subclass__'], 2, 'Calling the class.', 'Calling a class calls type(cls).__call__, which normally runs __new__ and __init__.')
K.quiz('m', 'A class has both a metaclass that adds tag in __new__ and a class decorator. Which runs first?', ['The decorator', 'The metaclass __new__', 'They run at the same time', 'It depends on the order in the file'], 1, 'Order of creation.', 'The class must exist before a decorator can receive it.')
K.quiz('h', 'type(A) is MetaA and type(B) is MetaB, two unrelated metaclasses. What does class C(A, B): pass do?', ['C uses MetaA', 'C uses type', 'TypeError: metaclass conflict', 'C uses MetaB'], 2, 'One metaclass must win.', 'Python needs a metaclass that is a subclass of both, and there is none.')
K.quiz('h', 'What is type(Colour).__name__ for class Colour(Enum) in Python 3.14?', ['Enum', 'type', 'EnumType', 'EnumMeta'], 2, 'Enum has a metaclass.', 'EnumType (still available under the old name EnumMeta) gives the class len, iteration and indexing.')
K.quiz('h', 'Why does a child of Job use CheckMeta even without metaclass= in its class line?', ['Metaclasses are global', 'Python uses the metaclass of the base classes when none is given', 'Decorators are inherited', 'It does not'], 1, 'Metaclass selection.', 'The most derived metaclass of the bases is used.')
K.quiz('x', 'In the style of a Stanford CS 242 exam: every subclass of Model must be registered and must set a table name. Which is the lightest correct tool?', ['A metaclass with __prepare__', '__init_subclass__ on Model', 'A decorator on every subclass', 'An if chain in main'], 1, 'Least magic that works.', '__init_subclass__ runs for every child automatically, needs no metaclass and cannot be forgotten like a decorator.')
K.quiz('x', 'In the style of an Oxford exam: what are isinstance(type, object) and isinstance(object, type)?', ['True and False', 'False and True', 'Both True', 'Both False'], 2, 'The loop at the top.', 'type is an object, and object is a class made by type.')

K.calc('e', 'make_record is called once for each of 3 colours and each of 4 sizes. How many classes are built?', '12', 'Multiply the choices.', ['3 colour choices.', '4 size choices for each colour.', eq('3 &times; 4 = 12')], check=3 * 4)
K.calc('e', 'Starting from rex, how many calls of type() reach type? (type(rex) is Dog, Dog is built by Meta.)', '3', 'Follow the chain.', ['type(rex) = Dog.', 'type(Dog) = Meta.', eq('type(Meta) = type, so 3 calls')], check=3)
K.calc('e', 'Config uses the Singleton metaclass. Config() is called 50 times. How many Config objects exist?', '1', 'Saved after the first call.', ['The first call creates the object.', 'The other 49 calls return the saved one.', eq('1')], check=1)
K.calc('m', 'A base has b = 3 children per class over d = 2 levels. How many subclasses does __init_subclass__ see?', '12', 'b + b<sup>2</sup>.', ['Level 1: 3.', 'Level 2: 3 &times; 3 = 9.', eq('3 + 9 = 12')], check=3 + 9)
K.calc('m', 'An if and elif chain picks one of 9 equally likely actions. How many checks does it need on average?', '5', '(n + 1) / 2.', ['n = 9.', '(9 + 1) / 2.', eq('5')], check=(9 + 1) / 2)
K.calc('m', 'Kitten.__mro__ is (Kitten, Cat, object). At most how many dicts does Python check to find an attribute of a Kitten object?', '4', '1 + len(MRO).', ['First the instance dict: 1.', 'Then 3 classes in the MRO.', eq('1 + 3 = 4')], check=1 + 3)
K.calc('m', 'Plugin registers every subclass. A(Plugin), B(Plugin) and C(A) are defined. How many registry entries are there?', '3', 'Grandchildren count too.', ['A and B are direct children.', 'C is a child of A, so Plugin.__init_subclass__ still runs.', eq('3')], check=3)
K.calc('h', 'b = 2 children per class over d = 10 levels. How many subclasses are there in total?', '2046', 'b(b<sup>d</sup> &minus; 1) / (b &minus; 1).', ['2<sup>10</sup> = 1024.', '2 &times; (1024 &minus; 1) / (2 &minus; 1) = 2 &times; 1023.', eq('2046')], check=2 * (2 ** 10 - 1) // (2 - 1))
K.calc('h', '1000 commands go through an if chain of 20 equally likely names. How many times more checks is that than 1000 dict lookups?', '10.5', 'Average checks per command.', ['Average checks: (20 + 1) / 2 = 10.5.', '1000 &times; 10.5 = 10,500 checks against 1000 lookups.', eq('10,500 / 1000 = 10.5')], check=(20 + 1) / 2)
K.calc('x', 'In the style of an ETH Zurich exam: a metaclass adds one attribute to every class it builds. The base uses it and has 3 children per class over 3 levels below it. How many classes get the attribute, counting the base?', '40', '1 + 3 + 9 + 27.', ['The base: 1.', 'Below it: 3 + 9 + 27 = 39.', eq('1 + 39 = 40')], check=1 + 3 + 9 + 27)

K.assign('plugins', 'm', 'A shape registry with __init_subclass__',
         '<p>Make every child of <code>Shape</code> register itself in <code>Shape.registry</code> under the key given in its class line (for example <code>class Circle(Shape, key="circle")</code>). Then write <code>make(key, *args)</code> that builds the right shape, and raises <code>KeyError</code> for an unknown key. Circle uses 3.14 for pi. raises() is a test helper.</p>',
         '''
class Shape:
    registry = {}

    # your code here: def __init_subclass__(cls, key, **kwargs)


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


def make(key, *args):
    pass


def raises(func, *args):
    try:
        func(*args)
    except Exception as err:
        return type(err).__name__
    return None
''', [('sorted(Shape.registry)', ['circle', 'square']), ('make("square", 3).area()', 9), ('make("circle", 1).area()', 3.14), ('raises(make, "hexagon", 2)', 'KeyError')],
         '''
class Shape:
    registry = {}

    def __init_subclass__(cls, key, **kwargs):
        super().__init_subclass__(**kwargs)
        Shape.registry[key] = cls


class Circle(Shape, key="circle"):
    def __init__(self, r):
        self.r = r

    def area(self):
        return 3.14 * self.r * self.r


class Square(Shape, key="square"):
    def __init__(self, side):
        self.side = side

    def area(self):
        return self.side * self.side


def make(key, *args):
    cls = Shape.registry[key]                  # KeyError for an unknown key
    return cls(*args)


def raises(func, *args):
    try:
        func(*args)
    except Exception as err:
        return type(err).__name__
    return None
''', 'Add key="circle" and key="square" to the class lines. In __init_subclass__ store cls under key. make looks the class up and calls it.', '<p>Adding a new shape now needs no change to make(): the new class registers itself the moment it is defined.</p>')
K.assign('factory', 'e', 'A class factory with type()',
         '<p>Write <code>make_class(name, attrs)</code> that uses <code>type()</code> to build a class called name, with the dict attrs as class attributes, and a method <code>describe(self)</code> that returns the class name, a colon, and the attribute names sorted and joined by ", ". Example: make_class("Car", {"wheels": 4, "doors": 2})().describe() gives "Car: doors, wheels".</p>',
         '''
def make_class(name, attrs):
    pass
''', [('make_class("Car", {"wheels": 4, "doors": 2})().describe()', 'Car: doors, wheels'), ('make_class("Bike", {"wheels": 2}).wheels', 2), ('make_class("Box", {}).__name__', 'Box'), ('make_class("Tag", {"x": 1})().describe()', 'Tag: x')],
         '''
def make_class(name, attrs):
    keys = sorted(attrs)

    def describe(self):
        return name + ": " + ", ".join(keys)

    namespace = dict(attrs)
    namespace["describe"] = describe
    return type(name, (), namespace)
''', 'Copy attrs into a new dict, add a describe function, and pass it to type(name, (), namespace).', '<p>describe remembers name and keys through its closure, so every class built by the factory describes itself correctly.</p>')
K.assign('docmeta', 'h', 'A metaclass that demands docstrings',
         '<p>Write a metaclass <code>RequireDoc</code>. When it builds a class, every public method (a callable whose name does not start with "_") must have a docstring, or it raises <code>TypeError</code>. It also adds a class attribute <code>methods</code>: the sorted list of public method names. The helper <code>try_class(meta, name, namespace)</code> builds a class or returns the error name. documented and bare are sample functions.</p>',
         '''
class RequireDoc(type):
    pass


def documented(self):
    """Does the work."""


def bare(self):
    pass


def try_class(meta, name, namespace):
    try:
        return meta(name, (), dict(namespace))
    except Exception as err:
        return type(err).__name__
''', [('try_class(RequireDoc, "Good", {"run": documented, "stop": documented}).methods', ['run', 'stop']), ('try_class(RequireDoc, "Bad", {"run": bare})', 'TypeError'), ('try_class(RequireDoc, "Mixed", {"_helper": bare, "run": documented}).methods', ['run']), ('try_class(RequireDoc, "Data", {"size": 3}).methods', [])],
         '''
class RequireDoc(type):
    def __new__(mcs, name, bases, namespace):
        methods = []
        for key, value in namespace.items():
            if key.startswith("_") or not callable(value):
                continue
            if not value.__doc__:
                raise TypeError(name + "." + key + " has no docstring")
            methods.append(key)
        namespace["methods"] = sorted(methods)
        return super().__new__(mcs, name, bases, namespace)


def documented(self):
    """Does the work."""


def bare(self):
    pass


def try_class(meta, name, namespace):
    try:
        return meta(name, (), dict(namespace))
    except Exception as err:
        return type(err).__name__
''', 'In __new__ loop over the namespace, skip names starting with "_" and values that are not callable, check value.__doc__, then store the sorted list under "methods" before calling super().__new__.', '<p>The rule runs once per class, when it is defined, so a missing docstring is caught as soon as the module is imported.</p>')

K.must('Classes are objects', 'type(x) gives the class. type(Dog) is the metaclass (normally type). type(type) is type. Classes can be stored, passed and returned.')
K.must('type() with three arguments', 'type(name, bases, namespace) builds a class. A class statement does the same. The body runs once and fills the namespace.')
K.must('Introspection', 'getattr(obj, name, default), setattr, hasattr, delattr, callable, vars, dir, __class__, __bases__, __mro__, __subclasses__(), inspect.signature.')
K.must('Hooks', '__init_subclass__ on the parent runs for every child (registries, checks). Class decorators get the finished class.')
K.must('Metaclasses', 'class Meta(type): __new__ builds the class, __call__ makes objects. Inherited by children. Conflicts raise TypeError. Prefer lighter tools.')

T = K.topic(
    slug='py-metaclasses', topic='py-metaclasses', step=(1, 'Advanced object oriented programming', 'py-a1', 'Make classes behave like built in types, then master decorators, class design, exceptions, copying, serialisation and metaclasses.', 'Advanced'),
    title='Metaprogramming: type, class hooks and metaclasses', short='Metaclasses', badge='1.5', minutes=75,
    lead='Write code that builds and checks classes. Learn that classes are objects, how type() makes classes, introspection with getattr and friends, __init_subclass__, class decorators, metaclasses with __new__ and __call__, and the exact order in which Python creates a class.',
    desc='classes as objects, type with one and three arguments, the class body and namespace, getattr, setattr, hasattr, delattr, callable, vars, dir, inspect.signature, __class__, __bases__, __mro__, __subclasses__, __init_subclass__ registries, class decorators, metaclasses with __new__, __init__, __call__ and __prepare__, singletons, ABCMeta and EnumType, metaclass conflicts, the class creation order, types.new_class.',
    summary='classes as objects, type(), introspection, __init_subclass__, class decorators, metaclasses, creation order.',
    keywords=['metaclass', 'type', 'metaprogramming', 'getattr', 'setattr', 'introspection', '__init_subclass__', 'class decorator', '__new__', '__call__', '__prepare__', 'singleton', 'PCPP'],
    recap='<p>Classes are objects built by metaclasses. Hook into class creation with the lightest tool that works: a decorator, __init_subclass__, and only then a metaclass.</p>',
    added='2026-11-07', leet=leet_items())
