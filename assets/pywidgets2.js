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

/* =====================================================================================================
   Advanced 4.2  heapq: push with sift up, pop with sift down, shown as a list and as a tree
   ===================================================================================================== */
(() => {
  const { trace, head, codeView, D, box } = PYZ;
  const CODE = ['import heapq', 'heap = []', 'for x in DATA:', '    heapq.heappush(heap, x)', 'smallest = heapq.heappop(heap)'];
  trace('pyheap', {
    title: 'A heap: the smallest item always on top',
    sub: 'heapq keeps a plain list in heap order. Watch each push bubble up and the pop sink down, in the list and in the tree it stands for.',
    W: 600, H: 400,
    params: [{ k: 'data', label: 'Numbers to push', type: 'select', v: '5 3 8 1 9 2', opts: [['5 3 8 1 9 2', '5, 3, 8, 1, 9, 2'], ['1 2 3 4 5 6', '1, 2, 3, 4, 5, 6 (already in order)'], ['6 5 4 3 2 1', '6, 5, 4, 3, 2, 1 (every push goes to the top)']] }],
    tips: [
      { t: 'Numbers that arrive in order never move: each new one is bigger than its parent.', set: { data: '1 2 3 4 5 6' }, play: true },
      { t: 'Numbers in reverse order make every push climb all the way to the top: about log2 n swaps each.', set: { data: '6 5 4 3 2 1' }, play: true }
    ],
    frames(p) {
      const data = p.data.split(' ').map(Number);
      const code = CODE.map(l => l.replace('DATA', '[' + data.join(', ') + ']'));
      const h = [];
      const fr = [];
      const snap = (o) => fr.push({ code, heap: h.slice(), out: null, ...o });
      data.forEach(x => {
        h.push(x);
        let i = h.length - 1;
        snap({ line: 3, hl: [i], say: `heappush(heap, ${x}): ${x} goes on the END of the list, index ${i}. In the tree that is the next free place on the lowest level.` });
        while (i > 0) {
          const pi = (i - 1) >> 1;
          if (h[pi] <= h[i]) {
            snap({ line: 3, hl: [i, pi], ok: true, say: `Its parent is index (${i} &minus; 1) // 2 = ${pi}, holding ${h[pi]}. ${h[pi]} &le; ${h[i]}, so the heap rule holds and the push is done.` });
            break;
          }
          snap({ line: 3, hl: [i, pi], say: `Its parent is index (${i} &minus; 1) // 2 = ${pi}, holding ${h[pi]}. ${h[i]} is smaller than ${h[pi]}, so they swap: <b>sift up</b>.` });
          [h[pi], h[i]] = [h[i], h[pi]];
          i = pi;
          snap({ line: 3, hl: [i], say: i === 0 ? `${h[0]} has reached the top (index 0). It is now the smallest item in the heap.` : `${h[i]} moved up to index ${i}. Compare with the next parent.` });
        }
      });
      const top = h[0];
      snap({ line: 4, hl: [0], say: `heappop(heap): the smallest item is always heap[0], here ${top}. Python takes it out.` });
      const last = h.pop();
      if (h.length) {
        h[0] = last;
        let i = 0;
        snap({ line: 4, hl: [0], out: top, say: `The last item, ${last}, moves into the empty top place. That keeps the tree complete, but ${last} is probably too big for the top.` });
        for (;;) {
          const l = 2 * i + 1, r = l + 1;
          let m = i;
          if (l < h.length && h[l] < h[m]) m = l;
          if (r < h.length && h[r] < h[m]) m = r;
          const kids = [l, r].filter(k => k < h.length);
          if (m === i) {
            snap({ line: 4, hl: [i, ...kids], ok: true, out: top, say: kids.length ? `The children of index ${i} are ${kids.map(k => h[k]).join(' and ')}. ${h[i]} is not bigger than them, so the heap rule holds again.` : `${h[i]} has no children left, so it stops here.` });
            break;
          }
          snap({ line: 4, hl: [i, m], out: top, say: `The children of index ${i} sit at 2 &times; ${i} + 1 and 2 &times; ${i} + 2: ${kids.map(k => h[k]).join(' and ')}. The smaller child ${h[m]} is less than ${h[i]}, so they swap: <b>sift down</b>.` });
          [h[m], h[i]] = [h[i], h[m]];
          i = m;
        }
      }
      snap({ line: 4, hl: [], out: top, end: true, say: `smallest is ${top}. Each push and pop moved an item along one path of the tree, at most about log<sub>2</sub> n swaps, so both are O(log n). The list is NOT sorted, only heap[0] is guaranteed to be the smallest.` });
      return fr;
    },
    paint(z, f) {
      const c = z.col, g = z.g;
      const hlc = c.dark ? '#3a2a10' : '#fff7ed', okc = c.dark ? '#14321f' : '#dcfce7';
      codeView(z, f.code, f.line, 16, 10, 568, { s: 12, lh: 19 });
      head(z, 'heap (the list)', 16, 128);
      f.heap.forEach((v, i) => {
        const x = 16 + i * 52, on = f.hl.includes(i);
        box(z, x, 136, 46, 36, String(v), { mono: true, s: 15, b: on, stroke: on ? (f.ok ? c.green : c.orange) : c.cv, fill: on ? (f.ok ? okc : hlc) : c.surf });
        D.text(g, String(i), x + 23, 186, { a: 'center', s: 11, c: c.ink2 });
      });
      if (f.out !== null) {
        head(z, 'smallest', 470, 128);
        box(z, 470, 136, 114, 36, String(f.out), { mono: true, s: 16, b: true, stroke: c.green, fill: okc });
      }
      head(z, 'The same list as a tree: the parent of i is (i - 1) // 2', 16, 214);
      const pos = i => {
        const lv = Math.floor(Math.log2(i + 1)), k = i - (2 ** lv - 1), n = 2 ** lv;
        return [16 + (k + 0.5) * 568 / n, 244 + lv * 58];
      };
      f.heap.forEach((v, i) => { if (i) { const [x1, y1] = pos(i), [x2, y2] = pos((i - 1) >> 1); D.line(g, x1, y1, x2, y2, c.line, 2); } });
      f.heap.forEach((v, i) => {
        const [x, y] = pos(i), on = f.hl.includes(i);
        D.circle(g, x, y, 18, { fill: on ? (f.ok ? okc : hlc) : c.surf, stroke: on ? (f.ok ? c.green : c.orange) : c.cv, w: on ? 3 : 2 });
        D.text(g, String(v), x, y + 5, { a: 'center', s: 15, b: true, c: c.ink, mono: true });
        D.text(g, String(i), x + 24, y - 12, { s: 10, c: c.ink2 });
      });
    }
  });
})();

/* =====================================================================================================
   Advanced 5.1  threads and processes on a timeline: the GIL, waiting for I/O, and real parallel work
   ===================================================================================================== */
