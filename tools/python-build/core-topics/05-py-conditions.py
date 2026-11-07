# Core Python 2.1: making decisions. Follows PCEP-30-02 section 2.1 (if, if-else, if-elif, if-elif-else,
# multiple and nested conditional statements) and adds truthiness, the conditional expression, the walrus
# operator and structural pattern matching (match and case, PEP 634 to 636, Python 3.10+), checked against the
# Python 3.14 tutorial section 4.1 and 4.7 and the Language Reference section 8.6.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, lc, leet, files, grow, leet_items

chapter('py-conditions')
K = Kit()

K.code('basic', r'''
temperature = 31
if temperature > 30:
    print("It is hot. Drink water.")
print("Have a nice day.")          # always runs

marks = 38
if marks >= 40:
    print("Pass")
else:
    print("Fail, try again")
''')

K.code('grade', r'''
def grade(score):
    if score >= 90:
        return "A"
    elif score >= 75:
        return "B"
    elif score >= 50:
        return "C"
    else:
        return "F"

for s in [95, 90, 82, 50, 49, 0]:
    print(s, grade(s))
''')

K.code('truthy', r'''
values = [0, 1, -2, 0.0, "", "0", " ", [], [0], {}, None, True, False]
for v in values:
    if v:
        print(repr(v).ljust(6), "is truthy")
    else:
        print(repr(v).ljust(6), "is falsy")
''')

K.code('combine', r'''
age, member, day = 67, False, "Tue"
if age >= 60 or member:
    print("Discount")
if 13 <= age <= 19:
    print("Teenager")
if day in ("Sat", "Sun"):
    print("Weekend")
elif day == "Tue" and not member:
    print("Tuesday offer for new customers")
''')

K.code('ternary', r'''
n = 7
kind = "even" if n % 2 == 0 else "odd"     # conditional expression
print(n, "is", kind)
fee = 0 if n < 5 else 50 if n < 10 else 100
print("fee:", fee)
print(abs(-4), max(3, 9), min(3, 9))        # built ins that hide an if
''')

K.code('walrus', r'''
data = [3, 8, 12, 5]
if (n := len(data)) > 3:                    # assign and test in one go
    print("Too many items:", n)

words = ["apple", "fig", "banana", "kiwi"]
long_words = [w.upper() for w in words if (size := len(w)) > 4]
print(long_words, "last size checked:", size)
''')

K.code('match', r'''
def describe(command):
    match command.split():
        case ["quit"] | ["exit"]:
            return "Goodbye!"
        case ["go", direction] if direction in ("up", "down"):
            return "You climb " + direction
        case ["go", direction]:
            return "You walk " + direction
        case ["drop", *things]:
            return "You drop " + str(len(things)) + " thing(s)"
        case _:
            return "I do not understand"

for c in ["go north", "go up", "drop sword lamp", "quit", "dance"]:
    print(c.ljust(16), "->", describe(c))
''')

K.code('matchmore', r'''
def http_message(status):
    match status:
        case 200 | 201:
            return "OK"
        case 404:
            return "Not found"
        case int(code) if 500 <= code < 600:
            return "Server error " + str(code)
        case _:
            return "Something else"

def where(point):
    match point:
        case (0, 0):
            return "origin"
        case (0, y):
            return f"on the y axis at {y}"
        case (x, 0):
            return f"on the x axis at {x}"
        case {"x": x, "y": y}:
            return f"a dict point ({x}, {y})"
        case _:
            return "somewhere else"

print(http_message(201), "|", http_message(503), "|", http_message(302))
print(where((0, 0)), "|", where((0, 5)), "|", where((3, 0)), "|", where({"x": 1, "y": 2}))
''')

