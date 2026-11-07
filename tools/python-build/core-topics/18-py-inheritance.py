# Core Python 6.2: inheritance. Follows PCAP-31-03 section 3 (inheritance: single and multiple, superclass and
# subclass, isinstance() and issubclass(), overriding, the is operator, polymorphism, __bases__, the method resolution
# order and the diamond problem), checked against the Python 3.14 tutorial section 9.5 "Inheritance", the built-in
# functions super(), isinstance() and issubclass(), "The Python 2.3 Method Resolution Order" by Michele Simionato,
# and the abc module documentation.
import math
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, lc, leet, files, grow, leet_items

chapter('py-inheritance')
K = Kit()

K.code('basic', r'''
class Animal:                          # the parent class (superclass, base class)
    def __init__(self, name):
        self.name = name

    def speak(self):
        return "..."

    def describe(self):
        return self.name + " says " + self.speak()


class Dog(Animal):                     # Dog inherits everything from Animal
    def speak(self):                   # and overrides speak
        return "woof"


class Cat(Animal):
    def speak(self):
        return "meow"


class Fish(Animal):                    # overrides nothing
    pass


for pet in [Dog("Rex"), Cat("Tom"), Fish("Nemo")]:
    print(pet.describe())              # describe is written once, in Animal
''')

K.code('super', r'''
class Employee:
    def __init__(self, name, salary):
        self.name = name
        self.salary = salary

    def pay(self):
        return self.salary // 12       # monthly pay


class Manager(Employee):
    def __init__(self, name, salary, bonus):
        super().__init__(name, salary) # let the parent set name and salary
        self.bonus = bonus             # then add what is new

    def pay(self):
        return super().pay() + self.bonus   # extend the parent method, do not copy it


ravi = Employee("Ravi", 24000)
asha = Manager("Asha", 36000, 500)
print(ravi.pay(), asha.pay())
print(asha.__dict__)
''')

K.code('nosuper', r'''
class Employee:
    def __init__(self, name, salary):
        self.name = name
        self.salary = salary


class Intern(Employee):
    def __init__(self, name, school):  # overrides __init__ but forgets super()
        self.school = school


meera = Intern("Meera", "IIT")
print(meera.__dict__)
try:
    print(meera.name)
except AttributeError as err:
    print("AttributeError:", err)
''')

K.code('checks', r'''
class Animal:
    pass


class Dog(Animal):
    pass


rex = Dog()
print(isinstance(rex, Dog), isinstance(rex, Animal), isinstance(rex, object))
print(type(rex) == Dog, type(rex) == Animal)      # type() ignores parents
print(issubclass(Dog, Animal), issubclass(Animal, Dog))
print(Dog.__bases__, Animal.__bases__)
print([c.__name__ for c in Dog.__mro__])
print(issubclass(bool, int), isinstance(True, int), True + True)
print(isinstance(3, (str, int)))                  # a tuple means "any of these"
''')

K.code('override', r'''
class Animal:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return "an animal called " + self.name

    def speak(self):
        return "..."


class Dog(Animal):
    def __str__(self):
        return "a dog called " + self.name     # replaces the parent version

    def speak(self):
        old = Animal.speak(self)               # call the parent by its name (works, but super() is better)
        return old + " woof!"


rex = Dog("Rex")
print(rex)
print(rex.speak())
print(Dog.speak is Animal.speak, "speak" in Dog.__dict__, "__init__" in Dog.__dict__)
''')

K.code('poly', r'''
class Robot:                           # NOT an Animal
    def speak(self):
        return "beep"


class Duck:
    def speak(self):
        return "quack"


def make_noise(thing):                 # works with anything that has speak()
    return thing.speak()


for thing in [Duck(), Robot()]:
    print(type(thing).__name__, make_noise(thing))

print(len("abc"), len([1, 2]), len({"a": 1}))   # built in polymorphism
print(3 + 4, "3" + "4", [3] + [4])               # one operator, many types

try:
    make_noise(42)
except AttributeError as err:
    print("AttributeError:", err)
''')

K.code('shapes', r'''
import math


class Shape:
    def area(self):
        raise NotImplementedError("each shape must define area()")

    def describe(self):
        return type(self).__name__ + " with area " + str(round(self.area(), 2))


class Circle(Shape):
    def __init__(self, r):
        self.r = r

    def area(self):
        return math.pi * self.r ** 2


class Rectangle(Shape):
    def __init__(self, w, h):
        self.w = w
        self.h = h

    def area(self):
        return self.w * self.h


class Triangle(Shape):
    def __init__(self, a, b, c):
        self.a, self.b, self.c = a, b, c

    def area(self):                    # Heron's formula
        s = (self.a + self.b + self.c) / 2
        return math.sqrt(s * (s - self.a) * (s - self.b) * (s - self.c))


shapes = [Circle(2), Rectangle(3, 4), Triangle(3, 4, 5)]
for shape in shapes:
    print(shape.describe())
print("total", round(sum(shape.area() for shape in shapes), 2))
try:
    Shape().area()
except NotImplementedError as err:
    print("NotImplementedError:", err)
''')

K.code('abstract', r'''
from abc import ABC, abstractmethod


class Shape(ABC):                      # an abstract base class
    @abstractmethod
    def area(self):
        pass


class Square(Shape):
    def __init__(self, side):
        self.side = side

    def area(self):
        return self.side ** 2


class Blob(Shape):                     # forgot area()
    pass


print(Square(3).area())
for cls in [Shape, Blob]:
    try:
        cls()
    except TypeError as err:
        print("TypeError:", err)
''')

