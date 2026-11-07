# Core Python 6.1: classes and objects. Follows PCAP-31-03 section 3 (object oriented programming: class, object,
# property, method, encapsulation, instance and class variables, the __dict__ property, private components and name
# mangling, methods and self, constructors and __init__, introspection with hasattr(), __name__, __module__ and
# __bases__, the __str__ method, the is operator), checked against the Python 3.14 tutorial chapter 9 "Classes" and
# the data model reference section 3.3.
import math
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, lc, leet, files, grow, leet_items

chapter('py-classes')
K = Kit()

K.code('first', r'''
class Dog:
    species = "dog"                    # class attribute: shared by every dog

    def __init__(self, name, age):     # runs when a new dog is made
        self.name = name               # instance attributes: each dog has its own
        self.age = age

    def bark(self):                    # a method: a function that belongs to the class
        return self.name + " says woof"

    def birthday(self):
        self.age += 1


rex = Dog("Rex", 3)                    # make an object (an instance) of the class
moti = Dog("Moti", 5)
print(rex.name, rex.age, "|", moti.name, moti.age)
print(rex.bark())
rex.birthday()
print(rex.age, moti.age)               # only Rex got older
print(type(rex).__name__, isinstance(rex, Dog), rex.species)
''')

K.code('self', r'''
class Dog:
    def __init__(self, name):
        self.name = name

    def bark(self):
        return self.name + " says woof"

    def hello():                       # a mistake: forgot self
        return "hi"


rex = Dog("Rex")
print(rex.bark())
print(Dog.bark(rex))                   # the same call, written the long way
print(type(Dog.bark).__name__, type(rex.bark).__name__)
print(rex.bark.__self__ is rex)        # the bound method remembers its object

try:
    Dog.bark()
except TypeError as err:
    print("TypeError:", err)

try:
    rex.hello()
except TypeError as err:
    print("TypeError:", err)
''')

K.code('attrs', r'''
class Dog:
    species = "dog"

    def __init__(self, name):
        self.name = name


a = Dog("Rex")
b = Dog("Moti")
print(a.__dict__, b.__dict__)          # only instance attributes live here
print("species" in Dog.__dict__)       # the class attribute lives on the class

a.species = "wolf"                     # creates a NEW attribute on a only
print(a.species, b.species, Dog.species)
Dog.species = "canine"                 # changes the class attribute
print(a.species, b.species)
print(a.__dict__)

del a.species                          # remove a's own copy
print(a.species)                       # now found on the class again

a.color = "brown"                      # you may add attributes at any time
print(a.__dict__, hasattr(b, "color"))
''')

K.code('shared', r'''
class Bad:
    tricks = []                        # ONE list, shared by all objects

    def __init__(self, name):
        self.name = name

    def learn(self, trick):
        self.tricks.append(trick)


class Good:
    def __init__(self, name):
        self.name = name
        self.tricks = []               # a new list for every object

    def learn(self, trick):
        self.tricks.append(trick)


a, b = Bad("Rex"), Bad("Moti")
a.learn("sit")
print("Bad: ", b.tricks, a.tricks is b.tricks)

c, d = Good("Rex"), Good("Moti")
c.learn("sit")
print("Good:", d.tricks, c.tricks is d.tricks)
''')

K.code('counter', r'''
class Student:
    count = 0                          # how many students were made

    def __init__(self, name):
        self.name = name
        Student.count += 1             # change the CLASS attribute
        self.number = Student.count    # each student gets its own number


s1 = Student("Asha")
s2 = Student("Ravi")
s3 = Student("Meera")
print(Student.count, s1.number, s3.number)
print(s1.count)                        # read through an instance: still the class value
''')

K.code('strrepr', r'''
class Plain:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):                # for developers: looks like code
        return f"Point({self.x}, {self.y})"

    def __str__(self):                 # for users: nice to read
        return f"({self.x}, {self.y})"


p = Plain(3, 4)
print(repr(p).startswith("<__main__.Plain object at 0x"))   # the default: name and memory address

q = Point(3, 4)
print(q)                               # print uses __str__
print(repr(q))                         # repr uses __repr__
print([q, Point(0, 0)])                # a list shows the repr of its items
print(f"{q} and {q!r}")
print(str(q) + " is a point")
''')

K.code('introspect', r'''
class Point:
    """A point on a grid."""
    dims = 2

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def move(self, dx, dy):
        self.x += dx
        self.y += dy


p = Point(3, 4)
print(type(p).__name__, Point.__name__, Point.__module__)
print(isinstance(p, Point), isinstance(3, Point), p.__class__ is Point)
print(hasattr(p, "x"), hasattr(p, "z"), hasattr(p, "move"))
print(getattr(p, "y"), getattr(p, "z", "no z"))
setattr(p, "z", 5)                     # the same as p.z = 5
print(vars(p))                         # the same as p.__dict__
delattr(p, "z")                        # the same as del p.z
print(p.__dict__)
print(Point.__doc__, Point.__bases__)
print([name for name in Point.__dict__ if not name.startswith("__")])

field = "x"                            # the attribute name is only known at run time
print(getattr(p, field))
''')

K.code('private', r'''
class Account:
    def __init__(self, owner, balance):
        self.owner = owner             # public
        self._note = "vip"             # one underscore: "internal, please do not touch"
        self.__balance = balance       # two underscores: name mangled

    def balance(self):
        return self.__balance          # inside the class the short name works


acc = Account("Asha", 500)
print(acc.owner, acc._note, acc.balance())
try:
    print(acc.__balance)
except AttributeError as err:
    print("AttributeError:", err)
print(acc.__dict__)                    # the real name is _Account__balance
print(acc._Account__balance)           # still reachable: mangling is not security
''')

