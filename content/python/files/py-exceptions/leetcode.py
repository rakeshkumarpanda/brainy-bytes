# 5.1 Exceptions: try, except, else, finally and raise
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


# ================================================================== 20. Valid Parentheses (Easy)
# https://leetcode.com/problems/valid-parentheses/
# Pattern: Stack
# Idea: Push every opening bracket. A closing bracket must match the top of the stack. At the end
# the stack must be empty.

def is_valid(s):
    pairs = {")": "(", "]": "[", "}": "{"}
    stack = []
    for ch in s:
        if ch in "([{":
            stack.append(ch)
        else:
            if not stack or stack[-1] != pairs[ch]:
                return False
            stack.pop()
    return not stack


# ================================================================== 1614. Maximum Nesting Depth of the Parentheses (Easy)
# https://leetcode.com/problems/maximum-nesting-depth-of-the-parentheses/
# Pattern: Counter
# Idea: Add 1 for "(" and take 1 for ")". The answer is the largest value the counter reaches.

def max_depth(s):
    depth = 0
    best = 0
    for ch in s:
        if ch == "(":
            depth = depth + 1
            if depth > best:
                best = depth
        elif ch == ")":
            depth = depth - 1
    return best


# ================================================================== 1021. Remove Outermost Parentheses (Easy)
# https://leetcode.com/problems/remove-outermost-parentheses/
# Pattern: Depth counter
# Idea: Keep a bracket only when it is not at depth 0 before an opening or after a closing.

def remove_outer_parentheses(s):
    result = []
    depth = 0
    for ch in s:
        if ch == "(":
            if depth > 0:
                result.append(ch)
            depth = depth + 1
        else:
            depth = depth - 1
            if depth > 0:
                result.append(ch)
    return "".join(result)


# ================================================================== 682. Baseball Game (Easy)
# https://leetcode.com/problems/baseball-game/
# Pattern: Stack of scores
# Idea: "+" adds the last two, "D" doubles the last, "C" removes the last, anything else is a
# number.

def cal_points(operations):
    scores = []
    for op in operations:
        if op == "+":
            scores.append(scores[-1] + scores[-2])
        elif op == "D":
            scores.append(scores[-1] * 2)
        elif op == "C":
            scores.pop()
        else:
            scores.append(int(op))
    return sum(scores)


# ================================================================== 8. String to Integer (atoi) (Medium)
# https://leetcode.com/problems/string-to-integer-atoi/
# Pattern: Careful parsing
# Idea: Skip leading spaces, read one optional sign, read digits until something else, then clamp to
# the 32 bit range.

def my_atoi(s):
    i = 0
    n = len(s)
    while i < n and s[i] == " ":
        i = i + 1
    sign = 1
    if i < n and s[i] in "+-":
        if s[i] == "-":
            sign = -1
        i = i + 1
    value = 0
    while i < n and "0" <= s[i] <= "9":
        value = value * 10 + int(s[i])
        i = i + 1
    value = value * sign
    low = -(2 ** 31)
    high = 2 ** 31 - 1
    if value < low:
        return low
    if value > high:
        return high
    return value


# ================================================================== 150. Evaluate Reverse Polish Notation (Medium)
# https://leetcode.com/problems/evaluate-reverse-polish-notation/
# Pattern: Stack
# Idea: Numbers go on a stack. An operator pops two numbers, applies itself and pushes the result.
# Division truncates toward zero.

def eval_rpn(tokens):
    stack = []
    for t in tokens:
        if t in ("+", "-", "*", "/"):
            b = stack.pop()
            a = stack.pop()
            if t == "+":
                stack.append(a + b)
            elif t == "-":
                stack.append(a - b)
            elif t == "*":
                stack.append(a * b)
            else:
                stack.append(int(a / b))
        else:
            stack.append(int(t))
    return stack[0]


# ================================================================== 468. Validate IP Address (Medium)
# https://leetcode.com/problems/validate-ip-address/
# Pattern: Validate every part
# Idea: IPv4: 4 parts of digits, 0 to 255, no leading zero. IPv6: 8 parts of 1 to 4 hex digits.
# Check characters yourself, because int() also accepts signs and spaces.

def valid_ipv4_part(part):
    if len(part) == 0 or len(part) > 3:
        return False
    for ch in part:
        if not ("0" <= ch <= "9"):
            return False
    if len(part) > 1 and part[0] == "0":
        return False
    return int(part) <= 255


def valid_ipv6_part(part):
    if len(part) == 0 or len(part) > 4:
        return False
    for ch in part:
        if ch not in "0123456789abcdefABCDEF":
            return False
    return True


def valid_ip_address(query_ip):
    if query_ip.count(".") == 3:
        parts = query_ip.split(".")
        if all(valid_ipv4_part(p) for p in parts):
            return "IPv4"
    if query_ip.count(":") == 7:
        parts = query_ip.split(":")
        if all(valid_ipv6_part(p) for p in parts):
            return "IPv6"
    return "Neither"