K.code('multi', r'''
import json


class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age


class JsonMixin:                       # a small class that only adds one ability
    def to_json(self):
        return json.dumps(self.__dict__)


class Employee(Person, JsonMixin):     # two parents
    def __init__(self, name, age, job):
        super().__init__(name, age)
        self.job = job


asha = Employee("Asha", 30, "pilot")
print(asha.to_json())
print([c.__name__ for c in Employee.__mro__])
print(Employee.__bases__)
''')

K.code('diamond', r'''
class A:
    def hello(self):
        return "A"


class B(A):
    def hello(self):
        return "B" + super().hello()


class C(A):
    def hello(self):
        return "C" + super().hello()


class D(B, C):
    def hello(self):
        return "D" + super().hello()


print([c.__name__ for c in D.__mro__])
print(D().hello())                     # each class runs once, A last
print(B().hello())                     # on a B object, super() in B goes to A
''')

K.code('mroerror', r'''
class X: pass
class Y: pass
class A(X, Y): pass                    # A says: X before Y
class B(Y, X): pass                    # B says: Y before X

try:
    class C(A, B): pass                # no order can keep both promises
except TypeError as err:
    print("TypeError:", err)

try:
    class E(X, X): pass
except TypeError as err:
    print("TypeError:", err)
''')

K.code('compose', r'''
class Engine:
    def __init__(self, power):
        self.power = power

    def start(self):
        return "engine with " + str(self.power) + " hp started"


class Car:                             # a car HAS an engine (composition)
    def __init__(self, model, power):
        self.model = model
        self.engine = Engine(power)

    def start(self):
        return self.model + ": " + self.engine.start()   # pass the work on (delegation)


class BadStack(list):                  # a stack IS a list: then it gets every list method
    def push(self, item):
        self.append(item)


class GoodStack:                       # a stack HAS a list
    def __init__(self):
        self.items = []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        return self.items.pop()


print(Car("Nano", 37).start())
bad = BadStack()
bad.push(1)
bad.push(2)
bad.insert(0, 99)                      # allowed, but it breaks the stack rule
print(bad)
good = GoodStack()
good.push(1)
print(hasattr(good, "insert"))
''')

K.lesson('idea', 'Inheritance: reuse a class', f'''
{src('Python 3.14 tutorial section 9.5 "Inheritance", the built-in functions super, isinstance and issubclass, the abc module documentation, M. Simionato "The Python 2.3 Method Resolution Order", and PCAP-31-03 section 3.')}
{wwh('<b>Inheritance</b> lets a new class (the <b>child</b>, subclass or derived class) take all the attributes and methods of an existing class (the <b>parent</b>, superclass or base class) and then add to them or change them.',
     'Many classes share most of their code: dogs and cats both have a name and can describe themselves. Writing that code again in each class means copies to keep in step. Inheritance writes it once in the parent, and each child only adds what is different.',
     'class Dog(Animal): makes Dog a child of Animal. When you use rex.describe(), Python looks for describe in Dog, does not find it, and moves on to Animal. A method the child defines with the same name <b>overrides</b> the parent one.')}
{scene('a family recipe', '<p>A family has a basic dal recipe. One cousin uses it exactly as it is. Another follows it but adds more chilli. A third keeps every step but swaps the last one for a coconut finish. Nobody rewrites the whole recipe: they inherit it and change only what they need.</p>')}
{run('basic')}
{note('The child is a special kind of the parent: a Dog is an Animal. If you cannot say "a Child is a Parent" in plain words, inheritance is probably the wrong tool (see composition below).', 'tip')}
''', kw=['inheritance', 'subclass', 'superclass', 'parent class', 'child class', 'base class', 'derived class', 'is a'])

K.lesson('override', 'Overriding methods', f'''
{run('override')}
{steps('How Python finds rex.speak()', [
    'Look in rex.__dict__ (the object itself).',
    'Look in Dog, the class of rex. speak is there, so use it.',
    'Only if Dog had no speak would Python look in Animal, then in object.',
    'Not found anywhere: AttributeError.'])}
{note('An overriding method normally keeps the same parameters as the parent one, so code that works with an Animal also works with a Dog. This rule is called the Liskov substitution principle.', 'exam')}
''', kw=['override', 'overriding', 'method lookup', 'Liskov substitution principle', '__str__ override'])

K.lesson('super', 'super(): use the parent version', f'''
{run('super')}
{run('nosuper')}
{versus('Two ways to call the parent', ['', 'super().method(...)', 'Parent.method(self, ...)'], [
    ['self', 'Passed for you', 'You pass it by hand'],
    ['If the parent class is renamed', 'Nothing to change', 'Every call must be edited'],
    ['Multiple inheritance', 'Follows the MRO, so every class runs once', 'Can run a class twice or skip one'],
    ['Seen in', 'Modern code', 'Old code']],
    'use super(). It is shorter and correct with multiple inheritance.')}
{note('A child __init__ replaces the parent one completely. If it does not call super().__init__(...), the attributes the parent sets are never created.', 'warn')}
''', kw=['super', 'super().__init__', 'extend method', 'constructor chaining', 'forgot super'])

K.lesson('checks', 'isinstance, issubclass and __bases__', f'''
{run('checks')}
{table(['Check', 'True when'], [
    ['isinstance(obj, C)', 'obj was made by C or by any child of C'],
    ['type(obj) is C', 'obj was made by exactly C (children do not count)'],
    ['issubclass(A, B)', 'A is B or a child (at any depth) of B'],
    ['C.__bases__', 'A tuple of the direct parents of C'],
    ['C.__mro__', 'The full search order, ending with object']])}
{note('Prefer isinstance over type(x) == C, because a child object is also a valid parent object. Every class inherits from object in the end, and bool is a child of int, which is why True + True is 2.', 'exam')}
''', kw=['isinstance', 'issubclass', 'type', '__bases__', '__mro__', 'object', 'bool is int'])

