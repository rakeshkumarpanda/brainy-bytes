# Core Python 3.1: strings. Follows PCEP-30-02 section 3.4 (strings: constructing, indexing, slicing, immutability,
# escaping with the backslash, quotes and apostrophes, multi line strings, basic methods) and PCAP-31-03 section 2
# (strings in detail: ASCII, UNICODE, UTF-8, code points, ord() and chr(), comparing strings, string methods),
# checked against the Python 3.14 library reference section "Text Sequence Type str".
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, lc, leet, files, grow, leet_items

chapter('py-strings')
K = Kit()

K.code('make', r'''
a = 'single quotes'
b = "double quotes"
c = "It's easy"            # an apostrophe inside double quotes
d = 'She said "hi"'        # double quotes inside single quotes
e = """Three quotes
let a string run over
many lines"""
print(a, b, c, d, sep=" | ")
print(e)
print(len("hello"), len(""), len("  "))
print(str(42) + "!", str(3.5), str(True))
''')

K.code('escape', r'''
print("one\ttab")           # \t is a tab
print("line 1\nline 2")     # \n is a new line
print("a backslash: \\")    # \\ is one backslash
print('it\'s')              # \' is a quote inside the same quotes
print(r"C:\new\folder")     # r"..." is a raw string: backslashes stay as they are
print(len("\n"), len(r"\n"))  # one character or two
''')

K.code('index', r'''
word = "PYTHON"
print(word[0], word[1], word[5])     # first, second, last
print(word[-1], word[-2])            # negative index counts from the right
print(word[0:2], word[2:], word[:3]) # slices: start included, stop excluded
print(word[::2], word[::-1])         # every second letter, and reversed
print(word[1:100])                   # a slice never fails
try:
    print(word[10])
except IndexError as err:
    print("IndexError:", err)
''')

K.code('immut', r'''
name = "rita"
try:
    name[0] = "R"
except TypeError as err:
    print("TypeError:", err)

# You cannot change a string, but you can build a new one
name = "R" + name[1:]
print(name)
print(name.upper(), name)     # upper() returns a new string, name is unchanged
''')

K.code('ops', r'''
print("ab" + "cd")        # join two strings
print("ha" * 3)           # repeat
print("cat" in "concatenate", "dog" not in "hotdog")
print("apple" < "banana", "Zebra" < "apple", "10" < "9")
print(min("python"), max("python"))
for ch in "abc":
    print(ch, ord(ch))
print(chr(65), chr(97), chr(8377))
''')

K.code('methods', r'''
s = "  Hello, World  "
print(repr(s.strip()), repr(s.lstrip()), repr(s.rstrip()))
t = s.strip()
print(t.upper(), t.lower(), t.swapcase())
print("hello world".title(), "hello world".capitalize())
print(t.replace("World", "Python"))
print(t.startswith("Hell"), t.endswith("!"))
print(t.find("o"), t.rfind("o"), t.find("z"), t.count("l"))
print(t.index("W"))
print("42".isdigit(), "abc".isalpha(), "a1".isalnum(), "   ".isspace())
print("7".zfill(3), "hi".center(8, "*"), "hi".ljust(5) + "|", "hi".rjust(5))
print("report.pdf".removesuffix(".pdf"), "Mr Rao".removeprefix("Mr "))
''')

K.code('split', r'''
line = "apple,mango,,banana"
parts = line.split(",")
print(parts, len(parts))
print("  many   spaces here ".split())      # no argument: split on any run of spaces
print("a-b-c-d".split("-", 2))             # at most 2 splits
print("a-b-c-d".rsplit("-", 1))
print("-".join(["2026", "11", "07"]))
print("".join(reversed("stressed")))
print("user@example.com".partition("@"))
print("one\ntwo\nthree".splitlines())
''')

K.code('build', r'''
# Building text: join a list instead of adding in a loop
words = []
for i in range(1, 6):
    words.append(str(i * i))
print(", ".join(words))

# Counting letters with a simple loop
text = "banana"
count_a = 0
for ch in text:
    if ch == "a":
        count_a += 1
print(count_a, text.count("a"))

# Caesar cipher: move each letter 3 places
secret = ""
for ch in "attack at dawn":
    if ch.isalpha():
        secret += chr((ord(ch) - ord("a") + 3) % 26 + ord("a"))
    else:
        secret += ch
print(secret)
''')