# ================================================================== 71. Simplify Path (Medium)
# https://leetcode.com/problems/simplify-path/
# Pattern: Stack of folder names
# Idea: Split on "/". Skip "" and ".", pop for "..", push anything else. Join with "/".

def simplify_path(path):
    stack = []
    for part in path.split("/"):
        if part == "" or part == ".":
            continue
        if part == "..":
            if stack:
                stack.pop()
        else:
            stack.append(part)
    return "/" + "/".join(stack)


# ================================================================== 227. Basic Calculator II (Medium)
# https://leetcode.com/problems/basic-calculator-ii/
# Pattern: Stack with the previous operator
# Idea: Read a number, then apply the operator before it: + and − push, * and / combine with the top
# of the stack. Sum the stack.

def calculate(s):
    stack = []
    number = 0
    op = "+"
    s = s + "+"
    for ch in s:
        if ch == " ":
            continue
        if "0" <= ch <= "9":
            number = number * 10 + int(ch)
            continue
        if op == "+":
            stack.append(number)
        elif op == "-":
            stack.append(-number)
        elif op == "*":
            stack.append(stack.pop() * number)
        else:
            stack.append(int(stack.pop() / number))
        op = ch
        number = 0
    return sum(stack)


# ================================================================== 65. Valid Number (Hard)
# https://leetcode.com/problems/valid-number/
# Pattern: Scan with a few flags
# Idea: Track whether you saw a digit, a dot and an exponent. A sign is allowed only at the start or
# right after e. A dot is not allowed after e.

def is_number(s):
    seen_digit = False
    seen_dot = False
    seen_exp = False
    for i in range(len(s)):
        ch = s[i]
        if "0" <= ch <= "9":
            seen_digit = True
        elif ch in "+-":
            if i > 0 and s[i - 1] not in "eE":
                return False
        elif ch == ".":
            if seen_dot or seen_exp:
                return False
            seen_dot = True
        elif ch in "eE":
            if seen_exp or not seen_digit:
                return False
            seen_exp = True
            seen_digit = False
        else:
            return False
    return seen_digit


if __name__ == "__main__":
    results = []
    results.append(check("20. Valid Parentheses", [('is_valid("()[]{}")', True), ('is_valid("(]")', False), ('is_valid("([)]")', False), ('is_valid("{[]}")', True), ('is_valid("(")', False)]))
    results.append(check("1614. Maximum Nesting Depth of the Parentheses", [('max_depth("(1+(2*3)+((8)/4))+1")', 3), ('max_depth("(1)+((2))+(((3)))")', 3), ('max_depth("1")', 0)]))
    results.append(check("1021. Remove Outermost Parentheses", [('remove_outer_parentheses("(()())(())")', '()()()'), ('remove_outer_parentheses("()()")', '')]))
    results.append(check("682. Baseball Game", [('cal_points(["5", "2", "C", "D", "+"])', 30), ('cal_points(["5", "-2", "4", "C", "D", "9", "+", "+"])', 27)]))
    results.append(check("8. String to Integer (atoi)", [('my_atoi("42")', 42), ('my_atoi("   -042")', -42), ('my_atoi("1337c0d3")', 1337), ('my_atoi("words 987")', 0), ('my_atoi("-91283472332")', -2147483648)]))
    results.append(check("150. Evaluate Reverse Polish Notation", [('eval_rpn(["2", "1", "+", "3", "*"])', 9), ('eval_rpn(["4", "13", "5", "/", "+"])', 6), ('eval_rpn(["10", "6", "9", "3", "+", "-11", "*", "/", "*", "17", "+", "5", "+"])', 22)]))
    results.append(check("468. Validate IP Address", [('valid_ip_address("172.16.254.1")', 'IPv4'), ('valid_ip_address("2001:0db8:85a3:0:0:8A2E:0370:7334")', 'IPv6'), ('valid_ip_address("256.256.256.256")', 'Neither'), ('valid_ip_address("01.1.1.1")', 'Neither')]))
    results.append(check("71. Simplify Path", [('simplify_path("/home/")', '/home'), ('simplify_path("/home//foo/")', '/home/foo'), ('simplify_path("/home/user/Documents/../Pictures")', '/home/user/Pictures'), ('simplify_path("/../")', '/')]))
    results.append(check("227. Basic Calculator II", [('calculate("3+2*2")', 7), ('calculate(" 3/2 ")', 1), ('calculate(" 3+5 / 2 ")', 5), ('calculate("14-3/2")', 13)]))
    results.append(check("65. Valid Number", [('is_number("0")', True), ('is_number("e")', False), ('is_number(".")', False), ('is_number("2e10")', True), ('is_number("-90E3")', True), ('is_number("99e2.5")', False), ('is_number("--6")', False), ('is_number("+.8")', True), ('is_number("4.")', True), ('is_number("1e")', False)]))
    if all(results):
        print("Every solution passes its tests.")
