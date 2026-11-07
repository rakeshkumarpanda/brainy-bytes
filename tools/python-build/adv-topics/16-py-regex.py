# Advanced Python 6.1: regular expressions. Checked against the Python 3.14 documentation of the re module
# (search, match, fullmatch, findall, finditer, sub, subn, split, compile, flags, groups, named groups, lookarounds,
# re.escape, possessive quantifiers and atomic groups from 3.11) and the Regular Expression HOWTO.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, lc, leet, files, grow, leet_items, show, term

chapter('py-regex')
K = Kit()

K.code('basics', r'''
import re

text = "Call 555-1234 or 555-9876 before 6 pm."

m = re.search(r"\d{3}-\d{4}", text)          # the first match anywhere
print(m.group(), m.start(), m.end(), m.span())
print(re.match(r"\d", text))                  # match only looks at the very start
print(re.fullmatch(r"\d{3}-\d{4}", "555-1234") is not None)   # the WHOLE string must match
print(re.findall(r"\d{3}-\d{4}", text))       # every match, as strings
for m in re.finditer(r"\d+", text):           # every match, as match objects
    print(m.group(), m.span())
print(len("\n"), len(r"\n"))                  # a raw string keeps the backslash
''')

K.code('groups', r'''
import re

m = re.search(r"(\d{4})-(\d{2})-(\d{2})", "Due: 2026-11-07.")
print(m.group(0), m.group(1), m.groups())

m = re.search(r"(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})", "Due: 2026-11-07.")
print(m["year"], m.groupdict())

print(re.findall(r"(\w+)@(\w+)\.com", "ann@mail.com, bo@shop.com"))   # groups: findall returns tuples
print(re.findall(r"(?:ha)+", "hahaha hoho haha"))                     # (?:...) groups without capturing
print(re.search(r"\b(\w+) \1\b", "this is is a typo").group())        # \1 means the same text again
print(re.findall(r"cat|dog", "cat, dog, bird, dogs"))                 # | means or
''')

K.code('subsplit', r'''
import re

print(re.sub(r"\s+", " ", "too    many   spaces"))
print(re.sub(r"(\d{4})-(\d{2})-(\d{2})", r"\3/\2/\1", "2026-11-07"))   # reorder with groups
print(re.sub(r"\d+", lambda m: str(int(m.group()) * 2), "3 apples and 10 pears"))
print(re.subn(r"o", "0", "foo boo"))                                  # (new text, how many)
print(re.split(r"[,;\s]+", "a, b;c  d"))
print(re.findall(r"^\w+", "one\ntwo\nthree", flags=re.MULTILINE))     # ^ at the start of every line
print(re.findall(r"python", "Python PYTHON python", flags=re.IGNORECASE))

price = re.compile(r"""
    \$                # a dollar sign
    (\d+)             # dollars
    (?:\.(\d{2}))?    # optional cents
""", re.VERBOSE)
print(price.findall("Tea $3.50, cake $4, coffee $12.05"))
print(re.escape("1+1=2?"))
''')

K.code('greedy', r'''
import re

html = "<b>bold</b> and <i>italic</i>"
print(re.findall(r"<.+>", html))              # greedy: as much as possible
print(re.findall(r"<.+?>", html))             # lazy: as little as possible
print(re.findall(r"\bcat\b", "cat concat cats cat."))   # \b is a word edge

# lookahead (?=...) and negative lookahead (?!...) check without using up characters
strong = re.compile(r"^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}$")
for pw in ["password", "Passw0rd", "Pa1"]:
    print(pw, bool(strong.match(pw)))

print(re.findall(r"(?<=\$)\d+", "cost $30, tax $4, 7 items"))   # lookbehind: digits after a $
print(re.findall(r"\b\d+\b(?! items)", "cost 30, 7 items"))
''')

K.code('parsing', r'''
import re

LINE = re.compile(r"""
    (?P<date>\d{4}-\d{2}-\d{2})\s
    (?P<time>\d{2}:\d{2}:\d{2})\s
    (?P<level>DEBUG|INFO|WARNING|ERROR|CRITICAL)\s
    (?P<logger>[\w.]+):\s
    (?P<message>.*)
""", re.VERBOSE)

logs = [
    "2026-11-07 10:00:01 ERROR shop.pay: card declined for order 1042",
    "this line is broken",
    "2026-11-07 10:00:05 INFO shop.cart: order 1043 saved",
]
for line in logs:
    m = LINE.fullmatch(line)
    if m is None:
        print("skipped:", line)
        continue
    order = re.search(r"order (\d+)", m["message"])
    print(m["level"], m["logger"], order.group(1) if order else None)
''')

