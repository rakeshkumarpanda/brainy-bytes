# 1.1 Agents, rewards and returns
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


# ================================================================== task 1: Discounted return
# Write discounted_return(rewards, gamma) that returns r1 + γ r2 + γ2 r3 + ... for the list rewards,
# rounded to 4 decimals.
# Why it works: Going backwards needs one multiplication per reward and no powers of gamma.

def discounted_return(rewards, gamma):
    G = 0.0
    for r in reversed(rewards):
        G = r + gamma * G
    return round(G, 4)


# ================================================================== task 2: Return from every step
# Write returns_per_step(rewards, gamma) that returns the list [G1, G2, ...], the return from each
# step to the end, each rounded to 3 decimals.
# Why it works: Monte Carlo learning (a later chapter) uses exactly these per step returns as
# targets for every state visited.

def returns_per_step(rewards, gamma):
    G = 0.0
    out = []
    for r in reversed(rewards):
        G = r + gamma * G
        out.append(round(G, 3))
    return out[::-1]


# ================================================================== task 3: Corridor simulator
# Write corridor_run(n, start, actions). Cells are 0 to n − 1. Each action is −1 (left) or 1
# (right). A move into cell n − 1 gives +10 and ends the episode, a move into cell 0 gives −10 and
# ends it, and any other move gives −1. Ignore actions after the end. Return [total reward, steps
# taken, final cell].
# Why it works: The first test replays the random episode from the lesson: total 4 after 7 steps,
# ending on the treasure.

def corridor_run(n, start, actions):
    pos, total, steps = start, 0, 0
    for a in actions:
        pos += a
        steps += 1
        if pos == n - 1:
            total += 10
            break
        if pos == 0:
            total -= 10
            break
        total -= 1
    return [total, steps, pos]


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Discounted return", [('discounted_return([-1, -1, -1, 10], 0.9)', 4.58), ('discounted_return([-1, -1, -1, 10], 1.0)', 7.0), ('discounted_return([5], 0.5)', 5.0), ('discounted_return([1, 2, 4], 0.5)', 3.0)]))
    results.append(check("Task 2: Return from every step", [('returns_per_step([-1, -1, -1, 10], 0.9)', [4.58, 6.2, 8.0, 10.0]), ('returns_per_step([1, 1, 1], 0.5)', [1.75, 1.5, 1.0])]))
    results.append(check("Task 3: Corridor simulator", [('corridor_run(6, 2, [1, -1, -1, 1, 1, 1, 1])', [4, 7, 5]), ('corridor_run(6, 2, [-1, -1, 1, 1])', [-11, 2, 0]), ('corridor_run(6, 2, [1, 1])', [-2, 2, 4])]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