K.code('unicode', r'''
for ch in ["A", "a", "é", "₹", "न", "😀"]:
    data = ch.encode("utf-8")
    print(ch, "code point", ord(ch), "hex", hex(ord(ch)), "bytes", len(data), list(data))

word = "café"
print(len(word), len(word.encode("utf-8")))
raw = word.encode("utf-8")
print(raw, raw.decode("utf-8"))
print("Straße".lower(), "Straße".casefold())   # casefold is the stronger lower case for comparing
''')

K.lesson('idea', 'What a string is', f'''
{src('Python 3.14 library reference, Text Sequence Type str. PCEP-30-02 section 3.4 and PCAP-31-03 section 2.')}
{wwh('A <b>string</b> (type str) is a piece of text: a sequence of characters such as letters, digits, spaces and symbols. You write it between quotes: single, double, or three of either for many lines.',
     'Almost every program works with text: names, messages, file contents, web pages, passwords. Numbers alone cannot hold "Hello, Asha". The str type stores any text in any language and gives you more than 40 ready made tools (methods) to work with it.',
     'Python keeps the characters in order, so each one has a position number (an <b>index</b>) starting at 0. You can read one character, cut out a part (a <b>slice</b>), join strings and search inside them. A string never changes after it is made. Every change builds a new string.')}
{scene('a name on a train ticket', '<p>A train ticket prints "RAVI KUMAR". The booking app stored what you typed, "  ravi kumar ", then removed the extra spaces with strip(), made it upper case with upper(), and printed it. It checked the PNR number with isdigit() and cut the coach number out of "B2-34" with a slice. Every one of these steps is a string method from this chapter.</p>')}
{run('make')}
{note('Single and double quotes make exactly the same string. Pick one style and keep it. Use the other kind when the text itself contains a quote.', 'tip')}
''', kw=['string', 'str', 'text', 'quotes', 'multi line string', 'len', 'str()'])

K.lesson('escape', 'Escape characters and raw strings', f'''
{run('escape')}
{table(['You write', 'You get', 'Name'], [
    ['<code>&#92;n</code>', 'a new line', 'newline'],
    ['<code>&#92;t</code>', 'a tab', 'tab'],
    ['<code>&#92;&#92;</code>', 'one backslash', 'backslash'],
    ['<code>&#92;&#39;</code> and <code>&#92;&quot;</code>', 'a quote inside quotes of the same kind', 'quote'],
    ['<code>&#92;u20b9</code>', 'the character with code point 20B9 (the rupee sign)', 'Unicode escape']])}
{note('A backslash starts an <b>escape sequence</b>: the backslash and the next character together stand for one special character. That is why len of the new line escape is 1. In a raw string (r before the quote) Python keeps every backslash, which is handy for Windows paths and regular expressions (Advanced 6.1).', 'exam')}
''', kw=['escape sequence', 'backslash', 'newline', 'tab', 'raw string', 'r string'])

K.lesson('index', 'Indexing and slicing', f'''
{viz('pystr')}
{run('index')}
{fxs(fx('Index of a character', '0, 1, ..., len(s) &minus; 1 from the left, and &minus;1, &minus;2, ..., &minus;len(s) from the right', 's[-k] is the same as s[len(s) &minus; k].', key=True),
     fx('Slice', 's[start:stop:step]', 'start is included, stop is not. Leave out start for "from the beginning" and stop for "to the end".', key=True),
     fx('Length of a simple slice', 'len(s[a:b]) = b &minus; a', 'when 0 &le; a &le; b &le; len(s). "PYTHON"[1:4] is "YTH", 3 characters.'))}
{note('A single index outside the string raises IndexError. A slice outside the string never fails: it just gives what is there, or an empty string.', 'exam')}
''', kw=['index', 'negative index', 'slice', 'start stop step', 'reverse string', 'IndexError'])

K.lesson('immut', 'Strings never change', f'''
{run('immut')}
{versus('Changing text', ['', 'str (immutable)', 'list of characters (mutable)'], [
    ['Change one character', 'Not allowed: build a new string', 'chars[0] = "R" works'],
    ['Safe to share', 'Yes, nobody can change it behind your back', 'No, every name sees the change'],
    ['Can be a dict key or set item', 'Yes', 'No'],
    ['Best for', 'Storing and passing text around', 'Many small edits, then "".join(chars) at the end']],
    'keep text as str. If you need hundreds of edits in place, turn it into a list, edit, and join it back.')}
{deep('Why Python made strings immutable', '<p>Because a string cannot change, Python can work out its hash once and keep it, which makes strings fast dict keys. Two names can share the same string object without risk, and Python reuses (interns) many short strings. Use == to compare text. Never use is, because whether two equal strings are the same object depends on the interpreter.</p>')}
''', kw=['immutable', 'TypeError', 'item assignment', 'new string', 'interning', 'is vs =='])