K.lesson('idea', 'Regular expressions: patterns for text', f'''
{src('Python 3.14 documentation of the re module and the Regular Expression HOWTO.')}
{wwh('A <b>regular expression</b> (regex) is a small pattern that describes text, such as "three digits, a dash, four digits". Python\'s <b>re</b> module uses patterns to find, check, split and replace text.',
     'Finding a phone number, checking an email address, pulling the date out of a log line or cleaning extra spaces would take many lines of loops and if statements. A pattern does it in one line, and the same pattern works in Python, JavaScript, SQL databases, editors and command line tools.',
     'Write the pattern as a raw string, r"...", so backslashes reach re unchanged. Special characters stand for groups of characters (&#92;d is any digit) or for repetition ({3} means exactly three times). The engine tries the pattern at each place in the text, from left to right, and returns a <b>match object</b> with the text and its position.')}
{viz('pyregex')}
{run('basics')}
{table(['Pattern', 'Matches', 'Pattern', 'Matches'], [
    ['.', 'Any character except a newline', '&#92;d, &#92;D', 'A digit, not a digit'],
    ['&#92;w, &#92;W', 'A word character (letter, digit, _), not one', '&#92;s, &#92;S', 'Whitespace, not whitespace'],
    ['[abc], [a-z]', 'One of these characters, a range', '[^0-9]', 'Any character NOT in the set'],
    ['^, $', 'Start, end of the text (or line with MULTILINE)', '&#92;b', 'A word edge'],
    ['*, +, ?', '0 or more, 1 or more, 0 or 1', '{3}, {2,5}', 'Exactly 3, from 2 to 5'],
    ['a|b', 'a or b', '(...)', 'A group, also captured'],
    ['&#92;. &#92;$ &#92;(', 'A real dot, dollar, bracket', '*?, +?', 'The lazy versions']])}
{versus('Finding things in text', ['', 'str methods (in, find, split, replace)', 're module'], [
    ['Fixed text', 'Best: simple and fast', 'Works, but more than needed'],
    ['Patterns (any digits, optional parts, either or)', 'Many lines of code', 'One pattern'],
    ['Readability', 'Very clear', 'Can be cryptic: use re.VERBOSE and comments'],
    ['Nested structures (HTML, JSON, brackets)', 'No', 'No: use a real parser']],
    'use str methods for fixed text, regex for patterns, and a parser (html.parser, json, xml) for nested formats.')}
''', kw=['regular expression', 'regex', 're module', 'pattern', 'raw string', 'search', 'match object', 'character class', 'quantifier'])

K.lesson('functions', 'search, match, fullmatch, findall, finditer', f'''
{table(['Function', 'Looks', 'Returns'], [
    ['re.search(p, s)', 'Anywhere, first match', 'A match object or None'],
    ['re.match(p, s)', 'Only at the start', 'A match object or None'],
    ['re.fullmatch(p, s)', 'The whole string', 'A match object or None'],
    ['re.findall(p, s)', 'Everywhere', 'A list of strings (or tuples of groups)'],
    ['re.finditer(p, s)', 'Everywhere', 'An iterator of match objects'],
    ['m.group(), m.start(), m.end(), m.span()', 'On a match object', 'The text and where it is']])}
{note('Use fullmatch to check input such as a postcode or a username. search would also accept "xx12345yy" because it finds 12345 inside it.', 'exam')}
''', kw=['re.search', 're.match', 're.fullmatch', 're.findall', 're.finditer', 'group', 'span', 'validation'])

K.lesson('groups', 'Groups: pulling parts out', f'''
{run('groups')}
{table(['Syntax', 'Meaning'], [
    ['(...)', 'Capture this part as group 1, 2, ...'],
    ['(?P&lt;name&gt;...)', 'A named group, read with m["name"] or m.group("name")'],
    ['(?:...)', 'Group without capturing, for | or repeats'],
    ['&#92;1, (?P=name)', 'The same text that group 1 or name matched'],
    ['m.groups(), m.groupdict()', 'All groups as a tuple, named groups as a dict']])}
{note('findall changes what it returns when the pattern has groups: with one group it returns that group\'s text, with several it returns tuples. Use (?:...) for groups you only need for | or repeats.', 'warn')}
''', kw=['capture group', 'named group', 'groupdict', 'non-capturing group', 'backreference', 'alternation'])

K.lesson('subsplit', 'sub, split, flags and compile', f'''
{run('subsplit')}
{table(['Flag', 'Effect'], [
    ['re.IGNORECASE (re.I)', 'Upper and lower case match each other'],
    ['re.MULTILINE (re.M)', '^ and $ match at the start and end of every line'],
    ['re.DOTALL (re.S)', '. matches newlines too'],
    ['re.VERBOSE (re.X)', 'Spaces and # comments in the pattern are ignored'],
    ['re.ASCII (re.A)', '&#92;w, &#92;d and &#92;s match only ASCII characters']])}
{note('re.compile(pattern) gives a pattern object with the same methods. re caches recent patterns, so compiling is mostly about clarity: give a long pattern a name and write it once.', 'tip')}
''', kw=['re.sub', 'replacement function', 're.subn', 're.split', 'flags', 'IGNORECASE', 'MULTILINE', 'DOTALL', 'VERBOSE', 're.compile', 're.escape'])

