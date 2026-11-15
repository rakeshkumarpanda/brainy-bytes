# 2.1 Federated learning in full
# Practice tasks. Fill in each function, then run this file.
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


# ================================================================== task 1: FedAvg weighted average
# updates is a list of client weight lists, sizes the number of examples per client. Write
# fedavg_aggregate(updates, sizes) that returns the weighted average list, each value rounded to 4
# decimals.
# Hint: Divide each size by the total, then add weight times value for every position.

def fedavg_aggregate(updates, sizes):
    # your code here
    pass


# ================================================================== task 2: Secure aggregation masked value
# masks is a dictionary from pairs (a, b) with a < b to the mask they share. Write masked_value(i,
# x, masks, M) that returns x plus every mask where i is the first of the pair, minus every mask
# where i is the second, all mod M.
# Hint: Loop over the pairs. Add when i is first, subtract when i is second, then take % M.

def masked_value(i, x, masks, M):
    # your code here
    pass


# ================================================================== task 3: FedProx local training
# A client’s loss is (a/2)(w − c)2. Write fedprox_local(w, a, c, w_global, mu, lr, steps) that takes
# steps gradient steps on the FedProx objective, whose gradient is a(w − c) + mu(w − w_global), and
# returns w rounded to 4 decimals.
# Hint: Repeat steps times: compute the gradient with the proximal term, then move against it.

def fedprox_local(w, a, c, w_global, mu, lr, steps):
    # your code here
    pass


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: FedAvg weighted average", [('fedavg_aggregate([[1.2], [0.8], [2.0]], [50, 30, 20])', [1.24]), ('fedavg_aggregate([[1.0, 2.0], [3.0, 4.0]], [1, 1])', [2.0, 3.0]), ('fedavg_aggregate([[0.0, 10.0], [10.0, 0.0]], [3, 1])', [2.5, 7.5])]))
    results.append(check("Task 2: Secure aggregation masked value", [('masked_value(1, 12, {(1, 2): 37, (1, 3): 81, (2, 3): 56}, 100)', 30), ('masked_value(2, 5, {(1, 2): 37, (1, 3): 81, (2, 3): 56}, 100)', 24), ('masked_value(3, 8, {(1, 2): 37, (1, 3): 81, (2, 3): 56}, 100)', 71)]))
    results.append(check("Task 3: FedProx local training", [('fedprox_local(0.0, 4.0, 10.0, 0.0, 0.0, 0.1, 1)', 4.0), ('fedprox_local(0.0, 4.0, 10.0, 0.0, 1.0, 0.1, 50)', 8.0), ('fedprox_local(2.0, 2.0, 2.0, 0.0, 1.0, 0.2, 3)', 1.376)]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
