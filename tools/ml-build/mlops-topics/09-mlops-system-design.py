# MLOps 4.1: designing an ML system end to end. Checked against Huyen, Designing Machine Learning Systems (2022),
# Kleppmann, Designing Data-Intensive Applications (2017) for capacity and latency, Sculley and colleagues, Hidden
# technical debt in machine learning systems (2015), Breck and colleagues, The ML test score (2017) for training-serving
# skew, Kohavi, Tang and Xu, Trustworthy Online Controlled Experiments (2020) for sample size and peeking, Covington,
# Adams and Sargin, Deep neural networks for YouTube recommendations (2016) for two stage retrieval and ranking, and
# Google's SRE workbook chapter on canarying releases.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, local, files, grow, term, show, leet_items
from mlkit import link, ossteps

chapter('mlops-system-design')
K = Kit()
K.code('capacity_plan', r'''
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
''', long=True)

K.code('skew_check', r'''
# Training-serving skew: the same feature computed two different ways in training and in the live service.
import numpy as np
from sklearn.linear_model import LogisticRegression

rng = np.random.default_rng(1)
n = 20000
spend_30d = rng.gamma(2.0, 40.0, n)                                 # money spent in the last 30 days
visits_30d = rng.poisson(6, n)
missing = rng.random(n) < 0.15                                      # new customers have no spend history
churn = (rng.random(n) < 1 / (1 + np.exp(0.03 * (spend_30d - 60) + 0.25 * (visits_30d - 6)))).astype(int)


tr, te = slice(0, 15000), slice(15000, n)
FILL = np.median(spend_30d[tr][~missing[tr]])                      # learned once, from training rows only


def features_training(spend, visits, miss):
    """The data scientist's notebook: missing spend filled with the training median, spend in pounds."""
    s = np.where(miss, FILL, spend)
    return np.column_stack([s, visits])


def features_serving_buggy(spend, visits, miss):
    """The backend team's rewrite: missing spend becomes 0, and spend arrives in pence."""
    s = np.where(miss, 0.0, spend * 100)
    return np.column_stack([s, visits])


model = LogisticRegression(max_iter=1000).fit(features_training(spend_30d[tr], visits_30d[tr], missing[tr]), churn[tr])
offline = model.score(features_training(spend_30d[te], visits_30d[te], missing[te]), churn[te])
online = model.score(features_serving_buggy(spend_30d[te], visits_30d[te], missing[te]), churn[te])
print(f'offline accuracy (training features): {offline:.3f}')
print(f'online accuracy (serving features):   {online:.3f}')
p_off = model.predict_proba(features_training(spend_30d[te], visits_30d[te], missing[te]))[:, 1]
p_on = model.predict_proba(features_serving_buggy(spend_30d[te], visits_30d[te], missing[te]))[:, 1]
print(f'mean predicted churn: offline {p_off.mean():.3f}, online {p_on.mean():.3f}')
a = features_training(spend_30d[te], visits_30d[te], missing[te])
b = features_serving_buggy(spend_30d[te], visits_30d[te], missing[te])
differ = ~np.isclose(a, b).all(axis=1)
print(f'parity test (same raw rows through both paths): {differ.mean():.1%} of rows differ, so it fails before release')
print('Fix: one feature function, or a feature store, shared by training and serving.')
''', long=True)

K.code('ab_test', r'''
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
''', long=True)

