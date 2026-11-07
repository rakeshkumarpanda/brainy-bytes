# Advanced Python 6.2: data formats. Checked against the Python 3.14 documentation of csv (DictReader, DictWriter,
# dialects, Sniffer, newline=""), json (dumps, loads, default, object_hook, JSONDecodeError), xml.etree.ElementTree
# (fromstring, find, findall, iter, the XPath subset, SubElement, indent, the XML vulnerabilities note),
# configparser, tomllib (read only, Python 3.11+) and pickle (with its security warning).
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, lc, leet, files, grow, leet_items, show, term

chapter('py-formats')
K = Kit()

K.code('csv_files', r'''
import csv
import io
import os
import tempfile

path = os.path.join(tempfile.mkdtemp(), "people.csv")
rows = [
    {"name": "Ann", "city": "Paris", "age": 31},
    {"name": "Smith, Bo", "city": "Rome", "age": 25},
]
with open(path, "w", newline="", encoding="utf-8") as f:   # newline="" is required for csv
    writer = csv.DictWriter(f, fieldnames=["name", "city", "age"])
    writer.writeheader()
    writer.writerows(rows)

with open(path, newline="", encoding="utf-8") as f:
    print(repr(f.read()))                      # the real text in the file

with open(path, newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        print(row["name"], int(row["age"]) + 1)    # every value comes back as a string

text = "id;price\n1;2,50\n2;3,10\n"           # European style: ; between fields, comma decimals
for row in csv.reader(io.StringIO(text), delimiter=";"):
    print(row)
print(csv.Sniffer().sniff(text).delimiter)
''')

K.code('json_data', r'''
import json
from datetime import date

order = {"id": 7, "paid": True, "items": ("tea", "cake"), "note": None, 2: "two"}
text = json.dumps(order)
print(text)
back = json.loads(text)
print(back, back == order)
print(json.dumps({"b": 1, "a": [1, 2]}, indent=2, sort_keys=True))
print(json.dumps({"city": "Zürich"}), json.dumps({"city": "Zürich"}, ensure_ascii=False))


def to_json(value):
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, set):
        return sorted(value)
    raise TypeError(f"cannot turn {type(value).__name__} into JSON")


print(json.dumps({"day": date(2026, 11, 7), "tags": {"b", "a"}}, default=to_json))


def from_json(d):
    if "day" in d:
        d["day"] = date.fromisoformat(d["day"])
    return d


print(json.loads('{"day": "2026-11-07"}', object_hook=from_json))

try:
    json.loads("{'single': 'quotes'}")
except json.JSONDecodeError as err:
    print("JSONDecodeError:", err.msg, "at position", err.pos)
''')

K.code('xml_data', r'''
import xml.etree.ElementTree as ET

text = """<library>
  <book id="1" lang="en"><title>Python Basics</title><price>20.5</price></book>
  <book id="2" lang="de"><title>Datenbanken</title><price>31</price></book>
</library>"""

root = ET.fromstring(text)
print(root.tag, len(root))
for book in root.findall("book"):
    print(book.get("id"), book.find("title").text, float(book.findtext("price")))
print([t.text for t in root.iter("title")])
print(root.find(".//book[@lang='de']/title").text)    # a small part of XPath

new = ET.SubElement(root, "book", id="3", lang="en")
ET.SubElement(new, "title").text = "Regex & More"
ET.SubElement(new, "price").text = "15"
root.find("book").set("lang", "fr")
print(ET.tostring(new, encoding="unicode"))           # & is written as &amp; for us
ET.indent(root)
print(ET.tostring(root, encoding="unicode").splitlines()[1])
''')

K.code('config_files', r'''
import configparser
import tomllib

ini = """
[DEFAULT]
debug = no

[server]
host = example.com
port = 8080

[paths]
base = /srv/app
logs = %(base)s/logs
"""
config = configparser.ConfigParser()
config.read_string(ini)
print(config.sections())
print(config["server"]["host"], config.getint("server", "port"), config.getboolean("server", "debug"))
print(config.get("paths", "logs"))                    # %(base)s is filled in
print(config.get("server", "timeout", fallback="30"))

toml = """
title = "Shop"

[database]
ports = [5432, 5433]
enabled = true
"""
data = tomllib.loads(toml)
print(data["title"], data["database"]["ports"], type(data["database"]["enabled"]).__name__)
''')

K.code('pickle_data', r'''
import pickle


class Player:
    def __init__(self, name, scores):
        self.name = name
        self.scores = scores


p = Player("Ann", {3, 1})
data = pickle.dumps(p)                         # bytes in Python's own format
print(type(data).__name__, data[:2])
copy = pickle.loads(data)
print(copy.name, sorted(copy.scores), copy is p)


class Evil:
    def __reduce__(self):
        return (print, ("this ran while loading!",))


pickle.loads(pickle.dumps(Evil()))             # loading runs code chosen by whoever made the data
''')

