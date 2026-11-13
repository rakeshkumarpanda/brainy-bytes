# 3.1 Function approximation and deep Q networks
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


# ================================================================== task 1: A semi gradient TD update
# Write semi_td_update(w, x, x2, r, done, alpha, gamma) for a linear value function. w, x and x2 are
# lists of equal length (weights, features of s and features of s′). Return the new weights as a
# list, each rounded to 4 decimals. If done is True the next value is 0.
# Why it works: Only the features of s appear in the gradient. Adding the features of s′ too would
# give the residual gradient method instead.

def semi_td_update(w, x, x2, r, done, alpha, gamma):
    v = sum(wi * xi for wi, xi in zip(w, x))
    v2 = 0.0 if done else sum(wi * xi for wi, xi in zip(w, x2))
    delta = r + gamma * v2 - v
    return [round(wi + alpha * delta * xi, 4) for wi, xi in zip(w, x)]


# ================================================================== task 2: DQN and Double DQN targets
# Write dqn_targets(rewards, dones, q_online_next, q_target_next, gamma, double). Each q list holds
# one list of action values per transition. If double is False, use the max of the target network’s
# values. If True, choose the action with the online values and take its target network value. Done
# transitions use just the reward. Return a list rounded to 4 decimals.
# Why it works: The first test matches the calculation problem: 3.25 for DQN against 2.35 for Double
# DQN, because the target network does not agree with the online network’s favourite action.

def dqn_targets(rewards, dones, q_online_next, q_target_next, gamma, double):
    out = []
    for r, d, qo, qt in zip(rewards, dones, q_online_next, q_target_next):
        if d:
            out.append(round(float(r), 4))
            continue
        nxt = qt[qo.index(max(qo))] if double else max(qt)
        out.append(round(r + gamma * nxt, 4))
    return out


# ================================================================== task 3: Dueling Q values
# Write dueling_q(v, adv) that combines a state value v and a list of advantages into Q values with
# Q = V + A − mean(A). Round each to 4 decimals.
# Why it works: Without subtracting the mean, adding any constant to V and removing it from every A
# would give the same Q, so the network could not tell them apart.

def dueling_q(v, adv):
    m = sum(adv) / len(adv)
    return [round(v + a - m, 4) for a in adv]


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: A semi gradient TD update", [('semi_td_update([0.5, 1.0], [1, 2], [1, 1], 1, False, 0.1, 0.9)', [0.485, 0.97]), ('semi_td_update([0.0, 0.0], [1, 0], [0, 1], 2, True, 0.5, 0.9)', [1.0, 0.0])]))
    results.append(check("Task 2: DQN and Double DQN targets", [('dqn_targets([1, 0], [False, True], [[2, 3], [5, 1]], [[2.5, 1.5], [4, 4]], 0.9, False)', [3.25, 0.0]), ('dqn_targets([1, 0], [False, True], [[2, 3], [5, 1]], [[2.5, 1.5], [4, 4]], 0.9, True)', [2.35, 0.0])]))
    results.append(check("Task 3: Dueling Q values", [('dueling_q(2, [1, -1, 3])', [2.0, 0.0, 4.0]), ('dueling_q(0.5, [0, 0])', [0.5, 0.5]), ('dueling_q(-1, [2, 4])', [-2.0, 0.0])]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
