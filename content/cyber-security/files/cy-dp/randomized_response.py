# 2.3 Differential privacy
# Example "randomized_response" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Randomised response (Warner 1965): ask a sensitive yes or no question so that no single answer can be trusted
import math
import random

random.seed(1)
TRUE_RATE = 0.30                          # 30% really did cheat on the exam (unknown to the surveyor)
people = [random.random() < TRUE_RATE for _ in range(2000)]

def answer(truth):
    if random.random() < 0.5:             # first coin heads: tell the truth
        return truth
    return random.random() < 0.5          # tails: flip again and say yes on heads, no on tails

answers = [answer(t) for t in people]
yes = sum(answers) / len(answers)
estimate = 2 * yes - 0.5                  # P(yes) = 0.5 * p + 0.25, so p = 2 * P(yes) - 0.5
print(f"share answering yes: {yes:.3f}")
print(f"estimated true rate: {estimate:.3f}   (actual {sum(people) / len(people):.3f})")

# privacy: P(yes | truth yes) = 0.75 and P(yes | truth no) = 0.25, so the ratio is 3
eps = math.log(0.75 / 0.25)
print(f"epsilon = ln 3 = {eps:.4f}: any single 'yes' is at most 3 times more likely from a cheater")
