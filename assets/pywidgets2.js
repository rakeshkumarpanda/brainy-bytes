/* ===== Complete Python animations, part 2: Advanced Python. See assets/pywidgets.js for the framework. ===== */

/* =====================================================================================================
   Advanced 1.1  how Python turns operators and built in functions into special (dunder) method calls
   ===================================================================================================== */
(() => {
  const { trace, head, codeView, consoleBox, D, box } = PYZ;
  /* each case: code lines and steps [line, chain entry, say, output] */
  const CASES = {
    add: {
      code: ['class Vector:', '    def __init__(self, x, y):', '        self.x, self.y = x, y', '    def __add__(self, other):', '        return Vector(self.x + other.x, self.y + other.y)', '    def __repr__(self):', '        return f"Vector({self.x}, {self.y})"', '', 'print(Vector(1, 2) + Vector(3, 4))'],
      steps: [
        [8, 'Vector(1, 2) + Vector(3, 4)', 'Python reads a + b. It has no idea how to add two Vectors, so it looks for a special method on the type of the LEFT object.', ''],
        [3, 'Vector.__add__(left, right)', 'Vector has __add__, so Python calls it with self = the left object and other = the right one.', ''],
        [4, 'returns Vector(1 + 3, 2 + 4)', '__add__ builds and returns a NEW Vector. Neither of the two original objects changes.', ''],
        [5, 'print uses __repr__ (no __str__)', 'print needs text. Vector has no __str__, so Python uses __repr__ instead.', 'Vector(4, 6)']]
    },
    radd: {
      code: ['class Vector:', '    def __init__(self, x, y):', '        self.x, self.y = x, y', '    def __mul__(self, k):', '        return Vector(self.x * k, self.y * k)', '    def __rmul__(self, k):', '        return self.__mul__(k)', '    def __repr__(self):', '        return f"Vector({self.x}, {self.y})"', 'print(2 * Vector(1, 2))'],
      steps: [
        [9, '2 * Vector(1, 2)', 'The left object is the int 2, so Python asks int first.', ''],
        [9, 'int.__mul__(2, v): NotImplemented', 'int does not know Vectors. Its __mul__ returns the special value NotImplemented, which means "I cannot do this, ask the other side".', ''],
        [5, 'Vector.__rmul__(v, 2)', 'Python now tries the <b>reflected</b> method of the right object: __rmul__ (r for right). self is the Vector, k is 2.', ''],
        [3, 'calls __mul__: Vector(2, 4)', '__rmul__ hands the work to __mul__, because 2 * v and v * 2 mean the same here.', ''],
        [9, 'print shows the repr', 'Without __rmul__, Python would raise TypeError: unsupported operand type(s) for *: \'int\' and \'Vector\'.', 'Vector(2, 4)']]
    },
    bool: {
      code: ['class Basket:', '    def __init__(self, items):', '        self.items = items', '    def __len__(self):', '        return len(self.items)', '', 'b = Basket([])', 'if b:', '    print("full")', 'else:', '    print("empty")'],
      steps: [
        [7, 'if b: needs bool(b)', 'An if needs True or False, so Python works out bool(b).', ''],
        [7, 'Basket.__bool__? not found', 'First Python looks for __bool__. Basket does not have one.', ''],
        [3, 'fallback: Basket.__len__(b) is 0', 'Then it tries __len__. A length of 0 counts as False, any other length as True.', ''],
        [10, 'bool(b) is False: else runs', 'With neither __bool__ nor __len__, every object would count as True.', 'empty']]
    },
    contains: {
      code: ['class Countdown:', '    def __init__(self, start):', '        self.start = start', '    def __iter__(self):', '        n = self.start', '        while n > 0:', '            yield n', '            n -= 1', '', 'print(3 in Countdown(5))'],
      steps: [
        [9, '3 in Countdown(5)', 'in asks the RIGHT object whether it contains the left one.', ''],
        [9, '__contains__? not found', 'Python first looks for __contains__. Countdown does not have one.', ''],
        [6, 'fallback __iter__: 5 == 3? no', 'So Python loops over the object with __iter__ and compares each item with ==. The first item is 5.', ''],
        [6, '4 == 3? no', 'The next item is 4.', ''],
        [6, '3 == 3? yes, stop', 'The third item matches, so the search stops at once. 2 and 1 are never made.', ''],
        [9, 'result True', 'Writing __contains__ yourself is faster when you can check without a loop, for example with a set.', 'True']]
    },
    eq: {
      code: ['class Money:', '    def __init__(self, amount):', '        self.amount = amount', '    def __eq__(self, other):', '        if not isinstance(other, Money):', '            return NotImplemented', '        return self.amount == other.amount', '', 'print(Money(5) == Money(5), Money(5) == 5)'],
      steps: [
        [8, 'Money(5) == Money(5)', 'The first comparison: == becomes Money.__eq__(left, right).', ''],
        [6, 'both Money: 5 == 5 is True', 'other is a Money, so the amounts are compared.', ''],
        [8, 'Money(5) == 5: Money.__eq__', 'The second comparison starts the same way.', ''],
        [5, 'not a Money: NotImplemented', 'Money cannot compare itself with an int, so it returns NotImplemented instead of guessing.', ''],
        [8, 'int.__eq__(5, m): NotImplemented', 'For == the reflected method is __eq__ of the right object. int does not know Money either.', ''],
        [8, 'both gave up: m is 5? False', 'When both sides return NotImplemented, == falls back to "is", so the answer is False (!= would give True).', 'True False']]
    },
    getitem: {
      code: ['class Deck:', '    def __init__(self):', '        self.cards = ["A", "K", "Q"]', '    def __len__(self):', '        return len(self.cards)', '    def __getitem__(self, i):', '        return self.cards[i]', '', 'deck = Deck()', 'print(deck[0], len(deck))', 'for card in deck:', '    print(card)'],
      steps: [
        [9, 'deck[0]: __getitem__(0) is "A"', 'Square brackets call __getitem__ with the index.', ''],
        [9, 'len(deck): __len__() is 3', 'len() calls __len__, which must return an int that is 0 or more.', 'A 3'],
        [10, 'for: no __iter__, __getitem__(0)', 'A for loop wants __iter__. Deck has none, so Python uses the old rule: call __getitem__ with 0, 1, 2 and so on.', 'A 3\nA'],
        [10, '__getitem__(1), then (2)', 'Each index gives the next card.', 'A 3\nA\nK\nQ'],
        [6, '__getitem__(3): IndexError, stop', 'IndexError is the signal that the sequence has ended, so the loop finishes quietly.', 'A 3\nA\nK\nQ']]
    }
  };
  trace('pydunder', {
    title: 'Operators become special method calls',
    sub: 'Pick an expression. Each step shows which special (dunder) method Python looks for, what it finds, and what it does when a method is missing or says NotImplemented.',
    W: 600, H: 340,
    params: [{ k: 'cs', label: 'Expression', type: 'select', v: 'add', opts: [['add', 'Vector(1, 2) + Vector(3, 4)'], ['radd', '2 * Vector(1, 2)'], ['bool', 'if Basket([]):'], ['contains', '3 in Countdown(5)'], ['eq', 'Money(5) == 5'], ['getitem', 'deck[0], len(deck), for']] }],
    tips: [
      { t: 'a + b calls type(a).__add__(a, b). The method returns a new object.', set: { cs: 'add' }, play: true },
      { t: 'When the left side returns NotImplemented, Python tries the reflected method of the right side.', set: { cs: 'radd' }, play: true },
      { t: 'in and for fall back to older protocols when the newer special method is missing.', set: { cs: 'contains' }, play: true }
    ],
    frames(p) {
      const C = CASES[p.cs];
      return C.steps.map((s, i) => ({ code: C.code, line: s[0], chain: C.steps.slice(0, i + 1).map(x => x[1]), say: s[2], out: s[3] }));
    },
    paint(z, f) {
      const c = z.col;
      head(z, 'Program', 16, 18);
      codeView(z, f.code, f.line, 16, 26, 286, { s: 11, lh: 18 });
      head(z, 'What Python does', 316, 18);
      f.chain.forEach((t, i) => {
        const last = i === f.chain.length - 1;
        box(z, 316, 28 + i * 40, 268, 32, t, { mono: true, s: 11.5, fill: last ? (c.dark ? '#14321f' : '#dcfce7') : c.surf, stroke: last ? c.green : c.line });
        if (i) D.text(z.g, String(i + 1), 311, 48 + i * 40, { a: 'right', s: 10, c: c.ink2 });
      });
      if (f.out) consoleBox(z, f.out, 16, 262, 286, 70, { title: 'Output' });
    }
  });
})();

/* =====================================================================================================
   Advanced 1.2  decorators: what happens when the def runs and what happens at each call
   ===================================================================================================== */
