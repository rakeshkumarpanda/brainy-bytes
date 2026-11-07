# 6.2 CSV, JSON, XML and settings files
# LeetCode solutions for this chapter. Try each problem on leetcode.com before you read its answer.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>


# ------------------------------------------------------------------ the checker
# check(tests) runs each test and says PASS or FAIL. A test is a pair: the call to make and the answer we expect.
import json


def check(name, tests):
    passed = 0
    for call, expected in tests:
        try:
            got = eval(call)
        except Exception as error:
            got = "error: " + type(error).__name__ + ": " + str(error)
        if json.dumps(got, sort_keys=True, default=repr) == json.dumps(expected, sort_keys=True, default=repr):
            passed = passed + 1
            print("  PASS", call)
        else:
            print("  FAIL", call, "expected", repr(expected), "but got", repr(got))
    print(name + ":", passed, "of", len(tests), "tests pass")
    return passed == len(tests)


# ================================================================== 171. Excel Sheet Column Number (Easy)
# https://leetcode.com/problems/excel-sheet-column-number/
# Pattern: Base 26 with letters
# Idea: Spreadsheet columns count A to Z, then AA. Each letter is a digit from 1 to 26: result =
# result × 26 + value.

def title_to_number(column_title):
    result = 0
    for ch in column_title:
        result = result * 26 + (ord(ch) - ord("A") + 1)
    return result


# ================================================================== 168. Excel Sheet Column Title (Easy)
# https://leetcode.com/problems/excel-sheet-column-title/
# Pattern: Base 26 the other way, with a shift
# Idea: There is no zero digit, so subtract 1 before each divmod by 26.

def convert_to_title(column_number):
    title = ""
    while column_number > 0:
        column_number -= 1
        title = chr(ord("A") + column_number % 26) + title
        column_number //= 26
    return title


# ================================================================== 1507. Reformat Date (Easy)
# https://leetcode.com/problems/reformat-date/
# Pattern: Split and look up the month
# Idea: Split "20th Oct 2052" into three parts. Strip the two letter ending from the day, look the
# month up in a list, and pad with zfill(2).

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def reformat_date(date):
    day, month, year = date.split()
    day_number = day[:-2]
    month_number = MONTHS.index(month) + 1
    return f"{year}-{month_number:02d}-{int(day_number):02d}"


# ================================================================== 2194. Cells in a Range on an Excel Sheet (Easy)
# https://leetcode.com/problems/cells-in-a-range-on-an-excel-sheet/
# Pattern: Two nested loops over letters and rows
# Idea: The range "K1:L2" gives column letters K to L and rows 1 to 2. Columns go in the outer loop.

def cells_in_range(s):
    first_col, first_row, last_col, last_row = s[0], int(s[1]), s[3], int(s[4])
    cells = []
    for col in range(ord(first_col), ord(last_col) + 1):
        for row in range(first_row, last_row + 1):
            cells.append(chr(col) + str(row))
    return cells


# ================================================================== 1410. HTML Entity Parser (Medium)
# https://leetcode.com/problems/html-entity-parser/
# Pattern: Replace the entities, the ampersand one last
# Idea: Replace each named entity with its character. Do the ampersand entity last, or the text you
# just made could be read as a new entity.

ENTITIES = [("&quot;", '"'), ("&apos;", "'"), ("&gt;", ">"), ("&lt;", "<"), ("&frasl;", "/")]


def entity_parser(text):
    for entity, ch in ENTITIES:
        text = text.replace(entity, ch)
    return text.replace("&amp;", "&")


# ================================================================== 385. Mini Parser (Medium)
# https://leetcode.com/problems/mini-parser/
# Pattern: A stack of lists while reading characters
# Idea: LeetCode uses a NestedInteger class. Here plain ints and lists stand for it. Push a new list
# at [, finish a number at , or ], and pop at ].

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


# ================================================================== 831. Masking Personal Information (Medium)
# https://leetcode.com/problems/masking-personal-information/
# Pattern: Two formats, two rules
# Idea: An email keeps the first and last letter of the name and lower cases everything. A phone
# keeps only digits, shows the last 4, and stars for a country code.

