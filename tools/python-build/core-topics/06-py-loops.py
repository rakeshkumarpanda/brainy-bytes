# Core Python 2.2: loops. Follows PCEP-30-02 section 2.2 (pass, while, for, range(), in, while-else, for-else,
# nesting loops, break and continue) and adds loop patterns, enumerate and zip, and loop counting maths, checked
# against the Python 3.14 tutorial sections 4.2 to 4.6 and the range() documentation.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, lc, leet, files, grow, leet_items

chapter('py-loops')
K = Kit()

K.code('while', r'''
count = 1
while count <= 5:
    print("Turn", count)
    count += 1          # without this line the loop never ends
print("Done, count is now", count)
''')

K.code('for', r'''
for fruit in ["apple", "mango", "banana"]:
    print("I like", fruit)

for letter in "Hi!":
    print(letter)

for i in range(3):          # 0, 1, 2
    print("range gives", i)
''')

K.code('range', r'''
print(list(range(5)))           # [0, 1, 2, 3, 4]
print(list(range(2, 8)))        # start 2, stop 8 (not included)
print(list(range(1, 10, 3)))    # step 3
print(list(range(10, 0, -2)))   # counting down
print(list(range(5, 1)))        # empty: you cannot go up from 5 to 1
print(len(range(0, 100, 7)), range(0, 100, 7)[-1])
''')

K.code('breakcont', r'''
# break: stop the whole loop. continue: skip to the next turn.
for n in range(1, 11):
    if n % 2 == 0:
        continue          # skip even numbers
    if n > 7:
        break             # stop completely
    print(n, end=" ")
print()

# else on a loop runs only when there was no break
for n in [3, 7, 11]:
    if n % 2 == 0:
        print("found an even number")
        break
else:
    print("no even number in the list")
''')

K.code('patterns', r'''
marks = [72, 45, 91, 38, 66]

total = 0                       # accumulator
for m in marks:
    total += m
print("total", total)

passed = 0                      # counter
for m in marks:
    if m >= 40:
        passed += 1
print("passed", passed)

best = marks[0]                 # running maximum
for m in marks:
    if m > best:
        best = m
print("best", best)

first_fail = None               # search with break
for m in marks:
    if m < 40:
        first_fail = m
        break
print("first fail", first_fail)
''')

K.code('nested', r'''
# A small multiplication table: a loop inside a loop
for row in range(1, 4):
    for col in range(1, 6):
        print(f"{row * col:3}", end="")
    print()          # new line after each row

# A triangle of stars
for i in range(1, 5):
    print("*" * i)
''')

K.code('enumzip', r'''
names = ["Asha", "Ravi", "Meera"]
scores = [88, 72, 95]

for i, name in enumerate(names, start=1):     # position and value together
    print(i, name)

for name, score in zip(names, scores):        # walk two lists side by side
    print(name, "scored", score)

for name in reversed(names):
    print(name, end=" ")
print()
for name in sorted(names):
    print(name, end=" ")
print()
''')

K.code('digits', r'''
# Taking a number apart digit by digit with % and //
n = 90731
digits = []
while n > 0:
    digits.append(n % 10)   # the last digit
    n = n // 10             # drop the last digit
print(digits)               # in reverse order
print("sum of digits:", sum(digits))

# Collatz: halve if even, else 3n + 1, until 1. Nobody has proved it always ends!
n, steps = 27, 0
while n != 1:
    n = n // 2 if n % 2 == 0 else 3 * n + 1
    steps += 1
print("27 reaches 1 after", steps, "steps")
''')