K.lesson('idea', 'Data formats: saving and sharing data', f'''
{src('Python 3.14 documentation of csv, json, xml.etree.ElementTree, configparser, tomllib and pickle.')}
{wwh('A <b>data format</b> is an agreed way to write data as text or bytes, so that another program (or the same one tomorrow) can read it back. Python\'s standard library reads and writes the common ones: <b>CSV</b> for tables, <b>JSON</b> for nested data, <b>XML</b> for documents with tags, <b>INI</b> and <b>TOML</b> for settings, and <b>pickle</b> for Python objects.',
     'Objects live only while the program runs. To save them, send them over the network or share them with a spreadsheet, a web browser or a program in another language, they must become text or bytes in a format the other side understands.',
     'Each module turns Python objects into text (writing, also called <b>serializing</b> or dumping) and text back into objects (reading, <b>parsing</b> or loading). The conversion is not always perfect, as the animation shows: types can change on the way.')}
{viz('pyformat')}
{versus('Choosing a format', ['', 'CSV', 'JSON', 'XML', 'TOML / INI', 'pickle'], [
    ['Shape', 'Flat table', 'Nested lists and dicts', 'Nested tags with attributes', 'Settings in sections', 'Any Python object'],
    ['Types kept', 'None, all strings', 'str, numbers, bool, null, list, dict', 'All strings', 'TOML: numbers, bools, dates, lists', 'All of them'],
    ['Read by people', 'Yes, and spreadsheets', 'Yes', 'Yes, wordy', 'Yes, made for it', 'No (bytes)'],
    ['Other languages', 'Every one', 'Every one', 'Every one', 'Many', 'Python only'],
    ['Safe with untrusted data', 'Yes', 'Yes', 'With care (defusedxml)', 'Yes', 'NO: loading can run code'],
    ['Typical use', 'Exports, reports, data science', 'Web APIs, settings, logs', 'Documents, older APIs, office files', 'pyproject.toml, app config', 'Caches inside one trusted program']],
    'JSON for most data exchange, CSV for tables, TOML for configuration, XML when a system requires it, and pickle only for your own trusted data.')}
''', kw=['data format', 'serialization', 'parsing', 'CSV', 'JSON', 'XML', 'TOML', 'INI', 'pickle', 'choosing a format'])

K.lesson('csv', 'CSV: tables as text', f'''
{run('csv_files')}
{note('Always open CSV files with newline="". The csv module handles line endings itself (rows end with &#92;r&#92;n by default), and quotes inside values. Without newline="" you can get blank lines between rows on Windows.', 'exam')}
{table(['csv tool', 'Does'], [
    ['csv.reader(f), csv.writer(f)', 'Rows as lists'],
    ['csv.DictReader(f), csv.DictWriter(f, fieldnames)', 'Rows as dicts keyed by the header'],
    ['<code>delimiter=";", quotechar=\'"\'</code>', 'Other separators and quote characters'],
    ['quoting=csv.QUOTE_ALL, QUOTE_MINIMAL, QUOTE_NONNUMERIC', 'When values get quotes'],
    ['csv.Sniffer().sniff(sample)', 'Guess the separator of an unknown file']])}
''', kw=['csv', 'DictReader', 'DictWriter', 'newline', 'delimiter', 'quoting', 'Sniffer', 'dialect'])

K.lesson('json', 'JSON: nested data for the web', f'''
{run('json_data')}
{table(['Python', 'JSON', 'Back to Python'], [
    ['dict', 'object {...}', 'dict (keys always str)'], ['list, tuple', 'array [...]', 'list'],
    ['str', 'string "..."', 'str'], ['int, float', 'number', 'int or float'],
    ['True, False', 'true, false', 'True, False'], ['None', 'null', 'None'],
    ['set, date, Decimal, your classes', 'TypeError unless default= handles them', '']])}
{note('dump and load work with files, dumps and loads (s for string) with strings. indent=2 makes it readable, sort_keys=True makes the output stable for tests and diffs, and ensure_ascii=False keeps letters like ü instead of &#92;u00fc.', 'tip')}
''', kw=['json', 'dumps', 'loads', 'dump', 'load', 'indent', 'sort_keys', 'ensure_ascii', 'default', 'object_hook', 'JSONDecodeError'])