(() => {
  const { trace, head, D, box } = PYZ;
  const MODES = {
    io: { name: 'threads', work: [['run', 1], ['wait', 4], ['run', 1]], gil: true, what: 'download a page: a little Python work, a long wait for the network, a little work' },
    cpu: { name: 'threads', work: [['run', 4]], gil: true, what: 'pure Python number crunching, with no waiting' },
    proc: { name: 'processes', work: [['run', 4]], gil: false, what: 'the same number crunching, each in its own process with its own interpreter' }
  };
  function simulate(m) {
    const ws = [0, 1, 2].map(() => ({ ph: m.work.map(p => [p[0], p[1]]), i: 0 }));
    const cols = [];
    let holder = -1, held = 0;
    while (ws.some(w => w.i < w.ph.length) && cols.length < 30) {
      const col = ws.map(w => (w.i >= w.ph.length ? 'done' : w.ph[w.i][0] === 'wait' ? 'wait' : 'ready'));
      const runnable = col.map((s, k) => (s === 'ready' ? k : -1)).filter(k => k >= 0);
      let runs = [];
      if (!m.gil) runs = runnable;
      else if (runnable.length) {
        let pick = runnable.includes(holder) && held < 1 ? holder : runnable.find(k => k > holder);
        if (pick === undefined) pick = runnable[0];
        held = pick === holder ? held + 1 : 0;
        holder = pick;
        runs = [pick];
      }
      runs.forEach(k => { col[k] = 'run'; });
      cols.push(col);
      ws.forEach((w, k) => {
        if (w.i >= w.ph.length) return;
        const p = w.ph[w.i];
        if (p[0] === 'wait' || runs.includes(k)) { p[1] -= 1; if (p[1] === 0) w.i += 1; }
      });
    }
    return cols;
  }
  trace('pygil', {
    title: 'Three workers on a timeline',
    sub: 'Each column is one unit of time. Pick the kind of work and see what the GIL (global interpreter lock) allows to run at the same time.',
    W: 600, H: 330,
    params: [{ k: 'mode', label: 'Kind of work', type: 'select', v: 'io', opts: [['io', 'Waiting for I/O, with threads'], ['cpu', 'CPU work, with threads'], ['proc', 'CPU work, with processes']] }],
    tips: [
      { t: 'While one thread waits for the network, another can run. Threads help I/O bound work.', set: { mode: 'io' }, play: true },
      { t: 'CPU work with threads: only one runs at a time, so it takes as long as doing the jobs one by one.', set: { mode: 'cpu' }, play: true },
      { t: 'Processes each have their own GIL and run on different cores at the same time.', set: { mode: 'proc' }, play: true }
    ],
    frames(p) {
      const m = MODES[p.mode];
      const cols = simulate(m);
      const seq = 3 * m.work.reduce((a, w) => a + w[1], 0);
      const who = m.gil ? 'Thread' : 'Process';
      const fr = [{ mode: p.mode, upto: 0, seq, total: cols.length, cols, say: `Three ${m.name} each have to ${m.what}. Done one after another, that takes ${seq} units of time.` }];
      cols.forEach((col, t) => {
        const run = col.map((s, k) => (s === 'run' ? `${who} ${k + 1}` : '')).filter(Boolean);
        const wait = col.filter(s => s === 'wait').length, ready = col.map((s, k) => (s === 'ready' ? `${who} ${k + 1}` : '')).filter(Boolean);
        let say = `Time ${t + 1}: ` + (run.length ? `${run.join(' and ')} ${run.length > 1 ? 'run' : 'runs'}` : 'nobody runs');
        if (m.gil && run.length) say += ' while holding the GIL';
        say += '.';
        if (wait) say += ` ${wait} waiting for the network, and waiting does not need the GIL.`;
        if (ready.length) say += ` ${ready.join(' and ')} ${ready.length > 1 ? 'are' : 'is'} ready but must wait for the GIL.`;
        fr.push({ mode: p.mode, upto: t + 1, seq, total: cols.length, cols, say });
      });
      const verdict = p.mode === 'io' ? 'Threads finished much sooner because the waits overlapped.' : p.mode === 'cpu' ? 'No gain: the GIL let only one thread run Python code at a time.' : 'About three times faster: three cores worked at the same time.';
      fr.push({ mode: p.mode, upto: cols.length, seq, total: cols.length, cols, end: true, say: `All done after ${cols.length} units instead of ${seq}. ${verdict}` });
      return fr;
    },
    paint(z, f) {
      const c = z.col, g = z.g;
      const m = MODES[f.mode];
      const fill = { run: c.dark ? '#14532d' : '#86efac', wait: c.dark ? '#1e3a5f' : '#bfdbfe', ready: c.dark ? '#5a3a10' : '#fed7aa', done: c.surf };
      const cw = Math.min(46, 470 / Math.max(f.total, 8));
      head(z, m.gil ? 'One process, one GIL, three threads' : 'Three processes, three GILs, three cores', 16, 18);
      [0, 1, 2].forEach(k => {
        const y = 34 + k * 46;
        D.text(g, (m.gil ? 'Thread ' : 'Process ') + (k + 1), 16, y + 25, { s: 13, b: true, c: c.ink });
        for (let t = 0; t < f.upto; t++) {
          const s = f.cols[t][k];
          D.rect(g, 100 + t * cw, y + 4, cw - 2, 32, { fill: fill[s], stroke: s === 'done' ? c.line : null });
        }
      });
      D.line(g, 100, 178, 100 + Math.max(f.total, 1) * cw, 178, c.line, 1);
      for (let t = 0; t <= f.total; t += 2) D.text(g, String(t), 100 + t * cw, 192, { a: 'center', s: 10, c: c.ink2 });
      D.text(g, 'time', 100 + f.total * cw + 8, 192, { s: 10, c: c.ink2 });
      const leg = [['run', 'running Python code'], ['wait', 'waiting for I/O'], ['ready', 'ready, waiting for the GIL'], ['done', 'finished']];
      leg.forEach(([k, label], i) => {
        const x = [16, 176, 306, 494][i];
        D.rect(g, x, 210, 16, 16, { fill: fill[k], stroke: c.line });
        D.text(g, label, x + 22, 223, { s: 11, c: c.ink2 });
      });
      if (f.upto) box(z, 16, 246, 280, 40, `Time so far: ${f.upto}`, { s: 14, b: true, stroke: c.cv });
      if (f.end) box(z, 304, 246, 280, 40, `One by one: ${f.seq}. Here: ${f.total}`, { s: 14, b: true, stroke: f.total < f.seq ? c.green : c.red });
    }
  });
})();

/* =====================================================================================================
   Advanced 5.2  the asyncio event loop: ready queue, sleeping tasks, the clock, and what blocking does
   ===================================================================================================== */
