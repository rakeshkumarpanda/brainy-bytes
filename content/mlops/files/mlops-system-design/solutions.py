# 4.1 Designing an ML system end to end
# Model solutions. Try practice.py first.
# From the Brainy Bytes MLOps subject. Run it with: python3 <this file>
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


# ================================================================== task 1: Replicas from traffic
# Write replicas_needed(daily_requests, peak_factor, per_replica, load). Compute the peak requests
# per second (daily requests / 86,400 × peak factor) and return the number of replicas needed so
# that each runs at no more than load of its capacity per_replica. Round up.
# Why it works: The tiny 1e−9 guards against floating point results such as 1.0000000002 turning
# into 2 replicas. Real systems also add one spare replica per zone.

import math


def replicas_needed(daily_requests, peak_factor, per_replica, load):
    peak = daily_requests / 86_400 * peak_factor
    return math.ceil(peak / (per_replica * load) - 1e-9)


# ================================================================== task 2: A/B test sample size
# Write ab_sample_size(p, delta) for a base rate p and a lift delta. Use p̄ = p + delta / 2, z
# values 1.96 and 0.8416, and return the users needed per group, n = (1.96 + 0.8416)² · 2p̄(1 − p̄)
# / delta², rounded up.
# Why it works: Notice how the answer explodes for small lifts: detecting 0.5 points on a 5 percent
# rate needs over 31,000 users per group.

import math


def ab_sample_size(p, delta):
    p_bar = p + delta / 2
    return math.ceil((1.96 + 0.8416) ** 2 * 2 * p_bar * (1 - p_bar) / delta ** 2)


# ================================================================== task 3: A canary guardrail check
# Write canary_check(stages, guard, min_requests). stages is a list of (requests, errors) pairs, one
# per rollout step. Return the index of the first stage whose error rate is above guard and that has
# at least min_requests requests, or −1 if every stage passes.
# Why it works: The minimum request count stops a single unlucky error in a tiny stage from
# triggering a rollback. Production systems use a statistical test instead of a fixed count.

def canary_check(stages, guard, min_requests):
    for i, (requests, errors) in enumerate(stages):
        if requests >= min_requests and errors / requests > guard:
            return i
    return -1


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Replicas from traffic", [('replicas_needed(200_000_000, 3, 100, 0.6)', 116), ('replicas_needed(86_400, 1, 1, 1.0)', 1), ('replicas_needed(864_000, 2, 5, 0.5)', 8), ('replicas_needed(0, 3, 100, 0.6)', 0)]))
    results.append(check("Task 2: A/B test sample size", [('ab_sample_size(0.05, 0.005)', 31235), ('ab_sample_size(0.10, 0.02)', 3843), ('ab_sample_size(0.5, 0.1)', 389)]))
    results.append(check("Task 3: A canary guardrail check", [('canary_check([(1000, 24), (5000, 120)], 0.012, 500)', 0), ('canary_check([(1000, 6), (5000, 31), (25000, 150)], 0.012, 500)', -1), ('canary_check([(100, 5), (5000, 80)], 0.012, 500)', 1), ('canary_check([], 0.012, 500)', -1)]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
