# 2.2 Recurrent networks, LSTM and GRU
# LeetCode solutions for this chapter. Try each problem on leetcode.com before you read its answer.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn


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
# Pattern: Push opening brackets and pop on each closing one
# Idea: Read the string one character at a time, keeping a stack of brackets still open. A closing
# bracket must match the top of the stack. Like an RNN, the stack is a state that carries what
# matters from earlier in the sequence.

def is_valid(s):
    pairs = {')': '(', ']': '[', '}': '{'}
    stack = []
    for ch in s:
        if ch in pairs:
            if not stack or stack.pop() != pairs[ch]:
                return False
        else:
            stack.append(ch)
    return not stack


# ================================================================== 901. Online Stock Span (Medium)
# https://leetcode.com/problems/online-stock-span/
# Pattern: Keep a stack of (price, span) and merge smaller prices into the new one
# Idea: Prices arrive one at a time, and the answer must come immediately, exactly the streaming
# setting of an RNN. Pop every earlier price that is not higher and add its span, so each price is
# pushed and popped once. Our helper feeds a list of prices.

class StockSpanner:
    def __init__(self):
        self.stack = []

    def next(self, price):
        span = 1
        while self.stack and self.stack[-1][0] <= price:
            span += self.stack.pop()[1]
        self.stack.append((price, span))
        return span


def stock_spans(prices):
    s = StockSpanner()
    return [s.next(p) for p in prices]


# ================================================================== 394. Decode String (Medium)
# https://leetcode.com/problems/decode-string/
# Pattern: Save the current text and count on a stack at each opening bracket
# Idea: Build the current piece character by character. At "[" save it with the repeat count, at "]"
# pop and repeat. Nested structure in a sequence is exactly what a single fixed size state finds
# hard, and why a stack makes it easy.

def decode_string(s):
    stack, current, num = [], '', 0
    for ch in s:
        if ch.isdigit():
            num = num * 10 + int(ch)
        elif ch == '[':
            stack.append((current, num))
            current, num = '', 0
        elif ch == ']':
            prev, k = stack.pop()
            current = prev + current * k
        else:
            current += ch
    return current


# ================================================================== 1143. Longest Common Subsequence (Medium)
# https://leetcode.com/problems/longest-common-subsequence/
# Pattern: A table over prefixes of both strings
# Idea: dp[i][j] is the answer for the first i characters of a and the first j of b. Matching
# characters extend the diagonal, otherwise take the better of dropping one character. Aligning two
# sequences is the problem encoder decoder models and attention solve for translation.

def longest_common_subsequence(a, b):
    dp = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return dp[-1][-1]


# ================================================================== 72. Edit Distance (Hard)
# https://leetcode.com/problems/edit-distance/
# Pattern: Each cell is the cheapest of insert, delete or replace from a neighbour
# Idea: dp[i][j] is the number of edits to turn the first i letters of word1 into the first j
# letters of word2. Speech recognition is scored with this distance at the word level (the word
# error rate), and CTC training for speech RNNs uses a closely related table.

def min_distance(word1, word2):
    m, n = len(word1), len(word2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if word1[i - 1] == word2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])
    return dp[m][n]


if __name__ == "__main__":
    results = []
    results.append(check("20. Valid Parentheses", [("is_valid('()[]{}')", True), ("is_valid('(]')", False), ("is_valid('([)]')", False), ("is_valid('{[]}')", True)]))
    results.append(check("901. Online Stock Span", [('stock_spans([100, 80, 60, 70, 60, 75, 85])', [1, 1, 1, 2, 1, 4, 6])]))
    results.append(check("394. Decode String", [("decode_string('3[a]2[bc]')", 'aaabcbc'), ("decode_string('3[a2[c]]')", 'accaccacc'), ("decode_string('2[abc]3[cd]ef')", 'abcabccdcdcdef')]))
    results.append(check("1143. Longest Common Subsequence", [("longest_common_subsequence('abcde', 'ace')", 3), ("longest_common_subsequence('abc', 'abc')", 3), ("longest_common_subsequence('abc', 'def')", 0)]))
    results.append(check("72. Edit Distance", [("min_distance('horse', 'ros')", 3), ("min_distance('intention', 'execution')", 5), ("min_distance('', 'a')", 1)]))
    if all(results):
        print("Every solution passes its tests.")
