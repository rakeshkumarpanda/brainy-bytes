# 1.1 Agents, rewards and returns
# Practice tasks. Fill in each function, then run this file.
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
# Hint: Work backwards: G = r + gamma times G.

def discounted_return(rewards, gamma):
    # your code here
    pass


# ================================================================== task 2: Return from every step
# Write returns_per_step(rewards, gamma) that returns the list [G1, G2, ...], the return from each
# step to the end, each rounded to 3 decimals.
# Hint: Collect G while walking backwards, then reverse the list.

def returns_per_step(rewards, gamma):
    # your code here
    pass


# ================================================================== task 3: Corridor simulator
# Write corridor_run(n, start, actions). Cells are 0 to n − 1. Each action is −1 (left) or 1
# (right). A move into cell n − 1 gives +10 and ends the episode, a move into cell 0 gives −10 and
# ends it, and any other move gives −1. Ignore actions after the end. Return [total reward, steps
# taken, final cell].
# Hint: Move, then check for the two ends before charging the normal move cost.

def corridor_run(n, start, actions):
    # your code here
    pass


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Discounted return", [('discounted_return([-1, -1, -1, 10], 0.9)', 4.58), ('discounted_return([-1, -1, -1, 10], 1.0)', 7.0), ('discounted_return([5], 0.5)', 5.0), ('discounted_return([1, 2, 4], 0.5)', 3.0)]))
    results.append(check("Task 2: Return from every step", [('returns_per_step([-1, -1, -1, 10], 0.9)', [4.58, 6.2, 8.0, 10.0]), ('returns_per_step([1, 1, 1], 0.5)', [1.75, 1.5, 1.0])]))
    results.append(check("Task 3: Corridor simulator", [('corridor_run(6, 2, [1, -1, -1, 1, 1, 1, 1])', [4, 7, 5]), ('corridor_run(6, 2, [-1, -1, 1, 1])', [-11, 2, 0]), ('corridor_run(6, 2, [1, 1])', [-2, 2, 4])]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