K.lesson('xml', 'XML with ElementTree', f'''
{run('xml_data')}
{table(['ElementTree', 'Does'], [
    ['ET.parse(path), ET.fromstring(text)', 'Read a file or a string into a tree'],
    ['el.tag, el.attrib, el.get(name), el.text', 'The tag name, attributes and text of an element'],
    ['el.find(path), el.findall(path), el.findtext(path)', 'Children by a simple path, such as "book/title"'],
    ['el.iter(tag)', 'Every element with that tag, at any depth'],
    ['.//book[@lang="de"]', 'The XPath subset: any depth, attribute tests, positions'],
    ['ET.SubElement, el.set, ET.indent, ET.tostring, tree.write', 'Build, change and write XML']])}
{note('Never parse XML from strangers with the standard library alone: specially made files can use huge amounts of memory (the "billion laughs" attack). Use the defusedxml package for untrusted XML.', 'warn')}
''', kw=['xml', 'ElementTree', 'fromstring', 'find', 'findall', 'iter', 'XPath', 'SubElement', 'attributes', 'defusedxml'])

K.lesson('config', 'Settings: INI and TOML', f'''
{run('config_files')}
{versus('Settings files', ['', 'INI (configparser)', 'TOML (tomllib)', 'JSON', 'Environment variables'], [
    ['Types', 'Strings, with getint, getboolean', 'Real numbers, bools, dates, lists, tables', 'Numbers, bools, lists, dicts', 'Strings'],
    ['Comments', 'Yes', 'Yes', 'No', 'No'],
    ['Write with the standard library', 'Yes', 'No, read only (tomli-w writes)', 'Yes', 'os.environ'],
    ['Typical use', 'Older tools, setup.cfg', 'pyproject.toml, new apps', 'Web app settings', 'Secrets and per server values (12 factor apps)']],
    'TOML for new configuration files, environment variables for secrets such as passwords and API keys.')}
''', kw=['configparser', 'INI', 'sections', 'getint', 'getboolean', 'fallback', 'interpolation', 'tomllib', 'TOML', 'pyproject.toml', 'environment variables'])

K.lesson('pickle', 'pickle: Python objects as bytes', f'''
{run('pickle_data')}
{note('pickle can save almost any Python object, but pickle.loads can run any code the creator of the data chose, as the Evil class shows with a harmless print. Never unpickle data from the internet, uploads or anyone you do not fully trust. Use JSON for data you exchange.', 'warn')}
{deep('Other binary formats', '<p>For big tables, columnar formats such as Parquet (with pandas or pyarrow) are much smaller and faster than CSV. For messages between services, Protocol Buffers or MessagePack are compact and typed. The struct module packs numbers into exact byte layouts for files and network protocols.</p>')}
''', kw=['pickle', 'dumps', 'loads', 'protocol', '__reduce__', 'security', 'untrusted data', 'Parquet', 'MessagePack', 'struct'])

K.lesson('maths', 'The maths: sizes and overheads', f'''
{fxs(fx('CSV file size', 'bytes &asymp; rows &times; (sum of value lengths + separators + 2 for &#92;r&#92;n)', '1000 rows of 3 values of 6 characters: 1000 &times; (18 + 2 + 2) = 22,000 bytes.', key=True),
     fx('JSON overhead for a list of dicts', 'every row repeats every key with quotes, a colon and a comma', 'Keys "name", "city", "age" add about 25 bytes to each row, often more than the data itself.'),
     fx('Base64 for binary data in JSON or XML', 'size out = 4 &times; &lceil;n / 3&rceil;', 'A 300 KB image becomes 400 KB of text.', key=True),
     fx('Unicode escapes', 'ensure_ascii=True writes a non ASCII letter as 6 characters', '"Zürich" grows from 7 bytes (UTF-8) to 11 characters with &#92;u00fc.'),
     fx('Sniffing a separator', 'pick the character that appears the same number of times on every line', '<code>"id;price"</code> and <code>"1;2,50"</code>: the <code>;</code> appears once on each line, the comma does not.'))}
{steps('Worked example: CSV or JSON for 10,000 orders with id, city and total?', [
    'A CSV row like "1042,Paris,29.90&#92;r&#92;n" is 16 characters plus 2 line ending bytes, so 18 bytes: 10,000 rows is about 180 KB.',
    'A JSON row like {"id": 1042, "city": "Paris", "total": 29.9}, is about 46 bytes: about 460 KB.',
    'The keys repeat in every JSON row, so JSON is about 2.5 times bigger here.',
    eq('CSV &asymp; 180 KB, JSON &asymp; 460 KB, but JSON keeps types and nesting')])}
''', kw=['file size', 'overhead', 'base64', 'unicode escape', 'csv vs json size'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>Read and write CSV with DictReader and DictWriter (newline=""), and JSON with dump, load, dumps and loads.</p>',
    '<p>Handle quoting and separators, write default= and object_hook for dates and sets, read XML with find, findall and iter, and settings with configparser and tomllib.</p>',
    '<p>Choose a format by shape, types, size and safety, avoid pickle and raw XML with untrusted data, and validate JSON with a schema (jsonschema, pydantic).</p>',
    '<p>Stream huge files (csv row by row, ET.iterparse, ijson), use columnar and binary formats (Parquet, Arrow, Protocol Buffers), and design versioned formats that stay readable for years.</p>')}
{grow('Save and load CSV and JSON.', 'Handle XML, settings and custom types.', 'Choose, validate and stream formats at scale.')}
''', kw=['beginner', 'expert', 'iterparse', 'jsonschema', 'pydantic', 'Parquet', 'streaming'])

lc(171, 'Excel Sheet Column Number', 'excel-sheet-column-number', 'e', 'Base 26 with letters', 'Spreadsheet columns count A to Z, then AA. Each letter is a digit from 1 to 26: result = result &times; 26 + value.', r'''
def title_to_number(column_title):
    result = 0
    for ch in column_title:
        result = result * 26 + (ord(ch) - ord("A") + 1)
    return result