K.lesson('idea', 'Programs that choose', f'''
{src('Python 3.14 tutorial sections 4.1 and 4.7, Language Reference 8.1 and 8.6, PCEP-30-02 section 2.1.')}
{wwh('A <b>conditional statement</b> runs a block of code only when a condition is True. The condition is any expression, and Python asks "is it truthy?".',
     'Real decisions depend on data: pass or fail, discount or no discount, access allowed or denied. Without conditions a program does the same thing every time.',
     'Python works out the condition. If it is truthy, the indented block under it runs. If not, the block is skipped and Python moves to the next elif, the else, or the code after the statement.')}
{scene('a traffic signal', '<p>A driver checks the signal: if it is red, stop. Otherwise if it is yellow, slow down. Otherwise (green), go. The driver checks in that order and does exactly one thing. That is an if, elif, else chain. Checking "green" first and then also checking "red" separately would be dangerous, and in code it gives the wrong answer too.</p>')}
{run('basic')}
''', kw=['if', 'else', 'condition', 'block', 'decision', 'branch'])

K.lesson('chain', 'if, elif and else chains', f'''
{viz('pyif')}
{run('grade')}
{steps('Rules for a chain', [
    'A chain starts with one if, may have any number of elif, and may end with one else.',
    'Python checks the conditions from the top. The first truthy one wins and only its block runs.',
    'After a block runs, every remaining elif and else of the chain is skipped without being checked.',
    eq('Put the strictest condition first, for example score &gt;= 90 before score &gt;= 75')])}
{versus('elif chain, separate ifs, or nesting', ['', 'if / elif / else', 'separate if statements', 'nested if'], [
    ['How many blocks can run', 'Exactly one (or none without else)', 'Any number', 'Depends on the tree'],
    ['Use when', 'The cases exclude each other (a grade)', 'Several things can be true together (flags)', 'A second question only makes sense after the first'],
    ['Risk', 'Wrong order catches cases too early', 'Several outputs when you wanted one', 'Deep indentation that is hard to read']],
    'an elif chain is the usual choice. Use separate ifs for independent checks and keep nesting to two levels.')}
''', kw=['elif', 'else', 'chain', 'order of conditions', 'nested if', 'separate if'])

K.lesson('truthy', 'Truthy and falsy values', f'''
<p>A condition does not have to be True or False. Python accepts any value and decides if it counts as true.</p>
{table(['Falsy (counts as False)', 'Truthy (counts as True)'], [
    ['False, None', 'True'],
    ['0, 0.0, 0j', 'any other number, even -2 and 0.001'],
    ['"" (empty text)', '"0", " ", "False" (non empty text)'],
    ['[], (), {}, set(), range(0)', '[0], (None,), {"a": 1} (non empty collections)']])}
{run('truthy')}
{note('Write if items: instead of if len(items) &gt; 0:, and if not name: instead of if name == "":. PEP 8 recommends this short form. But write if x is None: when you really mean None, because 0 and "" are falsy too.', 'tip')}
''', kw=['truthy', 'falsy', 'bool()', 'empty collection', 'None check', 'is None'])

K.lesson('combine', 'Combining conditions', f'''
{run('combine')}
{table(['Need', 'Write', 'Instead of'], [
    ['Both must hold', 'a and b', 'a nested if inside if'],
    ['Either is enough', 'a or b', 'two ifs with the same block'],
    ['A range', '13 &lt;= age &lt;= 19', 'age &gt;= 13 and age &lt;= 19'],
    ['One of several values', 'day in ("Sat", "Sun")', 'day == "Sat" or day == "Sun"'],
    ['The opposite', 'not done', 'done == False']])}
{note('if day == "Sat" or "Sun": is always True. Python reads it as (day == "Sat") or "Sun", and "Sun" is truthy. Write day in ("Sat", "Sun").', 'warn')}
''', kw=['and', 'or', 'not', 'chained comparison', 'in tuple', 'common bug or'])

