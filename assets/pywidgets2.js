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