K.lesson('greedy', 'Greedy, lazy, anchors and lookarounds', f'''
{run('greedy')}
{table(['Syntax', 'Meaning'], [
    ['.*, .+', 'Greedy: take as much as possible, then back off'],
    ['.*?, .+?', 'Lazy: take as little as possible, then take more'],
    ['(?=...), (?!...)', 'Lookahead: what follows must (not) match. Uses up no characters'],
    ['(?&lt;=...), (?&lt;!...)', 'Lookbehind: what comes before must (not) match'],
    ['*+, ++, (?&gt;...)', 'Possessive and atomic (3.11+): never give characters back']])}
{note('Some patterns make the engine try a huge number of ways before failing, for example (a+)+$ on "aaaaaaaaaaaaaaaaaaaaaaaaaaaa!". This is <b>catastrophic backtracking</b>, and attackers use it to freeze servers (ReDoS). Avoid nested repeats of the same thing, or use possessive quantifiers.', 'warn')}
''', kw=['greedy', 'lazy', 'backtracking', 'word boundary', 'lookahead', 'lookbehind', 'password validation', 'catastrophic backtracking', 'ReDoS', 'possessive'])

K.lesson('parsing', 'Parsing real text', f'''
{run('parsing')}
{note('A named, verbose pattern reads like documentation. fullmatch makes sure the line has exactly the expected shape, and broken lines are skipped instead of giving wrong data.', 'tip')}
{deep('How the engine works', '<p>Python\'s re is a <b>backtracking</b> engine: it tries one way, and when it gets stuck, goes back to the last choice and tries another. That makes features like backreferences possible, but can be slow on bad patterns. Engines such as RE2 (Google) turn the pattern into an automaton that never backtracks and always runs in time proportional to the text, but they cannot support backreferences.</p>')}
''', kw=['log parsing', 'verbose regex', 'named groups', 'backtracking engine', 'automaton', 'RE2'])

K.lesson('maths', 'The maths: languages and automata', f'''
{fxs(fx('Choices for a character class', 'patterns of length n over a class of size k match k<sup>n</sup> strings', '&#92;d{4} matches 10<sup>4</sup> = 10,000 strings, 0000 to 9999.', key=True),
     fx('A range of repeats', '[ab]{1,3} matches 2 + 4 + 8 = 14 strings', '&sum; k<sup>i</sup> for i from min to max.'),
     fx('Positions tried by search', 'up to n + 1 starting places', 'Text of length 17: starts 0 to 17.'),
     fx('A regular language', 'built from single characters with union (|), concatenation and star (*)', 'Every such pattern can be matched by a finite automaton with no memory.', key=True),
     fx('Catastrophic backtracking', 'ways to split n letters among nested repeats grows like 2<sup>n</sup>', '(a+)+$ on 30 a\'s followed by "!": about 2<sup>30</sup> &asymp; 10<sup>9</sup> tries.', key=True),
     fx('Linear time engines', 'time = O(m &times; n) for pattern size m and text size n', 'RE2 and Rust\'s regex guarantee this, Python\'s re does not.'))}
{steps('Worked example: how many PIN codes does r"&#92;d{4}" accept, and how many have no repeated digit?', [
    'Each of the 4 places can be any of 10 digits: 10<sup>4</sup> = 10,000 codes.',
    'No repeated digit: 10 choices, then 9, then 8, then 7.',
    '10 &times; 9 &times; 8 &times; 7 = 5040.',
    eq('10,000 codes, of which 5040 have four different digits')])}
''', kw=['regular language', 'finite automaton', 'counting strings', 'backtracking complexity', 'linear time'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>Use &#92;d, &#92;w, &#92;s, ., [ ], *, + and ? with re.search, findall and sub, always in raw strings.</p>',
    '<p>Use groups and named groups, fullmatch for validation, split, flags, re.VERBOSE and re.compile, and lazy quantifiers.</p>',
    '<p>Use lookarounds and backreferences, understand backtracking, avoid catastrophic patterns, and know when a parser is the right tool.</p>',
    '<p>Know regular languages, NFAs and DFAs, Thompson\'s construction, why backreferences make matching NP-hard, and linear time engines such as RE2.</p>')}
{grow('Find and replace with patterns.', 'Validate and parse with groups.', 'Reason about engines and their cost.')}
''', kw=['beginner', 'expert', 'NFA', 'DFA', 'Thompson', 'NP-hard'])

lc(1805, 'Number of Different Integers in a String', 'number-of-different-integers-in-a-string', 'e', 'findall the digit runs', 'r"&#92;d+" finds every run of digits. int() removes leading zeros, and a set keeps the different values.', r'''
import re


