# 3.2 Monitoring and drift
# Example "daily_drift_job" from the lesson.
# From the Brainy Bytes MLOps subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

# A daily drift check that your computer's scheduler (cron, Task Scheduler) or a CI schedule can run.
# It compares today's inputs and predictions with the reference data and writes drift_report.json.
#   python daily_drift_job.py            check and write the report
#   python daily_drift_job.py --strict   also exit with code 1 when anything drifted, so the scheduler can alert
import json
import os
import sys
from datetime import datetime

import numpy as np
import pandas as pd


def psi(ref, cur, bins=10):
    edges = np.unique(np.quantile(ref, np.linspace(0, 1, bins + 1)))
    edges[0], edges[-1] = -np.inf, np.inf
    p = np.clip(np.histogram(ref, edges)[0] / len(ref), 1e-4, None)
    q = np.clip(np.histogram(cur, edges)[0] / len(cur), 1e-4, None)
    return round(float(np.sum((q - p) * np.log(q / p))), 3)


if '__file__' in globals():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))        # schedulers often start in another folder

if not os.path.exists('reference.csv'):                             # demo data, so the job runs anywhere
    rng = np.random.default_rng(7)
    ref = pd.DataFrame({'age': rng.normal(45, 12, 5000), 'income': rng.lognormal(10.5, 0.4, 5000), 'score': rng.beta(2, 5, 5000)})
    today = pd.DataFrame({'age': rng.normal(45, 12, 800), 'income': rng.lognormal(10.8, 0.4, 800), 'score': rng.beta(2.6, 5, 800)})
    today.loc[today.sample(frac=0.06, random_state=1).index, 'age'] = np.nan
    ref.to_csv('reference.csv', index=False)
    today.to_csv('today.csv', index=False)

ref, today = pd.read_csv('reference.csv'), pd.read_csv('today.csv')
report = {'time': datetime.now().isoformat(timespec='seconds'), 'rows_today': len(today), 'columns': {}}
drifted = []
for col in ref.columns:
    missing = float(today[col].isna().mean())
    value = psi(ref[col].dropna(), today[col].dropna())
    status = 'drift' if value >= 0.25 or missing > 0.05 else ('watch' if value >= 0.1 else 'ok')
    report['columns'][col] = {'psi': value, 'missing_share': round(missing, 3), 'status': status}
    if status == 'drift':
        drifted.append(col)
    print(f'{col:7s} PSI {value:6.3f}   missing {missing:5.1%}   {status}')

report['drifted'] = drifted
with open('drift_report.json', 'w') as f:
    json.dump(report, f, indent=2)
print('wrote drift_report.json, drifted columns:', drifted or 'none')
if drifted and '--strict' in sys.argv:
    sys.exit(1)