def mask_pii(s):
    if "@" in s:
        name, domain = s.lower().split("@")
        return name[0] + "*****" + name[-1] + "@" + domain
    digits = [ch for ch in s if ch.isdigit()]
    local = "***-***-" + "".join(digits[-4:])
    country = len(digits) - 10
    return local if country == 0 else "+" + "*" * country + "-" + local


# ================================================================== 640. Solve the Equation (Medium)
# https://leetcode.com/problems/solve-the-equation/
# Pattern: A regex for the terms on each side
# Idea: The pattern [+-]?\d*x|[+-]?\d+ finds terms like +2x, -x or 5. Add up x coefficients and
# numbers on each side, then move everything to one side.

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


# ================================================================== 726. Number of Atoms (Hard)
# https://leetcode.com/problems/number-of-atoms/
# Pattern: A stack of Counters
# Idea: Read an atom name (capital letter and lower case letters) and its count. At ( push a new
# Counter, at ) multiply the top one by the number after it and add it to the one below.

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


# ================================================================== 1096. Brace Expansion II (Hard)
# https://leetcode.com/problems/brace-expansion-ii/
# Pattern: A recursive parser for union and product
# Idea: A comma means union of sets, writing things next to each other means every combination
# (product). Parse with a function that reads until } and calls itself at {.

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


if __name__ == "__main__":
    results = []
    results.append(check("171. Excel Sheet Column Number", [('title_to_number("A")', 1), ('title_to_number("AB")', 28), ('title_to_number("ZY")', 701)]))
    results.append(check("168. Excel Sheet Column Title", [('convert_to_title(1)', 'A'), ('convert_to_title(28)', 'AB'), ('convert_to_title(701)', 'ZY')]))
    results.append(check("1507. Reformat Date", [('reformat_date("20th Oct 2052")', '2052-10-20'), ('reformat_date("6th Jun 1933")', '1933-06-06'), ('reformat_date("26th May 1960")', '1960-05-26')]))
    results.append(check("2194. Cells in a Range on an Excel Sheet", [('cells_in_range("K1:L2")', ['K1', 'K2', 'L1', 'L2']), ('cells_in_range("A1:F1")', ['A1', 'B1', 'C1', 'D1', 'E1', 'F1'])]))
    results.append(check("1410. HTML Entity Parser", [('entity_parser("&amp; is an HTML entity but &ambassador; is not.")', '& is an HTML entity but &ambassador; is not.'), ('entity_parser("and I quote: &quot;...&quot;")', 'and I quote: "..."'), ('entity_parser("&amp;gt;")', '&gt;')]))
    results.append(check("385. Mini Parser", [('deserialize("324")', 324), ('deserialize("[123,[456,[789]]]")', [123, [456, [789]]]), ('deserialize("[-1,[],[2]]")', [-1, [], [2]])]))
    results.append(check("831. Masking Personal Information", [('mask_pii("LeetCode@LeetCode.com")', 'l*****e@leetcode.com'), ('mask_pii("AB@qq.com")', 'a*****b@qq.com'), ('mask_pii("1(234)567-890")', '***-***-7890'), ('mask_pii("86-(10)12345678")', '+**-***-***-5678')]))
    results.append(check("640. Solve the Equation", [('solve_equation("x+5-3+x=6+x-2")', 'x=2'), ('solve_equation("x=x")', 'Infinite solutions'), ('solve_equation("2x=x")', 'x=0'), ('solve_equation("x=x+2")', 'No solution')]))
    results.append(check("726. Number of Atoms", [('count_of_atoms("H2O")', 'H2O'), ('count_of_atoms("Mg(OH)2")', 'H2MgO2'), ('count_of_atoms("K4(ON(SO3)2)2")', 'K4N2O14S4')]))
    results.append(check("1096. Brace Expansion II", [('brace_expansion_ii("{a,b}{c,{d,e}}")', ['ac', 'ad', 'ae', 'bc', 'bd', 'be']), ('brace_expansion_ii("{{a,z},a{b,c},{ab,z}}")', ['a', 'ab', 'ac', 'z'])]))
    if all(results):
        print("Every solution passes its tests.")