K.lesson('poly', 'Polymorphism and duck typing', f'''
{run('poly')}
{wwh('<b>Polymorphism</b> means one piece of code works with many types: make_noise(thing) calls thing.speak() without caring what thing is.',
     'Without it you would write if type is Dog ... elif type is Cat ... everywhere, and add a branch for every new type.',
     'Python does not check the type. It only looks up the method by name when the code runs. If the object has speak, it works. This is <b>duck typing</b>: if it walks like a duck and quacks like a duck, treat it as a duck.')}
{versus('Two kinds of polymorphism', ['', 'through inheritance', 'duck typing'], [
    ['Needs a shared parent', 'Yes', 'No'],
    ['Checked', 'When the code runs', 'When the code runs'],
    ['Error if a method is missing', 'NotImplementedError from the parent, or a TypeError from abc', 'AttributeError at the call'],
    ['Seen in', 'Frameworks: Django models, views', 'Everywhere: len, for loops, files, +']],
    'Python mostly relies on duck typing. Use a common parent when the classes really share code.')}
''', kw=['polymorphism', 'duck typing', 'dynamic dispatch', 'operator overloading', 'len'])

K.lesson('shapes', 'Abstract methods and a shape family', f'''
{run('shapes')}
{run('abstract')}
{versus('Making children write a method', ['', 'raise NotImplementedError', 'abc.ABC with @abstractmethod'], [
    ['When the mistake shows', 'Only when the missing method is called', 'As soon as you try to make the object'],
    ['Parent can be made', 'Yes', 'No'],
    ['Import needed', 'No', 'from abc import ABC, abstractmethod']],
    'abc finds the mistake earlier. Advanced 1.3 covers abstract base classes in depth.')}
''', kw=['abstract method', 'NotImplementedError', 'abc', 'ABC', 'abstractmethod', 'shape area', 'Heron formula'])

K.lesson('multi', 'Multiple inheritance and mixins', f'''
{run('multi')}
{note('A <b>mixin</b> is a small class that adds one ability (like to_json) and is not meant to be used alone. Django uses mixins a lot, for example LoginRequiredMixin on views. Put mixins first or last consistently and keep them free of __init__ when you can.', 'tip')}
''', kw=['multiple inheritance', 'mixin', 'JsonMixin', 'LoginRequiredMixin', '__bases__'])

K.lesson('mro', 'The MRO and the diamond problem', f'''
{viz('pymro')}
{run('diamond')}
{fxs(fx('C3 linearisation', 'L[C] = C + merge(L[B<sub>1</sub>], ..., L[B<sub>n</sub>], [B<sub>1</sub>, ..., B<sub>n</sub>])', 'B<sub>1</sub> ... B<sub>n</sub> are the parents of C in the order written.', key=True),
     fx('The merge rule', 'take the first head that is not in the tail of any list, remove it everywhere, repeat', 'If every head is in some tail, there is no valid order and Python raises TypeError.'))}
{steps('Rules every MRO keeps', [
    'A class comes before its parents.',
    'Parents keep the order you wrote them in: in D(B, C), B comes before C.',
    'Each class appears exactly once, so in the diamond A runs only once.',
    'object is always last.'])}
{run('mroerror')}
{note('super() does not mean "my parent". It means "the next class in the MRO of the object I am working on". Inside B, super().hello() went to C for a D object but to A for a B object. That is what lets every class in a diamond run exactly once.', 'exam')}
''', kw=['MRO', 'method resolution order', 'C3 linearisation', 'diamond problem', '__mro__', 'cooperative super', 'inconsistent MRO'])

K.lesson('compose', 'Composition compared with inheritance', f'''
{run('compose')}
{versus('Two ways to reuse code', ['', 'inheritance (is a)', 'composition (has a)'], [
    ['Example', 'class Dog(Animal)', 'self.engine = Engine(...)'],
    ['Link', 'Fixed when the class is written', 'Can be swapped while running'],
    ['Child gets', 'Every parent method, wanted or not', 'Only what you pass on'],
    ['Risk', 'A change in the parent can break children', 'More small methods that pass work on'],
    ['Use when', 'The child really is a kind of the parent', 'The object uses another object to do a job']],
    'the well known rule is "favour composition over inheritance". Inherit for real "is a" families, compose for everything else.')}
''', kw=['composition', 'has a', 'is a', 'delegation', 'favour composition over inheritance', 'subclass list'])

