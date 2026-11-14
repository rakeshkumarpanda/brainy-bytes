# 3.2 Monitoring and drift
# Example "service_metrics" from the lesson.
# From the Brainy Bytes MLOps subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

# Service health of a model API for one day: latency percentiles and error rate against an SLO.
import numpy as np

rng = np.random.default_rng(3)
n = 100_000                                                         # requests in one day
latency = rng.lognormal(mean=np.log(18), sigma=0.35, size=n)        # most requests take about 18 ms
slow = rng.random(n) < 0.02                                         # 2 percent hit a cold cache or a long input
latency[slow] += rng.uniform(150, 400, slow.sum())
errors = rng.random(n) < 0.0007                                     # 500 errors

p50, p95, p99 = np.percentile(latency, [50, 95, 99])
print(f'mean {latency.mean():.1f} ms   p50 {p50:.1f} ms   p95 {p95:.1f} ms   p99 {p99:.1f} ms')
print('The mean looks fine, but 1 request in 100 waits more than', round(p99), 'ms.')

slo_latency, slo_success = 200, 0.999                              # 99 percent under 200 ms, 99.9 percent succeed
print(f'Share under {slo_latency} ms: {np.mean(latency < slo_latency):.4f}   (target 0.99)')
budget = (1 - slo_success) * n                                      # errors the SLO allows today
print(f'Errors: {errors.sum()} of an error budget of {budget:.0f}, so {errors.sum() / budget:.0%} of the budget is used')