K.lesson('ternary', 'One line choices: the conditional expression and the walrus', f'''
{fxs(fx('Conditional expression', 'value_if_true if condition else value_if_false', 'An expression, so it gives a value: kind = "even" if n % 2 == 0 else "odd".', key=True),
     fx('Assignment expression (walrus)', '(name := expression)', 'Python 3.8+. Assigns and gives the value in one go, useful inside if and while conditions.'))}
{run('ternary')}
{run('walrus')}
{note('Do not chain many conditional expressions in one line. a if x else b if y else c is legal but hard to read. Use an if, elif, else statement instead.', 'tip')}
''', kw=['conditional expression', 'ternary operator', 'walrus operator', ':=', 'assignment expression', 'PEP 572'])

K.lesson('match', 'match and case: pattern matching', f'''
{wwh('match compares a value (the subject) with a list of <b>patterns</b>. The first pattern that fits runs its block. Patterns can check the shape of the data and pull values out of it at the same time.',
     'Long elif chains that look inside lists, tuples and dicts are hard to read. match describes the shape you expect directly, like a picture of the data.',
     'Python tries each case from the top. A literal must be equal, a name captures the value, [a, b] needs a sequence of length 2, *rest collects the remaining items, {"key": v} looks inside a dict, | means or, if adds a guard, and _ matches anything.')}
{viz('pymatch')}
{run('match')}
{run('matchmore')}
{table(['Pattern', 'Fits', 'Example'], [
    ['Literal', 'A value equal to it', 'case 404:'],
    ['Capture', 'Anything, and binds it to the name', 'case code:'],
    ['Wildcard', 'Anything, binds nothing', 'case _:'],
    ['Or', 'Any of the alternatives', 'case 200 | 201:'],
    ['Sequence', 'A list or tuple of that length', 'case ["go", direction]:'],
    ['Star', 'Collects the rest of a sequence', 'case ["drop", *things]:'],
    ['Mapping', 'A dict with those keys (others allowed)', 'case {"x": x, "y": y}:'],
    ['Class', 'An instance of the class, with attributes', 'case Point(x=0, y=y):'],
    ['Guard', 'The pattern plus a condition', 'case int(n) if n &gt; 0:']])}
{note('A plain name in a case is a capture, not a comparison. case RED: catches everything and binds it to RED. To compare with a constant, use a dotted name such as case Color.RED:.', 'warn')}
''', kw=['match', 'case', 'pattern matching', 'structural pattern matching', 'capture pattern', 'wildcard', 'guard', 'sequence pattern', 'mapping pattern', 'PEP 634'])