K.lesson('ops', 'Joining, repeating, searching and comparing', f'''
{run('ops')}
{table(['Operation', 'Example', 'Result'], [
    ['+ joins', '"ab" + "cd"', '"abcd"'],
    ['* repeats', '"ha" * 3', '"hahaha"'],
    ['in searches', '"cat" in "concatenate"', 'True'],
    ['&lt; &gt; compare', '"apple" &lt; "banana"', 'True'],
    ['ord()', 'ord("A")', '65'],
    ['chr()', 'chr(97)', '"a"']])}
{note('Strings are compared letter by letter by code point, not by dictionary order. All upper case letters (65 to 90) come before all lower case letters (97 to 122), so "Zebra" &lt; "apple" is True. "10" &lt; "9" is True too, because "1" comes before "9". Turn text into numbers before comparing numbers.', 'warn')}
''', kw=['concatenation', 'repetition', 'in operator', 'string comparison', 'ord', 'chr', 'lexicographic'])

K.lesson('methods', 'The most used string methods', f'''
{run('methods')}
{table(['Group', 'Methods', 'Note'], [
    ['Clean', 'strip(), lstrip(), rstrip(), removeprefix(), removesuffix()', 'strip() with no argument removes spaces, tabs and new lines at both ends'],
    ['Case', 'upper(), lower(), title(), capitalize(), swapcase(), casefold()', 'Use casefold() to compare text without caring about case'],
    ['Search', 'find(), rfind(), index(), rindex(), count(), startswith(), endswith()', 'find() gives &minus;1 when not found, index() raises ValueError'],
    ['Test', 'isdigit(), isalpha(), isalnum(), isspace(), isupper(), islower()', 'Return True or False. An empty string gives False'],
    ['Change', 'replace(old, new, count)', 'Returns a new string'],
    ['Pad', 'zfill(), center(), ljust(), rjust()', 'Make columns of the same width']])}
{note('Every method returns a new string. s.upper() alone on a line does nothing useful. Write s = s.upper() to keep the result.', 'warn')}
''', kw=['string methods', 'strip', 'upper', 'lower', 'replace', 'find', 'index', 'count', 'isdigit', 'zfill', 'casefold'])

K.lesson('split', 'split and join', f'''
{run('split')}
{versus('Building one string from many pieces', ['', 'Adding in a loop (s += piece)', '"sep".join(pieces)'], [
    ['Code', 'result = "" then result += w + ", " each turn', '", ".join(words)'],
    ['Extra separator at the end', 'Yes, you must remove it', 'No'],
    ['Speed', 'Each += may copy the whole text so far: up to O(n<sup>2</sup>) work', 'Works out the size once and copies each piece once: O(n)'],
    ['Pieces must be', 'Anything you convert with str()', 'All strings already']],
    'collect the pieces in a list and join them once at the end.')}
{note('split() with no argument and split(" ") are different. "a  b".split() gives ["a", "b"], but "a  b".split(" ") gives ["a", "", "b"] because there are two spaces.', 'exam')}
''', kw=['split', 'join', 'rsplit', 'partition', 'splitlines', 'separator', 'string building'])

K.lesson('build', 'Working through text with loops', f'''
{run('build')}
{note('Most text problems follow one plan: walk through the characters with for ch in text, test each one (isalpha, isdigit, a comparison), and collect or count the ones you want. The Caesar cipher above uses ord() and chr() to do arithmetic on letters.', 'tip')}
''', kw=['loop over string', 'count characters', 'Caesar cipher', 'ord chr arithmetic'])