(() => {
  const { trace, head, codeView, consoleBox, D, box } = PYZ;
  const CODE = {
    gather: ['async def make_tea(name, seconds):', '    print(f"{name}: start")', '    await asyncio.sleep(seconds)', '    print(f"{name}: ready")', '', 'async def main():', '    await asyncio.gather(make_tea("green", 0.3), make_tea("black", 0.2))'],
    seq: ['async def make_tea(name, seconds):', '    print(f"{name}: start")', '    await asyncio.sleep(seconds)', '    print(f"{name}: ready")', '', 'async def main():', '    await make_tea("green", 0.3)', '    await make_tea("black", 0.2)'],
    block: ['async def make_tea(name, seconds):', '    print(f"{name}: start")', '    time.sleep(seconds)          # does not await!', '    print(f"{name}: ready")', '', 'async def main():', '    await asyncio.gather(make_tea("green", 0.3), make_tea("black", 0.2))']
  };
  function script(mode) {
    const S = [];
    let s = { clock: 0, run: '', ready: ['main'], wait: [], out: [], line: 5 };
    const add = (ch, say) => { s = { ...s, ...ch }; S.push({ ...s, ready: s.ready.slice(), wait: s.wait.slice(), out: s.out.slice(), say }); };
    add({}, 'asyncio.run(main()) makes an <b>event loop</b>, wraps main() in a task and puts it in the ready queue. One thread runs everything.');
    if (mode === 'seq') {
      add({ run: 'main', ready: [], line: 6, out: ['green: start'] }, 'The loop runs main. <b>await make_tea(...)</b> on a coroutine runs it straight away inside main. No new task is made, and black has not even been created yet.');
      add({ run: '', wait: ['main (in green) until 0.3'], line: 2 }, 'await asyncio.sleep(0.3) pauses main and hands control back to the loop, with a wake up time of 0.3.');
      add({ clock: 0.3, run: 'main', wait: [], line: 3, out: [...s.out, 'green: ready'] }, 'Nothing else is ready, so the loop waits until 0.3. main wakes up and green finishes.');
      add({ line: 7, out: [...s.out, 'black: start'] }, 'Only now does main reach the second await and start black.');
      add({ run: '', wait: ['main (in black) until 0.5'], line: 2 }, 'black sleeps for 0.2 s, so main parks until 0.3 + 0.2 = 0.5.');
      add({ clock: 0.5, run: 'main', wait: [], line: 3, out: [...s.out, 'black: ready'] }, 'At 0.5 black finishes and main returns.');
      add({ run: '', line: -1, done: true }, 'Total 0.5 s: awaiting coroutines one after another runs them one after another. To overlap the waits you need tasks, for example with gather.');
      return S;
    }
    add({ run: 'main', ready: ['green', 'black'], wait: ['main until both finish'], line: 6 }, 'The loop runs main. gather wraps both coroutines in <b>tasks</b> and puts them in the ready queue. main waits until both are done.');
    add({ run: 'green', ready: ['black'], line: 1, out: ['green: start'] }, 'The loop takes the first ready task, green, and runs it until it reaches an await.');
    if (mode === 'block') {
      add({ clock: 0.3, line: 2 }, '<b>time.sleep</b> is a normal function, not an await. It blocks the only thread for 0.3 s. black is ready but the loop cannot run it: the loop is stuck inside green.');
      add({ run: '', ready: ['black'], line: 3, out: [...s.out, 'green: ready'] }, 'green finishes at 0.3 without ever giving control back.');
      add({ run: 'black', ready: [], line: 1, out: [...s.out, 'black: start'] }, 'Only now can black start.');
      add({ clock: 0.5, line: 2 }, 'black blocks the thread with time.sleep for its own 0.2 s, until 0.5.');
      add({ line: 3, out: [...s.out, 'black: ready'] }, 'black finishes at 0.5.');
      add({ run: 'main', wait: [], line: 6 }, 'Both tasks are done, so main wakes up and gather returns.');
      add({ run: '', line: -1, done: true }, 'Total 0.5 s, as slow as doing it in a row. One blocking call freezes every task. Use await asyncio.sleep, an async library, or asyncio.to_thread for blocking code.');
      return S;
    }
    add({ run: '', wait: ['main until both finish', 'green until 0.3'], line: 2 }, 'await asyncio.sleep(0.3) pauses green. It goes to the waiting list with a wake up time of 0.3, and the loop is free again.');
    add({ run: 'black', ready: [], line: 1, out: [...s.out, 'black: start'] }, 'The loop runs the next ready task, black, at the same moment, time 0.');
    add({ run: '', wait: ['main until both finish', 'green until 0.3', 'black until 0.2'], line: 2 }, 'black sleeps too, until 0.2. Now nothing is ready.');
    add({ clock: 0.2, run: 'black', wait: ['main until both finish', 'green until 0.3'], line: 3, out: [...s.out, 'black: ready'] }, 'The loop waits until the earliest wake up time, 0.2. black wakes up and finishes.');
    add({ clock: 0.3, run: 'green', wait: ['main until both finish'], line: 3, out: [...s.out, 'green: ready'] }, 'At 0.3 green wakes up and finishes.');
    add({ run: 'main', wait: [], line: 6 }, 'Both tasks are done, so main wakes up and gather returns ["green", "black"], in the order they were passed in.');
    add({ run: '', line: -1, done: true }, 'Total 0.3 s instead of 0.5 s: the two waits happened at the same time, in one thread, with no locks.');
    return S;
  }
  trace('pyloop', {
    title: 'Inside the asyncio event loop',
    sub: 'One thread, one loop. Watch tasks move between running, ready and waiting while the clock advances.',
    W: 600, H: 410,
    params: [{ k: 'mode', label: 'How main runs the two teas', type: 'select', v: 'gather', opts: [['gather', 'asyncio.gather (overlap the waits)'], ['seq', 'await one after the other'], ['block', 'gather, but with time.sleep inside']] }],
    tips: [
      { t: 'gather: both teas wait at the same time, 0.3 s in total.', set: { mode: 'gather' }, play: true },
      { t: 'Awaiting one coroutine after another: 0.5 s.', set: { mode: 'seq' }, play: true },
      { t: 'One time.sleep blocks the whole loop.', set: { mode: 'block' }, play: true }
    ],
    frames(p) { return script(p.mode).map(f => ({ ...f, mode: p.mode })); },
    paint(z, f) {
      const c = z.col;
      codeView(z, CODE[f.mode], f.line, 16, 8, 568, { s: 11.5, lh: 17 });
      const y0 = 160;
      head(z, 'Clock', 16, y0);
      box(z, 16, y0 + 8, 100, 40, f.clock.toFixed(1) + ' s', { mono: true, s: 16, b: true, stroke: c.cv });
      head(z, 'Running now', 130, y0);
      box(z, 130, y0 + 8, 140, 40, f.run || (f.done ? 'finished' : '(the loop)'), { mono: true, s: 13, b: !!f.run, stroke: f.run ? c.green : c.line, fill: f.run ? (c.dark ? '#14321f' : '#dcfce7') : c.surf });
      head(z, 'Ready queue', 284, y0);
      if (!f.ready.length) box(z, 284, y0 + 8, 300, 40, '(empty)', { s: 12, c: c.ink2 });
      f.ready.forEach((r, i) => box(z, 284 + i * 104, y0 + 8, 96, 40, r, { mono: true, s: 13, stroke: c.orange, fill: c.dark ? '#3a2a10' : '#fff7ed' }));
      head(z, 'Waiting (awaiting a sleep or another task)', 16, y0 + 74);
      if (!f.wait.length) box(z, 16, y0 + 82, 568, 34, '(nobody)', { s: 12, c: c.ink2 });
      f.wait.forEach((w, i) => box(z, 16 + i * 192, y0 + 82, 184, 34, w, { mono: true, s: 11, stroke: c.cv }));
      consoleBox(z, f.out.join('\n') || '(nothing printed yet)', 16, y0 + 130, 568, 100, { title: 'Output' });
    }
  });
})();

/* =====================================================================================================
   Advanced 6.1  how the regex engine walks the text: try a start, match token by token, back off, give up
   ===================================================================================================== */
