# 2.1 Dynamic programming: policy and value iteration
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


# ================================================================== task 1: Policy evaluation
# Write evaluate_policy(P, R, policy, gamma, theta). P[s][a] is a list of [chance, next state]
# pairs, R[s][a] the reward for taking a in s, and policy[s] the action taken in s. Sweep in place
# until the largest change is below theta. Return the values rounded to 3 decimals.
# Hint: For each state use only the action the policy picks.

def evaluate_policy(P, R, policy, gamma, theta):
    # your code here
    pass


# ================================================================== task 2: Greedy policy from values
# Write greedy_policy(P, R, V, gamma) that returns, for every state, the action with the largest
# R[s][a] + gamma Σ chance × V[next]. On a tie pick the lowest action number.
# Hint: Compute the action values for each state and take the first maximum.

def greedy_policy(P, R, V, gamma):
    # your code here
    pass


# ================================================================== task 3: Value iteration
# Write value_iteration_solve(P, R, gamma, theta) in the same format. Sweep v(s) ← maxa [R[s][a] +
# gamma Σ chance × v(next)] in place until the largest change is below theta. Return [values rounded
# to 3 decimals, greedy policy], with ties going to the lowest action.
# Hint: Same backup as policy evaluation, but with a max over actions.

def value_iteration_solve(P, R, gamma, theta):
    # your code here
    pass


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Policy evaluation", [('evaluate_policy([[[[1, 1]], [[1, 2]]], [[[1, 2]], [[1, 0]]], [[[1, 2]], [[1, 2]]]], [[0, 1], [5, 0], [0, 0]], [1, 1, 0], 0.9, 1e-9)', [1.0, 0.9, 0.0]), ('evaluate_policy([[[[1, 1]], [[1, 2]]], [[[1, 2]], [[1, 0]]], [[[1, 2]], [[1, 2]]]], [[0, 1], [5, 0], [0, 0]], [0, 0, 0], 0.9, 1e-9)', [4.5, 5.0, 0.0])]))
    results.append(check("Task 2: Greedy policy from values", [('greedy_policy([[[[1, 1]], [[1, 2]]], [[[1, 2]], [[1, 0]]], [[[1, 2]], [[1, 2]]]], [[0, 1], [5, 0], [0, 0]], [1.0, 0.9, 0.0], 0.9)', [1, 0, 0]), ('greedy_policy([[[[1, 1]], [[1, 2]]], [[[1, 2]], [[1, 0]]], [[[1, 2]], [[1, 2]]]], [[0, 1], [5, 0], [0, 0]], [4.5, 5.0, 0.0], 0.9)', [0, 0, 0])]))
    results.append(check("Task 3: Value iteration", [('value_iteration_solve([[[[1, 1]], [[1, 2]]], [[[1, 2]], [[1, 0]]], [[[1, 2]], [[1, 2]]]], [[0, 1], [5, 0], [0, 0]], 0.9, 1e-9)', [[4.5, 5.0, 0.0], [0, 0, 0]]), ('value_iteration_solve([[[[1, 1]], [[1, 2]]], [[[1, 2]], [[1, 0]]], [[[1, 2]], [[1, 2]]]], [[0, 1], [5, 0], [0, 0]], 0.1, 1e-9)', [[1.0, 5.0, 0.0], [1, 0, 0]])]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