K.lesson('unicode', 'Unicode, code points and UTF-8', f'''
{viz('pyutf8')}
{run('unicode')}
{wwh('<b>Unicode</b> gives every character of every language a number called a <b>code point</b>. "A" is 65, "₹" is 8377 (U+20B9). <b>UTF-8</b> is the most common way to store those numbers as bytes.',
     'Old ASCII had only 128 characters, enough for English but not for Hindi, Tamil, Chinese or emojis. Unicode covers more than 150,000 characters, so one program can handle every language.',
     'A Python str holds code points, so len() counts characters. When you save to a file or send over a network, encode() turns the text into bytes and decode() turns bytes back into text. UTF-8 uses 1 byte for ASCII and 2, 3 or 4 bytes for other characters.')}
{table(['Code point range', 'UTF-8 bytes', 'Examples'], [
    ['0 to 127', '1', 'A, z, 5, space'],
    ['128 to 2,047', '2', 'é, ñ, Greek and Arabic letters'],
    ['2,048 to 65,535', '3', '₹, Hindi and most Indian scripts, Chinese'],
    ['65,536 to 1,114,111', '4', 'emojis, old scripts']])}
{note('Always say the encoding when you open a text file: open(name, encoding="utf-8"). Otherwise Python uses the system default, which is not UTF-8 on every Windows computer (Core 5.3).', 'warn')}
''', kw=['Unicode', 'code point', 'UTF-8', 'ASCII', 'encode', 'decode', 'bytes', 'casefold'])

K.lesson('versus', 'str, bytes and lists of characters', f'''
{versus('Three ways to hold text', ['', 'str', 'bytes', 'list of str'], [
    ['Holds', 'Unicode characters', 'Numbers 0 to 255', 'Any items, here single characters'],
    ['Written as', '"café"', 'b"caf&#92;xc3&#92;xa9"', '["c", "a", "f", "é"]'],
    ['Changeable', 'No', 'No (bytearray is)', 'Yes'],
    ['len("café")', '4 characters', '5 bytes in UTF-8', '4 items'],
    ['Used for', 'Text you read and show', 'Files, images, network data', 'Editing text one character at a time']],
    'use str for text inside your program, bytes only at the edges where data goes to a file or the network.')}
{deep('How CPython stores a str (PEP 393)', '<p>CPython looks at the largest code point in a string and picks 1, 2 or 4 bytes per character for the whole string. Pure ASCII text uses 1 byte each, a string with a rupee sign uses 2, and one emoji pushes it to 4. That is why sys.getsizeof("a") is 42 but sys.getsizeof of the emoji chr(128512) is 64 on Python 3.14. Indexing stays O(1) because every character in one string has the same width.</p>')}
''', kw=['str vs bytes', 'bytearray', 'PEP 393', 'memory', 'sys.getsizeof'])

K.lesson('maths', 'The maths of strings', f'''
{fxs(fx('Number of substrings of a text of length n', 'n(n + 1) / 2', 'Pick a start and an end. "abc" has 6: a, b, c, ab, bc, abc.', key=True),
     fx('Number of subsequences (keep or drop each letter)', '2<sup>n</sup>', 'Including the empty one. "abc" has 8.'),
     fx('Number of different arrangements (anagrams)', 'n! / (c<sub>1</sub>! &middot; c<sub>2</sub>! &middot; ...)', 'c<sub>i</sub> is how often each letter repeats. "banana": 6! / (3! &middot; 2! &middot; 1!) = 60.', key=True),
     fx('Caesar shift of a lower case letter', 'new = (ord(ch) &minus; 97 + k) mod 26 + 97', 'mod 26 wraps z round to a.'),
     fx('Polynomial hash of a text (used in Rabin Karp search)', 'h = (c<sub>0</sub>&middot;b<sup>n&minus;1</sup> + c<sub>1</sub>&middot;b<sup>n&minus;2</sup> + ... + c<sub>n&minus;1</sub>) mod m', 'Lets a program compare a window of text with a pattern in O(1) by sliding the hash one letter at a time.'))}
{steps('Worked example: how many slices s[a:b] with a &lt; b does "PYTHON" have?', [
    'n = 6. A slice is fixed by a start a and an end b with 0 &le; a &lt; b &le; 6.',
    'That is choosing 2 different numbers from the 7 numbers 0 to 6.',
    eq('C(7, 2) = 7 &times; 6 / 2 = 21'),
    'This equals n(n + 1)/2 = 6 &times; 7 / 2 = 21, the number of substrings by position.'])}
''', kw=['substrings', 'subsequences', 'anagrams', 'permutations', 'Caesar cipher', 'rolling hash', 'Rabin Karp'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>A string is text in quotes. You can read one character with s[i], cut a part with s[a:b] and join strings with +.</p>',
    '<p>Strings are immutable, so methods return new strings. Use strip, split, join, replace, find and the is tests. Compare with ==, and know that comparison goes by code point.</p>',
    '<p>A str is a sequence of Unicode code points. encode and decode move between text and bytes. Build large text with join, not +=. Use casefold() for case blind matching and say encoding="utf-8" for files.</p>',
    '<p>CPython stores each string with a fixed width of 1, 2 or 4 bytes per character (PEP 393), caches its hash, and interns many identifiers. Real text processing must also think about Unicode normalisation (unicodedata.normalize, because "é" can be one or two code points) and grapheme clusters that look like one letter but are several code points.</p>')}
{grow('Make strings, index and slice them, and use upper, lower, strip and len.',
      'Use split, join, find, replace and the is tests, loop over characters and compare strings correctly.',
      'Explain code points, UTF-8 and the cost of +=, use slicing with negative steps without thinking, and handle text from any language.')}
