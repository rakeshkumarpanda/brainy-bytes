# 1.3 Markov decision processes and Bellman equations
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


# ================================================================== task 1: Distribution after k steps
# Write step_distribution(dist, P, k). dist is a list of probabilities over states and P a
# transition matrix (list of rows). Return the distribution after k steps, each entry rounded to 3
# decimals.
# Hint: Each step, the new chance of j is the sum over i of d[i] times P[i][j].

def step_distribution(dist, P, k):
    # your code here
    pass


# ================================================================== task 2: Values by repeated backups
# Write mrp_values(P, R, gamma, sweeps) that starts with all values 0 and repeats V ← R + γPV the
# given number of times. Return the values rounded to 3 decimals.
# Hint: Build the whole new list from the old one each sweep.

def mrp_values(P, R, gamma, sweeps):
    # your code here
    pass


# ================================================================== task 3: One step lookahead
# Write one_step_lookahead(P, R, V, gamma) for one state. P[a] is the list of next state chances for
# action a, R[a] its expected reward, and V the list of next state values. Return the list of action
# values R[a] + γ Σ P[a][s′] V[s′], each rounded to 3 decimals.
# Hint: One line per action: reward plus discounted expected next value.

def one_step_lookahead(P, R, V, gamma):
    # your code here
    pass


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Distribution after k steps", [('step_distribution([0, 0, 1], [[0.7, 0.2, 0.1], [0.3, 0.4, 0.3], [0.2, 0.4, 0.4]], 2)', [0.34, 0.36, 0.3]), ('step_distribution([1, 0], [[0.9, 0.1], [0.5, 0.5]], 1)', [0.9, 0.1]), ('step_distribution([1, 0], [[0.9, 0.1], [0.5, 0.5]], 50)', [0.833, 0.167])]))
    results.append(check("Task 2: Values by repeated backups", [('mrp_values([[0, 0.5, 0, 0.5, 0], [0, 0, 0.8, 0.2, 0], [0, 0, 0, 0.4, 0.6], [0.4, 0, 0, 0.6, 0], [0, 0, 0, 0, 1]], [-1, -2, 10, -1, 0], 0.9, 200)', [-0.138, 4.198, 9.179, -2.282, 0.0]), ('mrp_values([[0.6, 0.4], [0, 1]], [-1, 0], 0.9, 200)', [-2.174, 0.0]), ('mrp_values([[0, 1], [0, 1]], [5, 0], 0.5, 1)', [5.0, 0.0])]))
    results.append(check("Task 3: One step lookahead", [('one_step_lookahead([[1, 0], [0.5, 0.5]], [1, 2], [10, 0], 0.9)', [10.0, 6.5]), ('one_step_lookahead([[0, 1], [1, 0]], [-1, -1], [-20, -18], 1.0)', [-19.0, -21.0])]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
