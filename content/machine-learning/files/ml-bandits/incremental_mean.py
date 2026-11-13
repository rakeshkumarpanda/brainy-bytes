# 1.2 Multi armed bandits
# Example "incremental_mean" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

rewards = [4, 6, 5, 9, 1]
Q, n = 0.0, 0
for r in rewards:
    n += 1
    Q = Q + (r - Q) / n                                  # new estimate = old + step size * (target - old)
    print("reward", r, " estimate after", n, "pulls:", round(Q, 3))
print("plain average:", sum(rewards) / len(rewards))

# A constant step size forgets old rewards, which helps when the arm changes over time
Q, alpha = 0.0, 0.5
for r in [1, 1, 1, 10, 10, 10]:
    Q = Q + alpha * (r - Q)
    print("constant step 0.5, reward", r, " estimate", round(Q, 3))