''', kw=['beginner', 'expert', 'normalisation', 'grapheme', 'unicodedata'])

lc(344, 'Reverse String', 'reverse-string', 'e', 'Two pointers', 'The input is a list of characters. Swap the first and last, then move both ends inward.', r'''
def reverse_string(s):
    left = 0
    right = len(s) - 1
    while left < right:
        s[left], s[right] = s[right], s[left]
        left = left + 1
        right = right - 1
    return s
''', [('reverse_string(list("hello"))', list('olleh')), ('reverse_string(list("Hannah"))', list('hannaH'))])
lc(125, 'Valid Palindrome', 'valid-palindrome', 'e', 'Clean then compare', 'Keep only letters and digits in lower case, then compare the text with its reverse.', r'''
def is_palindrome(s):
    clean = ""
    for ch in s:
        if ch.isalnum():
            clean = clean + ch.lower()
    return clean == clean[::-1]
''', [('is_palindrome("A man, a plan, a canal: Panama")', True), ('is_palindrome("race a car")', False), ('is_palindrome(" ")', True)])
lc(58, 'Length of Last Word', 'length-of-last-word', 'e', 'split', 'split() with no argument ignores extra spaces. Take the last word.', r'''
def length_of_last_word(s):
    words = s.split()
    return len(words[-1])
''', [('length_of_last_word("Hello World")', 5), ('length_of_last_word("   fly me   to   the moon  ")', 4)])
lc(1768, 'Merge Strings Alternately', 'merge-strings-alternately', 'e', 'Index loop over the longer length', 'Loop i up to the longer length and add word1[i] and word2[i] when they exist.', r'''
def merge_alternately(word1, word2):
    result = []
    longest = max(len(word1), len(word2))
    for i in range(longest):
        if i < len(word1):
            result.append(word1[i])
        if i < len(word2):
            result.append(word2[i])
    return "".join(result)
''', [('merge_alternately("abc", "pqr")', 'apbqcr'), ('merge_alternately("ab", "pqrs")', 'apbqrs')])
lc(14, 'Longest Common Prefix', 'longest-common-prefix', 'e', 'Compare column by column', 'Take the first word. For each position, check that every other word has the same character there.', r'''
def longest_common_prefix(strs):
    first = strs[0]
    for i in range(len(first)):
        for word in strs[1:]:
            if i >= len(word) or word[i] != first[i]:
                return first[:i]
    return first
''', [('longest_common_prefix(["flower", "flow", "flight"])', 'fl'), ('longest_common_prefix(["dog", "racecar", "car"])', ''), ('longest_common_prefix(["a"])', 'a')])
lc(28, 'Find the Index of the First Occurrence in a String', 'find-the-index-of-the-first-occurrence-in-a-string', 'e', 'Sliding window of slices', 'Try every start i and compare haystack[i:i + len(needle)] with needle. str.find does this for you.', r'''
def str_str(haystack, needle):
    size = len(needle)
    for i in range(len(haystack) - size + 1):
        if haystack[i:i + size] == needle:
            return i
    return -1
''', [('str_str("sadbutsad", "sad")', 0), ('str_str("leetcode", "leeto")', -1), ('str_str("hello", "ll")', 2)])
lc(13, 'Roman to Integer', 'roman-to-integer', 'e', 'Look ahead one character', 'Add each value, but subtract it when the next symbol is bigger (IV, IX, XL).', r'''
def roman_to_int(s):
    value = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
    total = 0
    for i in range(len(s)):
        if i + 1 < len(s) and value[s[i]] < value[s[i + 1]]:
            total = total - value[s[i]]
        else:
            total = total + value[s[i]]
    return total
''', [('roman_to_int("III")', 3), ('roman_to_int("LVIII")', 58), ('roman_to_int("MCMXCIV")', 1994)])
lc(151, 'Reverse Words in a String', 'reverse-words-in-a-string', 'm', 'split and join', 'split() removes the extra spaces. Reverse the list of words and join with one space.', r'''
def reverse_words(s):
    words = s.split()
    words.reverse()
    return " ".join(words)