K.lesson('idea', 'Why we need loops', f'''
{src('Python 3.14 tutorial sections 4.2 to 4.6 and PCEP-30-02 section 2.2.')}
{wwh('A <b>loop</b> runs the same block of code again and again. Python has two loops: <b>while</b> repeats as long as a condition is True, and <b>for</b> repeats once for each item of a sequence.',
     'Computers are good at boring, repeated work: printing 1,000 pay slips, checking every row of a file, trying every password on a list. Writing the same line 1,000 times is impossible to maintain. A loop writes it once.',
     'Each repetition is called an <b>iteration</b> or a turn. Before every turn, Python checks if it should go on: is the condition still True (while), or is there another item (for)?')}
{scene('washing a pile of plates', '<p>"While there are dirty plates, take one and wash it" is a while loop: you do not know how many plates there are, you just check before each one. "For each of the 12 plates on the table, wash it" is a for loop: you walk through a known collection. If you forget to take a plate off the pile, the while loop never ends. In code that is an infinite loop.</p>')}
{run('while')}
{run('for')}
''', kw=['loop', 'iteration', 'while', 'for', 'repeat', 'infinite loop'])

K.lesson('range', 'for loops and range()', f'''
{viz('pyloop')}
{fxs(fx('range(start, stop, step)', 'start, start + step, start + 2&middot;step, ... while still before stop', 'stop is never included. start defaults to 0, step to 1. step must not be 0.', key=True),
     fx('How many numbers range gives', 'len = max(0, &lceil;(stop &minus; start) / step&rceil;)', 'range(1, 10, 3) has &lceil;9/3&rceil; = 3 numbers: 1, 4, 7.', key=True))}
{run('range')}
{note('range(5) is 0, 1, 2, 3, 4: five numbers, but 5 itself is not included. This "stop is excluded" rule matches list indexes, so range(len(items)) gives every valid index.', 'exam')}
{deep('range is lazy', '<p>range(10**12) does not build a trillion numbers. It is a small object that knows start, stop and step and works out each number when asked. len(), indexing and the in test are all O(1) maths, for example 999 in range(0, 10**12, 3) is answered instantly.</p>')}
''', kw=['for', 'range', 'start stop step', 'stop excluded', 'counting down', 'lazy range'])

K.lesson('control', 'break, continue, pass and else', f'''
{run('breakcont')}
{table(['Statement', 'What it does', 'Typical use'], [
    ['break', 'Leaves the innermost loop at once', 'Stop searching once you found what you wanted'],
    ['continue', 'Skips the rest of this turn and starts the next', 'Ignore bad rows and carry on'],
    ['pass', 'Does nothing. A placeholder where a statement is needed', 'An empty block you will write later'],
    ['else (on a loop)', 'Runs once after the loop if it was not stopped by break', 'Say "not found" after a search']])}
{note('The loop else is not "else if the loop did not run". It means "no break happened". A for loop over an empty list runs its else block.', 'exam')}
''', kw=['break', 'continue', 'pass', 'loop else', 'for else', 'while else', 'search'])

K.lesson('patterns', 'Loop patterns every programmer uses', f'''
{run('patterns')}
{table(['Pattern', 'Start with', 'Each turn', 'Built in shortcut'], [
    ['Accumulator (sum)', 'total = 0', 'total += x', 'sum(items)'],
    ['Counter', 'count = 0', 'if test: count += 1', 'sum(1 for x in items if test)'],
    ['Running maximum', 'best = first item', 'if x &gt; best: best = x', 'max(items)'],
    ['Search', 'found = None', 'if test: found = x and break', 'next((x for x in items if test), None)'],
    ['Build a new list', 'result = []', 'result.append(f(x))', '[f(x) for x in items] (Core 4.3)'],
    ['Sentinel', 'read a value', 'while value != "stop": ... read again', '']])}
{note('Learn the loops first, then the shortcuts. In an interview you may be asked to write max() yourself, and the running maximum pattern is the answer.', 'tip')}
''', kw=['accumulator', 'counter', 'running maximum', 'search', 'sentinel', 'sum', 'max', 'loop patterns'])

K.lesson('nested', 'Loops inside loops', f'''
{run('nested')}
{fxs(fx('Turns of a nested loop', 'outer &times; inner', '3 rows &times; 5 columns = 15 prints. Three nested loops of n each run n<sup>3</sup> times.', key=True),
     fx('Triangle loop', '1 + 2 + ... + n = n(n + 1)/2', 'When the inner loop runs i times on turn i, the total is a triangular number.', key=True))}
{note('break only leaves the inner loop. To leave two loops at once, put them in a function and use return, or set a flag and check it in the outer loop.', 'warn')}
''', kw=['nested loops', 'multiplication table', 'pattern printing', 'triangular number', 'break inner loop'])

