# 3.3 Diffusion models
# Example "forward_noise" from the lesson.
# From the Brainy Bytes Deep Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

# The forward process of a diffusion model: add a little Gaussian noise at every step until only noise is left.
# Data: numbers from two bumps, around -2 and +2. Schedule: DDPM linear betas, T = 1000 steps.
import numpy as np

rng = np.random.default_rng(0)
x0 = np.where(rng.random(5000) < 0.5, -2.0, 2.0) + rng.normal(0, 0.3, 5000)

T = 1000
betas = np.linspace(1e-4, 0.02, T)          # noise added at step t
alphas = 1 - betas
alpha_bar = np.cumprod(alphas)              # how much of x0 is left after t steps

# Step by step: x_t = sqrt(1 - beta_t) x_(t-1) + sqrt(beta_t) noise
x = x0.copy()
print(f'start  data: mean {x0.mean():.2f}  std {x0.std():.2f}  share in the valley {np.mean(np.abs(x0) < 0.5):.2f}')
print('   t   alpha_bar   step by step: mean  std   one jump: mean  std   share in the valley |x| < 0.5')
for t in range(1, T + 1):
    x = np.sqrt(alphas[t - 1]) * x + np.sqrt(betas[t - 1]) * rng.normal(size=x.shape)
    if t in (1, 50, 100, 250, 500, 1000):
        # One jump: x_t = sqrt(alpha_bar_t) x0 + sqrt(1 - alpha_bar_t) noise gives the same distribution
        a = alpha_bar[t - 1]
        jump = np.sqrt(a) * x0 + np.sqrt(1 - a) * rng.normal(size=x0.shape)
        valley = np.mean(np.abs(x) < 0.5)                # empty at the start, 38 percent for N(0, 1)
        print(f'{t:4d}   {a:9.5f}   {x.mean():17.2f} {x.std():5.2f}   {jump.mean():13.2f} {jump.std():5.2f}   {valley:10.2f}')
print('After 1000 steps the data is plain N(0, 1) noise: the bumps are gone.')
