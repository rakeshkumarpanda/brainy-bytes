# 2.3 Naive Bayes: classify by counting clues
# Example "log_probabilities" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import math

probs = [0.01] * 400            # 400 words, each with probability 0.01
product = 1.0
for p in probs:
    product = product * p
print("multiply 400 small probabilities:", product)

log_sum = 0.0
for p in probs:
    log_sum = log_sum + math.log(p)
print("add their logs instead:", round(log_sum, 2))
print("compare classes with log scores, the larger one wins")