K.code('identity', r'''
class Box:
    def __init__(self, size):
        self.size = size


a = Box(5)
b = Box(5)
c = a                                  # c is another name for the SAME object
print(a == b, a is b, a is c)          # by default == means "is"
c.size = 9
print(a.size)                          # a changed too


class Coin:
    def __init__(self, value):
        self.value = value

    def __eq__(self, other):           # decide what "equal" means for coins
        return isinstance(other, Coin) and self.value == other.value


print(Coin(5) == Coin(5), Coin(5) is Coin(5), Coin(5) == 5)
print(Coin.__hash__)                   # None: a class with __eq__ but no __hash__ cannot go in a set
''')

K.code('bank', r'''
class BankAccount:
    bank = "Brainy Bank"

    def __init__(self, owner, balance=0):
        self.owner = owner
        self.balance = balance
        self.history = []

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("amount must be positive")
        self.balance += amount
        self.history.append(("deposit", amount))

    def withdraw(self, amount):
        if amount > self.balance:
            raise ValueError("not enough money")
        self.balance -= amount
        self.history.append(("withdraw", amount))

    def __str__(self):
        return f"{self.owner} has {self.balance} at {self.bank}"


acc = BankAccount("Asha", 100)
acc.deposit(50)
acc.withdraw(30)
try:
    acc.withdraw(500)
except ValueError as err:
    print("refused:", err)
print(acc)
print(acc.history)
''')

K.code('vector', r'''
import math


class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def length(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def add(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def dot(self, other):
        return self.x * other.x + self.y * other.y

    def __repr__(self):
        return f"Vector({self.x}, {self.y})"


a = Vector(3, 4)
b = Vector(1, 2)
print(a.length(), a.add(b), a.dot(b))
cos_angle = a.dot(b) / (a.length() * b.length())
print(round(math.degrees(math.acos(cos_angle)), 2), "degrees between a and b")
''')

K.lesson('idea', 'Classes and objects', f'''
{src('Python 3.14 tutorial chapter 9 "Classes", the data model reference section 3.3, and PCAP-31-03 section 3.')}
{wwh('A <b>class</b> is a blueprint that describes a kind of thing: what data it holds (its <b>attributes</b>) and what it can do (its <b>methods</b>). An <b>object</b> (also called an <b>instance</b>) is one real thing made from that blueprint.',
     'Programs model the real world: students, bank accounts, shapes, orders. Keeping each thing as loose variables and separate functions gets messy fast. A class keeps the data and the code that works on it together in one place, so each object looks after itself.',
     'class Dog: makes a class object. Calling Dog("Rex", 3) makes a new empty object and runs __init__ on it to fill in its attributes. Every object has its own attributes but shares the methods of its class. When you write rex.bark(), Python finds bark on the class and passes rex in as self.')}
{scene('a cake recipe and the cakes', '<p>A recipe says a cake has a flavour and a size and can be cut into slices. The recipe itself is not a cake. Each cake you bake from it is a separate cake with its own flavour and size. Cutting one cake does not change the others. The recipe is the class and each cake is an object.</p>')}
{run('first')}
{table(['Word', 'Meaning', 'In the program'], [
    ['class', 'The blueprint', 'Dog'],
    ['object or instance', 'One thing made from the class', 'rex, moti'],
    ['attribute', 'A value stored on an object or a class', 'name, age, species'],
    ['method', 'A function defined inside the class', 'bark, birthday'],
    ['constructor', 'The code that sets up a new object', '__init__'],
    ['self', 'The object a method is working on', 'self.name']])}
''', kw=['class', 'object', 'instance', 'attribute', 'method', 'blueprint', 'OOP', 'object oriented programming'])

K.lesson('self', 'Methods, self and __init__', f'''
{run('self')}
{note('self is not a keyword. It is only the name every Python programmer uses for the first parameter of a method. Python fills it in for you: rex.bark() becomes Dog.bark(rex). Forget self in the def line and the call fails with "takes 0 positional arguments but 1 was given".', 'exam')}
{table(['You write', 'Python does'], [
    ['rex = Dog("Rex")', 'Makes an empty object, then calls Dog.__init__(that object, "Rex"), then names it rex'],
    ['rex.bark()', 'Finds bark on the class and calls Dog.bark(rex)'],
    ['Dog.bark', 'A plain function'],
    ['rex.bark', 'A bound method: the function plus the object, ready to call']])}
{deep('Where does the new object come from', '<p>Making an object has two steps. First the special method __new__ creates the empty object. Then __init__ fills it in. __init__ only sets things up and must return None. Returning anything else raises TypeError. You almost never write __new__ yourself (Advanced 1.4 shows when you do).</p>')}
''', kw=['self', '__init__', 'constructor', 'method', 'bound method', '__new__', 'missing self'])

K.lesson('attrs', 'Instance attributes and class attributes', f'''
{viz('pyclass')}
{run('attrs')}
{versus('Two places an attribute can live', ['', 'instance attribute', 'class attribute'], [
    ['Made by', 'self.name = ... (usually in __init__)', 'name = ... in the class body'],
    ['Stored in', 'obj.__dict__', 'Class.__dict__'],
    ['How many copies', 'One per object', 'One for the whole class'],
    ['Good for', 'Data that differs between objects: name, age, balance', 'Constants and data every object shares: species, bank name, a counter']],
    'put data that changes from object to object on the instance, and shared constants on the class.')}
{steps('How Python reads obj.attr', [
    'Look in obj.__dict__, the attributes of the object itself.',
    'If it is not there, look in the class of the object (and later in its parent classes, see 6.2).',
    'If it is still not found, raise AttributeError.'])}
{note('Writing obj.attr = value never goes to the class. It always creates or changes the attribute on that one object. That is why a.species = "wolf" left b.species and Dog.species alone.', 'exam')}
''', kw=['instance attribute', 'class attribute', '__dict__', 'attribute lookup', 'shadowing', 'del attribute'])

