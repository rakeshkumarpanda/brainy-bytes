# 3.3 Diffusion models
# Example "ddpm_1d" from the lesson.
# From the Brainy Bytes Deep Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

# Train a tiny noise predictor and generate new data with DDPM sampling. NumPy only.
# Data: two bumps at -2 and +2 (spread 0.3). The "network" is a linear model on smooth features of (x, t),
# trained with the DDPM loss: predict the noise that was added.
import numpy as np

rng = np.random.default_rng(0)
T = 1000
betas = np.linspace(1e-4, 0.02, T)
alphas = 1 - betas
alpha_bar = np.cumprod(alphas)


def sample_data(n):
    return np.where(rng.random(n) < 0.5, -2.0, 2.0) + rng.normal(0, 0.3, n)


CENTRES = np.linspace(-5, 5, 51)


def features(x, t):
    s = t / T                                                         # time scaled to 0..1
    bumps = np.exp(-((x[:, None] - CENTRES) ** 2) / (2 * 0.2 ** 2))   # 51 smooth bumps over x
    bumps = np.concatenate([bumps, x[:, None]], axis=1)               # plus x itself, for values far out
    time = np.stack([np.ones_like(s), s, s ** 2, np.sqrt(s)], axis=1)
    return (bumps[:, :, None] * time[:, None, :]).reshape(len(x), -1)


# Training: pick x0, a random step t and noise eps, build x_t, and fit eps_hat(x_t, t) to eps
n = 20000
x0 = sample_data(n)
t = rng.integers(1, T + 1, n)
eps = rng.normal(size=n)
xt = np.sqrt(alpha_bar[t - 1]) * x0 + np.sqrt(1 - alpha_bar[t - 1]) * eps
F = features(xt, t)
w = np.linalg.solve(F.T @ F + 1e-3 * np.eye(F.shape[1]), F.T @ eps)   # least squares = one perfect training run
loss = np.mean((F @ w - eps) ** 2)
print(f'DDPM training loss (mean squared error of the noise): {loss:.3f}   (guessing 0 would give 1.000)')

# Sampling: start from pure noise and remove the predicted noise step by step
x = rng.normal(size=2000)
for step in range(T, 0, -1):
    eps_hat = features(x, np.full(len(x), step)) @ w
    a, ab, b = alphas[step - 1], alpha_bar[step - 1], betas[step - 1]
    x = (x - b / np.sqrt(1 - ab) * eps_hat) / np.sqrt(a)
    if step > 1:
        x += np.sqrt(b) * rng.normal(size=len(x))                    # DDPM adds fresh noise on every step but the last

real = sample_data(2000)
for name, v in [('real data ', real), ('generated ', x)]:
    left, right = v[v < 0], v[v > 0]
    print(f'{name} share right {np.mean(v > 0):.2f}   left bump mean {left.mean():5.2f} std {left.std():.2f}   right bump mean {right.mean():5.2f} std {right.std():.2f}')
counts, edges = np.histogram(x, bins=16, range=(-4, 4))
for c, e in zip(counts, edges):
    print(f'{e:5.1f} {"#" * int(c / 12)}')
