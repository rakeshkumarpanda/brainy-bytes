# MLOps 3.2: monitoring models in production and detecting drift. Checked against Gama and colleagues, A survey on
# concept drift adaptation (ACM Computing Surveys 2014), Rabanser, Guennemann and Lipton, Failing loudly: an empirical
# study of methods for detecting dataset shift (NeurIPS 2019), Siddiqi, Credit risk scorecards (2006) for the
# population stability index, the SciPy documentation for ks_2samp, Google's Site Reliability Engineering book (chapters
# on SLOs and error budgets), Huyen, Designing Machine Learning Systems (2022) chapter 8, and the crontab, launchd,
# Windows schtasks and GitHub Actions schedule documentation.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, local, files, grow, term, show, leet_items
from mlkit import link, ossteps

chapter('mlops-monitoring')
K = Kit()
K.code('service_metrics', r'''
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
''', long=True)

K.code('drift_tests', r'''
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
''', long=True)

K.code('decay_sim', r'''
# Two kinds of drift over 12 months, and what retraining does.
# Concept drift: the inputs look the same but the rule linking them to the label slowly turns.
# Data drift: the inputs move but the rule stays the same.
import numpy as np
from sklearn.linear_model import LogisticRegression

rng = np.random.default_rng(1)


def month_data(month, kind, n=2000):
    X = rng.normal(0, 1, (n, 2))
    if kind == 'data':
        X[:, 0] += 0.25 * month                                       # customers change, the rule does not
    angle = np.radians(6 * month) if kind == 'concept' else 0.0       # the rule turns 6 degrees a month
    y = (X[:, 0] * np.cos(angle) + X[:, 1] * np.sin(angle) > 0).astype(int)
    flip = rng.random(n) < 0.05                                       # 5 percent label noise
    return X, np.where(flip, 1 - y, y)


def psi(ref, cur, bins=10):
    edges = np.quantile(ref, np.linspace(0, 1, bins + 1))
    edges[0], edges[-1] = -np.inf, np.inf
    p = np.clip(np.histogram(ref, edges)[0] / len(ref), 1e-4, None)
    q = np.clip(np.histogram(cur, edges)[0] / len(cur), 1e-4, None)
    return float(np.sum((q - p) * np.log(q / p)))


for kind, retrain in [('concept', None), ('concept', 3), ('data', None)]:
    X0, y0 = month_data(0, kind)
    model = LogisticRegression().fit(X0, y0)
    label = f'{kind} drift, ' + ('never retrained' if retrain is None else f'retrained every {retrain} months')
    print(label)
    print('  month:   ' + ' '.join(f'{m:5d}' for m in range(0, 13, 2)))
    accs, psis = [], []
    for m in range(13):
        X, y = month_data(m, kind)
        if m % 2 == 0:
            accs.append(model.score(X, y))
            psis.append(psi(X0[:, 0], X[:, 0]))
        if retrain and m > 0 and m % retrain == 0:
            model = LogisticRegression().fit(X, y)                     # needs this month's true labels
    print('  accuracy ' + ' '.join(f'{a:5.2f}' for a in accs))
    print('  PSI x1   ' + ' '.join(f'{p:5.2f}' for p in psis))
print('Concept drift hides from input checks (PSI stays near 0) but shows in accuracy.')
print('Data drift sets off the PSI alarm, yet this model stays accurate because its rule still holds.')
''', long=True)

K.code('daily_drift_job', r'''
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
''', long=True)

WHY_JOB = 'It is meant to be started every day by your computer&rsquo;s scheduler, which a browser page cannot do.'
GHA = '''name: daily-drift-check
on:
  schedule:
    - cron: "0 6 * * *"        # every day at 06:00 UTC
  workflow_dispatch:            # plus a Run workflow button
jobs:
  drift:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.14"
      - run: pip install numpy pandas
      - run: python daily_drift_job.py --strict
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: drift-report
          path: drift_report.json'''

