# 1.2 Multi armed bandits
# Model solutions. Try practice.py first.
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


# ================================================================== task 1: Running estimates
# Write running_estimates(rewards) that returns the running average after each reward, using Q ← Q +
# (r − Q)/n, each rounded to 3 decimals.
# Why it works: The update never stores old rewards, which matters when a bandit runs for millions
# of rounds.

def running_estimates(rewards):
    Q, out = 0.0, []
    for n, r in enumerate(rewards, start=1):
        Q = Q + (r - Q) / n
        out.append(round(Q, 3))
    return out


# ================================================================== task 2: A UCB choice
# Write ucb_choose(Q, N, t, c). Q and N are lists of estimates and pull counts. If any arm has N = 0
# return the first such index. Otherwise return the index with the highest Q + c √(ln t / N), the
# first one on a tie.
# Why it works: The first test is the worked example: the less certain arm wins with c = 1. With a
# small c = 0.1 the bonus barely matters and the higher estimate wins.

import math


def ucb_choose(Q, N, t, c):
    for i, n in enumerate(N):
        if n == 0:
            return i
    scores = [q + c * math.sqrt(math.log(t) / n) for q, n in zip(Q, N)]
    return scores.index(max(scores))


# ================================================================== task 3: Long run reward of epsilon greedy
# Write eps_greedy_value(means, eps): the expected reward per pull of ε greedy once it knows which
# arm is best. With chance 1 − ε it pulls the best arm, and with chance ε a uniformly random arm.
# Round to 4 decimals.
# Why it works: The first test gives 0.768, so even a perfect ε greedy loses 0.032 per pull against
# the best arm’s 0.8. That is why ε is often lowered over time.

def eps_greedy_value(means, eps):
    best = max(means)
    avg = sum(means) / len(means)
    return round((1 - eps) * best + eps * avg, 4)


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Running estimates", [('running_estimates([4, 6, 5, 9, 1])', [4.0, 5.0, 5.0, 6.0, 5.0]), ('running_estimates([1, 0, 0])', [1.0, 0.5, 0.333])]))
    results.append(check("Task 2: A UCB choice", [('ucb_choose([0.6, 0.5], [25, 4], 100, 1.0)', 1), ('ucb_choose([0.6, 0.5], [25, 4], 100, 0.1)', 0), ('ucb_choose([0.9, 0.1, 0.5], [3, 0, 2], 6, 1.0)', 1)]))
    results.append(check("Task 3: Long run reward of epsilon greedy", [('eps_greedy_value([0.2, 0.5, 0.8, 0.3, 0.6], 0.1)', 0.768), ('eps_greedy_value([1, 0], 0.5)', 0.75), ('eps_greedy_value([0.4, 0.4], 0.3)', 0.4)]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
