# 2.1 Principal component analysis (PCA)
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


# ================================================================== 867. Transpose Matrix (Easy)
# https://leetcode.com/problems/transpose-matrix/
# Pattern: Swap rows and columns
# Idea: Row i of the answer is column i of the input. The transpose appears in every PCA formula,
# starting with the covariance matrix XT X.

def transpose(matrix):
    return [list(col) for col in zip(*matrix)]


# ================================================================== 48. Rotate Image (Medium)
# https://leetcode.com/problems/rotate-image/
# Pattern: Transpose, then reverse every row
# Idea: A quarter turn clockwise is a transpose followed by flipping each row. PCA is also a
# rotation: it turns the axes to line up with the directions of most variance. LeetCode changes the
# matrix in place, and ours also returns it so it can be checked.

def rotate(matrix):
    n = len(matrix)
    for i in range(n):
        for j in range(i + 1, n):
            matrix[i][j], matrix[j][i] = matrix[j][i], matrix[i][j]
    for row in matrix:
        row.reverse()
    return matrix


# ================================================================== 2482. Difference Between Ones and Zeros in Row and Column (Medium)
# https://leetcode.com/problems/difference-between-ones-and-zeros-in-row-and-column/
# Pattern: Count once per row and once per column
# Idea: Precompute the number of ones in each row and each column. Then each cell is 2 × ones in its
# row + 2 × ones in its column − rows − columns. Row and column totals are also the first step of
# centring data.

def ones_minus_zeros(grid):
    m, n = len(grid), len(grid[0])
    row = [sum(r) for r in grid]
    col = [sum(grid[i][j] for i in range(m)) for j in range(n)]
    return [[2 * row[i] + 2 * col[j] - m - n for j in range(n)] for i in range(m)]


# ================================================================== 1329. Sort the Matrix Diagonally (Medium)
# https://leetcode.com/problems/sort-the-matrix-diagonally/
# Pattern: Group cells by i minus j
# Idea: Cells on the same diagonal share the value i − j. Collect each diagonal, sort it, and write
# it back in order. The diagonal of a covariance matrix holds the variances, and an eigen
# decomposition turns the whole matrix diagonal.

def diagonal_sort(mat):
    m, n = len(mat), len(mat[0])
    diag = {}
    for i in range(m):
        for j in range(n):
            diag.setdefault(i - j, []).append(mat[i][j])
    for key in diag:
        diag[key].sort(reverse=True)
    out = [[0] * n for _ in range(m)]
    for i in range(m):
        for j in range(n):
            out[i][j] = diag[i - j].pop()
    return out


# ================================================================== 1314. Matrix Block Sum (Medium)
# https://leetcode.com/problems/matrix-block-sum/
# Pattern: Two dimensional prefix sums
# Idea: Build P where P[i][j] is the sum of the top left i by j block. Any rectangle sum is then
# four lookups. The same trick computes many means and covariances over windows quickly.

def matrix_block_sum(mat, k):
    m, n = len(mat), len(mat[0])
    P = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m):
        for j in range(n):
            P[i + 1][j + 1] = mat[i][j] + P[i][j + 1] + P[i + 1][j] - P[i][j]
    out = [[0] * n for _ in range(m)]
    for i in range(m):
        for j in range(n):
            r1, c1, r2, c2 = max(0, i - k), max(0, j - k), min(m, i + k + 1), min(n, j + k + 1)
            out[i][j] = P[r2][c2] - P[r1][c2] - P[r2][c1] + P[r1][c1]
    return out


# ================================================================== 1074. Number of Submatrices That Sum to Target (Hard)
# https://leetcode.com/problems/number-of-submatrices-that-sum-to-target/
# Pattern: Fix two rows, then count subarrays with a hash map
# Idea: For every pair of top and bottom rows, add the columns between them into one array. Then
# count subarrays of that array with the target sum using running sums and a dictionary. It reduces
# a two dimensional problem to many one dimensional ones, much as PCA reduces dimensions.

def num_submatrix_sum_target(matrix, target):
    m, n = len(matrix), len(matrix[0])
    count = 0
    for top in range(m):
        cols = [0] * n
        for bottom in range(top, m):
            for j in range(n):
                cols[j] += matrix[bottom][j]
            seen = {0: 1}
            running = 0
            for v in cols:
                running = running + v
                count = count + seen.get(running - target, 0)
                seen[running] = seen.get(running, 0) + 1
    return count


if __name__ == "__main__":
    results = []
    results.append(check("867. Transpose Matrix", [('transpose([[1, 2, 3], [4, 5, 6]])', [[1, 4], [2, 5], [3, 6]]), ('transpose([[1]])', [[1]])]))
    results.append(check("48. Rotate Image", [('rotate([[1, 2, 3], [4, 5, 6], [7, 8, 9]])', [[7, 4, 1], [8, 5, 2], [9, 6, 3]]), ('rotate([[1, 2], [3, 4]])', [[3, 1], [4, 2]])]))
    results.append(check("2482. Difference Between Ones and Zeros in Row and Column", [('ones_minus_zeros([[0, 1, 1], [1, 0, 1], [0, 0, 1]])', [[0, 0, 4], [0, 0, 4], [-2, -2, 2]]), ('ones_minus_zeros([[1, 1, 1], [1, 1, 1]])', [[5, 5, 5], [5, 5, 5]])]))
    results.append(check("1329. Sort the Matrix Diagonally", [('diagonal_sort([[3, 3, 1, 1], [2, 2, 1, 2], [1, 1, 1, 2]])', [[1, 1, 1, 1], [1, 2, 2, 2], [1, 2, 3, 3]])]))
    results.append(check("1314. Matrix Block Sum", [('matrix_block_sum([[1, 2, 3], [4, 5, 6], [7, 8, 9]], 1)', [[12, 21, 16], [27, 45, 33], [24, 39, 28]])]))
    results.append(check("1074. Number of Submatrices That Sum to Target", [('num_submatrix_sum_target([[0, 1, 0], [1, 1, 1], [0, 1, 0]], 0)', 4), ('num_submatrix_sum_target([[1, -1], [-1, 1]], 0)', 5)]))
    if all(results):
        print("Every solution passes its tests.")