(() => {
  const { trace, head, codeView, consoleBox, D, box } = PYZ;
  const CODE = {
    simple: ['def shout(func):', '    def wrapper(*args, **kwargs):', '        print("calling", func.__name__)', '        result = func(*args, **kwargs)', '        return result', '    return wrapper', '', '@shout', 'def add(a, b):', '    return a + b', '', 'print(add(2, 3))'],
    stack: ['def bold(f):', '    return lambda: "**" + f() + "**"', 'def italic(f):', '    return lambda: "_" + f() + "_"', '', '@bold', '@italic', 'def hi():', '    return "hi"', '', 'print(hi())'],
    factory: ['def repeat(times):', '    def decorate(func):', '        def wrapper(*args):', '            for i in range(times):', '                func(*args)', '        return wrapper', '    return decorate', '', '@repeat(3)', 'def wave(name):', '    print("hi", name)', '', 'wave("Asha")']
  };
  /* [line, names [[name, points to, remembers]], stack, out, say] */
  const S = {
    simple: [
      [0, [['shout', 'function shout', '']], [], '', 'def shout runs. It only creates a function object and names it shout. Nothing inside it runs yet.'],
      [8, [['shout', 'function shout', ''], ['(no name yet)', 'function add', '']], [], '', 'def add runs and makes a function object. Because of @shout, Python does NOT name it add yet. It first hands it to the decorator.'],
      [1, [['shout', 'function shout', ''], ['(no name yet)', 'function add', ''], ['wrapper', 'function wrapper', 'func = add']], ['shout(add)'], '', 'shout(func) runs with func = the original add. It defines wrapper, a closure that remembers func.'],
      [7, [['shout', 'function shout', ''], ['add', 'function wrapper', 'func = original add']], [], '', 'shout returns wrapper, and Python binds the name add to it. @shout above def add is the same as add = shout(add). The original add is now reachable only through the closure.'],
      [11, [['shout', 'function shout', ''], ['add', 'function wrapper', 'func = original add']], ['wrapper(2, 3)'], '', 'add(2, 3) really calls wrapper. *args collects (2, 3) and **kwargs is {}.'],
      [2, [['shout', 'function shout', ''], ['add', 'function wrapper', 'func = original add']], ['wrapper(2, 3)'], 'calling add', 'wrapper does its extra work first: it prints the name of the function it wraps.'],
      [3, [['shout', 'function shout', ''], ['add', 'function wrapper', 'func = original add']], ['wrapper(2, 3)', 'original add(2, 3)'], 'calling add', 'Then it calls the original function with the same arguments.'],
      [9, [['shout', 'function shout', ''], ['add', 'function wrapper', 'func = original add']], ['wrapper(2, 3)'], 'calling add', 'The original add returns 5 to wrapper.'],
      [4, [['shout', 'function shout', ''], ['add', 'function wrapper', 'func = original add']], [], 'calling add\n5', 'wrapper returns 5 to the caller and print shows it. The caller never knew a wrapper was in the way.']],
    stack: [
      [7, [['bold', 'function bold', ''], ['italic', 'function italic', ''], ['(no name yet)', 'function hi', '']], [], '', 'def hi makes the function. There are two decorators, and the one NEAREST the def is applied first.'],
      [3, [['bold', 'function bold', ''], ['italic', 'function italic', ''], ['(no name yet)', 'lambda from italic', 'f = original hi']], ['italic(hi)'], '', 'italic(hi) returns a lambda that adds _ around whatever f() gives.'],
      [1, [['bold', 'function bold', ''], ['italic', 'function italic', ''], ['hi', 'lambda from bold', 'f = italic lambda']], ['bold(...)'], '', 'bold gets the italic lambda and wraps it again. So hi = bold(italic(hi)).'],
      [10, [['bold', 'function bold', ''], ['italic', 'function italic', ''], ['hi', 'lambda from bold', 'f = italic lambda']], ['bold lambda'], '', 'hi() runs the outer (bold) lambda first.'],
      [3, [['bold', 'function bold', ''], ['italic', 'function italic', ''], ['hi', 'lambda from bold', 'f = italic lambda']], ['bold lambda', 'italic lambda'], '', 'It calls its f, the italic lambda.'],
      [8, [['bold', 'function bold', ''], ['italic', 'function italic', ''], ['hi', 'lambda from bold', 'f = italic lambda']], ['bold lambda', 'italic lambda', 'original hi'], '', 'Which calls the original hi, which returns "hi".'],
      [3, [['bold', 'function bold', ''], ['italic', 'function italic', ''], ['hi', 'lambda from bold', 'f = italic lambda']], ['bold lambda'], '', 'italic adds _ on both sides: "_hi_".'],
      [10, [['bold', 'function bold', ''], ['italic', 'function italic', ''], ['hi', 'lambda from bold', 'f = italic lambda']], [], '**_hi_**', 'bold adds ** around that. Applied bottom up, run top down: the top decorator is the outermost layer.']],
    factory: [
      [0, [['repeat', 'function repeat', '']], [], '', 'def repeat makes a function that will BUILD decorators.'],
      [8, [['repeat', 'function repeat', ''], ['(temporary)', 'function decorate', 'times = 3']], ['repeat(3)'], '', '@repeat(3) has brackets, so repeat(3) is called first. It returns decorate, a closure that remembers times = 3.'],
      [9, [['repeat', 'function repeat', ''], ['(temporary)', 'function decorate', 'times = 3'], ['(no name yet)', 'function wave', '']], [], '', 'def wave makes the function, which is passed to decorate.'],
      [2, [['repeat', 'function repeat', ''], ['wave', 'function wrapper', 'times = 3, func = wave']], ['decorate(wave)'], '', 'decorate returns wrapper, which remembers both times and func. The name wave now points to wrapper. So @repeat(3) means wave = repeat(3)(wave).'],
      [12, [['repeat', 'function repeat', ''], ['wave', 'function wrapper', 'times = 3, func = wave']], ['wrapper("Asha")'], '', 'wave("Asha") calls wrapper with args = ("Asha",).'],
      [4, [['repeat', 'function repeat', ''], ['wave', 'function wrapper', 'times = 3, func = wave']], ['wrapper("Asha")', 'original wave'], 'hi Asha', 'Loop turn 1: the original wave prints.'],
      [4, [['repeat', 'function repeat', ''], ['wave', 'function wrapper', 'times = 3, func = wave']], ['wrapper("Asha")', 'original wave'], 'hi Asha\nhi Asha', 'Loop turn 2.'],
      [4, [['repeat', 'function repeat', ''], ['wave', 'function wrapper', 'times = 3, func = wave']], [], 'hi Asha\nhi Asha\nhi Asha', 'Loop turn 3, then wrapper returns None. A decorator with arguments has three levels: the factory, the decorator and the wrapper.']]
  };
  trace('pydeco', {
    title: 'How a decorator wraps a function',
    sub: 'Pick a program. The Names panel shows which function object each name points to and what each closure remembers. The Call stack shows who is running.',
    W: 600, H: 340,
    params: [{ k: 'prog', label: 'Program', type: 'select', v: 'simple', opts: [['simple', 'A simple decorator'], ['stack', 'Two stacked decorators'], ['factory', 'A decorator with arguments']] }],
    tips: [
      { t: '@shout above def add means add = shout(add). The name ends up pointing to the wrapper.', set: { prog: 'simple' }, play: true },
      { t: 'Stacked decorators are applied from the bottom up, and the top one runs first at call time.', set: { prog: 'stack' }, play: true },
      { t: '@repeat(3) calls repeat(3) first, and what it returns is the real decorator.', set: { prog: 'factory' }, play: true }
    ],
    frames(p) { return S[p.prog].map(s => ({ code: CODE[p.prog], line: s[0], names: s[1], stack: s[2], out: s[3], say: s[4] })); },
    paint(z, f) {
      const c = z.col;
      head(z, 'Program', 16, 18);
      codeView(z, f.code, f.line, 16, 26, 270, { s: 11, lh: 17 });
      head(z, 'Names', 300, 18);
      f.names.forEach((n, i) => {
        const y = 28 + i * 40;
        box(z, 300, y, 92, 34, n[0], { mono: true, s: 11, b: true, fill: c.surf, stroke: c.cv });
        D.line(z.g, 392, y + 17, 404, y + 17, c.ink2, 1.4);
        box(z, 404, y, 180, 34, '', { fill: n[2] ? (c.dark ? '#2a1f0b' : '#fff7ed') : c.surf, stroke: n[2] ? c.orange : c.line });
        D.text(z.g, n[1], 494, n[2] ? y + 14 : y + 21, { a: 'center', s: PYZ.fit(z.g, n[1], 170, 11.5, { mono: true }), mono: true, c: c.ink });
        if (n[2]) D.text(z.g, 'remembers ' + n[2], 494, y + 28, { a: 'center', s: PYZ.fit(z.g, 'remembers ' + n[2], 170, 10.5, { mono: true }), mono: true, c: c.orange });
      });
      head(z, 'Call stack (top is running)', 300, 182);
      if (!f.stack.length) D.text(z.g, '(nothing running)', 300, 204, { s: 11, c: c.ink2 });
      f.stack.slice().reverse().forEach((s, i) => box(z, 300, 192 + i * 30, 284, 24, s, { mono: true, s: 11, fill: i === 0 ? (c.dark ? '#14321f' : '#dcfce7') : c.surf, stroke: i === 0 ? c.green : c.line }));
      if (f.out) consoleBox(z, f.out, 16, 262, 270, 72, { title: 'Output' });
    }
  });
})();

/* =====================================================================================================
   Advanced 1.3  instance, class and static methods, and properties: what Python passes and where data goes
   ===================================================================================================== */