K.lesson('pythonic', 'enumerate, zip, reversed and sorted', f'''
{run('enumzip')}
{versus('Looping over a list with positions', ['', 'Index loop', 'enumerate'], [
    ['Code', 'for i in range(len(names)): print(i, names[i])', 'for i, name in enumerate(names): print(i, name)'],
    ['Reads', 'Two steps: index, then look up', 'Says what you mean'],
    ['Mistakes', 'Off by one, wrong list in names[i]', 'Fewer'],
    ['When you still need indexes', 'Changing items in place, comparing names[i] with names[i + 1]', '']],
    'loop over the items directly, add enumerate when you need the position and zip when you walk two lists together.')}
{note('zip stops at the shortest list. zip([1, 2, 3], "ab") gives only two pairs. Python 3.10 added zip(..., strict=True) to raise an error when the lengths differ.', 'warn')}
''', kw=['enumerate', 'zip', 'reversed', 'sorted', 'pythonic loops', 'strict zip'])

K.lesson('whileuse', 'When to use while', f'''
{run('digits')}
{versus('for or while', ['', 'for', 'while'], [
    ['Number of turns', 'Known: one per item', 'Unknown: until a condition changes'],
    ['Stops by itself', 'Yes, when items run out', 'Only if your code makes the condition False'],
    ['Examples', 'Each student, each line of a file, range(10)', 'Digits of a number, asking until the input is valid, a game loop, Collatz']],
    'use for whenever you walk over a collection or a range. Use while when you wait for something to happen.')}
{note('An infinite loop is not always a bug: servers and games run while True: with a break or return inside. In the REPL or a terminal, press Ctrl+C to stop a runaway loop.', 'tip')}
''', kw=['while', 'unknown number of turns', 'digits', 'Collatz', 'while True', 'Ctrl+C'])

K.lesson('maths', 'The maths of loops', f'''
{fxs(fx('Length of a range', 'len(range(a, b, s)) = max(0, &lceil;(b &minus; a)/s&rceil;)', 'Works for negative steps too: range(10, 0, -3) has &lceil;-10/-3&rceil; = 4 numbers.', key=True),
     fx('Last number of a range', 'a + (len &minus; 1) &middot; s', 'range(0, 100, 7)[-1] = 0 + 14 &times; 7 = 98.'),
     fx('Sum of an arithmetic sequence', 'S = n(first + last)/2', 'sum(range(1, 101)) = 100 &times; 101 / 2 = 5050 (the young Gauss story).', key=True),
     fx('Turns to halve n down to 1', '&lfloor;log<sub>2</sub> n&rfloor;', 'while n &gt; 1: n //= 2 runs about log<sub>2</sub> n times. This is why binary search is fast.'),
     fx('Digits of n (turns of the digit loop)', '&lfloor;log<sub>10</sub> n&rfloor; + 1', 'The digit loop above ran 5 times for 90731.'))}
{steps('Worked example: how many times does the inner print run?', [
    'for i in range(1, 5): for j in range(i): print(j)',
    'On turn i, the inner loop runs i times: 1, 2, 3, 4.',
    'Total = 1 + 2 + 3 + 4.',
    eq('4 &times; 5 / 2 = 10')])}
''', kw=['range length', 'arithmetic sequence', 'Gauss sum', 'logarithm', 'loop counting'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>A loop repeats a job. for does it once per item, while keeps going until a condition says stop.</p>',
    '<p>range(start, stop, step) excludes stop. break leaves, continue skips, else runs when no break happened. Use accumulator, counter, maximum and search patterns, and enumerate and zip instead of index loops.</p>',
    '<p>for works with any iterable: it calls iter() once and next() each turn until StopIteration (Advanced 2.1). Changing a list while looping over it skips items, so loop over a copy (items[:]) or build a new list.</p>',
    '<p>Loop analysis is the start of algorithm analysis: counting turns gives the running time, O(n) for one loop, O(n<sup>2</sup>) for two nested loops. Loop invariants (a statement true before and after every turn) are how computer scientists prove that a loop is correct, as in Hoare logic.</p>')}
{grow('Write while and for loops, use range() correctly, and stop with break.',
      'Use the standard patterns, nested loops, enumerate and zip, and count how many times a loop runs.',
      'Explain the iterator protocol behind for, avoid changing a list while looping, and prove a loop correct with an invariant.')}
{scene('an ATM PIN check', '<p>An ATM gives you three tries for your PIN. That is a loop of at most 3 turns: if the PIN is right, break and show the menu. If all three turns end without a break, the else block keeps the card. The for loop with else says this exactly: for attempt in range(3): ... break, else: keep the card.</p>')}
''', kw=['beginner', 'expert', 'iterator protocol', 'loop invariant', 'big O'])

lc(1480, 'Running Sum of 1d Array', 'running-sum-of-1d-array', 'e', 'Accumulator', 'Keep a total. Each turn add the current number and append the total.', r'''
def running_sum(nums):
    result = []
    total = 0
    for x in nums:
        total = total + x
        result.append(total)
    return result