''', [('reverse_words("the sky is blue")', 'blue is sky the'), ('reverse_words("  hello world  ")', 'world hello'), ('reverse_words("a good   example")', 'example good a')])
lc(6, 'Zigzag Conversion', 'zigzag-conversion', 'm', 'Simulate rows', 'Keep one string per row. Walk down and up the rows, adding each character to the current row.', r'''
def convert(s, num_rows):
    if num_rows == 1 or num_rows >= len(s):
        return s
    rows = [""] * num_rows
    row = 0
    step = 1
    for ch in s:
        rows[row] = rows[row] + ch
        if row == 0:
            step = 1
        elif row == num_rows - 1:
            step = -1
        row = row + step
    return "".join(rows)
''', [('convert("PAYPALISHIRING", 3)', 'PAHNAPLSIIGYIR'), ('convert("PAYPALISHIRING", 4)', 'PINALSIGYAHRPI'), ('convert("A", 1)', 'A')])
lc(5, 'Longest Palindromic Substring', 'longest-palindromic-substring', 'm', 'Expand around the centre', 'Every palindrome has a centre: a letter or the gap between two letters. Grow outwards from each of the 2n &minus; 1 centres.', r'''
def longest_palindrome(s):
    best = ""
    for centre in range(len(s)):
        for left, right in [(centre, centre), (centre, centre + 1)]:
            while left >= 0 and right < len(s) and s[left] == s[right]:
                left = left - 1
                right = right + 1
            part = s[left + 1:right]
            if len(part) > len(best):
                best = part
    return best
''', [('longest_palindrome("babad") in ("bab", "aba")', True), ('longest_palindrome("cbbd")', 'bb'), ('longest_palindrome("forgeeksskeegfor")', 'geeksskeeg')])

K.lesson('leetcode', 'LeetCode practice', leet(), kw=['LeetCode', 'reverse string', 'valid palindrome', 'longest common prefix', 'roman to integer', 'zigzag', 'longest palindromic substring'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'A <b>str</b> is an ordered, immutable sequence of Unicode characters, written in single, double or triple quotes.',
    'A backslash starts an escape such as new line or tab. A raw string r"..." keeps backslashes.',
    '<b>Indexing</b> s[i] counts from 0 on the left and from &minus;1 on the right. <b>Slicing</b> s[a:b:c] includes a, excludes b, and never fails.',
    'Strings cannot change. Methods such as upper, strip and replace return a new string.',
    '+ joins, * repeats, in searches, and &lt; compares by code point, so "Z" &lt; "a" and "10" &lt; "9".',
    'split cuts text into a list and "sep".join(list) glues it back. join is the fast way to build big text.',
    'ord and chr move between characters and code points. encode and decode move between str and UTF-8 bytes.'],
    'Core 3.2 moves to lists: a sequence you can change, with append, sort, slicing, copying and how CPython grows a list.')}
{files('Three tasks: a palindrome sentence check, a run length text compressor and a word capitaliser without title().')}
''', kw=['summary', 'recap'])