(() => {
  const { trace, head, codeView, consoleBox, D, box } = PYZ;
  const CODE = {
    kinds: ['class Pizza:', '    sizes = {"S": 20, "M": 25, "L": 30}', '    def __init__(self, cm):', '        self.cm = cm', '    def area(self):', '        return round(3.14 * (self.cm / 2) ** 2)', '    @classmethod', '    def from_code(cls, code):', '        return cls(cls.sizes[code])', '    @staticmethod', '    def is_valid(cm):', '        return 15 <= cm <= 40', 'p = Pizza.from_code("M")', 'print(p.area(), Pizza.is_valid(50))'],
    prop: ['class Temperature:', '    def __init__(self, c):', '        self.celsius = c', '    @property', '    def celsius(self):', '        return self._c', '    @celsius.setter', '    def celsius(self, value):', '        if value < -273.15:', '            raise ValueError("too cold")', '        self._c = value', '    @property', '    def fahrenheit(self):', '        return self._c * 9 / 5 + 32', 't = Temperature(25)', 't.fahrenheit', 't.celsius = -300', 't.fahrenheit = 0']
  };
  /* [line, call, first argument, instance dict, out, say] */
  const S = {
    kinds: [
      [12, 'Pizza.from_code("M")', 'cls = Pizza', '', '', 'from_code is a <b>class method</b>. Called on the class, Python passes the class itself as the first argument, named cls.'],
      [8, 'cls.sizes["M"] is 25, then cls(25)', 'cls = Pizza', '', '', 'cls(25) is the same as Pizza(25). Because it uses cls and not the name Pizza, a child class calling from_code would get a child object. This is an <b>alternative constructor</b>.'],
      [3, 'Pizza.__init__(new object, 25)', 'self = the new pizza', "'cm': 25", '', '__init__ is a normal <b>instance method</b>: its first argument is the object, self.'],
      [12, 'p = the new Pizza', '', "'cm': 25", '', 'The class method returns the finished object, which is named p.'],
      [5, 'p.area() is Pizza.area(p)', 'self = p', "'cm': 25", '', 'Calling a method on an object passes the object as self, so the method can read self.cm.'],
      [11, 'Pizza.is_valid(50)', '(nothing extra)', "'cm': 25", '', 'is_valid is a <b>static method</b>: Python passes no self and no cls. It is a plain function that lives in the class because it belongs to the topic.'],
      [13, 'print the results', '', "'cm': 25", '491 False', '3.14 &times; 12.5<sup>2</sup> rounds to 491, and 50 is not between 15 and 40.']],
    prop: [
      [14, 'Temperature(25) runs __init__', 'self = t', '', '', 'A new object is made and __init__ runs.'],
      [2, 'self.celsius = 25 goes to the SETTER', 'value = 25', '', '', 'celsius is a property, so even inside __init__ the assignment calls the setter method instead of storing directly.'],
      [10, 'the setter checks, then self._c = 25', 'value = 25', "'_c': 25", '', '25 is fine, so the real value is stored under _c. The instance dict holds _c, not celsius.'],
      [15, 't.fahrenheit calls the GETTER', 'self = t', "'_c': 25", '', 'Reading a property runs its getter. fahrenheit is computed every time from _c: 25 &times; 9 / 5 + 32 = 77.0.'],
      [16, 't.celsius = -300 calls the setter', 'value = -300', "'_c': 25", '', 'Assignment goes through the setter again.'],
      [9, 'raise ValueError("too cold")', 'value = -300', "'_c': 25", 'ValueError: too cold', 'The check fails, so nothing is stored. The object can never hold an impossible temperature.'],
      [17, 't.fahrenheit = 0: no setter', '', "'_c': 25", "ValueError: too cold\nAttributeError: property 'fahrenheit' of 'Temperature' object has no setter", 'fahrenheit has only a getter, so it is <b>read only</b>. Python raises AttributeError.']]
  };
  trace('pymethods', {
    title: 'Method kinds and properties',
    sub: 'Pick a program. Each step shows the call Python really makes, what it passes as the first argument, and what is stored in the object.',
    W: 600, H: 360,
    params: [{ k: 'prog', label: 'Program', type: 'select', v: 'kinds', opts: [['kinds', 'Instance, class and static methods'], ['prop', 'A property with a setter']] }],
    tips: [
      { t: 'self is the object, cls is the class, and a static method gets neither.', set: { prog: 'kinds' }, play: true },
      { t: 'A property turns attribute reads and writes into method calls, so checks always run.', set: { prog: 'prop' }, play: true }
    ],
    frames(p) { return S[p.prog].map(s => ({ code: CODE[p.prog], line: s[0], call: s[1], arg: s[2], dict: s[3], out: s[4], say: s[5] })); },
    paint(z, f) {
      const c = z.col;
      head(z, 'Program', 16, 18);
      codeView(z, f.code, f.line, 16, 26, 300, { s: 10.5, lh: 17 });
      head(z, 'Python really does', 332, 18);
      box(z, 332, 28, 252, 40, f.call, { mono: true, s: 11.5, fill: c.dark ? '#14321f' : '#dcfce7', stroke: c.green });
      head(z, 'First argument', 332, 92);
      box(z, 332, 100, 252, 32, f.arg || '(none)', { mono: true, s: 12, b: true, stroke: c.cv });
      head(z, 'Inside the object (its __dict__)', 332, 156);
      box(z, 332, 164, 252, 32, f.dict ? '{' + f.dict + '}' : '{}', { mono: true, s: 12, stroke: c.orange });
      if (f.out) consoleBox(z, f.out, 332, 216, 252, 120, { title: 'Output', err: /Error/.test(f.out.split('\n').pop()) });
    }
  });
})();

/* =====================================================================================================
   Advanced 1.4  assignment, shallow copy and deep copy: which objects are shared
   ===================================================================================================== */
(() => {
  const { trace, head, codeView, consoleBox, D, box } = PYZ;
  const CODE = ['import copy', 'a = [[1, 2], [3, 4]]', 'b = a', 'c = a.copy()', 'd = copy.deepcopy(a)', 'c[0].append(9)', 'c.append([5])', 'print(a)', 'print(c)', 'print(d)'];
  const POS = { O1: 64, O2: 160, O3: 256, I1: 46, I2: 94, I5: 160, I3: 236, I4: 284 };
  const NAMEY = { a: 52, b: 82, c: 160, d: 256 };
  const ST = [
    [1, { a: 'O1' }, { O1: ['I1', 'I2'], I1: [1, 2], I2: [3, 4] }, [], '', 'a list holding two inner lists is made. There are three list objects: the outer one and two inner ones.'],
    [2, { a: 'O1', b: 'O1' }, { O1: ['I1', 'I2'], I1: [1, 2], I2: [3, 4] }, ['O1'], '', 'b = a copies NOTHING. b is a second name for the very same outer list.'],
    [3, { a: 'O1', b: 'O1', c: 'O2' }, { O1: ['I1', 'I2'], O2: ['I1', 'I2'], I1: [1, 2], I2: [3, 4] }, ['O2'], '', 'a.copy() is a <b>shallow copy</b>: a NEW outer list, but its slots point to the SAME inner lists.'],
    [4, { a: 'O1', b: 'O1', c: 'O2', d: 'O3' }, { O1: ['I1', 'I2'], O2: ['I1', 'I2'], O3: ['I3', 'I4'], I1: [1, 2], I2: [3, 4], I3: [1, 2], I4: [3, 4] }, ['O3', 'I3', 'I4'], '', 'copy.deepcopy(a) is a <b>deep copy</b>: a new outer list AND new inner lists, all the way down. Nothing is shared with a.'],
    [5, { a: 'O1', b: 'O1', c: 'O2', d: 'O3' }, { O1: ['I1', 'I2'], O2: ['I1', 'I2'], O3: ['I3', 'I4'], I1: [1, 2, 9], I2: [3, 4], I3: [1, 2], I4: [3, 4] }, ['I1'], '', 'c[0].append(9) changes the inner list that a, b and c all share. Only d has its own copy, so only d is safe.'],
    [6, { a: 'O1', b: 'O1', c: 'O2', d: 'O3' }, { O1: ['I1', 'I2'], O2: ['I1', 'I2', 'I5'], O3: ['I3', 'I4'], I1: [1, 2, 9], I2: [3, 4], I5: [5], I3: [1, 2], I4: [3, 4] }, ['O2', 'I5'], '', 'c.append([5]) changes the OUTER list of c, which is c\'s own. a and b do not see it.'],
    [9, { a: 'O1', b: 'O1', c: 'O2', d: 'O3' }, { O1: ['I1', 'I2'], O2: ['I1', 'I2', 'I5'], O3: ['I3', 'I4'], I1: [1, 2, 9], I2: [3, 4], I5: [5], I3: [1, 2], I4: [3, 4] }, [], '[[1, 2, 9], [3, 4]]\n[[1, 2, 9], [3, 4], [5]]\n[[1, 2], [3, 4]]', 'Shallow copies share what is inside. Deep copies share nothing. Assignment shares everything.']
  ];
  trace('pycopy', {
    title: 'Assignment, shallow copy and deep copy',
    sub: 'Each step runs one line. Names are on the left, outer lists in the middle and inner lists on the right. Lines show which object each slot points to.',
    W: 600, H: 400,
    tips: [{ t: 'Watch step 5: one append is seen through a, b and c, because they reach the same inner list.', play: true }],
    frames() { return ST.map(s => ({ line: s[0], names: s[1], objs: s[2], hl: s[3], out: s[4], say: s[5] })); },
    paint(z, f) {
      const c = z.col;
      codeView(z, CODE, f.line, 16, 16, 196, { s: 10.5, lh: 17 });
      const NX = 228, OX = 290, IX = 450, W = 30;
      head(z, 'Names', NX, 22); head(z, 'Outer lists', OX, 22); head(z, 'Inner lists', IX, 22);
      Object.entries(f.names).forEach(([n, o]) => {
        box(z, NX, NAMEY[n] - 12, 34, 24, n, { mono: true, b: true, s: 13, stroke: c.cv });
        D.line(z.g, NX + 34, NAMEY[n], OX, POS[o], c.cv, 1.6);
      });
      Object.entries(f.objs).forEach(([id, v]) => {
        const on = f.hl.includes(id);
        if (id[0] === 'O') {
          v.forEach((t, i) => {
            box(z, OX + i * W, POS[id] - 13, W, 26, '', { r: 3, fill: on ? (c.dark ? '#14321f' : '#dcfce7') : c.surf, stroke: on ? c.green : c.ink2 });
            D.line(z.g, OX + i * W + W / 2, POS[id], IX, POS[t], f.hl.includes(t) ? c.green : c.orange, 1.3);
            D.circle(z.g, OX + i * W + W / 2, POS[id], 3, { fill: c.orange });
          });
        } else {
          v.forEach((x, i) => box(z, IX + i * W, POS[id] - 13, W, 26, String(x), { r: 3, mono: true, s: 12, fill: on ? (c.dark ? '#14321f' : '#dcfce7') : c.surf, stroke: on ? c.green : c.ink2 }));
        }
      });
      if (f.out) consoleBox(z, f.out, 16, 300, 300, 92, { title: 'Output' });
    }
  });
})();

