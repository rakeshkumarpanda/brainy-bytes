# 3.1 Experiment tracking and the model registry
# Model solutions. Try practice.py first.
# From the Brainy Bytes MLOps subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn


# ------------------------------------------------------------------ the checker
# check(tests) runs each test and says PASS or FAIL. A test is a pair: the call to make and the answer we expect.
import json


def check(name, tests):
    passed = 0
    for call, expected in tests:
        try:
            got = eval(call)
        except Exception as error:
            got = "error: " + type(error).__name__ + ": " + str(error)
        if json.dumps(got, sort_keys=True, default=repr) == json.dumps(expected, sort_keys=True, default=repr):
            passed = passed + 1
            print("  PASS", call)
        else:
            print("  FAIL", call, "expected", repr(expected), "but got", repr(got))
    print(name + ":", passed, "of", len(tests), "tests pass")
    return passed == len(tests)


# ================================================================== task 1: Pick the best run
# Each run is a dict like {'id': 3, 'metrics': {'val_auc': 0.99}}. Write pick_best(runs, metric,
# higher=True) that returns the id of the run with the highest value of metric, or the lowest when
# higher is False. Ignore runs that did not log the metric.
# Why it works: mlflow.search_runs(order_by=['metrics.val_auc DESC']) does the same on the server.

def pick_best(runs, metric, higher=True):
    scored = [r for r in runs if metric in r['metrics']]
    pick = max if higher else min
    return pick(scored, key=lambda r: r['metrics'][metric])['id']


# ================================================================== task 2: A promotion gate
# Write should_promote(champion, challenger, margin=0.002) that returns True when the challenger’s
# score is at least the champion’s plus the margin. A champion of None means there is no champion
# yet, so any challenger is promoted.
# Why it works: The tiny 1e-12 keeps a challenger that is exactly at the margin from failing because
# of float rounding.

def should_promote(champion, challenger, margin=0.002):
    if champion is None:
        return True
    return challenger >= champion + margin - 1e-12


# ================================================================== task 3: How many random runs?
# Write runs_needed(top_share, confidence) that returns the smallest n with 1 − (1 − top_share)n ≥
# confidence.
# Why it works: The closed form is the ceiling of ln(1 − confidence) / ln(1 − top_share), but a loop
# avoids rounding traps.

def runs_needed(top_share, confidence):
    n, miss = 1, 1 - top_share
    while 1 - miss ** n < confidence:
        n += 1
    return n


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Pick the best run", [("pick_best([{'id': 1, 'metrics': {'auc': 0.9}}, {'id': 2, 'metrics': {'auc': 0.95}}], 'auc')", 2), ("pick_best([{'id': 1, 'metrics': {'loss': 0.3}}, {'id': 2, 'metrics': {'loss': 0.2}}], 'loss', False)", 2), ("pick_best([{'id': 1, 'metrics': {}}, {'id': 2, 'metrics': {'auc': 0.5}}], 'auc')", 2)]))
    results.append(check("Task 2: A promotion gate", [('should_promote(0.9555, 0.9942)', True), ('should_promote(0.9943, 0.9942)', False), ('should_promote(None, 0.7)', True), ('should_promote(0.9, 0.95, 0.1)', False)]))
    results.append(check("Task 3: How many random runs?", [('runs_needed(0.05, 0.95)', 59), ('runs_needed(0.1, 0.9)', 22), ('runs_needed(0.5, 0.75)', 2), ('runs_needed(1.0, 0.99)', 1)]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
