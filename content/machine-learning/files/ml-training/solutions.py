# 1.3 Training deep networks: optimisers, normalisation and regularisation
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


# ================================================================== task 1: A momentum update
# Write momentum_update(w, v, g, lr, beta) that applies one momentum step, v = beta v + g and then w
# = w − lr v, and returns [new w, new v], each rounded to 4 decimals.
# Why it works: With a steady gradient the velocity settles at g/(1 − beta), 10 times g for beta =
# 0.9.

def momentum_update(w, v, g, lr, beta):
    v = beta * v + g
    w = w - lr * v
    return [round(w, 4), round(v, 4)]


# ================================================================== task 2: One Adam step
# Write adam_step(w, m, v, g, t, lr=0.001, b1=0.9, b2=0.999, eps=1e-8) that updates m and v, applies
# bias correction for step t, updates w, and returns [w, m, v], each rounded to 6 decimals.
# Why it works: On the first step m hat is g and v hat is g squared, so the step is lr times the
# sign of g, whatever the size of g.

def adam_step(w, m, v, g, t, lr=0.001, b1=0.9, b2=0.999, eps=1e-8):
    m = b1 * m + (1 - b1) * g
    v = b2 * v + (1 - b2) * g * g
    m_hat = m / (1 - b1 ** t)
    v_hat = v / (1 - b2 ** t)
    w = w - lr * m_hat / (v_hat ** 0.5 + eps)
    return [round(w, 6), round(m, 6), round(v, 6)]


# ================================================================== task 3: A batch normalisation forward pass
# Write batchnorm_forward(values, gamma, beta, eps=1e-5) for one feature over a batch: subtract the
# mean, divide by √(variance + eps) using the population variance, then multiply by gamma and add
# beta. Return the list rounded to 4 decimals.
# Why it works: eps stops a division by zero when every value in the batch is the same, as in the
# second test.

def batchnorm_forward(values, gamma, beta, eps=1e-5):
    n = len(values)
    mean = sum(values) / n
    var = sum((x - mean) ** 2 for x in values) / n
    return [round(gamma * (x - mean) / (var + eps) ** 0.5 + beta + 0.0, 4) for x in values]


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: A momentum update", [('momentum_update(1.0, 0.0, 2.0, 0.1, 0.9)', [0.8, 2.0]), ('momentum_update(0.8, 2.0, 1.0, 0.1, 0.9)', [0.52, 2.8])]))
    results.append(check("Task 2: One Adam step", [('adam_step(1.0, 0.0, 0.0, 0.5, 1, lr=0.1)', [0.9, 0.05, 0.00025]), ('adam_step(0.0, 0.0, 0.0, -4.0, 1, lr=0.01)', [0.01, -0.4, 0.016])]))
    results.append(check("Task 3: A batch normalisation forward pass", [('batchnorm_forward([1.0, 2.0, 3.0], 1.0, 0.0)', [-1.2247, 0.0, 1.2247]), ('batchnorm_forward([2.0, 2.0, 2.0], 2.0, 1.0)', [1.0, 1.0, 1.0]), ('batchnorm_forward([0.0, 10.0], 1.0, 5.0)', [4.0, 6.0])]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