''', [('title_to_number("A")', 1), ('title_to_number("AB")', 28), ('title_to_number("ZY")', 701)])
lc(168, 'Excel Sheet Column Title', 'excel-sheet-column-title', 'e', 'Base 26 the other way, with a shift', 'There is no zero digit, so subtract 1 before each divmod by 26.', r'''
def convert_to_title(column_number):
    title = ""
    while column_number > 0:
        column_number -= 1
        title = chr(ord("A") + column_number % 26) + title
        column_number //= 26
    return title
''', [('convert_to_title(1)', 'A'), ('convert_to_title(28)', 'AB'), ('convert_to_title(701)', 'ZY')])
lc(1507, 'Reformat Date', 'reformat-date', 'e', 'Split and look up the month', 'Split "20th Oct 2052" into three parts. Strip the two letter ending from the day, look the month up in a list, and pad with zfill(2).', r'''
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def reformat_date(date):
    day, month, year = date.split()
    day_number = day[:-2]
    month_number = MONTHS.index(month) + 1
    return f"{year}-{month_number:02d}-{int(day_number):02d}"
''', [('reformat_date("20th Oct 2052")', '2052-10-20'), ('reformat_date("6th Jun 1933")', '1933-06-06'), ('reformat_date("26th May 1960")', '1960-05-26')])
lc(2194, 'Cells in a Range on an Excel Sheet', 'cells-in-a-range-on-an-excel-sheet', 'e', 'Two nested loops over letters and rows', 'The range "K1:L2" gives column letters K to L and rows 1 to 2. Columns go in the outer loop.', r'''
def cells_in_range(s):
    first_col, first_row, last_col, last_row = s[0], int(s[1]), s[3], int(s[4])
    cells = []
    for col in range(ord(first_col), ord(last_col) + 1):
        for row in range(first_row, last_row + 1):
            cells.append(chr(col) + str(row))
    return cells
''', [('cells_in_range("K1:L2")', ['K1', 'K2', 'L1', 'L2']), ('cells_in_range("A1:F1")', ['A1', 'B1', 'C1', 'D1', 'E1', 'F1'])])
lc(1410, 'HTML Entity Parser', 'html-entity-parser', 'm', 'Replace the entities, the ampersand one last', 'Replace each named entity with its character. Do the ampersand entity last, or the text you just made could be read as a new entity.', r'''
ENTITIES = [("&quot;", '"'), ("&apos;", "'"), ("&gt;", ">"), ("&lt;", "<"), ("&frasl;", "/")]


def entity_parser(text):
    for entity, ch in ENTITIES:
        text = text.replace(entity, ch)
    return text.replace("&amp;", "&")
''', [('entity_parser("&amp; is an HTML entity but &ambassador; is not.")', '& is an HTML entity but &ambassador; is not.'), ('entity_parser("and I quote: &quot;...&quot;")', 'and I quote: "..."'), ('entity_parser("&amp;gt;")', '&gt;')])
lc(385, 'Mini Parser', 'mini-parser', 'm', 'A stack of lists while reading characters', 'LeetCode uses a NestedInteger class. Here plain ints and lists stand for it. Push a new list at [, finish a number at , or ], and pop at ].', r'''
def deserialize(s):
    if s[0] != "[":
        return int(s)
    stack = []
    number = ""
    result = None
    for ch in s:
        if ch == "[":
            stack.append([])
        elif ch in ",]":
            if number:
                stack[-1].append(int(number))
                number = ""
            if ch == "]":
                done = stack.pop()
                if stack:
                    stack[-1].append(done)
                else:
                    result = done
        else:
            number += ch
    return result
''', [('deserialize("324")', 324), ('deserialize("[123,[456,[789]]]")', [123, [456, [789]]]), ('deserialize("[-1,[],[2]]")', [-1, [], [2]])])
lc(831, 'Masking Personal Information', 'masking-personal-information', 'm', 'Two formats, two rules', 'An email keeps the first and last letter of the name and lower cases everything. A phone keeps only digits, shows the last 4, and stars for a country code.', r'''
def mask_pii(s):
    if "@" in s:
        name, domain = s.lower().split("@")
        return name[0] + "*****" + name[-1] + "@" + domain
    digits = [ch for ch in s if ch.isdigit()]
    local = "***-***-" + "".join(digits[-4:])
    country = len(digits) - 10
    return local if country == 0 else "+" + "*" * country + "-" + local