K.lesson('shared', 'The shared list trap', f'''
{run('shared')}
{note('A class attribute that holds a list, dict or set is ONE object for all instances. Changing it with append or update through any object changes it for every object. Create such data in __init__ with self.items = [] instead. This is the same trap as a mutable default argument (4.1).', 'warn')}
''', kw=['mutable class attribute', 'shared list', 'class attribute trap'])

K.lesson('counter', 'Class attributes as counters', f'''
{run('counter')}
{note('Inside a method, change a class attribute through the class name: Student.count += 1. Writing self.count += 1 reads the class value but then stores the result on the object, so the class counter would never change.', 'exam')}
''', kw=['class attribute', 'counter', 'instance count', 'self.count trap'])

K.lesson('strrepr', '__str__ and __repr__', f'''
{run('strrepr')}
{versus('Two ways to turn an object into text', ['', '__str__', '__repr__'], [
    ['Used by', 'print(obj), str(obj), f"{obj}"', 'repr(obj), f"{obj!r}", the REPL, items inside a list'],
    ['Written for', 'Users', 'Developers'],
    ['Good style', 'Short and friendly: (3, 4)', 'Clear and exact, ideally valid code: Point(3, 4)'],
    ['If missing', 'Python uses __repr__', 'Python shows the class name and memory address']],
    'always write __repr__. Add __str__ only when users need a friendlier form.')}
''', kw=['__str__', '__repr__', 'print object', 'string representation', 'dunder method', 'magic method'])

K.lesson('introspect', 'Introspection: looking inside objects', f'''
{run('introspect')}
{table(['Tool', 'Answers'], [
    ['type(obj), obj.__class__', 'Which class made this object'],
    ['isinstance(obj, C)', 'Is obj a C (or a child class of C, see 6.2)'],
    ['hasattr(obj, "x")', 'Can obj.x be read without an error'],
    ['getattr(obj, "x", default)', 'Read an attribute by its name as a string'],
    ['setattr(obj, "x", v), delattr(obj, "x")', 'Set or delete an attribute by name'],
    ['vars(obj), obj.__dict__', 'The instance attributes as a dict'],
    ['C.__name__, C.__module__, C.__bases__, C.__doc__', 'The class name, its module, its parent classes and its docstring'],
    ['dir(obj)', 'Every attribute name, including the inherited ones']])}
{note('getattr with a name in a variable is how frameworks such as Django read a field whose name comes from a settings file or a URL.', 'tip')}
''', kw=['introspection', 'hasattr', 'getattr', 'setattr', 'isinstance', 'type', '__name__', '__module__', '__bases__', 'vars', 'dir'])

K.lesson('private', 'Encapsulation, _private and name mangling', f'''
{run('private')}
{table(['Name', 'Meaning', 'Enforced'], [
    ['balance', 'Public: anyone may use it', 'Not needed'],
    ['_balance', 'Internal: please use it only inside the class', 'No, a convention only'],
    ['__balance', 'Name mangled to _Account__balance so child classes cannot clash with it by accident', 'Partly: the short name fails outside the class'],
    ['__init__', 'Special (dunder) name used by Python itself', 'Do not invent your own']])}
{note('<b>Encapsulation</b> means an object guards its own data and offers methods to work with it, so outside code cannot put it into a bad state (like a negative balance). Python trusts programmers: it has no real private keyword like Java. Use one underscore for internal things, and properties (Advanced 1.3) when you need checks on reading or writing.', 'exam')}
''', kw=['encapsulation', 'private', 'name mangling', '_Account__balance', 'underscore', 'convention'])

K.lesson('identity', 'Identity and equality of objects', f'''
{run('identity')}
{note('a is b asks "are these the same object". a == b asks "are these equal". For your own classes == means the same as is until you write __eq__. Writing __eq__ sets __hash__ to None, so the objects can no longer be set items or dict keys unless you also write __hash__ (Advanced 1.1).', 'exam')}
''', kw=['is', '==', 'identity', 'equality', '__eq__', '__hash__', 'alias'])

K.lesson('bank', 'Putting it together: a bank account', f'''
{run('bank')}
{note('Each method keeps the object valid: deposit refuses amounts that are not positive and withdraw refuses to go below zero. Code outside the class never has to repeat these checks. That is the main gain of object oriented design.', 'tip')}
''', kw=['bank account', 'class design', 'validation', 'raise in method', 'history'])

K.lesson('compare', 'Classes compared with other ways to group data', f'''
{versus('A student record three ways', ['', 'separate variables', 'a dict', 'a class'], [
    ['Example', 'name1, mark1, name2, mark2', '{"name": "Asha", "mark": 88}', 'Student("Asha", 88)'],
    ['Typing mistakes', 'Easy to mix up', 's["nmae"] fails only when run', 's.nmae fails, and editors warn early'],
    ['Behaviour', 'Separate functions', 'Separate functions', 'Methods next to the data'],
    ['Rules (no negative marks)', 'Checked everywhere by hand', 'Checked everywhere by hand', 'Checked once, in the class'],
    ['Many of them', 'Impossible', 'A list of dicts', 'A list of objects'],
    ['Best for', 'A few unrelated values', 'Data from JSON, flexible keys', 'Things with data AND behaviour']],
    'use a dict for loose data, and a class when the data has rules and actions. For pure data with no behaviour, dataclasses (Advanced 1.3) give you a class in two lines.')}
{versus('Object oriented and procedural style', ['', 'procedural (functions and data apart)', 'object oriented (classes)'], [
    ['Organised around', 'Steps and functions', 'Things and their behaviour'],
    ['Data protection', 'Any function can change any data', 'Methods guard their own object'],
    ['Reuse', 'Copy or call functions', 'Inheritance and composition (6.2)'],
    ['Good for', 'Short scripts, data pipelines', 'Bigger programs, games, GUIs, web frameworks']],
    'Python lets you mix both. Start with functions and move to a class when several functions keep passing the same data around.')}
''', kw=['class vs dict', 'procedural vs object oriented', 'when to use a class', 'data and behaviour'])

