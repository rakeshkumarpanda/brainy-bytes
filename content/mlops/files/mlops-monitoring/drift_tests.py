# 3.2 Monitoring and drift
# Example "drift_tests" from the lesson.
# From the Brainy Bytes MLOps subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

# Has a feature drifted? Compare live data with the training (reference) data using PSI and the KS test.
import numpy as np
from scipy.stats import ks_2samp

rng = np.random.default_rng(0)


def psi(reference, current, bins=10):
    """Population stability index with bins cut at the reference deciles."""
    edges = np.quantile(reference, np.linspace(0, 1, bins + 1))
    edges[0], edges[-1] = -np.inf, np.inf
    p = np.histogram(reference, edges)[0] / len(reference)
    q = np.histogram(current, edges)[0] / len(current)
    p, q = np.clip(p, 1e-4, None), np.clip(q, 1e-4, None)          # avoid log of zero in empty bins
    return float(np.sum((q - p) * np.log(q / p)))


def verdict(value):
    return 'stable' if value < 0.1 else ('watch' if value < 0.25 else 'drift')


reference = rng.normal(50, 10, 5000)                                   # e.g. customer age at training time
cases = {
    'same distribution': rng.normal(50, 10, 5000),
    'mean +2 (small shift)': rng.normal(52, 10, 5000),
    'mean +8 (big shift)': rng.normal(58, 10, 5000),
    'spread 10 -> 16': rng.normal(50, 16, 5000),
}
print(f'{"live data":24s} {"PSI":>6s}  verdict   {"KS stat":>7s}  {"p value":>8s}')
for name, current in cases.items():
    value = psi(reference, current)
    ks = ks_2samp(reference, current)
    print(f'{name:24s} {value:6.3f}  {verdict(value):8s}  {ks.statistic:7.3f}  {ks.pvalue:8.1e}')

big_ref, big_cur = rng.normal(50, 10, 200000), rng.normal(50.3, 10, 200000)
print()
print('With 200,000 rows a mean shift of only 0.3:')
print(f'  KS p value {ks_2samp(big_ref, big_cur).pvalue:.1e} (looks alarming)   PSI {psi(big_ref, big_cur):.4f} (stable)')
print('  Huge samples make tiny, harmless changes significant. Judge the size of the change, not only the p value.')