K.code('load_test', r'''
# A small load test for a model API, using only the Python standard library.
#   python load_test.py                                  tests a built-in demo server (4 workers, 20 ms a prediction)
#   python load_test.py --url http://127.0.0.1:8000/predict   tests your own FastAPI or Docker service from MLOps 2.2 and 2.3
import argparse
import json
import statistics
import threading
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

FLOWER = {'sepal_length': 5.9, 'sepal_width': 3.0, 'petal_length': 5.1, 'petal_width': 1.8}
NO_PROXY = urllib.request.build_opener(urllib.request.ProxyHandler({}))   # talk to the server directly
WORKERS = threading.Semaphore(4)                                     # the demo server can work on 4 requests at once


class DemoModel(BaseHTTPRequestHandler):
    def do_POST(self):
        self.rfile.read(int(self.headers.get('Content-Length', 0)))
        with WORKERS:                                                # extra requests wait in a queue here
            time.sleep(0.020)                                        # pretend the model needs 20 ms
        body = json.dumps({'species': 'virginica', 'probability': 0.97}).encode()
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):                                    # keep the terminal quiet
        pass


class DemoServer(ThreadingHTTPServer):
    request_queue_size = 128                                         # the default backlog of 5 is too small for 16 users


def one_call(url):
    data = json.dumps(FLOWER).encode()
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    start = time.perf_counter()
    with NO_PROXY.open(req, timeout=10) as r:
        r.read()
    return (time.perf_counter() - start) * 1000


def run_level(url, users, total):
    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=users) as pool:
        ms = sorted(pool.map(lambda _: one_call(url), range(total)))
    seconds = time.perf_counter() - start
    pct = lambda q: ms[min(len(ms) - 1, int(q * len(ms)))]
    return total / seconds, statistics.median(ms), pct(0.95), pct(0.99)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--url', help='the /predict address of a running service')
    ap.add_argument('--requests', type=int, default=300)
    args = ap.parse_args()
    url, server = args.url, None
    if not url:
        server = DemoServer(('127.0.0.1', 0), DemoModel)              # port 0: the system picks a free port
        threading.Thread(target=server.serve_forever, daemon=True).start()
        url = f'http://127.0.0.1:{server.server_port}/predict'
        print('No --url given, so testing the built-in demo server: 4 workers, 20 ms a prediction')
    one_call(url)                                                    # warm up
    print(f'{"users":>5s} {"req/s":>7s} {"p50 ms":>7s} {"p95 ms":>7s} {"p99 ms":>7s}')
    for users in [1, 2, 4, 8, 16]:
        rps, p50, p95, p99 = run_level(url, users, args.requests)
        print(f'{users:5d} {rps:7.0f} {p50:7.1f} {p95:7.1f} {p99:7.1f}')
    print("Little's law: requests/s is about users / latency until the workers are full.")
    print('After that, more users only make every request wait longer.')
    if server:
        server.shutdown()


if __name__ == '__main__':
    main()
''', long=True)

WHY_LOAD = 'A load test needs real network calls to a server on your machine, which a browser page cannot make.'
REAL_RUN = term(['$ docker run -d --rm --name lt -p 8000:8000 iris-api:1.0.0',
                 '$ curl http://127.0.0.1:8000/health',
                 '{"status":"ok","model_version":"1.0.0"}',
                 '$ python load_test.py --url http://127.0.0.1:8000/predict --requests 200',
                 'users   req/s  p50 ms  p95 ms  p99 ms',
                 '    1     446     2.1     2.7     3.6',
                 '    2     792     2.3     3.4     4.2',
                 '    4    1060     3.5     5.8     7.9',
                 '    8    1182     6.3    10.3    11.7',
                 '   16    1180    12.1    19.1    20.5',
                 '$ docker stop lt'], 'A real run against the Docker image from MLOps 2.3 (Linux)')

LT_MAC = ('<ol><li>Start Docker Desktop, then start the image you built in MLOps 2.3. Without Docker, start the FastAPI service from MLOps 2.2 with <code>uvicorn fastapi_serve:app --port 8000 --workers 4</code>. Both accept the same flower fields.</li>'
          '<li>Wait until the health check answers, then run the load test in a second Terminal window.</li>'
          '<li>Compare the table with the real run below. Apple Silicon Macs are usually faster than the cloud machine used for this page.</li></ol>'
          + term(['docker run -d --rm --name lt -p 8000:8000 iris-api:1.0.0', 'curl http://127.0.0.1:8000/health', 'python3 load_test.py --url http://127.0.0.1:8000/predict', 'docker stop lt'], 'Terminal (macOS)'))
LT_WIN = ('<ol><li>Start Docker Desktop (it uses WSL 2), then run the container in PowerShell. Or start the FastAPI service with uvicorn as in MLOps 2.2, which also runs on Windows.</li>'
          '<li>Use <code>127.0.0.1</code> rather than <code>localhost</code>. On Windows localhost may try the IPv6 address first, which adds a delay to every request and spoils the timings.</li>'
          '<li>In PowerShell <code>curl</code> is an alias of Invoke-WebRequest, so type <code>curl.exe</code> to get the real curl.</li></ol>'
          + term(['docker run -d --rm --name lt -p 8000:8000 iris-api:1.0.0', 'curl.exe http://127.0.0.1:8000/health', 'python load_test.py --url http://127.0.0.1:8000/predict', 'docker stop lt'], 'PowerShell (Windows)'))
LT_LINUX = ('<p>Docker commands need <code>sudo</code> unless your user is in the docker group (log out and in again after adding it). Close other heavy programs while measuring, because they share the same CPU.</p>'
            + term(['sudo usermod -aG docker $USER        # once, then log out and in', 'docker run -d --rm --name lt -p 8000:8000 iris-api:1.0.0', 'curl http://127.0.0.1:8000/health', 'python3 load_test.py --url http://127.0.0.1:8000/predict', 'docker stop lt'], 'Terminal (Linux)'))