''', [('running_sum([1, 2, 3, 4])', [1, 3, 6, 10]), ('running_sum([3, 1, 2, 10, 1])', [3, 4, 6, 16, 17])])
lc(9, 'Palindrome Number', 'palindrome-number', 'e', 'Digit loop with % and //', 'Negative numbers are not palindromes. Build the reversed number digit by digit and compare.', r'''
def is_palindrome(x):
    if x < 0:
        return False
    original = x
    reversed_number = 0
    while x > 0:
        reversed_number = reversed_number * 10 + x % 10
        x = x // 10
    return reversed_number == original
''', [('is_palindrome(121)', True), ('is_palindrome(-121)', False), ('is_palindrome(10)', False)])
lc(1295, 'Find Numbers with Even Number of Digits', 'find-numbers-with-even-number-of-digits', 'e', 'Counter', 'Count the digits of each number with len(str(n)) and count the even ones.', r'''
def find_numbers(nums):
    count = 0
    for n in nums:
        if len(str(n)) % 2 == 0:
            count = count + 1
    return count
''', [('find_numbers([12, 345, 2, 6, 7896])', 2), ('find_numbers([555, 901, 482, 1771])', 1)])
lc(7, 'Reverse Integer', 'reverse-integer', 'm', 'Digit loop and range check', 'Reverse the absolute value with a digit loop, put the sign back, and return 0 if it leaves the 32 bit range.', r'''
def reverse(x):
    sign = 1
    if x < 0:
        sign = -1
        x = -x
    result = 0
    while x > 0:
        result = result * 10 + x % 10
        x = x // 10
    result = result * sign
    if result < -(2 ** 31) or result > 2 ** 31 - 1:
        return 0
    return result
''', [('reverse(123)', 321), ('reverse(-123)', -321), ('reverse(120)', 21), ('reverse(1534236469)', 0)])
lc(202, 'Happy Number', 'happy-number', 'e', 'while loop with a seen set', 'Replace n by the sum of the squares of its digits. Stop at 1 (happy) or when a number repeats (a cycle).', r'''
def is_happy(n):
    seen = set()
    while n != 1:
        if n in seen:
            return False
        seen.add(n)
        total = 0
        while n > 0:
            digit = n % 10
            total = total + digit * digit
            n = n // 10
        n = total
    return True
''', [('is_happy(19)', True), ('is_happy(2)', False)])
lc(1137, 'N-th Tribonacci Number', 'n-th-tribonacci-number', 'e', 'Loop with three running values', 'Keep the last three numbers a, b, c and move them forward n times.', r'''
def tribonacci(n):
    a, b, c = 0, 1, 1
    if n == 0:
        return 0
    for _ in range(n - 2):
        a, b, c = b, c, a + b + c
    return c
