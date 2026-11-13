# 3.3 RL in practice: models, offline data and RLHF
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


# ================================================================== task 1: The Bradley&ndash;Terry loss
# Write bt_loss(r_win, r_lose). Both are lists of reward model scores for the preferred and the
# rejected answer of each pair. Return the average of −ln σ(r_win − r_lose), rounded to 4 decimals.
# Why it works: When the reward model ranks a pair the wrong way round, as in the third test, the
# loss is large, about the size of the gap.

import math


def bt_loss(r_win, r_lose):
    total = 0.0
    for w, l in zip(r_win, r_lose):
        total += math.log(1 + math.exp(-(w - l)))
    return round(total / len(r_win), 4)


# ================================================================== task 2: The KL regularised policy
# Write kl_policy(pi_ref, rewards, beta) that returns the probabilities π(y) ∝ πref(y) er(y)/β, each
# rounded to 4 decimals.
# Why it works: The third test shows that equal rewards leave the reference policy unchanged,
# whatever β is.

import math


def kl_policy(pi_ref, rewards, beta):
    top = max(rewards)
    w = [p * math.exp((r - top) / beta) for p, r in zip(pi_ref, rewards)]
    z = sum(w)
    return [round(x / z, 4) for x in w]


# ================================================================== task 3: The DPO loss
# Write dpo_loss(logp_w, logp_l, ref_w, ref_l, beta). Each argument except beta is a list of log
# probabilities, one per pair: the policy and the reference, for the winner and the loser. Return
# the average DPO loss −ln σ(β[(logp_w − ref_w) − (logp_l − ref_l)]), rounded to 4 decimals.
# Why it works: At the start of training the policy equals the reference, every margin is 0 and the
# loss is ln 2 = 0.6931, as in the first test.

import math


def dpo_loss(logp_w, logp_l, ref_w, ref_l, beta):
    total = 0.0
    for pw, pl, rw, rl in zip(logp_w, logp_l, ref_w, ref_l):
        margin = beta * ((pw - rw) - (pl - rl))
        total += math.log(1 + math.exp(-margin))
    return round(total / len(logp_w), 4)


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: The Bradley&ndash;Terry loss", [('bt_loss([1.5], [0.5])', 0.3133), ('bt_loss([0.0, 2.0], [0.0, 0.0])', 0.41), ('bt_loss([0.0], [3.0])', 3.0486)]))
    results.append(check("Task 2: The KL regularised policy", [('kl_policy([0.5, 0.5], [1.0, 0.0], 1.0)', [0.7311, 0.2689]), ('kl_policy([0.5, 0.5], [1.0, 0.0], 0.5)', [0.8808, 0.1192]), ('kl_policy([0.2, 0.3, 0.5], [0.0, 0.0, 0.0], 0.1)', [0.2, 0.3, 0.5])]))
    results.append(check("Task 3: The DPO loss", [('dpo_loss([-1.0], [-1.0], [-1.0], [-1.0], 1.0)', 0.6931), ('dpo_loss([0.6931], [-0.6931], [0.0], [0.0], 1.0)', 0.2232), ('dpo_loss([-2.0, -1.0], [-1.0, -2.0], [-1.5, -1.5], [-1.5, -1.5], 0.5)', 0.7241)]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