''', [('mask_pii("LeetCode@LeetCode.com")', 'l*****e@leetcode.com'), ('mask_pii("AB@qq.com")', 'a*****b@qq.com'), ('mask_pii("1(234)567-890")', '***-***-7890'), ('mask_pii("86-(10)12345678")', '+**-***-***-5678')])
lc(640, 'Solve the Equation', 'solve-the-equation', 'm', 'A regex for the terms on each side', 'The pattern [+-]?&#92;d*x|[+-]?&#92;d+ finds terms like +2x, -x or 5. Add up x coefficients and numbers on each side, then move everything to one side.', r'''
import re


def parse_side(side):
    x_total = 0
    number_total = 0
    for term in re.findall(r"[+-]?\d*x|[+-]?\d+", side):
        if term.endswith("x"):
            coefficient = term[:-1]
            if coefficient in ("", "+"):
                x_total += 1
            elif coefficient == "-":
                x_total -= 1
            else:
                x_total += int(coefficient)
        else:
            number_total += int(term)
    return x_total, number_total


def solve_equation(equation):
    left, right = equation.split("=")
    a, b = parse_side(left)
    c, d = parse_side(right)
    x_coefficient = a - c
    constant = d - b
    if x_coefficient == 0:
        return "Infinite solutions" if constant == 0 else "No solution"
    return f"x={constant // x_coefficient}"
''', [('solve_equation("x+5-3+x=6+x-2")', 'x=2'), ('solve_equation("x=x")', 'Infinite solutions'), ('solve_equation("2x=x")', 'x=0'), ('solve_equation("x=x+2")', 'No solution')])
lc(726, 'Number of Atoms', 'number-of-atoms', 'h', 'A stack of Counters', 'Read an atom name (capital letter and lower case letters) and its count. At ( push a new Counter, at ) multiply the top one by the number after it and add it to the one below.', r'''
from collections import Counter


def count_of_atoms(formula):
    stack = [Counter()]
    i = 0
    n = len(formula)

    def read_number(i):
        start = i
        while i < n and formula[i].isdigit():
            i += 1
        return (int(formula[start:i]) if i > start else 1), i

    while i < n:
        ch = formula[i]
        if ch == "(":
            stack.append(Counter())
            i += 1
        elif ch == ")":
            times, i = read_number(i + 1)
            inner = stack.pop()
            for atom, count in inner.items():
                stack[-1][atom] += count * times
        else:
            start = i
            i += 1
            while i < n and formula[i].islower():
                i += 1
            atom = formula[start:i]
            count, i = read_number(i)
            stack[-1][atom] += count
    counts = stack[0]
    return "".join(atom + (str(counts[atom]) if counts[atom] > 1 else "") for atom in sorted(counts))
''', [('count_of_atoms("H2O")', 'H2O'), ('count_of_atoms("Mg(OH)2")', 'H2MgO2'), ('count_of_atoms("K4(ON(SO3)2)2")', 'K4N2O14S4')])
lc(1096, 'Brace Expansion II', 'brace-expansion-ii', 'h', 'A recursive parser for union and product', 'A comma means union of sets, writing things next to each other means every combination (product). Parse with a function that reads until } and calls itself at {.', r'''
def brace_expansion_ii(expression):
    def parse(i):
        union = set()
        current = {""}
        while i < len(expression) and expression[i] != "}":
            ch = expression[i]
            if ch == ",":
                union |= current
                current = {""}
                i += 1
            elif ch == "{":
                inner, i = parse(i + 1)
                i += 1
                current = {a + b for a in current for b in inner}
            else:
                current = {a + ch for a in current}
                i += 1
        union |= current
        return union, i

    words, _ = parse(0)
    return sorted(words)
