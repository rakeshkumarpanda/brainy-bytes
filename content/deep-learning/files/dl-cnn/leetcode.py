# 2.1 Convolutional neural networks
# LeetCode solutions for this chapter. Try each problem on leetcode.com before you read its answer.
# From the Brainy Bytes Deep Learning subject. Run it with: python3 <this file>
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


# ================================================================== 661. Image Smoother (Easy)
# https://leetcode.com/problems/image-smoother/
# Pattern: Average each cell with its neighbours that exist
# Idea: For every cell, add up the values in the 3 × 3 window that fall inside the image and divide
# by how many there were. This is exactly a blur filter, the first filter in the animation, with the
# edges handled by counting instead of padding.

def image_smoother(img):
    m, n = len(img), len(img[0])
    out = [[0] * n for _ in range(m)]
    for i in range(m):
        for j in range(n):
            total = count = 0
            for a in range(max(0, i - 1), min(m, i + 2)):
                for b in range(max(0, j - 1), min(n, j + 2)):
                    total += img[a][b]
                    count += 1
            out[i][j] = total // count
    return out


# ================================================================== 835. Image Overlap (Medium)
# https://leetcode.com/problems/image-overlap/
# Pattern: Count, for every shift, how many 1s line up
# Idea: Pair every 1 in the first image with every 1 in the second and record the shift between
# them. The shift seen most often gives the largest overlap. Sliding one image over another and
# counting matches is a cross correlation, the same operation a convolution layer computes.

def largest_overlap(img1, img2):
    n = len(img1)
    ones1 = [(i, j) for i in range(n) for j in range(n) if img1[i][j]]
    ones2 = [(i, j) for i in range(n) for j in range(n) if img2[i][j]]
    counts = {}
    for a, b in ones1:
        for c, d in ones2:
            shift = (c - a, d - b)
            counts[shift] = counts.get(shift, 0) + 1
    return max(counts.values(), default=0)


# ================================================================== 304. Range Sum Query 2D, Immutable (Medium)
# https://leetcode.com/problems/range-sum-query-2d-immutable/
# Pattern: Precompute a 2D prefix sum (an integral image)
# Idea: Store s[i][j], the sum of everything above and to the left. Any rectangle sum is then four
# lookups. Integral images make box filters cost the same for any window size, and they powered the
# classic Viola and Jones face detector. Our helper answers a list of queries.

class NumMatrix:
    def __init__(self, matrix):
        m, n = len(matrix), len(matrix[0])
        self.s = [[0] * (n + 1) for _ in range(m + 1)]
        for i in range(m):
            for j in range(n):
                self.s[i + 1][j + 1] = matrix[i][j] + self.s[i][j + 1] + self.s[i + 1][j] - self.s[i][j]

    def sumRegion(self, r1, c1, r2, c2):
        s = self.s
        return s[r2 + 1][c2 + 1] - s[r1][c2 + 1] - s[r2 + 1][c1] + s[r1][c1]


def region_sums(matrix, queries):
    nm = NumMatrix(matrix)
    return [nm.sumRegion(*q) for q in queries]


# ================================================================== 221. Maximal Square (Medium)
# https://leetcode.com/problems/maximal-square/
# Pattern: The square ending at a cell is 1 plus the smallest of its three neighbours
# Idea: dp[i][j] is the side of the largest all 1 square whose bottom right corner is (i, j). It
# equals 1 plus the minimum of the cells above, to the left and diagonally up left. Each cell
# depends on a small window of earlier cells, the same local pattern a convolution uses.

def maximal_square(matrix):
    m, n = len(matrix), len(matrix[0])
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    best = 0
    for i in range(m):
        for j in range(n):
            if matrix[i][j] == '1':
                dp[i + 1][j + 1] = 1 + min(dp[i][j], dp[i][j + 1], dp[i + 1][j])
                best = max(best, dp[i + 1][j + 1])
    return best * best


# ================================================================== 85. Maximal Rectangle (Hard)
# https://leetcode.com/problems/maximal-rectangle/
# Pattern: Turn each row into a histogram and find its largest rectangle with a stack
# Idea: Keep, for each column, how many 1s stand above the current row. Each row is then a
# histogram, and a monotonic stack finds its largest rectangle in one pass. Building up a 2D answer
# row by row from 1D summaries is how many image algorithms stay fast.

def maximal_rectangle(matrix):
    heights = [0] * len(matrix[0])
    best = 0
    for row in matrix:
        heights = [h + 1 if v == '1' else 0 for h, v in zip(heights, row)]
        bars = heights + [0]
        stack = []
        for i, h in enumerate(bars):
            while stack and bars[stack[-1]] >= h:
                top = stack.pop()
                left = stack[-1] + 1 if stack else 0
                best = max(best, bars[top] * (i - left))
            stack.append(i)
    return best


if __name__ == "__main__":
    results = []
    results.append(check("661. Image Smoother", [('image_smoother([[1, 1, 1], [1, 0, 1], [1, 1, 1]])', [[0, 0, 0], [0, 0, 0], [0, 0, 0]]), ('image_smoother([[100, 200, 100], [200, 50, 200], [100, 200, 100]])', [[137, 141, 137], [141, 138, 141], [137, 141, 137]])]))
    results.append(check("835. Image Overlap", [('largest_overlap([[1, 1, 0], [0, 1, 0], [0, 1, 0]], [[0, 0, 0], [0, 1, 1], [0, 0, 1]])', 3), ('largest_overlap([[1]], [[1]])', 1), ('largest_overlap([[0]], [[0]])', 0)]))
    results.append(check("304. Range Sum Query 2D, Immutable", [('region_sums([[3, 0, 1, 4, 2], [5, 6, 3, 2, 1], [1, 2, 0, 1, 5], [4, 1, 0, 1, 7], [1, 0, 3, 0, 5]], [(2, 1, 4, 3), (1, 1, 2, 2), (1, 2, 2, 4)])', [8, 11, 12])]))
    results.append(check("221. Maximal Square", [("maximal_square([['1', '0', '1', '0', '0'], ['1', '0', '1', '1', '1'], ['1', '1', '1', '1', '1'], ['1', '0', '0', '1', '0']])", 4), ("maximal_square([['0', '1'], ['1', '0']])", 1), ("maximal_square([['0']])", 0)]))
    results.append(check("85. Maximal Rectangle", [("maximal_rectangle([['1', '0', '1', '0', '0'], ['1', '0', '1', '1', '1'], ['1', '1', '1', '1', '1'], ['1', '0', '0', '1', '0']])", 6), ("maximal_rectangle([['0']])", 0), ("maximal_rectangle([['1']])", 1)]))
    if all(results):
        print("Every solution passes its tests.")
