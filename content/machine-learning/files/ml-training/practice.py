# 1.3 Training deep networks: optimisers, normalisation and regularisation
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


# ================================================================== task 1: A momentum update
# Write momentum_update(w, v, g, lr, beta) that applies one momentum step, v = beta v + g and then w
# = w − lr v, and returns [new w, new v], each rounded to 4 decimals.
# Hint: Update the velocity first, then move the weight by the learning rate times the velocity.

def momentum_update(w, v, g, lr, beta):
    # your code here
    pass


# ================================================================== task 2: One Adam step
# Write adam_step(w, m, v, g, t, lr=0.001, b1=0.9, b2=0.999, eps=1e-8) that updates m and v, applies
# bias correction for step t, updates w, and returns [w, m, v], each rounded to 6 decimals.
# Hint: Update both averages, divide each by 1 minus beta to the power t, then step by lr times m
# hat over the root of v hat.

def adam_step(w, m, v, g, t, lr=0.001, b1=0.9, b2=0.999, eps=1e-8):
    # your code here
    pass


# ================================================================== task 3: A batch normalisation forward pass
# Write batchnorm_forward(values, gamma, beta, eps=1e-5) for one feature over a batch: subtract the
# mean, divide by √(variance + eps) using the population variance, then multiply by gamma and add
# beta. Return the list rounded to 4 decimals.
# Hint: Find the mean and the population variance, normalise each value, then scale and shift.

def batchnorm_forward(values, gamma, beta, eps=1e-5):
    # your code here
    pass


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: A momentum update", [('momentum_update(1.0, 0.0, 2.0, 0.1, 0.9)', [0.8, 2.0]), ('momentum_update(0.8, 2.0, 1.0, 0.1, 0.9)', [0.52, 2.8])]))
    results.append(check("Task 2: One Adam step", [('adam_step(1.0, 0.0, 0.0, 0.5, 1, lr=0.1)', [0.9, 0.05, 0.00025]), ('adam_step(0.0, 0.0, 0.0, -4.0, 1, lr=0.01)', [0.01, -0.4, 0.016])]))
    results.append(check("Task 3: A batch normalisation forward pass", [('batchnorm_forward([1.0, 2.0, 3.0], 1.0, 0.0)', [-1.2247, 0.0, 1.2247]), ('batchnorm_forward([2.0, 2.0, 2.0], 2.0, 1.0)', [1.0, 1.0, 1.0]), ('batchnorm_forward([0.0, 10.0], 1.0, 5.0)', [4.0, 6.0])]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