''', [('brace_expansion_ii("{a,b}{c,{d,e}}")', ['ac', 'ad', 'ae', 'bc', 'bd', 'be']), ('brace_expansion_ii("{{a,z},a{b,c},{ab,z}}")', ['a', 'ab', 'ac', 'z'])])

K.lesson('leetcode', 'LeetCode practice', leet('<p>These problems read and write small formats: spreadsheet column names and ranges, dates, HTML entities, a nested list parser that works like a tiny JSON reader, masking personal data before it is logged, equations, chemical formulas and brace patterns.</p>'), kw=['LeetCode', 'parsing', 'spreadsheet', 'dates', 'HTML entities', 'nested list', 'stack', 'recursive descent'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'CSV: csv.DictReader and DictWriter, open with newline="", values come back as strings, commas inside values get quotes.',
    'JSON: dumps and loads (strings), dump and load (files). Tuples become lists, keys become strings. default= and object_hook for other types.',
    'XML: ET.fromstring or parse, find, findall, iter and simple XPath. defusedxml for untrusted files.',
    'Settings: configparser for INI (getint, getboolean, fallback), tomllib to read TOML. Secrets in environment variables.',
    'pickle saves any object but loading can run code: only for trusted data.'],
    'Next: storing data in a real database with sqlite3 and SQL.')}
{files('Three tasks: add up a CSV by city, write JSON with dates and sets, and pick cheap books out of XML.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'Which module reads a spreadsheet exported as comma separated values?', ['json', 'csv', 'pickle', 'xml'], 1, 'Comma separated values.', 'csv.reader and csv.DictReader read such files.')
K.quiz('e', 'What does json.dumps(None) return?', ["'None'", "'null'", 'None', "''"], 1, 'JSON spelling.', 'None becomes null in JSON.')
K.quiz('e', 'What is the difference between json.dump and json.dumps?', ['None', 'dump writes to a file, dumps returns a string', 'dumps is faster', 'dump sorts the keys'], 1, 's for string.', 'The same is true for load and loads.')
K.quiz('m', 'What type is row["age"] when a CSV is read with DictReader?', ['int', 'float', 'str', 'It depends on the value'], 2, 'CSV has no types.', 'Convert with int() or float() yourself.')
K.quiz('m', 'json.loads(json.dumps({1: (2, 3)})) gives what?', ["{1: (2, 3)}", "{'1': [2, 3]}", "{1: [2, 3]}", 'An error'], 1, 'Two changes.', 'Keys become strings and tuples become lists.')
K.quiz('m', 'Why open CSV files with newline=""?', ['It is faster', 'So the csv module can handle line endings and quoted newlines itself', 'To skip the header', 'To use UTF-8'], 1, 'Line endings.', 'Otherwise extra blank lines can appear on Windows.')
K.quiz('m', 'How do you make json.dumps handle a datetime.date?', ['It does already', 'Pass default= a function that returns date.isoformat()', 'Use pickle inside JSON', 'Set ensure_ascii=False'], 1, 'A fallback function.', 'default is called for every object JSON does not know.')
K.quiz('m', 'Which ElementTree method finds elements with a tag at any depth?', ['find', 'findall("tag") on the root only', 'iter("tag")', 'get'], 2, 'Walk the whole tree.', 'find and findall without .// only look at direct children by default.')
K.quiz('h', 'Why is pickle.loads dangerous on data from the internet?', ['It is slow', 'Loading can call any function the data names, so it can run code', 'It loses types', 'It only works on Linux'], 1, '__reduce__.', 'Use JSON for data you exchange.')
K.quiz('h', 'Which can tomllib in the standard library do?', ['Read and write TOML', 'Only read TOML', 'Only write TOML', 'Neither'], 1, 'Read only.', 'Use the tomli-w package to write.')
K.quiz('h', 'What does configparser give for config.get("paths", "logs") when logs = %(base)s/logs and base = /srv/app?', ['%(base)s/logs', '/srv/app/logs', 'An error', 'base/logs'], 1, 'Interpolation.', 'BasicInterpolation fills in %(name)s from the same section or DEFAULT.')
K.quiz('x', 'In the style of a CMU 15-445 exam: why do analytics systems store tables in a columnar format such as Parquet rather than CSV?', ['Columnar files are easier to read by hand', 'Values of one column are stored together, so they compress well and a query reads only the columns it needs', 'CSV cannot store numbers', 'Parquet is text'], 1, 'Read less.', 'Scanning 2 of 50 columns reads about 4 % of the data, and similar values compress far better.')
K.quiz('x', 'In the style of a Stanford CS 255 exam: why is "billion laughs" a risk for naive XML parsers?', ['It breaks UTF-8', 'Nested entity definitions expand a small file into gigabytes in memory', 'XML cannot store numbers', 'It needs a network'], 1, 'Exponential expansion.', 'Ten levels of entities that each repeat the previous one ten times give 10<sup>10</sup> copies.')

K.calc('e', 'Excel column "AB" has which number?', '28', '26 &times; 1 + 2.', ['A = 1, B = 2.', '1 &times; 26 + 2.', eq('28')], check=28)
K.calc('e', 'A CSV has a header and 250 data rows. How many lines does it have?', '251', 'Header plus rows.', ['1 header line.', '250 rows.', eq('251')], check=251)
K.calc('e', 'How many characters is the JSON text of [1, 2, 3] written by json.dumps?', '9', 'Count brackets, digits, commas and spaces.', ['"[1, 2, 3]".', '[ 1 , space 2 , space 3 ].', eq('9')], check=len('[1, 2, 3]'))
K.calc('m', 'Base64 turns 300 bytes into how many characters?', '400', '4 &times; &lceil;n / 3&rceil;.', ['300 / 3 = 100.', '4 &times; 100.', eq('400')], check=4 * (300 // 3))
K.calc('m', '1000 CSV rows of 3 values of 6 characters, commas between, &#92;r&#92;n at the end. How many bytes?', '22000', 'Per row: 18 + 2 + 2.', ['18 characters of data.', '2 commas and 2 line ending bytes: 22 per row.', eq('22,000 bytes')], check=1000 * (18 + 2 + 2))
K.calc('m', 'Excel column "ZY" has which number?', '701', '26 &times; 26 + 25.', ['Z = 26, Y = 25.', '26 &times; 26 + 25.', eq('701')], check=26 * 26 + 25)
K.calc('m', 'With ensure_ascii=True, how many characters does json.dumps("Zürich") return, counting the quotes?', '13', 'ü becomes a 6 character escape.', ['Z, r, i, c, h: 5 characters.', 'The escape for ü: 6, plus 2 quotes.', eq('13')], check=len(__import__('json').dumps('Zürich')))
K.calc('h', 'A 1.2 MB image is put in JSON as base64. About how many MB is the text?', '1.6', '&times; 4 / 3.', ['1.2 &times; 4 = 4.8.', '4.8 / 3.', eq('1.6 MB')], check=round(1.2 * 4 / 3, 1))
K.calc('h', 'What is the column number of "AAA"?', '703', '26² + 26 + 1.', ['A = 1 in each place.', '676 + 26 + 1.', eq('703')], check=26 * 26 + 26 + 1)
K.calc('x', 'In the style of a Stanford CS 255 exam: 10 nested XML entities each repeat the one below 10 times, ending in a 3 byte string. How many GB does it expand to (10<sup>9</sup> bytes)?', '30', '3 &times; 10<sup>10</sup> bytes.', ['10<sup>10</sup> copies.', '&times; 3 bytes = 3 &times; 10<sup>10</sup>.', eq('30 GB')], check=3 * 10 ** 10 // 10 ** 9)

K.assign('citytotals', 'e', 'Add up a CSV by city',
         '<p>Write <code>total_by_city(csv_text)</code>. The text has a header line city,amount and one sale per line. Return a dict from city to the total amount as a float, in the order cities first appear. Read it with csv.DictReader(io.StringIO(csv_text)). Remember that every value is a string.</p>',
         '''
