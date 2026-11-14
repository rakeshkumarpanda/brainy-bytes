# 3.2 Generative adversarial networks
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


# ================================================================== 292. Nim Game (Easy)
# https://leetcode.com/problems/nim-game/
# Pattern: You lose exactly when the number of stones is a multiple of 4
# Idea: Whatever you take (1 to 3), your opponent can make the total of the round 4. So multiples of
# 4 are losing positions for the player to move. Two players who each play their best against the
# other is the same setting as the GAN game.

def can_win_nim(n):
    return n % 4 != 0


# ================================================================== 486. Predict the Winner (Medium)
# https://leetcode.com/problems/predict-the-winner/
# Pattern: Minimax on intervals: best lead = max(take left minus their best lead, take right minus
# their best lead)
# Idea: Let lead(i, j) be the most the player to move can get ahead by on nums[i..j]. Taking an end
# gives that number minus the opponent’s best lead on what remains. This is a minimax game: each
# player assumes the other plays as well as possible, as the generator and the discriminator do.

def predict_the_winner(nums):
    n = len(nums)
    diff = nums[:]
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            diff[i] = max(nums[i] - diff[i + 1], nums[j] - diff[i])
    return diff[0] >= 0


# ================================================================== 877. Stone Game (Medium)
# https://leetcode.com/problems/stone-game/
# Pattern: Same interval minimax as Predict the Winner (and the first player always wins with an
# even count)
# Idea: Compute the best lead of the player to move on piles[i..j] from shorter intervals. With an
# even number of piles and an odd total, the first player can always take all the even positions or
# all the odd ones, so the answer is always true, but the dynamic programming shows why.

def stone_game(piles):
    n = len(piles)
    lead = piles[:]
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            lead[i] = max(piles[i] - lead[i + 1], piles[j] - lead[i])
    return lead[0] > 0


# ================================================================== 375. Guess Number Higher or Lower II (Medium)
# https://leetcode.com/problems/guess-number-higher-or-lower-ii/
# Pattern: cost(lo, hi) = min over guesses g of g + max(cost(lo, g minus 1), cost(g + 1, hi))
# Idea: You pick the guess (min) and the number is chosen to hurt you most (max). Memoise the cost
# of every range. The min over your choices of the max over the opponent’s choices is exactly the
# min over G of the max over D in the GAN value.

from functools import lru_cache


def get_money_amount(n):
    @lru_cache(maxsize=None)
    def cost(lo, hi):
        if lo >= hi:
            return 0
        return min(g + max(cost(lo, g - 1), cost(g + 1, hi)) for g in range(lo, hi + 1))
    return cost(1, n)


# ================================================================== 1406. Stone Game III (Hard)
# https://leetcode.com/problems/stone-game-iii/
# Pattern: best[i] = max over taking 1, 2 or 3 stones of (stones taken minus best[next])
# Idea: Work backwards from the end. The player to move takes 1 to 3 values and then the opponent
# faces the rest, so the lead is what you took minus the opponent’s best lead. The sign of best[0]
# names the winner.

def stone_game_iii(values):
    n = len(values)
    best = [0] * (n + 3)
    for i in range(n - 1, -1, -1):
        take, best[i] = 0, float('-inf')
        for k in range(3):
            if i + k < n:
                take += values[i + k]
                best[i] = max(best[i], take - best[i + k + 1])
    if best[0] > 0:
        return 'Alice'
    return 'Bob' if best[0] < 0 else 'Tie'


if __name__ == "__main__":
    results = []
    results.append(check("292. Nim Game", [('can_win_nim(4)', False), ('can_win_nim(1)', True), ('can_win_nim(7)', True)]))
    results.append(check("486. Predict the Winner", [('predict_the_winner([1, 5, 2])', False), ('predict_the_winner([1, 5, 233, 7])', True)]))
    results.append(check("877. Stone Game", [('stone_game([5, 3, 4, 5])', True), ('stone_game([3, 7, 2, 3])', True)]))
    results.append(check("375. Guess Number Higher or Lower II", [('get_money_amount(10)', 16), ('get_money_amount(1)', 0), ('get_money_amount(2)', 1)]))
    results.append(check("1406. Stone Game III", [('stone_game_iii([1, 2, 3, 7])', 'Bob'), ('stone_game_iii([1, 2, 3, -9])', 'Alice'), ('stone_game_iii([1, 2, 3, 6])', 'Tie')]))
    if all(results):
        print("Every solution passes its tests.")