LT_CHROME = ('<p>Docker Desktop does not run on ChromeOS. Start the FastAPI service from MLOps 2.2 with uvicorn inside the Linux environment and test it from a second Linux terminal. The Linux environment has fewer CPU cores than the Chromebook itself, so expect lower numbers.</p>'
             + term(['source .venv/bin/activate', 'uvicorn fastapi_serve:app --port 8000 --workers 2 &', 'python3 load_test.py --url http://127.0.0.1:8000/predict', 'kill %1                               # stop the server'], 'Terminal (ChromeOS Linux)'))

K.lesson('frame', 'Start with the problem, then size the system', f'''
{src('Huyen, Designing Machine Learning Systems (2022) chapters 1 and 2, and Kleppmann, Designing Data-Intensive Applications (2017) chapter 1.')}
{steps('A framework for any ML system design question', [
    'Clarify the goal: the business metric (for example watch time or fraud losses) and the ML task that serves it (ranking, classification).',
    'Write the requirements: how many users, how fast an answer must be, how fresh the data, what a wrong answer costs, privacy and fairness limits.',
    'Design the data: where labels come from, which features, how they are computed for training and for serving.',
    'Choose the model: start with a simple baseline, then the model that fits the latency and the data.',
    'Design serving: batch or online, one stage or retrieval then ranking, and how many replicas.',
    'Plan evaluation: offline metrics first, then a shadow run, a canary and an online A/B test.',
    'Plan operations: monitoring, retraining and rollback (MLOps 3.1 and 3.2).'])}
{wwh('<b>ML system design</b> is the plan for everything around a model: data pipelines, features, training, serving, evaluation and monitoring, sized for real traffic.',
     'In production the model is a small part of the code. Most failures come from the system around it: slow serving, features that differ between training and serving, or a rollout with no way back. Interviews at large companies test exactly this.',
     'Turn every requirement into a number, do quick arithmetic for traffic, latency and storage, and let those numbers choose the design.')}
{run('capacity_plan')}
{note('Ten million daily users with 20 requests each average 2,315 requests per second and peak at 6,944. One replica with 4 workers at 40 ms handles 100 per second, so 116 replicas keep each at 60 percent load. Ranking a million items per request would take a full second, which is why recommenders retrieve 500 candidates first.', 'exam')}
{fxs(fx('Average load', 'QPS = daily requests / 86,400', 'A day has 86,400 seconds.', key=True),
     fx('Little&rsquo;s law', 'L = &lambda; &times; W', 'Requests in the system = arrival rate &times; time each one spends. So throughput = workers / latency.', key=True),
     fx('Replicas', 'replicas = &lceil; peak QPS / (per replica QPS &times; target load) &rceil;', 'A target load of 0.6 leaves room for spikes and a failed replica.'))}
''', kw=['ML system design', 'requirements', 'capacity planning', 'QPS', "Little's law", 'replicas', 'back of the envelope'])

K.lesson('serve', 'Batch, online and streaming predictions', f'''
{src('Huyen (2022) chapter 7, Covington, Adams and Sargin, Deep neural networks for YouTube recommendations (2016), and Breck and colleagues, The ML test score (2017).')}
{versus('Three ways to deliver predictions', ['', 'Batch', 'Online (on request)', 'Streaming'], [
    ['When it predicts', 'On a schedule, for everyone', 'When a request arrives', 'When an event arrives'],
    ['Latency', 'Hours, results read from a table', 'Milliseconds', 'Seconds'],
    ['Feature freshness', 'As old as the last run', 'Request data plus stored features', 'Features updated from the event stream'],
    ['Example', 'Nightly churn scores for the sales team', 'Fraud check during a payment', 'Live delivery time estimates'],
    ['Main risk', 'Stale scores, wasted work for inactive users', 'Tail latency and cost', 'Complex pipelines (Kafka, Flink)']],
    'Many systems mix them: batch for heavy features, online for the final score.')}
{wwh('<b>Training-serving skew</b> means the model sees features in production that were computed differently from the ones it was trained on. A <b>feature store</b> keeps one definition of each feature and serves it both to training jobs (as of a past date) and to the live service (the latest value).',
     'Skew is silent. The service answers, the offline score looked great, and the live accuracy is poor. It is one of the most common reasons why a model that won offline loses online.',
     'Compute every feature with one shared function or a feature store, log the features the service actually used, and add a parity test that sends the same raw rows through the training path and the serving path.')}
{run('skew_check')}
{note('The model scored 0.730 offline. The serving code filled missing spend with 0 instead of the training median and received spend in pence, not pounds, so live accuracy fell to 0.550 and the mean predicted churn collapsed from 0.435 to 0.124. A parity test on the same raw rows finds the difference on 100 percent of rows before release.', 'warn')}
{deep('Two stage recommenders', '<p>Large recommenders answer in two stages. <b>Retrieval</b> picks a few hundred candidates out of millions with a cheap method, such as nearest neighbours of a user embedding in a vector index. <b>Ranking</b> scores only those candidates with a heavier model that uses many features. Some systems add a third <b>re-ranking</b> step for business rules such as diversity and freshness. The capacity program above shows why: at 1 microsecond an item, ranking everything takes 1,000 ms, ranking 500 candidates takes 0.5 ms.</p>')}
''', kw=['batch prediction', 'online prediction', 'streaming', 'training-serving skew', 'feature store', 'parity test', 'retrieval and ranking'])