SCHED_MAC = ('<p>macOS has two schedulers. <b>cron</b> is simple and the same as on Linux. <b>launchd</b> is Apple&rsquo;s own, and unlike cron it runs a job that was missed while the Mac was asleep once it wakes up.</p>'
             '<ol><li>Run the job once by hand and check that drift_report.json appears.</li>'
             '<li>Open your crontab and add the line below (use your own folder). The five fields are minute, hour, day of month, month and day of week.</li>'
             '<li>If the project lives in Documents, Desktop or Downloads, macOS privacy protection blocks cron. Give <code>/usr/sbin/cron</code> Full Disk Access in System Settings, Privacy and Security, or keep the project in another folder such as ~/ml-project.</li></ol>'
             + term(['cd ~/ml-project && .venv/bin/python daily_drift_job.py', 'crontab -e', '# add this line, save and close:', '0 6 * * * ~/ml-project/.venv/bin/python ~/ml-project/daily_drift_job.py --strict >> ~/ml-project/drift.log 2>&1', 'crontab -l                      # check it is there'], 'Terminal (macOS)'))
SCHED_WIN = ('<p>Windows uses <b>Task Scheduler</b>. The <code>schtasks</code> command creates a task without clicking through the Task Scheduler window. The job changes to its own folder first, so the task can start anywhere.</p>'
             + term(['cd $HOME\\ml-project', '.venv\\Scripts\\python.exe daily_drift_job.py      # once by hand', '',
                     'schtasks /Create /SC DAILY /ST 06:00 /TN "DriftCheck" /TR "$HOME\\ml-project\\.venv\\Scripts\\python.exe $HOME\\ml-project\\daily_drift_job.py --strict"',
                     'schtasks /Run /TN "DriftCheck"        # run it now to test', 'schtasks /Query /TN "DriftCheck" /V /FO LIST   # Last Result 0 means no drift, 1 means drift'], 'PowerShell (Windows)')
             + '<p>The task only runs while you are signed in, unless you open it in Task Scheduler and choose Run whether user is logged on or not. A laptop that is off at 06:00 skips the run unless you also tick Run task as soon as possible after a scheduled start is missed.</p>')
SCHED_LINUX = ('<p>Use <b>cron</b>, or a <b>systemd timer</b> on servers. With <code>Persistent=true</code> a timer also catches up on runs missed while the machine was off.</p>'
               + term(['cd ~/ml-project && .venv/bin/python daily_drift_job.py', 'crontab -e', '0 6 * * * ~/ml-project/.venv/bin/python ~/ml-project/daily_drift_job.py --strict >> ~/ml-project/drift.log 2>&1',
                       'grep CRON /var/log/syslog | tail      # Ubuntu and Debian: did it run', 'journalctl -u cron --since today      # or ask systemd (the service is crond on Fedora)'], 'Terminal (Linux)'))
SCHED_CHROME = ('<p>The Linux environment on a Chromebook only runs while it is open, so a cron job there misses runs while the Chromebook sleeps. Use it to test the job, and run the real schedule in GitHub Actions (below), which works the same whatever computer you use.</p>'
                + term(['sudo apt install cron                 # cron is not installed by default', 'sudo service cron start', 'crontab -e',
                        '0 6 * * * ~/ml-project/.venv/bin/python ~/ml-project/daily_drift_job.py --strict >> ~/ml-project/drift.log 2>&1'], 'Terminal (ChromeOS Linux)'))

K.lesson('what', 'What to watch once a model is live', f'''
{src('Google, Site Reliability Engineering (2016), chapters on service level objectives, and Huyen, Designing Machine Learning Systems (2022) chapter 8.')}
{wwh('<b>Monitoring</b> means measuring a live model all the time on four layers: the <b>service</b> (latency, errors, traffic), the <b>data</b> (missing values, schema, drift), the <b>model</b> (prediction distribution, accuracy once labels arrive) and the <b>business</b> (the metric the model exists to move).',
     'A model can fail silently. The API keeps answering 200 while the data underneath has changed and the predictions have become useless. Normal software monitoring sees nothing wrong, so ML needs extra checks.',
     'Set a target for each layer, such as 99 percent of requests under 200 ms (a service level objective, SLO). Collect the numbers from every request, look at percentiles rather than averages, and alert only on sustained problems that need a person.')}
{table(['Layer', 'Examples', 'Needs true labels?'], [
    ['Service', 'p50, p95, p99 latency, error rate, requests per second', 'No'],
    ['Data', 'missing share, unseen categories, out of range values, PSI per feature', 'No'],
    ['Model', 'prediction mean and spread, PSI of the scores, accuracy, calibration', 'Accuracy needs labels'],
    ['Business', 'fraud losses, click through rate, churn', 'Usually, and with delay']])}
{run('service_metrics')}
{note('The average latency is 24.5 ms, which sounds fine, but the 99th percentile is 292 ms, so 1 request in 100 is ten times slower than typical. Only 98.27 percent of requests met the 200 ms target, below the 99 percent SLO, while errors used 65 percent of the day&rsquo;s budget.', 'warn')}
{fxs(fx('Percentile', 'p99 = the value that 99 percent of requests stay below', 'Tail latency is what users notice.', key=True),
     fx('Error budget', 'allowed failures = (1 &minus; SLO) &times; requests', '99.9 percent of 100,000 leaves a budget of 100 errors.', key=True),
     fx('Burn rate', 'actual error rate / allowed error rate', 'A burn rate of 5 uses a 30 day budget in 6 days.'))}
''', kw=['monitoring', 'SLO', 'latency percentile', 'p99', 'error budget', 'burn rate', 'observability'])