K.lesson('maths', 'The maths inside a class', f'''
{run('vector')}
{fxs(fx('Length of a vector (Pythagoras)', '|v| = &radic;(x<sup>2</sup> + y<sup>2</sup>)', 'Vector(3, 4).length() is &radic;(9 + 16) = 5.', key=True),
     fx('Dot product', 'a &middot; b = a<sub>x</sub>b<sub>x</sub> + a<sub>y</sub>b<sub>y</sub>', '(3, 4) &middot; (1, 2) = 3 + 8 = 11.', key=True),
     fx('Angle between two vectors', 'cos &theta; = (a &middot; b) / (|a| |b|)', 'cos &theta; = 11 / (5 &times; 2.236) = 0.984, so &theta; = 10.3 degrees.'),
     fx('Counting objects with a class attribute', 'count after n objects = n', 'One class attribute is shared, so 3 students give Student.count = 3.'),
     fx('Name mangling', '__name inside class C becomes _C__name', '__balance in Account becomes _Account__balance (17 characters).'),
     fx('Memory', 'n objects store n copies of each instance attribute but 1 copy of each class attribute and method', '1,000 dogs: 1,000 names, 1 species, 1 bark function.'))}
{steps('Worked example: the angle between a = (3, 4) and b = (1, 2)', [
    'a &middot; b = 3 &times; 1 + 4 &times; 2 = 11.',
    '|a| = &radic;25 = 5 and |b| = &radic;5 &asymp; 2.236.',
    'cos &theta; = 11 / 11.18 &asymp; 0.9839.',
    eq('&theta; = acos(0.9839) &asymp; 10.30 degrees, which the program printed')])}
''', kw=['vector class', 'dot product', 'vector length', 'angle', 'name mangling rule', 'memory of objects'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>A class is a blueprint and objects are things made from it. Write __init__ to set attributes with self, and call methods with dot notation.</p>',
    '<p>Tell instance attributes from class attributes, avoid the shared list trap, write __str__ and __repr__, use isinstance, hasattr and getattr, and protect data with methods and the underscore convention.</p>',
    '<p>Know how attribute lookup works (instance dict, then class), what a bound method is, what name mangling does and why it exists, and how __eq__ and __hash__ go together. Choose between a dict, a class and a dataclass for a design.</p>',
    '<p>Classes are objects too: their type is type, the class body runs once and fills a namespace that type() turns into a class. Attribute access goes through object.__getattribute__, which checks data descriptors on the class, then the instance __dict__, then other class attributes. Methods are functions that are descriptors: their __get__ makes the bound method. __slots__ replaces the per object dict with fixed slots to save memory (Advanced 1.3 and 1.4).</p>')}
{grow('Write a class with __init__, attributes and methods, and make objects from it.',
      'Use class attributes correctly, write __str__ and __repr__, use introspection and encapsulation.',
      'Explain attribute lookup, bound methods, name mangling and the __eq__ and __hash__ contract.')}
''', kw=['beginner', 'expert', 'descriptors', '__getattribute__', 'type', '__slots__', 'metaclass'])

lc(155, 'Min Stack', 'min-stack', 'm', 'Keep a second stack of minimums', 'Next to the normal stack, keep a stack whose top is always the smallest value so far. Push to it when the new value is not bigger.', r'''
class MinStack:
    # LeetCode names the methods getMin and so on, so we keep their names
    def __init__(self):
        self.items = []
        self.mins = []          # mins[-1] is always the smallest value in the stack

    def push(self, val):
        self.items.append(val)
        if not self.mins or val <= self.mins[-1]:
            self.mins.append(val)

    def pop(self):
        val = self.items.pop()
        if val == self.mins[-1]:
            self.mins.pop()

    def top(self):
        return self.items[-1]

    def getMin(self):
        return self.mins[-1]
''', [('(lambda s: [s.push(-2), s.push(0), s.push(-3), s.getMin(), s.pop(), s.top(), s.getMin()])(MinStack())', [None, None, None, -3, None, 0, -2])])
lc(232, 'Implement Queue using Stacks', 'implement-queue-using-stacks', 'e', 'Two stacks', 'Push onto an inbox stack. To pop, pour the inbox into an outbox stack (which reverses it) only when the outbox is empty.', r'''
class MyQueue:
    def __init__(self):
        self.inbox = []
        self.outbox = []

    def push(self, x):
        self.inbox.append(x)

    def move(self):
        if not self.outbox:
            while self.inbox:
                self.outbox.append(self.inbox.pop())

    def pop(self):
        self.move()
        return self.outbox.pop()

    def peek(self):
        self.move()
        return self.outbox[-1]

    def empty(self):
        return not self.inbox and not self.outbox
''', [('(lambda q: [q.push(1), q.push(2), q.peek(), q.pop(), q.empty()])(MyQueue())', [None, None, 1, 1, False])])
lc(225, 'Implement Stack using Queues', 'implement-stack-using-queues', 'e', 'Rotate one queue', 'After adding x to the back, move every older item from the front to the back, so x is at the front.', r'''
from collections import deque