/* =====================================================================================================
   Advanced 1.5  how a class statement becomes a class: metaclass, namespace, __new__, __init_subclass__, decorator
   ===================================================================================================== */
(() => {
  const { trace, head, codeView, consoleBox, D, box } = PYZ;
  const CODE = ['registry = []', 'class Base:', '    def __init_subclass__(cls):', '        registry.append(cls.__name__)',
    'class Meta(type):', '    def __init__(cls, name, bases, ns):', '        super().__init__(name, bases, ns)', '        cls.tag = name.lower()',
    'def stamp(cls):', '    cls.stamped = True', '    return cls', '@stamp', 'class Dog(Base, metaclass=Meta):', '    sound = "woof"',
    '    def speak(self):', '        return self.sound', 'print(Dog.tag, Dog.stamped, registry)', 'rex = Dog()', 'print(type(Dog).__name__)'];
  const NS0 = ["__module__ = '__main__'", "__qualname__ = 'Dog'", '__firstlineno__ = 13'];
  const NS1 = NS0.concat(["sound = 'woof'"]);
  const NS2 = NS1.concat(['speak = <function speak>']);
  const C1 = ['name: Dog, bases: (Base,)', 'type(Dog) is Meta', 'holds: sound, speak'];
  const C2 = C1.concat(["tag = 'dog'"]);
  const C3 = C2.concat(['stamped = True']);
  const O1 = "dog True ['Dog']";
  /* [line, stage, namespace rows or null, class rows or null, registry, output, newest highlight, say] */
  const ST = [
    [0, 'registry = [] (an empty list)', null, null, '[]', '', '', 'Lines 1 to 11 only define things: an empty list, the class Base, the metaclass Meta and the function stamp. Python is now at the class statement for Dog.'],
    [12, 'Pick the metaclass: Meta', null, null, '[]', '', '', 'Before anything else Python decides WHO will build the class. metaclass=Meta is given, so Meta builds Dog. Without it Python would use the metaclass of the base class, which is type.'],
    [12, 'Meta.__prepare__ returns {}', [], null, '[]', '', '', 'Python asks the metaclass for an empty namespace. Meta does not define __prepare__, so the one from type gives a plain empty dict. The class body will fill it.'],
    [13, 'Run the class body', NS1, null, '[]', '', 'ns', 'The class body runs like normal code, top to bottom. Python first stores __module__, __qualname__ and (since Python 3.13) __firstlineno__, then sound = "woof" puts the name sound in the namespace.'],
    [14, 'Run the class body', NS2, null, '[]', '', 'ns', 'def speak only makes a function and stores it under the name speak. Nothing calls speak yet. A method is simply a function stored in the class.'],
    [12, "Meta('Dog', (Base,), ns)", NS2, C1, '[]', '', 'cls', 'The body is done, so Python calls Meta("Dog", (Base,), ns). Meta has no __new__ of its own, so type.__new__ runs and turns the namespace into a real class object. type(Dog) is Meta, because Meta built it.'],
    [3, 'Base.__init_subclass__(Dog)', NS2, C1, "['Dog']", '', 'reg', 'Inside type.__new__ Python also calls __init_subclass__ on the parent. Base hears that it has a new child and adds "Dog" to the registry. This hook needs no metaclass at all.'],
    [7, 'Meta.__init__(Dog, ...)', NS2, C2, "['Dog']", '', 'cls', 'Next Python runs Meta.__init__ on the new class. It lets type.__init__ do its part, then adds tag = "dog". Every class built by Meta gets a tag without writing it in the class.'],
    [9, 'stamp(Dog), the class decorator', NS2, C3, "['Dog']", '', 'cls', 'Only now does the class decorator run. stamp gets the finished class, adds stamped = True and returns the class.'],
    [12, 'Store the result under the name Dog', NS2, C3, "['Dog']", '', '', 'Whatever the decorator returns is stored under the name Dog. The class statement is finished. The namespace dict is not needed any more.'],
    [16, 'print(...)', NS2, C3, "['Dog']", O1, '', 'tag came from the metaclass, stamped from the decorator and the registry entry from __init_subclass__. Three hooks, three different moments.'],
    [17, 'Dog() calls Meta.__call__', NS2, C3, "['Dog']", O1, '', 'Calling a class runs __call__ of its metaclass (Meta gets it from type). It runs Dog.__new__ to make an empty object and then Dog.__init__ to fill it, and returns the object.'],
    [18, 'print(...)', NS2, C3, "['Dog']", O1 + '\nMeta', '', 'type(Dog) is Meta. rex is made by Dog, and Dog is made by Meta. Objects come from classes, and classes come from metaclasses.']
  ];
  function rows(z, items, x, y, w, newest) {
    const c = z.col;
    items.forEach((t, i) => {
      const on = newest && i === items.length - 1;
      box(z, x, y + i * 22, w, 20, t, { r: 4, mono: true, s: 11, fill: on ? (c.dark ? '#14321f' : '#dcfce7') : c.surf, stroke: on ? c.green : c.line });
    });
  }
  trace('pymeta', {
    title: 'How a class statement becomes a class',
    sub: 'Each step shows what Python does now, the namespace dict the class body fills, the class object once it exists, and the registry.',
    W: 600, H: 430,
    tips: [{ t: 'Watch steps 6 to 9: type.__new__, __init_subclass__, Meta.__init__ and the decorator each get their own moment.', play: true }],
    frames() { return ST.map(s => ({ line: s[0], stage: s[1], ns: s[2], cls: s[3], reg: s[4], out: s[5], hl: s[6], say: s[7] })); },
    paint(z, f) {
      const c = z.col;
      head(z, 'Program', 16, 18);
      codeView(z, CODE, f.line, 16, 26, 300, { s: 10, lh: 16 });
      head(z, 'What Python does now', 318, 18);
      box(z, 318, 26, 266, 32, f.stage, { mono: true, s: 11.5, fill: c.dark ? '#14321f' : '#dcfce7', stroke: c.green });
      if (f.ns) {
        head(z, 'Namespace dict (the class body fills it)', 318, 80);
        if (f.ns.length) rows(z, f.ns, 318, 88, 266, f.hl === 'ns'); else box(z, 318, 88, 266, 20, '{}', { r: 4, mono: true, s: 11 });
      }
      if (f.cls) {
        head(z, 'Class object Dog', 318, 238);
        rows(z, f.cls, 318, 246, 266, f.hl === 'cls');
      }
      head(z, 'registry', 318, 378);
      box(z, 318, 386, 266, 26, f.reg, { r: 4, mono: true, s: 12, b: true, stroke: f.hl === 'reg' ? c.green : c.orange, fill: f.hl === 'reg' ? (c.dark ? '#14321f' : '#dcfce7') : c.surf });
      if (f.out) consoleBox(z, f.out, 16, 352, 300, 72, { title: 'Output' });
    }
  });
})();

/* =====================================================================================================
   Advanced 2.1  a generator pauses at yield: who runs, where it waits, what it hands over
   ===================================================================================================== */
