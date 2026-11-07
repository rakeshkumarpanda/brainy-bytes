# 5.2 Modules and packages: import, the standard library and pip
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


# ================================================================== 1979. Find Greatest Common Divisor of Array (Easy)
# https://leetcode.com/problems/find-greatest-common-divisor-of-array/
# Pattern: math.gcd
# Idea: Take the smallest and the largest number and return math.gcd of the two.

import math


def find_gcd(nums):
    return math.gcd(min(nums), max(nums))


# ================================================================== 1071. Greatest Common Divisor of Strings (Easy)
# https://leetcode.com/problems/greatest-common-divisor-of-strings/
# Pattern: math.gcd on lengths
# Idea: If str1 + str2 differs from str2 + str1 there is no answer. Otherwise the answer is the
# first gcd(len1, len2) characters.

import math


def gcd_of_strings(str1, str2):
    if str1 + str2 != str2 + str1:
        return ""
    size = math.gcd(len(str1), len(str2))
    return str1[:size]


# ================================================================== 69. Sqrt(x) (Easy)
# https://leetcode.com/problems/sqrtx/
# Pattern: Binary search (or math.isqrt)
# Idea: Find the largest m with m × m ≤ x by halving the search range.

def my_sqrt(x):
    low = 0
    high = x
    answer = 0
    while low <= high:
        mid = (low + high) // 2
        if mid * mid <= x:
            answer = mid
            low = mid + 1
        else:
            high = mid - 1
    return answer


# ================================================================== 367. Valid Perfect Square (Easy)
# https://leetcode.com/problems/valid-perfect-square/
# Pattern: math.isqrt
# Idea: math.isqrt(n) is the exact whole square root rounded down. Square it back and compare.

import math


def is_perfect_square(num):
    root = math.isqrt(num)
    return root * root == num


# ================================================================== 1185. Day of the Week (Easy)
# https://leetcode.com/problems/day-of-the-week/
# Pattern: datetime
# Idea: datetime.date(year, month, day).weekday() gives 0 for Monday. Map it to the names.

import datetime


def day_of_the_week(day, month, year):
    names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    return names[datetime.date(year, month, day).weekday()]


# ================================================================== 1360. Number of Days Between Two Dates (Easy)
# https://leetcode.com/problems/number-of-days-between-two-dates/
# Pattern: datetime subtraction
# Idea: Turn both texts into dates with date.fromisoformat and take abs of the difference in days.

import datetime


def days_between_dates(date1, date2):
    a = datetime.date.fromisoformat(date1)
    b = datetime.date.fromisoformat(date2)
    return abs((a - b).days)


# ================================================================== 1154. Day of the Year (Easy)
# https://leetcode.com/problems/day-of-the-year/
# Pattern: datetime
# Idea: Subtract 1 January of the same year and add 1.

import datetime


def day_of_year(date):
    d = datetime.date.fromisoformat(date)
    return (d - datetime.date(d.year, 1, 1)).days + 1


# ================================================================== 172. Factorial Trailing Zeroes (Medium)
# https://leetcode.com/problems/factorial-trailing-zeroes/
# Pattern: Count factors of 5
# Idea: Each trailing zero needs a 10 = 2 × 5, and 5s are rarer. Add n // 5 + n // 25 + n // 125 +
# ...

def trailing_zeroes(n):
    count = 0
    power = 5
    while power <= n:
        count = count + n // power
        power = power * 5
    return count


# ================================================================== 384. Shuffle an Array (Medium)
# https://leetcode.com/problems/shuffle-an-array/
# Pattern: random and the Fisher Yates shuffle
# Idea: Keep a copy of the original. To shuffle, swap item i with a random item from i to the end.

import random


class Shuffler:  # called Solution on LeetCode
    def __init__(self, nums):
        self.original = nums[:]

    def reset(self):
        return self.original[:]

    def shuffle(self):
        items = self.original[:]
        for i in range(len(items)):
            j = random.randint(i, len(items) - 1)
            items[i], items[j] = items[j], items[i]
        return items


# ================================================================== 528. Random Pick with Weight (Medium)
# https://leetcode.com/problems/random-pick-with-weight/
# Pattern: Prefix sums, random and bisect
# Idea: Build running totals. Pick a random number up to the total and find its slot with bisect.

import bisect
import random


class WeightedPicker:  # called Solution on LeetCode, with pickIndex
    def __init__(self, w):
        self.totals = []
        running = 0
        for weight in w:
            running = running + weight
            self.totals.append(running)

    def pick_index(self):
        target = random.randint(1, self.totals[-1])
        return bisect.bisect_left(self.totals, target)


if __name__ == "__main__":
    results = []
    results.append(check("1979. Find Greatest Common Divisor of Array", [('find_gcd([2, 5, 6, 9, 10])', 2), ('find_gcd([7, 5, 6, 8, 3])', 1), ('find_gcd([3, 3])', 3)]))
    results.append(check("1071. Greatest Common Divisor of Strings", [('gcd_of_strings("ABCABC", "ABC")', 'ABC'), ('gcd_of_strings("ABABAB", "ABAB")', 'AB'), ('gcd_of_strings("LEET", "CODE")', '')]))
    results.append(check("69. Sqrt(x)", [('my_sqrt(4)', 2), ('my_sqrt(8)', 2), ('my_sqrt(0)', 0), ('my_sqrt(2147395599)', 46339)]))
    results.append(check("367. Valid Perfect Square", [('is_perfect_square(16)', True), ('is_perfect_square(14)', False), ('is_perfect_square(1)', True)]))
    results.append(check("1185. Day of the Week", [('day_of_the_week(31, 8, 2019)', 'Saturday'), ('day_of_the_week(18, 7, 1999)', 'Sunday'), ('day_of_the_week(15, 8, 1993)', 'Sunday')]))
    results.append(check("1360. Number of Days Between Two Dates", [('days_between_dates("2019-06-29", "2019-06-30")', 1), ('days_between_dates("2020-01-15", "2019-12-31")', 15)]))
    results.append(check("1154. Day of the Year", [('day_of_year("2019-01-09")', 9), ('day_of_year("2019-02-10")', 41), ('day_of_year("2020-12-31")', 366)]))
    results.append(check("172. Factorial Trailing Zeroes", [('trailing_zeroes(3)', 0), ('trailing_zeroes(5)', 1), ('trailing_zeroes(100)', 24), ('trailing_zeroes(0)', 0)]))
    results.append(check("384. Shuffle an Array", [('sorted(Shuffler([1, 2, 3]).shuffle())', [1, 2, 3]), ('Shuffler([1, 2, 3]).reset()', [1, 2, 3]), ('len(Shuffler([5, 6]).shuffle())', 2)]))
    results.append(check("528. Random Pick with Weight", [('WeightedPicker([1]).pick_index()', 0), ('WeightedPicker([1, 3]).pick_index() in (0, 1)', True), ('WeightedPicker([1, 3]).totals', [1, 4])]))
    if all(results):
        print("Every solution passes its tests.")