class MyStack:
    def __init__(self):
        self.queue = deque()

    def push(self, x):
        self.queue.append(x)
        for i in range(len(self.queue) - 1):
            self.queue.append(self.queue.popleft())

    def pop(self):
        return self.queue.popleft()

    def top(self):
        return self.queue[0]

    def empty(self):
        return len(self.queue) == 0
''', [('(lambda s: [s.push(1), s.push(2), s.top(), s.pop(), s.empty()])(MyStack())', [None, None, 2, 2, False])])
lc(705, 'Design HashSet', 'design-hashset', 'e', 'Buckets of lists', 'Keep 1,000 small lists. A key goes in bucket key % 1000, so each search looks at only one short list.', r'''
class MyHashSet:
    def __init__(self):
        self.size = 1000
        self.buckets = [[] for i in range(self.size)]

    def add(self, key):
        bucket = self.buckets[key % self.size]
        if key not in bucket:
            bucket.append(key)

    def remove(self, key):
        bucket = self.buckets[key % self.size]
        if key in bucket:
            bucket.remove(key)

    def contains(self, key):
        return key in self.buckets[key % self.size]
''', [('(lambda h: [h.add(1), h.add(2), h.contains(1), h.contains(3), h.add(2), h.contains(2), h.remove(2), h.contains(2)])(MyHashSet())', [None, None, True, False, None, True, None, False])])
lc(706, 'Design HashMap', 'design-hashmap', 'e', 'Buckets of key and value pairs', 'Like the hash set, but each bucket holds [key, value] pairs. put updates a pair or adds one.', r'''
class MyHashMap:
    def __init__(self):
        self.size = 1000
        self.buckets = [[] for i in range(self.size)]

    def put(self, key, value):
        bucket = self.buckets[key % self.size]
        for pair in bucket:
            if pair[0] == key:
                pair[1] = value
                return
        bucket.append([key, value])

    def get(self, key):
        for pair in self.buckets[key % self.size]:
            if pair[0] == key:
                return pair[1]
        return -1

    def remove(self, key):
        bucket = self.buckets[key % self.size]
        for i in range(len(bucket)):
            if bucket[i][0] == key:
                bucket.pop(i)
                return
''', [('(lambda m: [m.put(1, 1), m.put(2, 2), m.get(1), m.get(3), m.put(2, 1), m.get(2), m.remove(2), m.get(2)])(MyHashMap())', [None, None, 1, -1, None, 1, None, -1]),
      ('(lambda m: [m.put(1, 5), m.put(1001, 7), m.get(1), m.get(1001)])(MyHashMap())', [None, None, 5, 7])])
lc(1603, 'Design Parking System', 'design-parking-system', 'e', 'One counter per car type', 'Store the free spaces in a list indexed by car type. A car parks only if its counter is above zero.', r'''
class ParkingSystem:
    def __init__(self, big, medium, small):
        self.free = [0, big, medium, small]     # index 1 is big, 2 is medium, 3 is small

    def addCar(self, carType):
        if self.free[carType] == 0:
            return False
        self.free[carType] -= 1
        return True
''', [('(lambda p: [p.addCar(1), p.addCar(2), p.addCar(3), p.addCar(1)])(ParkingSystem(1, 1, 0))', [True, True, False, False])])
lc(1472, 'Design Browser History', 'design-browser-history', 'm', 'A list and a position', 'Keep the pages in a list and the index of the current page. visit cuts off the forward pages, back and forward move the index within limits.', r'''
class BrowserHistory:
    def __init__(self, homepage):
        self.pages = [homepage]
        self.current = 0

    def visit(self, url):
        self.pages = self.pages[:self.current + 1]     # forward history is cleared
        self.pages.append(url)
        self.current += 1

    def back(self, steps):
        self.current = max(0, self.current - steps)
        return self.pages[self.current]

    def forward(self, steps):
        self.current = min(len(self.pages) - 1, self.current + steps)
        return self.pages[self.current]
''', [('(lambda b: [b.visit("google.com"), b.visit("facebook.com"), b.visit("youtube.com"), b.back(1), b.back(1), b.forward(1), b.visit("linkedin.com"), b.forward(2), b.back(2), b.back(7)])(BrowserHistory("leetcode.com"))',
       [None, None, None, 'facebook.com', 'google.com', 'facebook.com', None, 'linkedin.com', 'google.com', 'leetcode.com'])])
lc(622, 'Design Circular Queue', 'design-circular-queue', 'm', 'Fixed list, head index and count', 'The back of the queue is at (head + count) % k. Moving the head with % k makes the list wrap around.', r'''
class MyCircularQueue:
    def __init__(self, k):
        self.data = [0] * k
        self.k = k
        self.head = 0
        self.count = 0

    def enQueue(self, value):
        if self.isFull():
            return False
        tail = (self.head + self.count) % self.k
        self.data[tail] = value
        self.count += 1
        return True

    def deQueue(self):
        if self.isEmpty():
            return False
        self.head = (self.head + 1) % self.k
        self.count -= 1
        return True

    def Front(self):
        if self.isEmpty():
            return -1
        return self.data[self.head]

    def Rear(self):
        if self.isEmpty():
            return -1
        return self.data[(self.head + self.count - 1) % self.k]

    def isEmpty(self):
        return self.count == 0

    def isFull(self):
        return self.count == self.k