''', [('tribonacci(4)', 4), ('tribonacci(25)', 1389537), ('tribonacci(1)', 1)])

K.lesson('leetcode', 'LeetCode practice', leet(), kw=['LeetCode', 'running sum', 'palindrome number', 'reverse integer', 'happy number'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    '<b>while</b> repeats while a condition is True. Something in the body must change the condition, or the loop never ends.',
    '<b>for</b> repeats once per item of a list, text, range or any other iterable.',
    '<b>range(start, stop, step)</b> excludes stop. Its length is max(0, &lceil;(stop &minus; start)/step&rceil;).',
    '<b>break</b> leaves the loop, <b>continue</b> skips to the next turn, <b>pass</b> does nothing, and a loop <b>else</b> runs when no break happened.',
    'Patterns: accumulator, counter, running maximum, search with break, building a list, sentinel loop.',
    'Nested loops run outer &times; inner times. A triangle loop runs n(n + 1)/2 times.',
    'Use enumerate for positions, zip for walking lists together, reversed and sorted for order.'],
    'Core 3.1 opens up strings: indexing, slicing, methods and how text is stored as Unicode.')}
{files('Three tasks: FizzBuzz as text, prime check with a loop else, and a digit sum loop.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'What does list(range(4)) give?', ['[1, 2, 3, 4]', '[0, 1, 2, 3]', '[0, 1, 2, 3, 4]', '[4]'], 1, 'Starts at 0, stop excluded.', 'range(4) is 0, 1, 2, 3.')
K.quiz('e', 'Which statement leaves a loop at once?', ['continue', 'pass', 'break', 'return only'], 2, 'Leave.', 'break leaves the innermost loop.')
K.quiz('e', 'How many times does for c in "cat": print(c) print?', ['1', '3', '0', 'For ever'], 1, 'One per character.', '"cat" has 3 characters.')
K.quiz('m', 'What does list(range(10, 0, -3)) give?', ['[10, 7, 4, 1]', '[10, 7, 4, 1, -2]', '[]', '[10, 7, 4]'], 0, 'Count down, stop before 0.', '10, 7, 4, 1, and -2 is past the stop.')
K.quiz('m', 'When does the else block of a for loop run?', ['When the loop never runs', 'When the loop ends without break', 'After every turn', 'When break runs'], 1, 'No break.', 'else runs if the loop finished normally.')
K.quiz('m', 'What is printed? for i in range(5): if i == 2: continue then print(i, end="")', ['01234', '0134', '01', '234'], 1, 'Skip 2.', 'continue skips the print for 2.')
K.quiz('m', 'What is len(range(1, 20, 4))?', ['4', '5', '6', '20'], 1, '&lceil;19/4&rceil;.', '1, 5, 9, 13, 17: 5 numbers.')
K.quiz('h', 'What does for x in []: pass then else: print("E") print?', ['Nothing', 'E', 'An error', 'None'], 1, 'No break happened.', 'The loop ran zero times without break, so else runs.')
K.quiz('h', 'A loop with for i in range(n): for j in range(n): runs the inner body how many times?', ['n', '2n', 'n<sup>2</sup>', 'n(n + 1)/2'], 2, 'outer &times; inner.', 'n &times; n = n<sup>2</sup>.')
K.quiz('h', 'What happens with i = 0 then while i &lt; 3: print(i) and no other line?', ['Prints 0 1 2', 'Prints 0 for ever', 'Prints nothing', 'SyntaxError'], 1, 'Does i change?', 'i stays 0, so the condition is always True: an infinite loop.')
K.quiz('x', 'In the style of a Carnegie Mellon 15-112 exam: what is printed? s = 0, then for i in range(1, 6): for j in range(i, 6): s += 1, then print(s)', ['15', '25', '10', '21'], 0, 'Turn i runs 6 &minus; i times.', '5 + 4 + 3 + 2 + 1 = 15.')
K.quiz('x', 'In the style of an IIT JEE style programming aptitude question: n = 1000, k = 0, while n &gt; 1: n //= 2, k += 1. What is k?', ['9', '10', '500', '11'], 0, '&lfloor;log<sub>2</sub> 1000&rfloor;.', '1000, 500, 250, 125, 62, 31, 15, 7, 3, 1: nine halvings.')

K.calc('e', 'len(range(0, 10))?', '10', '0 to 9.', ['start 0, stop 10.', 'Step 1.', eq('10 numbers')], check=len(range(0, 10)))
K.calc('e', 'sum(range(1, 11))?', '55', 'n(first + last)/2.', ['n = 10, first 1, last 10.', '10 &times; 11 / 2.', eq('55')], check=sum(range(1, 11)))
K.calc('e', 'Last number of range(0, 100, 7)?', '98', '14 &times; 7.', ['len = &lceil;100/7&rceil; = 15.', 'Last = 0 + 14 &times; 7.', eq('98')], check=range(0, 100, 7)[-1])
K.calc('m', 'len(range(10, 0, -3))?', '4', '&lceil;-10/-3&rceil;.', ['(0 &minus; 10)/(-3) = 3.33.', 'Round up.', eq('4')], check=len(range(10, 0, -3)))
K.calc('m', 'sum(range(1, 101))?', '5050', 'Gauss.', ['n = 100.', '100 &times; 101 / 2.', eq('5050')], check=sum(range(1, 101)))
K.calc('m', 'Turns of the inner body: for i in range(1, 6): for j in range(i):', '15', 'Triangle.', ['Turn i runs i times.', '1 + 2 + 3 + 4 + 5.', eq('15')], check=sum(range(1, 6)))
K.calc('m', 'Sum of the even numbers from 2 to 100.', '2550', '50 terms.', ['2, 4, ..., 100 is 50 numbers.', '50 &times; (2 + 100) / 2.', eq('2550')], check=sum(range(2, 101, 2)))
K.calc('h', 'How many halvings take n = 1,000,000 down to 1 with n //= 2?', '19', '&lfloor;log<sub>2</sub> n&rfloor;.', ['2<sup>19</sup> = 524,288 &le; 10<sup>6</sup> &lt; 2<sup>20</sup>.', 'So &lfloor;log<sub>2</sub> 10<sup>6</sup>&rfloor; = 19.', eq('19')], check=(10 ** 6).bit_length() - 1)
K.calc('h', 'Steps for Collatz starting at 6 to reach 1.', '8', '6, 3, 10, 5, 16, 8, 4, 2, 1.', ['Even: halve. Odd: 3n + 1.', 'List: 6, 3, 10, 5, 16, 8, 4, 2, 1.', eq('8 steps')], check=8)
K.calc('x', 'In the style of an Oxford Computer Science interview problem: three nested loops for i in range(n): for j in range(i): for k in range(j): count += 1. Find count for n = 10.', '120', 'Choose 3 from 10.', ['Each turn picks k &lt; j &lt; i.', 'That is the number of ways to choose 3 different numbers from 0 to 9.', eq('C(10, 3) = 10 &times; 9 &times; 8 / 6 = 120')], check=sum(1 for i in range(10) for j in range(i) for k in range(j)))

K.assign('fizz', 'e', 'FizzBuzz as one line of text',
         '<p>Write <code>fizzbuzz_line(n)</code> that returns the FizzBuzz words for 1 to n joined by spaces: multiples of 15 give FizzBuzz, of 3 Fizz, of 5 Buzz, and other numbers themselves.</p>',
         '''