K.lesson('maths', 'The maths: boolean algebra', f'''
{fxs(fx('De Morgan laws', 'not (a and b) == (not a) or (not b),  not (a or b) == (not a) and (not b)', 'Use them to simplify or flip a condition.', key=True),
     fx('Number of paths', 'k independent if statements give up to 2<sup>k</sup> combinations', 'An elif chain with k conditions and an else has exactly k + 1 paths.', key=True),
     fx('Distributive law', 'a and (b or c) == (a and b) or (a and c)', 'Like a &times; (b + c) = ab + ac in school algebra.'))}
{steps('Worked example: flip "is a teenager"', [
    'Teenager: 13 &lt;= age and age &lt;= 19.',
    'Not a teenager: not (13 &lt;= age and age &lt;= 19).',
    'De Morgan: not (13 &lt;= age) or not (age &lt;= 19).',
    eq('age &lt; 13 or age &gt; 19')])}
{table(['a', 'b', 'not (a and b)', 'not a or not b'], [
    ['True', 'True', 'False', 'False'],
    ['True', 'False', 'True', 'True'],
    ['False', 'True', 'True', 'True'],
    ['False', 'False', 'True', 'True']])}
''', kw=['boolean algebra', 'De Morgan', 'truth table', 'number of paths', 'test cases'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>if is a fork in the road. Python checks a question and takes one path. elif adds more questions, else is the path when every answer was no.</p>',
    '<p>Conditions use truthiness. A chain runs exactly one block. Combine with and, or, not, chained comparisons and in. Use the conditional expression for simple one line choices and match for data shaped choices.</p>',
    '<p>match compiles to a sequence of type checks, length checks and lookups. Sequence patterns do not match str, bytes or bytearray, so case [a, b]: never fits "ab". Class patterns use __match_args__ for positional parts.</p>',
    '<p>Branches cost time on real chips when they are hard to predict (branch misprediction), which is why sorted data can make an if inside a loop faster in compiled languages. In testing, branch coverage (every if both ways) and MC/DC coverage (each condition shown to matter, required for avionics software) measure how well conditions are tested.</p>')}
{grow('Write if, elif, else chains in the right order and test every branch.',
      'Use truthiness, De Morgan, conditional expressions and match with captures and guards.',
      'Explain how match is compiled, why sequence patterns skip strings, and design tests for branch and MC/DC coverage.')}
{scene('an online shop checkout', '<p>At checkout, the shop decides delivery: if the order is above 499 rupees, delivery is free. Otherwise, if the customer is a member, it is 20 rupees. Otherwise it is 40. A coupon code is then matched: "WELCOME10", "FESTIVE", or anything else is "invalid code". The first part is an elif chain, the second is a natural match statement.</p>')}
''', kw=['beginner', 'expert', 'branch coverage', 'MC/DC', 'branch prediction'])

lc(1455, 'Check If a Word Occurs As a Prefix of Any Word in a Sentence', 'check-if-a-word-occurs-as-a-prefix-of-any-word-in-a-sentence', 'e', 'Condition inside a loop', 'Split the sentence. Return the 1 based position of the first word that starts with searchWord, else -1.', r'''
def is_prefix_of_word(sentence, search_word):
    words = sentence.split()
    for i in range(len(words)):
        if words[i].startswith(search_word):
            return i + 1
    return -1
''', [('is_prefix_of_word("i love eating burger", "burg")', 4), ('is_prefix_of_word("i am tired", "you")', -1)])
lc(2129, 'Capitalize the Title', 'capitalize-the-title', 'e', 'if else on length', 'Words of length 1 or 2 become all lower case. Longer words get a capital first letter and the rest lower.', r'''
def capitalize_title(title):
    result = []
    for word in title.split():
        if len(word) <= 2:
            result.append(word.lower())
        else:
            result.append(word[0].upper() + word[1:].lower())
    return " ".join(result)
''', [('capitalize_title("capiTalIze tHe titLe")', 'Capitalize The Title'), ('capitalize_title("i lOve leetcode")', 'i Love Leetcode')])
lc(1672, 'Richest Customer Wealth', 'richest-customer-wealth', 'e', 'Keep the biggest with if', 'Add up each row. Keep the biggest sum seen so far with an if.', r'''
def maximum_wealth(accounts):
    best = 0
    for customer in accounts:
        total = 0
        for money in customer:
            total = total + money
        if total > best:
            best = total
    return best
''', [('maximum_wealth([[1, 2, 3], [3, 2, 1]])', 6), ('maximum_wealth([[1, 5], [7, 3], [3, 5]])', 10)])
lc(2678, 'Number of Senior Citizens', 'number-of-senior-citizens', 'e', 'Condition on a slice', 'Characters 11 and 12 of each passenger text are the age. Count ages above 60.', r'''
def count_seniors(details):
    count = 0
    for d in details:
        age = int(d[11:13])
        if age > 60:
            count = count + 1
    return count
''', [('count_seniors(["7868190130M7522", "5303914400F9211", "9273338290F4010"])', 2), ('count_seniors(["1313579440F2036", "2921522980M5644"])', 0)])
lc(1344, 'Angle Between Hands of a Clock', 'angle-between-hands-of-a-clock', 'm', 'Formula and min', 'Minute hand at 6 &times; minutes degrees, hour hand at 30 &times; (hour % 12) + 0.5 &times; minutes. Return the smaller of the gap and 360 minus the gap.', r'''
def angle_clock(hour, minutes):
    minute_angle = 6 * minutes
    hour_angle = 30 * (hour % 12) + 0.5 * minutes
    gap = abs(hour_angle - minute_angle)
    if gap > 180:
        gap = 360 - gap
    return gap