def num_different_integers(word):
    return len({int(run) for run in re.findall(r"\d+", word)})
''', [('num_different_integers("a123bc34d8ef34")', 3), ('num_different_integers("leet1234code234")', 2), ('num_different_integers("a1b01c001")', 1)])
lc(2114, 'Maximum Number of Words Found in Sentences', 'maximum-number-of-words-found-in-sentences', 'e', 'Count words with split', 'split() with no argument splits on any run of whitespace, which is the same as re.split(r"&#92;s+", s.strip()).', r'''
def most_words_found(sentences):
    return max(len(s.split()) for s in sentences)
''', [('most_words_found(["alice and bob love leetcode", "i think so too", "this is great thanks very much"])', 6), ('most_words_found(["please wait", "continue to fight", "continue to win"])', 3)])
lc(2788, 'Split Strings by Separator', 'split-strings-by-separator', 'e', 're.split with an escaped separator', 'The separator may be a character that is special in regex, such as "." or "|", so pass it through re.escape. Drop empty pieces.', r'''
import re


def split_words_by_separator(words, separator):
    result = []
    for word in words:
        result += [piece for piece in re.split(re.escape(separator), word) if piece]
    return result
''', [('split_words_by_separator(["one.two.three", "four.five", "six"], ".")', ['one', 'two', 'three', 'four', 'five', 'six']), ('split_words_by_separator(["$easy$", "$problem$"], "$")', ['easy', 'problem']), ('split_words_by_separator(["|||"], "|")', [])])
lc(1910, 'Remove All Occurrences of a Substring', 'remove-all-occurrences-of-a-substring', 'm', 'A stack of characters', 'Removing one copy can create a new one, so a single re.sub is not enough. Build the result character by character and cut the part off whenever it ends with it.', r'''
def remove_occurrences(s, part):
    result = []
    n = len(part)
    for ch in s:
        result.append(ch)
        if len(result) >= n and "".join(result[-n:]) == part:
            del result[-n:]
    return "".join(result)
''', [('remove_occurrences("daabcbaabcbc", "abc")', 'dab'), ('remove_occurrences("axxxxyyyyb", "xy")', 'ab')])
lc(722, 'Remove Comments', 'remove-comments', 'm', 'Join the lines, then one regex', 'Join the source with newlines. r"//.*|/&#92;*(.|&#92;n)*?&#92;*/" matches a line comment or a block comment (lazy, across lines). Remove them, split again and drop empty lines.', r'''
import re


def remove_comments(source):
    text = "\n".join(source)
    text = re.sub(r"//.*|/\*(?:.|\n)*?\*/", "", text)
    return [line for line in text.split("\n") if line]
''', [('remove_comments(["/*Test program */", "int main()", "{ ", "  // variable declaration ", "int a, b, c;", "/* This is a test", "   multiline  ", "   comment for ", "   testing */", "a = b + c;", "}"])', ['int main()', '{ ', '  ', 'int a, b, c;', 'a = b + c;', '}']), ('remove_comments(["a/*comment", "line", "more_comment*/b"])', ['ab'])])
lc(1023, 'Camelcase Matching', 'camelcase-matching', 'm', 'Build a regex from the pattern', 'Between and around the pattern letters, only lower case letters may be added: "FB" becomes ^[a-z]*F[a-z]*B[a-z]*$.', r'''
import re


def camel_match(queries, pattern):
    regex = "^[a-z]*" + "[a-z]*".join(re.escape(ch) for ch in pattern) + "[a-z]*$"
    return [re.match(regex, q) is not None for q in queries]
''', [('camel_match(["FooBar", "FooBarTest", "FootBall", "FrameBuffer", "ForceFeedBack"], "FB")', [True, False, True, True, False]), ('camel_match(["FooBar", "FooBarTest", "FootBall", "FrameBuffer", "ForceFeedBack"], "FoBa")', [True, False, True, False, False])])
lc(1451, 'Rearrange Words in a Sentence', 'rearrange-words-in-a-sentence', 'm', 'A stable sort by length', 'Lower case the words, sort by length (sorted is stable, so equal lengths keep their order), then capitalise the first letter of the result.', r'''
def arrange_words(text):
    words = sorted(text.lower().split(), key=len)
    sentence = " ".join(words)
    return sentence[0].upper() + sentence[1:]
