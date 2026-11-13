# 1.3 Markov decision processes and Bellman equations
# Example "markov_chain" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np

states = ["sunny", "cloudy", "rainy"]
P = np.array([[0.7, 0.2, 0.1],                           # row = today, column = tomorrow
              [0.3, 0.4, 0.3],
              [0.2, 0.4, 0.4]])
print("each row sums to 1:", P.sum(axis=1))

rng = np.random.default_rng(0)
s, visits = 0, np.zeros(3)
for day in range(10000):                                 # walk the chain for 10,000 days
    visits[s] += 1
    s = rng.choice(3, p=P[s])                            # tomorrow depends only on today
print("share of days in each state:", (visits / visits.sum()).round(3))

dist = np.array([1.0, 0.0, 0.0])                          # start: certainly sunny
for _ in range(50):
    dist = dist @ P                                      # distribution after one more day
print("distribution after 50 days:", dist.round(3))
w, v = np.linalg.eig(P.T)
pi = np.real(v[:, np.argmin(abs(w - 1))])
print("stationary distribution (left eigenvector for eigenvalue 1):", (pi / pi.sum()).round(3))
print("two days ahead from rainy:", (np.array([0, 0, 1.0]) @ P @ P).round(3))
