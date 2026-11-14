# 4.1 Designing an ML system end to end
# Example "ab_test" from the lesson.
# From the Brainy Bytes MLOps subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

# Online A/B test of a new model: how many users you need, the test itself, and why peeking every day lies.
import numpy as np
from scipy.stats import norm

p_a, lift = 0.050, 0.005                       # old model converts 5.0 percent, we hope for 5.5 percent
alpha, power = 0.05, 0.80
z_a, z_b = norm.ppf(1 - alpha / 2), norm.ppf(power)
p_bar = p_a + lift / 2
n = int(np.ceil((z_a + z_b) ** 2 * 2 * p_bar * (1 - p_bar) / lift ** 2))
print(f'users needed per group: {n:,}   (z {z_a:.2f} and {z_b:.2f})')


def z_test(conv_a, conv_b, n_a, n_b):
    pa, pb = conv_a / n_a, conv_b / n_b
    pool = (conv_a + conv_b) / (n_a + n_b)
    z = (pb - pa) / np.sqrt(pool * (1 - pool) * (1 / n_a + 1 / n_b))
    return z, 2 * (1 - norm.cdf(abs(z)))


rng = np.random.default_rng(7)
conv_a, conv_b = rng.binomial(n, p_a), rng.binomial(n, p_a + lift)
z, p = z_test(conv_a, conv_b, n, n)
print(f'one real test: A {conv_a / n:.4f}  B {conv_b / n:.4f}  z {z:.2f}  p {p:.4f}  ->',
      'ship B' if p < alpha else 'no clear winner')

# 2000 A/A tests: both groups get the SAME model, so every "significant" result is a false alarm
days, per_day, sims = 20, n // 20, 2000
end_only = peeking = 0
for _ in range(sims):
    a = rng.binomial(per_day, p_a, days).cumsum()
    b = rng.binomial(per_day, p_a, days).cumsum()
    seen = per_day * np.arange(1, days + 1)
    pvals = [z_test(a[d], b[d], seen[d], seen[d])[1] for d in range(days)]
    end_only += pvals[-1] < alpha
    peeking += min(pvals) < alpha
print(f'false alarms when you look once at the end: {end_only / sims:.1%}')
print(f'false alarms when you stop on the first day with p < 0.05: {peeking / sims:.1%}')