''', [('(lambda q: [q.enQueue(1), q.enQueue(2), q.enQueue(3), q.enQueue(4), q.Rear(), q.isFull(), q.deQueue(), q.enQueue(4), q.Rear()])(MyCircularQueue(3))', [True, True, True, False, 3, True, True, True, 4])])
lc(2043, 'Simple Bank System', 'simple-bank-system', 'm', 'Check, then change', 'Every method first checks that the account numbers exist and the money is there, and only then changes the balances.', r'''
class Bank:
    def __init__(self, balance):
        self.balance = balance          # account number i is stored at balance[i - 1]

    def valid(self, account):
        return 1 <= account <= len(self.balance)

    def transfer(self, account1, account2, money):
        if not self.valid(account1) or not self.valid(account2):
            return False
        if self.balance[account1 - 1] < money:
            return False
        self.balance[account1 - 1] -= money
        self.balance[account2 - 1] += money
        return True

    def deposit(self, account, money):
        if not self.valid(account):
            return False
        self.balance[account - 1] += money
        return True

    def withdraw(self, account, money):
        if not self.valid(account) or self.balance[account - 1] < money:
            return False
        self.balance[account - 1] -= money
        return True
''', [('(lambda b: [b.withdraw(3, 10), b.transfer(5, 1, 20), b.deposit(5, 20), b.transfer(3, 4, 15), b.withdraw(10, 50)])(Bank([10, 100, 20, 50, 30]))', [True, True, True, False, False])])
lc(146, 'LRU Cache', 'lru-cache', 'm', 'A dict keeps insertion order', 'Python dicts remember the order keys were added. Move a key to the end when it is used, and remove the first key when the cache is full.', r'''
class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.data = {}              # oldest key first, newest key last

    def get(self, key):
        if key not in self.data:
            return -1
        value = self.data.pop(key)
        self.data[key] = value      # move it to the newest end
        return value

    def put(self, key, value):
        if key in self.data:
            self.data.pop(key)
        elif len(self.data) == self.capacity:
            oldest = next(iter(self.data))
            self.data.pop(oldest)
        self.data[key] = value