K.lesson('rollout', 'Shadow, canary and rollback', f'''
{src('Google, The Site Reliability Workbook (2018), chapter 16, Canarying releases.')}
{viz('mlrollout')}
{wwh('A <b>shadow deployment</b> sends a copy of live requests to the new model and logs its answers without showing them. A <b>canary</b> gives the new model to a small share of users and grows the share step by step. A <b>guardrail</b> is a metric with a limit, such as error rate or latency, checked after every step.',
     'Offline tests never cover everything real users do. A gradual rollout limits how many people a bad model can hurt, and an automatic rollback fixes it in seconds instead of hours.',
     'Run in shadow first to compare answers and latency. Then route 1, 5, 25, 50 and 100 percent of traffic, check the guardrails at each step, and keep the old version deployed until the new one has been stable for a while.')}
{table(['Strategy', 'Users see the new model', 'Good for', 'Watch out for'], [
    ['Shadow', 'No', 'Latency, crashes, agreement with the old model', 'Cannot measure user reactions, doubles compute'],
    ['Canary', 'A small growing share', 'Catching bugs with little harm', 'Small shares need time to show rare problems'],
    ['Blue-green', 'All at once, with an instant switch back', 'Simple, fast rollback', 'No gradual exposure'],
    ['A/B test', 'A fixed random half (or share)', 'Measuring the effect on a business metric', 'Needs enough users and a fixed plan'],
    ['Multi-armed bandit', 'More traffic to the version that is winning', 'Many variants, short campaigns', 'Harder to read the final effect']])}
''', kw=['shadow deployment', 'canary release', 'guardrail metric', 'rollback', 'blue-green deployment', 'multi-armed bandit'])

K.lesson('abtest', 'A/B testing a new model', f'''
{src('Kohavi, Tang and Xu, Trustworthy Online Controlled Experiments (2020) chapters 2, 17 and 18.')}
{viz('mlpeek')}
{wwh('An <b>A/B test</b> assigns users at random to the old model (A) or the new one (B) and compares a metric such as conversion. A <b>two proportion z test</b> says whether the difference is larger than chance. The <b>sample size</b> is fixed before the test from the smallest lift worth detecting.',
     'Offline gains often vanish online, because users react to the model and the offline metric is only a proxy. A randomised test is the only reliable way to measure the real effect, but only if it is run honestly.',
     'Choose the metric, the smallest lift that matters (minimum detectable effect, MDE), &alpha; and power. Compute n per group, run until both groups reach n, then test once. Watch guardrail metrics during the test, but do not stop early because the p value looks good.')}
{run('ab_test')}
{note('To detect a lift from 5.0 to 5.5 percent with &alpha; = 0.05 and 80 percent power you need 31,235 users per group. In 2,000 A/A tests a single look at the end gave 4.4 percent false alarms, close to the promised 5. Stopping on the first day with p &lt; 0.05 gave 22.0 percent, more than four times as many.', 'exam')}
{fxs(fx('Sample size per group', 'n = (z<sub>1&minus;&alpha;/2</sub> + z<sub>1&minus;&beta;</sub>)&sup2; &middot; 2 p&#772;(1 &minus; p&#772;) / &delta;&sup2;', 'p&#772; is the average rate, &delta; the lift. Halving &delta; needs four times the users.', key=True),
     fx('Two proportion z test', 'z = (p<sub>B</sub> &minus; p<sub>A</sub>) / &radic;( p(1 &minus; p)(1/n<sub>A</sub> + 1/n<sub>B</sub>) )', 'p is the pooled rate of both groups.', key=True),
     fx('Many looks', 'P(at least one false alarm) &le; 1 &minus; (1 &minus; &alpha;)<sup>k</sup>', 'An upper limit for k looks. Real looks share data, so the true rate is lower but still far above &alpha;.'))}
''', kw=['A/B test', 'minimum detectable effect', 'sample size', 'statistical power', 'z test', 'peeking', 'A/A test', 'sequential testing'])