(() => {
  const { trace, head, codeView, consoleBox, D, box } = PYZ;
  const GEN = ['def countdown(n):', '    print("start")', '    while n > 0:', '        yield n', '        n -= 1', '    print("done")'];
  const CALL = ['g = countdown(2)', 'print(next(g))', 'print(next(g))', 'print(next(g, "end"))'];
  /* [caller line, generator line or -1, state, n or '', handed value, output, say] */
  const ST = [
    [0, -1, 'CREATED', '2', '', '', 'Calling countdown(2) runs NONE of its body. Because the function contains yield, Python returns a generator object that waits before line 1, with n = 2 stored inside it.'],
    [1, 1, 'RUNNING', '2', '', 'start', 'next(g) wakes the generator for the first time. It runs from the top, so "start" is printed. The caller waits while the generator runs.'],
    [1, 2, 'RUNNING', '2', '', 'start', 'n > 0 is 2 > 0, which is True, so the loop body runs.'],
    [1, 3, 'SUSPENDED', '2', '2', 'start\n2', 'yield n hands 2 to the caller and PAUSES right here. The local variable n and the position are kept. next(g) returns 2 and print shows it.'],
    [2, 4, 'RUNNING', '1', '', 'start\n2', 'The second next(g) resumes the generator exactly after the yield. n -= 1 makes n = 1. Nothing starts again from the top.'],
    [2, 2, 'RUNNING', '1', '', 'start\n2', '1 > 0 is True, so the loop goes round again.'],
    [2, 3, 'SUSPENDED', '1', '1', 'start\n2\n1', 'yield hands over 1 and pauses again. The caller prints 1.'],
    [3, 4, 'RUNNING', '0', '', 'start\n2\n1', 'The third call resumes after the yield. n -= 1 makes n = 0.'],
    [3, 2, 'RUNNING', '0', '', 'start\n2\n1', '0 > 0 is False, so the loop ends.'],
    [3, 5, 'RUNNING', '0', '', 'start\n2\n1\ndone', 'print("done") runs. The generator reaches the end of its body.'],
    [3, -1, 'CLOSED', '', 'end', 'start\n2\n1\ndone\nend', 'Falling off the end raises StopIteration. next(g, "end") catches it and returns the default "end". The generator is now closed and every later next(g) stops at once.']
  ];
  const COL = { CREATED: 'cv', RUNNING: 'green', SUSPENDED: 'orange', CLOSED: 'red' };
  trace('pygen', {
    title: 'A generator pauses at yield',
    sub: 'The caller on the right asks for values with next(). Each step shows which line runs, the state of the generator, its local variable n and the value it hands over.',
    W: 600, H: 360,
    tips: [{ t: 'Compare steps 4 and 5: after a pause the generator goes on from the line after yield, with n still in memory.', play: true }],
    frames() { return ST.map(s => ({ cl: s[0], gl: s[1], st: s[2], n: s[3], val: s[4], out: s[5], say: s[6] })); },
    paint(z, f) {
      const c = z.col;
      head(z, 'Generator function', 16, 18);
      codeView(z, GEN, f.gl, 16, 26, 260, { s: 12, lh: 22, hl: f.st === 'RUNNING' ? (c.dark ? '#14321f' : '#dcfce7') : undefined });
      head(z, 'Caller', 300, 18);
      codeView(z, CALL, f.cl, 300, 26, 284, { s: 12, lh: 22 });
      head(z, 'Generator state', 16, 196);
      box(z, 16, 204, 124, 32, f.st, { mono: true, b: true, s: 12.5, stroke: c[COL[f.st]] });
      head(z, 'n inside it', 152, 196);
      box(z, 152, 204, 124, 32, f.n === '' ? '(gone)' : 'n = ' + f.n, { mono: true, s: 12.5, stroke: c.cv });
      head(z, 'Handed to the caller', 16, 262);
      box(z, 16, 270, 260, 32, f.val || '(nothing yet)', { mono: true, b: !!f.val, s: 12.5, stroke: f.val ? c.orange : c.line, fill: f.val ? (c.dark ? '#3a2a10' : '#fff7ed') : c.surf });
      if (f.out) consoleBox(z, f.out, 300, 160, 284, 140, { title: 'Output' });
    }
  });
})();

/* =====================================================================================================
   Advanced 2.2  product, permutations, combinations and combinations_with_replacement, one tuple per step
   ===================================================================================================== */
(() => {
  const { trace, head, consoleBox, D, box } = PYZ;
  const ITEMS = 'ABCD';
  function make(fn, n, r) {
    const out = [];
    const idx = [];
    (function walk() {
      if (idx.length === r) { out.push(idx.slice()); return; }
      for (let i = 0; i < n; i++) {
        if (fn === 'permutations' && idx.includes(i)) continue;
        if (fn === 'combinations' && idx.length && i <= idx[idx.length - 1]) continue;
        if (fn === 'combinations_with_replacement' && idx.length && i < idx[idx.length - 1]) continue;
        idx.push(i); walk(); idx.pop();
      }
    })();
    return out;
  }
  const fact = k => (k <= 1 ? 1 : k * fact(k - 1));
  function formula(fn, n, r) {
    if (fn === 'product') return [`n^r = ${n}^${r}`, n ** r];
    if (fn === 'permutations') return [`n! / (n - r)! = ${n}! / ${n - r}!`, fact(n) / fact(n - r)];
    if (fn === 'combinations') return [`n! / (r! (n - r)!) = ${n}! / (${r}! ${n - r}!)`, n >= r ? fact(n) / (fact(r) * fact(n - r)) : 0];
    return [`C(n + r - 1, r) = C(${n + r - 1}, ${r})`, fact(n + r - 1) / (fact(r) * fact(n - 1))];
  }
  const RULE = {
    product: 'every position can be any item, and items may repeat',
    permutations: 'order matters and an item cannot be used twice',
    combinations: 'order does not matter, so only increasing positions are kept, and no item repeats',
    combinations_with_replacement: 'order does not matter, but an item may be picked again'
  };
  trace('pycombo', {
    title: 'itertools: product, permutations and combinations',
    sub: 'Pick a function, how many items (n) and how long each tuple is (r). Each step makes the next tuple in the exact order Python gives them.',
    W: 600, H: 380,
    params: [
      { k: 'fn', label: 'Function', type: 'select', v: 'combinations', opts: [['product', 'product(items, repeat=r)'], ['permutations', 'permutations(items, r)'], ['combinations', 'combinations(items, r)'], ['combinations_with_replacement', 'combinations_with_replacement(items, r)']] },
      { k: 'n', label: 'Items (n)', type: 'select', v: '4', opts: [['2', '2: A B'], ['3', '3: A B C'], ['4', '4: A B C D']] },
      { k: 'r', label: 'Tuple length (r)', type: 'select', v: '2', opts: [['1', '1'], ['2', '2'], ['3', '3']] }
    ],
    tips: [
      { t: 'combinations of 4 items, 2 at a time: 6 tuples. AB and BA count once.', set: { fn: 'combinations', n: '4', r: '2' }, play: true },
      { t: 'permutations of the same items: 12 tuples, because AB and BA are different.', set: { fn: 'permutations', n: '4', r: '2' }, play: true },
      { t: 'product of 3 items with repeat=2: 9 tuples, AA and BB included.', set: { fn: 'product', n: '3', r: '2' }, play: true }
    ],
    frames(p) {
      const n = Number(p.n), r = Number(p.r), all = make(p.fn, n, r);
      const [f, total] = formula(p.fn, n, r);
      if (!all.length) return [{ n, r, fn: p.fn, done: [], cur: null, f, total, say: `There are fewer items (${n}) than places (${r}), so combinations gives no tuples at all. The formula also gives 0.` }];
      const fr = all.map((t, i) => ({ n, r, fn: p.fn, done: all.slice(0, i + 1), cur: t, f, total,
        say: i === 0 ? `The first tuple is ${t.map(k => ITEMS[k]).join('')}. Rule for ${p.fn}: ${RULE[p.fn]}.` :
          `Next comes ${t.map(k => ITEMS[k]).join('')}. Tuples come out in sorted order of positions, one per next() call, so nothing is stored in advance.` }));
      fr.push({ ...fr[fr.length - 1], cur: null, end: true, say: `All ${all.length} tuples are done, matching the formula ${f} = ${total}. A further next() would raise StopIteration.` });
      return fr;
    },
    paint(z, f) {
      const c = z.col;
      head(z, 'Items', 16, 20);
      for (let i = 0; i < f.n; i++) {
        const on = f.cur && f.cur.includes(i);
        box(z, 16 + i * 46, 30, 38, 34, ITEMS[i], { mono: true, b: true, s: 15, stroke: on ? c.green : c.cv, fill: on ? (c.dark ? '#14321f' : '#dcfce7') : c.surf });
      }
      head(z, 'This step', 220, 20);
      box(z, 220, 30, 150, 34, f.cur ? '(' + f.cur.map(k => "'" + ITEMS[k] + "'").join(', ') + ')' : (f.end ? 'StopIteration next' : '(none)'), { mono: true, s: 13, b: true, stroke: f.cur ? c.green : c.line });
      head(z, 'How many', 390, 20);
      box(z, 390, 30, 194, 34, `${f.done.length} of ${f.total}`, { s: 14, b: true, stroke: c.orange });
      head(z, 'Tuples so far', 16, 92);
      const big = f.total > 24, per = big ? 8 : 6, w = big ? 68 : 92, rh = big ? 22 : 30;
      f.done.forEach((t, i) => {
        const col = i % per, row = Math.floor(i / per);
        const last = f.cur && i === f.done.length - 1;
        box(z, 16 + col * (w + 4), 100 + row * rh, w, rh - 4, t.map(k => ITEMS[k]).join(''), { mono: true, s: 13, r: 5, stroke: last ? c.green : c.line, fill: last ? (c.dark ? '#14321f' : '#dcfce7') : c.surf });
      });
      head(z, 'Formula', 16, 330);
      box(z, 16, 338, 568, 32, `${f.f} = ${f.total}`, { mono: true, s: 13, stroke: c.cv });
    }
  });
})();