''', [('arrange_words("Leetcode is cool")', 'Is cool leetcode'), ('arrange_words("Keep calm and code on")', 'On and keep calm code'), ('arrange_words("To be or not to be")', 'To be or to be not')])
lc(10, 'Regular Expression Matching', 'regular-expression-matching', 'h', 'Dynamic programming over the two strings', 'match(i, j) asks whether s[i:] matches p[j:]. With a * after p[j], either skip "x*" or use it once if the first characters match. Memoise with lru_cache.', r'''
from functools import lru_cache


def is_match(s, p):
    @lru_cache(maxsize=None)
    def match(i, j):
        if j == len(p):
            return i == len(s)
        first = i < len(s) and p[j] in (s[i], ".")
        if j + 1 < len(p) and p[j + 1] == "*":
            return match(i, j + 2) or (first and match(i + 1, j))
        return first and match(i + 1, j + 1)

    return match(0, 0)
''', [('is_match("aa", "a")', False), ('is_match("aa", "a*")', True), ('is_match("ab", ".*")', True), ('is_match("mississippi", "mis*is*p*.")', False), ('is_match("aab", "c*a*b")', True)])
lc(44, 'Wildcard Matching', 'wildcard-matching', 'h', 'The same dynamic programming with ? and *', '? matches one character, * any run (also empty). A * can either match nothing (move in the pattern) or one more character (move in the text).', r'''
from functools import lru_cache


def is_wildcard_match(s, p):
    @lru_cache(maxsize=None)
    def match(i, j):
        if j == len(p):
            return i == len(s)
        if p[j] == "*":
            return match(i, j + 1) or (i < len(s) and match(i + 1, j))
        return i < len(s) and p[j] in (s[i], "?") and match(i + 1, j + 1)

    return match(0, 0)
''', [('is_wildcard_match("aa", "a")', False), ('is_wildcard_match("aa", "*")', True), ('is_wildcard_match("cb", "?a")', False), ('is_wildcard_match("adceb", "*a*b")', True), ('is_wildcard_match("acdcb", "a*c?b")', False)])
lc(591, 'Tag Validator', 'tag-validator', 'h', 'Regex for the pieces, a stack for the nesting', 'Regex cannot check nesting, so use it only for the pieces: remove CDATA blocks, then find tags with a regex and match open and close tags with a stack.', r'''
import re


def is_valid_tag_code(code):
    code = re.sub(r"<!\[CDATA\[.*?\]\]>", "c", code)
    stack = []
    i = 0
    while i < len(code):
        if i > 0 and not stack:
            return False
        m = re.match(r"<(/?)([A-Z]{1,9})>", code[i:])
        if m:
            name = m.group(2)
            if m.group(1):
                if not stack or stack.pop() != name:
                    return False
            else:
                stack.append(name)
            i += m.end()
        elif code[i] == "<":
            return False
        else:
            i += 1
    return not stack and len(code) > 0 and code.startswith("<")
