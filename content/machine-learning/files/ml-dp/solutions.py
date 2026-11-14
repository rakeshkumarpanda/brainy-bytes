# 2.1 Dynamic programming: policy and value iteration
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


# ================================================================== task 1: Policy evaluation
# Write evaluate_policy(P, R, policy, gamma, theta). P[s][a] is a list of [chance, next state]
# pairs, R[s][a] the reward for taking a in s, and policy[s] the action taken in s. Sweep in place
# until the largest change is below theta. Return the values rounded to 3 decimals.
# Why it works: In the small test MDP, state 2 loops to itself with reward 0, so it plays the role
# of a terminal state with value 0.

def evaluate_policy(P, R, policy, gamma, theta):
    V = [0.0] * len(P)
    while True:
        delta = 0.0
        for s in range(len(P)):
            a = policy[s]
            v = R[s][a] + gamma * sum(p * V[s2] for p, s2 in P[s][a])
            delta = max(delta, abs(v - V[s]))
            V[s] = v
        if delta < theta:
            return [round(v, 3) for v in V]


# ================================================================== task 2: Greedy policy from values
# Write greedy_policy(P, R, V, gamma) that returns, for every state, the action with the largest
# R[s][a] + gamma Σ chance × V[next]. On a tie pick the lowest action number.
# Why it works: Feeding the values of policy [1, 1, 0] into this function gives [1, 0, 0], a better
# policy. Repeating evaluation and this step is policy iteration.

def greedy_policy(P, R, V, gamma):
    policy = []
    for s in range(len(P)):
        q = [R[s][a] + gamma * sum(p * V[s2] for p, s2 in P[s][a]) for a in range(len(P[s]))]
        policy.append(q.index(max(q)))
    return policy


# ================================================================== task 3: Value iteration
# Write value_iteration_solve(P, R, gamma, theta) in the same format. Sweep v(s) ← maxa [R[s][a] +
# gamma Σ chance × v(next)] in place until the largest change is below theta. Return [values rounded
# to 3 decimals, greedy policy], with ties going to the lowest action.
# Why it works: With γ = 0.9 it pays to wait one step for the 5 (worth 4.5 now). With γ = 0.1 the 5
# is worth only 0.5 from state 0, so taking the 1 at once is better.

def value_iteration_solve(P, R, gamma, theta):
    n = len(P)
    V = [0.0] * n

    def q_of(s, a):
        return R[s][a] + gamma * sum(p * V[s2] for p, s2 in P[s][a])

    while True:
        delta = 0.0
        for s in range(n):
            best = max(q_of(s, a) for a in range(len(P[s])))
            delta = max(delta, abs(best - V[s]))
            V[s] = best
        if delta < theta:
            break
    policy = []
    for s in range(n):
        q = [q_of(s, a) for a in range(len(P[s]))]
        policy.append(q.index(max(q)))
    return [[round(v, 3) for v in V], policy]


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Policy evaluation", [('evaluate_policy([[[[1, 1]], [[1, 2]]], [[[1, 2]], [[1, 0]]], [[[1, 2]], [[1, 2]]]], [[0, 1], [5, 0], [0, 0]], [1, 1, 0], 0.9, 1e-9)', [1.0, 0.9, 0.0]), ('evaluate_policy([[[[1, 1]], [[1, 2]]], [[[1, 2]], [[1, 0]]], [[[1, 2]], [[1, 2]]]], [[0, 1], [5, 0], [0, 0]], [0, 0, 0], 0.9, 1e-9)', [4.5, 5.0, 0.0])]))
    results.append(check("Task 2: Greedy policy from values", [('greedy_policy([[[[1, 1]], [[1, 2]]], [[[1, 2]], [[1, 0]]], [[[1, 2]], [[1, 2]]]], [[0, 1], [5, 0], [0, 0]], [1.0, 0.9, 0.0], 0.9)', [1, 0, 0]), ('greedy_policy([[[[1, 1]], [[1, 2]]], [[[1, 2]], [[1, 0]]], [[[1, 2]], [[1, 2]]]], [[0, 1], [5, 0], [0, 0]], [4.5, 5.0, 0.0], 0.9)', [0, 0, 0])]))
    results.append(check("Task 3: Value iteration", [('value_iteration_solve([[[[1, 1]], [[1, 2]]], [[[1, 2]], [[1, 0]]], [[[1, 2]], [[1, 2]]]], [[0, 1], [5, 0], [0, 0]], 0.9, 1e-9)', [[4.5, 5.0, 0.0], [0, 0, 0]]), ('value_iteration_solve([[[[1, 1]], [[1, 2]]], [[[1, 2]], [[1, 0]]], [[[1, 2]], [[1, 2]]]], [[0, 1], [5, 0], [0, 0]], 0.1, 1e-9)', [[1.0, 5.0, 0.0], [1, 0, 0]])]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
