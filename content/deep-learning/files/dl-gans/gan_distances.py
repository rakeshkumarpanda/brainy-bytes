# 3.2 Generative adversarial networks
# Example "gan_distances" from the lesson.
# From the Brainy Bytes Deep Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

# Why Wasserstein GANs help: JS divergence stops changing once two distributions stop overlapping,
# but the Wasserstein (earth mover's) distance keeps growing with the gap, so it still gives a useful gradient.
import numpy as np
from scipy.stats import wasserstein_distance

rng = np.random.default_rng(0)
real = rng.uniform(0, 1, 20000)                     # real data: uniform on [0, 1]


def js_divergence(a, b, bins):
    p, _ = np.histogram(a, bins=bins)
    q, _ = np.histogram(b, bins=bins)
    p, q = p / p.sum(), q / q.sum()
    m = (p + q) / 2
    kl = lambda u, v: np.sum(u[u > 0] * np.log(u[u > 0] / v[u > 0]))
    return 0.5 * kl(p, m) + 0.5 * kl(q, m)


bins = np.linspace(-1, 12, 1301)
print('shift | JS divergence | Wasserstein distance')
for shift in (0.0, 0.5, 1.0, 2.0, 5.0, 10.0):
    fake = rng.uniform(0, 1, 20000) + shift          # the generator's samples, moved to the right
    print(f'{shift:5.1f} | {js_divergence(real, fake, bins):13.3f} | {wasserstein_distance(real, fake):20.3f}')
print(f'JS can never exceed log 2 = {np.log(2):.3f}')