(() => {
  const { trace, head, D, box, esc } = PYZ;
  const CASES = {
    phone: { pat: '\\d{3}-\\d{4}', text: 'call 555-1234 now' },
    greedy: { pat: '<.+>', text: 'x <b>hi</b>' },
    lazy: { pat: '<.+?>', text: 'x <b>hi</b>' },
    word: { pat: '\\bcat\\b', text: 'concat cat' }
  };
  function tokens(p) {
    const out = [];
    let i = 0;
    while (i < p.length) {
      let atom = p[i], kind = 'lit';
      if (p[i] === '\\') { atom = p.slice(i, i + 2); kind = { d: 'digit', w: 'word', s: 'space', b: 'edge' }[p[i + 1]] || 'lit'; if (kind === 'lit') atom = p[i + 1]; i += 2; }
      else { if (p[i] === '.') kind = 'any'; i += 1; }
      let min = 1, max = 1, lazy = false, q = '';
      const m = /^(\{(\d+)\}|\+|\*|\?)(\?)?/.exec(p.slice(i));
      if (m) {
        q = m[0];
        if (m[2]) { min = max = +m[2]; } else if (m[1] === '+') { min = 1; max = 99; } else if (m[1] === '*') { min = 0; max = 99; } else { min = 0; max = 1; }
        lazy = !!m[3];
        i += m[0].length;
      }
      out.push({ src: (kind === 'lit' ? atom : (atom.length > 1 ? atom : atom)) + q, kind, ch: atom, min, max, lazy });
    }
    return out;
  }
  const isW = c => /\w/.test(c || '');
  function ok(t, c) {
    if (c === undefined) return false;
    if (t.kind === 'digit') return /\d/.test(c);
    if (t.kind === 'word') return /\w/.test(c);
    if (t.kind === 'space') return /\s/.test(c);
    if (t.kind === 'any') return c !== '\n';
    return c === t.ch;
  }
  function frames(pat, text) {
    const T = tokens(pat), fr = [];
    const add = (o, say) => fr.push({ T, text, pat, ...o, spans: (o.spans || []).map(s => s.slice()), say: esc(say).replace(/\*\*(.+?)\*\*/g, '<b>$1</b>') });
    add({ start: -1, pos: -1, tok: -1 }, `re.search(r"${pat}", "${text}") looks for the pattern anywhere in the text. The engine tries each starting place from left to right.`);
    let steps = 0;
    function walk(start, ti, j, spans) {
      if (steps++ > 60) return false;
      if (ti === T.length) return true;
      const t = T[ti];
      if (t.kind === 'edge') {
        const edge = isW(text[j - 1]) !== isW(text[j]);
        add({ start, pos: j, tok: ti, spans, bad: !edge }, edge ? `\\b checks for a word edge between "${text[j - 1] || 'start'}" and "${text[j] || 'end'}": there is one. It uses up no characters.` : `\\b needs a word edge here, between "${text[j - 1] || 'start'}" and "${text[j] || 'end'}", but both sides are letters. Fail.`);
        return edge && walk(start, ti + 1, j, spans);
      }
      let n = 0;
      while (n < t.max && ok(t, text[j + n])) n++;
      if (n < t.min) {
        add({ start, pos: j + n, tok: ti, spans, bad: true }, `${t.src} needs ${t.min === 1 && t.max === 1 ? 'one character like that' : 'at least ' + t.min + ' of them'}, but finds "${text[j + n] === undefined ? 'the end' : text[j + n]}". This start fails.`);
        return false;
      }
      const order = [];
      if (t.lazy) for (let k = t.min; k <= n; k++) order.push(k); else for (let k = n; k >= t.min; k--) order.push(k);
      for (let a = 0; a < order.length; a++) {
        const k = order[a];
        const sp = spans.concat([[ti, j, j + k]]);
        let say;
        if (a === 0) say = t.max === 1 && t.min === 1 ? `The token ${t.src} matches "${text[j]}".` : t.lazy ? `${t.src} is **lazy**: it takes as FEW as it may, ${k} character${k === 1 ? '' : 's'} ("${text.slice(j, j + k)}"), and only takes more if the rest fails.` : `${t.src} is **greedy**: it takes as MANY as it can, ${k} character${k === 1 ? '' : 's'}: "${text.slice(j, j + k)}".`;
        else say = t.lazy ? `The rest failed, so the lazy ${t.src} takes one more: "${text.slice(j, j + k)}".` : `The rest failed, so ${t.src} **backtracks**: it gives back one character and keeps "${text.slice(j, j + k)}".`;
        add({ start, pos: j + k, tok: ti, spans: sp }, say);
        if (walk(start, ti + 1, j + k, sp)) return true;
      }
      return false;
    }
    for (let s = 0; s <= text.length; s++) {
      add({ start: s, pos: s, tok: 0, spans: [] }, `Try starting at index ${s} ("${text[s] === undefined ? 'end' : text[s]}").`);
      const before = fr.length;
      if (walk(s, 0, s, [])) {
        const last = fr[fr.length - 1];
        const end = last.spans.length ? Math.max(...last.spans.map(x => x[2])) : s;
        add({ start: s, pos: end, tok: -1, spans: last.spans, done: [s, end] }, `Every token matched. The match is "${text.slice(s, end)}", span (${s}, ${end}). search stops at the FIRST match.`);
        return fr;
      }
      if (fr.length - before > 0 && fr.length > 40) {
        fr.splice(before);
        add({ start: s, pos: s, tok: 0, spans: [], bad: true }, `Index ${s} fails too.`);
      }
    }
    add({ start: -1, pos: -1, tok: -1, spans: [], none: true }, 'No starting place worked: search returns None.');
    return fr;
  }
  trace('pyregex', {
    title: 'How the regex engine walks through the text',
    sub: 'Pick a pattern. The engine tries each start, matches token by token, and backs off when the rest does not fit.',
    W: 600, H: 300,
    params: [{ k: 'case', label: 'Pattern and text', type: 'select', v: 'phone', opts: [['phone', '\\d{3}-\\d{4} in "call 555-1234 now"'], ['greedy', '<.+> (greedy) in "x <b>hi</b>"'], ['lazy', '<.+?> (lazy) in "x <b>hi</b>"'], ['word', '\\bcat\\b in "concat cat"']] }],
    tips: [
      { t: 'Greedy .+ runs to the end of the text and then backs off to the LAST >.', set: { case: 'greedy' }, play: true },
      { t: 'Lazy .+? stops at the FIRST > that lets the match finish.', set: { case: 'lazy' }, play: true },
      { t: '\\b refuses the "cat" inside "concat".', set: { case: 'word' }, play: true }
    ],
    frames(p) { const c = CASES[p.case]; return frames(c.pat, c.text); },
    paint(z, f) {
      const c = z.col, g = z.g;
      const cols = [c.cv, c.orange, c.green, c.dark ? '#c4b5fd' : '#7c3aed', c.red];
      head(z, 'Pattern r"' + f.pat + '" as tokens', 16, 18);
      let x = 16;
      f.T.forEach((t, i) => {
        const w = Math.max(44, t.src.length * 10 + 18);
        box(z, x, 28, w, 34, t.src, { mono: true, s: 14, b: i === f.tok, stroke: i === f.tok ? (f.bad ? c.red : cols[i % 5]) : c.line, fill: i === f.tok && f.bad ? (c.dark ? '#3b1414' : '#fee2e2') : c.surf });
        x += w + 8;
      });
      head(z, 'Text', 16, 92);
      const cw = Math.min(32, 568 / f.text.length);
      for (let i = 0; i < f.text.length; i++) {
        const xi = 16 + i * cw;
        const sp = f.spans.find(s => i >= s[1] && i < s[2]);
        const fill = sp ? cols[sp[0] % 5] : (f.done && i >= f.done[0] && i < f.done[1] ? c.green : c.surf);
        D.rect(g, xi, 102, cw - 2, 38, { fill: sp ? (c.dark ? '#1f2937' : '#f1f5f9') : c.surf, stroke: sp ? fill : c.line, w: sp ? 2.5 : 1 });
        D.text(g, f.text[i] === ' ' ? '·' : f.text[i], xi + cw / 2 - 1, 127, { a: 'center', s: 15, b: !!sp, c: sp ? fill : c.ink, mono: true });
        D.text(g, String(i), xi + cw / 2 - 1, 154, { a: 'center', s: 10, c: c.ink2 });
      }
      if (f.start >= 0) {
        const xs = 16 + f.start * cw + cw / 2 - 1;
        D.text(g, 'start', xs, 172, { a: 'center', s: 11, b: true, c: c.cv });
        D.line(g, xs, 160, xs, 146, c.cv, 2);
      }
      if (f.pos >= 0 && !f.done) {
        const xp = 16 + f.pos * cw - 1;
        D.line(g, xp, 98, xp, 144, f.bad ? c.red : c.orange, 3);
      }
      if (f.done) box(z, 16, 196, 568, 44, `match: "${f.text.slice(f.done[0], f.done[1])}"   span (${f.done[0]}, ${f.done[1]})`, { mono: true, s: 15, b: true, stroke: c.green, fill: c.dark ? '#14321f' : '#dcfce7' });
      if (f.none) box(z, 16, 196, 568, 44, 'None: no match', { mono: true, s: 15, b: true, stroke: c.red });
    }
  });
})();