/* =====================================================================================================
   Advanced 2.3  what a with statement really does: __enter__, the body, __exit__ and the exception
   ===================================================================================================== */
(() => {
  const { trace, head, codeView, consoleBox, D, box } = PYZ;
  function code(path) {
    return ['class Door:', '    def __enter__(self):', '        print("open")', '        return "room"', '    def __exit__(self, kind, err, tb):', '        print("close")',
      path === 'swallow' ? '        return kind is ZeroDivisionError' : '        return False', '', 'with Door() as place:', '    print("inside", place)',
      path === 'normal' ? '    print("done inside")' : '    print(1 / 0)', 'print("after")'];
  }
  function frames(path) {
    const E = 'ZeroDivisionError';
    const f = [
      [8, '', '', '', '', 'Python evaluates Door(). The new object is the <b>context manager</b>: the thing that knows how to set up and clean up.'],
      [2, '', '', '', 'open', 'Python calls its __enter__ method. It runs the set up work, here printing open.'],
      [3, '"room"', '', '', 'open', '__enter__ returns "room". Because of <b>as place</b>, that return value (not the Door) is stored in place.'],
      [9, '"room"', '', '', 'open\ninside room', 'Now the body of the with block runs.']
    ];
    let out = 'open\ninside room';
    if (path === 'normal') {
      out += '\ndone inside';
      f.push([10, '"room"', '', '', out, 'The body finishes with no error.']);
      f.push([4, '"room"', 'None, None, None', '', out, 'Leaving the block calls __exit__. No error happened, so all three arguments are None.']);
      out += '\nclose';
      f.push([5, '"room"', 'None, None, None', '', out, 'The clean up runs: close is printed.']);
      out += '\nafter';
      f.push([11, '"room"', 'None, None, None', '', out, 'The program goes on after the with block. The clean up ran exactly once.']);
      return f;
    }
    f.push([10, '"room"', '', E, out, '1 / 0 raises ZeroDivisionError. The rest of the body is skipped at once, but Python does NOT leave yet.']);
    f.push([4, '"room"', E + ', err, tb', E, out, 'Python calls __exit__ with the error type (kind), the error object (err) and its traceback (tb). This happens for any error, so clean up is never skipped.']);
    out += '\nclose';
    f.push([5, '"room"', E + ', err, tb', E, out, 'The clean up runs: close is printed, even though the body failed.']);
    if (path === 'swallow') {
      f.push([6, '"room"', E + ', err, tb', 'swallowed', out, '__exit__ returns True (kind is ZeroDivisionError). A true return value tells Python to <b>suppress</b> the error.']);
      out += '\nafter';
      f.push([11, '"room"', E + ', err, tb', 'swallowed', out, 'The error is gone and the program goes on after the block, so after is printed.']);
    } else {
      f.push([6, '"room"', E + ', err, tb', E, out, '__exit__ returns False, so Python lets the error carry on.']);
      f.push([-1, '"room"', E + ', err, tb', E, out + '\nZeroDivisionError: division by zero', 'The error travels up and the program stops: print("after") never runs. But close was printed first, which is the whole point of with.']);
    }
    return f;
  }
  trace('pywith', {
    title: 'What a with statement does',
    sub: 'Pick a case. Each step shows the line that runs, what as stores, the arguments __exit__ gets, and whether an error is on its way.',
    W: 600, H: 400,
    params: [{ k: 'path', label: 'Case', type: 'select', v: 'error', opts: [['normal', 'The body works'], ['error', 'The body raises, __exit__ returns False'], ['swallow', 'The body raises, __exit__ returns True']] }],
    tips: [
      { t: 'An error in the body still runs __exit__, so close is printed before the program stops.', set: { path: 'error' }, play: true },
      { t: 'A true return value from __exit__ swallows the error.', set: { path: 'swallow' }, play: true }
    ],
    frames(p) { return frames(p.path).map(s => ({ code: code(p.path), line: s[0], as: s[1], args: s[2], err: s[3], out: s[4], say: s[5] })); },
    paint(z, f) {
      const c = z.col;
      head(z, 'Program', 16, 18);
      codeView(z, f.code, f.line, 16, 26, 320, { s: 11, lh: 19 });
      head(z, 'place (from as)', 352, 18);
      box(z, 352, 26, 232, 32, f.as || '(not set yet)', { mono: true, s: 12.5, b: !!f.as, stroke: c.cv });
      head(z, '__exit__ got', 352, 82);
      box(z, 352, 90, 232, 32, f.args || '(not called yet)', { mono: true, s: 11, stroke: f.args ? c.green : c.line });
      head(z, 'Error on its way', 352, 146);
      const bad = f.err && f.err !== 'swallowed';
      box(z, 352, 154, 232, 32, f.err || '(none)', { mono: true, s: 12, b: !!f.err, stroke: bad ? c.red : (f.err ? c.green : c.line), fill: bad ? (c.dark ? '#3b1414' : '#fee2e2') : c.surf });
      if (f.out) consoleBox(z, f.out, 16, 278, 568, 114, { title: 'Output', err: /Error/.test(f.out.split('\n').pop()) });
    }
  });
})();

/* =====================================================================================================
   Advanced 3.1  cleaning messy code one PEP 8 rule at a time, then a docstring and type hints
   ===================================================================================================== */
(() => {
  const { trace, head, codeView, D, box } = PYZ;
  /* [code lines, changed line indexes, rule, say] */
  const ST = [
    [['import sys, math', 'def CircleArea( R ):', '  if R==None : return 0', '  A=math.pi*R**2', '  return A'], [], 'Working, but messy',
      'This code works and gives the right answers. But it is hard to read and it breaks many rules of <b>PEP 8</b>, the official Python style guide. A linter such as ruff reports 8 problems here. We fix one rule per step.'],
    [['import math', 'def CircleArea( R ):', '  if R==None : return 0', '  A=math.pi*R**2', '  return A'], [0], 'Imports: one per line, no unused ones',
      'PEP 8 wants one import per line at the top of the file. sys was never used, so it simply goes (ruff calls this F401).'],
    [['import math', '', '', 'def CircleArea( R ):', '  if R==None : return 0', '  A=math.pi*R**2', '  return A'], [1, 2], 'Two blank lines before a top level def',
      'Top level functions and classes get two blank lines around them, methods inside a class get one. It lets the eye find where each part starts.'],
    [['import math', '', '', 'def circle_area( radius ):', '  if radius==None : return 0', '  area=math.pi*radius**2', '  return area'], [3, 4, 5, 6], 'Names: snake_case that says what it holds',
      'Functions and variables use lower_case_with_underscores. Classes use CapWords and constants UPPER_CASE. R and A told the reader nothing, radius and area do.'],
    [['import math', '', '', 'def circle_area( radius ):', '    if radius==None : return 0', '    area=math.pi*radius**2', '    return area'], [4, 5, 6], 'Indent with 4 spaces',
      'Use 4 spaces for each level, never tabs mixed with spaces. Python itself only needs the indents to match, but every Python reader expects 4.'],
    [['import math', '', '', 'def circle_area(radius):', '    if radius == None : return 0', '    area = math.pi * radius**2', '    return area'], [3, 4, 5], 'Spaces: around = and ==, not inside brackets',
      'No space just inside brackets. One space around =, == and other operators. With mixed operators PEP 8 lets the highest priority one hug: radius**2.'],
    [['import math', '', '', 'def circle_area(radius):', '    if radius == None:', '        return 0', '    area = math.pi * radius**2', '    return area'], [4, 5], 'One statement per line',
      'if ... : return 0 on one line hides the return. Put the body of if, for and while on its own indented line.'],
    [['import math', '', '', 'def circle_area(radius):', '    if radius is None:', '        return 0', '    area = math.pi * radius**2', '    return area'], [4], 'Compare to None with is',
      'None is a single object, so check it with is None. == None can be fooled by a class that changes __eq__. This rule changes behaviour, not just looks.'],
    [['import math', '', '', 'def circle_area(radius):', '    """Return the area of a circle, or 0 if radius is missing."""', '    if radius is None:', '        return 0', '    area = math.pi * radius**2', '    return area'], [4], 'A docstring (PEP 257)',
      'PEP 257: the first statement of a function is a docstring in triple double quotes, a one line summary that ends with a full stop. help(circle_area) now shows it.'],
    [['import math', '', '', 'def circle_area(radius: float | None) -> float:', '    """Return the area of a circle, or 0 if radius is missing."""', '    if radius is None:', '        return 0', '    area = math.pi * radius**2', '    return area'], [3], 'Type hints (PEP 484)',
      'Hints say radius is a float or None and the result is a float. Python ignores them at run time, but editors and mypy use them to catch mistakes before the program runs. The ruff report is now empty.']
  ];
  trace('pystyle', {
    title: 'Cleaning code one rule at a time',
    sub: 'Each step fixes one style rule. Changed lines are marked with a tick. The behaviour stays the same, the code gets easier to read.',
    W: 600, H: 330,
    tips: [{ t: 'Step 8 is the only rule that can change what the program does: is None cannot be fooled.', play: true }],
    frames() { return ST.map((s, i) => ({ lines: s[0], changed: s[1], rule: s[2], n: i, say: s[3] })); },
    paint(z, f) {
      const c = z.col;
      head(z, 'Rule fixed in this step', 16, 18);
      box(z, 16, 26, 568, 32, f.rule, { s: 13, b: true, fill: f.n ? (c.dark ? '#14321f' : '#dcfce7') : (c.dark ? '#3b1414' : '#fee2e2'), stroke: f.n ? c.green : c.red });
      head(z, 'The code now', 16, 82);
      codeView(z, f.lines, f.changed.length ? f.changed[0] : -1, 16, 90, 568, { s: 12, lh: 21, done: f.changed });
      D.text(z.g, `Rules fixed: ${f.n} of ${ST.length - 1}`, 584, 82, { a: 'right', s: 12, b: true, c: c.ink2 });
    }
  });
})();