''', [('angle_clock(12, 30)', 165.0), ('angle_clock(3, 30)', 75.0), ('angle_clock(3, 15)', 7.5)])

K.lesson('leetcode', 'LeetCode practice', leet(), kw=['LeetCode', 'capitalize the title', 'angle between hands of a clock'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    '<b>if</b> runs its block only when the condition is truthy. <b>else</b> runs when it is not. <b>elif</b> adds more checks in between.',
    'In a chain Python checks from the top, runs the first truthy branch only, and skips the rest. Put the strictest test first.',
    'Falsy values: False, None, 0, 0.0, "", and empty collections. Everything else is truthy, even "0" and [0].',
    'Combine with and, or, not, 13 &lt;= age &lt;= 19 and day in ("Sat", "Sun"). day == "Sat" or "Sun" is always True.',
    'One line choices: x if cond else y. The walrus (n := len(data)) assigns inside a condition.',
    '<b>match</b> tries patterns from the top: literals, captures, _, |, [a, *rest], {"k": v}, Class(...), and guards with if.',
    'De Morgan: not (a and b) == not a or not b. k independent ifs give up to 2<sup>k</sup> paths to test.'],
    'Core 2.2 repeats work with while and for loops, range(), break, continue and else.')}
{files('Three tasks: a ticket price chain, a leap year with match, and a triangle classifier.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'Which keyword adds another condition to an if chain?', ['else if', 'elif', 'elseif', 'or if'], 1, 'Short form.', 'Python uses elif.')
K.quiz('e', 'What does if 0: print("yes") print?', ['yes', 'Nothing', '0', 'An error'], 1, 'Is 0 truthy?', '0 is falsy, so the block is skipped.')
K.quiz('e', 'How many branches of an if, elif, elif, else chain can run at once?', ['0', 'Exactly 1', 'Up to 3', 'All of them'], 1, 'With else.', 'With an else, exactly one branch always runs.')
K.quiz('m', 'score = 95. With separate ifs for >= 90, >= 75 and >= 50, how many lines print?', ['1', '2', '3', '0'], 2, 'Each if is checked.', 'All three conditions are True.')
K.quiz('m', 'Which value is truthy?', ['""', '[]', '"0"', 'None'], 2, 'Non empty text.', '"0" has one character, so it is truthy.')
K.quiz('m', 'What does "even" if 7 % 2 == 0 else "odd" give?', ['"even"', '"odd"', 'True', 'An error'], 1, '7 % 2 is 1.', 'The condition is False, so the else value is chosen.')
K.quiz('m', 'day = "Mon". What is day == "Sat" or "Sun"?', ['False', '"Sun"', 'True', '"Mon"'], 1, 'or returns an operand.', 'day == "Sat" is False, so or returns "Sun", which is truthy.')
K.quiz('h', 'In match, what does case x: do?', ['Compares with a variable x', 'Matches anything and binds it to x', 'Raises an error', 'Matches only None'], 1, 'Capture pattern.', 'A bare name is a capture pattern.')
K.quiz('h', 'Which equals not (a or b)?', ['not a or not b', 'not a and not b', 'a and b', 'not a and b'], 1, 'De Morgan.', 'not (a or b) == (not a) and (not b).')
K.quiz('h', 'Does case [a, b]: match the text "ab"?', ['Yes, a = "a", b = "b"', 'No, sequence patterns do not match str', 'Only with a guard', 'It raises TypeError'], 1, 'Strings are special.', 'str, bytes and bytearray never match sequence patterns.')
K.quiz('x', 'In the style of an MIT 6.100L exam: how many test cases are needed at minimum to run every branch of an if, elif, elif, else chain?', ['1', '3', '4', '8'], 2, 'k + 1 paths.', 'Three conditions plus else give 4 paths, each needs one test.')
K.quiz('x', 'In the style of a Princeton COS 126 question: x = 5. What does print(x > 3 and x < 4 or x == 5) show?', ['False', 'True', '5', 'An error'], 1, 'and before or.', '(True and False) or True = False or True = True.')

K.calc('e', 'An elif chain has 4 conditions and an else. How many paths?', '5', 'k + 1.', ['4 conditions, each can be the first True one.', 'Plus else when none is True.', eq('4 + 1 = 5')], check=5)
K.calc('e', 'How many falsy values are in [0, 1, "", "a", None, [], [0]]?', '4', 'Zero and empty.', ['0, "", None, [] are falsy.', '1, "a", [0] are truthy.', eq('4')], check=4)
K.calc('m', 'Three independent if statements (no elif). How many True and False combinations?', '8', '2<sup>k</sup>.', ['Each if is True or False.', 'k = 3.', eq('2<sup>3</sup> = 8')], check=8)
K.calc('m', 'grade(score) gives A for &ge; 90, B for &ge; 75, C for &ge; 50. How many whole scores from 0 to 100 get a B?', '15', '75 to 89.', ['Smallest B is 75.', 'Largest B is 89.', eq('89 &minus; 75 + 1 = 15')], check=15)
K.calc('m', 'Clock angle at 3:30 in degrees.', '75', 'Hour hand moves too.', ['Minute hand: 6 &times; 30 = 180.', 'Hour hand: 30 &times; 3 + 0.5 &times; 30 = 105.', eq('|105 &minus; 180| = 75')], check=75)
K.calc('m', 'Delivery: free above 499, else 20 for members, else 40. A non member orders 450. Delivery charge?', '40', 'Check in order.', ['450 &gt; 499 is False.', 'Not a member.', eq('else: 40')], check=40)
K.calc('h', 'How many whole numbers from 1 to 100 make n % 3 == 0 or n % 5 == 0 True?', '47', 'Inclusion and exclusion.', ['Multiples of 3: 33. Of 5: 20.', 'Of both (15): 6.', eq('33 + 20 &minus; 6 = 47')], check=sum(1 for n in range(1, 101) if n % 3 == 0 or n % 5 == 0))
K.calc('h', 'Clock angle at 9:45 (the smaller one) in degrees.', '22.5', 'Then take min with 360 minus it.', ['Minute: 6 &times; 45 = 270.', 'Hour: 30 &times; 9 + 0.5 &times; 45 = 292.5.', eq('|292.5 &minus; 270| = 22.5')], check=22.5)
K.calc('h', 'How many years from 1901 to 2000 are leap years?', '25', '2000 counts.', ['Divisible by 4: 1904 to 2000, that is 25 years.', 'None of them is 1900. 2000 divides by 400, so it stays.', eq('25')], check=sum(1 for y in range(1901, 2001) if (y % 4 == 0 and y % 100 != 0) or y % 400 == 0))
K.calc('x', 'In the style of a Stanford CS103 problem: a condition has 4 Boolean inputs. How many rows does its full truth table have?', '16', '2<sup>n</sup>.', ['Each input is True or False.', 'n = 4.', eq('2<sup>4</sup> = 16')], check=16)

K.assign('ticket', 'e', 'Cinema ticket price',
         '<p>Write <code>ticket_price(age, is_student)</code>: children under 5 go free (0), people 60 and over pay 100, students pay 120, everyone else pays 200. Check in this order.</p>',
         '''