K.quiz('e', 'What is "PYTHON"[1]?', ['"P"', '"Y"', '"T"', 'An error'], 1, 'Indexes start at 0.', 'Index 0 is P, index 1 is Y.')
K.quiz('e', 'What is "PYTHON"[-1]?', ['"P"', '"N"', '"O"', 'An error'], 1, 'From the right.', '&minus;1 is the last character.')
K.quiz('e', 'What does len("hi there") give?', ['7', '8', '2', '6'], 1, 'Count the space too.', 'h, i, space, t, h, e, r, e: 8.')
K.quiz('e', 'What does "ab" * 3 give?', ['"ab3"', '"ababab"', '"aaabbb"', 'TypeError'], 1, 'Repeat.', '* repeats the whole string.')
K.quiz('m', 'What does "hello"[1:4] give?', ['"hel"', '"ell"', '"ello"', '"hell"'], 1, 'Start included, stop excluded.', 'Indexes 1, 2, 3: e, l, l.')
K.quiz('m', 'What happens with s = "cat" then s[0] = "b"?', ['s becomes "bat"', 'TypeError', 'IndexError', 'Nothing'], 1, 'Strings are immutable.', "'str' object does not support item assignment.")
K.quiz('m', 'What is "banana".find("n")?', ['1', '2', '3', '&minus;1'], 1, 'First match.', 'b0 a1 n2: the first n is at 2.')
K.quiz('m', 'Which is True?', ['"apple" &lt; "Apple"', '"Zoo" &lt; "ant"', '"9" &lt; "10"', '"b" &lt; "a"'], 1, 'Upper case comes first.', 'ord("Z") = 90 is less than ord("a") = 97.')
K.quiz('m', 'What is "a,b,,c".split(",")?', ['["a", "b", "c"]', '["a", "b", "", "c"]', '["a,b,,c"]', '["a", "b", ",", "c"]'], 1, 'Two commas in a row.', 'An empty string sits between the two commas.')
K.quiz('h', 'What is len("₹".encode("utf-8"))?', ['1', '2', '3', '4'], 2, 'U+20B9 is above 2,047.', 'Code points from 2,048 to 65,535 need 3 bytes.')
K.quiz('h', 'What is "abcdef"[::-2]?', ['"fdb"', '"eca"', '"ace"', '"fedcba"'], 0, 'Start at the end, step back 2.', 'f (5), d (3), b (1).')
K.quiz('x', 'In the style of an MIT 6.100L exam: what is "abcdef"[-2:1:-1]?', ['"edc"', '"edcb"', '"ba"', '""'], 0, '&minus;2 is index 4. Stop 1 is not included.', 'Indexes 4, 3, 2 give e, d, c.')
K.quiz('x', 'In the style of a Stanford CS106A exam: s = "x" then for i in range(3): s = s + s. What is len(s)?', ['3', '6', '8', '4'], 2, 'Length doubles each turn.', '1, 2, 4, 8.')

