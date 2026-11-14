# 4.2 MLOps revision and certification practice
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


# ================================================================== task 1: A release gate
# Write gate_failures(metrics, rules). metrics maps a check name to its value. rules maps the same
# names to a pair (op, limit), where op is '>=', '<=' or '<'. Return the sorted list of names whose
# value breaks its rule. A name missing from metrics counts as a failure.
# Why it works: Failing on a missing metric is deliberate: a gate that silently skips a check it
# cannot compute lets unchecked models through.

def gate_failures(metrics, rules):
    checks = {'>=': lambda v, t: v >= t, '<=': lambda v, t: v <= t, '<': lambda v, t: v < t}
    failed = []
    for name, (op, limit) in rules.items():
        if name not in metrics or not checks[op](metrics[name], limit):
            failed.append(name)
    return sorted(failed)


# ================================================================== task 2: Champion after promotions and rollbacks
# Write current_champion(events). Each event is either 'promote vN' or 'rollback'. A promotion makes
# vN the champion. A rollback returns to the champion before the current one. Return the champion at
# the end, or None if there is none.
# Why it works: A registry keeps every version, so a rollback never needs retraining. The stack of
# past champions is exactly what the alias history in MLflow records.

def current_champion(events):
    history = []
    for event in events:
        if event == 'rollback':
            if history:
                history.pop()
        else:
            history.append(event.split()[1])
    return history[-1] if history else None


# ================================================================== task 3: How long an error budget lasts
# Write budget_days(slo, error_rate, window_days). The burn rate is error_rate / (1 − slo). Return
# window_days / burn rate rounded to 2 decimals, or None when error_rate is 0.
# Why it works: A burn rate of 1 uses the budget exactly over the window. Above 1 the budget runs
# out early, which is what burn rate alerts watch.

def budget_days(slo, error_rate, window_days):
    if error_rate == 0:
        return None
    burn = error_rate / (1 - slo)
    return round(window_days / burn, 2)


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: A release gate", [("gate_failures({'auc_gain': 0.05, 'di': 0.48, 'tpr_gap': 0.23}, {'auc_gain': ('>=', 0.002), 'di': ('>=', 0.8), 'tpr_gap': ('<=', 0.1)})", ['di', 'tpr_gap']), ("gate_failures({'auc_gain': 0.0125, 'di': 0.87, 'psi': 0.008}, {'auc_gain': ('>=', 0.002), 'di': ('>=', 0.8), 'psi': ('<', 0.1)})", []), ("gate_failures({'di': 0.9}, {'di': ('>=', 0.8), 'psi': ('<', 0.1)})", ['psi']), ("gate_failures({'psi': 0.1}, {'psi': ('<', 0.1)})", ['psi'])]))
    results.append(check("Task 2: Champion after promotions and rollbacks", [("current_champion(['promote v1', 'promote v3', 'rollback'])", 'v1'), ("current_champion(['promote v1'])", 'v1'), ('current_champion([])', None), ("current_champion(['promote v1', 'promote v2', 'promote v3', 'rollback', 'rollback'])", 'v1'), ("current_champion(['promote v1', 'rollback'])", None)]))
    results.append(check("Task 3: How long an error budget lasts", [('budget_days(0.999, 0.005, 30)', 6.0), ('budget_days(0.999, 0.001, 30)', 30.0), ('budget_days(0.99, 0.02, 28)', 14.0), ('budget_days(0.999, 0, 30)', None)]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