''', [('is_valid_tag_code("<DIV>This is the first line <![CDATA[<div>]]></DIV>")', True), ('is_valid_tag_code("<DIV>>>  ![cdata[]] <![CDATA[<div>]>]]>]]>>]</DIV>")', True), ('is_valid_tag_code("<A>  <B> </A>   </B>")', False), ('is_valid_tag_code("<DIV>  div tag is not closed  <DIV>")', False), ('is_valid_tag_code("<A></A><B></B>")', False)])

K.lesson('leetcode', 'LeetCode practice', leet('<p>The easy ones use findall, split and re.escape. The medium ones build a pattern from the input or use a lazy block comment pattern. The hard ones are classics: write your own matcher for . and * (how a regex engine works inside), wildcard matching, and a tag validator that shows where regex stops and a stack must take over.</p>'), kw=['LeetCode', 'regex', 'findall', 're.escape', 'dynamic programming', 'pattern matching', 'stack'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'Write patterns as raw strings. &#92;d &#92;w &#92;s . [ ] are characters, * + ? {m,n} are repeats, ^ $ &#92;b are positions.',
    'search finds the first match, match only at the start, fullmatch the whole string. findall gives strings, finditer match objects.',
    'Groups ( ) and named groups (?P&lt;name&gt;...) pull out parts. (?:...) groups without capturing.',
    'sub replaces (with &#92;1 or a function), split cuts. Flags: IGNORECASE, MULTILINE, DOTALL, VERBOSE.',
    'Repeats are greedy unless you add ?. Lookarounds check without using characters. Avoid nested repeats (ReDoS).',
    'Regex is for patterns, not nested formats: use a parser for HTML, JSON and XML.'],
    'Next: reading and writing CSV, JSON, XML, configuration files and pickles.')}
{files('Three tasks: find email addresses, turn dates around with named groups, and write a small tokenizer for arithmetic.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'Which pattern matches exactly three digits?', [r'&#92;d3', r'&#92;d{3}', r'[3]', r'&#92;d+3'], 1, 'Curly brackets count.', r'{3} repeats the item before it three times.')
K.quiz('e', 'What does re.findall(r"&#92;d+", "a1b22c333") return?', ["['1', '22', '333']", '[1, 22, 333]', "['1', '2', '2', '3', '3', '3']", "'122333'"], 0, 'Strings, runs of digits.', 'findall returns a list of the matched strings.')
K.quiz('e', 'Why write regex patterns as raw strings like r"&#92;d"?', ['They are faster', 'Python then leaves the backslashes alone for re to read', 'They allow Unicode', 're needs bytes'], 1, 'Escape sequences.', 'In a normal string, "&#92;b" would become a backspace character.')
K.quiz('m', 'Which function checks that the WHOLE string is a 5 digit postcode?', [r're.search(r"&#92;d{5}", s)', r're.match(r"&#92;d{5}", s)', r're.fullmatch(r"&#92;d{5}", s)', r're.findall(r"&#92;d{5}", s)'], 2, 'All of it.', 'search and match would accept extra text after (or around) the digits.')
K.quiz('m', 're.findall(r"&lt;.+&gt;", "&lt;a&gt;&lt;b&gt;") returns what?', ["['&lt;a&gt;', '&lt;b&gt;']", "['&lt;a&gt;&lt;b&gt;']", "['a', 'b']", '[]'], 1, 'Greedy.', '.+ runs as far as it can, so one match covers both tags. Use .+? for two matches.')
K.quiz('m', 'What does (?:ab)+ do differently from (ab)+?', ['Nothing', 'It groups without capturing', 'It matches lazily', 'It is a lookahead'], 1, 'Non-capturing.', 'Useful with findall, which would otherwise return only the group.')
K.quiz('m', 'What does re.sub(r"(&#92;w+) (&#92;w+)", r"&#92;2 &#92;1", "hello world") give?', ['hello world', 'world hello', '&#92;2 &#92;1', 'helloworld'], 1, 'Backreferences in the replacement.', '&#92;2 is the second group, &#92;1 the first.')
K.quiz('m', 'Which flag makes ^ match at the start of every line?', ['re.DOTALL', 're.MULTILINE', 're.IGNORECASE', 're.VERBOSE'], 1, 'Many lines.', 'Without it, ^ only matches at the start of the whole text.')
K.quiz('h', 'What does (?=.*&#92;d) do at the start of a password pattern?', ['Matches one digit and uses it up', 'Checks that a digit appears somewhere ahead, without using up characters', 'Forbids digits', 'Matches the end'], 1, 'Lookahead.', 'Several lookaheads can each check one rule.')
K.quiz('h', 'Why can (a+)+$ freeze on "aaaaaaaaaaaaaaaaaaaaaaaaa!"?', ['It is a syntax error', 'The engine tries an exponential number of ways to split the a\'s before failing', 'The text is too long', 're has a bug'], 1, 'Catastrophic backtracking.', 'Nested repeats of the same thing create about 2<sup>n</sup> paths.')
K.quiz('h', 'Why should you not parse nested HTML with one regex?', ['Regex is slow', 'Nesting to any depth is not a regular language, so a pattern cannot track it', 'HTML is binary', 're forbids <'], 1, 'Counting needs memory.', 'Use html.parser, BeautifulSoup or lxml.')
K.quiz('x', 'In the style of a Stanford CS103 exam: which language can no regular expression describe?', ['All strings of a\'s and b\'s', 'Strings with an even number of a\'s', 'a<sup>n</sup>b<sup>n</sup>: some a\'s followed by the same number of b\'s', 'Strings ending in ab'], 2, 'The pumping lemma.', 'A finite automaton cannot count without limit, so a<sup>n</sup>b<sup>n</sup> is not regular.')
K.quiz('x', 'In the style of an MIT 6.045 exam: what is the size of the DFA for "the n-th letter from the end is a" over {a, b}, in the worst case?', ['n states', '2n states', '2<sup>n</sup> states', 'n² states'], 2, 'Remember the last n letters.', 'The DFA must remember which of the last n letters were a, which needs 2<sup>n</sup> states, while an NFA needs only n + 1.')

K.calc('e', 'How many different strings does r"&#92;d{3}" match?', '1000', '10 choices, 3 times.', ['10 &times; 10 &times; 10.', 'From 000 to 999.', eq('1000')], check=10 ** 3)
K.calc('e', 'How many matches does re.findall(r"o", "foo boo zoo") return?', '6', 'Count the o letters.', ['foo has 2, boo 2, zoo 2.', '2 + 2 + 2.', eq('6')], check=6)
K.calc('e', 're.search(r"&#92;d+", "abc 42 x") finds 42. What is m.start()?', '4', 'Count from 0.', ['a=0, b=1, c=2, space=3.', '4 is the 4.', eq('4')], check=4)
K.calc('m', 'How many strings does r"[ab]{1,3}" match?', '14', '2 + 4 + 8.', ['Length 1: 2.', 'Length 2: 4, length 3: 8.', eq('14')], check=2 + 4 + 8)
K.calc('m', 'How many starting places can re.search try in a text of 17 characters?', '18', 'n + 1.', ['Starts 0 to 16.', 'Plus the empty end position 17.', eq('18')], check=18)
K.calc('m', 're.subn(r"&#92;s+", " ", "a  b   c d") gives (text, n). What is n?', '3', 'Count the runs of spaces.', ['"  ", "   " and " ".', 'Each run is one replacement.', eq('3')], check=3)
K.calc('m', 'How many 4 digit PIN codes have four different digits?', '5040', '10 &times; 9 &times; 8 &times; 7.', ['10 choices for the first.', 'One fewer each time.', eq('5040')], check=10 * 9 * 8 * 7)
K.calc('h', 'About how many ways can (a+)+ split 20 a\'s? Use 2<sup>n &minus; 1</sup>.', '524288', '2<sup>19</sup>.', ['Between each pair of a\'s, split or not.', '19 gaps: 2<sup>19</sup>.', eq('524,288')], check=2 ** 19)
K.calc('h', 'How many strings of length 8 does r"[a-z0-9]{8}" match? Give the power of 36 as a number: 36 to the what?', '8', 'k<sup>n</sup>.', ['26 letters + 10 digits = 36.', 'Length 8.', eq('36<sup>8</sup>')], check=8)
K.calc('x', 'In the style of an MIT 6.045 exam: an NFA for "the 5th letter from the end is a" has 6 states. How many states does the smallest DFA need?', '32', '2<sup>n</sup>.', ['The DFA remembers the last 5 letters.', '2<sup>5</sup>.', eq('32')], check=32)

K.assign('emails', 'e', 'Find the email addresses',
         '<p>Write <code>find_emails(text)</code> that returns every email address in text, in order. An address here is one or more of letters, digits, dots, underscores or dashes, then @, then a domain made of words separated by dots, ending in a dot and 2 or more letters. Use re.findall.</p>',
         '''