def ticket_price(age, is_student):
    # your code here
    pass
''', [('ticket_price(3, False)', 0), ('ticket_price(65, True)', 100), ('ticket_price(20, True)', 120), ('ticket_price(30, False)', 200)],
         '''
def ticket_price(age, is_student):
    if age < 5:
        return 0
    elif age >= 60:
        return 100
    elif is_student:
        return 120
    else:
        return 200
''', 'An if, elif, elif, else chain in the order given.', '<p>A 65 year old student pays 100, because the age rule comes first.</p>')
K.assign('season', 'm', 'Month to season with match',
         '<p>Write <code>season(month)</code> for month 1 to 12 using match: 12, 1, 2 give "winter", 3 to 5 "spring", 6 to 8 "summer", 9 to 11 "autumn". Anything else gives "invalid".</p>',
         '''
def season(month):
    # your code here
    pass
''', [('season(1)', 'winter'), ('season(4)', 'spring'), ('season(7)', 'summer'), ('season(10)', 'autumn'), ('season(13)', 'invalid')],
         '''
def season(month):
    match month:
        case 12 | 1 | 2:
            return "winter"
        case 3 | 4 | 5:
            return "spring"
        case 6 | 7 | 8:
            return "summer"
        case 9 | 10 | 11:
            return "autumn"
        case _:
            return "invalid"