/* =====================================================================================================
   Advanced 3.2  a test run: collect, run each test, red, fix, green, refactor
   ===================================================================================================== */
(() => {
  const { trace, head, codeView, consoleBox, D, box } = PYZ;
  const V1 = ['def discount(price, percent):', '    if percent < 0 or percent > 100:', '        raise ValueError("percent must be 0 to 100")', '    return price - price * percent // 100'];
  const V2 = V1.slice(0, 3).concat(['    return price - price * percent / 100']);
  const V3 = V1.slice(0, 3).concat(['    return price * (100 - percent) / 100']);
  const TESTS = ['test_no_discount', 'test_half_price', 'test_ten_percent', 'test_bad_percent'];
  const CHECKS = ['discount(100, 0) == 100', 'discount(80, 50) == 40', 'discount(99, 10) == 89.1', 'raises(ValueError): discount(10, 150)'];
  /* [code, code line, statuses, check text, result text, summary, say] */
  const P = 'PASSED', F = 'FAILED', W = 'waiting';
  const ST = [
    [V1, -1, [W, W, W, W], '', '', 'collected 4 items', 'pytest looks in files named test_*.py for functions whose names start with test_. It finds 4 tests. Nothing has run yet.'],
    [V1, 3, [P, W, W, W], CHECKS[0], '100 == 100', '', 'test_no_discount calls discount(100, 0). 100 &minus; 100 &times; 0 // 100 is 100, so assert 100 == 100 holds: PASSED.'],
    [V1, 3, [P, P, W, W], CHECKS[1], '40 == 40', '', 'test_half_price: 80 &minus; 80 &times; 50 // 100 = 80 &minus; 40 = 40. PASSED.'],
    [V1, 3, [P, P, F, W], CHECKS[2], 'assert 90 == 89.1', '', 'test_ten_percent: 99 &times; 10 // 100 is 990 // 100 = 9, because // throws the decimals away. 99 &minus; 9 = 90, not 89.1. The assert fails and pytest shows both values: FAILED.'],
    [V1, 2, [P, P, F, P], CHECKS[3], 'ValueError raised, as expected', '', 'test_bad_percent expects an error. 150 is above 100, so ValueError is raised, which is exactly what pytest.raises wants: PASSED.'],
    [V1, -1, [P, P, F, P], '', '', '1 failed, 3 passed', 'The run is <b>red</b>: one test failed. The failing test points straight at the bug, the // on line 4.'],
    [V2, 3, [W, W, W, W], '', '', 'code changed', 'Fix the bug: use / (true division) instead of //. Now 99 &times; 10 / 100 is 9.9.'],
    [V2, -1, [P, P, P, P], CHECKS[2], '89.1 == 89.1', '4 passed', 'Run all the tests again, not only the one that failed. All 4 pass: the run is <b>green</b>, and the fix broke nothing else.'],
    [V3, 3, [P, P, P, P], '', '', '4 passed', 'Refactor: rewrite the formula as price &times; (100 &minus; percent) / 100, which avoids a tiny rounding error at 100 %. The tests still pass, so the change is safe. Red, green, refactor is the TDD cycle.']
  ];
  const COL = { PASSED: 'green', FAILED: 'red', waiting: 'line' };
  trace('pyunit', {
    title: 'A test run: red, green, refactor',
    sub: 'The code under test is on the left, the tests on the right. Each step runs one test or changes the code.',
    W: 600, H: 340,
    tips: [{ t: 'Step 4 shows why tests matter: the bug only appears for prices whose discount is not a whole number.', play: true }],
    frames() { return ST.map(s => ({ code: s[0], line: s[1], st: s[2], check: s[3], res: s[4], sum: s[5], say: s[6] })); },
    paint(z, f) {
      const c = z.col;
      head(z, 'shop.py (code under test)', 16, 18);
      codeView(z, f.code, f.line, 16, 26, 568, { s: 11.5, lh: 21 });
      head(z, 'test_shop.py', 16, 136);
      f.st.forEach((s, i) => {
        const y = 144 + i * 30;
        box(z, 16, y, 200, 26, TESTS[i], { mono: true, s: 11.5, r: 5 });
        box(z, 222, y, 86, 26, s, { b: s !== W, s: 11.5, r: 5, stroke: c[COL[s]], c: s === F ? c.red : (s === P ? c.green : c.ink2) });
      });
      head(z, 'Check', 330, 136);
      box(z, 330, 144, 254, 30, f.check || '(none)', { mono: true, s: 11, stroke: c.cv });
      head(z, 'Result', 330, 196);
      const bad = /^assert/.test(f.res);
      box(z, 330, 204, 254, 30, f.res || '(none)', { mono: true, s: 11.5, b: !!f.res, stroke: bad ? c.red : (f.res ? c.green : c.line), fill: bad ? (c.dark ? '#3b1414' : '#fee2e2') : c.surf });
      if (f.sum) {
        const red = /failed/.test(f.sum), green = /passed/.test(f.sum) && !red;
        box(z, 16, 278, 568, 40, f.sum, { s: 15, b: true, stroke: red ? c.red : (green ? c.green : c.cv), fill: red ? (c.dark ? '#3b1414' : '#fee2e2') : (green ? (c.dark ? '#14321f' : '#dcfce7') : c.surf) });
      }
    }
  });
})();

/* =====================================================================================================
   Advanced 3.3  the journey of a log record: logger level, handler levels, formatter, output
   ===================================================================================================== */
