# 3.2 Lists: storing, changing, sorting and copying
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


# ================================================================== 1929. Concatenation of Array (Easy)
# https://leetcode.com/problems/concatenation-of-array/
# Pattern: List repetition
# Idea: The answer is the list followed by itself.

def get_concatenation(nums):
    return nums + nums


# ================================================================== 66. Plus One (Easy)
# https://leetcode.com/problems/plus-one/
# Pattern: Walk from the right with a carry
# Idea: Start at the last digit. A 9 becomes 0 and the carry moves left. If every digit was 9, put a
# 1 in front.

def plus_one(digits):
    digits = digits[:]
    i = len(digits) - 1
    while i >= 0:
        if digits[i] < 9:
            digits[i] = digits[i] + 1
            return digits
        digits[i] = 0
        i = i - 1
    return [1] + digits


# ================================================================== 27. Remove Element (Easy)
# https://leetcode.com/problems/remove-element/
# Pattern: Two pointers (read and write)
# Idea: Keep a write position. Copy every item that is not val to the write position. Return how
# many you kept.

def remove_element(nums, val):
    write = 0
    for read in range(len(nums)):
        if nums[read] != val:
            nums[write] = nums[read]
            write = write + 1
    return write


# ================================================================== 26. Remove Duplicates from Sorted Array (Easy)
# https://leetcode.com/problems/remove-duplicates-from-sorted-array/
# Pattern: Two pointers
# Idea: The list is sorted, so repeats sit next to each other. Write an item only when it differs
# from the last one written.

def remove_duplicates(nums):
    if not nums:
        return 0
    write = 1
    for read in range(1, len(nums)):
        if nums[read] != nums[write - 1]:
            nums[write] = nums[read]
            write = write + 1
    return write


# ================================================================== 283. Move Zeroes (Easy)
# https://leetcode.com/problems/move-zeroes/
# Pattern: Two pointers
# Idea: Move every non zero item forward to a write position, then fill the rest with zeros.

def move_zeroes(nums):
    write = 0
    for x in nums:
        if x != 0:
            nums[write] = x
            write = write + 1
    for i in range(write, len(nums)):
        nums[i] = 0
    return nums


# ================================================================== 121. Best Time to Buy and Sell Stock (Easy)
# https://leetcode.com/problems/best-time-to-buy-and-sell-stock/
# Pattern: Running minimum
# Idea: Keep the lowest price so far. Each day, check the profit if you sold today.

def max_profit(prices):
    lowest = prices[0]
    best = 0
    for price in prices:
        if price < lowest:
            lowest = price
        if price - lowest > best:
            best = price - lowest
    return best


# ================================================================== 88. Merge Sorted Array (Easy)
# https://leetcode.com/problems/merge-sorted-array/
# Pattern: Three pointers from the back
# Idea: Fill nums1 from its end. Each time place the bigger of the two last items.

def merge(nums1, m, nums2, n):
    i = m - 1
    j = n - 1
    k = m + n - 1
    while j >= 0:
        if i >= 0 and nums1[i] > nums2[j]:
            nums1[k] = nums1[i]
            i = i - 1
        else:
            nums1[k] = nums2[j]
            j = j - 1
        k = k - 1
    return nums1


# ================================================================== 118. Pascal's Triangle (Easy)
# https://leetcode.com/problems/pascals-triangle/
# Pattern: Build each row from the one above
# Idea: Each row starts and ends with 1. Every inner number is the sum of the two numbers above it.

def generate(num_rows):
    triangle = []
    for r in range(num_rows):
        row = [1] * (r + 1)
        for c in range(1, r):
            row[c] = triangle[r - 1][c - 1] + triangle[r - 1][c]
        triangle.append(row)
    return triangle


# ================================================================== 189. Rotate Array (Medium)
# https://leetcode.com/problems/rotate-array/
# Pattern: Three reversals
# Idea: Reverse the whole list, then reverse the first k items and the rest. Use k % n first.

def reverse_part(nums, left, right):
    while left < right:
        nums[left], nums[right] = nums[right], nums[left]
        left = left + 1
        right = right - 1


def rotate(nums, k):
    n = len(nums)
    k = k % n
    reverse_part(nums, 0, n - 1)
    reverse_part(nums, 0, k - 1)
    reverse_part(nums, k, n - 1)
    return nums


# ================================================================== 75. Sort Colors (Medium)
# https://leetcode.com/problems/sort-colors/
# Pattern: Dutch national flag (three pointers)
# Idea: Keep low, mid and high. A 0 swaps to low, a 2 swaps to high, a 1 just moves mid on.