''', [('(lambda c: [c.put(1, 1), c.put(2, 2), c.get(1), c.put(3, 3), c.get(2), c.put(4, 4), c.get(1), c.get(3), c.get(4)])(LRUCache(2))', [None, None, 1, None, -1, None, -1, 3, 4])])

K.lesson('leetcode', 'LeetCode practice', leet('<p>LeetCode "design" problems ask you to write a class: you choose the attributes in __init__ and write the methods. They are the best practice for this chapter because each one is about keeping an object in a correct state.</p>'), kw=['LeetCode', 'design problems', 'min stack', 'queue', 'hash map', 'LRU cache', 'class design'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'A <b>class</b> is a blueprint, an <b>object</b> (instance) is one thing made from it. Calling the class makes an object.',
    '__init__(self, ...) sets up a new object. self is the object a method works on: obj.m() means Class.m(obj).',
    'Instance attributes (self.x) belong to one object. Class attributes (in the class body) are shared by all objects.',
    'Reading obj.x looks in the object first, then the class. Writing obj.x = v always writes to the object.',
    'A list or dict as a class attribute is shared by every object. Create it in __init__ instead.',
    '__str__ is for print, __repr__ is for developers. Write __repr__ at least.',
    'type, isinstance, hasattr, getattr, setattr, vars and __name__, __module__, __bases__ let code look inside objects.',
    '_x means internal by convention. __x is name mangled to _Class__x. is checks identity, == checks equality (identity until you write __eq__).'],
    '6.2 builds on this with inheritance, super(), overriding, multiple inheritance and the MRO.')}
{files('Three tasks: a Rectangle class, a bank Account that refuses bad amounts, and a Stack class that keeps its own list.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'What does calling Dog("Rex") do?', ['Defines the class', 'Makes a new Dog object and runs __init__', 'Calls the bark method', 'Prints Rex'], 1, 'Calling a class.', 'Calling a class creates an instance and runs __init__ on it.')
K.quiz('e', 'What is self inside a method?', ['The class', 'The object the method was called on', 'A keyword that must be written self', 'The module'], 1, 'Whose method.', 'self is the instance. The name self is only a convention.')
K.quiz('e', 'Where should a value that is different for each object be stored?', ['In a class attribute', 'In an instance attribute set with self', 'In a global variable', 'In a method name'], 1, 'One per object.', 'self.name = name gives every object its own value.')
K.quiz('m', 'class A: x = 1. Then a = A(), a.x = 5. What is A.x?', ['5', '1', 'AttributeError', 'None'], 1, 'Where does assignment go.', 'a.x = 5 creates an attribute on a only. The class attribute stays 1.')
K.quiz('m', 'def hello(): return 1 is written inside class C (no self). What does C().hello() do?', ['Returns 1', 'Raises TypeError', 'Returns None', 'Raises NameError'], 1, 'Python passes the object.', 'Python passes the object as the first argument, but hello takes none: "takes 0 positional arguments but 1 was given".')
K.quiz('m', 'Which method does print(obj) use first?', ['__repr__', '__str__', '__init__', '__print__'], 1, 'For users.', 'print calls str(obj), which uses __str__ and falls back to __repr__.')
K.quiz('m', 'Inside class Account, self.__pin = 1234 is stored under which name?', ['__pin', '_pin', '_Account__pin', 'Account.__pin'], 2, 'Name mangling.', 'Two leading underscores are changed to _ClassName plus the name.')
K.quiz('m', 'For a plain class with no __eq__, when is a == b True?', ['When all attributes are equal', 'Only when a is b', 'Never', 'Always'], 1, 'Default equality.', 'Without __eq__, == falls back to identity.')
K.quiz('h', 'class Dog: tricks = []. a = Dog(), b = Dog(), a.tricks.append("sit"). What is b.tricks?', ['[]', '["sit"]', 'AttributeError', 'None'], 1, 'One list.', 'tricks is one list on the class. append changes that shared list.')
K.quiz('h', 'In __init__ the line self.count += 1 runs (count = 0 is a class attribute). What happens to the class attribute?', ['It becomes 1', 'It stays 0, the object gets its own count = 1', 'TypeError', 'Both become 1'], 1, 'Read from the class, write to the object.', 'self.count += 1 reads 0 from the class and writes 1 onto the object.')
K.quiz('h', 'A class defines __eq__ but not __hash__. What happens with {Coin(5)}?', ['Works', 'TypeError: unhashable type', 'Makes an empty set', 'Uses the id'], 1, 'The hash contract.', 'Defining __eq__ sets __hash__ to None, so the object is unhashable.')
K.quiz('x', 'In the style of an MIT 6.100L exam: class A: x = [] then a1, a2 = A(), A(), then a1.x.append(1), then a2.x = [2]. What is printed by print(A.x, a1.x, a2.x)?', ['[] [1] [2]', '[1] [1] [2]', '[1, 2] [1, 2] [1, 2]', '[1] [1] [1]'], 1, 'Mutate versus assign.', 'append changes the shared class list, so A.x and a1.x show [1]. a2.x = [2] makes a new attribute on a2 only.')
K.quiz('x', 'In the style of a Stanford CS 41 question: class C: pass, then c = C(), then C.f = lambda self: 42. What is c.f()?', ['AttributeError, f did not exist when c was made', '42', 'TypeError, a lambda cannot be a method', 'None'], 1, 'Lookup happens at call time.', 'Python looks up f on the class when c.f is read, not when c was made, and any function on a class becomes a method.')

K.calc('e', 'Student.count starts at 0 and __init__ does Student.count += 1. Five students are made. What is Student.count?', '5', 'One per object.', ['Each new student adds 1 to the class attribute.', 'Five students are made.', eq('5')], check=5)
K.calc('e', 'Rectangle(3, 4).area() where area returns width times height.', '12', '3 times 4.', ['width = 3, height = 4.', 'area = 3 &times; 4.', eq('12')], check=12)
K.calc('e', 'Vector(6, 8).length() using &radic;(x<sup>2</sup> + y<sup>2</sup>).', '10', 'Pythagoras.', ['36 + 64 = 100.', '&radic;100.', eq('10')], check=int(math.sqrt(6 ** 2 + 8 ** 2)))
K.calc('m', 'Vector(3, 4).dot(Vector(1, 2)).', '11', 'Multiply matching parts and add.', ['3 &times; 1 = 3.', '4 &times; 2 = 8.', eq('3 + 8 = 11')], check=3 * 1 + 4 * 2)
K.calc('m', 'Dog("Rex", 3) sets self.name and self.age. Then rex.color = "brown". How many keys are in rex.__dict__?', '3', 'Only instance attributes.', ['__init__ adds name and age.', 'rex.color adds a third.', eq('3 (class attributes are not in it)')], check=3)
K.calc('m', 'class Dog: tricks = []. Three dogs a, b, c. a.learn("sit") and b.learn("roll") both append to self.tricks. What is len(c.tricks)?', '2', 'One shared list.', ['Both appends go to the class list.', 'c reads the same list.', eq('2')], check=2)
K.calc('m', 'An account starts at 100. deposit(50), withdraw(30), then withdraw(500) raises ValueError and is caught. What is the balance?', '120', 'The refused withdrawal changes nothing.', ['100 + 50 = 150.', '150 &minus; 30 = 120.', eq('120, because withdraw(500) raises before changing the balance')], check=100 + 50 - 30)
K.calc('h', 'Dog.species = "dog". a, b and c are dogs. a.species = "wolf", then Dog.species = "cat". How many different values do a.species, b.species and c.species show?', '2', 'Who has their own.', ['a has its own: "wolf".', 'b and c read the class: "cat".', eq('2 different values')], check=len({'wolf', 'cat', 'cat'}))
K.calc('h', 'How many characters long is the stored name of self.__balance inside class Account?', '17', '_Account__balance.', ['The name becomes _ + Account + __balance.', '1 + 7 + 9 characters.', eq('17')], check=len('_Account__balance'))
K.calc('x', 'In the style of an Imperial College maths for computing problem: what is the angle in degrees between Vector(3, 4) and Vector(4, 3), to 2 decimal places?', '16.26', 'cos &theta; = a &middot; b / (|a| |b|).', ['a &middot; b = 12 + 12 = 24.', '|a| |b| = 5 &times; 5 = 25, so cos &theta; = 0.96.', eq('&theta; = acos(0.96) &asymp; 16.26 degrees')], check=round(math.degrees(math.acos(24 / 25)), 2))

RAISES = '''

def raises(func, *args):
    """Test helper: the name of the exception func(*args) raises, or None."""
    try:
        func(*args)
    except Exception as err:
        return type(err).__name__
    return None
'''

K.assign('rect', 'e', 'A Rectangle class',
         '<p>Write a class <code>Rectangle</code> made with <code>Rectangle(width, height)</code>. Give it the methods <code>area()</code>, <code>perimeter()</code> and <code>is_square()</code>, and a <code>__str__</code> that returns text like <code>"Rectangle 3 x 4"</code>.</p>',
         '''
class Rectangle:
    def __init__(self, width, height):
        # your code here
        pass

    def area(self):
        pass

    def perimeter(self):
        pass

    def is_square(self):
        pass

    def __str__(self):
        return ""
''', [('Rectangle(3, 4).area()', 12), ('Rectangle(3, 4).perimeter()', 14), ('Rectangle(3, 4).is_square()', False), ('Rectangle(5, 5).is_square()', True), ('str(Rectangle(3, 4))', 'Rectangle 3 x 4')],
         '''
class Rectangle:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height

    def perimeter(self):
        return 2 * (self.width + self.height)

    def is_square(self):
        return self.width == self.height

    def __str__(self):
        return "Rectangle " + str(self.width) + " x " + str(self.height)