def fizzbuzz_line(n):
    # your code here
    pass
''', [('fizzbuzz_line(5)', '1 2 Fizz 4 Buzz'), ('fizzbuzz_line(15).split()[-1]', 'FizzBuzz'), ('fizzbuzz_line(1)', '1')],
         '''
def fizzbuzz_line(n):
    words = []
    for i in range(1, n + 1):
        if i % 15 == 0:
            words.append("FizzBuzz")
        elif i % 3 == 0:
            words.append("Fizz")
        elif i % 5 == 0:
            words.append("Buzz")
        else:
            words.append(str(i))
    return " ".join(words)
''', 'Loop from 1 to n with range(1, n + 1). Check 15 first.', '<p>FizzBuzz is a famous first interview question because it tests loops, % and the order of conditions.</p>')
K.assign('prime', 'm', 'Prime check with a loop else',
         '<p>Write <code>is_prime(n)</code>. n is prime if n &ge; 2 and no number d from 2 up to the square root of n divides it. Use a for loop with break and else.</p>',
         '''
def is_prime(n):
    # your code here
    pass
''', [('is_prime(2)', True), ('is_prime(1)', False), ('is_prime(97)', True), ('is_prime(91)', False), ('is_prime(49)', False)],
         '''
def is_prime(n):
    if n < 2:
        return False
    d = 2
    for d in range(2, int(n ** 0.5) + 1):
        if n % d == 0:
            break
    else:
        return True
    return False
