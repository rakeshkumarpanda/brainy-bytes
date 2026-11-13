# 2.2 Monte Carlo and temporal difference learning
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


# ================================================================== task 1: A TD(0) update
# Write td0_update(V, s, r, s2, alpha, gamma). V is a dictionary of values. Return the new value of
# V[s] after one TD(0) update, rounded to 4 decimals. Treat a next state s2 that is missing from V
# as terminal (value 0).
# Hint: Target r + gamma V(s2), then move V(s) a fraction alpha towards it.

def td0_update(V, s, r, s2, alpha, gamma):
    # your code here
    pass


# ================================================================== task 2: First visit Monte Carlo
# Write mc_first_visit(episodes). Each episode is a list of [state, reward] pairs, where the reward
# follows that state. With γ = 1, return a dictionary from each state to the average of the returns
# after its first visit in each episode, rounded to 3 decimals.
# Hint: Walk each episode backwards. The last time you write a state’s return going backwards is its
# first visit.

def mc_first_visit(episodes):
    # your code here
    pass


# ================================================================== task 3: n step return
# Write n_step_return(rewards, v_boot, gamma): the n step return Σ γk rewards[k] + γn v_boot, where
# n is the number of rewards. Round to 4 decimals.
# Hint: Start from the bootstrap value and fold the rewards in backwards.

def n_step_return(rewards, v_boot, gamma):
    # your code here
    pass


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: A TD(0) update", [('td0_update({"a": 0.5, "b": 0.7}, "a", 0, "b", 0.1, 1.0)', 0.52), ('td0_update({"a": 2.0, "b": 2.0}, "a", 1, "b", 0.5, 0.9)', 2.4), ('td0_update({"e": 0.5}, "e", 1, "end", 0.1, 1.0)', 0.55)]))
    results.append(check("Task 2: First visit Monte Carlo", [('mc_first_visit([[["A", 0], ["B", 0]]] + [[["B", 1]]] * 6 + [[["B", 0]]])', {'A': 0.0, 'B': 0.75}), ('mc_first_visit([[["x", 1], ["y", 2], ["x", 3]], [["y", 4]]])', {'x': 6.0, 'y': 4.5})]))
    results.append(check("Task 3: n step return", [('n_step_return([0, 0], 0.5, 0.9)', 0.405), ('n_step_return([1], 2.0, 0.9)', 2.8), ('n_step_return([1, 1, 1], 0.0, 0.5)', 1.75)]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
