# 3.1 Autoencoders and variational autoencoders
# Model solutions. Try practice.py first.
# From the Brainy Bytes Deep Learning subject. Run it with: python3 <this file>
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


# ================================================================== task 1: The reparameterisation step
# Write reparameterize(mu, logvar, eps) that returns z = mu + exp(0.5 × logvar) × eps, rounded to 4
# decimals.
# Why it works: In a real VAE, eps is drawn fresh from N(0, 1) for every example at every step.
# Passing it in makes the function easy to test.

import math


def reparameterize(mu, logvar, eps):
    return round(mu + math.exp(0.5 * logvar) * eps, 4)


# ================================================================== task 2: The Gaussian KL term
# Write kl_gaussian(mus, sigmas) that returns the KL divergence from N(mu, sigma²) to N(0, 1),
# summed over all dimensions, rounded to 4 decimals.
# Why it works: The dimensions are independent under both distributions, which is why their KL
# values simply add.

import math


def kl_gaussian(mus, sigmas):
    total = 0.0
    for m, s in zip(mus, sigmas):
        total += 0.5 * (m * m + s * s - 1 - math.log(s * s))
    return round(total, 4)


# ================================================================== task 3: Reconstruction error
# Write reconstruction_mse(x, x_hat) that returns the mean squared difference between the input list
# and its reconstruction, rounded to 4 decimals.
# Why it works: For anomaly detection, this number is the score: compare it with a threshold set
# from normal data.

def reconstruction_mse(x, x_hat):
    return round(sum((a - b) ** 2 for a, b in zip(x, x_hat)) / len(x) + 0.0, 4)


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: The reparameterisation step", [('reparameterize(1.0, 0.0, 2.0)', 3.0), ('reparameterize(0.0, -2.0, 1.0)', 0.3679), ('reparameterize(-1.0, 0.0, -1.0)', -2.0)]))
    results.append(check("Task 2: The Gaussian KL term", [('kl_gaussian([0.0], [1.0])', 0.0), ('kl_gaussian([1.0], [1.0])', 0.5), ('kl_gaussian([1.0, 0.0], [1.0, 0.5])', 0.8181)]))
    results.append(check("Task 3: Reconstruction error", [('reconstruction_mse([1.0, 0.0, 1.0], [0.8, 0.2, 1.0])', 0.0267), ('reconstruction_mse([0.5], [0.5])', 0.0)]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