K.lesson('maths', 'The maths: areas, MROs and lookup cost', f'''
{fxs(fx('Circle', 'A = &pi;r<sup>2</sup>', 'Circle(2): 3.14159 &times; 4 = 12.57.', key=True),
     fx('Heron for a triangle', 's = (a + b + c) / 2, A = &radic;(s(s &minus; a)(s &minus; b)(s &minus; c))', 'Triangle(3, 4, 5): s = 6, A = &radic;(6 &times; 3 &times; 2 &times; 1) = 6.', key=True),
     fx('Total area by polymorphism', 'total = sum of shape.area() for every shape', '12.57 + 12 + 6 = 30.57, one loop for every kind of shape.'),
     fx('Length of an MRO', 'len(C.__mro__) = number of distinct ancestors + 1 (C itself), object included', 'Diamond D(B, C): D, B, C, A, object is 5.'),
     fx('Lookup cost', 'worst case one dict check per class in the MRO: O(len(MRO))', 'CPython caches the result per type, so repeated lookups are close to O(1).'))}
{steps('Worked example: the MRO of the diamond with C3', [
    'L[A] = [A, object]. L[B] = [B, A, object]. L[C] = [C, A, object].',
    'L[D] = D + merge([B, A, object], [C, A, object], [B, C]).',
    'Take B (in no tail). Next head A is in the tail of [C, A, object], so skip it and take C.',
    'Now A is free, then object.',
    eq('L[D] = [D, B, C, A, object]')])}
''', kw=['circle area', 'Heron formula', 'MRO length', 'C3 merge worked example', 'lookup cost'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>Write class Child(Parent): to reuse the parent, override a method by writing it again, and call super().__init__ in the child __init__.</p>',
    '<p>Use isinstance and issubclass, extend methods with super(), use polymorphism and duck typing, write abstract methods, and choose composition when "is a" does not fit.</p>',
    '<p>Explain multiple inheritance, mixins, the MRO and the C3 rules, why super() follows the MRO of the object, and why some class orders raise TypeError.</p>',
    '<p>C3 gives a linearisation that is monotonic (a class keeps the order of its parents in every child) and respects local precedence. super() is a proxy built from the type and the instance that searches the MRO after the given class. __init_subclass__ and metaclasses hook into class creation, and abc uses __subclasshook__ and register for virtual subclasses (Advanced 1.4).</p>')}
{grow('Make a child class, override a method and call super().',
      'Use isinstance, polymorphism, abstract methods, mixins and composition.',
      'Work out an MRO with C3 by hand and explain cooperative super() in a diamond.')}
''', kw=['beginner', 'expert', 'monotonic', '__init_subclass__', 'virtual subclass', 'register'])

lc(284, 'Peeking Iterator', 'peeking-iterator', 'm', 'Wrap an object and look one step ahead', 'Keep the next value in an attribute. peek returns it, next returns it and fetches a new one. This is composition: the class holds another object.', r'''
class ListIterator:
    # LeetCode gives you an iterator with hasNext() and next(). This small class plays that part.
    def __init__(self, nums):
        self.nums = nums
        self.i = 0

    def hasNext(self):
        return self.i < len(self.nums)

    def next(self):
        self.i += 1
        return self.nums[self.i - 1]


class PeekingIterator:
    def __init__(self, iterator):
        self.iterator = iterator
        self.has_ahead = iterator.hasNext()
        self.ahead = iterator.next() if self.has_ahead else None

    def peek(self):
        return self.ahead

    def next(self):
        value = self.ahead
        self.has_ahead = self.iterator.hasNext()
        self.ahead = self.iterator.next() if self.has_ahead else None
        return value

    def hasNext(self):
        return self.has_ahead
''', [('(lambda p: [p.next(), p.peek(), p.next(), p.next(), p.hasNext()])(PeekingIterator(ListIterator([1, 2, 3])))', [1, 2, 2, 3, False])])
lc(341, 'Flatten Nested List Iterator', 'flatten-nested-list-iterator', 'm', 'Flatten once with recursion', 'Walk the nested list with a recursive helper and store every integer in a plain list. Then next and hasNext only move an index.', r'''
class NestedInteger:
    # LeetCode gives you this class. Each one holds either one integer or a list of NestedInteger.
    def __init__(self, value):
        self.value = value

    def isInteger(self):
        return not isinstance(self.value, list)

    def getInteger(self):
        return self.value

    def getList(self):
        return self.value


class NestedIterator:
    def __init__(self, nestedList):
        self.values = []
        self.add_all(nestedList)
        self.i = 0

    def add_all(self, items):
        for item in items:
            if item.isInteger():
                self.values.append(item.getInteger())
            else:
                self.add_all(item.getList())

    def next(self):
        self.i += 1
        return self.values[self.i - 1]

    def hasNext(self):
        return self.i < len(self.values)


def build_nested(data):
    # turns [[1, 1], 2, [1, 1]] into NestedInteger objects for the tests
    if isinstance(data, list):
        return NestedInteger([build_nested(x) for x in data])
    return NestedInteger(data)


def drain(it):
    out = []
    while it.hasNext():
        out.append(it.next())
    return out
''', [('drain(NestedIterator(build_nested([[1, 1], 2, [1, 1]]).getList()))', [1, 1, 2, 1, 1]), ('drain(NestedIterator(build_nested([1, [4, [6]]]).getList()))', [1, 4, 6])])
lc(707, 'Design Linked List', 'design-linked-list', 'm', 'Node objects and a dummy head', 'Each node object holds a value and a link to the next node. A dummy node before the first one means adding at index 0 needs no special case.', r'''
class LinkedNode:
    def __init__(self, val, next_node=None):
        self.val = val
        self.next = next_node


class MyLinkedList:
    def __init__(self):
        self.dummy = LinkedNode(0)      # a fake node before the real first node
        self.size = 0

    def node_before(self, index):
        node = self.dummy
        for i in range(index):
            node = node.next
        return node

    def get(self, index):
        if index < 0 or index >= self.size:
            return -1
        return self.node_before(index).next.val

    def addAtHead(self, val):
        self.addAtIndex(0, val)

    def addAtTail(self, val):
        self.addAtIndex(self.size, val)

    def addAtIndex(self, index, val):
        if index < 0 or index > self.size:
            return
        before = self.node_before(index)
        before.next = LinkedNode(val, before.next)
        self.size += 1

    def deleteAtIndex(self, index):
        if index < 0 or index >= self.size:
            return
        before = self.node_before(index)
        before.next = before.next.next
        self.size -= 1