K.lesson('drift', 'Drift: when live data stops looking like training data', f'''
{src('Rabanser, Guennemann and Lipton, Failing loudly (2019), Siddiqi, Credit risk scorecards (2006), and SciPy, scipy.stats.ks_2samp.')}
{viz('mlpsi')}
{wwh('<b>Data drift</b> (covariate shift) means the inputs change, for example younger customers after a marketing campaign. <b>Label shift</b> means the share of each class changes. <b>Concept drift</b> means the link between inputs and label changes, for example fraudsters change tactics. Drift tests compare a live window with the training data.',
     'A model only knows the world it was trained on. Drift is the early warning that its answers may be getting worse, often weeks before enough true labels arrive to measure accuracy.',
     'For each numeric feature compute the <b>PSI</b> (size of the change, thresholds 0.1 and 0.25) and the <b>KS test</b> (is there any change at all). For categories use a chi square test and watch for unseen values. Track the model&rsquo;s own score distribution too.')}
{run('drift_tests')}
{note('A shift of 8 in the mean gives PSI 0.610, clear drift. A wider spread gives 0.246 with no change in the mean, which a check on averages would miss. With 200,000 rows a harmless shift of 0.3 already has a KS p value of 1.3e&minus;12, while PSI is 0.001. Use the size of the change to decide, and the p value only as a hint.', 'exam')}
{fxs(fx('Population stability index', 'PSI = &Sigma;<sub>bins</sub> (q<sub>i</sub> &minus; p<sub>i</sub>) ln(q<sub>i</sub> / p<sub>i</sub>)', 'p training shares, q live shares. Below 0.1 stable, 0.1 to 0.25 watch, above 0.25 drift.', key=True),
     fx('Kolmogorov Smirnov statistic', 'D = max<sub>x</sub> |F<sub>train</sub>(x) &minus; F<sub>live</sub>(x)|', 'Largest gap between the two cumulative curves.', key=True),
     fx('PSI and KL divergence', 'PSI = KL(q || p) + KL(p || q)', 'For two normals with the same spread: (&Delta;&mu; / &sigma;)&sup2;.'))}
''', kw=['data drift', 'covariate shift', 'label shift', 'concept drift', 'PSI', 'KS test', 'chi square', 'p value'])

K.lesson('decay', 'Concept drift, label delay and retraining', f'''
{src('Gama and colleagues, A survey on concept drift adaptation (2014).')}
{viz('mldecay')}
{wwh('Input checks cannot see <b>concept drift</b>, because the inputs look the same. It only shows in the model&rsquo;s accuracy, which needs true labels, and labels often arrive late: a loan default shows up months later, a churn label after the customer leaves.',
     'Teams that only watch input drift miss the most damaging failure, and teams that retrain on every drift alarm waste effort on changes that did no harm.',
     'Collect labels wherever you can (user feedback, manual review of a sample, later outcomes). Watch proxies while waiting, such as the score distribution. Retrain on a schedule, or when performance drops past a threshold, always through the tested pipeline and the registry gate of MLOps 3.1.')}
{run('decay_sim')}
{note('Under concept drift accuracy fell from 0.95 to 0.57 in a year while the PSI of the input stayed at 0.01. Retraining every 3 months kept it between 0.86 and 0.94. Under data drift the PSI reached 6.20 but accuracy stayed at 0.94 to 0.95, because the model&rsquo;s rule still held.', 'exam')}
{table(['Retraining strategy', 'When it fits', 'Cost'], [
    ['On a schedule (weekly, monthly)', 'Steady, slow drift and labels arrive regularly', 'Simple, may retrain without need'],
    ['On a trigger (accuracy or drift past a threshold)', 'Irregular changes', 'Needs reliable monitoring'],
    ['Online or continual learning', 'Fast changing data such as ads or news', 'Complex, risk of learning from bad data']])}
''', kw=['concept drift', 'label delay', 'performance monitoring', 'retraining', 'proxy metrics', 'continual learning'])

