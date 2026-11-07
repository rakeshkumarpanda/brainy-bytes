# 7.1 Exam practice: PCEP and PCAP style papers
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


# ================================================================== 11. Container With Most Water (Medium)
# https://leetcode.com/problems/container-with-most-water/
# Pattern: Two pointers
# Idea: Start at both ends. The area is width times the shorter wall. Move the shorter wall inwards,
# because only that can make the area bigger.

def max_area(height):
    left = 0
    right = len(height) - 1
    best = 0
    while left < right:
        area = (right - left) * min(height[left], height[right])
        best = max(best, area)
        if height[left] < height[right]:
            left += 1
        else:
            right -= 1
    return best


# ================================================================== 12. Integer to Roman (Medium)
# https://leetcode.com/problems/integer-to-roman/
# Pattern: Greedy table
# Idea: Walk a table from 1000 (M) down to 1 (I), including 900, 400, 90, 40, 9 and 4. Take each
# value as many times as it fits.

def int_to_roman(num):
    table = [(1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"), (90, "XC"),
             (50, "L"), (40, "XL"), (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")]
    result = ""
    for value, letters in table:
        while num >= value:
            result = result + letters
            num = num - value
    return result


# ================================================================== 15. 3Sum (Medium)
# https://leetcode.com/problems/3sum/
# Pattern: Sort, then two pointers
# Idea: Sort the list. For each first number, look for two more with two pointers. Skip equal
# neighbours so no triple repeats.

def three_sum(nums):
    nums = sorted(nums)
    result = []
    for i in range(len(nums) - 2):
        if i > 0 and nums[i] == nums[i - 1]:
            continue
        left = i + 1
        right = len(nums) - 1
        while left < right:
            total = nums[i] + nums[left] + nums[right]
            if total < 0:
                left += 1
            elif total > 0:
                right -= 1
            else:
                result.append([nums[i], nums[left], nums[right]])
                left += 1
                while left < right and nums[left] == nums[left - 1]:
                    left += 1
                right -= 1
    return result


# ================================================================== 17. Letter Combinations of a Phone Number (Medium)
# https://leetcode.com/problems/letter-combinations-of-a-phone-number/
# Pattern: Grow the list digit by digit
# Idea: Start with [""] and, for every digit, add each of its letters to every string made so far.

def letter_combinations(digits):
    if digits == "":
        return []
    keys = {"2": "abc", "3": "def", "4": "ghi", "5": "jkl", "6": "mno", "7": "pqrs", "8": "tuv", "9": "wxyz"}
    result = [""]
    for digit in digits:
        result = [start + letter for start in result for letter in keys[digit]]
    return result


# ================================================================== 36. Valid Sudoku (Medium)
# https://leetcode.com/problems/valid-sudoku/
# Pattern: Sets for rows, columns and boxes
# Idea: Keep a set for each row, column and 3 by 3 box. A digit seen twice in any of them makes the
# board invalid. The box number is (r // 3) * 3 + c // 3.

def is_valid_sudoku(board):
    rows = [set() for i in range(9)]
    cols = [set() for i in range(9)]
    boxes = [set() for i in range(9)]
    for r in range(9):
        for c in range(9):
            value = board[r][c]
            if value == ".":
                continue
            b = (r // 3) * 3 + c // 3
            if value in rows[r] or value in cols[c] or value in boxes[b]:
                return False
            rows[r].add(value)
            cols[c].add(value)
            boxes[b].add(value)
    return True


def make_board(top_left):
    # a board that is empty except for the first row given as a string
    board = [["."] * 9 for i in range(9)]
    for c in range(len(top_left)):
        board[0][c] = top_left[c]
    return board


# ================================================================== 38. Count and Say (Medium)
# https://leetcode.com/problems/count-and-say/
# Pattern: Describe the previous term
# Idea: Read the previous string in runs of equal digits and write the run length followed by the
# digit.

def count_and_say(n):
    term = "1"
    for step in range(n - 1):
        new = ""
        i = 0
        while i < len(term):
            j = i
            while j < len(term) and term[j] == term[i]:
                j += 1
            new = new + str(j - i) + term[i]
            i = j
        term = new
    return term


# ================================================================== 56. Merge Intervals (Medium)
# https://leetcode.com/problems/merge-intervals/
# Pattern: Sort by start
# Idea: Sort the intervals by start. If the next one starts before the last merged one ends, stretch
# the end, otherwise start a new interval.

def merge(intervals):
    result = []
    for start, end in sorted(intervals):
        if result and start <= result[-1][1]:
            result[-1][1] = max(result[-1][1], end)
        else:
            result.append([start, end])
    return result


# ================================================================== 67. Add Binary (Easy)
# https://leetcode.com/problems/add-binary/
# Pattern: Add from the right with a carry
# Idea: Walk both strings from the end, add the digits and the carry, write total % 2 and carry
# total // 2.

def add_binary(a, b):
    i = len(a) - 1
    j = len(b) - 1
    carry = 0
    result = ""
    while i >= 0 or j >= 0 or carry:
        total = carry
        if i >= 0:
            total += int(a[i])
            i -= 1
        if j >= 0:
            total += int(b[j])
            j -= 1
        result = str(total % 2) + result
        carry = total // 2
    return result


# ================================================================== 238. Product of Array Except Self (Medium)
# https://leetcode.com/problems/product-of-array-except-self/
# Pattern: Products from the left and from the right
# Idea: answer[i] is the product of everything left of i times everything right of i. Two passes, no
# division.

def product_except_self(nums):
    n = len(nums)
    answer = [1] * n
    left = 1
    for i in range(n):
        answer[i] = left
        left = left * nums[i]
    right = 1
    for i in range(n - 1, -1, -1):
        answer[i] = answer[i] * right
        right = right * nums[i]
    return answer


# ================================================================== 448. Find All Numbers Disappeared in an Array (Easy)
# https://leetcode.com/problems/find-all-numbers-disappeared-in-an-array/
# Pattern: Set difference
# Idea: The numbers should be 1 to n. Put the list in a set and keep the numbers from 1 to n that
# are not in it.

def find_disappeared_numbers(nums):
    seen = set(nums)
    return [n for n in range(1, len(nums) + 1) if n not in seen]


if __name__ == "__main__":
    results = []
    results.append(check("11. Container With Most Water", [('max_area([1, 8, 6, 2, 5, 4, 8, 3, 7])', 49), ('max_area([1, 1])', 1)]))
    results.append(check("12. Integer to Roman", [('int_to_roman(3749)', 'MMMDCCXLIX'), ('int_to_roman(58)', 'LVIII'), ('int_to_roman(1994)', 'MCMXCIV')]))
    results.append(check("15. 3Sum", [('three_sum([-1, 0, 1, 2, -1, -4])', [[-1, -1, 2], [-1, 0, 1]]), ('three_sum([0, 1, 1])', []), ('three_sum([0, 0, 0])', [[0, 0, 0]])]))
    results.append(check("17. Letter Combinations of a Phone Number", [('letter_combinations("23")', ['ad', 'ae', 'af', 'bd', 'be', 'bf', 'cd', 'ce', 'cf']), ('letter_combinations("")', []), ('letter_combinations("2")', ['a', 'b', 'c'])]))
    results.append(check("36. Valid Sudoku", [('is_valid_sudoku(make_board("53..7...."))', True), ('is_valid_sudoku(make_board("53..7...5"))', False)]))
    results.append(check("38. Count and Say", [('count_and_say(1)', '1'), ('count_and_say(4)', '1211'), ('count_and_say(6)', '312211')]))
    results.append(check("56. Merge Intervals", [('merge([[1, 3], [2, 6], [8, 10], [15, 18]])', [[1, 6], [8, 10], [15, 18]]), ('merge([[1, 4], [4, 5]])', [[1, 5]])]))
    results.append(check("67. Add Binary", [('add_binary("11", "1")', '100'), ('add_binary("1010", "1011")', '10101')]))
    results.append(check("238. Product of Array Except Self", [('product_except_self([1, 2, 3, 4])', [24, 12, 8, 6]), ('product_except_self([-1, 1, 0, -3, 3])', [0, 0, 9, 0, 0])]))
    results.append(check("448. Find All Numbers Disappeared in an Array", [('find_disappeared_numbers([4, 3, 2, 7, 8, 2, 3, 1])', [5, 6]), ('find_disappeared_numbers([1, 1])', [2])]))
    if all(results):
        print("Every solution passes its tests.")
