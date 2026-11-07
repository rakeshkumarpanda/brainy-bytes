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