K.lesson('schedule', 'Run a drift check every day on your computer', f'''
{src('crontab(5), Apple launchd documentation, Microsoft schtasks documentation, and GitHub Actions, Events that trigger workflows (schedule).')}
{wwh('A <b>scheduled job</b> runs the drift check by itself every day, writes a report, and exits with an error code when something drifted, so the scheduler or CI can alert you.',
     'A check that you must remember to run is a check that stops running. A schedule makes monitoring automatic.',
     'Download the job, run it once by hand, then register it with the scheduler of your system below, or with a GitHub Actions schedule that works the same for everyone.')}
{local('daily_drift_job', WHY_JOB)}
{note('On the demo data the income column moved (PSI 0.472) and 6 percent of ages went missing, above the 5 percent limit, so both are flagged. The score column needs watching (0.155). With --strict the job exits with code 1, which schedulers and CI treat as a failure.', 'tip')}
{ossteps('Schedule the job every morning at 06:00', SCHED_MAC, SCHED_WIN, SCHED_LINUX, SCHED_CHROME)}
{show('.github/workflows/drift.yml', GHA, {4: 'Cron syntax in UTC: minute 0, hour 6, every day.', 5: 'Adds a button to run it by hand from the Actions tab.', 15: '--strict makes the run fail, and GitHub emails you, when anything drifted.', 17: 'Keep the report even when the run failed.'}, lang='yaml')}
''', kw=['scheduled job', 'cron', 'launchd', 'Task Scheduler', 'schtasks', 'systemd timer', 'GitHub Actions schedule', 'exit code'])

K.lesson('respond', 'When an alert fires', f'''
{steps('A drift and decay playbook', [
    'Check the pipeline first: a broken join, a renamed column or a unit change causes most sudden drift.',
    'Measure the impact: did accuracy, calibration or the business metric move, or only an input?',
    'If the model is wrong and a previous version was fine, roll back the champion alias (MLOps 3.1).',
    'If the world changed, retrain on recent labelled data through the tested pipeline and the promotion gate.',
    'Write down the cause and add a test or a monitor so the same failure is caught earlier next time.'])}
{versus('Drift checks compared', ['', 'PSI', 'KS test', 'Chi square', 'Wasserstein distance'], [
    ['Data type', 'Numeric (binned) or categories', 'Numeric', 'Categories', 'Numeric'],
    ['Answers', 'How big is the change', 'Is there any change', 'Is there any change', 'How far did the values move'],
    ['Sensitive to sample size', 'Little', 'Very: big samples flag tiny changes', 'Very', 'Little'],
    ['Rule of thumb', '0.1 watch, 0.25 drift', 'p below 0.05, used with care', 'p below 0.05, used with care', 'Compare with the feature&rsquo;s spread']],
    'Use PSI or Wasserstein distance to decide and alert, and the tests as a second opinion. Tools such as Evidently compute all of them, and Prometheus with Grafana stores and charts the service metrics.')}
''', kw=['incident response', 'playbook', 'Wasserstein distance', 'Evidently', 'Prometheus', 'Grafana'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>Keep checking that the model is still fast, still answering and still seeing the kind of data it learned from.</p>',
    '<p>Track latency percentiles and error budgets, compute PSI and KS per feature, and schedule a daily drift report with alerts.</p>',
    '<p>Tell data, label and concept drift apart, handle label delay with proxies and sampled labels, and choose scheduled or triggered retraining.</p>',
    '<p>Detect drift in high dimensional data such as text and images with embeddings and two sample tests, adapt models online, and estimate accuracy without labels.</p>')}
{grow('Watch a live model every day.',
      'Detect drift and respond with a playbook.',
      'Keep models accurate as the world changes.')}