K.calc('e', 'len("PYTHON"[2:5])?', '3', 'b &minus; a.', ['a = 2, b = 5.', '5 &minus; 2.', eq('3')], check=len("PYTHON"[2:5]))
K.calc('e', 'ord("a") &minus; ord("A")?', '32', '97 &minus; 65.', ['ord("a") = 97.', 'ord("A") = 65.', eq('32')], check=ord('a') - ord('A'))
K.calc('e', 'len("ha" * 5)?', '10', '2 &times; 5.', ['"ha" has 2 characters.', 'Repeated 5 times.', eq('10')], check=len('ha' * 5))
K.calc('m', 'How many substrings does a text of 10 characters have (by position)?', '55', 'n(n + 1)/2.', ['n = 10.', '10 &times; 11 / 2.', eq('55')], check=10 * 11 // 2)
K.calc('m', 'How many different arrangements of the letters of "banana"?', '60', '6! / (3! 2! 1!).', ['6! = 720.', '3! &times; 2! &times; 1! = 12.', eq('720 / 12 = 60')], check=720 // 12)
K.calc('m', 'UTF-8 byte length of "café"?', '5', 'é takes 2 bytes.', ['c, a, f: 1 byte each.', 'é (233) is in 128 to 2,047: 2 bytes.', eq('3 + 2 = 5')], check=len('café'.encode('utf-8')))
K.calc('m', 'Caesar shift 3 of "z": what is the code point of the result?', '99', '(25 + 3) mod 26 = 2.', ['ord("z") &minus; 97 = 25.', '(25 + 3) mod 26 = 2.', eq('2 + 97 = 99, which is "c"')], check=(ord('z') - 97 + 3) % 26 + 97)
K.calc('h', 'How many subsequences (including empty) does "python" have?', '64', '2<sup>n</sup>.', ['Each of 6 letters is kept or dropped.', '2<sup>6</sup>.', eq('64')], check=2 ** 6)
K.calc('h', 'len((chr(128512) + " ok").encode("utf-8"))? chr(128512) is a smiling face emoji.', '7', 'Emoji is 4 bytes.', ['128,512 is above 65,535: 4 bytes.', 'Space, o, k: 3 bytes.', eq('4 + 3 = 7')], check=len((chr(128512) + ' ok').encode('utf-8')))
K.calc('x', 'In the style of a Cambridge Tripos question: how many different strings can you make by rearranging all the letters of "MISSISSIPPI"?', '34650', '11! / (4! 4! 2! 1!).', ['M once, I four times, S four times, P twice.', '11! = 39,916,800.', '4! &times; 4! &times; 2! = 1,152.', eq('39,916,800 / 1,152 = 34,650')], check=39916800 // (24 * 24 * 2))

K.assign('palsent', 'e', 'Palindrome sentence',
         '<p>Write <code>is_pal_sentence(text)</code> that returns True when the letters of text, read in lower case and ignoring every space and symbol, are the same forwards and backwards.</p>',
         '''
def is_pal_sentence(text):
    # your code here
    pass
''', [('is_pal_sentence("Never odd or even")', True), ('is_pal_sentence("Hello")', False), ('is_pal_sentence("Was it a car or a cat I saw?")', True)],
         '''
def is_pal_sentence(text):
    letters = ""
    for ch in text:
        if ch.isalpha():
            letters = letters + ch.lower()
    return letters == letters[::-1]
''', 'Keep only the characters where ch.isalpha() is True, in lower case. Then compare with [::-1].', '<p>This is LeetCode 125 with letters only. Cleaning the text first and then using one simple test is a common pattern.</p>')
K.assign('rle', 'm', 'Run length compression',
         '<p>Write <code>compress(text)</code> that replaces each run of the same character with the character and the run length. "aaabcc" becomes "a3b1c2". An empty text gives "".</p>',
         '''
def compress(text):
    # your code here
    pass
''', [('compress("aaabcc")', 'a3b1c2'), ('compress("")', ''), ('compress("abc")', 'a1b1c1'), ('compress("zzzzzzzzzzzz")', 'z12')],
         '''
def compress(text):
    if text == "":
        return ""
    parts = []
    current = text[0]
    count = 1
    for ch in text[1:]:
        if ch == current:
            count = count + 1
        else:
            parts.append(current + str(count))
            current = ch
            count = 1
    parts.append(current + str(count))
    return "".join(parts)
''', 'Keep the current character and its count. When the character changes, save the pair and start again. Do not forget the last run.', '<p>Run length encoding is used in fax machines and simple image formats. The "do not forget the last run" step catches many people.</p>')
K.assign('caps', 'm', 'Capitalise every word',
         '<p>Write <code>cap_words(text)</code> that makes the first letter of every word upper case and the rest lower case, keeping single spaces between words. Do not use title().</p>',
         '''
def cap_words(text):
    # your code here
    pass
''', [('cap_words("hello wORLD")', 'Hello World'), ('cap_words("python")', 'Python'), ('cap_words("a b c")', 'A B C')],
         '''
def cap_words(text):
    result = []
    for word in text.split():
        result.append(word[0].upper() + word[1:].lower())
    return " ".join(result)
''', 'split() into words, fix each word with word[0].upper() + word[1:].lower(), then " ".join().', "<p>title() treats an apostrophe as a word break, so \"it's\".title() gives \"It'S\". Writing it yourself avoids that.</p>")

K.must('Making strings', 'Quotes: single, double or triple. Escapes start with a backslash. r"..." is a raw string. len() counts characters.')
K.must('Index and slice', 's[0] first, s[-1] last. s[a:b:c] includes a, excludes b. s[::-1] reverses. Slices never raise IndexError.')
K.must('Immutable', 'You cannot change a character. Methods return new strings: write s = s.upper().')
K.must('Key methods', 'strip, split, join, replace, find (-1) vs index (ValueError), count, startswith, isdigit, isalpha, upper, lower.')
K.must('Unicode', 'ord("A") = 65, chr(97) = "a". UTF-8 uses 1 to 4 bytes per character. Compare strings by code point.')

T = K.topic(
    slug='py-strings', topic='py-strings', step=(3, 'Data collections', 'py-c3', 'Store and work with many values: strings, lists, tuples, sets and dictionaries.', 'Beginner'),
    title='Strings: text, slicing, methods and Unicode', short='Strings', badge='3.1', minutes=60,
    lead='Work with text the way real programs do. Make strings, use escape characters, index and slice them, learn why they never change, use the most important methods, split and join text, and see how Unicode and UTF-8 store every language.',
    desc='string literals, quotes, multi line strings, escape sequences, raw strings, indexing, negative indexes, slicing with start stop step, immutability, concatenation, repetition, in, comparing strings by code point, ord and chr, string methods, split and join, loops over text, Caesar cipher, Unicode, code points, UTF-8, encode and decode, str vs bytes, PEP 393 and string counting maths.',
    summary='str, quotes, escapes, indexing, slicing, immutability, methods, split and join, Unicode, UTF-8, string maths.',
    keywords=['strings', 'str', 'slicing', 'indexing', 'string methods', 'split', 'join', 'Unicode', 'UTF-8', 'ord', 'chr', 'immutable', 'PCEP', 'PCAP'],
    recap='<p>A string is an immutable sequence of Unicode characters. Index and slice it, use its methods to clean, search and split it, and encode it to bytes only at the edges.</p>',
    added='2026-11-07', leet=leet_items())