/* =====================================================================================================
   Advanced 6.2  turning Python objects into JSON or CSV text and back, and what changes on the way
   ===================================================================================================== */
(() => {
  const { trace, head, D, box, consoleBox } = PYZ;
  const MODES = {
    json: {
      left: 'Python dict', right: 'json.dumps(order, indent=2)',
      rows: [
        ['order = {', '{', 'json.dumps starts. A Python <b>dict</b> becomes a JSON <b>object</b> in curly brackets.'],
        ['    "id": 7,', '  "id": 7,', 'Strings and whole numbers look the same in JSON. JSON strings always use double quotes.'],
        ['    "paid": True,', '  "paid": true,', 'True becomes <b>true</b> (lower case). False would become false.'],
        ['    "items": ("tea", "cake"),', '  "items": ["tea", "cake"],', 'JSON has no tuples. A tuple (and a list) becomes an <b>array</b> in square brackets.', 1],
        ['    "note": None,', '  "note": null,', 'None becomes <b>null</b>.'],
        ['    2: "two",', '  "2": "two"', 'JSON object keys must be strings, so the int key 2 is turned into "2".', 1],
        ['}', '}', 'The object closes. The result is plain text that any language can read.']
      ],
      back: 'json.loads(text)', backText: "{'id': 7, 'paid': True, 'items': ['tea', 'cake'],\n 'note': None, '2': 'two'}",
      backSay: 'Reading the text back gives a dict again, but not the same one: items is now a <b>list</b>, not a tuple, and the key is the <b>string</b> "2". Sets, dates and your own classes cannot be written at all without a default= function.'
    },
    csv: {
      left: 'Python list of dicts', right: 'csv.DictWriter output',
      rows: [
        ['fieldnames = ["name", "city", "age"]', 'name,city,age', 'writeheader() writes the field names as the first line.'],
        ['{"name": "Ann", "city": "Paris", "age": 31}', 'Ann,Paris,31', 'writerow turns each value into text and puts commas between them.'],
        ['{"name": "Smith, Bo", "city": "Rome", "age": 25}', '"Smith, Bo",Rome,25', 'This name contains a comma, so the writer puts it in double quotes. Never build CSV lines with ",".join yourself.', 1],
        ['{"name": "Cy", "city": "Oslo"}', 'Cy,Oslo,', 'A missing key gives an empty field (restval="" by default).'],
        ['(end of each row)', '\\r\\n', 'Every row ends with \\r\\n. Open the file with newline="" so Python does not change these line endings.']
      ],
      back: 'list(csv.DictReader(f))', backText: "[{'name': 'Ann', 'city': 'Paris', 'age': '31'},\n {'name': 'Smith, Bo', 'city': 'Rome', 'age': '25'},\n {'name': 'Cy', 'city': 'Oslo', 'age': ''}]",
      backSay: 'Reading the file back gives dicts again. The quotes are removed, so "Smith, Bo" is one field, but every value is a <b>string</b>: 31 came back as "31". Convert numbers yourself with int().'
    }
  };
  trace('pyformat', {
    title: 'From Python objects to text and back',
    sub: 'Each step writes one piece. The last step reads the text back and shows what changed on the way.',
    W: 600, H: 400,
    params: [{ k: 'mode', label: 'Format', type: 'select', v: 'json', opts: [['json', 'JSON (json.dumps and json.loads)'], ['csv', 'CSV (csv.DictWriter and DictReader)']] }],
    tips: [
      { t: 'JSON: watch the tuple and the int key change.', set: { mode: 'json' }, play: true },
      { t: 'CSV: a comma inside a value needs quotes, and numbers come back as strings.', set: { mode: 'csv' }, play: true }
    ],
    frames(p) {
      const m = MODES[p.mode];
      const fr = m.rows.map((r, i) => ({ mode: p.mode, upto: i + 1, back: false, say: r[2] }));
      fr.push({ mode: p.mode, upto: m.rows.length, back: true, say: m.backSay });
      return fr;
    },
    paint(z, f) {
      const c = z.col, g = z.g, m = MODES[f.mode];
      head(z, m.left, 16, 18);
      head(z, m.right, 316, 18);
      m.rows.slice(0, f.upto).forEach((r, i) => {
        const y = 28 + i * 34, cur = i === f.upto - 1 && !f.back, warn = r[3];
        box(z, 16, y, 270, 28, '', { stroke: cur ? c.cv : c.line, b: cur });
        D.text(g, r[0], 24, y + 18, { s: r[0].length > 34 ? 10 : 11.5, mono: true, c: c.ink });
        D.arrow(g, 290, y + 14, 312, y + 14, cur ? c.cv : c.line, 2, 6);
        box(z, 316, y, 268, 28, '', { stroke: warn ? c.orange : (cur ? c.cv : c.line), b: cur, fill: warn ? (c.dark ? '#3a2a10' : '#fff7ed') : c.surf });
        D.text(g, r[1], 324, y + 18, { s: 11.5, mono: true, c: warn ? c.orange : c.ink });
      });
      if (f.back) consoleBox(z, m.backText, 16, 280, 568, 100, { title: m.back + ' gives' });
    }
  });
})();

/* =====================================================================================================
   Advanced 6.3  sqlite3: the order a SELECT really runs in, SQL injection against ? placeholders, and a
   transaction that rolls back
   ===================================================================================================== */