''', [('(lambda m: [m.addAtHead(1), m.addAtTail(3), m.addAtIndex(1, 2), m.get(1), m.deleteAtIndex(1), m.get(1)])(MyLinkedList())', [None, None, None, 2, None, 3])])
lc(208, 'Implement Trie (Prefix Tree)', 'implement-trie-prefix-tree', 'm', 'A tree of node objects', 'Each node has a dict of children, one per next letter, and a flag that marks the end of a word.', r'''
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_word = False


class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        node = self.root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]
        node.is_word = True

    def find(self, text):
        node = self.root
        for ch in text:
            if ch not in node.children:
                return None
            node = node.children[ch]
        return node

    def search(self, word):
        node = self.find(word)
        return node is not None and node.is_word

    def startsWith(self, prefix):
        return self.find(prefix) is not None
''', [('(lambda t: [t.insert("apple"), t.search("apple"), t.search("app"), t.startsWith("app"), t.insert("app"), t.search("app")])(Trie())', [None, True, False, True, None, True])])
lc(641, 'Design Circular Deque', 'design-circular-deque', 'm', 'Fixed list with a moving front', 'Like the circular queue, but the front can also move back by one: (front &minus; 1) % k.', r'''
class MyCircularDeque:
    def __init__(self, k):
        self.data = [0] * k
        self.k = k
        self.front = 0
        self.count = 0

    def insertFront(self, value):
        if self.isFull():
            return False
        self.front = (self.front - 1) % self.k
        self.data[self.front] = value
        self.count += 1
        return True

    def insertLast(self, value):
        if self.isFull():
            return False
        self.data[(self.front + self.count) % self.k] = value
        self.count += 1
        return True

    def deleteFront(self):
        if self.isEmpty():
            return False
        self.front = (self.front + 1) % self.k
        self.count -= 1
        return True

    def deleteLast(self):
        if self.isEmpty():
            return False
        self.count -= 1
        return True

    def getFront(self):
        if self.isEmpty():
            return -1
        return self.data[self.front]

    def getRear(self):
        if self.isEmpty():
            return -1
        return self.data[(self.front + self.count - 1) % self.k]

    def isEmpty(self):
        return self.count == 0

    def isFull(self):
        return self.count == self.k
''', [('(lambda d: [d.insertLast(1), d.insertLast(2), d.insertFront(3), d.insertFront(4), d.getRear(), d.isFull(), d.deleteLast(), d.insertFront(4), d.getFront()])(MyCircularDeque(3))', [True, True, True, False, 2, True, True, True, 4])])
lc(933, 'Number of Recent Calls', 'number-of-recent-calls', 'e', 'A queue of times', 'Add each new time to the back. Remove times from the front that are older than t &minus; 3000. The length is the answer.', r'''
from collections import deque


class RecentCounter:
    def __init__(self):
        self.times = deque()

    def ping(self, t):
        self.times.append(t)
        while self.times[0] < t - 3000:
            self.times.popleft()
        return len(self.times)
''', [('(lambda r: [r.ping(1), r.ping(100), r.ping(3001), r.ping(3002)])(RecentCounter())', [1, 2, 3, 3])])
lc(901, 'Online Stock Span', 'online-stock-span', 'm', 'Stack of price and span pairs', 'Keep a stack of [price, span]. While the top price is not bigger than today, pop it and add its span to today.', r'''
class StockSpanner:
    def __init__(self):
        self.stack = []        # pairs [price, span], prices going down

    def next(self, price):
        span = 1
        while self.stack and self.stack[-1][0] <= price:
            span += self.stack.pop()[1]
        self.stack.append([price, span])
        return span
''', [('(lambda s: [s.next(p) for p in [100, 80, 60, 70, 60, 75, 85]])(StockSpanner())', [1, 1, 1, 2, 1, 4, 6])])
lc(1352, 'Product of the Last K Numbers', 'product-of-the-last-k-numbers', 'm', 'Prefix products, reset at zero', 'Keep running products. The product of the last k is last / products[&minus;k &minus; 1]. A zero clears the list, and asking past it gives 0.', r'''
class ProductOfNumbers:
    def __init__(self):
        self.products = [1]

    def add(self, num):
        if num == 0:
            self.products = [1]
        else:
            self.products.append(self.products[-1] * num)

    def getProduct(self, k):
        if k >= len(self.products):
            return 0
        return self.products[-1] // self.products[-k - 1]
