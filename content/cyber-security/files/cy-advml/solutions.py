# 1.2 Attacks on machine learning and their defences
# Model solutions. Try practice.py first.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.


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


# ================================================================== task 1: Certified radius of a linear model
# Write certified_radius(w, b, x) that returns |w · x + b| / Σ |wi| rounded to 4 decimals: the
# largest change per feature that can never flip the decision.
# Why it works: A radius of 0 means the point sits on the boundary, so any change can flip it.
# Defenders like large radii for important inputs.

def certified_radius(w, b, x):
    z = b
    for wi, xi in zip(w, x):
        z += wi * xi
    l1 = 0
    for wi in w:
        l1 += abs(wi)
    return round(abs(z) / l1, 4)


# ================================================================== task 2: One FGSM step against a linear score
# Write fgsm_step(x, w, eps) that returns a new list where each feature moves by eps against the
# sign of its weight (xi − eps · sign(wi)), clipped to the range 0 to 1, each value rounded to 4
# decimals. A weight of 0 leaves the feature unchanged.
# Why it works: Clipping keeps the input valid, just as a real attacker must keep an image in the 0
# to 255 range or keep a program runnable.

def fgsm_step(x, w, eps):
    out = []
    for xi, wi in zip(x, w):
        s = (wi > 0) - (wi < 0)
        v = xi - eps * s
        v = min(1.0, max(0.0, v))
        out.append(round(v, 4))
    return out


# ================================================================== task 3: Membership advantage of a threshold attack
# member_conf and other_conf are lists of model confidences for members and non members. Write
# membership_adv(member_conf, other_conf, threshold) that guesses "member" when a confidence is at
# least the threshold and returns TPR − FPR rounded to 4 decimals.
# Why it works: Privacy audits run attacks like this one to estimate how much a model leaks before
# it is released.

def membership_adv(member_conf, other_conf, threshold):
    tp = 0
    for c in member_conf:
        if c >= threshold:
            tp += 1
    fp = 0
    for c in other_conf:
        if c >= threshold:
            fp += 1
    return round(tp / len(member_conf) - fp / len(other_conf), 4)


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Certified radius of a linear model", [('certified_radius([2.0, 1.5, 1.8, 1.2, -2.5], -2.0, [0.8, 0.7, 0.9, 0.6, 0.0])', 0.3322), ('certified_radius([1.6, 1.2], -1.4, [0.75, 0.7])', 0.2286), ('certified_radius([1.0, -1.0], 0.0, [0.5, 0.5])', 0.0)]))
    results.append(check("Task 2: One FGSM step against a linear score", [('fgsm_step([0.75, 0.7], [1.6, 1.2], 0.25)', [0.5, 0.45]), ('fgsm_step([0.8, 0.0], [2.0, -2.5], 0.1)', [0.7, 0.1]), ('fgsm_step([0.05, 0.5, 0.95], [1.0, 0.0, -1.0], 0.1)', [0.0, 0.5, 1.0])]))
    results.append(check("Task 3: Membership advantage of a threshold attack", [('membership_adv([1.0, 1.0, 0.9, 0.6], [1.0, 0.5, 0.4, 0.3], 0.9)', 0.5), ('membership_adv([0.5, 0.6], [0.5, 0.6], 0.55)', 0.0), ('membership_adv([0.9, 0.95, 0.99], [0.2, 0.3, 0.97], 0.9)', 0.6667)]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
