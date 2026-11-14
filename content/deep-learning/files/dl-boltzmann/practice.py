# 3.4 Energy based models: Hopfield networks, Boltzmann machines and RBMs
# Practice tasks. Fill in each function, then run this file.
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


# ================================================================== task 1: Hebb weights for a Hopfield network
# Write hebb_weights(patterns). Each pattern is a list of +1 and −1 of length N. Return the N by N
# weight matrix wij = (1/N) Σ pipj as a list of lists, with zeros on the diagonal, each value
# rounded to 3 decimals.
# Hint: Two loops over unit pairs, skip i equal to j, and sum the products over the patterns.

def hebb_weights(patterns):
    # your code here
    pass


# ================================================================== task 2: RBM hidden probabilities
# Write rbm_hidden_probs(v, W, b). v is a list of visible values, W a list of rows (one row per
# visible unit, one column per hidden unit) and b the hidden biases. Return p(hj = 1 | v) = σ(bj +
# Σi viWij) for each hidden unit, rounded to 4 decimals.
# Hint: For each hidden unit add its bias to the weighted sum of the visible values, then apply the
# sigmoid.

def rbm_hidden_probs(v, W, b):
    # your code here
    pass


# ================================================================== task 3: Boltzmann probabilities at a temperature
# Write boltzmann_probs(energies, T) that returns p = e−E/T / Z for each energy, rounded to 4
# decimals. Subtract the smallest energy before taking exponentials so large energies do not
# overflow.
# Hint: Shift by the minimum energy, exponentiate, then divide by the sum.

def boltzmann_probs(energies, T):
    # your code here
    pass


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Hebb weights for a Hopfield network", [('hebb_weights([[1, -1]])', [[0.0, -0.5], [-0.5, 0.0]]), ('hebb_weights([[1, 1, -1], [1, -1, 1]])', [[0.0, 0.0, 0.0], [0.0, 0.0, -0.667], [0.0, -0.667, 0.0]]), ('hebb_weights([[1, 1, 1, 1], [1, 1, -1, -1], [1, -1, 1, -1]])', [[0.0, 0.25, 0.25, -0.25], [0.25, 0.0, -0.25, 0.25], [0.25, -0.25, 0.0, 0.25], [-0.25, 0.25, 0.25, 0.0]])]))
    results.append(check("Task 2: RBM hidden probabilities", [('rbm_hidden_probs([1, 1], [[0.5], [1.0]], [-1.0])', [0.6225]), ('rbm_hidden_probs([0, 0], [[3.0, -2.0], [3.0, -2.0]], [0.0, 0.0])', [0.5, 0.5]), ('rbm_hidden_probs([1, 0, 1], [[2.0, -1.0], [5.0, 5.0], [2.0, -1.0]], [-2.0, 1.0])', [0.8808, 0.2689])]))
    results.append(check("Task 3: Boltzmann probabilities at a temperature", [('boltzmann_probs([0, -1, 1], 1)', [0.2447, 0.6652, 0.09]), ('boltzmann_probs([0, 0], 3)', [0.5, 0.5]), ('boltzmann_probs([0, 2], 0.5)', [0.982, 0.018]), ('boltzmann_probs([1000, 1001], 1)', [0.7311, 0.2689])]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
