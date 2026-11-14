# 3.2 Policy gradients, actor critic and PPO
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


# ================================================================== task 1: The softmax log gradient
# Write softmax_log_grad(prefs, a) that returns the gradient of ln π(a) with respect to each
# preference for a softmax policy: one hot(a) minus the probabilities. Round each value to 4
# decimals.
# Hint: Compute stable softmax probabilities, then subtract them from the one hot vector.

def softmax_log_grad(prefs, a):
    # your code here
    pass


# ================================================================== task 2: Generalised advantage estimation
# Write gae(rewards, values, gamma, lam) for one episode that ends after the last reward. values has
# one more entry than rewards: the last one is the value after the final step and is 0 at the end of
# an episode. Return the advantages, each rounded to 4 decimals.
# Hint: Work backwards: At = δt + γλAt+1.

def gae(rewards, values, gamma, lam):
    # your code here
    pass


# ================================================================== task 3: The PPO clipped objective
# Write ppo_objective(ratios, advantages, eps) that returns the average over samples of min(r A,
# clip(r, 1 − eps, 1 + eps) A), rounded to 4 decimals.
# Hint: Clip each ratio, compute both terms, keep the smaller, then average.

def ppo_objective(ratios, advantages, eps):
    # your code here
    pass


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: The softmax log gradient", [('softmax_log_grad([0.0, 0.0], 1)', [-0.5, 0.5]), ('softmax_log_grad([1.0, 0.0], 0)', [0.2689, -0.2689]), ('softmax_log_grad([0.0, 0.0, 0.0, 0.0], 2)', [-0.25, -0.25, 0.75, -0.25])]))
    results.append(check("Task 2: Generalised advantage estimation", [('gae([0, 1], [0.5, 0.8, 0.0], 0.9, 0.8)', [0.364, 0.2]), ('gae([1, 1, 1], [0, 0, 0, 0], 1.0, 1.0)', [3.0, 2.0, 1.0]), ('gae([1, 1], [0, 0, 0], 1.0, 0.0)', [1.0, 1.0])]))
    results.append(check("Task 3: The PPO clipped objective", [('ppo_objective([1.3], [2.0], 0.2)', 2.4), ('ppo_objective([0.7], [-1.0], 0.2)', -0.8), ('ppo_objective([1.0, 1.5, 0.5], [1.0, 1.0, 1.0], 0.2)', 0.9)]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