''', 'Loop d over range(2, int(n ** 0.5) + 1). If n % d == 0, break. The else returns True.', '<p>Checking up to &radic;n is enough: if n = a &times; b and both were above &radic;n, then a &times; b would be above n. 91 = 7 &times; 13 fools many people.</p>')
K.assign('digitsum', 'm', 'Digital root',
         '<p>Write <code>digital_root(n)</code> for n &ge; 0: add the digits of n, then the digits of the result, until one digit is left. Use while loops, not str().</p>',
         '''
def digital_root(n):
    # your code here
    pass
''', [('digital_root(38)', 2), ('digital_root(0)', 0), ('digital_root(99999)', 9), ('digital_root(12345)', 6)],
         '''
def digital_root(n):
    while n >= 10:
        total = 0
        while n > 0:
            total = total + n % 10
            n = n // 10
        n = total
    return n
''', 'An outer while for "more than one digit" and an inner while that adds the digits with % 10 and // 10.', '<p>The maths shortcut 1 + (n &minus; 1) % 9 gives the same answer for n &gt; 0 (LeetCode 258).</p>')

K.must('while and for', 'while repeats while a condition is True. for repeats once per item of an iterable.')
K.must('range', 'range(start, stop, step) excludes stop. len = max(0, ceil((stop - start)/step)). step 0 is an error.')
K.must('Loop control', 'break leaves, continue skips, pass does nothing, loop else runs when no break happened.')
K.must('Patterns', 'Accumulator, counter, running max, search with break, build a list. Nested loops: outer x inner turns.')
K.must('Pythonic loops', 'enumerate(items, start=1), zip(a, b) stops at the shortest, reversed(), sorted().')

T = K.topic(
    slug='py-loops', topic='py-loops', step=(2, 'Control flow', 'py-c2', 'Choose with if, elif, else and match, and repeat with while and for loops.', 'Beginner'),
    title='Loops: while, for, range, break and continue', short='Loops', badge='2.2', minutes=50,
    lead='Make the computer do repeated work. Learn while and for loops, every detail of range(), break, continue, pass and the loop else, the patterns every programmer uses, nested loops, enumerate and zip, and how to count exactly how many times a loop runs.',
    desc='while loops, infinite loops, for loops over lists, text and range, range start stop step and its length formula, break, continue, pass, for else and while else, accumulator, counter, maximum and search patterns, nested loops, enumerate, zip, reversed, sorted, digit loops and loop counting maths.',
    summary='while, for, range, break, continue, pass, loop else, loop patterns, nested loops, enumerate and zip, loop maths.',
    keywords=['loops', 'while', 'for', 'range', 'break', 'continue', 'pass', 'for else', 'nested loops', 'enumerate', 'zip', 'iteration', 'PCEP'],
    recap='<p>for walks through items, while waits for a condition. break, continue and else control the loop, and counting turns tells you how fast it is.</p>',
    added='2026-11-07', leet=leet_items())
