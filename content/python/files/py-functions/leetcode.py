# 4.1 Functions: def, return and every kind of argument
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


# ================================================================== 1342. Number of Steps to Reduce a Number to Zero (Easy)
# https://leetcode.com/problems/number-of-steps-to-reduce-a-number-to-zero/
# Pattern: Loop inside a function
# Idea: While num > 0: halve it if even, else take away 1. Count the steps and return the count.

def number_of_steps(num):
    steps = 0
    while num > 0:
        if num % 2 == 0:
            num = num // 2
        else:
            num = num - 1
        steps = steps + 1
    return steps


# ================================================================== 1920. Build Array from Permutation (Easy)
# https://leetcode.com/problems/build-array-from-permutation/
# Pattern: Index into a list
# Idea: ans[i] is nums[nums[i]]. Build a new list and return it.

def build_array(nums):
    ans = []
    for i in range(len(nums)):
        ans.append(nums[nums[i]])
    return ans


# ================================================================== 1470. Shuffle the Array (Easy)
# https://leetcode.com/problems/shuffle-the-array/
# Pattern: Two halves side by side
# Idea: Walk i from 0 to n − 1 and add nums[i] then nums[i + n].

def shuffle(nums, n):
    result = []
    for i in range(n):
        result.append(nums[i])
        result.append(nums[i + n])
    return result


# ================================================================== 2011. Final Value of Variable After Performing Operations (Easy)
# https://leetcode.com/problems/final-value-of-variable-after-performing-operations/
# Pattern: A helper decides plus or minus
# Idea: Every operation contains either "++" or "--". Add 1 or take away 1.

def final_value_after_operations(operations):
    x = 0
    for op in operations:
        if "+" in op:
            x = x + 1
        else:
            x = x - 1
    return x


# ================================================================== 1365. How Many Numbers Are Smaller Than the Current Number (Easy)
# https://leetcode.com/problems/how-many-numbers-are-smaller-than-the-current-number/
# Pattern: Helper function per item
# Idea: Write a small helper that counts the numbers smaller than x, then call it for every item.

def count_smaller(nums, x):
    count = 0
    for y in nums:
        if y < x:
            count = count + 1
    return count


def smaller_numbers_than_current(nums):
    result = []
    for x in nums:
        result.append(count_smaller(nums, x))
    return result


# ================================================================== 1431. Kids With the Greatest Number of Candies (Easy)
# https://leetcode.com/problems/kids-with-the-greatest-number-of-candies/
# Pattern: Find the max once
# Idea: Work out max(candies) once. Kid i can be the greatest if candies[i] + extra reaches it.

def kids_with_candies(candies, extra_candies):
    best = max(candies)
    result = []
    for c in candies:
        result.append(c + extra_candies >= best)
    return result


# ================================================================== 2652. Sum Multiples (Easy)
# https://leetcode.com/problems/sum-multiples/
# Pattern: Small test function
# Idea: Add every number from 1 to n that divides by 3, 5 or 7.

def sum_of_multiples(n):
    total = 0
    for i in range(1, n + 1):
        if i % 3 == 0 or i % 5 == 0 or i % 7 == 0:
            total = total + i
    return total


# ================================================================== 1323. Maximum 69 Number (Easy)
# https://leetcode.com/problems/maximum-69-number/
# Pattern: Change the first 6
# Idea: Turn the number into text, replace the first 6 with a 9, and turn it back.

def maximum_69_number(num):
    text = str(num)
    return int(text.replace("6", "9", 1))


# ================================================================== 2160. Minimum Sum of Four Digit Number After Splitting Digits (Easy)
# https://leetcode.com/problems/minimum-sum-of-four-digit-number-after-splitting-digits/
# Pattern: Sort the digits
# Idea: Sort the 4 digits a ≤ b ≤ c ≤ d. The best split is (10a + c) + (10b + d).

def minimum_sum(num):
    d = sorted(str(num))
    return int(d[0] + d[2]) + int(d[1] + d[3])


# ================================================================== 1641. Count Sorted Vowel Strings (Medium)
# https://leetcode.com/problems/count-sorted-vowel-strings/
# Pattern: Maths in a function
# Idea: A sorted string of length n over 5 vowels is a choice of n items from 5 with repeats: C(n +
# 4, 4).

def count_vowel_strings(n):
    return (n + 1) * (n + 2) * (n + 3) * (n + 4) // 24


if __name__ == "__main__":
    results = []
    results.append(check("1342. Number of Steps to Reduce a Number to Zero", [('number_of_steps(14)', 6), ('number_of_steps(8)', 4), ('number_of_steps(123)', 12)]))
    results.append(check("1920. Build Array from Permutation", [('build_array([0, 2, 1, 5, 3, 4])', [0, 1, 2, 4, 5, 3]), ('build_array([5, 0, 1, 2, 3, 4])', [4, 5, 0, 1, 2, 3])]))
    results.append(check("1470. Shuffle the Array", [('shuffle([2, 5, 1, 3, 4, 7], 3)', [2, 3, 5, 4, 1, 7]), ('shuffle([1, 1, 2, 2], 2)', [1, 2, 1, 2])]))
    results.append(check("2011. Final Value of Variable After Performing Operations", [('final_value_after_operations(["--X", "X++", "X++"])', 1), ('final_value_after_operations(["++X", "++X", "X++"])', 3)]))
    results.append(check("1365. How Many Numbers Are Smaller Than the Current Number", [('smaller_numbers_than_current([8, 1, 2, 2, 3])', [4, 0, 1, 1, 3]), ('smaller_numbers_than_current([7, 7, 7])', [0, 0, 0])]))
    results.append(check("1431. Kids With the Greatest Number of Candies", [('kids_with_candies([2, 3, 5, 1, 3], 3)', [True, True, True, False, True]), ('kids_with_candies([4, 2, 1, 1, 2], 1)', [True, False, False, False, False])]))
    results.append(check("2652. Sum Multiples", [('sum_of_multiples(7)', 21), ('sum_of_multiples(10)', 40), ('sum_of_multiples(9)', 30)]))
    results.append(check("1323. Maximum 69 Number", [('maximum_69_number(9669)', 9969), ('maximum_69_number(9996)', 9999), ('maximum_69_number(9999)', 9999)]))
    results.append(check("2160. Minimum Sum of Four Digit Number After Splitting Digits", [('minimum_sum(2932)', 52), ('minimum_sum(4009)', 13)]))
    results.append(check("1641. Count Sorted Vowel Strings", [('count_vowel_strings(1)', 5), ('count_vowel_strings(2)', 15), ('count_vowel_strings(33)', 66045)]))
    if all(results):
        print("Every solution passes its tests.")