''', 'Save width and height on self in __init__. Every method reads them from self.', '<p>The methods need no arguments apart from self, because the object already knows its own size.</p>')
K.assign('account', 'm', 'A safe bank account',
         '<p>Write a class <code>Account(owner, balance=0)</code>. <code>deposit(amount)</code> adds money and returns the new balance, but raises <code>ValueError</code> if amount is not more than 0. <code>withdraw(amount)</code> takes money and returns the new balance, but raises <code>ValueError</code> if amount is more than the balance. The balance must not change when an error is raised. raises() is a test helper.</p>',
         '''
class Account:
    def __init__(self, owner, balance=0):
        # your code here
        pass

    def deposit(self, amount):
        pass

    def withdraw(self, amount):
        pass
''' + RAISES, [('Account("Asha", 100).deposit(50)', 150), ('Account("Asha", 100).withdraw(30)', 70), ('raises(Account("Asha").deposit, 0)', 'ValueError'), ('raises(Account("Asha", 10).withdraw, 11)', 'ValueError'),
                ('(lambda a: (raises(a.withdraw, 500), a.balance))(Account("Ravi", 100))', ['ValueError', 100])],
         '''
class Account:
    def __init__(self, owner, balance=0):
        self.owner = owner
        self.balance = balance

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("amount must be positive")
        self.balance = self.balance + amount
        return self.balance

    def withdraw(self, amount):
        if amount > self.balance:
            raise ValueError("not enough money")
        self.balance = self.balance - amount
        return self.balance
''' + RAISES, 'Check first and raise ValueError before you change self.balance. Then change it and return it.', '<p>Checking before changing is what keeps the object valid. If you changed the balance first and checked after, a refused withdrawal would still have taken the money.</p>')
K.assign('stack', 'm', 'A Stack class with its own list',
         '<p>Write a class <code>Stack</code> with <code>push(item)</code>, <code>pop()</code> (returns the top item, raises <code>IndexError</code> if empty), <code>peek()</code> (returns the top without removing it), <code>__len__</code> so that <code>len(stack)</code> works, and <code>__repr__</code> that returns text like <code>"Stack([1, 2])"</code>. Two stacks must never share items.</p>',
         '''
class Stack:
    items = []          # careful: is this the right place?

    def push(self, item):
        pass

    def pop(self):
        pass

    def peek(self):
        pass
''' + RAISES, [('(lambda s: (s.push(1), s.push(2), s.pop(), len(s), s.peek()))(Stack())', [None, None, 2, 1, 1]), ('raises(Stack().pop)', 'IndexError'),
                ('(lambda s: (s.push(1), s.push(2), repr(s))[2])(Stack())', 'Stack([1, 2])'), ('(lambda a, b: (a.push(1), len(b))[1])(Stack(), Stack())', 0)],
         '''
class Stack:
    def __init__(self):
        self.items = []         # a new list for every stack

    def push(self, item):
        self.items.append(item)

    def pop(self):
        if len(self.items) == 0:
            raise IndexError("pop from empty stack")
        return self.items.pop()

    def peek(self):
        return self.items[-1]

    def __len__(self):
        return len(self.items)

    def __repr__(self):
        return "Stack(" + repr(self.items) + ")"
''' + RAISES, 'Move items into __init__ as self.items = []. Add __len__ and __repr__ methods.', '<p>The starter put the list on the class, so every stack would share it. That is the shared list trap from this chapter.</p>')

K.must('Class and object', 'class C: defines a blueprint. C(...) makes an object and runs __init__(self, ...). self is the object.')
K.must('Two kinds of attribute', 'self.x is per object (in obj.__dict__). x = ... in the class body is shared. Read looks in the object, then the class. Write goes to the object.')
K.must('Shared list trap', 'A list or dict class attribute is shared by all objects. Create it in __init__.')
K.must('Text forms', '__str__ for print and str, __repr__ for repr, lists and debugging. Write __repr__ at least.')
K.must('Introspection and privacy', 'type, isinstance, hasattr, getattr, setattr, vars, __name__, __module__, __bases__. _x is a convention, __x becomes _Class__x. is = same object.')

T = K.topic(
    slug='py-classes', topic='py-classes', step=(6, 'Object oriented programming', 'py-c6', 'Model things as objects with classes, attributes and methods, then reuse code with inheritance.', 'Intermediate'),
    title='Classes and objects: attributes, methods, self and encapsulation', short='Classes', badge='6.1', minutes=70,
    lead='Model real things as objects. Learn to write a class with __init__ and methods, what self is, instance attributes and class attributes, the shared list trap, __str__ and __repr__, introspection with hasattr and getattr, private names and name mangling, and identity and equality of objects.',
    desc='classes and objects, the class statement, __init__ and self, methods and bound methods, instance and class attributes, __dict__, attribute lookup and shadowing, mutable class attributes, counters, __str__ and __repr__, type, isinstance, hasattr, getattr, setattr, delattr, vars, __name__, __module__, __bases__, encapsulation, single underscore, name mangling, is and ==, __eq__ and __hash__, class design, classes compared with dicts.',
    summary='classes, objects, __init__, self, instance and class attributes, __str__ and __repr__, introspection, name mangling, is and ==.',
    keywords=['class', 'object', 'instance', '__init__', 'self', 'method', 'attribute', '__dict__', '__str__', '__repr__', 'hasattr', 'name mangling', 'encapsulation', 'OOP', 'PCAP'],
    recap='<p>A class keeps data and behaviour together. Put per object data on self in __init__, shared constants on the class, write __repr__, and let methods guard the object so it is never in a bad state.</p>',
    added='2026-11-07', leet=leet_items())
