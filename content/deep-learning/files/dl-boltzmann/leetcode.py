# 3.4 Energy based models: Hopfield networks, Boltzmann machines and RBMs
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


# ================================================================== 289. Game of Life (Medium)
# https://leetcode.com/problems/game-of-life/
# Pattern: Update every cell from its neighbours at the same time, encoding old and new state in one
# number
# Idea: A Hopfield update looks at its neighbours and sets a new state. Game of Life updates all
# cells at once (synchronously), so the new value must not be seen before every cell has read the
# old one. Store old state in bit 0 and new state in bit 1, then shift. O(mn) time, O(1) extra
# space.

def gameOfLife(board):
    m, n = len(board), len(board[0])
    for i in range(m):
        for j in range(n):
            live = 0
            for di in (-1, 0, 1):
                for dj in (-1, 0, 1):
                    if (di or dj) and 0 <= i + di < m and 0 <= j + dj < n:
                        live += board[i + di][j + dj] & 1      # bit 0 is the old state
            if board[i][j] & 1 and live in (2, 3) or not board[i][j] & 1 and live == 3:
                board[i][j] |= 2                               # bit 1 is the new state
    for i in range(m):
        for j in range(n):
            board[i][j] >>= 1
    return board


# ================================================================== 191. Number of 1 Bits (Easy)
# https://leetcode.com/problems/number-of-1-bits/
# Pattern: Clear the lowest set bit with n & (n - 1) until n is 0
# Idea: A binary state vector of units can be packed into one integer. Counting its on units is
# counting 1 bits. n & (n minus 1) removes exactly one set bit, so the loop runs once per on unit.

def hammingWeight(n):
    count = 0
    while n:
        n &= n - 1          # drop the lowest 1 bit
        count += 1
    return count


# ================================================================== 338. Counting Bits (Easy)
# https://leetcode.com/problems/counting-bits/
# Pattern: Reuse smaller answers: bits(i) = bits(i >> 1) + (i & 1)
# Idea: Enumerating every state of a small Boltzmann machine walks through all integers 0 to 2^n
# minus 1. The number of on units in i equals that of i with its last bit removed, plus that last
# bit. O(n) time.

def countBits(n):
    ans = [0] * (n + 1)
    for i in range(1, n + 1):
        ans[i] = ans[i >> 1] + (i & 1)
    return ans


# ================================================================== 476. Number Complement (Easy)
# https://leetcode.com/problems/number-complement/
# Pattern: Flip every bit below the highest set bit with a mask of ones
# Idea: Flipping every unit of a binary state, like the spurious negative of a Hopfield memory.
# Build a mask with as many ones as n has bits and xor with it.

def findComplement(num):
    mask = (1 << num.bit_length()) - 1
    return num ^ mask


# ================================================================== 1611. Minimum One Bit Operations to Make Integers Zero (Hard)
# https://leetcode.com/problems/minimum-one-bit-operations-to-make-integers-zero/
# Pattern: The allowed moves walk the Gray code, so the answer is the inverse Gray code of n
# Idea: Each allowed operation changes one bit, so the states form a path in which neighbours differ
# in one unit, exactly like a single unit Gibbs or Hopfield update. The order of that path is the
# Gray code. The number of steps from n to 0 is the position of n in the Gray code, found by xoring
# all right shifts of n. O(log n).

def minimumOneBitOperations(n):
    res = 0
    while n:
        res ^= n            # inverse Gray code: xor of all right shifts
        n >>= 1
    return res


if __name__ == "__main__":
    results = []
    results.append(check("289. Game of Life", [('gameOfLife([[0, 1, 0], [0, 0, 1], [1, 1, 1], [0, 0, 0]])', [[0, 0, 0], [1, 0, 1], [0, 1, 1], [0, 1, 0]]), ('gameOfLife([[1, 1], [1, 0]])', [[1, 1], [1, 1]]), ('gameOfLife([[1]])', [[0]])]))
    results.append(check("191. Number of 1 Bits", [('hammingWeight(11)', 3), ('hammingWeight(128)', 1), ('hammingWeight(2147483645)', 30), ('hammingWeight(0)', 0)]))
    results.append(check("338. Counting Bits", [('countBits(2)', [0, 1, 1]), ('countBits(5)', [0, 1, 1, 2, 1, 2]), ('countBits(0)', [0])]))
    results.append(check("476. Number Complement", [('findComplement(5)', 2), ('findComplement(1)', 0), ('findComplement(10)', 5), ('findComplement(2147483647)', 0)]))
    results.append(check("1611. Minimum One Bit Operations to Make Integers Zero", [('minimumOneBitOperations(3)', 2), ('minimumOneBitOperations(6)', 4), ('minimumOneBitOperations(0)', 0), ('minimumOneBitOperations(9)', 14), ('minimumOneBitOperations(333)', 393)]))
    if all(results):
        print("Every solution passes its tests.")
