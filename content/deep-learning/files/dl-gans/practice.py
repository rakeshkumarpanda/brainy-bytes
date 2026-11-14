# 3.2 Generative adversarial networks
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


# ================================================================== task 1: The discriminator loss
# Write discriminator_loss(d_real, d_fake) that takes the discriminator’s scores on a list of real
# examples and a list of fake examples, and returns the average of −ln D(real) over the real list
# plus the average of −ln(1 − D(fake)) over the fake list, rounded to 4 decimals.
# Hint: Average −ln d over the real scores and −ln(1 − d) over the fake scores, then add the two
# averages.

def discriminator_loss(d_real, d_fake):
    # your code here
    pass


# ================================================================== task 2: Saturating and non saturating generator losses
# Write generator_loss(d_fake, kind). For kind 'ns' return the average of −ln d, and for kind 'sat'
# return the average of ln(1 − d), over the list of scores, rounded to 4 decimals.
# Hint: Pick the formula from kind, apply it to each score and average.

def generator_loss(d_fake, kind):
    # your code here
    pass


# ================================================================== task 3: The Fr&eacute;chet distance in one dimension
# Write frechet_1d(mu1, var1, mu2, var2) that returns (mu1 − mu2)² + var1 + var2 − 2√(var1 × var2),
# rounded to 4 decimals. This is FID with one feature.
# Hint: Square the gap between the means, add both variances and subtract twice the square root of
# their product.

def frechet_1d(mu1, var1, mu2, var2):
    # your code here
    pass


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: The discriminator loss", [('discriminator_loss([0.9], [0.2])', 0.3285), ('discriminator_loss([0.5, 0.5], [0.5, 0.5])', 1.3863), ('discriminator_loss([0.99], [0.01])', 0.0201)]))
    results.append(check("Task 2: Saturating and non saturating generator losses", [("generator_loss([0.1], 'ns')", 2.3026), ("generator_loss([0.1], 'sat')", -0.1054), ("generator_loss([0.5, 0.5], 'ns')", 0.6931)]))
    results.append(check("Task 3: The Fr&eacute;chet distance in one dimension", [('frechet_1d(1, 1, 3, 4)', 5.0), ('frechet_1d(0, 1, 0, 1)', 0.0), ('frechet_1d(2, 0.25, 2, 1)', 0.25)]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