''', kw=['beginner', 'expert', 'embedding drift'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'Monitor four layers: <b>service</b> (p99 latency, errors), <b>data</b>, <b>model</b> and <b>business</b>. The mean latency hid a 292 ms p99.',
    '<b>PSI</b> measures how much a feature moved (0.1 watch, 0.25 drift). <b>KS</b> flags any change, and with huge samples it flags harmless ones.',
    '<b>Concept drift</b> leaves inputs alone and destroyed accuracy (0.95 to 0.57). <b>Data drift</b> raised PSI to 6.2 with no loss of accuracy.',
    'Schedule the drift job with cron or launchd (macOS), Task Scheduler (Windows), cron or systemd (Linux), or GitHub Actions on any system.',
    'On an alert: check the pipeline, measure impact, roll back or retrain through the gate, then add a test.'],
    'Coming next: explaining predictions and checking that a model is fair to every group.')}
{files('Three tasks: PSI from bin shares, a nearest rank percentile, and an alert that needs several bad days in a row.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'Why monitor the p99 latency instead of only the mean?', ['It is easier', 'The mean hides the slow tail that some users suffer', 'p99 is always lower', 'The mean is not defined'], 1, 'Tail latency.', '24.5 ms mean, 292 ms p99.')
K.quiz('e', 'A PSI of 0.61 for a feature means', ['Stable', 'Clear drift', 'A bug in the code', 'Better accuracy'], 1, 'Above 0.25.', 'Investigate.')
K.quiz('e', 'Concept drift means', ['The inputs change', 'The relationship between inputs and the label changes', 'The server is slow', 'The model file changed'], 1, 'The rule turns.', 'Inputs may look the same.')
K.quiz('e', 'A service level objective (SLO) is', ['A loss function', 'A target such as 99 percent of requests under 200 ms', 'A database', 'A model type'], 1, 'A promise you measure.', 'The error budget comes from it.')
K.quiz('m', 'Which check can catch concept drift?', ['PSI of the inputs', 'Accuracy measured on new true labels', 'KS test of the inputs', 'Request count'], 1, 'Needs labels.', 'Inputs can look unchanged.')
K.quiz('m', 'With 200,000 rows a harmless shift gives KS p = 1e&minus;12. The lesson is', ['Retrain at once', 'Big samples make tiny changes significant, so judge the size of the change', 'KS is wrong', 'Use fewer features'], 1, 'Effect size.', 'PSI was 0.001.')
K.quiz('m', 'On macOS, a cron job cannot read files in Documents. Why?', ['cron is broken', 'Privacy protection blocks it until cron gets Full Disk Access', 'The file is too big', 'Python is missing'], 1, 'macOS privacy.', 'Or keep the project elsewhere.')
K.quiz('m', 'On Windows, the built in way to run a job every day is', ['cron', 'Task Scheduler, for example with schtasks', 'launchd', 'systemd'], 1, 'Windows scheduler.', 'schtasks /Create /SC DAILY.')
K.quiz('m', 'A wider spread with the same mean shows up as', ['Nothing', 'Emptier middle bins and fuller outer bins, raising PSI', 'Lower latency', 'A change in labels'], 1, 'Shape, not mean.', 'Averages alone miss it.')
K.quiz('h', 'Data drift with no drop in accuracy is possible because', ['PSI is broken', 'The model&rsquo;s learned rule still holds for the moved inputs', 'Accuracy cannot change', 'Labels were wrong'], 1, 'Covariate shift with a correct model.', 'PSI 6.2, accuracy 0.95.')
K.quiz('h', 'The first step when a drift alert fires suddenly overnight is', ['Retrain', 'Check the data pipeline for a broken join, rename or unit change', 'Delete the model', 'Ignore it'], 1, 'Most sudden drift is a bug.', 'Then measure impact.')
K.quiz('h', 'An alert rule that needs 3 bad days in a row mainly', ['Finds drift faster', 'Reduces false alarms and alert fatigue', 'Measures accuracy', 'Replaces labels'], 1, 'Sustained problems only.', 'At the cost of a short delay.')
K.quiz('x', 'In the style of a Stanford CS329S exam: for two normals with the same spread &sigma; and means &Delta; apart, PSI is close to', ['&Delta; / &sigma;', '(&Delta; / &sigma;)&sup2;', '&Delta;&sup2;', '&sigma; / &Delta;'], 1, 'Symmetric KL of two normals.', 'A shift of 0.8 &sigma; gives about 0.64.')
K.quiz('x', 'In the style of an ML system design interview: labels for a credit model arrive after 6 months. The best early signal is', ['Wait 6 months', 'Drift of inputs and of the score distribution, plus a sample of quickly labelled cases', 'Training loss', 'CPU usage'], 1, 'Proxies plus sampled labels.', 'Accuracy comes later.')

K.calc('e', 'One bin holds 10 percent of training values and 20 percent of live values. Its PSI term?', '0.0693', '(q &minus; p) ln(q / p).', ['q &minus; p = 0.2 &minus; 0.1 = 0.1.', 'ln(0.2 / 0.1) = ln 2 = 0.6931.', eq('0.1 &times; 0.6931 = 0.0693')], check=0.0693, tol=0.0005)
K.calc('e', 'An SLO says 99.9 percent of 100,000 daily requests must succeed. How many errors does the budget allow?', '100', '(1 &minus; SLO) &times; requests.', ['1 &minus; 0.999 = 0.001.', 'Requests: 100,000.', eq('0.001 &times; 100,000 = 100 errors')], check=100)
K.calc('e', 'Out of 100,000 requests, how many are slower than the p99 latency?', '1000', 'One percent.', ['p99 leaves 1 percent above it.', '1 percent of 100,000.', eq('0.01 &times; 100,000 = 1000')], check=1000)
K.calc('m', 'Two bins with training shares 0.5 and 0.5 and live shares 0.7 and 0.3. PSI?', '0.1695', 'Add both terms.', ['Bin 1: 0.2 &times; ln 1.4 = 0.2 &times; 0.3365 = 0.0673.', 'Bin 2: (&minus;0.2) &times; ln 0.6 = 0.2 &times; 0.5108 = 0.1022.', eq('0.0673 + 0.1022 = 0.1695')], check=0.1695, tol=0.0005)
K.calc('m', 'Accuracy fell from 0.95 to 0.57 over 12 months. Average drop per month?', '0.0317', 'Total drop over months.', ['0.95 &minus; 0.57 = 0.38.', '12 months.', eq('0.38 / 12 = 0.0317')], check=0.0317, tol=0.0005)
K.calc('m', 'A model answers 20,000 requests a day and 2 percent get a label from manual review. Labels per week?', '2800', 'Daily labels times 7.', ['2 percent of 20,000 = 400 a day.', '7 days.', eq('400 &times; 7 = 2800')], check=2800)
K.calc('m', 'At some value the training CDF is 0.50 and the live CDF is 0.81, the biggest gap anywhere. KS statistic?', '0.31', 'Largest absolute gap.', ['|0.81 &minus; 0.50|.', 'It is the largest gap.', eq('D = 0.31')], check=0.31)
K.calc('h', 'Two normals with spread 10 and means 8 apart. Approximate PSI with (&Delta;/&sigma;)&sup2;?', '0.64', 'Square the standardised shift.', ['&Delta; / &sigma; = 8 / 10 = 0.8.', 'Square it.', eq('0.8&sup2; = 0.64 (the binned value was 0.60)')], check=0.64)
K.calc('h', 'The error budget allows 0.1 percent errors, and the service now fails 0.5 percent. How many days does a 30 day budget last?', '6', 'Burn rate, then divide.', ['Burn rate = 0.5 / 0.1 = 5.', 'The budget is spent 5 times too fast.', eq('30 / 5 = 6 days')], check=6)
K.calc('x', 'In the style of a monitoring design question: to see accuracy fall from 0.90 to 0.85 at two standard errors, use n = 4p(1 &minus; p)/d<sup>2</sup> with p = 0.9. Labelled cases needed?', '144', 'd = 0.05.', ['p(1 &minus; p) = 0.9 &times; 0.1 = 0.09.', '4 &times; 0.09 = 0.36, and d<sup>2</sup> = 0.0025.', eq('0.36 / 0.0025 = 144')], check=144)

K.assign('psi_bins', 'e', 'PSI from bin shares',
         '<p>Write <code>psi_bins(p, q)</code> for two lists of bin shares (training p, live q). Replace any share below 0.0001 with 0.0001, then return the sum of (q &minus; p) &middot; ln(q / p), rounded to 4 decimals.</p>',
         """
def psi_bins(p, q):
    # your code here
    pass
""", [('psi_bins([0.5, 0.5], [0.7, 0.3])', 0.1695), ('psi_bins([0.1, 0.9], [0.1, 0.9])', 0.0), ('psi_bins([0.5, 0.5], [1.0, 0.0])', 4.6043)],
         """
import math


def psi_bins(p, q):
    total = 0.0
    for a, b in zip(p, q):
        a, b = max(a, 1e-4), max(b, 1e-4)
        total += (b - a) * math.log(b / a)
    return round(total + 0.0, 4)
""", 'Clip each share, then add one term per bin.', '<p>Without the clip an empty bin would give ln 0 and crash. The clip also caps how much one empty bin can add.</p>')
K.assign('percentile', 'e', 'A nearest rank percentile',
         '<p>Write <code>percentile(values, pct)</code> using the nearest rank method: sort the values and return the one at rank ceil(pct / 100 &times; n), counting ranks from 1.</p>',
         """
def percentile(values, pct):
    # your code here
    pass
""", [('percentile([20, 18, 300, 19, 21], 50)', 20), ('percentile(list(range(1, 101)), 99)', 99), ('percentile([5], 95)', 5), ('percentile([3, 1, 2, 4], 100)', 4)],
         """
import math


def percentile(values, pct):
    ordered = sorted(values)
    rank = max(1, math.ceil(pct / 100 * len(ordered)))
    return ordered[rank - 1]
""", 'Sort, compute the rank with ceil, and index from 0.', '<p>numpy.percentile interpolates between ranks by default, so its answers can differ slightly. Monitoring systems state which method they use.</p>')
K.assign('sustained_alert', 'm', 'Alert only on sustained drift',
         '<p>Write <code>sustained_alert(values, threshold, k)</code> that returns True when at least <code>k</code> values in a row are at or above <code>threshold</code>.</p>',
         """
def sustained_alert(values, threshold, k):
    # your code here
    pass
""", [('sustained_alert([0.1, 0.3, 0.3, 0.3, 0.1], 0.25, 3)', True), ('sustained_alert([0.3, 0.1, 0.3, 0.1, 0.3], 0.25, 2)', False), ('sustained_alert([], 0.25, 1)', False), ('sustained_alert([0.25], 0.25, 1)', True)],
         """
def sustained_alert(values, threshold, k):
    run = 0
    for v in values:
        run = run + 1 if v >= threshold else 0
        if run >= k:
            return True
    return False
""", 'Count the current streak of bad values and reset it on a good one.', '<p>Requiring a streak cuts false alarms from one noisy day, at the cost of alerting a little later.</p>')

K.must('Four layers', 'Service (p50, p95, p99, errors), data (missing, schema, drift), model (scores, accuracy), business. Percentiles, not means.')
K.must('SLO and budget', 'Budget = (1 &minus; SLO) &times; requests. Burn rate = actual / allowed error rate.')
K.must('Drift types', 'Data (inputs move), label (class shares move), concept (rule changes, invisible to input checks).')
K.must('PSI and KS', 'PSI = &Sigma;(q &minus; p) ln(q/p): 0.1 watch, 0.25 drift. KS = max CDF gap, very sensitive to sample size.')
K.must('Decay', 'Concept drift: accuracy 0.95 to 0.57 with PSI 0.01. Data drift: PSI 6.2, accuracy 0.95. Retrain on schedule or trigger through the gate.')
K.must('Scheduling', 'cron or launchd (macOS, Full Disk Access for Documents), schtasks (Windows), cron or systemd timer (Linux), GitHub Actions schedule anywhere.')

T = K.topic(
    slug='mlops-monitoring', topic='mlops-monitoring', step=(3, 'Operate and improve', 'mlops-s3', 'Track experiments, register model versions, watch for drift and decay, and explain and audit predictions.', 'Advanced'),
    title='Monitoring and drift', short='Monitoring and drift', badge='3.2', minutes=55,
    lead='Watch a live model on four layers, measure tail latency against an SLO, detect data drift with PSI and the KS test, catch concept drift through accuracy, schedule a daily drift job on every operating system, and respond to alerts with a playbook.',
    desc='Monitoring, SLO, latency percentiles, error budget, burn rate, data drift, covariate shift, label shift, concept drift, population stability index, KS test, chi square, label delay, retraining, cron, launchd, Task Scheduler, schtasks, systemd timer, GitHub Actions schedule, Evidently, Prometheus, Grafana.',
    summary='What to monitor, PSI and KS drift tests, concept against data drift, retraining, and a scheduled drift job on every OS.',
    keywords=['model monitoring', 'data drift', 'concept drift', 'PSI', 'KS test', 'SLO', 'p99 latency', 'retraining', 'cron', 'Task Scheduler'],
    recap='<p>Measure the live model every day on service, data, model and business numbers, tell harmless drift from harmful decay, and let a scheduled job raise the alarm.</p>',
    added='2026-11-14', leet=leet_items())
