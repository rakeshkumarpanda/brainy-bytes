# 3.2 Generative adversarial networks
# Example "gan_theory" from the lesson.
# From the Brainy Bytes Deep Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

# The optimal discriminator and what the GAN game really minimises.
# Real data p = N(0, 1). Generator q = N(m, 1) for a few shifts m. We work on a fine grid of x values.
import numpy as np

x = np.linspace(-20, 30, 200001)
dx = x[1] - x[0]


def normal_pdf(x, mean, std=1.0):
    return np.exp(-0.5 * ((x - mean) / std) ** 2) / (std * np.sqrt(2 * np.pi))


def kl(p, q):
    mask = p > 1e-300
    return np.sum(p[mask] * np.log(p[mask] / q[mask])) * dx


p = normal_pdf(x, 0)
print('shift m | D* at x = 0 | value V(D*, G) | -log 4 + 2 JS | JS divergence')
for m in (0, 1, 3, 10):
    q = normal_pdf(x, m)
    d_star = p / (p + q + 1e-300)                    # the best possible discriminator for this generator
    value = (np.sum(p * np.log(d_star + 1e-300)) + np.sum(q * np.log(1 - d_star + 1e-300))) * dx
    mix = (p + q) / 2
    js = 0.5 * kl(p, mix) + 0.5 * kl(q, mix)
    print(f'{m:7d} | {d_star[np.argmin(abs(x))]:11.3f} | {value:14.4f} | {-np.log(4) + 2 * js:13.4f} | {js:.4f}')
print(f'log 2 = {np.log(2):.4f}, -log 4 = {-np.log(4):.4f}')
