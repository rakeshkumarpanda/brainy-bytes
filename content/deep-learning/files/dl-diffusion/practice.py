# 3.3 Diffusion models
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


# ================================================================== task 1: The alpha bar schedule
# Write alpha_bars(betas) that returns the list of āt = (1 − β1) ... (1 − βt), each rounded to 4
# decimals.
# Hint: Keep a running product of 1 − β and record it after each step.

def alpha_bars(betas):
    # your code here
    pass


# ================================================================== task 2: A noisy sample in one jump
# Write noisy_sample(x0, alpha_bar, eps) that returns √ā · x0 + √(1 − ā) · eps rounded to 4
# decimals.
# Hint: Two square roots, then a weighted sum.

def noisy_sample(x0, alpha_bar, eps):
    # your code here
    pass


# ================================================================== task 3: Classifier free guidance
# Write guided_eps(eps_cond, eps_uncond, w) for two lists of the same length. Return (1 + w) · cond
# − w · uncond for each position, rounded to 4 decimals.
# Hint: Combine the two predictions position by position.

def guided_eps(eps_cond, eps_uncond, w):
    # your code here
    pass


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: The alpha bar schedule", [('alpha_bars([0.1, 0.2])', [0.9, 0.72]), ('alpha_bars([0.5, 0.5, 0.5])', [0.5, 0.25, 0.125]), ('alpha_bars([])', [])]))
    results.append(check("Task 2: A noisy sample in one jump", [('noisy_sample(2, 0.64, 0.5)', 1.9), ('noisy_sample(1, 1.0, 3)', 1.0), ('noisy_sample(0, 0.0, -1.5)', -1.5)]))
    results.append(check("Task 3: Classifier free guidance", [('guided_eps([0.4], [0.1], 3)', [1.3]), ('guided_eps([1, 2], [1, 0], 1)', [1, 4]), ('guided_eps([0.3, -0.2], [0.9, 0.5], 0)', [0.3, -0.2])]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
