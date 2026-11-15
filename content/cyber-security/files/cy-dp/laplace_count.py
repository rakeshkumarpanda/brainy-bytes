# 2.3 Differential privacy
# Example "laplace_count" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# The Laplace mechanism: answer a counting query with noise of scale sensitivity / epsilon
import random

random.seed(3)
def laplace(scale):
    # the difference of two exponential draws has a Laplace distribution
    return random.expovariate(1 / scale) - random.expovariate(1 / scale)

true_count = 412                           # patients in a database with a certain disease
sensitivity = 1                            # adding or removing one person changes a count by at most 1
for eps in (0.1, 0.5, 1.0, 5.0):
    b = sensitivity / eps
    answers = [true_count + laplace(b) for _ in range(1000)]
    mean_err = sum(abs(a - true_count) for a in answers) / len(answers)
    print(f"eps {eps:3}: scale b = {b:5.1f}, one answer {answers[0]:7.1f}, average error {mean_err:5.1f} (theory b = {b:.1f})")
print("\nSmaller epsilon means more privacy and more noise. The noise does not depend on the database size,")
print("so for large counts the relative error is tiny.")
