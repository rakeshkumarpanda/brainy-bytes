# 1.3 Markov decision processes and Bellman equations
# Example "mrp_value" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np

states = ["Wake", "Gym", "Work", "Couch", "End"]
P = np.array([[0.0, 0.5, 0.0, 0.5, 0.0],                 # Wake: gym or couch
              [0.0, 0.0, 0.8, 0.2, 0.0],                 # Gym: work or couch
              [0.0, 0.0, 0.0, 0.4, 0.6],                 # Work: couch or done for the day
              [0.4, 0.0, 0.0, 0.6, 0.0],                 # Couch: stay or wake up again
              [0.0, 0.0, 0.0, 0.0, 1.0]])                # End: stays there, no more reward
R = np.array([-1.0, -2.0, 10.0, -1.0, 0.0])              # reward for leaving each state
gamma = 0.9

V_exact = np.linalg.solve(np.eye(5) - gamma * P, R)      # Bellman equation V = R + gamma P V, solved at once
print("exact values:      ", {name: round(float(v), 3) for name, v in zip(states, V_exact)})

V = np.zeros(5)
for sweep in range(1, 101):
    V = R + gamma * P @ V                                # apply the Bellman equation as an update
    if sweep in (1, 2, 5, 20, 100):
        print("after", str(sweep).rjust(3), "sweeps:", V.round(3))