''', [('(lambda p: [p.add(3), p.add(0), p.add(2), p.add(5), p.add(4), p.getProduct(2), p.getProduct(3), p.getProduct(4), p.add(8), p.getProduct(2)])(ProductOfNumbers())', [None, None, None, None, None, 20, 40, 0, None, 32])])
lc(2241, 'Design an ATM Machine', 'design-an-atm-machine', 'm', 'Greedy from the biggest note', 'Store how many of each note there are. To withdraw, take as many big notes as possible, then smaller ones. If money is left over, refuse and change nothing.', r'''
class ATM:
    def __init__(self):
        self.values = [20, 50, 100, 200, 500]
        self.counts = [0, 0, 0, 0, 0]

    def deposit(self, banknotesCount):
        for i in range(5):
            self.counts[i] += banknotesCount[i]

    def withdraw(self, amount):
        take = [0, 0, 0, 0, 0]
        for i in range(4, -1, -1):
            take[i] = min(self.counts[i], amount // self.values[i])
            amount -= take[i] * self.values[i]
        if amount != 0:
            return [-1]
        for i in range(5):
            self.counts[i] -= take[i]
        return take
''', [('(lambda a: [a.deposit([0, 0, 1, 2, 1]), a.withdraw(600), a.deposit([0, 1, 0, 1, 1]), a.withdraw(600), a.withdraw(550)])(ATM())', [None, [0, 0, 1, 0, 1], None, [-1], [0, 1, 0, 0, 1]])])
lc(1396, 'Design Underground System', 'design-underground-system', 'm', 'Two dicts', 'One dict remembers where and when each card checked in. Another adds up total time and trip count for each pair of stations.', r'''
class UndergroundSystem:
    def __init__(self):
        self.inside = {}       # card id: (station, time)
        self.trips = {}        # (start, end): [total time, count]

    def checkIn(self, id, stationName, t):
        self.inside[id] = (stationName, t)

    def checkOut(self, id, stationName, t):
        start, t0 = self.inside.pop(id)
        key = (start, stationName)
        if key not in self.trips:
            self.trips[key] = [0, 0]
        self.trips[key][0] += t - t0
        self.trips[key][1] += 1

    def getAverageTime(self, startStation, endStation):
        total, count = self.trips[(startStation, endStation)]
        return total / count
''', [('(lambda u: [u.checkIn(45, "Leyton", 3), u.checkIn(32, "Paradise", 8), u.checkIn(27, "Leyton", 10), u.checkOut(45, "Waterloo", 15), u.checkOut(27, "Waterloo", 20), u.checkOut(32, "Cambridge", 22), u.getAverageTime("Paradise", "Cambridge"), u.getAverageTime("Leyton", "Waterloo")])(UndergroundSystem())',
       [None, None, None, None, None, None, 14.0, 11.0])])

K.lesson('leetcode', 'LeetCode practice', leet('<p>These design problems build classes that hold other objects: an iterator inside a wrapper, node objects inside a linked list or a trie, and queues and stacks inside counters. That is composition, the partner of inheritance.</p>'), kw=['LeetCode', 'design problems', 'iterator', 'linked list', 'trie', 'composition'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'class Child(Parent): gives Child every attribute and method of Parent. Every class inherits from object in the end.',
    'Writing a method again in the child <b>overrides</b> it. Python looks in the object, then the class, then the parents in MRO order.',
    'super().__init__(...) runs the parent setup. A child __init__ without it skips the parent attributes. super().m() extends a method.',
    'isinstance(obj, C) counts children, type(obj) is C does not. issubclass, __bases__ and __mro__ show the family.',
    'Polymorphism: one call, many types. Duck typing needs only the right method name, not a shared parent.',
    'Abstract methods: raise NotImplementedError, or abc.ABC with @abstractmethod which blocks making the object.',
    'Multiple inheritance uses the C3 MRO: children before parents, parents in written order, each class once, object last. Impossible orders raise TypeError.',
    'Prefer composition (has a) to inheritance (is a) unless the child really is a kind of the parent.'],
    'Step 7 is a full practice exam in the style of PCEP and PCAP, covering everything in the core part.')}
{files('Three tasks: a shape family with an abstract area, an Employee and Manager pair that uses super(), and a ReprMixin that any class can use.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'Which line makes Dog a child of Animal?', ['class Dog extends Animal:', 'class Dog(Animal):', 'class Dog: Animal', 'class Animal(Dog):'], 1, 'Parent in brackets.', 'The parent class goes in brackets after the child name.')
K.quiz('e', 'A child class defines speak(), which the parent also has. This is called', ['overloading', 'overriding', 'hiding the class', 'an error'], 1, 'Replace.', 'The child version overrides the parent one for child objects.')
K.quiz('e', 'What does super().__init__(name) do inside a child __init__?', ['Makes a new parent object', 'Runs the parent __init__ on the same object', 'Deletes the parent', 'Calls the child again'], 1, 'Parent setup.', 'It runs the parent setup code on self.')
K.quiz('m', 'class Dog(Animal), rex = Dog(). What is type(rex) == Animal?', ['True', 'False', 'TypeError', 'None'], 1, 'Exact type.', 'type gives exactly Dog. isinstance(rex, Animal) would be True.')
K.quiz('m', 'What is issubclass(bool, int)?', ['True', 'False', 'TypeError', 'Only in Python 2'], 0, 'True + True.', 'bool is a child class of int, so True behaves like 1.')
K.quiz('m', 'A child __init__ does not call super().__init__. The parent __init__ sets self.name. What does child_obj.name do?', ['Returns None', 'Raises AttributeError', 'Returns ""', 'Calls the parent'], 1, 'Never set.', 'The parent __init__ never ran, so name was never created.')
K.quiz('m', 'The classes are A, B(A), C(A) and D(B, C). What is D.__mro__?', ['D, B, A, C, object', 'D, B, C, A, object', 'D, C, B, A, object', 'D, A, B, C, object'], 1, 'Parents before grandparents.', 'C3 puts B and C before their shared parent A.')
K.quiz('m', 'Which class do all classes inherit from in the end?', ['type', 'object', 'base', 'class'], 1, 'The root.', 'object is at the end of every MRO.')
K.quiz('h', 'A.f returns "A". B(A).f returns "B" + super().f(). C(B) has no f. What is C().f()?', ['"A"', '"BA"', '"CBA"', 'AttributeError'], 1, 'Found on B.', 'C inherits f from B, and super() in B leads to A.')
K.quiz('h', 'The classes are X, Y, A(X, Y) and B(Y, X). Then class C(A, B) is written. What happens?', ['C is made with MRO C, A, B, X, Y, object', 'TypeError: Cannot create a consistent method resolution order', 'C is made with MRO C, A, X, B, Y, object', 'A warning only'], 1, 'Opposite promises.', 'A wants X before Y and B wants Y before X. No order keeps both, so class creation fails.')
K.quiz('h', 'What does duck typing mean?', ['Type hints are required', 'Any object with the needed methods works, whatever its class', 'Only classes that inherit from Duck', 'Checking type() before every call'], 1, 'Quacks like a duck.', 'Python only looks for the method by name when the call runs.')
K.quiz('x', 'In the style of a Cambridge Part IB question: in the diamond A, B(A), C(A) and D(B, C), every hello() calls super().hello(). When D().hello() runs the B version, where does super().hello() inside B go?', ['A, because A is the parent of B', 'C, the next class in the MRO of D', 'object', 'B again'], 1, 'super follows the MRO of the object.', 'The object is a D, whose MRO is D, B, C, A, object. The class after B is C.')
K.quiz('x', 'In the style of a CMU 17-214 software design exam: class Stack(list) adds push. Users can still call insert(0, x) and break the stack rule. Which design fixes this?', ['Override insert to do nothing', 'Composition: Stack keeps a list in self.items and offers only push and pop', 'Add more mixins', 'Make Stack inherit from tuple'], 1, 'Has a, not is a.', 'With composition the stack shows only the methods you choose. A stack is not really a kind of list.')

K.calc('e', 'Square(4).area() where area returns side squared.', '16', '4 times 4.', ['side = 4.', 'area = 4<sup>2</sup>.', eq('16')], check=16)
K.calc('e', 'The classes are A, B(A), C(A) and D(B, C). What is len(D.__mro__)?', '5', 'Count object too.', ['D.__mro__ is D, B, C, A, object.', 'Count them.', eq('5')], check=5)
K.calc('e', 'Employee.pay() returns salary // 12. Manager.pay() returns super().pay() + bonus. What is Manager("Asha", 2400, 100).pay()?', '300', 'Parent part plus bonus.', ['2400 // 12 = 200.', 'Add the bonus 100.', eq('300')], check=2400 // 12 + 100)
K.calc('m', 'Circle(2).area() with &pi;r<sup>2</sup>, rounded to 2 decimal places.', '12.57', '&pi; &times; 4.', ['r<sup>2</sup> = 4.', '3.14159 &times; 4 = 12.566.', eq('12.57')], check=round(math.pi * 4, 2))
K.calc('m', 'Triangle(3, 4, 5).area() with Heron\'s formula.', '6', 's = 6.', ['s = (3 + 4 + 5) / 2 = 6.', '6 &times; 3 &times; 2 &times; 1 = 36.', eq('&radic;36 = 6')], check=int(math.sqrt(6 * 3 * 2 * 1)))
K.calc('m', 'object, then A(object), B(A), C(B). A method is defined only on A. How many classes does Python search to find it from a C object?', '3', 'C, then B, then A.', ['Not on C.', 'Not on B.', eq('Found on A, the 3rd class searched')], check=3)
K.calc('m', 'Total area of [Square(2), Rectangle(3, 4), Square(1)].', '17', 'Add each area.', ['4 + 12 + 1.', 'One loop calls area() on each.', eq('17')], check=4 + 12 + 1)
K.calc('h', 'The classes are O, then A, B, C, D and E (each a child of O), then K1(A, B, C), K2(D, B, E), K3(D, A) and Z(K1, K2, K3). At which index (from 0) is D in Z.__mro__?', '4', 'Z, K1, K2, K3 come first.', ['Z.__mro__ = Z, K1, K2, K3, D, A, B, C, E, O, object.', 'Count from 0.', eq('D is at index 4')], check=4)
K.calc('h', 'How many classes are in Z.__mro__ for the same example (object included)?', '11', 'Z, its 3 parents, 6 more, object.', ['Z, K1, K2, K3.', 'D, A, B, C, E, O.', eq('4 + 6 + 1 = 11')], check=11)
K.calc('x', 'In the style of an Oxford Mathematical Institute problem: area of Triangle(13, 14, 15) using Heron\'s formula.', '84', 's = 21.', ['s = 42 / 2 = 21.', '21 &times; 8 &times; 7 &times; 6 = 7,056.', eq('&radic;7,056 = 84')], check=int(math.sqrt(21 * 8 * 7 * 6)))

RAISES = '''

def raises(func, *args):
    """Test helper: the name of the exception func(*args) raises, or None."""
    try:
        func(*args)
    except Exception as err:
        return type(err).__name__
    return None
'''

K.assign('shapes', 'e', 'A shape family',
         '<p>The class <code>Shape</code> is given. Write <code>Square(side)</code> and <code>Rectangle(w, h)</code> as children of Shape, each with its own <code>area()</code>. Do not write describe again: it is inherited. raises() is a test helper.</p>',
         '''
class Shape:
    def area(self):
        raise NotImplementedError("each shape must define area()")

    def describe(self):
        return type(self).__name__ + " with area " + str(self.area())


class Square:
    # your code here
    pass


class Rectangle:
    # your code here
    pass
''' + RAISES, [('Square(3).area()', 9), ('Rectangle(2, 5).describe()', 'Rectangle with area 10'), ('isinstance(Square(1), Shape)', True), ('raises(Shape().area)', 'NotImplementedError'), ('Square(2).describe()', 'Square with area 4')],
         '''
class Shape:
    def area(self):
        raise NotImplementedError("each shape must define area()")

    def describe(self):
        return type(self).__name__ + " with area " + str(self.area())


class Square(Shape):
    def __init__(self, side):
        self.side = side

    def area(self):
        return self.side * self.side


class Rectangle(Shape):
    def __init__(self, w, h):
        self.w = w
        self.h = h

    def area(self):
        return self.w * self.h
''' + RAISES, 'Write class Square(Shape): with __init__ and area. describe comes from Shape and calls your area.', '<p>describe was written once in Shape, yet it prints the right name and area for every child. That is inheritance and polymorphism working together.</p>')
K.assign('manager', 'm', 'Employee and Manager with super()',
         '<p>Employee is given. Write <code>Manager(name, salary, bonus)</code> as a child of Employee. Its <code>__init__</code> must use <code>super()</code> to set name and salary, and store bonus. Its <code>pay()</code> must return the Employee pay plus the bonus, using <code>super().pay()</code>.</p>',
         '''
class Employee:
    def __init__(self, name, salary):
        self.name = name
        self.salary = salary

    def pay(self):
        return self.salary // 12


class Manager(Employee):
    def __init__(self, name, salary, bonus):
        # your code here
        pass
''', [('Manager("Asha", 1200, 50).pay()', 150), ('Manager("Asha", 1200, 50).name', 'Asha'), ('Employee("Ravi", 1200).pay()', 100), ('isinstance(Manager("A", 12, 1), Employee)', True), ('Manager("B", 2400, 0).pay()', 200)],
         '''
class Employee:
    def __init__(self, name, salary):
        self.name = name
        self.salary = salary

    def pay(self):
        return self.salary // 12


class Manager(Employee):
    def __init__(self, name, salary, bonus):
        super().__init__(name, salary)
        self.bonus = bonus

    def pay(self):
        return super().pay() + self.bonus
''', 'First line of __init__: super().__init__(name, salary). Then self.bonus = bonus. In pay, return super().pay() + self.bonus.', '<p>If the monthly pay rule in Employee ever changes, Manager follows it without any edit, because it never copied the rule.</p>')
K.assign('mixin', 'h', 'A ReprMixin',
         '<p>Write a mixin class <code>ReprMixin</code> with a <code>__repr__</code> that shows the class name and every instance attribute in the order they were set, like <code>Point(x=1, y=2)</code> or <code>Pet(name=\'Rex\')</code>. Use repr() for each value. Point and Pet are given and only inherit from the mixin.</p>',
         '''
class ReprMixin:
    def __repr__(self):
        # your code here
        pass


class Point(ReprMixin):
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Pet(ReprMixin):
    def __init__(self, name):
        self.name = name
''', [('repr(Point(1, 2))', 'Point(x=1, y=2)'), ('repr(Pet("Rex"))', "Pet(name='Rex')"), ('str([Point(0, 0)])', '[Point(x=0, y=0)]')],
         '''
class ReprMixin:
    def __repr__(self):
        parts = []
        for key in self.__dict__:
            parts.append(key + "=" + repr(self.__dict__[key]))
        return type(self).__name__ + "(" + ", ".join(parts) + ")"


class Point(ReprMixin):
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Pet(ReprMixin):
    def __init__(self, name):
        self.name = name
''', 'Loop over self.__dict__ (it keeps the order attributes were set). Use type(self).__name__ for the class name.', '<p>type(self) is the real class of the object (Point or Pet), not ReprMixin, so one mixin serves every class. dataclasses (Advanced 1.3) generate a __repr__ just like this.</p>')

K.must('Inherit and override', 'class Child(Parent): reuses Parent. Writing a method again overrides it. Lookup: object, class, then parents in MRO order, ending at object.')
K.must('super()', 'super().__init__(...) runs parent setup. super().m() extends a method. super() means the next class in the MRO of the object.')
K.must('Checks', 'isinstance counts children, type(x) is C does not. issubclass(bool, int) is True. __bases__ and __mro__ show the family.')
K.must('Polymorphism', 'One call works on many types. Duck typing needs only the method. Abstract methods: NotImplementedError or abc with @abstractmethod.')
K.must('MRO and composition', 'C3: child before parents, parents in written order, each once. Impossible order is TypeError. Prefer has a over is a.')

T = K.topic(
    slug='py-inheritance', topic='py-inheritance', step=(6, 'Object oriented programming', 'py-c6', 'Model things as objects with classes, attributes and methods, then reuse code with inheritance.', 'Intermediate'),
    title='Inheritance: super(), overriding, polymorphism and the MRO', short='Inheritance', badge='6.2', minutes=70,
    lead='Reuse classes. Learn single inheritance and overriding, super() for the parent setup and for extending methods, isinstance and issubclass, polymorphism and duck typing, abstract methods, multiple inheritance and mixins, the method resolution order with C3 and the diamond problem, and when composition is the better choice.',
    desc='inheritance, superclass and subclass, overriding, method lookup, super() and __init__ chaining, isinstance, issubclass, type, __bases__, __mro__, object, bool and int, polymorphism, duck typing, NotImplementedError, abc and abstractmethod, Heron area, multiple inheritance, mixins, the MRO and C3 linearisation, the diamond problem, inconsistent MRO, cooperative super, composition and delegation.',
    summary='inheritance, overriding, super(), isinstance, polymorphism, duck typing, abstract methods, mixins, MRO, composition.',
    keywords=['inheritance', 'subclass', 'override', 'super', 'isinstance', 'issubclass', 'polymorphism', 'duck typing', 'abstract', 'mixin', 'MRO', 'C3', 'diamond', 'composition', 'PCAP'],
    recap='<p>Inherit when the child really is a kind of the parent, call super() so every class in the family runs its part once, and let polymorphism replace long if chains over types.</p>',
    added='2026-11-07', leet=leet_items())
