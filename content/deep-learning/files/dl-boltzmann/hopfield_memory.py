# 3.4 Energy based models: Hopfield networks, Boltzmann machines and RBMs
# Example "hopfield_memory" from the lesson.
# From the Brainy Bytes Deep Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

# A Hopfield network: store letters as patterns of +1 and -1, then recall a letter from a damaged copy.
import numpy as np

LETTERS = {
    'T': ['#####', '..#..', '..#..', '..#..', '..#..'],
    'L': ['#....', '#....', '#....', '#....', '#####'],
    'X': ['#...#', '.#.#.', '..#..', '.#.#.', '#...#'],
}
to_vec = lambda rows: np.array([1 if ch == '#' else -1 for row in rows for ch in row])
show = lambda s: '\n'.join(''.join('#' if v > 0 else '.' for v in s[r * 5:r * 5 + 5]) for r in range(5))

P = np.array([to_vec(r) for r in LETTERS.values()])                 # 3 patterns, 25 units each
N = P.shape[1]
W = P.T @ P / N                                                     # Hebb rule: units that agree get a positive weight
np.fill_diagonal(W, 0)                                              # no unit connects to itself


def energy(s):
    return -0.5 * s @ W @ s


rng = np.random.default_rng(1)
s = P[0].copy()
flip = rng.choice(N, 6, replace=False)
s[flip] *= -1                                                       # damage 6 of the 25 pixels of T
print('damaged T, energy', round(energy(s), 3))
print(show(s))
for sweep in range(3):
    for i in rng.permutation(N):                                    # asynchronous: one unit at a time
        s[i] = 1 if W[i] @ s >= 0 else -1
    print(f'after sweep {sweep + 1}: energy {energy(s):.3f}, wrong pixels {int(np.sum(s != P[0]))}')
print(show(s))

# Capacity: how many random patterns can 100 units hold? Start each one with 10 pixels flipped.
N = 100
for k in [5, 10, 14, 20, 30]:
    pats = rng.choice([-1, 1], size=(k, N))
    W2 = pats.T @ pats / N
    np.fill_diagonal(W2, 0)
    ok = 0
    for p in pats:
        s = p.copy()
        s[rng.choice(N, 10, replace=False)] *= -1
        for _ in range(5):
            for i in rng.permutation(N):
                s[i] = 1 if W2[i] @ s >= 0 else -1
        ok += np.mean(s == p) >= 0.98                               # recalled with at most 2 wrong pixels
    print(f'{k:2d} patterns in 100 units: {ok} of {k} recalled ({ok / k:.0%})')
print('Rule of thumb: about 0.14 N random patterns (14 here) before recall breaks down.')