import re


def find_emails(text):
    return re.findall(r"\\w+@\\w+", text)
''', [('find_emails("Write to ann.lee@mail.com or bo_2@shop.co.uk today.")', ['ann.lee@mail.com', 'bo_2@shop.co.uk']), ('find_emails("no email here, just @ and .com")', []), ('find_emails("x-y@a.io, z@b")', ['x-y@a.io'])],
         '''
import re


def find_emails(text):
    return re.findall(r"[\\w.-]+@(?:\\w+\\.)+[A-Za-z]{2,}", text)
''', 'Name part: [&#92;w.-]+. Domain: (?:&#92;w+&#92;.)+ for "shop." and "co.", then [A-Za-z]{2,} for the ending. The group must be non-capturing, or findall would return only the group.', '<p>Real email rules (RFC 5322) are far more complex. For checking addresses in a sign up form, a simple pattern plus sending a confirmation email is the usual approach.</p>')
K.assign('dates', 'm', 'Turn dates around with named groups',
         '<p>Write <code>us_to_iso(text)</code> that changes every US date like 11/07/2026 (month/day/year) into the ISO form 2026-11-07, and leaves everything else alone. Use re.sub with named groups (?P&lt;month&gt;...) and refer to them in the replacement as &#92;g&lt;name&gt;. Months and days always have two digits.</p>',
         '''
import re


def us_to_iso(text):
    return re.sub(r"(\\d{2})/(\\d{2})/(\\d{4})", r"\\3-\\2-\\1", text)
''', [('us_to_iso("Due 11/07/2026.")', 'Due 2026-11-07.'), ('us_to_iso("01/02/2025 and 12/31/2025")', '2025-01-02 and 2025-12-31'), ('us_to_iso("no dates, 5/6 is a fraction")', 'no dates, 5/6 is a fraction')],
         '''
import re


def us_to_iso(text):
    return re.sub(r"(?P<month>\\d{2})/(?P<day>\\d{2})/(?P<year>\\d{4})", r"\\g<year>-\\g<month>-\\g<day>", text)