import csv
import io


def total_by_city(csv_text):
    totals = {}
    for row in csv.DictReader(io.StringIO(csv_text)):
        totals[row["city"]] = totals.get(row["city"], "") + row["amount"]
    return totals
''', [('total_by_city("city,amount\\nParis,10.5\\nRome,4\\nParis,2\\n")', {'Paris': 12.5, 'Rome': 4.0}), ('total_by_city("city,amount\\n")', {}), ('total_by_city(\'city,amount\\n"Washington, DC",3\\n\')', {'Washington, DC': 3.0})],
         '''
import csv
import io


def total_by_city(csv_text):
    totals = {}
    for row in csv.DictReader(io.StringIO(csv_text)):
        totals[row["city"]] = totals.get(row["city"], 0.0) + float(row["amount"])
    return totals
''', 'Start each total at 0.0 and add float(row["amount"]). The starter joins strings: "10.5" + "2" gives "10.52".', '<p>The quoted city "Washington, DC" stays one field because DictReader understands CSV quoting. Splitting lines on commas yourself would break it.</p>')
K.assign('jsondates', 'm', 'Write JSON with dates and sets',
         '<p>Write <code>dump_event(event)</code> that returns a JSON string of the dict event with sorted keys. Dates must become "YYYY-MM-DD" strings and sets sorted lists. Anything else that JSON does not support must still raise TypeError. Use json.dumps with default= and sort_keys=True.</p>',
         '''
import json
from datetime import date


def dump_event(event):
    return json.dumps(event, sort_keys=True)


def error_of(event):
    try:
        dump_event(event)
    except TypeError:
        return "TypeError"
    return "no error"
''', [('dump_event({"name": "launch", "day": date(2026, 11, 7)})', '{"day": "2026-11-07", "name": "launch"}'), ('dump_event({"tags": {"b", "a"}, "n": 1})', '{"n": 1, "tags": ["a", "b"]}'), ('dump_event({})', '{}'), ('error_of({"x": object()})', 'TypeError')],
         '''
import json
from datetime import date


def to_json(value):
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, set):
        return sorted(value)
    raise TypeError(f"{type(value).__name__} is not JSON serializable")


def dump_event(event):
    return json.dumps(event, default=to_json, sort_keys=True)


def error_of(event):
    try:
        dump_event(event)
    except TypeError:
        return "TypeError"
    return "no error"