K.lesson('load', 'Load test your model service on your own computer', f'''
{src('Python documentation: http.server, urllib.request and concurrent.futures.')}
{wwh('A <b>load test</b> sends many requests at once to a service and records throughput (requests per second) and latency percentiles at growing numbers of simultaneous users.',
     'Capacity plans are guesses until you measure. A load test shows the real requests per second of one replica, the number you divide the peak by, and the point where latency starts to climb.',
     'Start the service from MLOps 2.2 or the Docker image from MLOps 2.3, run the load test against it, and find the number of users where requests per second stop growing. Use that, with headroom, in the capacity plan.')}
{local('load_test', WHY_LOAD)}
{note('The built-in demo server can work on 4 requests at once, each taking 20 ms, so Little&rsquo;s law predicts 4 / 0.020 = 200 requests per second. The test gets close to 200 with 4 users and stays just under 200 with 8 and 16 users, while the median latency rises from about 21 ms to about 40 ms and then higher. Past the saturation point, more users only add waiting time. Timings change a little on every run.', 'exam')}
{ossteps('Start the model service and load test it', LT_MAC, LT_WIN, LT_LINUX, LT_CHROME)}
{REAL_RUN}
{note('The real FastAPI container from MLOps 2.3 levelled off at about 1,180 requests per second from 8 users, while its p50 went from 2.1 ms to 12.1 ms at 16 users. For the 6,944 requests per second peak, that machine would need about 10 such replicas at 60 percent load, a number you can now defend.', 'tip')}
''', kw=['load test', 'throughput', 'saturation', 'latency percentiles', 'concurrency', 'ThreadPoolExecutor'])

K.lesson('case', 'Worked design: real time fraud detection', f'''
{scene('A payment company asks for a fraud model', '<p>Every card payment must be approved or blocked within 100 ms, at a peak of 3,000 payments a second. Fraud is about 0.1 percent of payments. A missed fraud costs the full amount, and a wrongly blocked payment costs an angry customer. Fraud labels arrive weeks later, when customers dispute charges.</p>')}
{table(['Part of the design', 'Choice', 'Why', 'Chapter'], [
    ['Metric', 'Fraud losses saved, with a cap on wrongly blocked good payments', 'Accuracy is useless at 0.1 percent fraud', 'ML 2.x metrics'],
    ['Features', 'Payment amount, merchant, card history counts over 1 hour and 30 days', 'History counts come from a feature store, updated from the payment stream', 'This chapter'],
    ['Model', 'Gradient boosted trees, a few milliseconds per payment', 'Strong on tabular data, fast, explainable with SHAP', 'MLOps 3.3'],
    ['Serving', 'Online, inside the payment flow, rules as a fallback', 'Must decide before the payment completes', 'MLOps 2.2'],
    ['Rollout', 'Shadow for two weeks, then canary with guardrails on block rate', 'Fraud labels are slow, so start with safe signals', 'This chapter'],
    ['Monitoring', 'Score PSI, block rate, latency p99, dispute rate when labels arrive', 'Fraudsters adapt, so concept drift is certain', 'MLOps 3.2'],
    ['Retraining', 'Weekly through the tested pipeline and the registry gate', 'New fraud patterns appear all the time', 'MLOps 3.1']])}
{note('Interviewers look for the trade-offs, not one right answer. Say what you would measure, what you would try first, and how you would know it failed.', 'tip')}
''', kw=['fraud detection', 'case study', 'class imbalance', 'real time features', 'fallback rules', 'design interview'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>See a model as one part of a bigger system that collects data, answers users and needs watching.</p>',
    '<p>Size a system with QPS, Little&rsquo;s law and replicas, choose batch or online serving, and load test a service.</p>',
    '<p>Prevent training-serving skew, roll out with shadow and canary steps, and run an A/B test with a fixed sample size.</p>',
    '<p>Design multi stage recommenders and real time feature pipelines, use sequential tests and variance reduction such as CUPED, and lead design reviews.</p>')}
{grow('Explain the parts of an ML system.',
      'Size, serve and safely release a model.',
      'Design and defend a complete ML system in an interview or at work.')}
