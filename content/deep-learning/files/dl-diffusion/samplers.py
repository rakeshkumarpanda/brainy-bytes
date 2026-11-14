# 3.3 Diffusion models
# Example "samplers" from the lesson.
# From the Brainy Bytes Deep Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

# DDPM against DDIM, and classifier free guidance. To focus on the samplers, the noise predictor here is the exact
# best one for our two bump data (a trained network learns to approximate it).
import numpy as np

T = 1000
betas = np.linspace(1e-4, 0.02, T)
alpha_bar = np.cumprod(1 - betas)
MEANS, SPREAD = np.array([-2.0, 2.0]), 0.3


def eps_exact(x, t, weights=(0.5, 0.5)):
    """The best noise prediction at step t (1..T) for data made of bumps with these weights."""
    a = alpha_bar[t - 1]
    var = a * SPREAD ** 2 + 1 - a                                  # each bump after t steps of noise
    logp = np.log(np.array(weights) + 1e-300) - (x[:, None] - np.sqrt(a) * MEANS) ** 2 / (2 * var)
    r = np.exp(logp - logp.max(axis=1, keepdims=True))
    r /= r.sum(axis=1, keepdims=True)                              # which bump each x probably came from
    score = (r * -(x[:, None] - np.sqrt(a) * MEANS) / var).sum(axis=1)
    return -np.sqrt(1 - a) * score


def ddpm(n, eps_fn, seed=0):
    rng = np.random.default_rng(seed)
    x = rng.normal(size=n)
    for t in range(T, 0, -1):
        b, ab = betas[t - 1], alpha_bar[t - 1]
        x = (x - b / np.sqrt(1 - ab) * eps_fn(x, t)) / np.sqrt(1 - b)
        if t > 1:
            x += np.sqrt(b) * rng.normal(size=n)
    return x


def ddim(n, eps_fn, steps, seed=0):
    rng = np.random.default_rng(seed)
    ts = np.linspace(T, 1, steps).round().astype(int)              # visit only a few of the 1000 steps
    x = rng.normal(size=n)
    for i, t in enumerate(ts):
        e = eps_fn(x, t)
        x0_hat = (x - np.sqrt(1 - alpha_bar[t - 1]) * e) / np.sqrt(alpha_bar[t - 1])
        if i + 1 < len(ts):
            s = ts[i + 1]
            x = np.sqrt(alpha_bar[s - 1]) * x0_hat + np.sqrt(1 - alpha_bar[s - 1]) * e   # no fresh noise
        else:
            x = x0_hat
    return x


def describe(name, x, calls):
    right = x[x > 0]
    print(f'{name:22s} {calls:5d} network calls   share right {np.mean(x > 0):.2f}   right bump mean {right.mean():.2f} std {right.std():.2f}')


print('Real data: share right 0.50, each bump has mean +-2.00 and std 0.30')
describe('DDPM, 1000 steps', ddpm(3000, eps_exact), 1000)
for k in (50, 10, 3):
    describe(f'DDIM, {k} steps', ddim(3000, eps_exact, k), k)

print()
print('Classifier free guidance towards the right bump: eps = (1 + w) eps_cond - w eps_uncond')
for w in (0, 1, 3, 7):
    guided = lambda x, t, w=w: (1 + w) * eps_exact(x, t, (0.0, 1.0)) - w * eps_exact(x, t)
    describe(f'guidance w = {w}', ddim(3000, guided, 50), 2 * 50)
