# 2.3 SARSA and Q learning
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


# ================================================================== task 1: A Q learning update
# Write q_update(Q, s, a, r, s2, done, alpha, gamma). Q is a dictionary from state to a list of
# action values. Return the new Q[s][a] after one Q learning update, rounded to 4 decimals. If done
# is True the next value is 0.
# Why it works: Forgetting the done check is a classic bug: the agent then adds value after the
# episode has ended.

def q_update(Q, s, a, r, s2, done, alpha, gamma):
    nxt = 0.0 if done else max(Q[s2])
    return round(Q[s][a] + alpha * (r + gamma * nxt - Q[s][a]), 4)


# ================================================================== task 2: Three TD control targets
# Write control_target(method, q_next, a_next, r, eps, gamma). q_next is the list of next state
# action values and a_next the next action the agent will take. method is "q", "sarsa" or
# "expected". For "expected" use ε greedy probabilities: ε/n for every action plus 1 − ε for the
# first best action. Return the target rounded to 4 decimals.
# Why it works: The three tests use the same transition as the worked example: 3.7, 1.9 and 3.43.

def control_target(method, q_next, a_next, r, eps, gamma):
    if method == "q":
        nxt = max(q_next)
    elif method == "sarsa":
        nxt = q_next[a_next]
    else:
        n = len(q_next)
        best = q_next.index(max(q_next))
        nxt = sum((eps / n + (1 - eps if i == best else 0)) * v for i, v in enumerate(q_next))
    return round(r + gamma * nxt, 4)


# ================================================================== task 3: Epsilon greedy probabilities
# Write eps_greedy_probs(q, eps) that returns the probability of each action under ε greedy: every
# action gets ε/n, and the 1 − ε greedy share is split equally between all actions tied for the best
# value. Round each to 4 decimals.
# Why it works: Splitting ties evenly avoids always favouring the first action, which can bias
# exploration early on when every value is 0.

def eps_greedy_probs(q, eps):
    n = len(q)
    best = max(q)
    ties = [i for i, v in enumerate(q) if v == best]
    return [round(eps / n + ((1 - eps) / len(ties) if i in ties else 0), 4) for i in range(n)]


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: A Q learning update", [('q_update({"s": [2.0, 0.0], "t": [3.0, 1.0, 1.0]}, "s", 0, 1, "t", False, 0.5, 0.9)', 2.85), ('q_update({"s": [2.0, 0.0]}, "s", 1, 5, "end", True, 0.1, 0.9)', 0.5)]))
    results.append(check("Task 2: Three TD control targets", [('control_target("q", [3, 1, 1, 1], 1, 1, 0.2, 0.9)', 3.7), ('control_target("sarsa", [3, 1, 1, 1], 1, 1, 0.2, 0.9)', 1.9), ('control_target("expected", [3, 1, 1, 1], 1, 1, 0.2, 0.9)', 3.43)]))
    results.append(check("Task 3: Epsilon greedy probabilities", [('eps_greedy_probs([3, 1, 1, 1], 0.2)', [0.85, 0.05, 0.05, 0.05]), ('eps_greedy_probs([2, 2, 0], 0.3)', [0.45, 0.45, 0.1]), ('eps_greedy_probs([5, 1], 0.0)', [1.0, 0.0])]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
