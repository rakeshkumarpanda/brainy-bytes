# 4.1 Designing an ML system end to end
# Example "capacity_plan" from the lesson.
# From the Brainy Bytes MLOps subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

# Back of the envelope sizing for a real time recommendation model, the first step of an ML system design.
import math

daily_users = 10_000_000          # people who open the app each day
requests_per_user = 20            # feed refreshes per user per day
peak_factor = 3                   # the busiest hour is 3 times the daily average
latency_s = 0.040                 # one prediction takes 40 ms on one worker
workers_per_replica = 4           # parallel workers in one container
headroom = 0.6                    # run replicas at 60 percent load so a spike or a lost replica is safe

avg_qps = daily_users * requests_per_user / 86_400
peak_qps = avg_qps * peak_factor
per_replica = workers_per_replica / latency_s                       # Little's law: throughput = concurrency / time
replicas = math.ceil(peak_qps / (per_replica * headroom))
print(f'average {avg_qps:,.0f} requests/s, peak {peak_qps:,.0f} requests/s')
print(f'one replica serves {per_replica:.0f} requests/s, so {replicas} replicas at {headroom:.0%} load')

candidates, ranked = 1_000_000, 50                                  # catalogue size and items shown
rank_cost = 1e-6                                                    # the ranking model needs 1 microsecond per item
print(f'Ranking all {candidates:,} items would take {candidates * rank_cost * 1000:,.0f} ms per request.',
      f'Retrieve 500 candidates cheaply first, and ranking takes {500 * rank_cost * 1000:.1f} ms. Show the top {ranked}.')

bytes_per_log = 2_000                                               # features, prediction and id of one request
per_day_gb = daily_users * requests_per_user * bytes_per_log / 1e9
print(f'Prediction logs: {per_day_gb:,.0f} GB a day, {per_day_gb * 90 / 1000:,.1f} TB for 90 days of training data')
