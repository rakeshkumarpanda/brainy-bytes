# 2.3 Context managers and the with statement
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


# ================================================================== 636. Exclusive Time of Functions (Medium)
# https://leetcode.com/problems/exclusive-time-of-functions/
# Pattern: A stack of running functions
# Idea: Logs open and close like nested with blocks. Keep a stack of running ids. When something
# starts or ends, give the time since the last event to the function on top.

def exclusive_time(n, logs):
    result = [0] * n
    stack = []
    previous = 0
    for entry in logs:
        func_id, kind, time = entry.split(":")
        func_id = int(func_id)
        time = int(time)
        if kind == "start":
            if stack:
                result[stack[-1]] += time - previous
            stack.append(func_id)
            previous = time
        else:
            result[stack.pop()] += time - previous + 1
            previous = time + 1
    return result


# ================================================================== 71. Simplify Path (Medium)
# https://leetcode.com/problems/simplify-path/
# Pattern: A stack of folder names
# Idea: Split on "/". Skip empty parts and ".". ".." pops the last folder, like leaving a with
# block. Everything else is pushed.

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


# ================================================================== 921. Minimum Add to Make Parentheses Valid (Medium)
# https://leetcode.com/problems/minimum-add-to-make-parentheses-valid/
# Pattern: Count open brackets
# Idea: Track how many "(" are still open. A ")" with nothing open needs an added "(". At the end
# every open one needs a ")".

def min_add_to_make_valid(s):
    open_count = 0
    added = 0
    for ch in s:
        if ch == "(":
            open_count += 1
        elif open_count > 0:
            open_count -= 1
        else:
            added += 1
    return added + open_count


# ================================================================== 1249. Minimum Remove to Make Valid Parentheses (Medium)
# https://leetcode.com/problems/minimum-remove-to-make-valid-parentheses/
# Pattern: A stack of open positions
# Idea: Push the index of each "(". A ")" with an empty stack is removed. Any "(" left on the stack
# at the end is removed too.

def min_remove_to_make_valid(s):
    chars = list(s)
    stack = []
    for i in range(len(chars)):
        if chars[i] == "(":
            stack.append(i)
        elif chars[i] == ")":
            if stack:
                stack.pop()
            else:
                chars[i] = ""
    for i in stack:
        chars[i] = ""
    return "".join(chars)


# ================================================================== 856. Score of Parentheses (Medium)
# https://leetcode.com/problems/score-of-parentheses/
# Pattern: A stack of scores per level
# Idea: Opening starts a new level with score 0. Closing turns the level into 1 if it was empty, or
# double its score otherwise, and adds it to the level outside.

def score_of_parentheses(s):
    stack = [0]
    for ch in s:
        if ch == "(":
            stack.append(0)
        else:
            inner = stack.pop()
            stack[-1] += max(2 * inner, 1)
    return stack[0]


# ================================================================== 1190. Reverse Substrings Between Each Pair of Parentheses (Medium)
# https://leetcode.com/problems/reverse-substrings-between-each-pair-of-parentheses/
# Pattern: A stack of unfinished text
# Idea: On "(" save the text so far and start fresh. On ")" reverse the inner text and glue it to
# the saved text.

def reverse_parentheses(s):
    stack = []
    text = ""
    for ch in s:
        if ch == "(":
            stack.append(text)
            text = ""
        elif ch == ")":
            text = stack.pop() + text[::-1]
        else:
            text += ch
    return text


# ================================================================== 32. Longest Valid Parentheses (Hard)
# https://leetcode.com/problems/longest-valid-parentheses/
# Pattern: A stack of indexes with a base
# Idea: Keep the index of the last unmatched position at the bottom of the stack. After each match,
# the length is the current index minus the index on top.

def longest_valid_parentheses(s):
    stack = [-1]
    best = 0
    for i in range(len(s)):
        if s[i] == "(":
            stack.append(i)
        else:
            stack.pop()
            if not stack:
                stack.append(i)                # a new base
            else:
                best = max(best, i - stack[-1])
    return best