(() => {
  const { trace, head, codeView, D, box } = PYZ;
  const R = (v, s) => ({ v, s: s || '' });
  const ORDER_SQL = ['SELECT c.city, SUM(o.amount) AS total', 'FROM customers c JOIN orders o ON o.customer_id = c.id', 'WHERE o.amount >= 20', 'GROUP BY c.city', 'HAVING total > 60', 'ORDER BY total DESC', 'LIMIT 1'];
  const JOINED = [['Ann', 'Paris', 30], ['Ann', 'Paris', 20], ['Bo', 'Rome', 70], ['Cy', 'Paris', 15], ['Cy', 'Paris', 25], ['Di', 'Oslo', 50]];
  const G = { Paris: 'g0', Rome: 'g1', Oslo: 'g2' };
  const INJ_SQL = ['name = input("User name: ")', 'sql = f"SELECT * FROM users WHERE name = \'{name}\'"', 'conn.execute(sql).fetchall()', 'conn.execute("SELECT * FROM users WHERE name = ?", (name,)).fetchall()'];
  const USERS = [['ann', 's3cret'], ['bo', 'hunter2'], ['cy', 'pa55']];
  const TXN_SQL = ['with conn:', '    conn.execute("UPDATE accounts SET balance = balance + 500 WHERE name = \'ann\'")', '    conn.execute("UPDATE accounts SET balance = balance - 500 WHERE name = \'bo\'")', 'print(conn.execute("SELECT * FROM accounts").fetchall())'];
  const MODES = {
    order: () => {
      const cols = ['name', 'city', 'amount'], w = [0.3, 0.35, 0.35];
      const groups = [['Paris', '30, 20, 25', 75], ['Rome', '70', 70], ['Oslo', '50', 50]];
      return [
        { cur: 1, cols, w, title: 'Rows after FROM and JOIN', rows: JOINED.map(r => R(r)), say: 'The database does not start with SELECT. It starts with <b>FROM</b>: the JOIN pairs every order with the customer it belongs to. Ed, a customer with no orders, is not here, because a plain (inner) JOIN keeps only rows that have a partner.' },
        { cur: 2, cols, w, title: 'WHERE checks one row at a time', rows: JOINED.map(r => R(r, r[2] >= 20 ? '' : 'bad')), say: '<b>WHERE</b> looks at each row on its own and throws away the rows where the test is false. Cy\'s order of 15 is removed.' },
        { cur: 3, cols, w, title: 'GROUP BY puts rows with the same city together', rows: JOINED.filter(r => r[2] >= 20).map(r => R(r, G[r[1]])), say: '<b>GROUP BY</b> c.city collects the rows that share a city. Each colour is one group. Every group will become ONE row in the result.' },
        { cur: 4, cols: ['city', 'amounts in the group', 'SUM(o.amount)'], w: [0.3, 0.4, 0.3], title: 'One row per group, then HAVING', rows: groups.map(r => R(r, r[2] > 60 ? '' : 'bad')), say: 'SUM adds up each group: Paris 75, Rome 70, Oslo 50. <b>HAVING</b> is a WHERE for groups. It runs after the sums exist, so it can test total &gt; 60. Oslo is removed.' },
        { cur: 0, cols: ['city', 'total'], w: [0.5, 0.5], title: 'SELECT picks the columns', rows: [R(['Paris', 75]), R(['Rome', 70])], say: 'Only now does <b>SELECT</b> run and give the columns their names. This is why WHERE cannot use the name total: it does not exist yet when WHERE runs.' },
        { cur: 5, cols: ['city', 'total'], w: [0.5, 0.5], title: 'ORDER BY sorts the result', rows: [R(['Paris', 75], 'new'), R(['Rome', 70])], say: '<b>ORDER BY</b> total DESC sorts the finished rows, biggest first. Without ORDER BY the database may return rows in any order it likes.' },
        { cur: 6, cols: ['city', 'total'], w: [0.5, 0.5], title: 'LIMIT keeps the first rows', rows: [R(['Paris', 75], 'ok'), R(['Rome', 70], 'dim')], out: "[('Paris', 75.0)]", say: '<b>LIMIT</b> 1 keeps only the first row. The full order is FROM, WHERE, GROUP BY, HAVING, SELECT, ORDER BY, LIMIT, not the order the words are written in.' }
      ];
    },
    inject: () => {
      const cols = ['name', 'password'], w = [0.5, 0.5], all = USERS.map(r => R(r));
      const typed = "nobody' OR '1'='1";
      return [
        { cur: 0, cols, w, title: 'Table users', rows: all, out: 'name = "' + typed + '"', say: 'A login form asks for a user name. An attacker types <b>' + typed + '</b>, with quote characters on purpose.' },
        { cur: 1, cols, w, title: 'Table users', rows: all, out: "SELECT * FROM users WHERE name = 'nobody' OR '1'='1'", say: 'The f-string pastes the text straight into the SQL. Python does not know it is building SQL, so the quotes go in as they are.' },
        { cur: 1, cols, w, title: 'Table users', rows: all, out: "name = 'nobody'   OR   '1'='1'", bad: true, say: 'The database reads the quote after nobody as the END of the string. The rest, <b>OR \'1\'=\'1\'</b>, is now SQL code, and \'1\'=\'1\' is true for every row.' },
        { cur: 2, cols, w, title: 'Rows returned', rows: USERS.map(r => R(r, 'bad')), out: "[('ann', 's3cret'), ('bo', 'hunter2'), ('cy', 'pa55')]", say: 'Every user comes back, so the attacker is "logged in" without a password. This is <b>SQL injection</b>, one of the most common security holes on the web.' },
        { cur: 3, cols, w, title: 'Table users', rows: all, out: 'SQL: ... WHERE name = ?      value: "' + typed + '"', say: 'With a <b>? placeholder</b> the SQL text and the value travel separately. The database first reads the SQL, then fills ? with the value as plain data. Quotes inside the value are just letters.' },
        { cur: 3, cols, w, title: 'Rows returned', rows: USERS.map(r => R(r, 'dim')), out: '[]', say: 'No user has that strange name, so nothing comes back. Always use ? (or :name) for values. Never build SQL with f-strings, + or .format().' }
      ];
    },
    txn: () => {
      const cols = ['name', 'saved in the file', 'inside this transaction'], w = [0.25, 0.375, 0.375];
      return [
        { cur: 0, cols, w, title: 'Table accounts, CHECK (balance >= 0)', rows: [R(['ann', 100, 100]), R(['bo', 50, 50])], say: 'Bo sends 500 to Ann. <b>with conn:</b> starts a block. The first change will open a <b>transaction</b>: changes stay private until commit.' },
        { cur: 1, cols, w, title: 'Table accounts, CHECK (balance >= 0)', rows: [R(['ann', 100, 600], 'new'), R(['bo', 50, 50])], say: 'The first UPDATE gives Ann 500 more. Inside the transaction she has 600, but nothing is saved yet: other connections still see 100.' },
        { cur: 2, cols, w, title: 'Table accounts, CHECK (balance >= 0)', rows: [R(['ann', 100, 600], 'new'), R(['bo', 50, -450], 'bad')], bad: true, out: 'sqlite3.IntegrityError: CHECK constraint failed: balance >= 0', say: 'Bo only has 50. His new balance would be -450, so the CHECK rule fails and SQLite raises <b>IntegrityError</b>. Ann already got the money, so the data is now half done.' },
        { cur: 0, cols, w, title: 'Table accounts, CHECK (balance >= 0)', rows: [R(['ann', 100, 100], 'ok'), R(['bo', 50, 50])], say: 'The exception leaves the with block, so <b>with conn</b> calls <b>rollback()</b>. Every change since the transaction began is undone, including Ann\'s 500.' },
        { cur: 3, cols, w, title: 'Table accounts after the block', rows: [R(['ann', 100, 100], 'ok'), R(['bo', 50, 50], 'ok')], out: "[('ann', 100), ('bo', 50)]", say: 'Either both updates happen or neither does. This all or nothing rule is <b>atomicity</b>, the A in ACID. If the block had finished without an error, with conn would have called commit().' }
      ];
    }
  };
  trace('pysql', {
    title: 'Inside a database query',
    sub: 'Pick a case. Each step runs one part and shows the rows the database holds at that moment.',
    W: 600, H: 420,
    params: [{ k: 'case', label: 'Case', type: 'select', v: 'order', opts: [['order', 'The real order a SELECT runs in'], ['inject', 'SQL injection and ? placeholders'], ['txn', 'A transaction that rolls back']] }],
    tips: [
      { t: 'Order: WHERE runs before GROUP BY, and SELECT runs almost last.', set: { case: 'order' }, play: true },
      { t: 'Injection: one quote in the input changes the meaning of the SQL.', set: { case: 'inject' }, play: true },
      { t: 'Transaction: a failed second update undoes the first one.', set: { case: 'txn' }, play: true }
    ],
    frames(p) { return MODES[p.case]().map(f => ({ ...f, mode: p.case })); },
    paint(z, f) {
      const c = z.col, g = z.g;
      const sql = f.mode === 'order' ? ORDER_SQL : f.mode === 'inject' ? INJ_SQL : TXN_SQL;
      head(z, f.mode === 'order' ? 'SQL as written' : 'Python code', 16, 18);
      const y0 = codeView(z, sql, f.cur, 16, 26, 568, { lh: 21, s: 12, bad: f.bad ? f.cur : undefined }) + 26;
      head(z, f.title, 16, y0);
      const x0 = 16, W = 568, rh = 26;
      let x = x0;
      const xs = f.w.map(fr => { const a = x; x += fr * W; return a; });
      f.cols.forEach((h, i) => {
        box(z, xs[i], y0 + 8, f.w[i] * W - 4, rh, h, { s: 12, b: true, fill: c.dark ? '#1e293b' : '#e2e8f0' });
      });
      const gcol = { g0: c.cv, g1: c.orange, g2: c.dark ? '#c4b5fd' : '#7c3aed' };
      f.rows.forEach((r, j) => {
        const y = y0 + 8 + (j + 1) * (rh + 3);
        const st = r.s;
        const stroke = st === 'bad' ? c.red : st === 'new' ? c.orange : st === 'ok' ? c.green : gcol[st] || c.line;
        const fill = st === 'bad' ? (c.dark ? '#3b1414' : '#fee2e2') : st === 'ok' ? (c.dark ? '#14321f' : '#dcfce7') : st === 'new' ? (c.dark ? '#3a2a10' : '#fff7ed') : c.surf;
        r.v.forEach((v, i) => {
          box(z, xs[i], y, f.w[i] * W - 4, rh, String(v), { s: 12.5, mono: true, stroke, fill, w: st && st !== 'dim' ? 2 : 1.5, c: st === 'dim' ? c.ink2 : st === 'bad' ? c.red : undefined });
        });
        if (st === 'bad' && f.mode === 'order') D.line(g, x0 + 6, y + rh / 2, x0 + W - 10, y + rh / 2, c.red, 1.5);
      });
      if (f.out) {
        const yo = z.H - 46;
        box(z, 16, yo, 568, 36, f.out, { mono: true, s: 13, b: true, stroke: f.bad ? c.red : c.cv, fill: f.bad ? (c.dark ? '#3b1414' : '#fee2e2') : (c.dark ? '#0f2742' : '#eff6ff'), c: f.bad ? c.red : undefined });
      }
    }
  });
})();