''', 'default= gets each object json does not know. Return something it does know (a string, a list), or raise TypeError.', '<p>Web frameworks do this for you: Django REST framework and FastAPI turn dates, decimals and UUIDs into JSON with exactly this kind of default function.</p>')
K.assign('cheapbooks', 'h', 'Pick cheap books out of XML',
         '<p>Write <code>cheap_books(xml_text, limit)</code>. The XML has a root with book elements that each have a title and usually a price. Return the titles of books whose price is at most limit, sorted by price and then by title. Skip books without a price. If the text is not valid XML, raise ValueError (ElementTree raises ET.ParseError).</p>',
         '''
import xml.etree.ElementTree as ET


def cheap_books(xml_text, limit):
    root = ET.fromstring(xml_text)
    return [b.findtext("title") for b in root.iter("book")]


def error_of(xml_text):
    try:
        cheap_books(xml_text, 10)
    except ValueError:
        return "ValueError"
    except Exception as err:
        return type(err).__name__
    return "no error"


SHOP = """<shop>
  <book><title>B</title><price>9.5</price></book>
  <book><title>A</title><price>9.5</price></book>
  <book><title>C</title><price>30</price></book>
  <book><title>D</title></book>
  <book><title>E</title><price>4</price></book>
</shop>"""
''', [('cheap_books(SHOP, 10)', ['E', 'A', 'B']), ('cheap_books(SHOP, 1)', []), ('cheap_books(SHOP, 100)', ['E', 'A', 'B', 'C']), ('error_of("<shop><book>")', 'ValueError')],
         '''
import xml.etree.ElementTree as ET


def cheap_books(xml_text, limit):
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as err:
        raise ValueError(f"not valid XML: {err}") from err
    found = []
    for book in root.iter("book"):
        price = book.findtext("price")
        if price is None:
            continue
        if float(price) <= limit:
            found.append((float(price), book.findtext("title")))
    return [title for price, title in sorted(found)]


def error_of(xml_text):
    try:
        cheap_books(xml_text, 10)
    except ValueError:
        return "ValueError"
    except Exception as err:
        return type(err).__name__
    return "no error"


SHOP = """<shop>
  <book><title>B</title><price>9.5</price></book>
  <book><title>A</title><price>9.5</price></book>
  <book><title>C</title><price>30</price></book>
  <book><title>D</title></book>
  <book><title>E</title><price>4</price></book>
</shop>"""
''', 'findtext("price") gives None when there is no price. Sort (price, title) tuples so equal prices fall back to the title. Turn ET.ParseError into ValueError with raise ... from.', '<p>Raising your own ValueError hides which parser you used, so callers do not need to import ElementTree just to catch the error.</p>')

K.must('CSV', 'csv.DictReader, DictWriter(f, fieldnames), writeheader, open(..., newline=""), delimiter, quoting. Values are strings.')
K.must('JSON', 'dumps and loads, dump and load, indent, sort_keys, ensure_ascii, default=, object_hook, JSONDecodeError. Tuples become lists, keys strings.')
K.must('XML', 'ET.fromstring, ET.parse, find, findall, findtext, iter, .//tag[@attr="v"], SubElement, indent, tostring. defusedxml for untrusted XML.')
K.must('Settings', 'configparser: sections, getint, getboolean, fallback=, %(name)s. tomllib.load(binary file) and loads, read only.')
K.must('pickle', 'dumps and loads any object, Python only, NEVER load untrusted data (__reduce__ runs code).')

T = K.topic(
    slug='py-formats', topic='py-formats', step=(6, 'The standard library toolbox: text, data, databases and GUIs', 'py-a6', 'Find patterns in text, read and write data formats, store data in SQLite, and build desktop windows with tkinter.', 'Advanced'),
    title='CSV, JSON, XML and settings files', short='Data formats', badge='6.2', minutes=75,
    lead='Save data and share it with other programs. Learn CSV with DictReader and DictWriter, JSON with custom types, XML with ElementTree, settings with configparser and tomllib, and why pickle is only for trusted data.',
    desc='csv reader, writer, DictReader, DictWriter, newline, delimiter, quoting, Sniffer, json dumps, loads, indent, sort_keys, ensure_ascii, default, object_hook, JSONDecodeError, xml.etree.ElementTree fromstring, find, findall, iter, XPath subset, SubElement, indent, defusedxml, configparser sections and interpolation, tomllib, pickle and its security risk, choosing a format, sizes and overheads.',
    summary='CSV, JSON with custom types, XML with ElementTree, INI and TOML settings, pickle safety.',
    keywords=['csv', 'json', 'xml', 'ElementTree', 'configparser', 'toml', 'tomllib', 'pickle', 'serialization', 'data format'],
    recap='<p>CSV for tables, JSON for nested data, TOML for settings, XML when required, and pickle only for data you made yourself.</p>',
    added='2026-11-07', leet=leet_items())