''', 'Use or patterns such as case 12 | 1 | 2:, and case _: at the end.', '<p>match with or patterns reads like a table, much clearer than 12 comparisons.</p>')
K.assign('triangle', 'h', 'What kind of triangle',
         '<p>Write <code>triangle(a, b, c)</code> that returns "invalid" if the sides cannot make a triangle (one side is at least the sum of the other two, or a side is not above 0), else "equilateral", "isosceles" or "scalene".</p>',
         '''
def triangle(a, b, c):
    # your code here
    pass
''', [('triangle(3, 3, 3)', 'equilateral'), ('triangle(3, 3, 5)', 'isosceles'), ('triangle(3, 4, 5)', 'scalene'), ('triangle(1, 2, 3)', 'invalid'), ('triangle(0, 1, 1)', 'invalid')],
         '''
def triangle(a, b, c):
    if a <= 0 or b <= 0 or c <= 0:
        return "invalid"
    if a + b <= c or a + c <= b or b + c <= a:
        return "invalid"
    if a == b and b == c:
        return "equilateral"
    elif a == b or b == c or a == c:
        return "isosceles"
    else:
        return "scalene"
''', 'Check that it is a triangle first, then equilateral before isosceles.', '<p>1, 2, 3 is flat (1 + 2 = 3), so it is not a triangle. This is the classic first exercise in software testing books.</p>')

K.must('Chains', 'if, any number of elif, optional else. First truthy condition wins, the rest are skipped. Strictest test first.')
K.must('Truthiness', 'Falsy: False, None, 0, 0.0, "", empty collections. "0" and [0] are truthy.')
K.must('Combining', 'and, or, not, 13 <= x <= 19, x in (a, b). x == a or b is always truthy.')
K.must('One liners', 'a if cond else b. (n := len(x)) assigns inside an expression.')
K.must('match', 'Literal, capture, _, |, [a, *rest], {"k": v}, Class(), guard if. A bare name captures.')

T = K.topic(
    slug='py-conditions', topic='py-conditions', step=(2, 'Control flow', 'py-c2', 'Choose with if, elif, else and match, and repeat with while and for loops.', 'Beginner'),
    title='Making decisions: if, elif, else and match', short='Conditions', badge='2.1', minutes=45,
    lead='Teach your program to choose. Write if, elif and else chains in the right order, understand truthy and falsy values, combine conditions cleanly, use one line conditional expressions, and match data by its shape with match and case.',
    desc='if, if else, elif chains, order of conditions, separate ifs and nesting, truthy and falsy values, and, or, not, chained comparisons, in, conditional expressions, the walrus operator, structural pattern matching with literals, captures, wildcards, sequences, mappings, classes and guards, De Morgan laws.',
    summary='if, elif, else, truthiness, combining conditions, conditional expression, walrus, match and case, De Morgan.',
    keywords=['if', 'elif', 'else', 'conditions', 'truthy', 'falsy', 'ternary', 'walrus', 'match', 'case', 'pattern matching', 'De Morgan', 'PCEP'],
    recap='<p>Python checks conditions from the top and runs the first branch whose condition is truthy. match chooses by the shape of the data.</p>',
    added='2026-11-07', leet=leet_items())