''', kw=['beginner', 'expert', 'CUPED', 'sequential testing'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'Turn requirements into numbers: 10 million users &times; 20 requests is 2,315 per second on average, 6,944 at peak, 116 replicas at 60 percent load.',
    'Choose batch, online or streaming serving. Retrieve cheaply, then rank: 500 candidates take 0.5 ms instead of 1,000 ms.',
    '<b>Training-serving skew</b> took accuracy from 0.730 to 0.550. Share one feature function or a feature store and add a parity test.',
    'Release in steps: shadow, canary with guardrails, automatic rollback. A/B test with a fixed n (31,235 per group). Peeking raised false alarms from 4.4 to 22 percent.',
    'Load test on your own computer: throughput levels off at workers / latency, and after that only waiting time grows.'],
    'Coming next: revising every MLOps chapter for interviews and certification exams.')}
{files('Three tasks: replicas from traffic, A/B test sample size, and a canary guardrail check.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'Why size a system with numbers before choosing a design?', ['It looks professional', 'Traffic, latency and storage numbers decide which designs are possible', 'Numbers are required by law', 'It makes the model more accurate'], 1, 'Numbers choose the design.', '6,944 peak requests per second.')
K.quiz('e', 'Batch prediction fits best when', ['Answers are needed within 50 ms', 'Scores can be computed ahead of time, such as nightly churn scores', 'Every request is unique', 'Data changes every second'], 1, 'Ahead of time.', 'Results are read from a table.')
K.quiz('e', 'A shadow deployment', ['Shows the new model to all users', 'Sends copies of requests to the new model and only logs its answers', 'Deletes the old model', 'Trains in the background'], 1, 'Users never see it.', 'Good for latency and crashes.')
K.quiz('e', 'Little&rsquo;s law says throughput is about', ['latency / workers', 'workers / latency', 'workers &times; latency', 'users &times; workers'], 1, 'L = &lambda;W.', '4 / 0.020 = 200 per second.')
K.quiz('m', 'Training-serving skew is', ['A model too big for the server', 'Features computed differently in training and in serving', 'A slow network', 'Too few training rows'], 1, 'Same name, different value.', '0.730 offline, 0.550 online.')
K.quiz('m', 'The best protection against skew is', ['A bigger model', 'One shared feature definition or a feature store, plus a parity test', 'More epochs', 'Higher learning rate'], 1, 'One definition, tested.', 'Same raw rows through both paths.')
K.quiz('m', 'Why do large recommenders retrieve candidates before ranking?', ['Ranking every item is too slow for the latency budget', 'Retrieval is more accurate', 'Ranking needs no features', 'To save disk'], 0, 'Cost per item.', '1,000 ms against 0.5 ms.')
K.quiz('m', 'During a canary, the guardrail error rate is broken at 1 percent of traffic. The right action is', ['Wait for 100 percent', 'Roll back to the old version at once', 'Retrain during the canary', 'Turn off monitoring'], 1, 'Limit the harm.', 'Only about 1,000 requests were affected.')
K.quiz('m', 'On Windows, why test 127.0.0.1 instead of localhost?', ['localhost is forbidden', 'localhost may try IPv6 first and add a delay to each request', 'It is faster to type', 'Docker needs it'], 1, 'Name resolution.', 'The delay spoils the timings.')
K.quiz('h', 'An A/B test checks the p value daily and stops at the first p &lt; 0.05. The false alarm rate', ['Stays at 5 percent', 'Rises well above 5 percent', 'Falls to 0', 'Is unknown'], 1, 'Many looks.', '22 percent in 2,000 A/A tests.')
K.quiz('h', 'Halving the minimum detectable effect changes the sample size by', ['Half', 'Double', 'About four times', 'No change'], 2, 'n grows with 1/&delta;&sup2;.', 'Small effects are expensive to detect.')
K.quiz('h', 'Load testing shows requests per second flat from 8 to 16 users while latency doubles. The service', ['Has a memory leak', 'Is saturated: all workers are busy and requests queue', 'Is idle', 'Needs a bigger model'], 1, 'Past saturation.', 'Add replicas or workers.')
K.quiz('x', 'In the style of a FAANG ML design interview: fraud labels arrive 6 weeks late. Which first rollout plan is best?', ['Full launch and wait for labels', 'Shadow mode with score and block rate monitoring, then a canary with guardrails', 'An A/B test on fraud labels only', 'No rollout plan'], 1, 'Use fast safe signals first.', 'Labels confirm later.')
K.quiz('x', 'In the style of a Stanford CS329S exam: which change makes an online A/B test valid when you must look at results every day?', ['Use a smaller &alpha; on the last day only', 'Use a sequential test designed for repeated looks', 'Stop when p &lt; 0.05', 'Use the training loss'], 1, 'Alpha spending or always valid p values.', 'Plain z tests assume one look.')

K.calc('e', '10 million users each make 20 requests a day. Average requests per second?', '2315', 'Daily requests over seconds in a day.', ['10,000,000 &times; 20 = 200,000,000 requests a day.', 'A day has 86,400 seconds.', eq('200,000,000 / 86,400 = 2,315 per second')], check=2315, tol=0.5)
K.calc('e', 'A replica has 4 workers and each prediction takes 40 ms. Requests per second for one replica?', '100', 'Little&rsquo;s law.', ['Throughput = workers / latency.', '40 ms = 0.040 s.', eq('4 / 0.040 = 100 per second')], check=100)
K.calc('e', 'A canary gets 1 percent of 100,000 requests an hour. Requests to the new model in one hour?', '1000', 'Share times total.', ['1 percent = 0.01.', 'Total: 100,000.', eq('0.01 &times; 100,000 = 1,000')], check=1000)
K.calc('m', 'Peak load is 6,944 requests a second, each replica serves 100, and replicas run at 60 percent load. Replicas needed?', '116', 'Divide, then round up.', ['Usable per replica: 100 &times; 0.6 = 60.', '6,944 / 60 = 115.7.', eq('round up: 116 replicas')], check=116)
K.calc('m', '200 million requests a day are logged at 2 KB each. Gigabytes per day?', '400', 'Requests times size.', ['2 KB = 2,000 bytes.', '200,000,000 &times; 2,000 = 4 &times; 10<sup>11</sup> bytes.', eq('4 &times; 10<sup>11</sup> / 10<sup>9</sup> = 400 GB')], check=400)
K.calc('m', 'A ranker needs 1 microsecond per item. Milliseconds to rank 500 retrieved candidates?', '0.5', 'Items times cost.', ['500 &times; 1 &mu;s = 500 &mu;s.', '1,000 &mu;s = 1 ms.', eq('500 &mu;s = 0.5 ms')], check=0.5)
K.calc('m', 'Each group has 31,235 users, A converts 5.0 percent and B 5.5 percent, pooled rate 0.0525. z statistic?', '2.8016', 'Difference over the pooled standard error.', ['Variance term: 0.0525 &times; 0.9475 &times; (2 / 31,235) = 3.185 &times; 10<sup>&minus;6</sup>.', 'Standard error: &radic;(3.185 &times; 10<sup>&minus;6</sup>) = 0.0017847.', eq('z = 0.005 / 0.0017847 = 2.8016')], check=2.8016, tol=0.0005)
K.calc('h', 'Sample size per group with z values 1.96 and 0.84, p&#772; = 0.0525 and &delta; = 0.005?', '31199.28', 'n = (z<sub>a</sub> + z<sub>b</sub>)&sup2; &middot; 2p&#772;(1 &minus; p&#772;) / &delta;&sup2;.', ['(1.96 + 0.84)&sup2; = 2.8&sup2; = 7.84.', '2 &times; 0.0525 &times; 0.9475 = 0.0994875, and &delta;&sup2; = 0.000025.', eq('7.84 &times; 0.0994875 / 0.000025 = 31,199.28, so 31,200 users (the program used exact z values and got 31,235)')], check=31199.28, tol=0.01)
K.calc('h', '16 users keep requests going and the service completes 196 per second. Average time per request in ms (Little&rsquo;s law)?', '81.6', 'W = L / &lambda;.', ['L = 16 requests in the system.', '&lambda; = 196 per second.', eq('W = 16 / 196 = 0.0816 s = 81.6 ms')], check=81.6, tol=0.05)
K.calc('x', 'In the style of an experimentation exam: if 5 looks at an A/A test were independent, each at &alpha; = 0.05, what is the chance of at least one false alarm?', '0.2262', 'One minus the chance of none.', ['No false alarm on one look: 0.95.', 'None on 5 looks: 0.95<sup>5</sup> = 0.7738.', eq('1 &minus; 0.7738 = 0.2262')], check=0.2262, tol=0.0005)

K.assign('replicas_needed', 'e', 'Replicas from traffic',
         '<p>Write <code>replicas_needed(daily_requests, peak_factor, per_replica, load)</code>. Compute the peak requests per second (daily requests / 86,400 &times; peak factor) and return the number of replicas needed so that each runs at no more than <code>load</code> of its capacity <code>per_replica</code>. Round up.</p>',
         """
def replicas_needed(daily_requests, peak_factor, per_replica, load):
    # your code here
    pass
""", [('replicas_needed(200_000_000, 3, 100, 0.6)', 116), ('replicas_needed(86_400, 1, 1, 1.0)', 1), ('replicas_needed(864_000, 2, 5, 0.5)', 8), ('replicas_needed(0, 3, 100, 0.6)', 0)],
         """
import math


def replicas_needed(daily_requests, peak_factor, per_replica, load):
    peak = daily_requests / 86_400 * peak_factor
    return math.ceil(peak / (per_replica * load) - 1e-9)
""", 'Peak load over usable capacity per replica, then math.ceil.', '<p>The tiny 1e&minus;9 guards against floating point results such as 1.0000000002 turning into 2 replicas. Real systems also add one spare replica per zone.</p>')
K.assign('ab_sample_size', 'm', 'A/B test sample size',
         '<p>Write <code>ab_sample_size(p, delta)</code> for a base rate <code>p</code> and a lift <code>delta</code>. Use p&#772; = p + delta / 2, z values 1.96 and 0.8416, and return the users needed per group, n = (1.96 + 0.8416)&sup2; &middot; 2p&#772;(1 &minus; p&#772;) / delta&sup2;, rounded up.</p>',
         """
def ab_sample_size(p, delta):
    # your code here
    pass
""", [('ab_sample_size(0.05, 0.005)', 31235), ('ab_sample_size(0.10, 0.02)', 3843), ('ab_sample_size(0.5, 0.1)', 389)],
         """
import math


def ab_sample_size(p, delta):
    p_bar = p + delta / 2
    return math.ceil((1.96 + 0.8416) ** 2 * 2 * p_bar * (1 - p_bar) / delta ** 2)
""", 'Compute p&#772;, then the formula, then math.ceil.', '<p>Notice how the answer explodes for small lifts: detecting 0.5 points on a 5 percent rate needs over 31,000 users per group.</p>')
K.assign('canary_check', 'm', 'A canary guardrail check',
         '<p>Write <code>canary_check(stages, guard, min_requests)</code>. <code>stages</code> is a list of (requests, errors) pairs, one per rollout step. Return the index of the first stage whose error rate is above <code>guard</code> and that has at least <code>min_requests</code> requests, or &minus;1 if every stage passes.</p>',
         """
def canary_check(stages, guard, min_requests):
    # your code here
    pass
""", [('canary_check([(1000, 24), (5000, 120)], 0.012, 500)', 0), ('canary_check([(1000, 6), (5000, 31), (25000, 150)], 0.012, 500)', -1), ('canary_check([(100, 5), (5000, 80)], 0.012, 500)', 1), ('canary_check([], 0.012, 500)', -1)],
         """
def canary_check(stages, guard, min_requests):
    for i, (requests, errors) in enumerate(stages):
        if requests >= min_requests and errors / requests > guard:
            return i
    return -1
""", 'Loop with enumerate and skip stages that are too small to judge.', '<p>The minimum request count stops a single unlucky error in a tiny stage from triggering a rollback. Production systems use a statistical test instead of a fixed count.</p>')

K.must('Design framework', 'Goal and metric, requirements as numbers, data and features, baseline model, serving, offline then online evaluation, monitoring and retraining.')
K.must('Sizing', 'QPS = daily requests / 86,400, times a peak factor. Little&rsquo;s law: throughput = workers / latency. Replicas = ceil(peak / (capacity &times; load)).')
K.must('Serving modes', 'Batch (scheduled, stale), online (ms, tail latency), streaming (fresh features). Retrieve then rank for big catalogues.')
K.must('Skew', 'Same feature, different code in training and serving. One definition or feature store, logged features, parity test.')
K.must('Safe release', 'Shadow, canary 1 to 100 percent with guardrails, automatic rollback, keep the old version ready.')
K.must('A/B tests', 'n = (z<sub>a</sub> + z<sub>b</sub>)&sup2; 2p&#772;(1 &minus; p&#772;) / &delta;&sup2;. Fix n first, test once. Peeking: 4.4 to 22 percent false alarms.')

T = K.topic(
    slug='mlops-system-design', topic='mlops-system-design', step=(4, 'Design and certify', 'mlops-s4', 'Design a complete ML system from requirements to rollout, and revise every MLOps chapter for interviews and certification exams.', 'Expert'),
    title='Designing an ML system end to end', short='ML system design', badge='4.1', minutes=60,
    lead='Turn requirements into traffic, latency and storage numbers, choose batch, online or streaming serving, prevent training-serving skew, release with shadow and canary steps, run an honest A/B test, and load test a model service on your own computer.',
    desc='ML system design, requirements, capacity planning, QPS, Little\'s law, replicas, batch prediction, online prediction, streaming, retrieval and ranking, feature store, training-serving skew, parity test, shadow deployment, canary release, guardrail metrics, rollback, blue-green, A/B testing, sample size, minimum detectable effect, peeking, sequential testing, load testing, fraud detection case study.',
    summary='Sizing with QPS and Little\'s law, serving modes, skew, shadow and canary releases, A/B test sample size and peeking, and a local load test.',
    keywords=['ML system design', 'capacity planning', "Little's law", 'feature store', 'training-serving skew', 'canary release', 'A/B testing', 'load testing'],
    recap='<p>Start from the goal and the numbers, design data, serving and rollout around them, and prove each step with measurements before real users depend on it.</p>',
    added='2026-11-14', leet=leet_items())