def sort_colors(nums):
    low = 0
    mid = 0
    high = len(nums) - 1
    while mid <= high:
        if nums[mid] == 0:
            nums[low], nums[mid] = nums[mid], nums[low]
            low = low + 1
            mid = mid + 1
        elif nums[mid] == 1:
            mid = mid + 1
        else:
            nums[mid], nums[high] = nums[high], nums[mid]
            high = high - 1
    return nums


# ================================================================== 48. Rotate Image (Medium)
# https://leetcode.com/problems/rotate-image/
# Pattern: Transpose, then reverse each row
# Idea: Swap matrix[r][c] with matrix[c][r] above the diagonal, then reverse every row.

def rotate_image(matrix):
    n = len(matrix)
    for r in range(n):
        for c in range(r + 1, n):
            matrix[r][c], matrix[c][r] = matrix[c][r], matrix[r][c]
    for row in matrix:
        row.reverse()
    return matrix


# ================================================================== 54. Spiral Matrix (Medium)
# https://leetcode.com/problems/spiral-matrix/
# Pattern: Shrinking borders
# Idea: Keep top, bottom, left and right borders. Walk right, down, left and up, moving a border in
# after each side.

def spiral_order(matrix):
    result = []
    top = 0
    bottom = len(matrix) - 1
    left = 0
    right = len(matrix[0]) - 1
    while top <= bottom and left <= right:
        for c in range(left, right + 1):
            result.append(matrix[top][c])
        top = top + 1
        for r in range(top, bottom + 1):
            result.append(matrix[r][right])
        right = right - 1
        if top <= bottom:
            for c in range(right, left - 1, -1):
                result.append(matrix[bottom][c])
            bottom = bottom - 1
        if left <= right:
            for r in range(bottom, top - 1, -1):
                result.append(matrix[r][left])
            left = left + 1
    return result


if __name__ == "__main__":
    results = []
    results.append(check("1929. Concatenation of Array", [('get_concatenation([1, 2, 1])', [1, 2, 1, 1, 2, 1]), ('get_concatenation([5])', [5, 5])]))
    results.append(check("66. Plus One", [('plus_one([1, 2, 3])', [1, 2, 4]), ('plus_one([9, 9])', [1, 0, 0]), ('plus_one([0])', [1])]))
    results.append(check("27. Remove Element", [('remove_element([3, 2, 2, 3], 3)', 2), ('remove_element([0, 1, 2, 2, 3, 0, 4, 2], 2)', 5)]))
    results.append(check("26. Remove Duplicates from Sorted Array", [('remove_duplicates([1, 1, 2])', 2), ('remove_duplicates([0, 0, 1, 1, 1, 2, 2, 3, 3, 4])', 5)]))
    results.append(check("283. Move Zeroes", [('move_zeroes([0, 1, 0, 3, 12])', [1, 3, 12, 0, 0]), ('move_zeroes([0])', [0])]))
    results.append(check("121. Best Time to Buy and Sell Stock", [('max_profit([7, 1, 5, 3, 6, 4])', 5), ('max_profit([7, 6, 4, 3, 1])', 0)]))
    results.append(check("88. Merge Sorted Array", [('merge([1, 2, 3, 0, 0, 0], 3, [2, 5, 6], 3)', [1, 2, 2, 3, 5, 6]), ('merge([0], 0, [1], 1)', [1])]))
    results.append(check("118. Pascal's Triangle", [('generate(5)', [[1], [1, 1], [1, 2, 1], [1, 3, 3, 1], [1, 4, 6, 4, 1]]), ('generate(1)', [[1]])]))
    results.append(check("189. Rotate Array", [('rotate([1, 2, 3, 4, 5, 6, 7], 3)', [5, 6, 7, 1, 2, 3, 4]), ('rotate([-1, -100, 3, 99], 2)', [3, 99, -1, -100]), ('rotate([1, 2], 3)', [2, 1])]))
    results.append(check("75. Sort Colors", [('sort_colors([2, 0, 2, 1, 1, 0])', [0, 0, 1, 1, 2, 2]), ('sort_colors([2, 0, 1])', [0, 1, 2])]))
    results.append(check("48. Rotate Image", [('rotate_image([[1, 2, 3], [4, 5, 6], [7, 8, 9]])', [[7, 4, 1], [8, 5, 2], [9, 6, 3]])]))
    results.append(check("54. Spiral Matrix", [('spiral_order([[1, 2, 3], [4, 5, 6], [7, 8, 9]])', [1, 2, 3, 6, 9, 8, 7, 4, 5]), ('spiral_order([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]])', [1, 2, 3, 4, 8, 12, 11, 10, 9, 5, 6, 7])]))
    if all(results):
        print("Every solution passes its tests.")