# ================================================================== 735. Asteroid Collision (Medium)
# https://leetcode.com/problems/asteroid-collision/
# Pattern: A stack of survivors
# Idea: Only a left moving asteroid can hit the right moving ones on the stack. Pop the smaller
# ones, stop if it is destroyed.

def asteroid_collision(asteroids):
    stack = []
    for rock in asteroids:
        alive = True
        while alive and rock < 0 and stack and stack[-1] > 0:
            if stack[-1] < -rock:
                stack.pop()
            elif stack[-1] == -rock:
                stack.pop()
                alive = False
            else:
                alive = False
        if alive:
            stack.append(rock)
    return stack


# ================================================================== 844. Backspace String Compare (Easy)
# https://leetcode.com/problems/backspace-string-compare/
# Pattern: Build each text with a stack
# Idea: Push letters, pop on "#". Compare the two results.

def typed(text):
    stack = []
    for ch in text:
        if ch == "#":
            if stack:
                stack.pop()
        else:
            stack.append(ch)
    return stack


def backspace_compare(s, t):
    return typed(s) == typed(t)


# ================================================================== 2390. Removing Stars From a String (Medium)
# https://leetcode.com/problems/removing-stars-from-a-string/
# Pattern: A stack again
# Idea: Each star removes the closest letter on its left: push letters and pop on "*".

def remove_stars(s):
    stack = []
    for ch in s:
        if ch == "*":
            stack.pop()
        else:
            stack.append(ch)
    return "".join(stack)


if __name__ == "__main__":
    results = []
    results.append(check("636. Exclusive Time of Functions", [('exclusive_time(2, ["0:start:0", "1:start:2", "1:end:5", "0:end:6"])', [3, 4]), ('exclusive_time(1, ["0:start:0", "0:start:2", "0:end:5", "0:start:6", "0:end:6", "0:end:7"])', [8])]))
    results.append(check("71. Simplify Path", [('simplify_path("/home/")', '/home'), ('simplify_path("/home//foo/")', '/home/foo'), ('simplify_path("/home/user/Documents/../Pictures")', '/home/user/Pictures'), ('simplify_path("/../")', '/'), ('simplify_path("/.../a/../b/c/../d/./")', '/.../b/d')]))
    results.append(check("921. Minimum Add to Make Parentheses Valid", [('min_add_to_make_valid("())")', 1), ('min_add_to_make_valid("(((")', 3), ('min_add_to_make_valid("()))((")', 4)]))
    results.append(check("1249. Minimum Remove to Make Valid Parentheses", [('min_remove_to_make_valid("lee(t(c)o)de)")', 'lee(t(c)o)de'), ('min_remove_to_make_valid("a)b(c)d")', 'ab(c)d'), ('min_remove_to_make_valid("))((")', '')]))
    results.append(check("856. Score of Parentheses", [('score_of_parentheses("()")', 1), ('score_of_parentheses("(())")', 2), ('score_of_parentheses("()()")', 2), ('score_of_parentheses("(()(()))")', 6)]))
    results.append(check("1190. Reverse Substrings Between Each Pair of Parentheses", [('reverse_parentheses("(abcd)")', 'dcba'), ('reverse_parentheses("(u(love)i)")', 'iloveu'), ('reverse_parentheses("(ed(et(oc))el)")', 'leetcode')]))
    results.append(check("32. Longest Valid Parentheses", [('longest_valid_parentheses("(()")', 2), ('longest_valid_parentheses(")()())")', 4), ('longest_valid_parentheses("")', 0)]))
    results.append(check("735. Asteroid Collision", [('asteroid_collision([5, 10, -5])', [5, 10]), ('asteroid_collision([8, -8])', []), ('asteroid_collision([10, 2, -5])', [10]), ('asteroid_collision([-2, -1, 1, 2])', [-2, -1, 1, 2])]))
    results.append(check("844. Backspace String Compare", [('backspace_compare("ab#c", "ad#c")', True), ('backspace_compare("ab##", "c#d#")', True), ('backspace_compare("a#c", "b")', False)]))
    results.append(check("2390. Removing Stars From a String", [('remove_stars("leet**cod*e")', 'lecoe'), ('remove_stars("erase*****")', '')]))
    if all(results):
        print("Every solution passes its tests.")