/* =====================================================================================================
   Advanced 6.4  tkinter: what mainloop does with events, why a slow callback freezes the window, and how grid
   places widgets in rows and columns
   ===================================================================================================== */
(() => {
  const { trace, head, codeView, D, box } = PYZ;
  const { rr } = AIZ;
  const LOOP_CODE = ['root = tk.Tk()', 'label = tk.Label(root, text="Press the button")', 'button = tk.Button(root, text="Say hello", command=say_hello)', 'root.mainloop()', 'def say_hello(): label.config(text="Hello!")'];
  const FREEZE_CODE = ['def bad_click():', '    time.sleep(3)', '    status.config(text="Done")', 'def good_click():', '    root.after(3000, finish)', 'def finish(): status.config(text="Done")'];
  const GRID_CODE = ['ttk.Label(root, text="Name:").grid(row=0, column=0, sticky="e")', 'name_entry.grid(row=0, column=1, sticky="ew")', 'ttk.Label(root, text="Age:").grid(row=1, column=0, sticky="e")', 'age_entry.grid(row=1, column=1, sticky="w")', 'button.grid(row=2, column=0, columnspan=2)', 'root.columnconfigure(1, weight=1)'];
  const CASES = {
    loop: [
      { cur: 0, win: 1, say: '<b>tk.Tk()</b> makes the main window, called root. It is still empty, and Python keeps running the next lines.' },
      { cur: 1, win: 1, label: 'Press the button', say: 'A <b>Label</b> shows text. root is its parent, so it lives inside the window. (pack() or grid() places it, here we skip that line.)' },
      { cur: 2, win: 1, label: 'Press the button', btn: 1, say: 'A <b>Button</b> with command=say_hello. Note: say_hello WITHOUT brackets. We hand Tk the function to call later, we do not call it now.' },
      { cur: 3, win: 2, label: 'Press the button', btn: 1, loop: 'waiting', q: [], say: '<b>root.mainloop()</b> shows the window and starts the <b>event loop</b>: wait for an event, handle it, wait again. The program now stays on this line until the window closes.' },
      { cur: 3, win: 2, label: 'Press the button', btn: 2, loop: 'waiting', q: ['click on button'], say: 'The user clicks the button. The operating system sends a mouse event, and Tk puts it in the <b>event queue</b>.' },
      { cur: 4, win: 2, label: 'Press the button', btn: 2, loop: 'running say_hello()', q: [], say: 'mainloop takes the event from the queue, sees that the button has a command, and calls <b>say_hello()</b>.' },
      { cur: 4, win: 2, label: 'Hello!', btn: 1, loop: 'redraw', q: [], hl: 1, say: 'label.config(text="Hello!") changes the label. When the function returns, mainloop <b>redraws</b> the window with the new text.' },
      { cur: 3, win: 2, label: 'Hello!', btn: 1, loop: 'waiting', q: [], say: 'mainloop waits for the next event. Every GUI program works like this: your code runs only when an event calls one of your functions. This style is called <b>event driven</b> programming.' }
    ],
    freeze: [
      { cur: 0, win: 2, label: 'Press a button', loop: 'running bad_click()', q: [], say: 'The user clicks "bad way". mainloop calls <b>bad_click()</b> and waits for it to return.' },
      { cur: 1, win: 3, label: 'Press a button', loop: 'stuck in time.sleep(3)', q: ['redraw window'], say: '<b>time.sleep(3)</b> blocks. mainloop cannot take the next event, so the window cannot even redraw itself. It looks dead, and the system may say "Not Responding".' },
      { cur: 1, win: 3, label: 'Press a button', loop: 'stuck in time.sleep(3)', q: ['redraw window', 'click on button', 'move window'], say: 'The user clicks again and drags the window. These events only pile up in the queue. Nothing happens on screen.' },
      { cur: 2, win: 2, label: 'Done', loop: 'handling the pile', q: [], say: 'After 3 seconds bad_click returns. mainloop now handles the whole pile at once: the window jumps, and the second click runs bad_click AGAIN, freezing it for 3 more seconds.' },
      { cur: 4, win: 2, label: 'Press a button', loop: 'running good_click()', timer: 'finish() in 3000 ms', q: [], say: 'Now "good way": <b>root.after(3000, finish)</b> only sets a timer and returns at once. after() means "call this function later, from the event loop".' },
      { cur: 4, win: 2, label: 'Press a button', loop: 'waiting', timer: 'finish() in 1200 ms', q: [], live: 1, say: 'While the timer runs, mainloop keeps handling clicks, redraws and window moves. The window stays alive.' },
      { cur: 5, win: 2, label: 'Done', loop: 'running finish()', q: [], hl: 1, say: 'The timer fires and mainloop calls <b>finish()</b>. The rule: every callback must return quickly. For long work use after() in small steps, or a thread that reports back through a queue.' }
    ],
    grid: [
      { cur: 0, put: 1, say: '<b>grid</b> places widgets in a table of rows and columns. The "Name:" label goes in row 0, column 0. sticky="e" pushes it to the east (right) side of its cell.' },
      { cur: 1, put: 2, say: 'The name entry goes in row 0, column 1. sticky="ew" stretches it from west to east, so it fills the width of its cell.' },
      { cur: 2, put: 3, say: 'Row 1, column 0: the "Age:" label, again on the right of its cell, so the colons line up.' },
      { cur: 3, put: 4, say: 'The age entry is short and sticks to the west (left) side. Each column is as wide as its widest widget.' },
      { cur: 4, put: 5, say: '<b>columnspan=2</b> lets the button use both columns of row 2. Without sticky it sits in the middle.' },
      { cur: 5, put: 5, grow: 1, say: 'The user makes the window wider. <b>columnconfigure(1, weight=1)</b> gives all the extra width to column 1, so the name entry grows and the labels stay the same. With weight 0 (the default) the extra space would stay empty.' }
    ]
  };
  function windowBox(z, x, y, w, h, f, title) {
    const c = z.col, g = z.g;
    const dead = f.win === 3;
    rr(g, x, y, w, h, 8, { fill: c.surf, stroke: f.win === 1 ? c.line : c.cv, w: 2, dash: f.win === 1 ? [5, 4] : null });
    rr(g, x, y, w, 24, 8, { fill: dead ? (c.dark ? '#374151' : '#d1d5db') : (c.dark ? '#1e293b' : '#e2e8f0'), stroke: f.win === 1 ? c.line : c.cv, w: 2, dash: f.win === 1 ? [5, 4] : null });
    D.text(g, title + (dead ? '  (Not Responding)' : f.win === 1 ? '  (not on screen yet)' : ''), x + 10, y + 16, { s: 11.5, b: true, c: dead ? c.red : c.ink });
  }
  function queue(z, f, x, y) {
    const c = z.col, g = z.g;
    head(z, 'Event queue', x, y);
    const q = f.q || [];
    if (!q.length) D.text(g, '(empty)', x, y + 24, { s: 12, c: c.ink2 });
    q.forEach((e, i) => box(z, x, y + 10 + i * 32, 270, 26, e, { s: 12, stroke: c.orange, fill: c.dark ? '#3a2a10' : '#fff7ed' }));
    head(z, 'mainloop is', x, y + 120);
    box(z, x, y + 130, 270, 30, f.loop, { s: 13, b: true, mono: true, stroke: /stuck/.test(f.loop) ? c.red : c.cv, c: /stuck/.test(f.loop) ? c.red : undefined });
    if (f.timer) box(z, x, y + 168, 270, 26, 'timer: ' + f.timer, { s: 12, mono: true, stroke: c.green });
  }
  trace('pytk', {
    title: 'How a tkinter window works',
    sub: 'Pick a case. Each step shows the window, the waiting events and what mainloop is doing.',
    W: 600, H: 400,
    params: [{ k: 'case', label: 'Case', type: 'select', v: 'loop', opts: [['loop', 'mainloop and a button click'], ['freeze', 'A slow callback freezes the window'], ['grid', 'Placing widgets with grid']] }],
    tips: [
      { t: 'mainloop: your function runs only when an event arrives.', set: { case: 'loop' }, play: true },
      { t: 'Freeze: time.sleep blocks the loop, after() does not.', set: { case: 'freeze' }, play: true },
      { t: 'grid: sticky and weight decide where widgets sit and what grows.', set: { case: 'grid' }, play: true }
    ],
    frames(p) { return CASES[p.case].map(f => ({ ...f, mode: p.case })); },
    paint(z, f) {
      const c = z.col, g = z.g;
      if (f.mode === 'grid') {
        const wide = f.grow ? 150 : 0, x0 = 16, y0 = 40, cw = [90, 170 + wide], rh = 42;
        windowBox(z, x0 - 6, y0 - 30, cw[0] + cw[1] + 12 + 160 * 0, rh * 3 + 40, { win: 2 }, 'Sign up');
        for (let r = 0; r < 3; r++) for (let k = 0; k < 2; k++) {
          const x = x0 + (k ? cw[0] : 0);
          rr(g, x, y0 + r * rh, cw[k], rh, 2, { fill: 'transparent', stroke: c.line, w: 1, dash: [3, 3] });
          D.text(g, `row ${r}, col ${k}`, x + 4, y0 + r * rh + 10, { s: 8.5, c: c.ink2 });
        }
        const P = f.put;
        if (P >= 1) D.text(g, 'Name:', x0 + cw[0] - 8, y0 + 28, { a: 'right', s: 13, c: c.ink, b: f.cur === 0 });
        if (P >= 2) box(z, x0 + cw[0] + 4, y0 + 13, cw[1] - 8, 24, '', { stroke: f.cur === 1 || f.grow ? c.cv : c.line, w: f.cur === 1 || f.grow ? 2.5 : 1.5, r: 4 });
        if (P >= 3) D.text(g, 'Age:', x0 + cw[0] - 8, y0 + rh + 28, { a: 'right', s: 13, c: c.ink, b: f.cur === 2 });
        if (P >= 4) box(z, x0 + cw[0] + 4, y0 + rh + 13, 60, 24, '', { stroke: f.cur === 3 ? c.cv : c.line, w: f.cur === 3 ? 2.5 : 1.5, r: 4 });
        if (P >= 5) box(z, x0 + (cw[0] + cw[1]) / 2 - 40, y0 + 2 * rh + 9, 80, 26, 'Submit', { s: 12, stroke: f.cur === 4 ? c.cv : c.line, w: f.cur === 4 ? 2.5 : 1.5, r: 5 });
        if (f.grow) {
          D.arrow(g, x0 + cw[0] + 20, y0 + 3 * rh + 22, x0 + cw[0] + cw[1] - 10, y0 + 3 * rh + 22, c.green, 2, 7);
          D.text(g, 'column 1 gets the extra width', x0 + cw[0] + 24, y0 + 3 * rh + 40, { s: 11.5, b: true, c: c.green });
        }
        codeView(z, GRID_CODE, f.cur, 16, 232, 568, { lh: 22, s: 12 });
        return;
      }
      const loop = f.mode === 'loop';
      windowBox(z, 16, 30, 270, 180, f, loop ? 'My first window' : 'Frozen or not');
      if (f.win >= 1) {
        if (f.label) D.text(g, f.label, 151, 92, { a: 'center', s: 15, b: !!f.hl, c: f.hl ? c.cv : (f.win === 3 ? c.ink2 : c.ink) });
        if (loop && f.btn) box(z, 101, 120, 100, 30, 'Say hello', { s: 13, stroke: f.btn === 2 ? c.orange : c.line, w: f.btn === 2 ? 3 : 1.5, fill: f.btn === 2 ? (c.dark ? '#3a2a10' : '#fff7ed') : c.surf, r: 6 });
        if (!loop) {
          box(z, 46, 120, 100, 30, 'bad way', { s: 12, r: 6, stroke: f.cur <= 2 ? c.red : c.line });
          box(z, 156, 120, 100, 30, 'good way', { s: 12, r: 6, stroke: f.cur >= 3 ? c.green : c.line });
          if (f.live) D.text(g, 'window moves and redraws fine', 151, 182, { a: 'center', s: 11, c: c.green, b: true });
        }
        if (f.win === 3) rr(g, 18, 56, 266, 152, 6, { fill: c.dark ? 'rgba(0,0,0,0.45)' : 'rgba(255,255,255,0.55)', stroke: 'transparent' });
      }
      if (f.loop) queue(z, f, 314, 30);
      codeView(z, loop ? LOOP_CODE : FREEZE_CODE, f.cur, 16, 240, 568, { lh: 22, s: 12, bad: !loop && f.cur === 1 ? 1 : undefined });
    }
  });
})();