''', 'In month/day/year the month is first. The starter swaps day and month. Names make the order impossible to get wrong: &#92;g&lt;year&gt;-&#92;g&lt;month&gt;-&#92;g&lt;day&gt;.', '<p>Named groups document themselves. For real date work, parse with datetime.strptime and format with strftime, which also checks that the date exists.</p>')
K.assign('tokens', 'h', 'A tokenizer for arithmetic',
         '<p>Write <code>tokenize(expr)</code> that splits an expression like "3 + 4.5*(x - 2)" into a list of [kind, text] pairs, skipping spaces. Kinds: NUMBER (digits with an optional decimal part), NAME (a letter or _ then letters, digits or _), OP (one of + - * / ( )). Any other character raises ValueError. Use one pattern with named alternatives and re.finditer, checking m.lastgroup.</p>',
         '''
import re


def tokenize(expr):
    return [["OP", ch] for ch in expr if ch != " "]


def error_of(expr):
    try:
        tokenize(expr)
    except ValueError:
        return "ValueError"
    return "no error"
''', [('tokenize("3 + 4.5*(x - 2)")', [['NUMBER', '3'], ['OP', '+'], ['NUMBER', '4.5'], ['OP', '*'], ['OP', '('], ['NAME', 'x'], ['OP', '-'], ['NUMBER', '2'], ['OP', ')']]), ('tokenize("rate_2/10")', [['NAME', 'rate_2'], ['OP', '/'], ['NUMBER', '10']]), ('tokenize("")', []), ('error_of("2 $ 3")', 'ValueError')],
         '''
import re

TOKEN = re.compile(r"""
    (?P<NUMBER>\\d+(?:\\.\\d+)?)
  | (?P<NAME>[A-Za-z_]\\w*)
  | (?P<OP>[-+*/()])
  | (?P<SPACE>\\s+)
  | (?P<ERROR>.)
""", re.VERBOSE)


def tokenize(expr):
    tokens = []
    for m in TOKEN.finditer(expr):
        kind = m.lastgroup
        if kind == "SPACE":
            continue
        if kind == "ERROR":
            raise ValueError(f"unexpected character {m.group()!r} at {m.start()}")
        tokens.append([kind, m.group()])
    return tokens


def error_of(expr):
    try:
        tokenize(expr)
    except ValueError:
        return "ValueError"
    return "no error"
''', 'One VERBOSE pattern with named alternatives in priority order. m.lastgroup is the name of the alternative that matched. A last catch all (?P&lt;ERROR&gt;.) finds bad characters.', '<p>This is how real tokenizers start, including Python\'s own tokenize module and the first step of compilers. The tokens then go to a parser that understands precedence and brackets.</p>')

K.must('Syntax', '. &#92;d &#92;w &#92;s [abc] [^abc] ^ $ &#92;b, repeats * + ? {m,n}, lazy *? +?, | and ( ). Always raw strings.')
K.must('Functions', 'search (anywhere), match (start), fullmatch (whole), findall (strings), finditer (match objects), sub, subn, split.')
K.must('Groups', 'm.group(n), m.groups(), (?P&lt;name&gt;...), m.groupdict(), (?:...) non-capturing, &#92;1 backreference, &#92;g&lt;name&gt; in sub.')
K.must('Flags', 'IGNORECASE, MULTILINE, DOTALL, VERBOSE. re.compile for named patterns, re.escape for literal text.')
K.must('Care', 'Greedy versus lazy, lookarounds (?=) (?!) (?<=) (?<!), no nested repeats (ReDoS), parsers for nested formats.')

T = K.topic(
    slug='py-regex', topic='py-regex', step=(6, 'The standard library toolbox: text, data, databases and GUIs', 'py-a6', 'Find patterns in text, read and write data formats, store data in SQLite, and build desktop windows with tkinter.', 'Advanced'),
    title='Regular expressions', short='Regular expressions', badge='6.1', minutes=75,
    lead='Find, check and change text with patterns. Learn the regex syntax, search, match, fullmatch, findall and finditer, groups and named groups, sub and split, flags and compile, greedy and lazy repeats, lookarounds, and how the engine backtracks.',
    desc='regular expressions, raw strings, character classes, quantifiers, anchors, word boundaries, re.search, re.match, re.fullmatch, re.findall, re.finditer, match objects, capture groups, named groups, non-capturing groups, backreferences, re.sub with functions, re.split, flags, re.VERBOSE, re.compile, re.escape, greedy and lazy matching, lookahead and lookbehind, catastrophic backtracking, regular languages and automata.',
    summary='regex syntax, the re functions, groups, sub and split, flags, greedy and lazy, lookarounds.',
    keywords=['regex', 'regular expression', 're', 'search', 'findall', 'groups', 'sub', 'split', 'lookahead', 'greedy', 'lazy'],
    recap='<p>Raw string patterns, fullmatch to validate, named groups to extract, and a real parser for anything nested.</p>',
    added='2026-11-07', leet=leet_items())