(() => {
  const { trace, head, codeView, consoleBox, D, box } = PYZ;
  const NUM = { DEBUG: 10, INFO: 20, WARNING: 30, ERROR: 40, CRITICAL: 50 };
  const LV = Object.keys(NUM).map(k => [k, k + ' (' + NUM[k] + ')']);
  const MSG = { DEBUG: 'reading cart 42', INFO: 'cart total is 280', WARNING: 'stock is low', ERROR: 'payment failed', CRITICAL: 'database is down' };
  trace('pylog', {
    title: 'The journey of a log record',
    sub: 'Pick the level of the message, the level of the logger and the level of the console handler. The file handler takes everything from DEBUG up.',
    W: 600, H: 380,
    params: [
      { k: 'msg', label: 'Message level', type: 'select', v: 'INFO', opts: LV },
      { k: 'lg', label: 'Logger level', type: 'select', v: 'DEBUG', opts: LV.slice(0, 4) },
      { k: 'con', label: 'Console handler level', type: 'select', v: 'WARNING', opts: LV.slice(0, 4) }
    ],
    tips: [
      { t: 'An INFO message reaches the file but not the console, whose level is WARNING.', set: { msg: 'INFO', lg: 'DEBUG', con: 'WARNING' }, play: true },
      { t: 'With the logger at WARNING a DEBUG message stops at once: no record is even made.', set: { msg: 'DEBUG', lg: 'WARNING', con: 'DEBUG' }, play: true },
      { t: 'An ERROR passes everywhere.', set: { msg: 'ERROR', lg: 'INFO', con: 'WARNING' }, play: true }
    ],
    frames(p) {
      const m = NUM[p.msg], lg = NUM[p.lg], con = NUM[p.con], text = MSG[p.msg];
      const call = `logger.${p.msg.toLowerCase()}("${text}")`;
      const line = `${p.msg} shop.cart: ${text}`;
      const base = { call, msg: p.msg, lg: p.lg, con: p.con, stage: 0, rec: false, conOut: '', fileOut: '', conOk: null, fileOk: null };
      const fr = [{ ...base, say: `The program calls ${call}. The message level is ${p.msg}, which is the number ${m}.` }];
      if (m < lg) {
        fr.push({ ...base, stage: 1, blocked: true, say: `The logger's level is ${p.lg} (${lg}). ${m} &lt; ${lg}, so the logger drops the message right here. No record is made and no handler is asked. That is why debug lines cost almost nothing when they are switched off.` });
        return fr;
      }
      fr.push({ ...base, stage: 1, say: `The logger's level is ${p.lg} (${lg}). ${m} &ge; ${lg}, so the message passes.` });
      fr.push({ ...base, stage: 2, rec: true, say: 'The logger builds a <b>LogRecord</b>: the logger name (shop.cart), the level, the message, the time, the file and the line number. It hands the record to each of its handlers.' });
      const cOk = m >= con;
      fr.push({ ...base, stage: 3, rec: true, conOk: cOk, conOut: cOk ? line : '', say: cOk ? `The console handler's level is ${p.con} (${con}). ${m} &ge; ${con}, so its formatter turns the record into text and prints it.` : `The console handler's level is ${p.con} (${con}). ${m} &lt; ${con}, so this handler ignores the record. Each handler filters on its own.` });
      fr.push({ ...base, stage: 4, rec: true, conOk: cOk, conOut: cOk ? line : '', fileOk: true, fileOut: '10:00:00 ' + line, say: 'The file handler has level DEBUG (10), so it takes every record and writes it to app.log with the time in front. Files usually keep more detail than the screen.' });
      fr.push({ ...base, stage: 5, rec: true, conOk: cOk, conOut: cOk ? line : '', fileOk: true, fileOut: '10:00:00 ' + line, say: 'Last, the record <b>propagates</b> to the parent loggers shop and then the root logger, which would pass it to their handlers too. Here they have none, so the journey ends.' });
      return fr;
    },
    paint(z, f) {
      const c = z.col;
      const green = c.dark ? '#14321f' : '#dcfce7', red = c.dark ? '#3b1414' : '#fee2e2';
      head(z, 'The call', 16, 18);
      box(z, 16, 26, 568, 30, f.call, { mono: true, s: 12.5, stroke: c.cv });
      head(z, 'Logger shop.cart', 16, 82);
      box(z, 16, 90, 180, 46, `level ${f.lg} (${NUM[f.lg]})`, { mono: true, s: 12, b: f.stage === 1, stroke: f.stage >= 1 ? (f.blocked ? c.red : c.green) : c.line, fill: f.stage >= 1 ? (f.blocked ? red : green) : c.surf });
      if (f.blocked) D.text(z.g, 'stopped here', 106, 156, { a: 'center', s: 12, b: true, c: c.red });
      if (f.rec) {
        head(z, 'LogRecord', 216, 82);
        box(z, 216, 90, 160, 46, `${f.msg} | shop.cart`, { mono: true, s: 11, stroke: c.orange, fill: c.dark ? '#3a2a10' : '#fff7ed' });
        D.line(z.g, 196, 113, 216, 113, c.ink2, 1.5);
      }
      head(z, 'Console handler', 396, 82);
      box(z, 396, 90, 188, 46, `level ${f.con} (${NUM[f.con]})`, { mono: true, s: 11.5, stroke: f.conOk === null ? c.line : (f.conOk ? c.green : c.red), fill: f.conOk === null ? c.surf : (f.conOk ? green : red) });
      head(z, 'File handler', 396, 160);
      box(z, 396, 168, 188, 46, 'level DEBUG (10)', { mono: true, s: 11.5, stroke: f.fileOk ? c.green : c.line, fill: f.fileOk ? green : c.surf });
      if (f.rec) { D.line(z.g, 376, 113, 396, 113, c.ink2, 1.5); D.line(z.g, 376, 113, 396, 191, c.ink2, 1.5); }
      if (f.stage >= 5) {
        head(z, 'Propagates to', 16, 160);
        box(z, 16, 168, 180, 46, 'shop, then root', { mono: true, s: 12, stroke: c.cv });
      }
      consoleBox(z, f.conOut || '(nothing printed)', 16, 236, 280, 128, { title: 'Screen' });
      consoleBox(z, f.fileOut || '(nothing written)', 304, 236, 280, 128, { title: 'app.log' });
    }
  });
})();

/* =====================================================================================================
   Advanced 4.1  how the number of steps grows with n for the common Big O classes
   ===================================================================================================== */
(() => {
  const { trace, head, D, box } = PYZ;
  const L2 = x => Math.log2(Math.max(1, x));
  const CLS = [
    { k: 'O(1)', f: () => 1, ex: 'x in a set, d[key]', col: 'green', say: 'O(1), <b>constant time</b>: the work does not depend on n. Looking up a key in a dict or a set takes about the same time for 10 items or 10 million.' },
    { k: 'O(log n)', f: n => Math.ceil(L2(n)), ex: 'binary search, bisect', col: 'cv', say: 'O(log n), <b>logarithmic</b>: each step throws away half of what is left. Doubling n adds only one more step. Binary search on a sorted list works like this.' },
    { k: 'O(n)', f: n => n, ex: 'x in a list, sum(), max()', col: 'orange', say: 'O(n), <b>linear</b>: one step per item. Twice the data means twice the work. Searching an unsorted list or adding up all items is linear.' },
    { k: 'O(n log n)', f: n => Math.round(n * L2(n)), ex: 'sorted(), list.sort()', col: 'purple', say: 'O(n log n): a little more than linear. Good sorting is this fast, so "sort first, then scan once" is often a smart plan.' },
    { k: 'O(n²)', f: n => n * n, ex: 'two nested loops over the data', col: 'red', say: 'O(n²), <b>quadratic</b>: every item meets every other item, usually through a loop inside a loop. Twice the data means four times the work, and the curve leaves the chart quickly.' }
  ];
  trace('pybigo', {
    title: 'How the work grows with n',
    sub: 'Pick the size of the data. Each step adds one Big O class to the chart and to the table of steps.',
    W: 600, H: 370,
    params: [{ k: 'n', label: 'Size of the data n', type: 'select', v: '32', opts: [['16', 'n = 16'], ['32', 'n = 32'], ['64', 'n = 64'], ['1000', 'n = 1000']] }],
    tips: [
      { t: 'With n = 16 the classes look close together.', set: { n: '16' }, play: true },
      { t: 'With n = 1000, n² is 1,000,000 steps but log n is only 10.', set: { n: '1000' }, play: true }
    ],
    frames(p) {
      const n = +p.n;
      const fr = [{ n, shown: 0, say: `The x axis is the size of the data, from 1 to ${n}. The y axis is how many basic steps an algorithm needs. Big O describes the <b>shape</b> of this curve when n gets large.` }];
      CLS.forEach((c, i) => fr.push({ n, shown: i + 1, say: c.say + ` At n = ${n} that is ${c.f(n).toLocaleString('en')} step${c.f(n) === 1 ? '' : 's'}.` }));
      const r = CLS[4].f(n) / CLS[2].f(n);
      fr.push({ n, shown: 5, end: true, say: `Compare the table: at n = ${n} the quadratic algorithm needs ${r.toLocaleString('en')} times the work of the linear one. Changing the algorithm matters far more than a faster computer.` });
      return fr;
    },
    paint(z, f) {
      const c = z.col, g = z.g;
      const colour = k => k === 'purple' ? (c.dark ? '#c4b5fd' : '#7c3aed') : c[k];
      const ymax = Math.max(4, Math.round(f.n * L2(f.n) * 1.15));
      head(z, 'Steps needed for data of size n', 16, 18);
      const m = D.axes(g, z, [60, 30, 290, 270], [1, f.n], [0, ymax], { nx: 4, ny: 4, xl: 'n (size of the data)', yl: 'steps', fx: v => String(Math.round(v)), fy: v => Math.round(v).toLocaleString('en') });
      g.save(); g.beginPath(); g.rect(60, 30, 290, 270); g.clip();
      CLS.slice(0, f.shown).forEach((cl, i) => {
        const last = i === f.shown - 1 && !f.end;
        D.curve(g, x => cl.k === 'O(log n)' ? L2(x) : cl.f(x), [1, f.n], m, colour(cl.col), last ? 3.5 : 2.2, 300);
      });
      g.restore();
      let lowest = 999;
      CLS.slice(0, f.shown).forEach(cl => {
        const yv = cl.f(f.n);
        if (yv > ymax) { D.text(g, cl.k + ' goes off the top', 174, 44, { s: 11, b: true, c: colour(cl.col) }); return; }
        const yy = Math.min(lowest - 13, Math.max(40, m.sy(yv) - 4));
        lowest = yy;
        D.text(g, cl.k, 346, yy, { a: 'right', s: 11, b: true, c: colour(cl.col) });
      });
      head(z, `At n = ${f.n}`, 372, 18);
      CLS.forEach((cl, i) => {
        const y = 30 + i * 52;
        const on = i < f.shown;
        if (on) {
          box(z, 372, y, 212, 46, '', { stroke: colour(cl.col), b: i === f.shown - 1 && !f.end });
          const v = cl.f(f.n);
          D.text(g, cl.k, 382, y + 19, { s: 13, b: true, c: colour(cl.col), mono: true });
          D.text(g, v.toLocaleString('en') + (v === 1 ? ' step' : ' steps'), 574, y + 19, { a: 'right', s: 13, b: true, c: c.ink, mono: true });
          D.text(g, cl.ex, 382, y + 37, { s: 11, c: c.ink2 });
        }
      });
      if (f.end) box(z, 372, 296, 212, 40, `n² / n = ${(CLS[4].f(f.n) / CLS[2].f(f.n)).toLocaleString('en')} times the work`, { s: 12, b: true, stroke: c.red });
    }
  });
})();
